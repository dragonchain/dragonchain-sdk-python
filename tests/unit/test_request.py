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

import unittest
import importlib

import requests
import requests_mock

from tests import unit
from dragonchain_sdk import request
from dragonchain_sdk import credentials
from dragonchain_sdk import exceptions

if unit.PY36:
    from unittest.mock import patch, MagicMock
else:
    from mock import patch, MagicMock


class TestRequestsInitialization(unittest.TestCase):
    def setUp(self):
        self.creds = credentials.Credentials(dragonchain_id="TestID", auth_key="TestKey", auth_key_id="TestKeyId")

    @unittest.skipUnless(unit.CI_COVERAGE_VERSION, "Only run this test for code coverage purposes")
    @patch("typing.TYPE_CHECKING", True)
    def test_type_checking(self):
        importlib.reload(request)

    def test_initialization_raises_type_error(self):
        self.assertRaises(TypeError, request.Request, "not a credentials service")
        self.assertRaises(TypeError, request.Request, self.creds, verify=[])

    @patch("dragonchain_sdk.request.configuration.get_endpoint", return_value="https://dummy.test")
    def test_initialized_correct(self, mock_get_endpoint):
        test_request = request.Request(self.creds)
        self.assertEqual(test_request.credentials, self.creds)
        self.assertEqual(test_request.endpoint, "https://dummy.test")
        self.assertTrue(test_request.verify)


class TestRequestsMethods(unittest.TestCase):
    def setUp(self):
        self.creds = credentials.Credentials(dragonchain_id="TestID", auth_key="TestKey", auth_key_id="TestKeyId")
        self.request = request.Request(self.creds, endpoint="https://dummy.test")

    @patch("dragonchain_sdk.request.configuration.get_endpoint", return_value="hi")
    def test_update_endpoint_no_params(self, mock_get_endpoint):
        self.creds.dragonchain_id = "TestID2"
        self.request.update_endpoint()
        mock_get_endpoint.assert_called_once_with("TestID2")
        self.assertEqual(self.request.endpoint, "hi")

    def test_update_endpoint(self):
        self.request.update_endpoint("https://newurl.com")
        self.assertEqual(self.request.endpoint, "https://newurl.com")

    def test_update_endpoint_raises_type_error(self):
        self.assertRaises(TypeError, self.request.update_endpoint, [])
        self.assertRaises(TypeError, self.request.update_endpoint, {})
        self.assertRaises(TypeError, self.request.update_endpoint, 1234)

    @patch("dragonchain_sdk.request.Request._make_request", return_value="response")
    def test_get_calls_make_request(self, mock_request):
        self.assertEqual(self.request.get("/test"), "response")
        mock_request.assert_called_once_with(http_verb="GET", path="/test", verify=True, parse_response=True)

    @patch("dragonchain_sdk.request.Request._make_request", return_value="response")
    def test_put_calls_make_request(self, mock_request):
        self.assertEqual(self.request.put("/test", {"body": "hello world"}), "response")
        mock_request.assert_called_once_with(http_verb="PUT", path="/test", verify=True, json_content={"body": "hello world"}, parse_response=True)

    @patch("dragonchain_sdk.request.Request._make_request", return_value="response")
    def test_post_calls_make_request(self, mock_request):
        self.assertEqual(self.request.post("/test", {"body": "hello world"}), "response")
        mock_request.assert_called_once_with(
            additional_headers={}, http_verb="POST", path="/test", verify=True, json_content={"body": "hello world"}, parse_response=True
        )

    @patch("dragonchain_sdk.request.Request._make_request", return_value="response")
    def test_post_calls_make_request_with_additional_headers(self, mock_request):
        self.assertEqual(self.request.post("/test", {"body": "hello world"}, additional_headers={"banana": True}), "response")
        mock_request.assert_called_once_with(
            additional_headers={"banana": True},
            http_verb="POST",
            path="/test",
            verify=True,
            json_content={"body": "hello world"},
            parse_response=True,
        )

    @patch("dragonchain_sdk.request.Request._make_request", return_value="response")
    def test_delete_calls_make_request(self, mock_request):
        self.assertEqual(self.request.delete("/test"), "response")
        mock_request.assert_called_once_with(http_verb="DELETE", path="/test", verify=True, parse_response=True)

    @patch("dragonchain_sdk.request.Request._make_request", return_value="response")
    def test_patch_calls_make_request(self, mock_request):
        self.assertEqual(self.request.patch("/test", {"data": "banana"}), "response")
        mock_request.assert_called_once_with(http_verb="PATCH", path="/test", json_content={"data": "banana"}, verify=True, parse_response=True)

    def test_get_request_method_raises_type_error(self):
        self.assertRaises(TypeError, self.request.get_requests_method, [])
        self.assertRaises(TypeError, self.request.get_requests_method, {})
        self.assertRaises(TypeError, self.request.get_requests_method, 1234)

    def test_get_request_method_raises_value_error(self):
        self.assertRaises(ValueError, self.request.get_requests_method, "PLACE")

    def test_get_request_method_returns_get(self):
        self.assertEqual(self.request.get_requests_method("GET"), requests.get)
        self.assertEqual(self.request.get_requests_method("get"), requests.get)

    def test_get_request_method_returns_post(self):
        self.assertEqual(self.request.get_requests_method("POST"), requests.post)
        self.assertEqual(self.request.get_requests_method("post"), requests.post)

    def test_get_request_method_returns_put(self):
        self.assertEqual(self.request.get_requests_method("PUT"), requests.put)
        self.assertEqual(self.request.get_requests_method("put"), requests.put)

    def test_get_request_method_returns_patch(self):
        self.assertEqual(self.request.get_requests_method("PATCH"), requests.patch)
        self.assertEqual(self.request.get_requests_method("patch"), requests.patch)

    def test_get_request_method_returns_delete(self):
        self.assertEqual(self.request.get_requests_method("DELETE"), requests.delete)
        self.assertEqual(self.request.get_requests_method("delete"), requests.delete)

    def test_get_request_method_returns_head(self):
        self.assertEqual(self.request.get_requests_method("HEAD"), requests.head)
        self.assertEqual(self.request.get_requests_method("head"), requests.head)

    def test_get_request_method_returns_options(self):
        self.assertEqual(self.request.get_requests_method("OPTIONS"), requests.options)
        self.assertEqual(self.request.get_requests_method("options"), requests.options)

    def test_generate_query_string_raises_type_error(self):
        self.assertRaises(TypeError, self.request.generate_query_string, [])
        self.assertRaises(TypeError, self.request.generate_query_string, "test")
        self.assertRaises(TypeError, self.request.generate_query_string, 1234)

    def test_generate_query_string_returns_empty_string(self):
        self.assertEqual(self.request.generate_query_string({}), "")

    def test_generate_query_string(self):
        query = self.request.generate_query_string({"key1": "val1", "key2": "val2"})
        self.assertEqual(query[0], "?")
        self.assertIn("key1=val1", query)
        self.assertIn("key2=val2", query)
        self.assertEqual(query.count("&"), 1)

    def test_make_headers(self):
        self.assertEqual(
            self.request._make_headers("Timestamp", "Auth", ""), {"dragonchain": "TestID", "timestamp": "Timestamp", "Authorization": "Auth"}
        )
        self.assertEqual(
            self.request._make_headers("Timestamp", "Auth", "application/json"),
            {"dragonchain": "TestID", "timestamp": "Timestamp", "Authorization": "Auth", "Content-Type": "application/json"},
        )

    def test_make_headers_raises_type_error(self):
        self.assertRaises(TypeError, self.request._make_headers, [], "", "")
        self.assertRaises(TypeError, self.request._make_headers, "", [], "")
        self.assertRaises(TypeError, self.request._make_headers, "", "", [])

    def test_generate_request_data_raises_type_error(self):
        self.assertRaises(TypeError, self.request._generate_request_data, "GET", [])

    def test_generate_request_data_raises_value_error(self):
        self.assertRaises(ValueError, self.request._generate_request_data, "GET", "NoSlashPath")

    @patch("dragonchain_sdk.request.datetime.datetime", utcnow=MagicMock(return_value=MagicMock(isoformat=MagicMock(return_value="mock_time"))))
    def test_generate_request_data_returns_correct_params_with_content(self, mock_time):
        self.request.credentials.get_authorization = MagicMock(return_value="dummy_auth")
        response = self.request._generate_request_data("GET", "/path")
        self.assertEqual(
            response, ("https://dummy.test/path", b"", {"Authorization": "dummy_auth", "dragonchain": "TestID", "timestamp": "mock_timeZ"})
        )

    @patch("dragonchain_sdk.request.datetime.datetime", utcnow=MagicMock(return_value=MagicMock(isoformat=MagicMock(return_value="mock_time"))))
    def test_generate_request_data_adds_additional_headers(self, mock_time):
        self.request.credentials.get_authorization = MagicMock(return_value="dummy_auth")
        response = self.request._generate_request_data("GET", "/path", additional_headers={"some": "test"})
        self.assertEqual(
            response,
            ("https://dummy.test/path", b"", {"Authorization": "dummy_auth", "dragonchain": "TestID", "some": "test", "timestamp": "mock_timeZ"}),
        )

    @patch("dragonchain_sdk.request.datetime.datetime", utcnow=MagicMock(return_value=MagicMock(isoformat=MagicMock(return_value="mock_time"))))
    def test_generate_request_data_returns_correct_params_without_content(self, mock_time):
        self.request.credentials.get_authorization = MagicMock(return_value="dummy_auth")
        response = self.request._generate_request_data("POST", "/path", {"some": "content"})
        self.assertEqual(
            response,
            (
                "https://dummy.test/path",
                b'{"some":"content"}',
                {"Authorization": "dummy_auth", "dragonchain": "TestID", "timestamp": "mock_timeZ", "Content-Type": "application/json"},
            ),
        )

    @patch("dragonchain_sdk.request.Request._generate_request_data", return_value=("https://dummy.test/transaction", None, None))
    @patch("dragonchain_sdk.request.Request.get_requests_method")
    def test_make_request_raises_connectionexception_error_on_request_failure(self, mock_get_request, mock_gen_data):
        mock_get_request.return_value = MagicMock(side_effect=Exception)
        self.assertRaises(exceptions.ConnectionException, self.request._make_request, "GET", "/transaction")
        mock_get_request.assert_called_once_with("GET")

    @patch("dragonchain_sdk.request.Request._generate_request_data", return_value=("https://something/transaction", None, None))
    def test_make_request_returns_ok_false_on_bad_response_status(self, mock_gen_data):
        with requests_mock.mock() as m:
            m.get("https://something/transaction", status_code=400, text='{"error": "some error"}')
            expected_response = {"ok": False, "status": 400, "response": {"error": "some error"}}
            self.assertEqual(self.request._make_request("GET", "/transaction"), expected_response)

    @patch("dragonchain_sdk.request.Request._generate_request_data", return_value=("https://something/transaction", None, None))
    def test_make_request_parse_json(self, mock_gen_data):
        with requests_mock.mock() as m:
            m.get("https://something/transaction", status_code=200, json={"test": "object"})
            self.request._make_request("GET", "/transaction")
            expected_response = {"ok": True, "status": 200, "response": {"test": "object"}}
            self.assertEqual(self.request._make_request("GET", "/transaction", parse_response=True), expected_response)

    @patch("dragonchain_sdk.request.Request._generate_request_data", return_value=("https://something/transaction", None, None))
    def test_make_request_no_parse_json(self, mock_gen_data):
        with requests_mock.mock() as m:
            m.get("https://something/transaction", status_code=200, text='{"test": "object"}')
            expected_response = {"ok": True, "status": 200, "response": '{"test": "object"}'}
            self.assertEqual(self.request._make_request("GET", "/transaction", parse_response=False), expected_response)

    @patch("dragonchain_sdk.request.Request._generate_request_data", return_value=("https://something/transaction", None, None))
    @patch("dragonchain_sdk.request.Request.get_requests_method")
    def test_make_request_raises_unexpectedresponseexception_error_on_parse_json_error(self, mock_get_request, mock_gen_data):
        mock_get_request.return_value.return_value.json.side_effect = RuntimeError("JSON Parse Error")
        mock_get_request.return_value.return_value.status_code = 200
        self.assertRaises(exceptions.UnexpectedResponseException, self.request._make_request, "GET", "/transaction")

    @patch("dragonchain_sdk.request.Request._generate_request_data", return_value=("dummy_url", b"some content", {"some": "headers"}))
    @patch("dragonchain_sdk.request.Request.get_requests_method")
    def test_make_request_calls_requests_with_correct_params(self, mock_get_requests, mock_gen_data):
        self.request.credentials.get_authorization = MagicMock(return_value="dummy_auth")
        mock_request = MagicMock()
        mock_get_requests.return_value = mock_request
        self.request._make_request("POST", "/transaction", json_content={"some": "data"})
        mock_request.assert_called_once_with(data=b"some content", headers={"some": "headers"}, timeout=30, url="dummy_url", verify=True)
