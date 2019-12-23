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

import jsonschema

from tests.integration import schema
import dragonchain_sdk

ETHEREUM_INTERCHAIN_NAME_1 = "eth_integration_1"
ETHEREUM_INTERCHAIN_BODY = {
    "version": "1",
    "blockchain": "ethereum",
    "name": ETHEREUM_INTERCHAIN_NAME_1,
    "rpc_address": "http://internal-Parity-Ropsten-Internal-1699752391.us-west-2.elb.amazonaws.com:8545",
    "chain_id": 3,
    "address": "0x75901edd83835ca01B525C8B8F496A5dA3F9ebd5",
}
ETHEREUM_INTERCHAIN_NAME_2 = "eth_integration_2"

BITCOIN_INTERCHAIN_NAME_1 = "btc_integration_1"
BITCOIN_INTERCHAIN_BODY = {
    "version": "1",
    "blockchain": "bitcoin",
    "name": BITCOIN_INTERCHAIN_NAME_1,
    "rpc_address": "http://internal-Btc-Testnet-Internal-1334656512.us-west-2.elb.amazonaws.com:18332",
    "testnet": True,
    "address": "mgAjUvttNiuDcgRakGaAyR8jeB75YujF7c",
}
BITCOIN_INTERCHAIN_NAME_2 = "btc_integration_2"

BINANCE_INTERCHAIN_NAME_1 = "bnb_integration_1"
BINANCE_INTERCHAIN_BODY = {
    "version": "1",
    "blockchain": "binance",
    "name": BINANCE_INTERCHAIN_NAME_1,
    "node_url": "http://binance-node.dragonchain.com",
    "rpc_port": 26657,
    "api_port": 11699,
    "testnet": True,
    "address": "tbnb1st0kkjzxsy4dpdr96znpqmfxadyn48ynjry9zd",
}
BINANCE_INTERCHAIN_NAME_2 = "bnb_integration_2"


class TestInterchain(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()
        self.maxDiff = None  # allows max display of diffs in test logs

    # CREATE #

    def test_create_ethereum_interchain_with_values(self):
        response = self.client.create_ethereum_interchain(
            ETHEREUM_INTERCHAIN_NAME_1,
            "F+byGRzOerQOYI2B5Kdw2dMVWZ7y9Bb8eWHuSm8EiPY=",
            "http://internal-Parity-Ropsten-Internal-1699752391.us-west-2.elb.amazonaws.com:8545",
            3,
        )
        self.assertEqual(response, {"ok": True, "status": 201, "response": ETHEREUM_INTERCHAIN_BODY}, response)

    def test_create_ethereum_interchain_with_defaults(self):
        response = self.client.create_ethereum_interchain(ETHEREUM_INTERCHAIN_NAME_2, chain_id=1)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.ethereum_interchain_at_rest_schema)

    def test_create_ethereum_interchain_fails_with_existing_name(self):
        response = self.client.create_ethereum_interchain(ETHEREUM_INTERCHAIN_NAME_2, chain_id=1)
        expected_response = {
            "status": 409,
            "ok": False,
            "response": {"error": {"type": "INTERCHAIN_CONFLICT", "details": "An interchain network with the name you provided already exists"}},
        }
        self.assertEqual(response, expected_response)

    def test_create_ethereum_interchain_fails_with_bad_rpc_address(self):
        response = self.client.create_ethereum_interchain("garbage", rpc_address="http://youcantGETthis.whatever")
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400, response)
        self.assertTrue(response.get("response")["error"]["details"].startswith("Error trying to contact ethereum rpc node. Error: "), response)

    def test_create_ethereum_interchain_fails_with_mismatching_chain_id(self):
        response = self.client.create_ethereum_interchain(
            "garbage", rpc_address="http://internal-Parity-Ropsten-Internal-1699752391.us-west-2.elb.amazonaws.com:8545", chain_id=999
        )
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {"error": {"type": "BAD_REQUEST", "details": "User provided chain id 999, but RPC reported chain id 3"}},
            },
            response,
        )

    def test_create_ethereum_interchain_fails_with_bad_private_key(self):
        response = self.client.create_ethereum_interchain("garbage", private_key="c29tZSBzdHVmZiBpcyBjb29sCg==", chain_id=1)
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {"error": {"type": "BAD_REQUEST", "details": "Provided private key did not successfully decode into a valid key"}},
            },
            response,
        )

    def test_create_ethereum_interchain_fails_without_chain_id_or_rpc_address(self):
        response = self.client.create_ethereum_interchain("garbage")
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {
                    "error": {
                        "type": "BAD_REQUEST",
                        "details": "If an rpc address is not provided, a valid chain id must be provided. ETH_MAIN = 1, ETH_ROPSTEN = 3, ETC_MAIN = 61",
                    }
                },
            },
            response,
        )

    def test_create_bitcoin_interchain_with_values(self):
        response = self.client.create_bitcoin_interchain(
            BITCOIN_INTERCHAIN_NAME_1,
            True,
            "F+byGRzOerQOYI2B5Kdw2dMVWZ7y9Bb8eWHuSm8EiPY=",
            "http://internal-Btc-Testnet-Internal-1334656512.us-west-2.elb.amazonaws.com:18332",
            "Yml0Y29pbnJwYzpkcmFnb24=",
            False,
        )
        self.assertEqual(response, {"status": 201, "ok": True, "response": BITCOIN_INTERCHAIN_BODY}, response)

    def test_create_bitcoin_interchain_with_defaults(self):
        response = self.client.create_bitcoin_interchain(BITCOIN_INTERCHAIN_NAME_2, testnet=False)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.bitcoin_interchain_at_rest_schema)

    def test_create_bitcoin_interchain_fails_with_existing_name(self):
        response = self.client.create_bitcoin_interchain(BITCOIN_INTERCHAIN_NAME_2, testnet=False)
        expected_response = {
            "status": 409,
            "ok": False,
            "response": {"error": {"type": "INTERCHAIN_CONFLICT", "details": "An interchain network with the name you provided already exists"}},
        }
        self.assertEqual(response, expected_response)

    def test_create_bitcoin_interchain_fails_with_bad_rpc_address(self):
        response = self.client.create_bitcoin_interchain("garbage", testnet=True, rpc_address="http://youcantGETthis.whatever")
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400)
        self.assertTrue(response.get("response")["error"]["details"].startswith("Provided bitcoin node doesn't seem reachable. Error: "), response)

    def test_create_bitcoin_interchain_fails_without_wif_private_key_or_testnet(self):
        response = self.client.create_bitcoin_interchain("garbage")
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {"error": {"type": "BAD_REQUEST", "details": "Parameter boolean 'testnet' must be provided if key is not WIF"}},
            },
            response,
        )

    def test_create_bitcoin_interchain_fails_with_bad_private_key(self):
        response = self.client.create_bitcoin_interchain("garbage", private_key="c29tZSBzdHVmZiBpcyBjb29sCg=", testnet=True)
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {"error": {"type": "BAD_REQUEST", "details": "Provided private key did not successfully decode into a valid key"}},
            },
            response,
        )

    def test_create_binance_interchain_with_values(self):
        url = "http://binance-node.dragonchain.com"
        privkey = "c7603e7928cc9892982d5cda97cc50b9db81ec40ef3f7b9d515fb333151140bf"
        response = self.client.create_binance_interchain(
            name=BINANCE_INTERCHAIN_NAME_1, testnet=True, private_key=privkey, node_url=url, rpc_port=26657, api_port=11699
        )
        self.assertEqual(response, {"status": 201, "ok": True, "response": BINANCE_INTERCHAIN_BODY}, response)

    def test_create_binance_interchain_with_defaults(self):
        response = self.client.create_binance_interchain(name=BINANCE_INTERCHAIN_NAME_2)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 201, response)
        jsonschema.validate(response.get("response"), schema.binance_interchain_at_rest_schema)

    def test_create_binance_interchain_fails_with_bad_node_address(self):
        response = self.client.create_binance_interchain(
            name="garbage", testnet=True, node_url="http://youcantGETthis.whatever", rpc_port=26657, api_port=11699
        )
        self.assertFalse(response.get("ok"), response)
        self.assertEqual(response.get("status"), 400, response)
        self.assertTrue(response.get("response")["error"]["details"].startswith("Provided binance node doesn't seem reachable."), response)

    def test_create_binance_interchain_fails_with_bad_private_key(self):
        bad_hex = "9iQWROmdJ3iGwIZVDghnp2WpIejd0dpb9KPvgDEA06N3B0zp9CGOW5yAf09f8d8c"  # 64 random chars
        response = self.client.create_binance_interchain(name="garbage", testnet=True, private_key=bad_hex)
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {"error": {"type": "BAD_REQUEST", "details": "Provided private key did not successfully decode into a valid key."}},
            },
            response,
        )

    # GET #

    def test_get_existing_ethereum_interchain(self):
        response1 = self.client.get_interchain_network("ethereum", ETHEREUM_INTERCHAIN_NAME_1)
        response2 = self.client.get_interchain_network("ethereum", ETHEREUM_INTERCHAIN_NAME_2)
        self.assertEqual(response1, {"status": 200, "ok": True, "response": ETHEREUM_INTERCHAIN_BODY})
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.ethereum_interchain_at_rest_schema)

    def test_get_existing_bitcoin_interchain(self):
        response1 = self.client.get_interchain_network("bitcoin", BITCOIN_INTERCHAIN_NAME_1)
        response2 = self.client.get_interchain_network("bitcoin", BITCOIN_INTERCHAIN_NAME_2)
        self.assertEqual(response1, {"status": 200, "ok": True, "response": BITCOIN_INTERCHAIN_BODY})
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.bitcoin_interchain_at_rest_schema)

    def test_get_existing_binance_interchain(self):
        response1 = self.client.get_interchain_network("binance", BINANCE_INTERCHAIN_NAME_1)
        response2 = self.client.get_interchain_network("binance", BINANCE_INTERCHAIN_NAME_2)
        self.assertEqual(response1, {"status": 200, "ok": True, "response": BINANCE_INTERCHAIN_BODY})
        self.assertTrue(response2.get("ok"), response2)
        self.assertEqual(response2.get("status"), 200, response2)
        jsonschema.validate(response2.get("response"), schema.binance_interchain_at_rest_schema)

    def test_get_non_existing_interchains(self):
        response = self.client.get_interchain_network("bitcoin", "doesntexist")
        self.assertEqual(
            response,
            {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}}},
            response,
        )

    def test_get_bad_blockchain_type(self):
        response = self.client.get_interchain_network("doesntexist", "doesntexist")
        self.assertEqual(
            response,
            {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}}},
            response,
        )

    # LIST #

    def test_list_ethereum_interchains(self):
        response = self.client.list_interchain_networks("ethereum")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.ethereum_interchain_list_schema)
        # Check that our earlier created api key is in the output
        self.assertIn(ETHEREUM_INTERCHAIN_BODY, response["response"]["interchains"], response)

    def test_list_bitcoin_interchains(self):
        response = self.client.list_interchain_networks("bitcoin")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.bitcoin_interchain_list_schema)
        # Check that our earlier created api key is in the output
        self.assertIn(BITCOIN_INTERCHAIN_BODY, response["response"]["interchains"], response)

    def test_list_binance_interchains(self):
        response = self.client.list_interchain_networks("binance")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)

        jsonschema.validate(response.get("response"), schema.binance_interchain_list_schema)
        # Check that our earlier created api key is in the output
        self.assertIn(BINANCE_INTERCHAIN_BODY, response["response"]["interchains"], response)

    def test_list_bad_blockchain_interchains(self):
        response = self.client.list_interchain_networks("fakeblockchain")
        self.assertEqual(
            response,
            {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}}},
            response,
        )

    # UPDATE #

    def test_update_ethereum_interchain_only_updates_provided_fields(self):
        before_body = self.client.get_interchain_network("ethereum", ETHEREUM_INTERCHAIN_NAME_2)["response"]
        before_body["address"] = "0x8c4BB36A40dc7CA3F42851E732CA924110862CfE"
        response = self.client.update_ethereum_interchain(
            ETHEREUM_INTERCHAIN_NAME_2, private_key="0da389225dce935ba95a5f504f470a43bbfeaf7e8c3a27e30348291f8c7f42a9"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        # Check that after changing the private key, the only thing that's changed is the address
        self.assertEqual(response.get("response"), before_body, response)

    def test_update_ethereum_interchain_returns_at_rest_object(self):
        response = self.client.update_ethereum_interchain(ETHEREUM_INTERCHAIN_NAME_2, chain_id=1)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.ethereum_interchain_at_rest_schema)

    def test_update_ethereum_fails_with_mismatching_chain_id(self):
        response = self.client.update_ethereum_interchain(ETHEREUM_INTERCHAIN_NAME_2, chain_id=999)
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {"error": {"type": "BAD_REQUEST", "details": "User provided chain id 999, but RPC reported chain id 1"}},
            },
            response,
        )

    def test_update_bitcoin_interchain_only_updates_provided_fields(self):
        before_body = self.client.get_interchain_network("bitcoin", BITCOIN_INTERCHAIN_NAME_2)["response"]
        before_body["address"] = "1FXyBqD161Q51nE1eSFp9uzjVG2TWoNruE"
        response = self.client.update_bitcoin_interchain(BITCOIN_INTERCHAIN_NAME_2, private_key="jVgEEtR8WbPHRw3UGvgJzjqSzJz5lFknzxUhSPEmMaE=")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        # Check that after changing the private key, the only thing that's changed is the address
        self.assertEqual(response.get("response"), before_body, response)

    def test_update_bitcoin_interchain_returns_at_rest_object(self):
        response = self.client.update_bitcoin_interchain(BITCOIN_INTERCHAIN_NAME_2, testnet=False)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.bitcoin_interchain_at_rest_schema)

    def test_update_interchains_with_nonexistant_interchain_returns_404(self):
        # attempt to update nonexistent chains:
        response1 = self.client.update_bitcoin_interchain("garbage")
        response2 = self.client.update_ethereum_interchain("garbage")
        response3 = self.client.update_binance_interchain("garbage")
        details_text = "The requested resource(s) cannot be found."
        self.assertEqual(
            response1, {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": details_text}}}, response1,
        )
        self.assertEqual(
            response2, {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": details_text}}}, response2,
        )
        self.assertEqual(
            response3, {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": details_text}}}, response3,
        )

    def test_update_binance_interchain_only_updates_provided_fields(self):
        before_body = self.client.get_interchain_network("binance", BINANCE_INTERCHAIN_NAME_2)["response"]
        before_body["address"] = "tbnb1u06kxdru0we8at0ktd6q4c5qk80zwdyvhzrulk"
        priv_key = "495bb2a3f229eb0abb2bf71a3dca56b31d60c128dfd81e9e907e5eedb67f19a0"
        response = self.client.update_binance_interchain(BINANCE_INTERCHAIN_NAME_2, private_key=priv_key)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        # Check that after changing the private key, the only thing that's changed is the address
        self.assertEqual(response.get("response"), before_body, response)

    def test_update_binance_interchain_returns_at_rest_object(self):
        response = self.client.update_binance_interchain(BINANCE_INTERCHAIN_NAME_2, testnet=True)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.binance_interchain_at_rest_schema)

    # SIGN #

    def test_sign_ethereum_transaction_with_to_and_value(self):
        response = self.client.sign_ethereum_transaction(ETHEREUM_INTERCHAIN_NAME_1, to="0x0000000000000000000000000000000000000000", value="0x0")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_sign_ethereum_transaction_with_data(self):
        response = self.client.sign_ethereum_transaction(
            ETHEREUM_INTERCHAIN_NAME_1, to="0x0000000000000000000000000000000000000000", value="0x0", data="0xdeadbeef"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_sign_ethereum_transaction_with_gas_price(self):
        response = self.client.sign_ethereum_transaction(
            ETHEREUM_INTERCHAIN_NAME_1, to="0x0000000000000000000000000000000000000000", value="0x0", gas_price="0x1234"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_sign_ethereum_transaction_with_gas_limit(self):
        response = self.client.sign_ethereum_transaction(
            ETHEREUM_INTERCHAIN_NAME_1, to="0x0000000000000000000000000000000000000000", value="0x0", gas="0x1234"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_sign_ethereum_transaction_with_nonce(self):
        response = self.client.sign_ethereum_transaction(
            ETHEREUM_INTERCHAIN_NAME_1, to="0x0000000000000000000000000000000000000000", value="0x0", nonce="0x4321"
        )
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_ethereum_transaction_schema)

    def test_sign_ethereum_transaction_with_all_values(self):
        response = self.client.sign_ethereum_transaction(
            ETHEREUM_INTERCHAIN_NAME_1,
            to="0x249A52D7115039a4eB5cd42ca10bbF744F3B678A",
            value="0x1234",
            gas="0x4321",
            gas_price="0xabcd",
            data="0xbadf00d",
            nonce="0x1982",
        )
        # Because we specify all inputs, this signed transaction should be constant
        self.assertEqual(
            response,
            {
                "status": 200,
                "ok": True,
                "response": {
                    "signed": "0xf86982198282abcd82432194249a52d7115039a4eb5cd42ca10bbf744f3b678a821234840badf00d29a0ad00b4c8a14dbd89d1ce934c7ad2dd10c10f3160fb546cd46cd5c369f72afa3fa0262004c8cc710c88db95a6352a518a8e512b897626d33d7ba26ea3948390a464"  # noqa: B950
                },
            },
            response,
        )

    def test_sign_ethereum_transaction_fails_with_bad_to_value(self):
        response = self.client.sign_ethereum_transaction(ETHEREUM_INTERCHAIN_NAME_1, "0xnotanaddress", "0x0")
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {
                    "error": {"type": "BAD_REQUEST", "details": "Error signing transaction: Transaction had invalid fields: {'to': '0xnotanaddress'}"}
                },
            },
            response,
        )

    def test_sign_with_bitcoin_returns_not_enough_crypto(self):
        response = self.client.sign_bitcoin_transaction(BITCOIN_INTERCHAIN_NAME_2)
        self.assertEqual(
            response,
            {
                "status": 400,
                "ok": False,
                "response": {
                    "error": {
                        "type": "INSUFFICIENT_CRYPTO",
                        "details": "You do not have enough UTXOs or funds in this address to sign a transaction with",
                    }
                },
            },
            response,
        )

    def test_sign_binance_transaction_with_good_to_address(self):
        good_addy = "tbnb1zesqcktldshz7tat9u74duc037frzwvdq83wan"  # has had txns & a balance.
        response = self.client.sign_binance_transaction(name=BINANCE_INTERCHAIN_NAME_1, amount=1, to_address=good_addy)
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_binance_transaction_schema)

    def test_sign_binance_transaction_fails_with_bad_to_address(self):
        response = self.client.sign_binance_transaction(name=BINANCE_INTERCHAIN_NAME_1, amount=1, to_address="bad_addy")
        error_msg = "[BINANCE] Error signing transaction: 'NoneType' object is not iterable"
        self.assertEqual(response, {"status": 400, "ok": False, "response": {"error": {"type": "BAD_REQUEST", "details": error_msg}}}, response)

    def test_sign_binance_transaction_with_data(self):
        good_addy = "tbnb1zesqcktldshz7tat9u74duc037frzwvdq83wan"
        response = self.client.sign_binance_transaction(name=BINANCE_INTERCHAIN_NAME_1, amount=12345, to_address=good_addy, memo="banana")
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response.get("status"), 200, response)
        jsonschema.validate(response.get("response"), schema.created_binance_transaction_schema)

    # TODO: Come up with a way to test signing bitcoin transactions with actual funds

    # DELETE #

    def test_delete_existing_network_is_successful(self):
        response1 = self.client.delete_interchain_network("bitcoin", BITCOIN_INTERCHAIN_NAME_2)
        self.assertEqual(response1, {"status": 200, "ok": True, "response": {"success": True}}, response1)
        # Ensure we can't get the network after it's been deleted
        response2 = self.client.get_interchain_network("bitcoin", BITCOIN_INTERCHAIN_NAME_2)
        self.assertEqual(
            response2,
            {"status": 404, "ok": False, "response": {"error": {"type": "NOT_FOUND", "details": "The requested resource(s) cannot be found."}}},
            response2,
        )

    def test_delete_nonexisting_network_is_successful(self):
        response = self.client.delete_interchain_network("whatever", "athing")
        self.assertEqual(response, {"status": 200, "ok": True, "response": {"success": True}}, response)

    def interchain_cleanup(self):
        for interchain in [ETHEREUM_INTERCHAIN_NAME_1, ETHEREUM_INTERCHAIN_NAME_2]:
            try:
                self.client.delete_interchain_network("ethereum", interchain)
            except Exception:
                pass
        for interchain in [BITCOIN_INTERCHAIN_NAME_1, BITCOIN_INTERCHAIN_NAME_2]:
            try:
                self.client.delete_interchain_network("bitcoin", interchain)
            except Exception:
                pass
        for interchain in [BINANCE_INTERCHAIN_NAME_1, BINANCE_INTERCHAIN_NAME_2]:
            try:
                self.client.delete_interchain_network("binance", interchain)
            except Exception:
                pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestInterchain("test_create_ethereum_interchain_with_values"))
    suite.addTest(TestInterchain("test_create_ethereum_interchain_with_defaults"))
    suite.addTest(TestInterchain("test_create_ethereum_interchain_fails_with_existing_name"))
    suite.addTest(TestInterchain("test_create_ethereum_interchain_fails_with_bad_rpc_address"))
    suite.addTest(TestInterchain("test_create_ethereum_interchain_fails_with_mismatching_chain_id"))
    suite.addTest(TestInterchain("test_create_ethereum_interchain_fails_with_bad_private_key"))
    suite.addTest(TestInterchain("test_create_ethereum_interchain_fails_without_chain_id_or_rpc_address"))
    suite.addTest(TestInterchain("test_create_bitcoin_interchain_with_values"))
    suite.addTest(TestInterchain("test_create_bitcoin_interchain_with_defaults"))
    suite.addTest(TestInterchain("test_create_bitcoin_interchain_fails_with_existing_name"))
    suite.addTest(TestInterchain("test_create_bitcoin_interchain_fails_with_bad_rpc_address"))
    suite.addTest(TestInterchain("test_create_bitcoin_interchain_fails_without_wif_private_key_or_testnet"))
    suite.addTest(TestInterchain("test_create_bitcoin_interchain_fails_with_bad_private_key"))
    suite.addTest(TestInterchain("test_create_binance_interchain_with_values"))
    suite.addTest(TestInterchain("test_create_binance_interchain_with_defaults"))
    suite.addTest(TestInterchain("test_create_binance_interchain_fails_with_bad_node_address"))
    suite.addTest(TestInterchain("test_create_binance_interchain_fails_with_bad_private_key"))
    suite.addTest(TestInterchain("test_get_existing_ethereum_interchain"))
    suite.addTest(TestInterchain("test_get_existing_bitcoin_interchain"))
    suite.addTest(TestInterchain("test_get_existing_binance_interchain"))
    suite.addTest(TestInterchain("test_get_non_existing_interchains"))
    suite.addTest(TestInterchain("test_get_bad_blockchain_type"))
    suite.addTest(TestInterchain("test_list_ethereum_interchains"))
    suite.addTest(TestInterchain("test_list_bitcoin_interchains"))
    suite.addTest(TestInterchain("test_list_binance_interchains"))
    suite.addTest(TestInterchain("test_list_bad_blockchain_interchains"))
    suite.addTest(TestInterchain("test_update_ethereum_interchain_only_updates_provided_fields"))
    suite.addTest(TestInterchain("test_update_ethereum_interchain_returns_at_rest_object"))
    suite.addTest(TestInterchain("test_update_ethereum_fails_with_mismatching_chain_id"))
    suite.addTest(TestInterchain("test_update_bitcoin_interchain_only_updates_provided_fields"))
    suite.addTest(TestInterchain("test_update_bitcoin_interchain_returns_at_rest_object"))
    suite.addTest(TestInterchain("test_update_interchains_with_nonexistant_interchain_returns_404"))
    suite.addTest(TestInterchain("test_update_binance_interchain_only_updates_provided_fields"))
    suite.addTest(TestInterchain("test_update_binance_interchain_returns_at_rest_object"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_with_to_and_value"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_with_data"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_with_gas_price"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_with_gas_limit"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_with_nonce"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_with_all_values"))
    suite.addTest(TestInterchain("test_sign_ethereum_transaction_fails_with_bad_to_value"))
    suite.addTest(TestInterchain("test_sign_with_bitcoin_returns_not_enough_crypto"))
    suite.addTest(TestInterchain("test_sign_binance_transaction_with_good_to_address"))
    suite.addTest(TestInterchain("test_sign_binance_transaction_fails_with_bad_to_address"))
    suite.addTest(TestInterchain("test_sign_binance_transaction_with_data"))
    suite.addTest(TestInterchain("test_delete_existing_network_is_successful"))
    suite.addTest(TestInterchain("test_delete_nonexisting_network_is_successful"))
    suite.addTest(TestInterchain("interchain_cleanup"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
