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

import sys
import time
import unittest

import jsonschema

import dragonchain_sdk
from tests.integration import schema

TEST_TRANSACTION_TYPE = "test-blocks"
EXISTING_BLOCK = None


class TestBlocks(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    def test_block_set_up(self):
        # We need to post some transactions so a block will be created
        self.client.create_transaction_type(TEST_TRANSACTION_TYPE)
        self.client.create_transaction(TEST_TRANSACTION_TYPE, "string payload", tag="tagging")
        time.sleep(10)
        self.client.create_transaction(TEST_TRANSACTION_TYPE, {"object": "payload"})
        time.sleep(10)

    # QUERY #

    def test_query_blocks_generic(self):
        response = self.client.query_blocks("*")
        self.assertEqual(response.get("status"), 200)
        self.assertTrue(response.get("ok"))
        jsonschema.validate(response.get("response"), schema.query_block_schema)
        self.assertGreaterEqual(response["response"]["total"], 2)  # Assure we have at least as many blocks as we just created
        global EXISTING_BLOCK
        EXISTING_BLOCK = response["response"]["results"][0]

    def test_query_blocks_by_timestamp(self):
        # Get all block timestamp below now, sorted by timestamp
        response1 = self.client.query_blocks("@timestamp:[-inf {}]".format(time.time()), sort_by="timestamp", sort_ascending=True)
        response2 = self.client.query_blocks("@timestamp:[-inf {}]".format(time.time()), sort_by="timestamp", sort_ascending=False)
        response3 = self.client.query_blocks("@timestamp:[{} +inf]".format(time.time()))  # Should not return any results
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response2.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response2.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_block_schema)
        jsonschema.validate(response2.get("response"), schema.query_block_schema)
        jsonschema.validate(response3.get("response"), schema.query_block_schema)
        # Check our query that shouldn't have gotten any results worked
        self.assertEqual(response3["response"]["total"], 0)
        # Check sorted order is correct
        self.assertGreater(
            int(response1["response"]["results"][1]["header"]["timestamp"]), int(response1["response"]["results"][0]["header"]["timestamp"])
        )
        self.assertGreater(
            int(response2["response"]["results"][0]["header"]["timestamp"]), int(response2["response"]["results"][1]["header"]["timestamp"])
        )

    def test_query_blocks_by_id(self):
        current_block = int((time.time() - 1432238220) / 5) + 1
        response1 = self.client.query_blocks("@block_id:[-inf {}]".format(current_block), sort_by="block_id", sort_ascending=True)
        response2 = self.client.query_blocks("@block_id:[-inf {}]".format(current_block), sort_by="block_id", sort_ascending=False)
        response3 = self.client.query_blocks("@block_id:[{} +inf]".format(current_block))  # Should not return any results
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response2.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response2.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_block_schema)
        jsonschema.validate(response2.get("response"), schema.query_block_schema)
        jsonschema.validate(response3.get("response"), schema.query_block_schema)
        # Check our query that shouldn't have gotten any results worked
        self.assertEqual(response3["response"]["total"], 0)
        # Check sorted order is correct
        self.assertGreater(
            int(response1["response"]["results"][1]["header"]["block_id"]), int(response1["response"]["results"][0]["header"]["block_id"])
        )
        self.assertGreater(
            int(response2["response"]["results"][0]["header"]["block_id"]), int(response2["response"]["results"][1]["header"]["block_id"])
        )

    def test_query_blocks_by_prev_id(self):
        prev_id = EXISTING_BLOCK["header"]["prev_id"]
        # Do a number query with min/max as an exact id (essentially searching by exact prev_id)
        response = self.client.query_blocks("@prev_id:[{} {}]".format(prev_id, prev_id))
        self.assertEqual(response.get("status"), 200, response)
        self.assertTrue(response.get("ok"), response)
        jsonschema.validate(response.get("response"), schema.query_block_schema)
        # Check that our query only fetched one result, (since only one prev_id should match)
        self.assertEqual(response["response"]["total"], 1)
        # Check the result we got contains the block we expect
        self.assertIn(EXISTING_BLOCK, response["response"]["results"])

    def test_query_blocks_ids_only(self):
        response = self.client.query_blocks("*", ids_only=True)
        self.assertEqual(response.get("status"), 200, response)
        self.assertTrue(response.get("ok"), response)
        jsonschema.validate(response.get("response"), schema.query_ids_only)
        self.assertGreaterEqual(response["response"]["total"], 2)

    def test_query_blocks_paging(self):
        # For testing offset and limit parameters in a query
        response1 = self.client.query_blocks("*", limit=0)
        response2 = self.client.query_blocks("*", offset=0, limit=1, ids_only=True)
        response3 = self.client.query_blocks("*", offset=1, limit=1, ids_only=True)
        self.assertEqual(response1.get("status"), 200, response1)
        self.assertEqual(response2.get("status"), 200, response2)
        self.assertEqual(response3.get("status"), 200, response3)
        self.assertTrue(response1.get("ok"), response1)
        self.assertTrue(response2.get("ok"), response2)
        self.assertTrue(response3.get("ok"), response3)
        jsonschema.validate(response1.get("response"), schema.query_block_schema)
        jsonschema.validate(response2.get("response"), schema.query_ids_only)
        jsonschema.validate(response3.get("response"), schema.query_ids_only)
        # Check we got the correct totals
        self.assertGreaterEqual(response1["response"]["total"], 2)
        self.assertGreaterEqual(response2["response"]["total"], 2)
        self.assertGreaterEqual(response3["response"]["total"], 2)
        # Check that limit 0 returned an empty array
        self.assertEqual(response1["response"]["results"], [], "Limit 0 returned actual results")
        # Ensure the query returned the expected number of results in the array
        self.assertEqual(len(response2["response"]["results"]), 1)
        self.assertEqual(len(response3["response"]["results"]), 1)
        # Ensure our paginated results didn't return the same thing (same query with different offsets)
        self.assertNotEqual(response2["response"]["results"], response3["response"]["results"])

    def test_query_blocks_raises_400_with_bad_query(self):
        response = self.client.query_blocks("invalid-")
        expected_response = {
            "status": 400,
            "ok": False,
            "response": {"error": {"type": "BAD_REQUEST", "details": "Syntax error at offset 7 near 'invalid'"}},
        }
        self.assertEqual(response, expected_response)

    # GET #

    def test_get_block_with_valid_id(self):
        response = self.client.get_block(EXISTING_BLOCK["header"]["block_id"])
        expected_response = {"status": 200, "ok": True, "response": EXISTING_BLOCK}
        self.assertEqual(expected_response, response)

    def test_get_block_with_invalid_id_returns_404(self):
        response = self.client.get_block("9876543210")
        expected_response = {
            "status": 404,
            "ok": False,
            "response": {"error": {"details": "The requested resource(s) cannot be found.", "type": "NOT_FOUND"}},
        }
        self.assertEqual(expected_response, response)

    def test_block_tear_down(self):
        self.client.delete_transaction_type(TEST_TRANSACTION_TYPE)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestBlocks("test_block_set_up"))
    suite.addTest(TestBlocks("test_query_blocks_generic"))
    suite.addTest(TestBlocks("test_query_blocks_by_timestamp"))
    suite.addTest(TestBlocks("test_query_blocks_by_id"))
    suite.addTest(TestBlocks("test_query_blocks_by_prev_id"))
    suite.addTest(TestBlocks("test_query_blocks_ids_only"))
    suite.addTest(TestBlocks("test_query_blocks_paging"))
    suite.addTest(TestBlocks("test_query_blocks_raises_400_with_bad_query"))
    suite.addTest(TestBlocks("test_get_block_with_valid_id"))
    suite.addTest(TestBlocks("test_get_block_with_invalid_id_returns_404"))
    suite.addTest(TestBlocks("test_block_tear_down"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
