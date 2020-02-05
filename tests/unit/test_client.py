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

import os
import logging
import unittest
import importlib

from tests import unit
import dragonchain_sdk
from dragonchain_sdk import dragonchain_client

if unit.PY36:
    from unittest.mock import patch, MagicMock, ANY
else:
    from mock import patch, MagicMock, ANY


@patch("dragonchain_sdk.dragonchain_client.credentials")
@patch("dragonchain_sdk.dragonchain_client.request")
class TestClientInitialization(unittest.TestCase):
    @unittest.skipUnless(unit.CI_COVERAGE_VERSION, "Only run this test for code coverage purposes")
    @patch("typing.TYPE_CHECKING", True)
    def test_type_checking(self, mock_request, mock_creds):
        importlib.reload(dragonchain_client)

    def test_create_client_initializes_correctly_from_module(self, mock_request, mock_creds):
        self.client = dragonchain_sdk.create_client()
        mock_creds.Credentials.assert_called_once_with(None, None, None, "SHA256")
        mock_request.Request.assert_called_once_with(ANY, None, True)

    @patch("dragonchain_sdk.logging")
    def test_set_stream_logger(self, mock_logging, mock_request, mock_creds):
        mock_logger, mock_stream_handler, mock_formatter = MagicMock(), MagicMock(), MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.StreamHandler.return_value = mock_stream_handler
        mock_logging.Formatter.return_value = mock_formatter

        dragonchain_sdk.set_stream_logger(name="TestLogger", level=logging.INFO)

        mock_logging.getLogger.assert_called_once_with("TestLogger")
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.StreamHandler.assert_called_once()
        mock_stream_handler.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.Formatter.assert_called_once_with("%(asctime)s %(name)s [%(levelname)s] %(message)s")
        mock_stream_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_logger.addHandler.assert_called_once_with(mock_stream_handler)

    @patch("dragonchain_sdk.logging")
    def test_set_stream_logger_with_format(self, mock_logging, mock_request, mock_creds):
        mock_logger, mock_stream_handler, mock_formatter = MagicMock(), MagicMock(), MagicMock()
        mock_logging.getLogger.return_value = mock_logger
        mock_logging.StreamHandler.return_value = mock_stream_handler
        mock_logging.Formatter.return_value = mock_formatter

        dragonchain_sdk.set_stream_logger(name="TestLogger", level=logging.INFO, format_string="%(message)s")

        mock_logging.getLogger.assert_called_once_with("TestLogger")
        mock_logger.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.StreamHandler.assert_called_once()
        mock_stream_handler.setLevel.assert_called_once_with(logging.INFO)
        mock_logging.Formatter.assert_called_once_with("%(message)s")
        mock_stream_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_logger.addHandler.assert_called_once_with(mock_stream_handler)

    def test_client_initializes_correctly_no_params(self, mock_request, mock_creds):
        self.client = dragonchain_sdk.create_client()
        mock_creds.Credentials.assert_called_once_with(None, None, None, "SHA256")
        mock_request.Request.assert_called_once_with(ANY, None, True)

    def test_client_initializes_correctly_with_params(self, mock_request, mock_creds):
        self.client = dragonchain_client.Client(
            dragonchain_id="TestID", auth_key="Auth", auth_key_id="AuthID", verify=False, endpoint="endpoint", algorithm="SHA256"
        )
        mock_creds.Credentials.assert_called_once_with("TestID", "Auth", "AuthID", "SHA256")
        mock_request.Request.assert_called_once_with(ANY, "endpoint", False)


@patch("dragonchain_sdk.dragonchain_client.request")
@patch("dragonchain_sdk.dragonchain_client.credentials")
class TestClientMethods(unittest.TestCase):
    def test_validate_and_build_custom_index_fields_array_trims_unnecessary_fields(self, mock_creds, mock_request):
        my_index = {"type": "text", "path": "a.b", "field_name": "myField", "options": {"not_needed": "thing"}, "unnecessary": "stuff"}
        result = dragonchain_client._validate_and_build_custom_index_fields_array([my_index])
        # Remove unnecessary fields and check thats what the validation returned
        del my_index["unnecessary"]
        del my_index["options"]["not_needed"]
        self.assertEqual(result[0], my_index)

    def test_validate_and_build_custom_index_fields_array_extracts_necessary_option_fields(self, mock_creds, mock_request):
        my_index = {"type": "text", "path": "a.b", "field_name": "myField", "options": {}}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)
        my_index["options"] = {"weight": 0.0, "no_stem": True, "sortable": False}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)
        my_index["options"] = {"no_index": True}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)
        my_index["type"] = "tag"
        my_index["options"] = {"separator": "thing"}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)
        my_index["options"] = {"no_index": True}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)
        my_index["type"] = "number"
        my_index["options"] = {"sortable": True}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)
        my_index["options"] = {"no_index": True}
        self.assertEqual(dragonchain_client._validate_and_build_custom_index_fields_array([my_index])[0], my_index)

    def test_validate_and_build_custom_index_fields_array_checks_root_fields(self, mock_creds, mock_request):
        my_index = {"type": "text", "path": "a.b", "field_name": "myField", "options": 123}
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, ["not_valid"])
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["field_name"] = 123
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["type"] = 123
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["path"] = 123
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])

    def test_validate_and_build_custom_index_fields_array_checks_option_types(self, mock_creds, mock_request):
        my_index = {
            "type": "text",
            "path": "a.b",
            "field_name": "myField",
            "options": {"separator": ",", "no_index": False, "weight": 0.0, "no_stem": False, "sortable": "bogus"},
        }
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["options"]["no_stem"] = "bogus"
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["options"]["weight"] = "bogus"
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["options"]["no_index"] = "bogus"
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])
        my_index["options"]["separator"] = 123
        self.assertRaises(TypeError, dragonchain_client._validate_and_build_custom_index_fields_array, [my_index])

    def test_build_transaction_dict_raises_type_error(self, mock_creds, mock_request):
        self.assertRaises(TypeError, dragonchain_client._build_transaction_dict, {}, {"fake": "payload"}, 'Tag:"value"')
        self.assertRaises(TypeError, dragonchain_client._build_transaction_dict, "FAKEtransaction", [], 'Tag:"value"')
        self.assertRaises(TypeError, dragonchain_client._build_transaction_dict, "FAKEtransaction", {"fake": "payload"}, {})
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_build_transaction_dict_returns_dict(self, mock_creds, mock_request):
        self.assertEqual(
            dragonchain_client._build_transaction_dict("FAKEtransaction", {}, 'Tag:"value"'),
            {"version": "1", "txn_type": "FAKEtransaction", "payload": {}, "tag": 'Tag:"value"'},
        )
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_build_transaction_dict_returns_dict_no_tag(self, mock_creds, mock_request):
        self.assertEqual(
            dragonchain_client._build_transaction_dict("FAKEtransaction", {}), {"version": "1", "txn_type": "FAKEtransaction", "payload": {}}
        )
        mock_creds.assert_not_called()
        mock_request.assert_not_called()

    def test_get_smart_contract_secret_throws_type_error(self, mock_creds, mock_request):
        os.environ["SMART_CONTRACT_ID"] = ""
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_smart_contract_secret, None)
        self.assertRaises(RuntimeError, self.client.get_smart_contract_secret, "valid_secret")

    @patch("dragonchain_sdk.dragonchain_client.open")
    def test_get_smart_contract_secret_calls_open(self, mock_open, mock_creds, mock_request):
        os.environ["SMART_CONTRACT_ID"] = "bogusSCID"
        self.client = dragonchain_sdk.create_client()
        mock_open.return_value.read.return_value = "fakeSecret"
        self.client.credentials.dragonchain_id = "fakeDragonchainId"
        self.client.get_smart_contract_secret("mySecret")
        path = os.path.join(os.path.abspath(os.sep), "var", "openfaas", "secrets", "sc-bogusSCID-mySecret")
        mock_open.assert_called_once_with(path, "r")

    def test_get_smart_contract_logs_calls_get(self, mock_creds, mock_request):
        mock_request.Request.return_value.generate_query_string.return_value = ""
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract_logs("my-id", tail=None)
        self.client.request.get.assert_called_once_with("/v1/contract/my-id/logs")

    def test_get_smart_contract_logs_calls_get_with_parameters(self, mock_creds, mock_request):
        mock_request.Request.return_value.generate_query_string.return_value = "?whatever"
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract_logs("my-id", 1000, "my-date")
        self.client.request.get.assert_called_once_with("/v1/contract/my-id/logs?whatever")
        self.client.request.generate_query_string.assert_called_once_with({"tail": 1000, "since": "my-date"})

    def test_get_smart_contract_logs_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_smart_contract_logs, 1234)
        self.assertRaises(TypeError, self.client.get_smart_contract_logs, "my-id", tail="bad type")
        self.assertRaises(TypeError, self.client.get_smart_contract_logs, "my-id", since=1)

    def test_get_smart_contract_logs_throws_value_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(ValueError, self.client.get_smart_contract_logs, None)

    def test_get_status_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_status()
        self.client.request.get.assert_called_once_with("/v1/status")

    def test_list_smart_contracts_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_smart_contracts()
        self.client.request.get.assert_called_once_with("/v1/contract")

    def test_get_smart_contract_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_smart_contract, 1234, "str")
        self.assertRaises(TypeError, self.client.get_smart_contract, "str", 1234)
        self.assertRaises(TypeError, self.client.get_smart_contract, "str", "str")

    def test_get_smart_contract_throws_value_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(ValueError, self.client.get_smart_contract)

    def test_get_smart_contract_with_id_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract("some_id")
        self.client.request.get.assert_called_once_with("/v1/contract/some_id")

    def test_get_smart_contract_with_transaction_type_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract(transaction_type="Name")
        self.client.request.get.assert_called_once_with("/v1/contract/txn_type/Name")

    def test_create_smart_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_smart_contract, transaction_type=[], image="valid", cmd="valid")
        self.assertRaises(TypeError, self.client.create_smart_contract, transaction_type="valid", image=[], cmd="valid")
        self.assertRaises(TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd=[])
        self.assertRaises(TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args="FAIL")
        self.assertRaises(
            TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args=["valid"], execution_order=[]
        )
        self.assertRaises(
            ValueError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args=["valid"], execution_order="FAIL"
        )
        self.assertRaises(
            TypeError,
            self.client.create_smart_contract,
            transaction_type="valid",
            image="valid",
            cmd="",
            args=["valid"],
            environment_variables="FAIL",
        )
        self.assertRaises(
            TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args=["valid"], secrets="FAIL"
        )
        self.assertRaises(
            TypeError,
            self.client.create_smart_contract,
            transaction_type="valid",
            image="valid",
            cmd="",
            args=["valid"],
            schedule_interval_in_seconds="FAIL",
        )
        self.assertRaises(
            ValueError,
            self.client.create_smart_contract,
            transaction_type="valid",
            image="valid",
            cmd="",
            args=["valid"],
            schedule_interval_in_seconds=99999,
            cron_expression="FAIL",
        )
        self.assertRaises(
            TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args=["valid"], cron_expression=[]
        )
        self.assertRaises(
            TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args=["valid"], registry_credentials=[]
        )
        self.assertRaises(
            TypeError, self.client.create_smart_contract, transaction_type="valid", image="valid", cmd="", args=["valid"], custom_index_fields="blah"
        )

    def test_create_smart_contract_calls_post(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial", environment_variables={"test": "env"})
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {"version": "3", "txn_type": "Name", "image": "ubuntu:latest", "cmd": "python3.6", "execution_order": "serial", "env": {"test": "env"}},
        )

    def test_create_smart_contract_enabled_false(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial")
        self.client.request.post.assert_called_once_with(
            "/v1/contract", {"version": "3", "txn_type": "Name", "image": "ubuntu:latest", "cmd": "python3.6", "execution_order": "serial"}
        )

    def test_post_custom_contract_calls_post_with_args(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", ["something"], "serial", environment_variables={"test": "env"})
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {
                "version": "3",
                "txn_type": "Name",
                "image": "ubuntu:latest",
                "cmd": "python3.6",
                "execution_order": "serial",
                "env": {"test": "env"},
                "args": ["something"],
            },
        )

    def test_create_smart_contract_calls_post_with_secrets(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial", None, None, 1)
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {"version": "3", "txn_type": "Name", "image": "ubuntu:latest", "cmd": "python3.6", "execution_order": "serial", "seconds": 1},
        )

    def test_create_smart_contract_calls_post_with_cron(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial", None, None, None, "* * *")
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {"version": "3", "txn_type": "Name", "image": "ubuntu:latest", "cmd": "python3.6", "execution_order": "serial", "cron": "* * *"},
        )

    def test_create_smart_contract_calls_post_with_auth(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial", None, None, None, None, "auth")
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {"version": "3", "txn_type": "Name", "image": "ubuntu:latest", "cmd": "python3.6", "execution_order": "serial", "auth": "auth"},
        )

    def test_create_smart_contract_calls_post_with_seconds(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial", None, {"secret": "test"})
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {
                "version": "3",
                "txn_type": "Name",
                "image": "ubuntu:latest",
                "cmd": "python3.6",
                "execution_order": "serial",
                "secrets": {"secret": "test"},
            },
        )

    def test_create_smart_contract_calls_post_no_env(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract("Name", "ubuntu:latest", "python3.6", None, "serial")
        self.client.request.post.assert_called_once_with(
            "/v1/contract", {"version": "3", "txn_type": "Name", "image": "ubuntu:latest", "cmd": "python3.6", "execution_order": "serial"}
        )

    def test_create_smart_contract_calls_post_with_custom_indexes(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_smart_contract(
            "Name", "ubuntu:latest", "python3.6", custom_index_fields=[{"type": "text", "field_name": "myField", "path": "a.b"}]
        )
        self.client.request.post.assert_called_once_with(
            "/v1/contract",
            {
                "version": "3",
                "txn_type": "Name",
                "image": "ubuntu:latest",
                "cmd": "python3.6",
                "execution_order": "parallel",
                "custom_indexes": [{"path": "a.b", "type": "text", "field_name": "myField", "options": {}}],
            },
        )

    def test_update_smart_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", image=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", cmd=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", execution_order=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", desired_state=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", args={})
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", environment_variables=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", secrets=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", schedule_interval_in_seconds="seconds")
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", cron_expression=1)
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", registry_credentials=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", enabled=[])
        self.assertRaises(TypeError, self.client.update_smart_contract, smart_contract_id="some_id", disable_schedule=[])
        self.assertRaises(ValueError, self.client.update_smart_contract, smart_contract_id="some_id", execution_order="asdasd")

    def test_update_smart_contract_calls_put_no_env(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", enabled=False, execution_order="parallel", environment_variables=None)
        self.client.request.put.assert_called_once_with(
            "/v1/contract/some_id", {"version": "3", "execution_order": "parallel", "desired_state": "inactive"}
        )

    def test_update_smart_contract_calls_enabled_false(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", enabled=True, execution_order="parallel", environment_variables=None)
        self.client.request.put.assert_called_once_with(
            "/v1/contract/some_id", {"version": "3", "desired_state": "active", "execution_order": "parallel"}
        )

    def test_update_smart_contract_calls_put(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(
            smart_contract_id="some_id", enabled=True, execution_order="parallel", environment_variables={"test": "env"}
        )
        self.client.request.put.assert_called_once_with(
            "/v1/contract/some_id", {"version": "3", "execution_order": "parallel", "desired_state": "active", "env": {"test": "env"}}
        )

    def test_update_smart_contract_calls_put_with_image(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", image="sampleImage")
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "image": "sampleImage"})

    def test_update_smart_contract_calls_put_with_cmd(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", cmd="command")
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "cmd": "command"})

    def test_update_smart_contract_calls_put_with_args(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", args=["arg"])
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "args": ["arg"]})

    def test_update_smart_contract_calls_put_with_secrets(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", secrets={"secret": "value"})
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "secrets": {"secret": "value"}})

    def test_update_smart_contract_calls_put_with_seconds(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", schedule_interval_in_seconds=1)
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "seconds": 1})

    def test_update_smart_contract_calls_put_with_cron(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", cron_expression="* * *")
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "cron": "* * *"})

    def test_update_smart_contract_calls_put_with_auth(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", registry_credentials="auth")
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "auth": "auth"})

    def test_update_smart_contract_calls_put_with_disable_schedule(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_smart_contract(smart_contract_id="some_id", disable_schedule=True)
        self.client.request.put.assert_called_once_with("/v1/contract/some_id", {"version": "3", "disable_schedule": True})

    def test_delete_smart_contract_raises_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_smart_contract, 1)

    def test_delete_smart_contract_raises_type_error_when_txn_type_is_not_str(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_smart_contract, None, 1)

    def test_delete_smart_contract_raises_type_error_when_nothing_specified(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_smart_contract)

    def test_delete_smart_contract_raises_type_error_when_both_values_present(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_smart_contract, "some_id", "some_name")

    def test_delete_smart_contract_calls_delete(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.delete_smart_contract(smart_contract_id="some_id")
        self.client.request.delete.assert_called_once_with("/v1/contract/some_id")

    def test_delete_smart_contract_calls_delete_with_transaction_type(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.delete_smart_contract(transaction_type="some_name")
        self.client.request.delete.assert_called_once_with("/v1/contract/txn_type/some_name")

    def test_query_transactions_calls_get_with_params(self, mock_creds, mock_request):
        mock_request.Request.return_value.generate_query_string.return_value = "?whatever"
        self.client = dragonchain_sdk.create_client()
        self.client.query_transactions("txn_type", "irrelevant_query")
        self.client.request.generate_query_string.assert_called_once_with(
            {"transaction_type": "txn_type", "q": "irrelevant_query", "verbatim": False, "offset": 0, "limit": 10, "id_only": False}
        )
        self.client.request.get.assert_called_once_with("/v1/transaction?whatever")

    def test_query_transactions_adds_sort_by_when_provided(self, mock_creds, mock_request):
        mock_request.Request.return_value.generate_query_string.return_value = "?whatever"
        self.client = dragonchain_sdk.create_client()
        self.client.query_transactions("txn_type", "irrelevant_query", sort_by="field", sort_ascending=False)
        self.client.request.generate_query_string.assert_called_once_with(
            {
                "transaction_type": "txn_type",
                "q": "irrelevant_query",
                "verbatim": False,
                "offset": 0,
                "limit": 10,
                "id_only": False,
                "sort_by": "field",
                "sort_asc": False,
            }
        )

    def test_query_transactions_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.query_transactions)
        self.assertRaises(TypeError, self.client.query_transactions, 1234, "q")
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", 1234)
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", "q", 1234)
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", "q", True, "abc")
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", "q", True, 1, "abc")
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", "q", True, 1, 1, 123)
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", "q", True, 1, 1, "field", 123)
        self.assertRaises(TypeError, self.client.query_transactions, "txn_type", "q", True, 1, 1, "field", True, 123)

    def test_post_bulk_transaction_raises_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_bulk_transaction, {})
        self.assertRaises(TypeError, self.client.create_bulk_transaction, [1234, "not a dict"])

    def test_post_bulk_transaction_calls_posts(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_bulk_transaction(
            [
                {"transaction_type": "TEST_transaction", "payload": {"Test": "Payload"}, "tag": 'Test:"Tag"'},
                {"transaction_type": "TEST_transaction2", "payload": {"Test": "Payload"}, "tag": 'Test:"Tag"'},
            ]
        )
        self.client.request.post.assert_called_once_with(
            "/v1/transaction_bulk",
            [
                {"version": "1", "txn_type": "TEST_transaction", "payload": {"Test": "Payload"}, "tag": 'Test:"Tag"'},
                {"version": "1", "txn_type": "TEST_transaction2", "payload": {"Test": "Payload"}, "tag": 'Test:"Tag"'},
            ],
        )

    def test_create_transaction_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_transaction, transaction_type=[], payload={})
        self.assertRaises(TypeError, self.client.create_transaction, transaction_type="Test", payload=[])
        self.assertRaises(TypeError, self.client.create_transaction, transaction_type="Test", payload={}, tag=[])

    def test_create_transaction_calls_post_with_dict_payload(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_transaction(
            transaction_type="TEST_transaction", payload={"hello": "world"}, tag='MyTag:"value" OtherTag:"other value"', callback_url="banana"
        )
        self.client.request.post.assert_called_once_with(
            "/v1/transaction",
            {"version": "1", "txn_type": "TEST_transaction", "payload": {"hello": "world"}, "tag": 'MyTag:"value" OtherTag:"other value"'},
            additional_headers={"X-Callback-Url": "banana"},
        )

    def test_create_transaction_calls_post_with_no_tag(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_transaction(transaction_type="TEST_transaction", payload={"hello": "world"})
        self.client.request.post.assert_called_once_with(
            "/v1/transaction", {"version": "1", "txn_type": "TEST_transaction", "payload": {"hello": "world"}}, additional_headers={}
        )

    def test_create_transaction_calls_post_with_str_payload(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_transaction(transaction_type="TEST_transaction", payload="Hello world", tag='MyTag:"value" OtherTag:"other value"')
        self.client.request.post.assert_called_once_with(
            "/v1/transaction",
            {"version": "1", "txn_type": "TEST_transaction", "payload": "Hello world", "tag": 'MyTag:"value" OtherTag:"other value"'},
            additional_headers={},
        )

    def test_get_transaction_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_transaction, [])
        self.assertRaises(TypeError, self.client.get_transaction, {})
        self.assertRaises(TypeError, self.client.get_transaction, 1234)
        self.assertRaises(TypeError, self.client.get_transaction, ())

    def test_get_transaction_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_transaction("Test")
        self.client.request.get.assert_called_once_with("/v1/transaction/Test")

    def test_query_blocks_calls_get_with_params(self, mock_creds, mock_request):
        mock_request.Request.return_value.generate_query_string.return_value = "?whatever"
        self.client = dragonchain_sdk.create_client()
        self.client.query_blocks("irrelevant")
        self.client.request.generate_query_string.assert_called_once_with({"q": "irrelevant", "offset": 0, "limit": 10, "id_only": False})
        self.client.request.get.assert_called_once_with("/v1/block?whatever")

    def test_query_blocks_adds_sort_by_when_provided(self, mock_creds, mock_request):
        mock_request.Request.return_value.generate_query_string.return_value = "?whatever"
        self.client = dragonchain_sdk.create_client()
        self.client.query_blocks("irrelevant", sort_by="field", sort_ascending=False)
        self.client.request.generate_query_string.assert_called_once_with(
            {"q": "irrelevant", "offset": 0, "limit": 10, "id_only": False, "sort_by": "field", "sort_asc": False}
        )

    def test_query_blocks_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.query_blocks)
        self.assertRaises(TypeError, self.client.query_blocks, 1234)
        self.assertRaises(TypeError, self.client.query_blocks, "q", "abc")
        self.assertRaises(TypeError, self.client.query_blocks, "q", 1, "abc")
        self.assertRaises(TypeError, self.client.query_blocks, "q", 1, 1, 123)
        self.assertRaises(TypeError, self.client.query_blocks, "q", 1, 1, "field", 123)
        self.assertRaises(TypeError, self.client.query_blocks, "q", 1, 1, "field", True, 123)

    def test_get_block_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_block, [])
        self.assertRaises(TypeError, self.client.get_block, {})
        self.assertRaises(TypeError, self.client.get_block, ())

    def test_get_block_calls_get_with_string(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_block("1234")
        self.client.request.get.assert_called_once_with("/v1/block/1234")

    def test_get_pending_verifications_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_pending_verifications, [])
        self.assertRaises(TypeError, self.client.get_pending_verifications, {})
        self.assertRaises(TypeError, self.client.get_pending_verifications, ())
        self.assertRaises(TypeError, self.client.get_pending_verifications, 123)

    def test_get_pending_verifications_calls_get_with_correct_path(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_pending_verifications("123")
        self.client.request.get.assert_called_once_with("/v1/verifications/pending/123")

    def test_get_verifications_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_verifications, [])
        self.assertRaises(TypeError, self.client.get_verifications, {})
        self.assertRaises(TypeError, self.client.get_verifications, ())
        self.assertRaises(TypeError, self.client.get_verifications, "1234", level=[])
        self.assertRaises(TypeError, self.client.get_verifications, "1234", level={})
        self.assertRaises(TypeError, self.client.get_verifications, "1234", level=())

    def test_get_verifications_throws_value_error_on_level_out_of_range(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(ValueError, self.client.get_verifications, "1234", level=6)
        self.assertRaises(TypeError, self.client.get_verifications, "1234", level="6")
        self.assertRaises(ValueError, self.client.get_verifications, "1234", level=1)
        self.assertRaises(TypeError, self.client.get_verifications, "1234", level="1")
        self.assertRaises(TypeError, self.client.get_verifications, 1234, level=6)
        self.assertRaises(TypeError, self.client.get_verifications, 1234, level="6")
        self.assertRaises(TypeError, self.client.get_verifications, 1234, level=1)
        self.assertRaises(TypeError, self.client.get_verifications, 1234, level="1")

    def test_get_verifications_calls_get_with_string(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_verifications("1234")
        self.client.request.get.assert_called_once_with("/v1/verifications/1234")

    def test_get_verifications_calls_get_with_string_and_level_integer(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_verifications("1234", level=5)
        self.client.request.get.assert_called_once_with("/v1/verifications/1234?level=5")

    def test_get_smart_contract_object_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_smart_contract_object, key=[], smart_contract_id="Test")
        self.assertRaises(TypeError, self.client.get_smart_contract_object, key=[])
        self.assertRaises(TypeError, self.client.get_smart_contract_object, key="MyKey", smart_contract_id=[])

    @patch.dict(os.environ, {"SMART_CONTRACT_ID": "MyName"})
    def test_get_smart_contract_object_reads_env_and_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract_object(key="MyKey")
        self.client.request.get.assert_called_once_with("/v1/get/MyName/MyKey", parse_response=False)

    @patch.dict(os.environ, {"SMART_CONTRACT_ID": "MyName"})
    def test_get_smart_contract_object_reads_env_and_calls_get_with_override(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract_object(smart_contract_id="Override", key="MyKey")
        self.client.request.get.assert_called_once_with("/v1/get/Override/MyKey", parse_response=False)

    def test_get_smart_contract_object_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_smart_contract_object(key="MyKey", smart_contract_id="MyContract")
        self.client.request.get.assert_called_once_with("/v1/get/MyContract/MyKey", parse_response=False)

    def test_list_smart_contract_objects_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.list_smart_contract_objects, prefix_key=[], smart_contract_id="MyContract")
        self.assertRaises(TypeError, self.client.list_smart_contract_objects, prefix_key="MyFolder", smart_contract_id=[])

    def test_list_smart_contract_objects_throws_value_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(ValueError, self.client.list_smart_contract_objects, prefix_key="MyFolder/", smart_contract_id="MyContract")

    @patch.dict(os.environ, {"SMART_CONTRACT_ID": "MyName"})
    def test_list_smart_contract_objects_reads_env_and_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_smart_contract_objects(prefix_key="MyFolder")
        self.client.request.get.assert_called_once_with("/v1/list/MyName/MyFolder/")

    @patch.dict(os.environ, {"SMART_CONTRACT_ID": "MyName"})
    def test_list_smart_contract_objects_reads_env_and_calls_get_with_override(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_smart_contract_objects(smart_contract_id="Override", prefix_key="MyFolder")
        self.client.request.get.assert_called_once_with("/v1/list/Override/MyFolder/")

    def test_list_smart_contract_objects_calls_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_smart_contract_objects(smart_contract_id="MyContract", prefix_key="MyFolder")
        self.client.request.get.assert_called_once_with("/v1/list/MyContract/MyFolder/")

    def test_list_smart_contract_objects_calls_get_root(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_smart_contract_objects(smart_contract_id="MyContract")
        self.client.request.get.assert_called_once_with("/v1/list/MyContract/")

    def test_create_transaction_type_calls_post_without_custom_indexes(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_transaction_type("MyNewType")
        self.client.request.post.assert_called_once_with("/v1/transaction-type", {"version": "2", "txn_type": "MyNewType"})

    def test_create_transaction_type_calls_post_with_custom_indexes(self, mock_creds, mock_request):
        custom_indexes = [{"path": "a.b", "field_name": "myField", "type": "text", "options": {}}]
        self.client = dragonchain_sdk.create_client()
        self.client.create_transaction_type("MyNewType", custom_indexes)
        self.client.request.post.assert_called_once_with(
            "/v1/transaction-type", {"version": "2", "txn_type": "MyNewType", "custom_indexes": custom_indexes}
        )

    def test_create_transaction_type_raises_errors(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_transaction_type, {})
        self.assertRaises(TypeError, self.client.create_transaction_type, "myType", "not a list")

    def test_delete_transaction_type_calls_delete(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.delete_transaction_type("MyCurrentType")
        self.client.request.delete.assert_called_once_with("/v1/transaction-type/MyCurrentType")

    def test_delete_transaction_type_raises_error_type_not_string(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_transaction_type, {})

    def test_get_transaction_type_raises_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_transaction_type, {})

    def test_get_transaction_type_succeeds(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_transaction_type("myType")
        self.client.request.get.assert_called_once_with("/v1/transaction-type/myType")

    def test_list_transaction_types_succeeds(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_transaction_types()
        self.client.request.get.assert_called_once_with("/v1/transaction-types")

    def test_public_blockchain_transaction_create(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_transaction_types()
        self.client.request.get.assert_called_once_with("/v1/transaction-types")

    def test_public_blockchain_address_get(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_public_blockchain_addresses()
        self.client.request.get.assert_called_once_with("/v1/public-blockchain-address")

    def test_create_bitcoin_transaction_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_bitcoin_transaction, "BTC_MAINNET", [], "data")
        self.assertRaises(TypeError, self.client.create_bitcoin_transaction, "BTC_MAINNET", 1, [])
        self.assertRaises(TypeError, self.client.create_bitcoin_transaction, "BTC_MAINNET", 1, "data", [])
        self.assertRaises(TypeError, self.client.create_bitcoin_transaction, "BTC_MAINNET", 1, "data", outputs="FAIL")
        self.assertRaises(ValueError, self.client.create_bitcoin_transaction, "FAIL", 1, "data")

    def test_create_bitcoin_transaction(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_bitcoin_transaction("BTC_MAINNET", 1, data="0x0", outputs=["banana"], change_address="apples")
        self.client.request.post.assert_called_once_with(
            "/v1/public-blockchain-transaction",
            body={"network": "BTC_MAINNET", "transaction": {"version": "1", "fee": 1, "data": "0x0", "outputs": ["banana"], "change": "apples"}},
        )

    def test_create_bitcoin_transaction_default_only(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_bitcoin_transaction("BTC_MAINNET")
        self.client.request.post.assert_called_once_with(
            "/v1/public-blockchain-transaction", body={"network": "BTC_MAINNET", "transaction": {"version": "1"}}
        )

    def test_create_ethereum_transaction_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_ethereum_transaction, "ETH_MAINNET", [], "value")
        self.assertRaises(TypeError, self.client.create_ethereum_transaction, "ETH_MAINNET", "to", [])
        self.assertRaises(TypeError, self.client.create_ethereum_transaction, "ETH_MAINNET", "to", "value", [])
        self.assertRaises(TypeError, self.client.create_ethereum_transaction, "ETH_MAINNET", "to", "value", "data", [])
        self.assertRaises(TypeError, self.client.create_ethereum_transaction, "ETH_MAINNET", "to", "value", "data", "gas_price", [])
        self.assertRaises(ValueError, self.client.create_ethereum_transaction, "NEO_MAINNET", "flim_flam", "potato")

    def test_create_ethereum_transaction(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_ethereum_transaction("ETH_ROPSTEN", "0x0000000000000000000000000000000000000000", "0x0")
        self.client.request.post.assert_called_once_with(
            "/v1/public-blockchain-transaction",
            body={"network": "ETH_ROPSTEN", "transaction": {"version": "1", "to": "0x0000000000000000000000000000000000000000", "value": "0x0"}},
        )

    def test_create_ethereum_transaction_with_data(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_ethereum_transaction("ETH_ROPSTEN", "0x0000000000000000000000000000000000000000", "0x0", data="Banana")
        self.client.request.post.assert_called_once_with(
            "/v1/public-blockchain-transaction",
            body={
                "network": "ETH_ROPSTEN",
                "transaction": {"version": "1", "to": "0x0000000000000000000000000000000000000000", "value": "0x0", "data": "Banana"},
            },
        )

    def test_create_ethereum_transaction_with_gas_price(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_ethereum_transaction("ETH_ROPSTEN", "0x0000000000000000000000000000000000000000", "0x0", data="Banana", gas_price="1")
        self.client.request.post.assert_called_once_with(
            "/v1/public-blockchain-transaction",
            body={
                "network": "ETH_ROPSTEN",
                "transaction": {
                    "version": "1",
                    "to": "0x0000000000000000000000000000000000000000",
                    "value": "0x0",
                    "data": "Banana",
                    "gasPrice": "1",
                },
            },
        )

    def test_create_ethereum_transaction_with_gas(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_ethereum_transaction(
            "ETH_ROPSTEN", "0x0000000000000000000000000000000000000000", "0x0", data="Banana", gas_price="1", gas="2"
        )
        self.client.request.post.assert_called_once_with(
            "/v1/public-blockchain-transaction",
            body={
                "network": "ETH_ROPSTEN",
                "transaction": {
                    "version": "1",
                    "to": "0x0000000000000000000000000000000000000000",
                    "value": "0x0",
                    "data": "Banana",
                    "gasPrice": "1",
                    "gas": "2",
                },
            },
        )

    def test_create_api_key_throws_with_type_errors(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_api_key, 1234)
        self.assertRaises(TypeError, self.client.create_api_key, "nickname", 1234)

    def test_create_api_key(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_api_key(nickname="nickname", permissions_document={"version": "1", "default_allow": True, "permissions": {}})
        self.client.request.post.assert_called_once_with(
            "/v1/api-key", {"nickname": "nickname", "permissions_document": {"version": "1", "default_allow": True, "permissions": {}}}
        )

    def test_creaste_api_key_succeeds_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_api_key()
        self.client.request.post.assert_called_once_with("/v1/api-key", {})

    def test_delete_api_key(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.delete_api_key("MyKeyID")
        self.client.request.delete.assert_called_once_with("/v1/api-key/MyKeyID")

    def test_delete_api_key_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_api_key, 1234)

    def test_get_api_key(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_api_key("MyKeyID")
        self.client.request.get.assert_called_once_with("/v1/api-key/MyKeyID")

    def test_get_api_key_throws_type_error(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_api_key, 1234)

    def test_list_api_keys(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_api_keys()
        self.client.request.get.assert_called_once_with("/v1/api-key")

    def test_update_api_key_throws_type_errors(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.update_api_key, 1234)
        self.assertRaises(TypeError, self.client.update_api_key, "1234", 1234)
        self.assertRaises(TypeError, self.client.update_api_key, "1234", "nickname", 1234)

    def test_update_api_key_succeeds(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_api_key(key_id="id", nickname="newName", permissions_document={"version": "1", "default_allow": True, "permissions": {}})
        self.client.request.put.assert_called_once_with(
            "/v1/api-key/id", {"nickname": "newName", "permissions_document": {"version": "1", "default_allow": True, "permissions": {}}}
        )

    def test_update_api_key_succeeds_with_defaults(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_api_key("key_id")
        self.client.request.put.assert_called_once_with("/v1/api-key/key_id", {})

    def test_get_default_interchain_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_default_interchain_network()
        self.client.request.get.assert_called_once_with("/v1/interchains/default")

    def test_set_default_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.set_default_interchain_network, 1, "a")
        self.assertRaises(TypeError, self.client.set_default_interchain_network, "a", 1)

    def test_set_default_interchain_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.set_default_interchain_network("a", "b")
        self.client.request.post.assert_called_once_with("/v1/interchains/default", {"version": "1", "blockchain": "a", "name": "b"})

    def test_publish_interchain_transaction_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.publish_interchain_transaction, 1, "b", "c")
        self.assertRaises(TypeError, self.client.publish_interchain_transaction, "a", 2, "c")
        self.assertRaises(TypeError, self.client.publish_interchain_transaction, "a", "b", 3)

    def test_publish_interchain_transaction_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        -self.client.publish_interchain_transaction("a", "b", "c")
        self.client.request.post.assert_called_once_with(
            "/v1/interchains/transaction/publish", {"version": "1", "blockchain": "a", "name": "b", "signed_txn": "c"}
        )

    def test_list_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.list_interchain_networks, 1)

    def test_list_interchain_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.list_interchain_networks("a")
        self.client.request.get.assert_called_once_with("/v1/interchains/a")

    def test_delete_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.delete_interchain_network, 1, "a")
        self.assertRaises(TypeError, self.client.delete_interchain_network, "a", 1)

    def test_delete_interchain_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.delete_interchain_network("a", "b")
        self.client.request.delete.assert_called_once_with("/v1/interchains/a/b")

    def test_get_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.get_interchain_network, 1, "a")
        self.assertRaises(TypeError, self.client.get_interchain_network, "a", 1)

    def test_get_interchain_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.get_interchain_network("a", "b")
        self.client.request.get.assert_called_once_with("/v1/interchains/a/b")

    def test_create_bitcoin_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_bitcoin_interchain, 1)
        self.assertRaises(TypeError, self.client.create_bitcoin_interchain, "a", 1)
        self.assertRaises(TypeError, self.client.create_bitcoin_interchain, "a", True, 1)
        self.assertRaises(TypeError, self.client.create_bitcoin_interchain, "a", True, "a", 1)
        self.assertRaises(TypeError, self.client.create_bitcoin_interchain, "a", True, "a", "a", 1)
        self.assertRaises(TypeError, self.client.create_bitcoin_interchain, "a", True, "a", "a", "a", 1)

    def test_create_bitcoin_interchain_calls_correctly_with_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_bitcoin_interchain("name", True, "key", "address", "auth", False)
        self.client.request.post.assert_called_once_with(
            "/v1/interchains/bitcoin",
            {
                "version": "1",
                "name": "name",
                "testnet": True,
                "private_key": "key",
                "rpc_address": "address",
                "rpc_authorization": "auth",
                "utxo_scan": False,
            },
        )

    def test_create_bitcoin_interchain_calls_correctly_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_bitcoin_interchain("name")
        self.client.request.post.assert_called_once_with("/v1/interchains/bitcoin", {"version": "1", "name": "name"})

    def test_update_bitcoin_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.update_bitcoin_interchain, 1)
        self.assertRaises(TypeError, self.client.update_bitcoin_interchain, "a", 1)
        self.assertRaises(TypeError, self.client.update_bitcoin_interchain, "a", True, 1)
        self.assertRaises(TypeError, self.client.update_bitcoin_interchain, "a", True, "a", 1)
        self.assertRaises(TypeError, self.client.update_bitcoin_interchain, "a", True, "a", "a", 1)
        self.assertRaises(TypeError, self.client.update_bitcoin_interchain, "a", True, "a", "a", "a", 1)

    def test_update_bitcoin_interchain_calls_correctly_with_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_bitcoin_interchain("name", True, "key", "address", "auth", False)
        self.client.request.patch.assert_called_once_with(
            "/v1/interchains/bitcoin/name",
            {"version": "1", "testnet": True, "private_key": "key", "rpc_address": "address", "rpc_authorization": "auth", "utxo_scan": False},
        )

    def test_update_bitcoin_interchain_calls_correctly_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_bitcoin_interchain("name")
        self.client.request.patch.assert_called_once_with("/v1/interchains/bitcoin/name", {"version": "1"})

    def test_sign_bitcoin_transaction_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.sign_bitcoin_transaction, 1)

    def test_sign_bitcoin_transaction_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.sign_bitcoin_transaction("name", 1, "data", "change", [{"to": "address", "value": 9.234}])
        self.client.request.post.assert_called_once_with(
            "/v1/interchains/bitcoin/name/transaction",
            {"version": "1", "outputs": [{"to": "address", "value": 9.234}], "fee": 1, "data": "data", "change": "change"},
        )

    def test_create_ethereum_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_ethereum_interchain, 1)
        self.assertRaises(TypeError, self.client.create_ethereum_interchain, "a", 1)
        self.assertRaises(TypeError, self.client.create_ethereum_interchain, "a", "a", 1)
        self.assertRaises(TypeError, self.client.create_ethereum_interchain, "a", "a", "a", "a")

    def test_create_ethereum_interchain_calls_correctly_with_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_ethereum_interchain("name", "key", "address", 1)
        self.client.request.post.assert_called_once_with(
            "/v1/interchains/ethereum", {"version": "1", "name": "name", "private_key": "key", "rpc_address": "address", "chain_id": 1}
        )

    def test_create_ethereum_interchain_calls_correctly_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_ethereum_interchain("name")
        self.client.request.post.assert_called_once_with("/v1/interchains/ethereum", {"version": "1", "name": "name"})

    def test_update_ethereum_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.update_ethereum_interchain, 1)
        self.assertRaises(TypeError, self.client.update_ethereum_interchain, "a", 1)
        self.assertRaises(TypeError, self.client.update_ethereum_interchain, "a", "a", 1)
        self.assertRaises(TypeError, self.client.update_ethereum_interchain, "a", "a", "a", "a")

    def test_update_ethereum_interchain_calls_correctly_with_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_ethereum_interchain("name", "key", "address", 1)
        self.client.request.patch.assert_called_once_with(
            "/v1/interchains/ethereum/name", {"version": "1", "private_key": "key", "rpc_address": "address", "chain_id": 1}
        )

    def test_update_ethereum_interchain_calls_correctly_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_ethereum_interchain("name")
        self.client.request.patch.assert_called_once_with("/v1/interchains/ethereum/name", {"version": "1"})

    def test_sign_ethereum_transaction_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.sign_ethereum_transaction, 1, "to", "value")
        self.assertRaises(TypeError, self.client.sign_ethereum_transaction, "name", "to", "value", nonce=1)

    def test_sign_ethereum_transaction_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.sign_ethereum_transaction("name", "0xaddress", "0xvalue", "0xdata", "0xgasprice", "0xgaslimit", "0xnonce")
        self.client.request.post.assert_called_once_with(
            "/v1/interchains/ethereum/name/transaction",
            {
                "version": "1",
                "to": "0xaddress",
                "value": "0xvalue",
                "data": "0xdata",
                "gasPrice": "0xgasprice",
                "gas": "0xgaslimit",
                "nonce": "0xnonce",
            },
        )

    def test_create_binance_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.create_binance_interchain, 1)  # "name", required
        self.assertRaises(TypeError, self.client.create_binance_interchain, "a", "not_boolean")  # "testnet", bool
        self.assertRaises(TypeError, self.client.create_binance_interchain, "a", True, 1)  # "private_key", str
        self.assertRaises(TypeError, self.client.create_binance_interchain, "a", True, "key", 1)  # "node_url", str
        self.assertRaises(TypeError, self.client.create_binance_interchain, "a", True, "key", "url", "port")  # "rpc_port", int
        self.assertRaises(TypeError, self.client.create_binance_interchain, "a", True, "key", "url", 123, "port")  # "api_port", int

    def test_create_binance_interchain_calls_correctly_with_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_binance_interchain("name", True, "key", "addy", 1234, 5678)
        params = {"version": "1", "name": "name", "testnet": True, "private_key": "key", "node_url": "addy", "rpc_port": 1234, "api_port": 5678}
        self.client.request.post.assert_called_once_with("/v1/interchains/binance", params)

    def test_create_binance_interchain_calls_correctly_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.create_binance_interchain("name")
        self.client.request.post.assert_called_once_with("/v1/interchains/binance", {"version": "1", "name": "name"})

    def test_update_binance_interchain_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.update_binance_interchain, 1)  # "name", required
        self.assertRaises(TypeError, self.client.update_binance_interchain, "a", "not_boolean")  # breaking: bool "testnet"
        self.assertRaises(TypeError, self.client.update_binance_interchain, "a", True, 1)  # breaking: str private_key"
        self.assertRaises(TypeError, self.client.update_binance_interchain, "a", True, "key", 1)  # breaking: str "node_url"
        self.assertRaises(TypeError, self.client.update_binance_interchain, "a", True, "key", "url", "port")  # breaking: int "rpc_port"
        self.assertRaises(TypeError, self.client.update_binance_interchain, "a", True, "key", "url", 123, "port")  # breaking: int "api_port"

    def test_update_binance_interchain_calls_correctly_with_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_binance_interchain("name", True, "key", "addy", 1234, 5678)
        params = {"version": "1", "testnet": True, "private_key": "key", "node_url": "addy", "rpc_port": 1234, "api_port": 5678}
        self.client.request.patch.assert_called_once_with("/v1/interchains/binance/name", params)

    def test_update_binance_interchain_calls_correctly_without_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.update_binance_interchain("name")
        self.client.request.patch.assert_called_once_with("/v1/interchains/binance/name", {"version": "1"})

    def test_sign_binance_transaction_throws_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.assertRaises(TypeError, self.client.sign_binance_transaction, 0, 100, "addy")  # breaking: str "name"
        self.assertRaises(TypeError, self.client.sign_binance_transaction, "name", "amt", "addy")  # breaking: int "amount"
        self.assertRaises(TypeError, self.client.sign_binance_transaction, "name", 100, 0000)  # breaking: str "to_address"
        self.assertRaises(TypeError, self.client.sign_binance_transaction, "name", 100, "addy", 000)  # breaking: str "symbol"
        self.assertRaises(TypeError, self.client.sign_binance_transaction, "name", 100, "addy", "BNB", 0000)  # breaking: str "memo"

    def test_sign_binance_transaction_calls_correctly(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.sign_binance_transaction("name", 123, "0xaddress", "SYMBOL", "MEMO")
        params = {"version": "1", "amount": 123, "to_address": "0xaddress", "symbol": "SYMBOL", "memo": "MEMO"}
        self.client.request.post.assert_called_once_with("/v1/interchains/binance/name/transaction", params)

    def test_sign_binance_transaction_calls_correctly_without_optional_params(self, mock_creds, mock_request):
        self.client = dragonchain_sdk.create_client()
        self.client.sign_binance_transaction("name", 123, "0xaddress")
        params = {"version": "1", "amount": 123, "to_address": "0xaddress"}
        self.client.request.post.assert_called_once_with("/v1/interchains/binance/name/transaction", params)
