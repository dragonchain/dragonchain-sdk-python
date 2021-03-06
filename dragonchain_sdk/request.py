# Copyright 2020 Dragonchain, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
import json
import urllib.parse
from typing import cast, Any, Callable, Optional, Dict, Tuple, TYPE_CHECKING

import requests

from dragonchain_sdk import configuration
from dragonchain_sdk import credentials
from dragonchain_sdk import exceptions

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import aiohttp  # noqa: F401 used by typing
    from dragonchain_sdk.types import request_response

supported_http = cast(
    Dict[str, Callable[..., requests.Response]],
    {
        "GET": requests.get,
        "POST": requests.post,
        "PUT": requests.put,
        "PATCH": requests.patch,
        "DELETE": requests.delete,
        "HEAD": requests.head,
        "OPTIONS": requests.options,
    },
)


class Request(object):
    """Construct a new `Request` object

    Args:
        credentials_obj (Credentials): The credentials for the chain to associate with requests
        endpoint (str, optional): The URL for the endpoint of the chain
        verify (bool, optional): Boolean indicating whether to validate the SSL certificate of the endpoint when making requests

    Raises:
        TypeError: with bad parameter types

    Returns:
        A new Request object.
    """

    def __init__(self, credentials_obj: credentials.Credentials, endpoint: Optional[str] = None, verify: bool = True):
        if isinstance(credentials_obj, credentials.Credentials):
            self.credentials = credentials_obj
        else:
            raise TypeError('Parameter "credentials" must be of type Credentials.')

        if isinstance(verify, bool):
            self.verify = verify
            logger.debug("SSL certificates will{} be verified when making requests".format("" if self.verify else " NOT"))
        else:
            raise TypeError('Parameter "verify" must be of type bool.')

        self.update_endpoint(endpoint)

        # This is assigned if/when creating an async client
        self.session = cast("aiohttp.ClientSession", None)

    def update_endpoint(self, endpoint: Optional[str] = None) -> None:
        """Update endpoint for this request object

        Args:
            endpoint (str, optional): Endpoint to set. Will auto-generate based on credentials dragonchain_id if not provided

        Raises:
            TypeError: with bad parameter types

        Returns:
            None, sets the endpoint of this Request instance
        """
        if endpoint is None:
            self.endpoint = configuration.get_endpoint(self.credentials.dragonchain_id)
        elif isinstance(endpoint, str):
            self.endpoint = endpoint
        else:
            raise TypeError('Parameter "endpoint" must be of type str.')
        logger.info("Target endpoint updated to {}".format(self.endpoint))

    def get(self, path: str, parse_response: bool = True) -> "request_response":
        """Make a GET request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            The response of the GET operation.
        """
        return self._make_request(http_verb="GET", path=path, verify=self.verify, parse_response=parse_response)

    def post(self, path: str, body: Any, parse_response: bool = True, additional_headers: Optional[Dict[str, str]] = None) -> "request_response":
        """Make a POST request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            body (JSON-encodable): Object representing the JSON to post.
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            The response of the POST operation.
        """
        if additional_headers is None:
            additional_headers = {}
        return self._make_request(
            http_verb="POST", path=path, verify=self.verify, json_content=body, parse_response=parse_response, additional_headers=additional_headers
        )

    def put(self, path: str, body: Any, parse_response: bool = True) -> "request_response":
        """Make a PUT request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            body (JSON-encodable): Object representing the JSON to put.
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            The response of the PUT operation.
        """
        return self._make_request(http_verb="PUT", path=path, verify=self.verify, json_content=body, parse_response=parse_response)

    def patch(self, path: str, body: Any, parse_response: bool = True) -> "request_response":
        """Make a PATCH request to a chain

        Args:
            path (str): Path of the request (including any path query parameters)
            body (JSON-encodable): Object representing the JSON to patch.
            parse_response (bool, optional): Decides whether the return from the chain sholud be parsed as json (default True)

        Returns:
            The response of the PATCH operation
        """
        return self._make_request(http_verb="PATCH", path=path, verify=self.verify, json_content=body, parse_response=parse_response)

    def delete(self, path: str, parsed_response: bool = True) -> "request_response":
        """Make a DELETE request to the chain

        Args:
            path (str): Path of the request (including any path query parameters)
            parse_response (bool, optional): Decides whether the return from the chain should be parsed as json (default True)

        Returns:
            The response of the DELETE operation
        """
        return self._make_request(http_verb="DELETE", path=path, verify=self.verify, parse_response=parsed_response)

    def get_requests_method(self, http_verb: str) -> Callable[..., requests.Response]:
        """Get the appropriate requests method for a given http_verb

        Args:
            http_verb (str): the type of http request to make (GET, POST, etc)

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            appropriate requests http method
        """
        if not isinstance(http_verb, str):
            raise TypeError('Parameter "http_verb" must be of type str.')
        request_method = supported_http.get(http_verb.upper())
        if not request_method:
            raise ValueError(http_verb + " is an unsupported http operation.")
        return request_method

    def generate_query_string(self, query_dict: Dict[str, str]) -> str:
        """Generate an http query string from a dictionary

        Args:
            query_dict (dict): dict of parameters to use in the query string

        Raises:
            TypeError: with bad parameter types

        Returns:
            query string to use in an HTTP request path
        """
        if not isinstance(query_dict, dict):
            raise TypeError('Parameter "query_dict" must be of type dict.')
        if query_dict:
            query = "?"
            query_string = urllib.parse.urlencode(query_dict)
            logger.debug("Generated query string {}".format(query_string))
            return "{}{}".format(query, query_string)
        else:
            # If input is empty, return an empty string as the query string
            return ""

    def _make_headers(self, timestamp: str, authorization: str, content_type: Optional[str] = None) -> Dict[str, str]:
        """Create a headers dictionary to send with a request to a dragonchain

        Args:
            timestamp (str): unix timestamp to put for this request
            content_type (str): content_type to use for this request
            authorization (str, optional): authorization header to include with the request

        Raises:
            TypeError: with bad parameter types

        Returns:
            dict of headers to use with the request
        """
        if not isinstance(timestamp, str):
            raise TypeError('Parameter "timestamp" must be of type str.')
        if not isinstance(authorization, str):
            raise TypeError('Parameter "authorization" must be of type str.')
        if content_type is not None and not isinstance(content_type, str):
            raise TypeError('Parameter "content_type" must be of type str.')
        header_dict = {"dragonchain": self.credentials.dragonchain_id, "timestamp": timestamp, "Authorization": authorization}
        if content_type:
            header_dict["Content-Type"] = content_type
        return header_dict

    def _generate_request_data(
        self, http_verb: str, path: str, json_content: Optional[Dict[Any, Any]] = None, additional_headers: Optional[Dict[str, str]] = None
    ) -> Tuple[str, bytes, Dict[str, str]]:
        """Generate all of the data needed to pass into an http request to a dragonchain

        Args:
            http_verb (str): the type of http request to make (GET, POST, etc)
            path (str): the full path to make the request (including query params if any) starting with a '/'
            json_content (dict, optional): dictionary object to send as json (automatically sets content-type to application/json)
            additional_headers (dict, optional): dictionary of additional headers to add to the request

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            Tuple where index 0 is the full URL, index 1 is the bytes of the request body, and index 2 is a dictionary of headers
        """
        if additional_headers is None:
            additional_headers = {}
        if not isinstance(path, str):
            raise TypeError('Parameter "path" must be of type str.')
        if not path.startswith("/"):
            raise ValueError("Parameter \"path\" must start with a '/'.")

        logger.debug("Creating request {} {}".format(http_verb, path))
        if json_content:
            content_type = "application/json"
            content = json.dumps(json_content, separators=(",", ":")).encode("utf8")
        else:
            content_type = ""
            content = b""
        # Add the 'Z' manually to indicate UTC (not added by isoformat)
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        authorization = self.credentials.get_authorization(http_verb, path, timestamp, content_type, content)

        header_dict = self._make_headers(timestamp, authorization, content_type)
        additional_headers.update(header_dict)
        full_url = self.endpoint + path

        logger.debug("{} {}".format(http_verb, full_url))
        logger.debug("Headers: {}".format(header_dict))
        logger.debug("Data: {!r}".format(content))
        return full_url, content, additional_headers

    def _make_request(
        self,
        http_verb: str,
        path: str,
        json_content: Optional[Dict[Any, Any]] = None,
        timeout: int = 30,
        verify: bool = True,
        parse_response: bool = True,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> "request_response":
        """Make an http request to a dragonchain with the given information

        Args:
            http_verb (str): the type of http request to make (GET, POST, etc)
            path (str): the full path to make the request (including query params if any) starting with a '/'
            json_content (dict, optional): dictionary object to send as json (automatically sets content-type to application/json)
            timeout (int, optional): the timeout to wait for the dragonchain to respond (defaults to 30 seconds if not set)
            verify (bool, optional): specify if the SSL cert of the chain should be verified
            parse_response (bool, optional): if the return from the chain should be parsed as json
            additional_headers (dict, optional): dictionary of additional headers to add to the request

        Raises:
            ConnectionException: when unable to communicate with the dragonchain
            UnexpectedResponseException: when the dragonchain responds with an unexpected payload

        Returns:
            Dictionary where status is the HTTP status code, response is the return body from the chain, and ok is a boolean if the status code was in the 2XX range
            {
                'status': int (http response code from chain)
                'ok': boolean (if http response code is 200-299)
                'response': dict if parse_response, else str (actual response body from chain)
            }
        """
        full_url, content, header_dict = self._generate_request_data(
            http_verb=http_verb, path=path, json_content=json_content, additional_headers=additional_headers
        )

        # Make request with appropriate data
        try:
            requests_method = self.get_requests_method(http_verb)
            logger.debug("Making request. Verify SSL: {}, Timeout: {}".format(verify, timeout))
            r = requests_method(url=full_url, data=content, headers=header_dict, timeout=timeout, verify=verify)
        except Exception as e:
            raise exceptions.ConnectionException("Error while communicating with the Dragonchain: {}".format(e))
        return_dict = {}
        # Generate the return dictionary
        try:
            return_dict["status"] = r.status_code
            logger.debug("Response status code: {}".format(r.status_code))
            return_dict["ok"] = r.status_code // 100 == 2
            return_dict["response"] = r.json() if parse_response else r.text
            return cast("request_response", return_dict)
        except Exception as e:
            raise exceptions.UnexpectedResponseException("Unexpected response from Dragonchain. Response: {} | Error: {}".format(r.text, e))
