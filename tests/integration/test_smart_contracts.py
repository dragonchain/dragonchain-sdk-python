# Copyright 2019 Dragonchain, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import unittest
import time

import jsonschema

import dragonchain_sdk
from tests.integration import schema

SMART_CONTRACT_BASIC_NAME = "bacon-cream"
SMART_CONTRACT_BASIC_ID = None
SMART_CONTRACT_ARGS_NAME = "bacon-cake"
SMART_CONTRACT_ARGS_ID = None
SMART_CONTRACT_ENV_NAME = "tomato-soup"
SMART_CONTRACT_ENV_ID = None
SMART_CONTRACT_SECRETS_NAME = "bacon-spaghetti"
SMART_CONTRACT_SECRETS_ID = None
SMART_CONTRACT_SCHEDULER_NAME = "bacon-time"
SMART_CONTRACT_SCHEDULER_ID = None
SMART_CONTRACT_ORDER_NAME = "bacon-soup"
SMART_CONTRACT_ORDER_ID = None
SMART_CONTRACT_CRON_NAME = "banana-cron"
SMART_CONTRACT_CRON_ID = None
ARGS_CONTRACT_BODY = None
CREATION_TIMESTAMP = None
CRON_INVOCATION_COUNT = None
SCHEDULER_INVOCATION_COUNT = None

SCHEDULER = 60
CRON = "* * * * *"

_expected_not_found_response = {
    "status": 404,
    "ok": False,
    "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}},
}


class TestSmartContracts(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()
        self.maxDiff = 3000

    # CREATE #

    def test_create_contract_with_bad_secrets_fails(self):
        _expected_fail_response = {
            "status": 400,
            "ok": False,
            "response": {"error": {"type": "VALIDATION_ERROR", "details": "data.secrets must contain only specified properties"}},
        }
        response1 = self.client.create_smart_contract(
            transaction_type="whatever", image="alpine:latest", cmd="uptime", secrets={"secret-key": "shouldn't work"}
        )
        response2 = self.client.create_smart_contract(
            transaction_type="whatever", image="alpine:latest", cmd="uptime", secrets={"auth-key-id": "shouldn't work"}
        )
        response3 = self.client.create_smart_contract(
            transaction_type="whatever", image="alpine:latest", cmd="uptime", secrets={"Doesn't work": "whatever"}
        )
        self.assertEqual(response1, _expected_fail_response, response1)
        self.assertEqual(response2, _expected_fail_response, response2)
        self.assertEqual(response2, _expected_fail_response, response3)

    def test_create_basic_contract(self):
        response = self.client.create_smart_contract(transaction_type=SMART_CONTRACT_BASIC_NAME, image="alpine:latest", cmd="uptime")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_BASIC_ID
        SMART_CONTRACT_BASIC_ID = response["response"]["id"]
        time.sleep(3)

    def test_create_contract_with_args(self):
        response = self.client.create_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME, image="alpine:latest", cmd="echo", args=["hello"])
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_ARGS_ID
        SMART_CONTRACT_ARGS_ID = response["response"]["id"]
        time.sleep(3)

    def test_create_contract_with_custom_env(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_ENV_NAME,
            image="alpine:latest",
            cmd="echo",
            args=["hello"],
            environment_variables={"MY_VAR": "custom value"},
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_ENV_ID
        SMART_CONTRACT_ENV_ID = response["response"]["id"]
        time.sleep(3)

    def test_create_contract_with_serial_execution_order(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_ORDER_NAME, image="alpine:latest", cmd="echo", args=["hello"], execution_order="serial"
        )
        self.assertTrue(response.get("ok"))
        self.assertEqual(response.get("status"), 202)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_ORDER_ID
        SMART_CONTRACT_ORDER_ID = response["response"]["id"]
        time.sleep(3)

    def test_create_contract_with_secrets(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_SECRETS_NAME, image="alpine:latest", cmd="echo", args=["hello"], secrets={"mysecret": "super secret"}
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_SECRETS_ID
        SMART_CONTRACT_SECRETS_ID = response["response"]["id"]
        time.sleep(3)

    def test_create_contract_with_scheduler(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_SCHEDULER_NAME, image="alpine:latest", cmd="echo", args=["hello"], schedule_interval_in_seconds=SCHEDULER
        )
        global CREATION_TIMESTAMP
        CREATION_TIMESTAMP = str(time.time())
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_SCHEDULER_ID
        SMART_CONTRACT_SCHEDULER_ID = response["response"]["id"]
        time.sleep(3)

    def test_create_contract_with_cron(self):
        response = self.client.create_smart_contract(
            transaction_type=SMART_CONTRACT_CRON_NAME, image="alpine:latest", cmd="echo", args=["hello"], cron_expression=CRON
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global SMART_CONTRACT_CRON_ID
        SMART_CONTRACT_CRON_ID = response["response"]["id"]
        time.sleep(40)

    # GET #

    def test_get_contract_with_transcation_type(self):
        response = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)
        global ARGS_CONTRACT_BODY
        ARGS_CONTRACT_BODY = response["response"]

    def test_get_contract_with_contract_id(self):
        response = self.client.get_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.smart_contract_at_rest_schema)

    # LIST #

    def test_list_smart_contracts(self):
        response = self.client.list_smart_contracts()
        self.assertTrue(response.get("ok"))
        self.assertEqual(response.get("status"), 200)
        jsonschema.validate(response.get("response"), schema.smart_contracts_list_schema)
        # Check one of our known contracts is in the list
        self.assertIn(ARGS_CONTRACT_BODY, response["response"]["smart_contracts"], response["response"]["smart_contracts"])
        # Check that we have at least as many contracts as we expect
        self.assertGreaterEqual(len(response["response"]["smart_contracts"]), 7, response["response"]["smart_contracts"])

    # UPDATE #

    def test_update_contract_with_bad_secrets_fails(self):
        _expected_fail_response = {
            "status": 400,
            "ok": False,
            "response": {"error": {"type": "VALIDATION_ERROR", "details": "data.secrets must contain only specified properties"}},
        }
        response1 = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, secrets={"secret-key": "shouldn't work"})
        response2 = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, secrets={"auth-key-id": "shouldn't work"})
        response3 = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, secrets={"InvalidName": "shouldn't work"})
        self.assertEqual(response1, _expected_fail_response, response1)
        self.assertEqual(response2, _expected_fail_response, response2)
        self.assertEqual(response2, _expected_fail_response, response3)

    def test_update_contract_with_image(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, image="busybox:latest")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertEqual(updated_smart_contract["response"]["image"], "busybox:latest")

    def test_update_contract_with_args(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ARGS_ID, args=["bacon"])
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertEqual(updated_smart_contract["response"]["args"][0], "bacon")

    def test_update_contract_with_env(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ENV_ID, environment_variables={"bacon": "tomato"})
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ENV_NAME)
        self.assertEqual(updated_smart_contract["response"]["env"]["bacon"], "tomato")

    def test_update_contract_with_secrets(self):
        response = self.client.update_smart_contract(
            smart_contract_id=SMART_CONTRACT_SECRETS_ID, secrets={"secret-banana": "bananas", "mysecret": "mynewsecret"}
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_SECRETS_NAME)
        # Check new secret was added
        self.assertIn("secret-banana", updated_smart_contract["response"]["existing_secrets"], updated_smart_contract["response"]["existing_secrets"])
        # Check existing secret is still there
        self.assertIn("mysecret", updated_smart_contract["response"]["existing_secrets"], updated_smart_contract["response"]["existing_secrets"])

    def test_update_contract_execution_order(self):
        response = self.client.update_smart_contract(smart_contract_id=SMART_CONTRACT_ORDER_ID, execution_order="parallel")
        self.assertTrue(response.get("ok"))
        self.assertEqual(response.get("status"), 202)
        updated_smart_contract = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ORDER_NAME)
        self.assertTrue(updated_smart_contract["response"]["execution_order"], "parallel")

    # INVOCATION #

    def wait_for_scheduler_invocation_1(self):
        time.sleep(55)

    def disable_schedule(self):
        self.assertTrue(self.client.update_smart_contract(SMART_CONTRACT_SCHEDULER_ID, disable_schedule=True).get("ok"))
        self.assertTrue(self.client.update_smart_contract(SMART_CONTRACT_CRON_ID, disable_schedule=True).get("ok"))

    def wait_for_scheduler_invocation_2(self):
        time.sleep(20)

    def test_successful_invocation_of_scheduler(self):
        transaction_invocation = self.client.query_transactions(SMART_CONTRACT_SCHEDULER_NAME, "*")
        global SCHEDULER_INVOCATION_COUNT
        SCHEDULER_INVOCATION_COUNT = transaction_invocation["response"]["total"]
        self.assertGreater(SCHEDULER_INVOCATION_COUNT, 0)
        self.assertGreater(transaction_invocation["response"]["results"][0]["header"]["timestamp"], CREATION_TIMESTAMP)

    def test_successful_invocation_of_cron(self):
        transaction_invocation = self.client.query_transactions(SMART_CONTRACT_CRON_NAME, "*")
        global CRON_INVOCATION_COUNT
        CRON_INVOCATION_COUNT = transaction_invocation["response"]["total"]
        self.assertGreater(CRON_INVOCATION_COUNT, 0)
        self.assertGreater(transaction_invocation["response"]["results"][0]["header"]["timestamp"], CREATION_TIMESTAMP)

    def wait_for_scheduler_invocation_3(self):
        time.sleep(65)

    def test_disable_schedule_works_on_scheduler(self):
        transaction_invocation = self.client.query_transactions(SMART_CONTRACT_SCHEDULER_NAME, "*")
        # Assert that the transaction count after waiting 60 seconds is the same as after we immediately disabled the schedule
        self.assertEqual(SCHEDULER_INVOCATION_COUNT, transaction_invocation["response"]["total"])

    def test_disable_schedule_works_on_cron(self):
        transaction_invocation = self.client.query_transactions(SMART_CONTRACT_CRON_NAME, "*")
        # Assert that the transaction count after waiting 60 seconds is the same as after we immediately disabled the schedule
        self.assertEqual(CRON_INVOCATION_COUNT, transaction_invocation["response"]["total"])

    def test_successful_invocation_with_transactions(self):
        args_transaction = self.client.create_transaction(SMART_CONTRACT_ARGS_NAME, "banana")
        env_transaction = self.client.create_transaction(SMART_CONTRACT_ENV_NAME, "banana")
        secrets_transaction = self.client.create_transaction(SMART_CONTRACT_SECRETS_NAME, "banana")
        time.sleep(30)
        # Query for created transactions by invoker tag
        args_query = self.client.query_transactions(
            SMART_CONTRACT_ARGS_NAME, "@invoker:{{{}}}".format(args_transaction.get("response").get("transaction_id").replace("-", "\\-"))
        )
        env_query = self.client.query_transactions(
            SMART_CONTRACT_ENV_NAME, "@invoker:{{{}}}".format(env_transaction.get("response").get("transaction_id").replace("-", "\\-"))
        )
        secrets_query = self.client.query_transactions(
            SMART_CONTRACT_SECRETS_NAME, "@invoker:{{{}}}".format(secrets_transaction.get("response").get("transaction_id").replace("-", "\\-"))
        )
        # Check that the queries were successful and had a result with the invoker
        self.assertEqual(args_query["response"]["results"][0]["header"]["invoker"], args_transaction["response"]["transaction_id"])
        self.assertEqual(env_query["response"]["results"][0]["header"]["invoker"], env_transaction["response"]["transaction_id"])
        self.assertEqual(secrets_query["response"]["results"][0]["header"]["invoker"], secrets_transaction["response"]["transaction_id"])

    # SMART CONTRACT LOGS #

    def test_get_contract_logs_with_contract_id(self):
        response = self.client.get_smart_contract_logs(smart_contract_id=SMART_CONTRACT_ARGS_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200)
        jsonschema.validate(response.get("response"), schema.smart_contract_logs_schema)
        self.assertGreater(len(response.get("response")["logs"]), 0)

    def test_get_contract_logs_with_contract_id_tail_and_since(self):
        response = self.client.get_smart_contract_logs(smart_contract_id=SMART_CONTRACT_ARGS_ID, tail=100, since="2019-09-16T23:10:04.000Z")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200)
        jsonschema.validate(response.get("response"), schema.smart_contract_logs_schema)
        self.assertGreater(len(response.get("response")["logs"]), 0)

    def test_get_contract_logs_with_invalid_contract_id_throws_not_found(self):
        response = self.client.get_smart_contract_logs(smart_contract_id="The real banana")
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 404)

    def test_get_contract_logs_with_tail_1_returns_1(self):
        response = self.client.get_smart_contract_logs(smart_contract_id=SMART_CONTRACT_ARGS_ID, tail=1)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200)
        jsonschema.validate(response.get("response"), schema.smart_contract_logs_schema)
        self.assertEqual(len(response.get("response")["logs"]), 1)

    def test_get_contract_logs_with_since_in_future_returns_none(self):
        response = self.client.get_smart_contract_logs(smart_contract_id=SMART_CONTRACT_ARGS_ID, since="8000-09-16T23:10:04.000Z")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200)
        jsonschema.validate(response.get("response"), schema.smart_contract_logs_schema)
        self.assertEqual(len(response.get("response")["logs"]), 0)

    # SMART CONTRACT HEAP #

    def test_get_smart_contract_object_by_prefix_key(self):
        response = self.client.get_smart_contract_object("rawResponse", SMART_CONTRACT_ARGS_ID)
        self.assertEqual(response["response"], '"bacon\\n"')

    def test_list_smart_contract_objects(self):
        response = self.client.list_smart_contract_objects(smart_contract_id=SMART_CONTRACT_ARGS_ID)
        expected_response = {"status": 200, "ok": True, "response": ["/rawResponse"]}
        self.assertEqual(response, expected_response)

    # BUILT STATE CHANGE #

    def test_successful_creation_of_contract(self):
        response = self.client.get_smart_contract(SMART_CONTRACT_BASIC_ID)
        self.assertEqual(response["response"]["status"]["state"], "active", response)
        self.assertEqual(response["response"]["status"]["msg"], "Creation success", response)

    def test_successful_update_of_contract(self):
        response = self.client.get_smart_contract(SMART_CONTRACT_ARGS_ID)
        self.assertEqual(response["response"]["status"]["state"], "active", response)

    # DELETE #

    def test_delete_basic_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_BASIC_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(30)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_BASIC_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def test_delete_updated_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_ARGS_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_ARGS_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def test_delete_scheduled_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_SCHEDULER_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_SCHEDULER_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def test_delete_cron_contract(self):
        response = self.client.delete_smart_contract(SMART_CONTRACT_CRON_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 202, response)
        time.sleep(20)
        deleted_fetch = self.client.get_smart_contract(transaction_type=SMART_CONTRACT_CRON_NAME)
        self.assertEqual(_expected_not_found_response, deleted_fetch)

    def smart_contract_clean_up(self):
        contracts = [
            (SMART_CONTRACT_BASIC_ID, SMART_CONTRACT_BASIC_NAME),
            (SMART_CONTRACT_ARGS_ID, SMART_CONTRACT_ARGS_NAME),
            (SMART_CONTRACT_ENV_ID, SMART_CONTRACT_ENV_NAME),
            (SMART_CONTRACT_SECRETS_ID, SMART_CONTRACT_SECRETS_NAME),
            (SMART_CONTRACT_ORDER_ID, SMART_CONTRACT_ORDER_NAME),
            (SMART_CONTRACT_SCHEDULER_ID, SMART_CONTRACT_SCHEDULER_NAME),
            (SMART_CONTRACT_CRON_ID, SMART_CONTRACT_CRON_NAME),
        ]
        for contract in contracts:
            try:
                sc_id = contract[0]
                if not sc_id:
                    sc_id = self.client.get_transaction_type(contract[1])["response"]["contract_id"]
                self.client.delete_smart_contract(sc_id)
            except Exception:
                pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestSmartContracts("test_create_contract_with_bad_secrets_fails"))
    suite.addTest(TestSmartContracts("test_create_basic_contract"))
    suite.addTest(TestSmartContracts("test_create_contract_with_args"))
    suite.addTest(TestSmartContracts("test_create_contract_with_custom_env"))
    suite.addTest(TestSmartContracts("test_create_contract_with_serial_execution_order"))
    suite.addTest(TestSmartContracts("test_create_contract_with_secrets"))
    suite.addTest(TestSmartContracts("test_create_contract_with_scheduler"))
    suite.addTest(TestSmartContracts("test_create_contract_with_cron"))
    suite.addTest(TestSmartContracts("test_get_contract_with_transcation_type"))
    suite.addTest(TestSmartContracts("test_get_contract_with_contract_id"))
    suite.addTest(TestSmartContracts("test_list_smart_contracts"))
    suite.addTest(TestSmartContracts("test_update_contract_with_bad_secrets_fails"))
    suite.addTest(TestSmartContracts("test_update_contract_with_image"))
    suite.addTest(TestSmartContracts("test_update_contract_with_args"))
    suite.addTest(TestSmartContracts("test_update_contract_with_env"))
    suite.addTest(TestSmartContracts("test_update_contract_with_secrets"))
    suite.addTest(TestSmartContracts("test_update_contract_execution_order"))
    suite.addTest(TestSmartContracts("wait_for_scheduler_invocation_1"))
    suite.addTest(TestSmartContracts("disable_schedule"))
    suite.addTest(TestSmartContracts("wait_for_scheduler_invocation_2"))
    suite.addTest(TestSmartContracts("test_successful_invocation_of_scheduler"))
    suite.addTest(TestSmartContracts("test_successful_invocation_of_cron"))
    suite.addTest(TestSmartContracts("wait_for_scheduler_invocation_3"))
    suite.addTest(TestSmartContracts("test_disable_schedule_works_on_scheduler"))
    suite.addTest(TestSmartContracts("test_disable_schedule_works_on_cron"))
    suite.addTest(TestSmartContracts("test_successful_invocation_with_transactions"))
    suite.addTest(TestSmartContracts("test_get_contract_logs_with_contract_id"))
    suite.addTest(TestSmartContracts("test_get_contract_logs_with_contract_id_tail_and_since"))
    suite.addTest(TestSmartContracts("test_get_contract_logs_with_invalid_contract_id_throws_not_found"))
    suite.addTest(TestSmartContracts("test_get_contract_logs_with_tail_1_returns_1"))
    suite.addTest(TestSmartContracts("test_get_contract_logs_with_since_in_future_returns_none"))
    suite.addTest(TestSmartContracts("test_get_smart_contract_object_by_prefix_key"))
    suite.addTest(TestSmartContracts("test_list_smart_contract_objects"))
    suite.addTest(TestSmartContracts("test_successful_creation_of_contract"))
    suite.addTest(TestSmartContracts("test_successful_update_of_contract"))
    suite.addTest(TestSmartContracts("test_delete_basic_contract"))
    suite.addTest(TestSmartContracts("test_delete_updated_contract"))
    suite.addTest(TestSmartContracts("test_delete_scheduled_contract"))
    suite.addTest(TestSmartContracts("test_delete_cron_contract"))
    suite.addTest(TestSmartContracts("smart_contract_clean_up"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
