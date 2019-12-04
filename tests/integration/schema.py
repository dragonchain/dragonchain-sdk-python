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

_uuidv4_regex = "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
_digits_only_string_regex = "^[0-9]+$"
_ethereum_address_regex = "^0x[a-fA-F0-9]{40}$"

smart_contract_logs_schema = {
    "type": "object",
    "properties": {
        "logs": {
            "type": "array",
            "items": {
                "properties": {
                    "name": {"type": "string"},
                    "instance": {"type": "string"},
                    "timestamp": {"type": "string"},
                    "text": {"type": "string"},
                },
                "additionalProperties": False,
                "required": ["name", "instance", "timestamp", "text"],
            },
        }
    },
    "required": ["logs"],
    "additionalProperties": False,
}

list_transaction_type_schema = {
    "type": "object",
    "properties": {
        "transaction_types": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "txn_type": {"type": "string"},
                    "custom_indexes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field_name": {"type": "string"},
                                "path": {"type": "string"},
                                "type": {"type": "string"},
                                "options": {"type": "object"},
                            },
                            "required": ["field_name", "path", "type"],
                            "additionalProperties": False,
                        },
                    },
                    "contract_id": {"type": "string"},
                    "active_since_block": {"type": "string"},
                },
                "required": ["version", "txn_type", "custom_indexes", "contract_id", "active_since_block"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["transaction_types"],
    "additionalProperties": False,
}

create_transaction_response_schema = {"type": "object", "properties": {"transaction_id": {"type": "string"}}}

permissions_document_schema = {
    "type": "object",
    "properties": {"version": {"type": "string", "enum": ["1"]}, "default_allow": {"type": "boolean"}, "permissions": {"type": "object"}},
    "required": ["version", "default_allow", "permissions"],
    "additionalProperties": False,
}

api_key_create_schema = {
    "type": "object",
    "properties": {
        "key": {"type": "string"},
        "id": {"type": "string"},
        "registration_time": {"type": "integer"},
        "nickname": {"type": "string"},
        "root": {"type": "boolean"},
        "permissions_document": permissions_document_schema,
    },
    "required": ["key", "id", "registration_time", "nickname", "root", "permissions_document"],
    "additionalProperties": False,
}

api_key_generic_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "registration_time": {"type": "integer"},
        "nickname": {"type": "string"},
        "root": {"type": "boolean"},
        "permissions_document": permissions_document_schema,
    },
    "required": ["id", "registration_time", "nickname", "root", "permissions_document"],
    "additionalProperties": False,
}

api_key_list_schema = {
    "type": "object",
    "properties": {"keys": {"type": "array", "items": api_key_generic_schema}},
    "required": ["keys"],
    "additionalProperties": False,
}

get_status_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "scheme": {"type": "string", "enum": ["trust", "work"]},
        "encryptionAlgo": {"type": "string", "enum": ["secp256k1"]},
        "hashAlgo": {"type": "string", "enum": ["blake2b"]},
        "id": {"type": "string"},
        "level": {"type": "integer", "minimum": 1, "maximum": 5},
        "url": {"type": "string"},
    },
    "required": ["version", "scheme", "encryptionAlgo", "hashAlgo", "id", "level", "url"],
    "additionalProperties": False,
}

get_blockchain_addresses_schema = {
    "type": "object",
    "properties": {
        "eth_mainnet": {"type": "string", "pattern": _ethereum_address_regex},
        "eth_ropsten": {"type": "string", "pattern": _ethereum_address_regex},
        "etc_mainnet": {"type": "string", "pattern": _ethereum_address_regex},
        "etc_morden": {"type": "string", "pattern": _ethereum_address_regex},
        "btc_mainnet": {"type": "string"},
        "btc_testnet3": {"type": "string"},
    },
    "required": ["eth_mainnet", "eth_ropsten", "etc_mainnet", "etc_morden", "btc_mainnet", "btc_testnet3"],
    "additionalProperties": False,
}

created_ethereum_transaction_schema = {
    "type": "object",
    "properties": {"signed": {"type": "string", "pattern": "^0x[0-9a-fA-f]+$"}},
    "required": ["signed"],
    "additionalProperties": False,
}

created_bitcoin_transaction_schema = {
    "type": "object",
    "properties": {"signed": {"type": "string", "pattern": "^[0-9a-fA-f]+$"}},
    "required": ["signed"],
    "additionalProperties": False,
}

created_binance_transaction_schema = {
    "type": "object",
    "properties": {"signed": {"type": "string", "pattern": "^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{4})$"}},
    "required": ["signed"],
    "additionalProperties": False,
}

create_transaction_schema = {
    "type": "object",
    "properties": {"transaction_id": {"type": "string", "pattern": _uuidv4_regex}},
    "required": ["transaction_id"],
    "additionalProperties": False,
}

ethereum_interchain_at_rest_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "enum": ["1"]},
        "blockchain": {"type": "string", "enum": ["ethereum"]},
        "name": {"type": "string"},
        "rpc_address": {"type": "string"},
        "chain_id": {"type": "integer"},
        "address": {"type": "string", "pattern": _ethereum_address_regex},
    },
    "required": ["version", "blockchain", "name", "rpc_address", "chain_id", "address"],
    "additionalProperties": False,
}

ethereum_interchain_list_schema = {
    "type": "object",
    "properties": {"interchains": {"type": "array", "items": ethereum_interchain_at_rest_schema}},
    "required": ["interchains"],
    "additionalProperties": False,
}

bitcoin_interchain_at_rest_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "enum": ["1"]},
        "blockchain": {"type": "string", "enum": ["bitcoin"]},
        "name": {"type": "string"},
        "rpc_address": {"type": "string"},
        "testnet": {"type": "boolean"},
        "address": {"type": "string"},
    },
    "required": ["version", "blockchain", "name", "rpc_address", "testnet", "address"],
    "additionalProperties": False,
}

bitcoin_interchain_list_schema = {
    "type": "object",
    "properties": {"interchains": {"type": "array", "items": bitcoin_interchain_at_rest_schema}},
    "required": ["interchains"],
    "additionalProperties": False,
}

binance_interchain_at_rest_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "enum": ["1"]},
        "blockchain": {"type": "string", "enum": ["binance"]},
        "testnet": {"type": "boolean"},
        "name": {"type": "string"},
        "node_url": {"type": "string"},
        "rpc_port": {"type": "integer"},
        "api_port": {"type": "integer"},
        "address": {"type": "string"},
    },
    "required": ["version", "blockchain", "testnet", "name", "node_url", "rpc_port", "api_port", "address"],
    "additionalProperties": False,
}

binance_interchain_list_schema = {
    "type": "object",
    "properties": {"interchains": {"type": "array", "items": binance_interchain_at_rest_schema}},
    "required": ["interchains"],
    "additionalProperties": False,
}

bulk_create_transaction_schema = {
    "type": "object",
    "properties": {
        "201": {"type": "array", "items": {"type": "string", "pattern": _uuidv4_regex}},
        "400": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "version": {"type": "string"},
                    "txn_type": {"type": "string"},
                    "payload": {"type": ["object", "string"]},
                    "tag": {"type": "string"},
                },
                "required": ["txn_type", "payload"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["201", "400"],
    "additionalProperties": False,
}

get_transaction_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "enum": ["2"]},
        "dcrn": {"type": "string", "enum": ["Transaction::L1::FullTransaction"]},
        "header": {
            "type": "object",
            "properties": {
                "txn_type": {"type": "string"},
                "dc_id": {"type": "string"},
                "txn_id": {"type": "string", "pattern": _uuidv4_regex},
                "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                "timestamp": {"type": "string", "pattern": _digits_only_string_regex},
                "tag": {"type": "string"},
                "invoker": {"type": "string"},
            },
            "required": ["txn_type", "dc_id", "txn_id", "block_id", "timestamp", "tag", "invoker"],
            "additionalProperties": False,
        },
        "payload": {"type": ["string", "object"]},
        "proof": {
            "type": "object",
            "properties": {"full": {"type": "string"}, "stripped": {"type": "string"}},
            "required": ["full", "stripped"],
            "additionalProperties": False,
        },
    },
    "required": ["version", "dcrn", "header", "payload", "proof"],
    "additionalProperties": False,
}

query_transaction_schema = {
    "type": "object",
    "properties": {"total": {"type": "integer"}, "results": {"type": "array", "items": get_transaction_schema}},
    "required": ["total", "results"],
    "additionalProperties": False,
}

get_block_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "enum": ["1"]},
        "dcrn": {"type": "string", "enum": ["Block::L1::AtRest"]},
        "header": {
            "type": "object",
            "properties": {
                "dc_id": {"type": "string"},
                "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                "level": {"type": "integer", "minimum": 1, "maximum": 5},
                "timestamp": {"type": "string", "pattern": _digits_only_string_regex},
                "prev_id": {"type": "string"},
                "prev_proof": {"type": "string"},
            },
            "required": ["dc_id", "block_id", "level", "timestamp", "prev_id", "prev_proof"],
            "additionalProperties": False,
        },
        "transactions": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "proof": {
            "type": "object",
            "properties": {"scheme": {"type": "string", "enum": ["trust", "work"]}, "proof": {"type": "string"}, "nonce": {"type": "integer"}},
            "required": ["scheme", "proof"],
            "additionalProperties": False,
        },
    },
    "required": ["version", "dcrn", "header", "transactions", "proof"],
    "additionalProperties": False,
}

query_block_schema = {
    "type": "object",
    "properties": {"total": {"type": "integer"}, "results": {"type": "array", "items": get_block_schema}},
    "required": ["total", "results"],
    "additionalProperties": False,
}

query_ids_only = {
    "type": "object",
    "properties": {"total": {"type": "integer"}, "results": {"type": "array", "items": {"type": "string"}}},
    "required": ["total", "results"],
    "additionalProperties": False,
}

smart_contract_at_rest_schema = {
    "type": "object",
    "properties": {
        "version": {"type": "string", "enum": ["1"]},
        "dcrn": {"type": "string", "enum": ["SmartContract::L1::AtRest"]},
        "txn_type": {"type": "string"},
        "id": {"type": "string", "pattern": _uuidv4_regex},
        "status": {
            "type": "object",
            "properties": {"state": {"type": "string"}, "msg": {"type": "string"}, "timestamp": {"type": "string"}},
            "required": ["state", "msg", "timestamp"],
            "additionalProperties": False,
        },
        "image": {"type": "string"},
        "auth_key_id": {"type": ["string", "null"]},
        "image_digest": {"type": ["string", "null"]},
        "cmd": {"type": "string"},
        "args": {"type": "array", "items": {"type": "string"}},
        "env": {"type": ["object", "null"], "additionalProperties": {"type": "string"}},
        "existing_secrets": {"type": ["array", "null"], "items": {"type": "string"}},
        "cron": {"type": ["string", "null"]},
        "seconds": {"type": ["integer", "null"]},
        "execution_order": {"type": "string", "enum": ["serial", "parallel"]},
    },
    "required": [
        "version",
        "dcrn",
        "txn_type",
        "id",
        "status",
        "image",
        "auth_key_id",
        "image_digest",
        "cmd",
        "args",
        "env",
        "existing_secrets",
        "cron",
        "seconds",
        "execution_order",
    ],
    "additionalProperties": False,
}

smart_contracts_list_schema = {
    "type": "object",
    "properties": {"smart_contracts": {"type": "array", "items": smart_contract_at_rest_schema}},
    "required": ["smart_contracts"],
    "additionalProperties": False,
}

l2_verifications_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "version": {"type": "string", "enum": ["1"]},
            "dcrn": {"type": "string", "enum": ["Block::L2::AtRest"]},
            "header": {
                "type": "object",
                "properties": {
                    "dc_id": {"type": "string"},
                    "current_ddss": {"type": ["string", "null"]},
                    "level": {"type": "integer", "enum": [2]},
                    "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "timestamp": {"type": "string", "pattern": _digits_only_string_regex},
                    "prev_proof": {"type": "string"},
                },
                "required": ["dc_id", "current_ddss", "level", "block_id", "timestamp", "prev_proof"],
                "additionalProperties": False,
            },
            "validation": {
                "type": "object",
                "properties": {
                    "dc_id": {"type": "string"},
                    "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "stripped_proof": {"type": "string"},
                    "transactions": {"type": "string"},
                },
                "required": ["dc_id", "block_id", "stripped_proof", "transactions"],
                "additionalProperties": False,
            },
            "proof": {
                "type": "object",
                "properties": {"scheme": {"type": "string", "enum": ["trust", "work"]}, "proof": {"type": "string"}, "nonce": {"type": "integer"}},
                "required": ["scheme", "proof"],
                "additionalProperties": False,
            },
        },
        "required": ["version", "dcrn", "validation", "proof"],
        "additionalProperties": False,
    },
}

l3_verifications_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "version": {"type": "string", "enum": ["1", "2"]},
            "dcrn": {"type": "string", "enum": ["Block::L3::AtRest"]},
            "header": {
                "type": "object",
                "properties": {
                    "dc_id": {"type": "string"},
                    "current_ddss": {"type": ["string", "null"]},
                    "level": {"type": "integer", "enum": [3]},
                    "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "timestamp": {"type": "string", "pattern": _digits_only_string_regex},
                    "prev_proof": {"type": "string"},
                },
                "required": ["dc_id", "current_ddss", "level", "block_id", "timestamp", "prev_proof"],
                "additionalProperties": False,
            },
            "l2-validations": {
                "type": "object",
                "properties": {
                    "l1_dc_id": {"type": "string"},
                    "l1_block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "l1_proof": {"type": "string"},
                    "ddss": {"type": "string", "pattern": _digits_only_string_regex},
                    "count": {"type": "string", "pattern": _digits_only_string_regex},
                    "regions": {"type": "array", "items": {"type": "string"}},
                    "clouds": {"type": "array", "items": {"type": "string"}},
                    "l2_proofs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "dc_id": {"type": "string"},
                                "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                                "proof": {"type": "string"},
                            },
                            "required": ["dc_id", "block_id", "proof"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["l1_dc_id", "l1_block_id", "l1_proof", "ddss", "count", "regions", "clouds", "l2_proofs"],
                "additionalProperties": False,
            },
            "proof": {
                "type": "object",
                "properties": {"scheme": {"type": "string", "enum": ["trust", "work"]}, "proof": {"type": "string"}, "nonce": {"type": "integer"}},
                "required": ["scheme", "proof"],
                "additionalProperties": False,
            },
        },
        "required": ["version", "dcrn", "l2-validations", "proof"],
        "additionalProperties": False,
    },
}

l4_verifications_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "version": {"type": "string", "enum": ["1", "2"]},
            "dcrn": {"type": "string", "enum": ["Block::L4::AtRest"]},
            "header": {
                "type": "object",
                "properties": {
                    "dc_id": {"type": "string"},
                    "current_ddss": {"type": ["string", "null"]},
                    "level": {"type": "integer", "enum": [4]},
                    "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "timestamp": {"type": "string", "pattern": _digits_only_string_regex},
                    "prev_proof": {"type": "string"},
                    "l1_dc_id": {"type": "string"},
                    "l1_block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "l1_proof": {"type": "string"},
                },
                "required": ["dc_id", "current_ddss", "level", "block_id", "timestamp", "prev_proof", "l1_dc_id", "l1_block_id", "l1_proof"],
                "additionalProperties": False,
            },
            "l3-validations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "l3_dc_id": {"type": "string"},
                        "l3_block_id": {"type": "string", "pattern": _digits_only_string_regex},
                        "l3_proof": {"type": "string"},
                        "valid": {"type": "boolean"},
                    },
                    "required": ["l3_dc_id", "l3_block_id", "l3_proof", "valid"],
                    "additionalProperties": False,
                },
            },
            "proof": {
                "type": "object",
                "properties": {"scheme": {"type": "string", "enum": ["trust", "work"]}, "proof": {"type": "string"}, "nonce": {"type": "integer"}},
                "required": ["scheme", "proof"],
                "additionalProperties": False,
            },
        },
        "required": ["version", "dcrn", "l3-validations", "proof"],
        "additionalProperties": False,
    },
}

l5_verifications_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "version": {"type": "string", "enum": ["1"]},
            "dcrn": {"type": "string", "enum": ["Block::L5::AtRest"]},
            "header": {
                "type": "object",
                "properties": {
                    "dc_id": {"type": "string"},
                    "current_ddss": {"type": ["string", "null"]},
                    "level": {"type": "integer", "enum": [5]},
                    "block_id": {"type": "string", "pattern": _digits_only_string_regex},
                    "timestamp": {"type": "string", "pattern": _digits_only_string_regex},
                    "prev_proof": {"type": "string"},
                },
                "required": ["dc_id", "current_ddss", "level", "block_id", "timestamp", "prev_proof"],
                "additionalProperties": False,
            },
            "l4-blocks": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "proof": {
                "type": "object",
                "properties": {
                    "scheme": {"type": "string", "enum": ["trust"]},
                    "network": {"type": "string"},
                    "proof": {"type": "string"},
                    "block_last_sent_at": {"type": "integer"},
                    "transaction_hash": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["scheme", "proof", "network", "block_last_sent_at", "transaction_hash"],
                "additionalProperties": False,
            },
        },
        "required": ["version", "dcrn", "l4-blocks", "proof"],
        "additionalProperties": False,
    },
}

all_verifications_schema = {
    "type": "object",
    "properties": {"2": l2_verifications_schema, "3": l3_verifications_schema, "4": l4_verifications_schema, "5": l5_verifications_schema},
    "required": ["2", "3", "4", "5"],
    "additionalProperties": False,
}

pending_verifications_schema = {
    "type": "object",
    "properties": {
        "2": {"type": "array", "items": {"type": "string"}},
        "3": {"type": "array", "items": {"type": "string"}},
        "4": {"type": "array", "items": {"type": "string"}},
        "5": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["2", "3", "4", "5"],
    "additionalProperties": False,
}
