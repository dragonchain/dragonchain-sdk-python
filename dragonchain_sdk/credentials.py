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

import hashlib
import hmac
import sys
import base64
import logging
from typing import cast, Any, Optional, Union, Callable

from dragonchain_sdk import configuration

logger = logging.getLogger(__name__)


class Credentials(object):
    """Construct a new `Credentials` object

    Args:
        dragonchain_id (str, optional): The dragonchain ID for these credentials
        auth_key (str, optional): The auth_key to use with these credentials
        auth_key_id (str, optional): The auth_key_id associated with the provided auth_key
        algorithm (str, optional): The hash algorithm to use with the HMAC authentication scheme (SHA256 | BLAKE2b512 | SHA3-256)

    Raises:
        TypeError: with bad parameter types

    Returns:
        A new Credentials object.
    """

    def __init__(
        self, dragonchain_id: Optional[str] = None, auth_key: Optional[str] = None, auth_key_id: Optional[str] = None, algorithm: str = "SHA256"
    ):
        if dragonchain_id is None:
            self.dragonchain_id = configuration.get_dragonchain_id()
        else:
            logger.debug("dragonchain_id provided in constructor parameters, using this excplicitly")
            if isinstance(dragonchain_id, str):
                self.dragonchain_id = dragonchain_id
            else:
                raise TypeError('Parameter "dragonchain_id" must be of type str.')
        logger.debug("Loaded dragonchain id {}".format(self.dragonchain_id))

        if auth_key is None or auth_key_id is None:
            self.auth_key_id, self.auth_key = configuration.get_credentials(self.dragonchain_id)
        else:
            logger.debug("Auth keys provided in constructor parameters, using these excplicitly")
            if isinstance(auth_key, str) and isinstance(auth_key_id, str):
                self.auth_key = auth_key
                self.auth_key_id = auth_key_id
            else:
                raise TypeError('Parameter "auth_key" and "auth_key_id" must be of type str.')
        logger.debug("Loaded auth key with id: {}".format(self.auth_key_id))

        self.update_algorithm(algorithm)
        logger.debug("Created credentials client for {}".format(dragonchain_id))

    def update_algorithm(self, algorithm: str) -> None:
        """Update the algorithm to use with these credentials

        Args:
            algorithm (str): The algorithm to use. Valid options are BLAKE2b512, SHA256, or SHA3-256

        Raises:
            TypeError: with bad parameter types

        Returns:
            None, sets the HMAC signing algorithm for this credential instance
        """
        if isinstance(algorithm, str):
            self.hash_method = self.get_hash_method(algorithm)
            self.algorithm = algorithm
            logger.debug("Updated hashing algorithm to {}".format(algorithm))
        else:
            raise TypeError('Parameter "algorithm" must be of type str.')

    def get_hash_method(self, algorithm: str) -> Callable[..., Any]:
        """Return a hash method that supports the hashlib .new function

        Args:
            algorithm (str): The algorithm to use. Valid options are BLAKE2b512, SHA256, or SHA3-256

        Raises:
            NotImplementedError: when provided algorithm is not supported

        Returns
            hashlib interface compatible hash method
        """
        if algorithm == "SHA256":
            return hashlib.sha256
        if sys.version_info[:2] >= (3, 6):
            if algorithm == "BLAKE2b512":
                return hashlib.blake2b
            elif algorithm == "SHA3-256":
                return hashlib.sha3_256
        raise NotImplementedError("{} is not a supported hash algorithm.".format(algorithm))

    def bytes_to_b64_str(self, unencoded_bytes: bytes) -> str:
        """Take a bytes object and output a base64 python string

        Args:
            unencoded_bytes (bytes): Python bytes object to encode

        Raises:
            TypeError: with bad parameter types

        Returns:
            String of the base64 encoded bytes
        """
        if not isinstance(unencoded_bytes, bytes):
            raise TypeError('Parameter "unencoded_bytes" must be of type bytes.')
        return base64.b64encode(unencoded_bytes).decode("ascii")

    def bytes_from_input(self, input_data: Union[bytes, str]) -> bytes:
        """Return python bytes from input (either bytes or utf-8 encodable string)

        Args:
            input_data (bytes or str): input to process

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            bytes object representation of input
        """
        if isinstance(input_data, str):
            try:
                return input_data.encode("utf-8")
            except Exception:
                raise ValueError('Parameter "input_data" was of type str but not utf-8 encodable.')
        elif isinstance(input_data, bytes):
            return input_data
        else:
            raise TypeError('Parameter "input_data" must be of type str or bytes.')

    def base64_encode_input(self, input_data: Union[bytes, str]) -> str:
        """Base64 encode some input (either bytes or utf-8 encodable string)

        Args:
            input_data (bytes or str): data to encode

        Returns:
            string of base64 encoded input
        """
        return self.bytes_to_b64_str(self.bytes_from_input(input_data))

    def hash_input(self, input_data: Union[bytes, str]) -> bytes:
        """Hash some input_data with a specified (supported) hash type

        Args:
            input_data (str or bytes): data to hash

        Returns:
            bytes of hashed input
        """
        return cast(bytes, self.hash_method(self.bytes_from_input(input_data)).digest())  # We know this is always a hashlib hash that returns bytes

    def create_hmac(self, secret: str, message: Union[bytes, str]) -> bytes:
        """Create an hmac from a given hash type, secret, and message

        Args:
            secret (str): The secret to be used to generate the hmac
            message (bytes or str): The message to use as in the hmac generation

        Returns:
            Bytes for the generated hmac
        """
        return hmac.new(key=self.bytes_from_input(secret), msg=self.bytes_from_input(message), digestmod=self.hash_method).digest()

    def compare_hmac(self, hmac_string: str, secret: str, message: Union[bytes, str]) -> bool:
        """Compare a provided base64 encoded hmac string with a generated hmac from the provided secret/message

        Args:
            hmac_string (str): Base64 string of the hmac to compare
            secret (str): The secret to be used to generate the hmac to compare
            message (bytes or str): The message to use with in the hmac generation to compare

        Returns:
            bool if hmac matches or not
        """
        return hmac.compare_digest(base64.b64decode(hmac_string), self.create_hmac(secret, message))

    def hmac_message_string(self, http_verb: str, path: str, timestamp: str, content_type: str = "", content: Union[bytes, str] = "") -> str:
        """Generate the HMAC message string given the appropriate inputs

        Args:
            http_verb (str): HTTP verb of the request
            path (str): Full path of the request after the FQDN (including any query parameters) (e.g. /transaction)
            timestamp (str): timestamp of the request (must match timestamp header)
            content_type (str): content-type header of the request (if it exists)
            content (bytes or str): byte object of the body of the request (if it exists)

        Returns:
            string to use as the message in HMAC generation
        """
        return "{}\n{}\n{}\n{}\n{}\n{}".format(
            http_verb.upper(), path, self.dragonchain_id, timestamp, content_type, self.bytes_to_b64_str(self.hash_input(content))
        )

    def get_authorization(self, http_verb: str, path: str, timestamp: str, content_type: str = "", content: Union[bytes, str] = "") -> str:
        """Create an authorization header for making requests to a Dragonchain

        Args:
            http_verb (str): HTTP verb of the request
            path (str): full path of the request after the FQDN (including any query parameters) (e.g. /transaction)
            timestamp (str): timestamp of the request (must match timestamp header)
            content_type (str): content-type header of the request (if it exists)
            content (str or bytes): byte object of the body of the request (if it exists)

        Returns:
            String of generated authorization header
        """
        logger.debug("Creating Authorization header for request {} {}".format(http_verb, path))
        message_string = self.hmac_message_string(http_verb, path, timestamp, content_type, content)
        logger.debug("HMAC message string:\n{}".format(message_string))
        hmac = self.bytes_to_b64_str(self.create_hmac(self.auth_key, message_string))
        logger.debug("Generated Base64 HMAC string: {}".format(hmac))
        return "DC1-HMAC-{} {}:{}".format(self.algorithm, self.auth_key_id, hmac)
