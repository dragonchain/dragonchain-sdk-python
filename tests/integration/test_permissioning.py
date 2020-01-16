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
import unittest

import dragonchain_sdk

PERMISSION_TESTING_KEY_ID = None
PERMISSION_TESTING_KEY = None

DEFAULT_PERMISSIONS_DOCUMENT = {
    "version": "1",
    "default_allow": True,
    "permissions": {"api_keys": {"allow_create": False, "allow_update": False, "allow_delete": False}},
}


def default_action_forbidden_response(action):
    return {
        "status": 403,
        "ok": False,
        "response": {"error": {"type": "ACTION_FORBIDDEN", "details": "This key is not allowed to perform {}".format(action)}},
    }


# Api key functions
create_api_key = frozenset(
    {"fn": "create_api_key", "params": (), "permission_name": "create_api_key", "permission_group": "api_keys", "permission_type": "create"}.items()
)
update_api_key = frozenset(
    {
        "fn": "update_api_key",
        "params": ("whatever",),
        "permission_name": "update_api_key",
        "permission_group": "api_keys",
        "permission_type": "update",
    }.items()
)
delete_api_key = frozenset(
    {
        "fn": "delete_api_key",
        "params": ("whatever",),
        "permission_name": "delete_api_key",
        "permission_group": "api_keys",
        "permission_type": "delete",
    }.items()
)
get_api_key = frozenset(
    {
        "fn": "get_api_key",
        "params": ("whatever",),
        "permission_name": "get_api_key",
        "permission_group": "api_keys",
        "permission_type": "read",
    }.items()
)
list_api_keys = frozenset(
    {"fn": "list_api_keys", "params": (), "permission_name": "list_api_keys", "permission_group": "api_keys", "permission_type": "read"}.items()
)
# Block functions
get_block = frozenset(
    {"fn": "get_block", "params": ("block_id",), "permission_name": "get_block", "permission_group": "blocks", "permission_type": "read"}.items()
)
query_blocks = frozenset(
    {
        "fn": "query_blocks",
        "params": ("querystr",),
        "permission_name": "query_blocks",
        "permission_group": "blocks",
        "permission_type": "read",
    }.items()
)
# Interchain functions
create_bitcoin_interchain = frozenset(
    {
        "fn": "create_bitcoin_interchain",
        "params": ("name", True, "a",),
        "permission_name": "create_interchain",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
update_bitcoin_interchain = frozenset(
    {
        "fn": "update_bitcoin_interchain",
        "params": ("name",),
        "permission_name": "update_interchain",
        "permission_group": "interchains",
        "permission_type": "update",
    }.items()
)
sign_bitcoin_transaction = frozenset(
    {
        "fn": "sign_bitcoin_transaction",
        "params": ("name",),
        "permission_name": "create_interchain_transaction",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
create_ethereum_interchain = frozenset(
    {
        "fn": "create_ethereum_interchain",
        "params": ("name", "a",),
        "permission_name": "create_interchain",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
update_ethereum_interchain = frozenset(
    {
        "fn": "update_ethereum_interchain",
        "params": ("name",),
        "permission_name": "update_interchain",
        "permission_group": "interchains",
        "permission_type": "update",
    }.items()
)
sign_ethereum_transaction = frozenset(
    {
        "fn": "sign_ethereum_transaction",
        "params": ("name", "0x0000000000000000000000000000000000000000", "0x0",),
        "permission_name": "create_interchain_transaction",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
create_binance_interchain = frozenset(
    {
        "fn": "create_binance_interchain",
        "params": ("name", True, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",),
        "permission_name": "create_interchain",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
update_binance_interchain = frozenset(
    {
        "fn": "update_binance_interchain",
        "params": ("name",),
        "permission_name": "update_interchain",
        "permission_group": "interchains",
        "permission_type": "update",
    }.items()
)
sign_binance_transaction = frozenset(
    {
        "fn": "sign_binance_transaction",
        "params": ("name", 1, "abc",),
        "permission_name": "create_interchain_transaction",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
get_interchain_network = frozenset(
    {
        "fn": "get_interchain_network",
        "params": ("bitcoin", "whatever",),
        "permission_name": "get_interchain",
        "permission_group": "interchains",
        "permission_type": "read",
    }.items()
)
delete_interchain_network = frozenset(
    {
        "fn": "delete_interchain_network",
        "params": ("bitcoin", "whatever",),
        "permission_name": "delete_interchain",
        "permission_group": "interchains",
        "permission_type": "delete",
    }.items()
)
list_interchain_networks = frozenset(
    {
        "fn": "list_interchain_networks",
        "params": ("bitcoin",),
        "permission_name": "list_interchains",
        "permission_group": "interchains",
        "permission_type": "read",
    }.items()
)
set_default_interchain_network = frozenset(
    {
        "fn": "set_default_interchain_network",
        "params": ("bitcoin", "whatever",),
        "permission_name": "set_default_interchain",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
get_default_interchain_network = frozenset(
    {
        "fn": "get_default_interchain_network",
        "params": (),
        "permission_name": "get_default_interchain",
        "permission_group": "interchains",
        "permission_type": "read",
    }.items()
)
create_bitcoin_transaction = frozenset(
    {
        "fn": "create_bitcoin_transaction",
        "params": ("BTC_MAINNET",),
        "permission_name": "create_interchain_transaction_legacy",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
create_ethereum_transaction = frozenset(
    {
        "fn": "create_ethereum_transaction",
        "params": ("ETH_MAINNET", "0x0000000000000000000000000000000000000000", "0x0",),
        "permission_name": "create_interchain_transaction_legacy",
        "permission_group": "interchains",
        "permission_type": "create",
    }.items()
)
get_public_blockchain_addresses = frozenset(
    {
        "fn": "get_public_blockchain_addresses",
        "params": (),
        "permission_name": "get_interchain_legacy",
        "permission_group": "interchains",
        "permission_type": "read",
    }.items()
)
# Misc Functions
get_status = frozenset(
    {"fn": "get_status", "params": (), "permission_name": "get_status", "permission_group": "misc", "permission_type": "read"}.items()
)
# Contract Functions
get_smart_contract = frozenset(
    {
        "fn": "get_smart_contract",
        "params": ("id",),
        "permission_name": "get_contract",
        "permission_group": "contracts",
        "permission_type": "read",
    }.items()
)
get_smart_contract_logs = frozenset(
    {
        "fn": "get_smart_contract_logs",
        "params": ("id",),
        "permission_name": "get_contract_logs",
        "permission_group": "contracts",
        "permission_type": "read",
    }.items()
)
list_smart_contracts = frozenset(
    {
        "fn": "list_smart_contracts",
        "params": (),
        "permission_name": "list_contracts",
        "permission_group": "contracts",
        "permission_type": "read",
    }.items()
)
create_smart_contract = frozenset(
    {
        "fn": "create_smart_contract",
        "params": ("type", "blah", "cmd",),
        "permission_name": "create_contract",
        "permission_group": "contracts",
        "permission_type": "create",
    }.items()
)
update_smart_contract = frozenset(
    {
        "fn": "update_smart_contract",
        "params": ("id",),
        "permission_name": "update_contract",
        "permission_group": "contracts",
        "permission_type": "update",
    }.items()
)
delete_smart_contract = frozenset(
    {
        "fn": "delete_smart_contract",
        "params": ("id",),
        "permission_name": "delete_contract",
        "permission_group": "contracts",
        "permission_type": "delete",
    }.items()
)
get_smart_contract_object = frozenset(
    {
        "fn": "get_smart_contract_object",
        "params": ("key", "id",),
        "permission_name": "get_contract_object",
        "permission_group": "contracts",
        "permission_type": "read",
    }.items()
)
list_smart_contract_objects = frozenset(
    {
        "fn": "list_smart_contract_objects",
        "params": ("key", "id",),
        "permission_name": "list_contract_objects",
        "permission_group": "contracts",
        "permission_type": "read",
    }.items()
)
# Transaction type functions
get_transaction_type = frozenset(
    {
        "fn": "get_transaction_type",
        "params": ("type",),
        "permission_name": "get_transaction_type",
        "permission_group": "transaction_types",
        "permission_type": "read",
    }.items()
)
list_transaction_types = frozenset(
    {
        "fn": "list_transaction_types",
        "params": (),
        "permission_name": "list_transaction_types",
        "permission_group": "transaction_types",
        "permission_type": "read",
    }.items()
)
create_transaction_type = frozenset(
    {
        "fn": "create_transaction_type",
        "params": ("whatever",),
        "permission_name": "create_transaction_type",
        "permission_group": "transaction_types",
        "permission_type": "create",
    }.items()
)
delete_transaction_type = frozenset(
    {
        "fn": "delete_transaction_type",
        "params": ("whatever",),
        "permission_name": "delete_transaction_type",
        "permission_group": "transaction_types",
        "permission_type": "delete",
    }.items()
)
# Transaction functions
create_transaction = frozenset(
    {
        "fn": "create_transaction",
        "params": ("mytype", "payload",),
        "permission_name": "create_transaction",
        "permission_group": "transactions",
        "permission_type": "create",
    }.items()
)
query_transactions = frozenset(
    {
        "fn": "query_transactions",
        "params": ("type", "querystr",),
        "permission_name": "query_transactions",
        "permission_group": "transactions",
        "permission_type": "read",
    }.items()
)
get_transaction = frozenset(
    {
        "fn": "get_transaction",
        "params": ("id",),
        "permission_name": "get_transaction",
        "permission_group": "transactions",
        "permission_type": "read",
    }.items()
)
# Verification functions
get_verifications = frozenset(
    {
        "fn": "get_verifications",
        "params": ("id",),
        "permission_name": "get_verifications",
        "permission_group": "verifications",
        "permission_type": "read",
    }.items()
)
get_pending_verifications = frozenset(
    {
        "fn": "get_pending_verifications",
        "params": ("id",),
        "permission_name": "get_pending_verifications",
        "permission_group": "verifications",
        "permission_type": "read",
    }.items()
)

permission_groups = ["api_keys", "blocks", "interchains", "misc", "contracts", "transaction_types", "transactions", "verifications"]

all_client_functions = [
    create_api_key,
    update_api_key,
    delete_api_key,
    get_api_key,
    list_api_keys,
    get_block,
    query_blocks,
    create_bitcoin_interchain,
    update_bitcoin_interchain,
    sign_bitcoin_transaction,
    create_ethereum_interchain,
    update_ethereum_interchain,
    sign_ethereum_transaction,
    create_binance_interchain,
    update_binance_interchain,
    sign_binance_transaction,
    get_interchain_network,
    delete_interchain_network,
    list_interchain_networks,
    # set_default_interchain_network,  L5 Only
    # get_default_interchain_network,  L5 Only
    create_bitcoin_transaction,
    create_ethereum_transaction,
    get_public_blockchain_addresses,
    get_status,
    get_smart_contract,
    get_smart_contract_logs,
    list_smart_contracts,
    create_smart_contract,
    update_smart_contract,
    delete_smart_contract,
    get_smart_contract_object,
    list_smart_contract_objects,
    get_transaction_type,
    list_transaction_types,
    create_transaction_type,
    delete_transaction_type,
    create_transaction,
    query_transactions,
    get_transaction,
    get_verifications,
    get_pending_verifications,
]


def get_permission_type_functions(perm_type):
    ret_val = set()
    for fn in all_client_functions:
        parsed_fn = dict(fn)
        if parsed_fn["permission_type"] == perm_type:
            ret_val.add(fn)
    return ret_val


def get_permission_group_functions(perm_group):
    ret_val = set()
    for fn in all_client_functions:
        parsed_fn = dict(fn)
        if parsed_fn["permission_group"] == perm_group:
            ret_val.add(fn)
    return ret_val


class TestPermissioning(unittest.TestCase):
    def setUp(self):
        self.client = dragonchain_sdk.create_client()

    def create_default_permissions_testing_key(self):
        response = self.client.create_api_key()
        self.assertTrue(response.get("ok"), response)
        self.assertEqual(response["response"].get("permissions_document"), DEFAULT_PERMISSIONS_DOCUMENT, response)
        global PERMISSION_TESTING_KEY
        global PERMISSION_TESTING_KEY_ID
        PERMISSION_TESTING_KEY = response["response"]["key"]
        PERMISSION_TESTING_KEY_ID = response["response"]["id"]

    def default_permissions_denies_create_update_delete_api_keys(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        self.assertEqual(c.create_api_key(), default_action_forbidden_response("create_api_key"))
        self.assertEqual(c.update_api_key("whatever"), default_action_forbidden_response("update_api_key"))
        self.assertEqual(c.delete_api_key("whatever"), default_action_forbidden_response("delete_api_key"))

    def default_allow_false_forbids_all_functions(self):
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": False, "permissions": {}}
        )
        self.assertTrue(setup.get("ok"), setup)
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for method in all_client_functions:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertEqual(response.get("status"), 403, method)

    def default_allow_true_allows_all_functions(self):
        setup = self.client.update_api_key(PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": True, "permissions": {}})
        self.assertTrue(setup.get("ok"), setup)
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for method in all_client_functions:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertNotEqual(response.get("status"), 403, method)

    # GLOBAL GROUP #

    def global_allow_create_works_with_all_create_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Check default true, allow false
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": True, "permissions": {"allow_create": False}}
        )
        self.assertTrue(setup.get("ok"), setup)
        methods = get_permission_type_functions("create")
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertEqual(response.get("status"), 403, method)
        # Check default false, allow true
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": False, "permissions": {"allow_create": True}}
        )
        self.assertTrue(setup.get("ok"), setup)
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertNotEqual(response.get("status"), 403, method)

    def global_allow_read_works_with_all_read_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Check default true, allow false
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": True, "permissions": {"allow_read": False}}
        )
        self.assertTrue(setup.get("ok"), setup)
        methods = get_permission_type_functions("read")
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertEqual(response.get("status"), 403, method)
        # Check default false, allow true
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": False, "permissions": {"allow_read": True}}
        )
        self.assertTrue(setup.get("ok"), setup)
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertNotEqual(response.get("status"), 403, method)

    def global_allow_update_works_with_all_update_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Check default true, allow false
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": True, "permissions": {"allow_update": False}}
        )
        self.assertTrue(setup.get("ok"), setup)
        methods = get_permission_type_functions("update")
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertEqual(response.get("status"), 403, method)
        # Check default false, allow true
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": False, "permissions": {"allow_update": True}}
        )
        self.assertTrue(setup.get("ok"), setup)
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertNotEqual(response.get("status"), 403, method)

    def global_allow_delete_works_with_all_delete_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Check default true, allow false
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": True, "permissions": {"allow_delete": False}}
        )
        self.assertTrue(setup.get("ok"), setup)
        methods = get_permission_type_functions("delete")
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertEqual(response.get("status"), 403, method)
        # Check default false, allow true
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": False, "permissions": {"allow_delete": True}}
        )
        self.assertTrue(setup.get("ok"), setup)
        for method in methods:
            method = dict(method)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertNotEqual(response.get("status"), 403, method)

    # Specific GROUP #

    def group_allow_create_works_with_group_create_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for group in permission_groups:
            # Check default true, allow false
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": True, "permissions": {group: {"allow_create": False}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            methods = get_permission_group_functions(group).intersection(get_permission_type_functions("create"))
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertEqual(response.get("status"), 403, method)
            # Check default false, allow true
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": False, "permissions": {group: {"allow_create": True}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertNotEqual(response.get("status"), 403, method)

    def group_allow_read_works_with_group_read_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for group in permission_groups:
            # Check default true, allow false
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": True, "permissions": {group: {"allow_read": False}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            methods = get_permission_group_functions(group).intersection(get_permission_type_functions("read"))
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertEqual(response.get("status"), 403, method)
            # Check default false, allow true
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": False, "permissions": {group: {"allow_read": True}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertNotEqual(response.get("status"), 403, method)

    def group_allow_update_works_with_group_update_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for group in permission_groups:
            # Check default true, allow false
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": True, "permissions": {group: {"allow_update": False}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            methods = get_permission_group_functions(group).intersection(get_permission_type_functions("update"))
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertEqual(response.get("status"), 403, method)
            # Check default false, allow true
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": False, "permissions": {group: {"allow_update": True}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertNotEqual(response.get("status"), 403, method)

    def group_allow_delete_works_with_group_delete_functions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for group in permission_groups:
            # Check default true, allow false
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": True, "permissions": {group: {"allow_delete": False}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            methods = get_permission_group_functions(group).intersection(get_permission_type_functions("delete"))
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertEqual(response.get("status"), 403, method)
            # Check default false, allow true
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={"version": "1", "default_allow": False, "permissions": {group: {"allow_delete": True}}},
            )
            self.assertTrue(setup.get("ok"), setup)
            for method in methods:
                method = dict(method)
                response = getattr(c, method["fn"])(*method["params"])
                self.assertNotEqual(response.get("status"), 403, method)

    # Specific permissions

    def test_individual_endpoints_allow_true_works_when_default_false(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for method in all_client_functions:
            method = dict(method)
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={
                    "version": "1",
                    "default_allow": False,
                    "permissions": {method["permission_group"]: {method["permission_name"]: {"allowed": True}}},
                },
            )
            self.assertTrue(setup.get("ok"), setup)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertNotEqual(response.get("status"), 403, method)

    def test_individual_endpoints_allow_false_works_when_default_true(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        for method in all_client_functions:
            method = dict(method)
            setup = self.client.update_api_key(
                PERMISSION_TESTING_KEY_ID,
                permissions_document={
                    "version": "1",
                    "default_allow": True,
                    "permissions": {method["permission_group"]: {method["permission_name"]: {"allowed": False}}},
                },
            )
            self.assertTrue(setup.get("ok"), setup)
            response = getattr(c, method["fn"])(*method["params"])
            self.assertEqual(response.get("status"), 403, method)

    def test_most_specific_permission_takes_priority_when_false(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Arbitrarily picked get_transaction for testing this generic behavior
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": True, "permissions": {"allow_read": False}}
        )
        self.assertTrue(setup.get("ok"), setup)
        response = c.get_transaction("blah")
        self.assertEqual(response.get("status"), 403, response)

        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID,
            permissions_document={"version": "1", "default_allow": True, "permissions": {"allow_read": True, "transactions": {"allow_read": False}}},
        )
        self.assertTrue(setup.get("ok"), setup)
        response = c.get_transaction("blah")
        self.assertEqual(response.get("status"), 403, response)

        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID,
            permissions_document={
                "version": "1",
                "default_allow": True,
                "permissions": {"allow_read": True, "transactions": {"allow_read": True, "get_transaction": {"allowed": False}}},
            },
        )
        self.assertTrue(setup.get("ok"), setup)
        response = c.get_transaction("blah")
        self.assertEqual(response.get("status"), 403, response)

    def test_most_specific_permission_takes_priority_when_true(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Arbitrarily picked get_transaction for testing this generic behavior
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID, permissions_document={"version": "1", "default_allow": False, "permissions": {"allow_read": True}}
        )
        self.assertTrue(setup.get("ok"), setup)
        response = c.get_transaction("blah")
        self.assertNotEqual(response.get("status"), 403, response)

        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID,
            permissions_document={"version": "1", "default_allow": False, "permissions": {"allow_read": False, "transactions": {"allow_read": True}}},
        )
        self.assertTrue(setup.get("ok"), setup)
        response = c.get_transaction("blah")
        self.assertNotEqual(response.get("status"), 403, response)

        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID,
            permissions_document={
                "version": "1",
                "default_allow": False,
                "permissions": {"allow_read": False, "transactions": {"allow_read": False, "get_transaction": {"allowed": True}}},
            },
        )
        self.assertTrue(setup.get("ok"), setup)
        response = c.get_transaction("blah")
        self.assertNotEqual(response.get("status"), 403, response)

    def test_custom_create_transaction_permissions(self):
        c = dragonchain_sdk.create_client(auth_key=PERMISSION_TESTING_KEY, auth_key_id=PERMISSION_TESTING_KEY_ID)
        # Test blacklist permissioning
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID,
            permissions_document={
                "version": "1",
                "default_allow": False,
                "permissions": {"transactions": {"create_transaction": {"allowed": True, "transaction_types": {"banana": False}}}},
            },
        )
        self.assertTrue(setup.get("ok"), setup)
        # Check with single not allowed transaction
        response = c.create_transaction("banana", "payload")
        self.assertEqual(response.get("status"), 403, response)
        # Check with single allowed transaction
        response = c.create_transaction("notbanana", "payload")
        self.assertNotEqual(response.get("status"), 403, response)
        # Check bulk with allowed/not allowed mix
        response = c.create_bulk_transaction(
            [{"transaction_type": "banana", "payload": "payload"}, {"transaction_type": "notbanana", "payload": "payload"}]
        )
        self.assertEqual(response.get("status"), 403, response)
        # Check bulk with only not allowed transactions
        response = c.create_bulk_transaction(
            [{"transaction_type": "banana", "payload": "payload"}, {"transaction_type": "banana", "payload": "payload"}]
        )
        self.assertEqual(response.get("status"), 403, response)
        # Check bulk with only allowed transactions
        response = c.create_bulk_transaction(
            [{"transaction_type": "notbanana", "payload": "payload"}, {"transaction_type": "notbanana", "payload": "payload"}]
        )
        self.assertNotEqual(response.get("status"), 403, response)
        # Test whitelist permissioning
        setup = self.client.update_api_key(
            PERMISSION_TESTING_KEY_ID,
            permissions_document={
                "version": "1",
                "default_allow": False,
                "permissions": {"transactions": {"create_transaction": {"allowed": False, "transaction_types": {"banana": True}}}},
            },
        )
        self.assertTrue(setup.get("ok"), setup)
        # Check with single allowed transaction
        response = c.create_transaction("banana", "payload")
        self.assertNotEqual(response.get("status"), 403, response)
        # Check with single not allowed transaction
        response = c.create_transaction("notbanana", "payload")
        self.assertEqual(response.get("status"), 403, response)
        # Check bulk with allowed/not allowed mix
        response = c.create_bulk_transaction(
            [{"transaction_type": "banana", "payload": "payload"}, {"transaction_type": "notbanana", "payload": "payload"}]
        )
        self.assertEqual(response.get("status"), 403, response)
        # Check bulk with only allowed transactions
        response = c.create_bulk_transaction(
            [{"transaction_type": "banana", "payload": "payload"}, {"transaction_type": "banana", "payload": "payload"}]
        )
        self.assertNotEqual(response.get("status"), 403, response)
        # Check bulk with only not allowed transactions
        response = c.create_bulk_transaction(
            [{"transaction_type": "notbanana", "payload": "payload"}, {"transaction_type": "notbanana", "payload": "payload"}]
        )
        self.assertEqual(response.get("status"), 403, response)

    def api_key_cleanup(self):
        for key_id in [PERMISSION_TESTING_KEY_ID]:
            try:
                self.client.delete_api_key(key_id)
            except Exception:
                pass


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestPermissioning("create_default_permissions_testing_key"))
    suite.addTest(TestPermissioning("default_permissions_denies_create_update_delete_api_keys"))
    suite.addTest(TestPermissioning("default_allow_false_forbids_all_functions"))
    suite.addTest(TestPermissioning("default_allow_true_allows_all_functions"))
    suite.addTest(TestPermissioning("global_allow_create_works_with_all_create_functions"))
    suite.addTest(TestPermissioning("global_allow_read_works_with_all_read_functions"))
    suite.addTest(TestPermissioning("global_allow_update_works_with_all_update_functions"))
    suite.addTest(TestPermissioning("global_allow_delete_works_with_all_delete_functions"))
    suite.addTest(TestPermissioning("group_allow_create_works_with_group_create_functions"))
    suite.addTest(TestPermissioning("group_allow_read_works_with_group_read_functions"))
    suite.addTest(TestPermissioning("group_allow_update_works_with_group_update_functions"))
    suite.addTest(TestPermissioning("group_allow_delete_works_with_group_delete_functions"))
    suite.addTest(TestPermissioning("test_individual_endpoints_allow_true_works_when_default_false"))
    suite.addTest(TestPermissioning("test_individual_endpoints_allow_false_works_when_default_true"))
    suite.addTest(TestPermissioning("test_most_specific_permission_takes_priority_when_false"))
    suite.addTest(TestPermissioning("test_most_specific_permission_takes_priority_when_true"))
    suite.addTest(TestPermissioning("test_custom_create_transaction_permissions"))
    suite.addTest(TestPermissioning("api_key_cleanup"))
    return suite


if __name__ == "__main__":
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite())
    sys.exit(0 if result.wasSuccessful() else 1)
