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
import time
import unittest

import jsonschema

from tests.integration import schema
import dragonchain_sdk

SC_ID = None
SC_TXN_TYPE = "contractType1"
INVOKER_TXN_ID = None
TEST_TXN_TYPE = "testingType1"
QUERY_TXN_TYPE = "queryTesting"
EMPTY_STRING_TXN_ID = None
EMTPY_OBJECT_TXN_ID = None
STRING_CONTENT = "some content"
STRING_CONTENT_TXN_ID = None
OBJECT_CONTENT = {"something": "cool", "array": ["things", True], "number": 4.5}
OBJECT_CONTENT_TXN_ID = None
TAG_TXN_ID = None
TAG_CONTENT = "someTag"
BULK_TXN_ID = None
BULK_TXN_CONTENT = "valid txn"
LOW_TXN_ID = None
HIGH_TXN_ID = None


class TestTransactions(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    def set_up_transaction_types(self):
        try:
            global SC_ID
            SC_ID = self.client.create_smart_contract(SC_TXN_TYPE, "alpine:latest", "echo", ["hello"])["response"]["id"]
            self.client.create_transaction_type(TEST_TXN_TYPE)
            self.client.create_transaction_type(
                QUERY_TXN_TYPE,
                [
                    {"path": "test.text", "field_name": "query_text", "type": "text", "options": {"sortable": True}},
                    {"path": "test.tag", "field_name": "query_tag", "type": "tag"},
                    {"path": "test.num", "field_name": "query_num", "type": "number", "options": {"sortable": True}},
                ],
            )
            time.sleep(25)
        except Exception:
            pass

    # CREATE #

    def test_create_transaction_with_empty_string_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload="")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global EMPTY_STRING_TXN_ID
        EMPTY_STRING_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_nonempty_string_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload=STRING_CONTENT)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global STRING_CONTENT_TXN_ID
        STRING_CONTENT_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_empty_object_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload={})
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global EMTPY_OBJECT_TXN_ID
        EMTPY_OBJECT_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_nonempty_object_payload(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload=OBJECT_CONTENT)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global OBJECT_CONTENT_TXN_ID
        OBJECT_CONTENT_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_tag(self):
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload="", tag=TAG_CONTENT)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global TAG_TXN_ID
        TAG_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_with_callback(self):
        # For this test, just check that the server accepts the callback url, but don't verify it actually calls back since
        # we aren't running any webserver which could recieve the callback
        response = self.client.create_transaction(transaction_type=TEST_TXN_TYPE, payload="", callback_url="http://fakeurl")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)

    def test_create_transaction_for_smart_contract(self):
        response = self.client.create_transaction(transaction_type=SC_TXN_TYPE, payload="")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.create_transaction_schema)
        global INVOKER_TXN_ID
        INVOKER_TXN_ID = response["response"]["transaction_id"]

    def test_create_transaction_fails_without_transaction_type(self):
        response = self.client.create_transaction(transaction_type="doesnotexist", payload="")
        expected_response = {
            "status": 403,
            "ok": False,
            "response": {
                "error": {
                    "type": "INVALID_TRANSACTION_TYPE",
                    "details": "The transaction type you are attempting to use either does not exist or is invalid.",
                }
            },
        }
        self.assertEqual(expected_response, response)

    def test_create_bulk_transactions_with_all_valid_transactions(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": TEST_TXN_TYPE, "payload": "thing"},
                {"transaction_type": TEST_TXN_TYPE, "payload": {"object": "thing"}},
                {"transaction_type": TEST_TXN_TYPE, "payload": "", "tag": "a tag"},
            ]
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 207, response)
        jsonschema.validate(response.get("response"), schema.bulk_create_transaction_schema)
        # Ensure the correct amount of transactions were posted successfully
        self.assertEqual(len(response["response"]["400"]), 0)
        self.assertEqual(len(response["response"]["201"]), 3)

    def test_create_bulk_transactions_with_some_nonexisting_transaction_types(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": TEST_TXN_TYPE, "payload": BULK_TXN_CONTENT},
                {"transaction_type": "thisdoesntexist", "payload": "invalid txn", "tag": "thing"},
            ]
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 207, response)
        jsonschema.validate(response.get("response"), schema.bulk_create_transaction_schema)
        # Ensure the correct amount of transactions were posted successfully
        self.assertEqual(len(response["response"]["201"]), 1)
        self.assertEqual(response["response"]["400"], [{"version": "1", "txn_type": "thisdoesntexist", "payload": "invalid txn", "tag": "thing"}])
        # Save the valid transaction id to check for later
        global BULK_TXN_ID
        BULK_TXN_ID = response["response"]["201"][0]

    def test_create_bulk_transactions_with_some_invalid_transactions(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": TEST_TXN_TYPE, "payload": "valid txn"},
                {"invalid": "transaction"},
                {"typo_type": "whoops", "payload": "", "tag": "a tag"},
            ]
        )
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400, response)
        self.assertEqual(response["response"]["error"]["type"], "VALIDATION_ERROR", response)

    def test_create_bulk_transactions_with_all_nonexistant_transaction_types(self):
        response = self.client.create_bulk_transaction(
            [
                {"transaction_type": "thisdoesntexist", "payload": {"hello": "thing"}},
                {"transaction_type": "thisalsodoesntexist", "payload": "invalid txn", "tag": "thing"},
            ]
        )
        expected_response = {
            "status": 400,
            "ok": False,
            "response": {
                "201": [],
                "400": [
                    {"version": "1", "txn_type": "thisdoesntexist", "payload": {"hello": "thing"}},
                    {"version": "1", "txn_type": "thisalsodoesntexist", "payload": "invalid txn", "tag": "thing"},
                ],
            },
        }
        self.assertEqual(expected_response, response)

    def test_create_bulk_transactions_with_all_invalid_transactions(self):
        response = self.client.create_bulk_transaction([{"thisschema": "isnotcorrect"}, {}])
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400, response)
        self.assertEqual(response["response"]["error"]["type"], "VALIDATION_ERROR", response)

    def wait_for_blocks(self):
        time.sleep(15)

    # GET #

    def test_get_transaction_returns_stub_if_not_in_block(self):
        txn_id = self.client.create_transaction(TEST_TXN_TYPE, "")["response"]["transaction_id"]
        response = self.client.get_transaction(txn_id)
        self.assertEqual(
            response,
            {
                "status": 200,
                "ok": True,
                "response": {"header": {"txn_id": txn_id}, "message": "This transaction is waiting to be included in a block", "status": "pending"},
            },
        )

    def test_get_transaction_with_empty_string_payload(self):
        response = self.client.get_transaction(EMPTY_STRING_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(EMPTY_STRING_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual("", response["response"]["payload"], response)

    def test_get_transaction_with_nonempty_string_payload(self):
        response = self.client.get_transaction(STRING_CONTENT_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(STRING_CONTENT_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(STRING_CONTENT, response["response"]["payload"], response)

    def test_get_transaction_with_empty_object_payload(self):
        response = self.client.get_transaction(EMTPY_OBJECT_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(EMTPY_OBJECT_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual({}, response["response"]["payload"], response)

    def test_get_transaction_with_nonempty_object_payload(self):
        response = self.client.get_transaction(OBJECT_CONTENT_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(OBJECT_CONTENT_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(OBJECT_CONTENT, response["response"]["payload"], response)

    def test_get_transaction_with_tag(self):
        response = self.client.get_transaction(TAG_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(TAG_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(TAG_CONTENT, response["response"]["header"]["tag"], response)

    def test_get_transaction_from_bulk_submission(self):
        response = self.client.get_transaction(BULK_TXN_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_transaction_schema)
        # Check various fields on the retrieved object
        self.assertEqual(BULK_TXN_ID, response["response"]["header"]["txn_id"], response)
        self.assertEqual(TEST_TXN_TYPE, response["response"]["header"]["txn_type"], response)
        self.assertEqual(BULK_TXN_CONTENT, response["response"]["payload"], response)

    def test_get_transaction_fails_with_bad_id(self):
        response = self.client.get_transaction("not_real_id")
        expected_response = {
            "status": 404,
            "ok": False,
            "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}},
        }
        self.assertEqual(expected_response, response)

    # QUERY #

    def set_up_queryable_transactions(self):
        global LOW_TXN_ID
        global HIGH_TXN_ID
        LOW_TXN_ID = self.client.create_transaction(
            QUERY_TXN_TYPE, tag="unique1 content", payload={"test": {"text": "a sortable text1 field", "tag": "someTag1", "num": 1234}}
        )["response"]["transaction_id"]
        time.sleep(8)
        HIGH_TXN_ID = self.client.create_transaction(
            QUERY_TXN_TYPE, tag="unique2 content", payload={"test": {"text": "a sortable text2 field", "tag": "someTag2", "num": 4321}}
        )["response"]["transaction_id"]
        time.sleep(8)

    def test_query_transactions_generic(self):
        response = self.client.query_transactions(QUERY_TXN_TYPE, "*")
        self.assertEqual(response.get("status"), 200)
        self.assertTrue(response.get("ok"))
        jsonschema.validate(response.get("response"), schema.query_transaction_schema)
        self.assertEqual(response["response"]["total"], 2)

    def test_query_transactions_by_timestamp(self):
        # Get all transactions timestamp below now, sorted by timestamp
        response1 = self.client.query_transactions(
            QUERY_TXN_TYPE, "@timestamp:[-inf {}]".format(time.time()), sort_by="timestamp", sort_ascending=True
        )
        response2 = self.client.query_transactions(
            QUERY_TXN_TYPE, "@timestamp:[-inf {}]".format(time.time()), sort_by="timestamp", sort_ascending=False
        )
        response3 = self.client.query_transactions(QUERY_TXN_TYPE, "@timestamp:[{} +inf]".format(time.time()))  # Should not return any results
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response2.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response2.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response3.get("response"), schema.query_transaction_schema)
        # Check we got the correct results
        self.assertEqual(response1["response"]["total"], 2)
        self.assertEqual(response2["response"]["total"], 2)
        self.assertEqual(response3["response"]["total"], 0)
        # Check sorted order is correct
        self.assertEqual(response1["response"]["results"][0]["header"]["txn_id"], LOW_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response1["response"]["results"][1]["header"]["txn_id"], HIGH_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response2["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "First result in descending query was not sorted")
        self.assertEqual(response2["response"]["results"][1]["header"]["txn_id"], LOW_TXN_ID, "First result in descending query was not sorted")

    def test_query_transactions_by_block_id(self):
        current_block = int((time.time() - 1432238220) / 5)
        # Get all transactions timestamp below now, sorted by timestamp
        response1 = self.client.query_transactions(
            QUERY_TXN_TYPE, "@block_id:[-inf {}]".format(current_block), sort_by="block_id", sort_ascending=True
        )
        response2 = self.client.query_transactions(
            QUERY_TXN_TYPE, "@block_id:[-inf {}]".format(current_block), sort_by="block_id", sort_ascending=False
        )
        response3 = self.client.query_transactions(QUERY_TXN_TYPE, "@block_id:[({} +inf]".format(current_block))  # Should not return any results
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response2.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response2.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response3.get("response"), schema.query_transaction_schema)
        # Check we got the correct results
        self.assertEqual(response1["response"]["total"], 2)
        self.assertEqual(response2["response"]["total"], 2)
        self.assertEqual(response3["response"]["total"], 0)
        # Check sorted order is correct
        self.assertEqual(response1["response"]["results"][0]["header"]["txn_id"], LOW_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response1["response"]["results"][1]["header"]["txn_id"], HIGH_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response2["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "First result in descending query was not sorted")
        self.assertEqual(response2["response"]["results"][1]["header"]["txn_id"], LOW_TXN_ID, "First result in descending query was not sorted")

    def test_query_transactions_by_general_tag(self):
        response1 = self.client.query_transactions(QUERY_TXN_TYPE, "unique1")
        response2 = self.client.query_transactions(QUERY_TXN_TYPE, "unique2")
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        # Check we got the correct results
        self.assertEqual(response1["response"]["total"], 1)
        self.assertEqual(response2["response"]["total"], 1)
        # Check sorted order is correct
        self.assertEqual(response1["response"]["results"][0]["header"]["txn_id"], LOW_TXN_ID, "Wrong result for tag query 1")
        self.assertEqual(response2["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "Wrong result for tag query 2")

    def test_query_transactions_by_invoker(self):
        response = self.client.query_transactions(SC_TXN_TYPE, "@invoker:{{{}}}".format(INVOKER_TXN_ID.replace("-", "\\-")))
        self.assertEqual(response.get("status"), 200, response)
        self.assertTrue(response.get("ok"), response)
        jsonschema.validate(response.get("response"), schema.query_transaction_schema)
        # Check we got the correct number of results
        self.assertEqual(response["response"]["total"], 1)
        # Double check that the transaction we got back has the invoker we expect
        self.assertEqual(response["response"]["results"][0]["header"]["invoker"], INVOKER_TXN_ID, response)

    def test_query_transactions_verbatim(self):
        response1 = self.client.query_transactions(QUERY_TXN_TYPE, "contently", verbatim=False)  # Stems to match "content" from the tag
        response2 = self.client.query_transactions(QUERY_TXN_TYPE, "contently", verbatim=True)
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        # Check that switching verbatim causes results to change
        self.assertEqual(response1["response"]["total"], 2)
        self.assertEqual(response2["response"]["total"], 0)

    def test_query_transactions_ids_only(self):
        response = self.client.query_transactions(QUERY_TXN_TYPE, "*", ids_only=True)
        self.assertEqual(response.get("status"), 200, response)
        self.assertTrue(response.get("ok"), response)
        jsonschema.validate(response.get("response"), schema.query_ids_only)
        self.assertEqual(response["response"]["total"], 2)
        self.assertIn(LOW_TXN_ID, response["response"]["results"])
        self.assertIn(HIGH_TXN_ID, response["response"]["results"])

    def test_query_transactions_paging(self):
        # For testing offset and limit parameters in a query
        response1 = self.client.query_transactions(QUERY_TXN_TYPE, "*", limit=0)
        response2 = self.client.query_transactions(QUERY_TXN_TYPE, "*", offset=0, limit=1, ids_only=True)
        response3 = self.client.query_transactions(QUERY_TXN_TYPE, "*", offset=1, limit=1, ids_only=True)
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response3.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response3.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_ids_only)
        jsonschema.validate(response3.get("response"), schema.query_ids_only)
        # Check we got the correct totals
        self.assertEqual(response1["response"]["total"], 2)
        self.assertEqual(response2["response"]["total"], 2)
        self.assertEqual(response3["response"]["total"], 2)
        # Check that limit 0 returned an empty array
        self.assertEqual(response1["response"]["results"], [], "Limit 0 returned actual results")
        # Ensure both our results our transactions are in the combined paginated results
        self.assertEqual(len(response2["response"]["results"]), 1)
        self.assertEqual(len(response3["response"]["results"]), 1)
        combined_result = response2["response"]["results"] + response3["response"]["results"]
        self.assertIn(LOW_TXN_ID, combined_result)
        self.assertIn(HIGH_TXN_ID, combined_result)

    def test_query_transactions_by_custom_text(self):
        # Should return both transactions
        response1 = self.client.query_transactions(QUERY_TXN_TYPE, "@query_text:(a sortable)", sort_by="query_text", sort_ascending=False)
        # Should return only LOW_TXN_ID txn
        response2 = self.client.query_transactions(QUERY_TXN_TYPE, "text1")
        # Should return only HIGH_TXN_ID txn
        response3 = self.client.query_transactions(QUERY_TXN_TYPE, "text2")
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response3.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response3.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response3.get("response"), schema.query_transaction_schema)
        # Check we got the correct results
        self.assertEqual(response1["response"]["total"], 2)
        self.assertEqual(response2["response"]["total"], 1)
        self.assertEqual(response3["response"]["total"], 1)
        # Check sorted order is correct
        self.assertEqual(response1["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response1["response"]["results"][1]["header"]["txn_id"], LOW_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response2["response"]["results"][0]["header"]["txn_id"], LOW_TXN_ID, "First result in descending query was not sorted")
        self.assertEqual(response3["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "First result in descending query was not sorted")

    def test_query_transactions_by_custom_tag(self):
        response1 = self.client.query_transactions(QUERY_TXN_TYPE, "@query_tag:{someTag1}")
        response2 = self.client.query_transactions(QUERY_TXN_TYPE, "@query_tag:{someTag2}")
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        # Check we got the correct results
        self.assertEqual(response1["response"]["total"], 1)
        self.assertEqual(response2["response"]["total"], 1)
        # Check sorted order is correct
        self.assertEqual(response1["response"]["results"][0]["header"]["txn_id"], LOW_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response2["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "First result in ascending query was not sorted")

    def test_query_transactions_by_custom_num(self):
        response1 = self.client.query_transactions(QUERY_TXN_TYPE, "@query_num:[-inf +inf]", sort_by="query_num", sort_ascending=True)
        response2 = self.client.query_transactions(QUERY_TXN_TYPE, "@query_num:[-inf +inf]", sort_by="query_num", sort_ascending=False)
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        jsonschema.validate(response1.get("response"), schema.query_transaction_schema)
        jsonschema.validate(response2.get("response"), schema.query_transaction_schema)
        # Check we got the correct results
        self.assertEqual(response1["response"]["total"], 2)
        self.assertEqual(response2["response"]["total"], 2)
        # Check sorted order is correct
        self.assertEqual(response1["response"]["results"][0]["header"]["txn_id"], LOW_TXN_ID, "First result in ascending query was not sorted")
        self.assertEqual(response2["response"]["results"][0]["header"]["txn_id"], HIGH_TXN_ID, "First result in ascending query was not sorted")

    def test_query_transactions_raises_400_with_bad_query(self):
        response = self.client.query_transactions(QUERY_TXN_TYPE, "invalid-")
        expected_response = {
            "status": 400,
            "ok": False,
            "response": {"error": {"type": "BAD_REQUEST", "details": "Syntax error at offset 7 near 'invalid'"}},
        }
        self.assertEqual(response, expected_response)

    def test_query_transactions_raises_400_with_bad_transaction_type(self):
        response = self.client.query_transactions("invalidbananatype", "*")
        expected_response = {"status": 400, "ok": False, "response": {"error": {"type": "BAD_REQUEST", "details": "Invalid transaction type"}}}
        self.assertEqual(response, expected_response)

    # CLEANUP #

    def clean_up_transaction_types(self):
        self.client.delete_smart_contract(SC_ID)
        self.client.delete_transaction_type(TEST_TXN_TYPE)
        self.client.delete_transaction_type(QUERY_TXN_TYPE)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestTransactions("set_up_transaction_types"))
    suite.addTest(TestTransactions("test_create_transaction_with_empty_string_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_nonempty_string_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_empty_object_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_nonempty_object_payload"))
    suite.addTest(TestTransactions("test_create_transaction_with_tag"))
    suite.addTest(TestTransactions("test_create_transaction_with_callback"))
    suite.addTest(TestTransactions("test_create_transaction_for_smart_contract"))
    suite.addTest(TestTransactions("test_create_transaction_fails_without_transaction_type"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_all_valid_transactions"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_some_nonexisting_transaction_types"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_some_invalid_transactions"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_all_nonexistant_transaction_types"))
    suite.addTest(TestTransactions("test_create_bulk_transactions_with_all_invalid_transactions"))
    suite.addTest(TestTransactions("set_up_queryable_transactions"))
    suite.addTest(TestTransactions("wait_for_blocks"))
    suite.addTest(TestTransactions("test_get_transaction_returns_stub_if_not_in_block"))
    suite.addTest(TestTransactions("test_get_transaction_with_empty_string_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_nonempty_string_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_empty_object_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_nonempty_object_payload"))
    suite.addTest(TestTransactions("test_get_transaction_with_tag"))
    suite.addTest(TestTransactions("test_get_transaction_from_bulk_submission"))
    suite.addTest(TestTransactions("test_get_transaction_fails_with_bad_id"))
    suite.addTest(TestTransactions("test_query_transactions_generic"))
    suite.addTest(TestTransactions("test_query_transactions_by_timestamp"))
    suite.addTest(TestTransactions("test_query_transactions_by_block_id"))
    suite.addTest(TestTransactions("test_query_transactions_by_general_tag"))
    suite.addTest(TestTransactions("test_query_transactions_by_invoker"))
    suite.addTest(TestTransactions("test_query_transactions_verbatim"))
    suite.addTest(TestTransactions("test_query_transactions_ids_only"))
    suite.addTest(TestTransactions("test_query_transactions_paging"))
    suite.addTest(TestTransactions("test_query_transactions_by_custom_text"))
    suite.addTest(TestTransactions("test_query_transactions_by_custom_tag"))
    suite.addTest(TestTransactions("test_query_transactions_by_custom_num"))
    suite.addTest(TestTransactions("test_query_transactions_raises_400_with_bad_query"))
    suite.addTest(TestTransactions("test_query_transactions_raises_400_with_bad_transaction_type"))
    suite.addTest(TestTransactions("clean_up_transaction_types"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
