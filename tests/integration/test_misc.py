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

from tests.integration import schema
import dragonchain_sdk

VERIFIED_BLOCK_ID = None
UNVERIFIED_BLOCK_ID = None


class TestMisc(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    # STATUS #

    def test_get_status(self):
        response = self.client.get_status()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.get_status_schema)

    # GET PENDING VERIFICATIONS #

    # First we have to create a fresh block (which requires a transaction type)
    def set_up_new_block_for_verification(self):
        self.client.create_transaction_type("banana_salad")
        transaction_id = self.client.create_transaction("banana_salad", "some data")
        # Sleep for block to be created
        time.sleep(8)
        transaction = self.client.get_transaction(transaction_id["response"]["transaction_id"])
        global UNVERIFIED_BLOCK_ID
        UNVERIFIED_BLOCK_ID = transaction["response"]["header"]["block_id"]

    def test_get_pending_verifications_schema_is_valid(self):
        response = self.client.get_pending_verifications(UNVERIFIED_BLOCK_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        # It's hard to check anything except simple schema validation, since we don't know how many verifications have already gone through
        jsonschema.validate(response.get("response"), schema.pending_verifications_schema)

    def pending_verifications_cleanup(self):
        try:
            self.client.delete_transaction_type("banana_salad")
        except Exception:
            pass

    # GET VERIFICATIONS #

    # First we have to find the block id of a block with verifications through level 5 to test
    def find_verified_block(self):
        # Get the oldest block on the chain and check if it's verified
        block_response = self.client.query_blocks("*", sort_by="block_id", sort_ascending=True, limit=1)
        block_id = block_response["response"]["results"][0]["header"]["block_id"]
        # Check that it has verifications
        verifications_response = self.client.get_verifications(block_id, 5)
        # Ensure that we found results
        self.assertGreater(len(verifications_response["response"]), 0, "No block with all verification levels found")
        global VERIFIED_BLOCK_ID
        VERIFIED_BLOCK_ID = block_id

    def test_get_l2_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 2)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l2_verifications_schema)

    def test_get_l3_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 3)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l3_verifications_schema)

    def test_get_l4_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 4)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l4_verifications_schema)

    def test_get_l5_verifications(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(VERIFIED_BLOCK_ID, 5)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.l5_verifications_schema)

    def test_get_all_verifications_for_block(self):
        self.assertIsNotNone(VERIFIED_BLOCK_ID, "No block with all verification levels found")
        response = self.client.get_verifications(block_id=VERIFIED_BLOCK_ID)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.all_verifications_schema)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestMisc("test_get_status"))
    suite.addTest(TestMisc("set_up_new_block_for_verification"))
    suite.addTest(TestMisc("test_get_pending_verifications_schema_is_valid"))
    suite.addTest(TestMisc("pending_verifications_cleanup"))
    suite.addTest(TestMisc("find_verified_block"))
    suite.addTest(TestMisc("test_get_l2_verifications"))
    suite.addTest(TestMisc("test_get_l3_verifications"))
    suite.addTest(TestMisc("test_get_l4_verifications"))
    suite.addTest(TestMisc("test_get_l5_verifications"))
    suite.addTest(TestMisc("test_get_all_verifications_for_block"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
