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

import os
import logging
from typing import cast, Any, Dict, Optional, Union, List, Iterable, TYPE_CHECKING

from dragonchain_sdk import request
from dragonchain_sdk import credentials

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from dragonchain_sdk.types import request_response, custom_index_fields_type  # noqa: F401 used by typing


class Client(object):
    def __init__(
        self,
        dragonchain_id: Optional[str],
        auth_key_id: Optional[str],
        auth_key: Optional[str],
        endpoint: Optional[str],
        verify: bool,
        algorithm: str,
    ):
        self.credentials = credentials.Credentials(dragonchain_id, auth_key, auth_key_id, algorithm)
        self.request = request.Request(self.credentials, endpoint, verify)
        logger.debug("Client finished initialization")

    def get_smart_contract_secret(self, secret_name: str) -> str:
        """Gets secrets for smart contracts

        Args:
            secret_name (str): name of the secret to retrieve

        Raises:
            TypeError: with bad parameter types
            RuntimeError: if not running in a smart contract environment

        Returns:
            String of the value of the specified secret
        """
        if not isinstance(secret_name, str):
            raise TypeError('Parameter "secret_name" must be of type str.')
        if not os.environ.get("SMART_CONTRACT_ID"):
            raise RuntimeError('Missing "SMART_CONTRACT_ID" from environment')
        path = os.path.join(
            os.path.abspath(os.sep), "var", "openfaas", "secrets", "sc-{}-{}".format(os.environ.get("SMART_CONTRACT_ID"), secret_name)
        )
        return open(path, "r").read()

    def get_status(self) -> "request_response":
        """Get the status from a chain

        Returns:
            Returns the status of a Dragonchain
        """
        return self.request.get("/v1/status")

    def list_smart_contracts(self) -> "request_response":
        """Get all smart contracts on a chain

        Returns:
            A list of all the smart contracts on the chain
        """
        return self.request.get("/v1/contract")

    def get_smart_contract(self, smart_contract_id: Optional[str] = None, transaction_type: Optional[str] = None) -> "request_response":
        """Perform a query on a chain's smart contracts

        Args:
            smart_contract_id (str, exclusive): Id of the contract to get
            transaction_type (str, exclusive): Name of the Transaction Type bound to this contract. Usually the contract "name"

        Raises:
            TypeError: with bad parameter types

        Returns:
            The contract returned from the request
        """
        if smart_contract_id is not None and not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        if transaction_type is not None and not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if smart_contract_id and transaction_type:
            raise TypeError('Only one of "smart_contract_id" and "transaction_type" can be specified')
        if smart_contract_id:
            return self.request.get("/v1/contract/{}".format(smart_contract_id))
        elif transaction_type:
            return self.request.get("/v1/contract/txn_type/{}".format(transaction_type))
        else:
            raise TypeError('At least one of "smart_contract_id" or "transaction_type" must be specified')

    def create_smart_contract(  # noqa: C901
        self,
        transaction_type: str,
        image: str,
        cmd: str,
        args: Optional[List[str]] = None,
        execution_order: str = "parallel",
        environment_variables: Optional[Dict[str, str]] = None,
        secrets: Optional[Dict[str, str]] = None,
        schedule_interval_in_seconds: Optional[int] = None,
        cron_expression: Optional[str] = None,
        registry_credentials: Optional[str] = None,
        custom_index_fields: Optional[Iterable["custom_index_fields_type"]] = None,
    ) -> "request_response":
        """Post a contract to a chain

        Args:
            transaction_type (str): transaction_type of the contract to create
            image (str): Docker image containing the smart contract logic
            cmd (str): Entrypoint command to run in the docker container
            execution_order (optional, str): Order of execution. Valid values are 'serial' or 'parallel'. default: 'parallel'
            args (optional, list): List of arguments to the cmd field
            environment_variables (optional, dict): dict mapping of environment variables for your contract runtime
            secrets (optional, dict): dict mapping of secrets for your contract runtime
            schedule_interval_in_seconds (optional, int): The seconds of scheduled execution in seconds. Must not be set if cron_expression is set
            cron_expression (optional, str): The rate of scheduled execution specified as a cron. Must not be set if schedule_interval_in_seconds is set
            registry_credentials (optional, str): basic-auth for pulling docker images, base64 encoded (e.g. username:password)
            custom_index_fields (optional): Custom index fields to assign to the transaction type for this smart contract. See create_transaction_type for details

        Raises:
            TypeError: with bad parameter types

        Returns:
            Success or failure object
        """
        if custom_index_fields is None:
            custom_index_fields = []
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if not isinstance(image, str):
            raise TypeError('Parameter "image" must be of type str.')
        if not isinstance(cmd, str):
            raise TypeError('Parameter "cmd" must be of type str.')
        if args is not None and not isinstance(args, list):
            raise TypeError('Parameter "args" must be of type list.')
        if not isinstance(execution_order, str):
            raise TypeError('Parameter "execution_order" must be of type str.')
        if execution_order is not None and execution_order not in ["parallel", "serial"]:
            raise ValueError('Parameter "execution_order" must be either "serial" or "parallel".')
        if environment_variables is not None and not isinstance(environment_variables, dict):
            raise TypeError('Parameter "environment_variables" must be of type dict.')
        if secrets is not None and not isinstance(secrets, dict):
            raise TypeError('Parameter "secrets" must be of type dict.')
        if schedule_interval_in_seconds is not None and cron_expression is not None:
            raise ValueError('Parameter "schedule_interval_in_seconds" and "cron_expression" can not both be set')
        if schedule_interval_in_seconds is not None and not isinstance(schedule_interval_in_seconds, int):
            raise TypeError('Parameter "schedule_interval_in_seconds" must be of type int.')
        if cron_expression is not None and not isinstance(cron_expression, str):
            raise TypeError('Parameter "cron_expression" must be of type str.')
        if registry_credentials is not None and not isinstance(registry_credentials, str):
            raise TypeError('Parameter "registry_credentials" must be of type str.')
        if not isinstance(custom_index_fields, list):
            raise TypeError('Parameter "custom_index_fields" must be of type list.')

        body = cast(Dict[str, Any], {"version": "3", "txn_type": transaction_type, "image": image, "cmd": cmd, "execution_order": execution_order})
        if environment_variables:
            body["env"] = environment_variables
        if args:
            body["args"] = args
        if secrets:
            body["secrets"] = secrets
        if schedule_interval_in_seconds:
            body["seconds"] = schedule_interval_in_seconds
        if cron_expression:
            body["cron"] = cron_expression
        if registry_credentials:
            body["auth"] = registry_credentials
        if custom_index_fields:
            body["custom_indexes"] = _validate_and_build_custom_index_fields_array(custom_index_fields)
        return self.request.post("/v1/contract", body)

    def update_smart_contract(  # noqa: C901
        self,
        smart_contract_id: str,
        image: Optional[str] = None,
        cmd: Optional[str] = None,
        args: Optional[List[str]] = None,
        execution_order: Optional[str] = None,
        enabled: Optional[bool] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        secrets: Optional[Dict[str, str]] = None,
        schedule_interval_in_seconds: Optional[int] = None,
        cron_expression: Optional[str] = None,
        registry_credentials: Optional[str] = None,
    ) -> "request_response":
        """Update an existing smart contract. The smart_contract_id and at least one optional parameter must be supplied.

        Args:
            smart_contract_id (str): id of the contract to update
            image (str): Docker image containing the smart contract logic
            cmd (str): Entrypoint command to run in the docker container
            execution_order (str): Order of execution. Valid values are 'serial' or 'parallel'
            enabled (bool, optional): Enabled status of contract
            args (list, optional): List of arguments to the cmd field
            environment_variables (dict, optional): dict mapping of environment variables for your contract runtime
            secrets (dict, optional): dict mapping of secrets for your contract runtime
            schedule_interval_in_seconds (int, optional): The seconds of scheduled execution in seconds
            cron_expression (str, optional): The rate of scheduled execution specified as a cron
            registry_credentials (str, optional): basic-auth for pulling docker images, base64 encoded (e.g. username:password)

        Raises:
            TypeError: with bad parameter types

        Returns:
            Success or failure object
        """
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        if image is not None and not isinstance(image, str):
            raise TypeError('Parameter "image" must be of type str.')
        if cmd is not None and not isinstance(cmd, str):
            raise TypeError('Parameter "cmd" must be of type str.')
        if execution_order is not None and not isinstance(execution_order, str):
            raise TypeError('Parameter "execution_order" must be of type str.')
        if execution_order is not None and execution_order not in ["parallel", "serial"]:
            raise ValueError('Parameter "execution_order" must be either "serial" or "parallel".')
        if enabled is not None and not isinstance(enabled, bool):
            raise TypeError('Parameter "enabled" must be of type bool.')
        if args is not None and not isinstance(args, list):
            raise TypeError('Parameter "args" must be of type list.')
        if environment_variables is not None and not isinstance(environment_variables, dict):
            raise TypeError('Parameter "env" must be of type dict.')
        if secrets is not None and not isinstance(secrets, dict):
            raise TypeError('Parameter "secrets" must be of type dict.')
        if schedule_interval_in_seconds is not None and not isinstance(schedule_interval_in_seconds, int):
            raise TypeError('Parameter "schedule_interval_in_seconds" must be of type int.')
        if cron_expression is not None and not isinstance(cron_expression, str):
            raise TypeError('Parameter "cron_expression" must be of type str.')
        if registry_credentials is not None and not isinstance(registry_credentials, str):
            raise TypeError('Parameter "registry_credentials" must be of type str.')

        body = cast(Dict[str, Any], {"version": "3"})
        if image:
            body["image"] = image
        if cmd:
            body["cmd"] = cmd
        if execution_order:
            body["execution_order"] = execution_order
        if enabled is False:
            body["desired_state"] = "inactive"
        if enabled is True:
            body["desired_state"] = "active"
        if args:
            body["args"] = args
        if environment_variables:
            body["env"] = environment_variables
        if secrets:
            body["secrets"] = secrets
        if schedule_interval_in_seconds:
            body["seconds"] = schedule_interval_in_seconds
        if cron_expression:
            body["cron"] = cron_expression
        if registry_credentials:
            body["auth"] = registry_credentials

        return self.request.put("/v1/contract/{}".format(smart_contract_id), body)

    def delete_smart_contract(self, smart_contract_id: str) -> "request_response":
        """Delete an existing contract

        Args:
            smart_contract_id (str): Transaction type of the contract to delete

        Raises:
            TypeError: with bad parameter types

        Returns:
            The results of the delete request
        """
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "state" must be of type str.')
        return self.request.delete("/v1/contract/{}".format(smart_contract_id))

    def query_transactions(
        self,
        transaction_type: str,
        redisearch_query: str,
        verbatim: bool = False,
        offset: int = 0,
        limit: int = 10,
        sort_by: str = "",
        sort_ascending: bool = True,
        ids_only: bool = False,
    ) -> "request_response":
        """Perform a query on a chain's transactions

        Args:
            transaction_type (str): The single transaction type to query
            redisearch_query (str): Redisearch query syntax string to search with
            verbatim (bool, optional): Whether or not to use redisearch's VERBATIM (if true, no stemming occurs on the query)
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)
            sort_by (str, optional): The name of the field to sort by
            sort_ascending (bool, optional): If sort_by is set, this sorts the results by field in ascending order (descending if false)
            ids_only (bool, optional): If true, rather than an array of transaction objects, it will return an array of transaction id strings instead

        Returns:
            The results of the query
        """
        if not transaction_type or not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if not redisearch_query or not isinstance(redisearch_query, str):
            raise TypeError('Parameter "redisearch_query" must be of type str.')
        if not isinstance(verbatim, bool):
            raise TypeError('Parameter "verbatim" must be of type bool.')
        if not isinstance(offset, int):
            raise TypeError('Parameter "offset" must be of type int.')
        if not isinstance(limit, int):
            raise TypeError('Parameter "limit" must be of type int.')
        if not isinstance(sort_by, str):
            raise TypeError('Parameter "sort_by" must be of type str.')
        if not isinstance(sort_ascending, bool):
            raise TypeError('Parameter "sort_ascending" must be of type bool.')
        if not isinstance(ids_only, bool):
            raise TypeError('Parameter "ids_only" must be of type bool.')
        query_dict = cast(
            Dict[str, Any],
            {
                "transaction_type": transaction_type,
                "q": redisearch_query,
                "verbatim": verbatim,
                "offset": offset,
                "limit": limit,
                "id_only": ids_only,
            },
        )
        if sort_by:
            query_dict["sort_by"] = sort_by
            query_dict["sort_asc"] = sort_ascending
        return self.request.get("/v1/transaction{}".format(self.request.generate_query_string(query_dict)))

    def get_transaction(self, transaction_id: str) -> "request_response":
        """Get a specific transaction by id

        Args:
            transaction_id (str): ID of the transaction to get (should be a UUID)

        Raises:
            TypeError: with bad parameter types

        Returns:
            The transaction searched for
        """
        if not isinstance(transaction_id, str):
            raise TypeError('Paramter "transaction_id" must be of type str.')
        return self.request.get("/v1/transaction/{}".format(transaction_id))

    def create_transaction(
        self, transaction_type: str, payload: Union[str, Dict[Any, Any]], tag: Optional[str] = None, callback_url: Optional[str] = None
    ) -> "request_response":
        """Post a transaction to a chain

        Args:
            transaction_type (str): Type of transaction
            payload (dict or string): The payload of the transaction
            tag (str, optional): A tag string to search on

        Returns:
            Transaction ID on success
        """
        headers = {}
        if callback_url:
            headers["X-Callback-Url"] = callback_url

        return self.request.post("/v1/transaction", _build_transaction_dict(transaction_type, payload, tag), additional_headers=headers)

    def create_bulk_transaction(self, transaction_list: List[Dict[Any, Any]]) -> "request_response":
        """Post many transactions to a chain at once, over a single connnection

        Args:
            transaction_list (list): List of transaction dictionaries. Schema: ``{'transaction_type': 'str', 'payload': 'str or dict', 'tag': 'str (optional)'}``

        Raises:
            TypeError: with bad parameter types

        Returns:
            List of succeeded transaction id's and list of failed transactions
        """
        if not isinstance(transaction_list, list):
            raise TypeError('Parameter "transaction_list" must be of type list.')

        post_data = []

        for transaction in transaction_list:
            if not isinstance(transaction, dict):
                raise TypeError('All items in parameter "transaction_list" must be of type dict.')
            post_data.append(
                _build_transaction_dict(transaction.get("transaction_type") or "", transaction.get("payload") or "", transaction.get("tag") or "")
            )

        return self.request.post("/v1/transaction_bulk", post_data)

    def query_blocks(
        self, redisearch_query: str, offset: int = 0, limit: int = 10, sort_by: str = "", sort_ascending: bool = True, ids_only: bool = False
    ) -> "request_response":
        """Perform a query on a chain's blocks

        Args:
            redisearch_query (str): Redisearch query syntax string to search with
            offset (int, optional): Pagination offset of query (default 0)
            limit (int, optional): Pagination limit (default 10)
            sort_by (str, optional): The name of the field to sort by
            sort_ascending (bool, optional): If sort_by is set, this sorts the results by field in ascending order (descending if false)
            ids_only (bool, optional): If true, rather than an array of block objects, it will return an array of block id strings instead

        Returns:
            The results of the query
        """
        if not redisearch_query or not isinstance(redisearch_query, str):
            raise TypeError('Parameter "redisearch_query" must be of type str.')
        if not isinstance(offset, int):
            raise TypeError('Parameter "offset" must be of type int.')
        if not isinstance(limit, int):
            raise TypeError('Parameter "limit" must be of type int.')
        if not isinstance(sort_by, str):
            raise TypeError('Parameter "sort_by" must be of type str.')
        if not isinstance(sort_ascending, bool):
            raise TypeError('Parameter "sort_ascending" must be of type bool.')
        if not isinstance(ids_only, bool):
            raise TypeError('Parameter "ids_only" must be of type bool.')
        query_dict = cast(Dict[str, Any], {"q": redisearch_query, "offset": offset, "limit": limit, "id_only": ids_only})
        if sort_by:
            query_dict["sort_by"] = sort_by
            query_dict["sort_asc"] = sort_ascending
        return self.request.get("/v1/block{}".format(self.request.generate_query_string(query_dict)))

    def get_block(self, block_id: str) -> "request_response":
        """Get a specific block by id

        Args:
            block_id (str): ID of the block to get

        Raises:
            TypeError: with bad parameter types

        Returns:
            The block which was retrieved from the chain
        """
        if not isinstance(block_id, str):
            raise TypeError('Parameter "block_id" must be of type str.')
        return self.request.get("/v1/block/{}".format(block_id))

    def get_pending_verifications(self, block_id: str) -> "request_response":
        """Get chain ids for pending and/or scheduled verifications

        Args:
            block_id (str): ID of the block to get pending verifications for

        Returns:
            Chain ids at each level (2-5) for verifications that are scheduled or sent, but not receieved
        """
        if not isinstance(block_id, str):
            raise TypeError('Parameter "block_id" must be of type str.')
        return self.request.get("/v1/verifications/pending/{}".format(block_id))

    def get_verifications(self, block_id: str, level: Optional[int] = None) -> "request_response":
        """Get higher level block verifications by level 1 block id

        Args:
            block_id (str): ID of the block to get verifications for
            level (int, optional): Level of verifications to get (valid values are 2, 3, 4 and 5)

        Raises:
            TypeError: with bad parameter types

        Returns:
            Higher level block verifications
        """
        if not isinstance(block_id, str):
            raise TypeError('Parameter "block_id" must be of type str.')
        if level is not None:
            if not isinstance(level, int):
                raise TypeError('Parameter "level" must be of int.')
            if level not in [2, 3, 4, 5]:
                raise ValueError('Parameter "level" must be between 2 and 5 inclusive.')
            return self.request.get("/v1/verifications/{}?level={}".format(block_id, level))
        return self.request.get("/v1/verifications/{}".format(block_id))

    def get_api_key(self, key_id: str) -> "request_response":
        """Get information about an HMAC API key

        Args:
            key_id (str): The ID of the api key to retrieve data about

        Raises:
            TypeError: with bad parameter types

        Returns:
            Data about the API key
        """
        if not isinstance(key_id, str):
            raise TypeError('Parameter "key_id" must be of type str.')
        return self.request.get("/v1/api-key/{}".format(key_id))

    def list_api_keys(self) -> "request_response":
        """List of HMAC API keys

        Returns:
            A list of key IDs and their associated data
        """
        return self.request.get("/v1/api-key")

    def create_api_key(self, nickname: Optional[str] = None) -> "request_response":
        """Generate a new HMAC API key

        Returns:
            A new API key ID and key
        """
        body = {}
        if nickname:
            if not isinstance(nickname, str):
                raise TypeError('Parameter "nickname" must be of type str.')
            body.update({"nickname": nickname})
        return self.request.post("/v1/api-key", body)

    def delete_api_key(self, key_id: str) -> "request_response":
        """Delete an existing HMAC API key

        Returns:
            204 No Content on success
        """
        if not isinstance(key_id, str):
            raise TypeError('Parameter "key_id" must be of type str.')
        return self.request.delete("/v1/api-key/{}".format(key_id))

    def update_api_key(self, key_id: str, nickname: str) -> "request_response":
        """Update the nickname of an existing HMAC API key

        Returns:
            success: True
        """
        if not isinstance(key_id, str):
            raise TypeError('Parameter "key_id" must be of type str.')
        if not isinstance(nickname, str):
            raise TypeError('Parameter "nickname" must be of type str.')
        return self.request.put("/v1/api-key/{}".format(key_id), {"nickname": nickname})

    def get_smart_contract_object(self, key: str, smart_contract_id: Optional[str] = None) -> "request_response":
        """Retrieve data from the object storage of a smart contract
        Note: When ran in an actual smart contract, smart_contract_id will be pulled automatically from the environment if not explicitly provided

        Args:
            key (str): The key stored in the heap to retrieve
            smart_contract_id (str, optional): The ID of the smart contract, optional if called from within a smart contract

        Raises:
            TypeError: with bad parameter types

        Returns:
            The value of the object in the heap
        """
        if not isinstance(key, str):
            raise TypeError('Parameter "key" must be of type str.')
        if smart_contract_id is None:
            smart_contract_id = os.environ.get("SMART_CONTRACT_ID")
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        return self.request.get("/v1/get/{}/{}".format(smart_contract_id, key), parse_response=False)

    def list_smart_contract_objects(self, prefix_key: Optional[str] = None, smart_contract_id: Optional[str] = None) -> "request_response":
        """Lists all objects stored in a smart contracts heap
        Note: When ran in an actual smart contract, smart_contract_id will be pulled automatically from the environment if not explicitly provided

        Args:
            smart_contract_id (str, optional): smart_contract_id heap to list. If not provided explicitly, it must be in the SMART_CONTRACT_NAME env var
            prefix_key (str, optional): the prefix_key or "folder" from which to list objects. Must NOT contain trailing slash "/".
                                        Note: Defaults to the root of the accessable filesystem + /list/{smart_contract_id}/

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            Parsed json response from the chain
        """
        if smart_contract_id is None:
            smart_contract_id = os.environ.get("SMART_CONTRACT_ID")
        if not isinstance(smart_contract_id, str):
            raise TypeError('Parameter "smart_contract_id" must be of type str.')
        if prefix_key is not None:
            if not isinstance(prefix_key, str):
                raise TypeError('Parameter "prefix_key" must be of type str.')
            if prefix_key.endswith("/"):
                raise ValueError('Parameter "prefix_key" cannot end with /.')
            return self.request.get("/v1/list/{}/{}/".format(smart_contract_id, prefix_key))
        return self.request.get("/v1/list/{}/".format(smart_contract_id))

    def get_transaction_type(self, transaction_type: str) -> "request_response":
        """Gets information on a registered transaction type

        Args:
            transaction_type (str): transaction_type to retrieve data for

        Raises:
            TypeError: with bad parameter types

        Returns:
            parsed json response of the transaction type or None
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        return self.request.get("/v1/transaction-type/{}".format(transaction_type))

    def list_transaction_types(self) -> "request_response":
        """Lists out all registered transaction types for a chain

        Returns:
            list of registered transaction types
        """
        return self.request.get("/v1/transaction-types")

    def create_transaction_type(
        self, transaction_type: str, custom_index_fields: Optional[Iterable["custom_index_fields_type"]] = None
    ) -> "request_response":
        """Creates a new custom transaction type.

        Transaction Types can optionally link custom search index fields to your transactions for easier querying later.
        A custom_index_field is a dictionary with 'path', 'field_name', 'type', and an optional 'options' dictionary:

        path (str): the JSONPath of your transaction payload you would like to result form a search on the "key".
        field_name (str): The field for this custom extracted value to be indexed under
        type ('text', 'tag', or 'number'): The type of redisearch index to use for this field
        options: (object) The redisearch options for this field
        - no_index (bool) (all types) whether or not to index on this field, or simply make it sortable only if false
        - separator (str) (tag only) what string should be used for the tag separator
        - weight (number) (text only) The weight to give this text field when doing text queries
        - no_stem (bool) (text only) Whether or not to allow search stemming in text searches on this field
        - sortable (bool) (text and number only) Whether or not a search on the index can be sortable by this field
        See redisearch for more details on these options: https://oss.redislabs.com/redisearch/Commands.html#field_options

        Args:
            transaction_type (str): transaction_type to update
            custom_index_fields (optional): custom_index_fields to update. Ex.: [{"path":"a.b","field_name":"myField","type":"text","options":{"no_index":True}}]

        Raises:
            TypeError: with bad parameter types

        Returns:
            Parsed json with success message
        """
        if custom_index_fields is None:
            custom_index_fields = []
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        if not isinstance(custom_index_fields, list):
            raise TypeError('Parameter "custom_index_fields" must be of type list.')
        params = cast(Dict[str, Any], {"version": "2", "txn_type": transaction_type})
        if custom_index_fields:
            params["custom_indexes"] = _validate_and_build_custom_index_fields_array(custom_index_fields)
        return self.request.post("/v1/transaction-type", params)

    def delete_transaction_type(self, transaction_type: str) -> "request_response":
        """Deletes a transaction type registration

        Args:
            transaction_type (str): transaction_type to delete

        Raises:
            TypeError: with bad parameter types

        Returns:
            Parsed json with success message
        """
        if not isinstance(transaction_type, str):
            raise TypeError('Parameter "transaction_type" must be of type str.')
        return self.request.delete("/v1/transaction-type/{}".format(transaction_type))

    def create_bitcoin_interchain(
        self,
        name: str,
        testnet: Optional[bool] = None,
        private_key: Optional[str] = None,
        rpc_address: Optional[str] = None,
        rpc_authorization: Optional[str] = None,
        utxo_scan: Optional[bool] = None,
    ) -> "request_response":
        """Create (or overwrite) a bitcoin wallet/network for interchain use

        Args:
            name (str): The name to use for this network. Will overwrite if providing a name that already exists
            testnet (bool): Whether or not this is a testnet wallet/address (not required if providing private_key as WIF)
            private_key (str, optional): The base64 encoded private key, or WIF for the desired wallet. Will generate randomly if not provided
            rpc_address (str, optional): The endpoint of the bitcoin core RPC node to use (i.e. http://my-node:8332)
            rpc_authorization (str, optional): The base64-encoded username:password for the rpc node. For example, user: a pass: b would be 'YTpi' (base64("a:b"))
            utxo_scan (bool, optional): Whether or not to force a utxo-rescan for the address.
                If using a private key for an existing wallet with funds, this must be True to use its existing funds

        Raises:
            TypeError: with bad parameter values

        Returns:
            The created interchain network
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if testnet is not None and not isinstance(testnet, bool):
            raise TypeError('Parameter "testnet" must be of type bool.')
        if private_key is not None and not isinstance(private_key, str):
            raise TypeError('Parameter "private_key" must be of type str.')
        if rpc_address is not None and not isinstance(rpc_address, str):
            raise TypeError('Parameter "rpc_address" must be of type str.')
        if rpc_authorization is not None and not isinstance(rpc_authorization, str):
            raise TypeError('Parameter "rpc_authorization" must be of type str.')
        if utxo_scan is not None and not isinstance(utxo_scan, bool):
            raise TypeError('Parameter "utxo_scan" must be of type bool.')
        body = cast(Dict[str, Any], {"version": "1", "name": name})
        if testnet is not None:
            body["testnet"] = testnet
        if utxo_scan is not None:
            body["utxo_scan"] = utxo_scan
        if private_key:
            body["private_key"] = private_key
        if rpc_address:
            body["rpc_address"] = rpc_address
        if rpc_authorization:
            body["rpc_authorization"] = rpc_authorization
        return self.request.post("/v1/interchains/bitcoin", body)

    def update_bitcoin_interchain(
        self,
        name: str,
        testnet: Optional[bool] = None,
        private_key: Optional[str] = None,
        rpc_address: Optional[str] = None,
        rpc_authorization: Optional[str] = None,
        utxo_scan: Optional[bool] = None,
    ) -> "request_response":
        """Update an existing bitcoin wallet/network for interchain use. Will only update the provided fields

        Args:
            name (str): The name of the network to update
            testnet (bool): Whether or not this is a testnet wallet/address (not required if providing private_key as WIF)
            private_key (str, optional): The base64 encoded private key, or WIF for the desired wallet
            rpc_address (str, optional): The endpoint of the bitcoin core RPC node to use (i.e. http://my-node:8332)
            rpc_authorization (str, optional): The base64-encoded username:password for the rpc node. For example, user: a pass: b would be 'YTpi' (base64("a:b"))
            utxo_scan (bool, optional): Whether or not to force a utxo-rescan for the address.
                If using a new private key for an existing wallet with funds, this must be True to use its existing funds

        Raises:
            TypeError: with bad parameter values

        Returns:
            The updated bitcoin interchain network
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if testnet is not None and not isinstance(testnet, bool):
            raise TypeError('Parameter "testnet" must be of type bool.')
        if private_key is not None and not isinstance(private_key, str):
            raise TypeError('Parameter "private_key" must be of type str.')
        if rpc_address is not None and not isinstance(rpc_address, str):
            raise TypeError('Parameter "rpc_address" must be of type str.')
        if rpc_authorization is not None and not isinstance(rpc_authorization, str):
            raise TypeError('Parameter "rpc_authorization" must be of type str.')
        if utxo_scan is not None and not isinstance(utxo_scan, bool):
            raise TypeError('Parameter "utxo_scan" must be of type bool.')
        body = cast(Dict[str, Any], {"version": "1"})
        if testnet is not None:
            body["testnet"] = testnet
        if utxo_scan is not None:
            body["utxo_scan"] = utxo_scan
        if private_key:
            body["private_key"] = private_key
        if rpc_address:
            body["rpc_address"] = rpc_address
        if rpc_authorization:
            body["rpc_authorization"] = rpc_authorization
        return self.request.patch("/v1/interchains/bitcoin/{}".format(name), body)

    def sign_bitcoin_transaction(
        self,
        name: str,
        satoshis_per_byte: Optional[int] = None,
        data: Optional[str] = None,
        change_address: Optional[str] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
    ) -> "request_response":
        """Create and sign a bitcoin transaction using your chain's interchain network

        Args:
            name (str): name of the bitcoin network to use for signing
            satoshis_per_byte (int, optional): fee to pay in satoshis/byte. If not supplied, it will be estimated for you.
            data (str, optional): string to embed in the transaction as null-data output type
            change_address (str, optional): address to send change to. If not supplied, it will default to the address you are sending from
            outputs (list, optional): (list of {'to': str, 'value': float} dictionaries. Value float is in BTC)

        Raises:
            TypeError: with bad parameter types

        Returns:
            The built and signed transaction
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        transaction = _build_bitcoin_transaction_body(satoshis_per_byte=satoshis_per_byte, data=data, change_address=change_address, outputs=outputs)
        return self.request.post("/v1/interchains/bitcoin/{}/transaction".format(name), transaction)

    def create_ethereum_interchain(
        self, name: str, private_key: Optional[str] = None, rpc_address: Optional[str] = None, chain_id: Optional[int] = None
    ) -> "request_response":
        """Create (or overwrite) an ethereum wallet/network for interchain use

        Args:
            name (str): The name to use for this network. Will overwrite if providing a name that already exists
            private_key (str, optional): The base64 or hex encoded private key. Will generate randomly if not provided
            rpc_address (str, optional): The endpoint of the ethereum RPC node to use (i.e. http://my-node:8545)
            chain_id (int, optional): The ethereum chain id to use. Will automatically derive this if providing a custom rpc_address
                Without providing a custom rpc_address, Dragonchain manages and supports: 1=ETH Mainnet|3=ETH Ropsten|61=ETC Mainnet|62=ETC Morden

        Raises:
            TypeError: with bad parameters

        Returns:
            The created interchain network
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if private_key is not None and not isinstance(private_key, str):
            raise TypeError('Parameter "private_key" must be of type str.')
        if rpc_address is not None and not isinstance(rpc_address, str):
            raise TypeError('Parameter "rpc_address" must be of type str.')
        if chain_id is not None and not isinstance(chain_id, int):
            raise TypeError('Parameter "chain_id" must be of type int.')
        body = cast(Dict[str, Any], {"version": "1", "name": name})
        if private_key:
            body["private_key"] = private_key
        if rpc_address:
            body["rpc_address"] = rpc_address
        if chain_id is not None:
            body["chain_id"] = chain_id
        return self.request.post("/v1/interchains/ethereum", body)

    def update_ethereum_interchain(
        self, name: str, private_key: Optional[str] = None, rpc_address: Optional[str] = None, chain_id: Optional[int] = None
    ) -> "request_response":
        """Update an existing ethereum wallet/network for interchain use

        Args:
            name (str): The name of the network to update
            private_key (str, optional): The base64 or hex encoded private key
            rpc_address (str, optional): The endpoint of the ethereum RPC node to use (i.e. http://my-node:8545)
            chain_id (int, optional): The ethereum chain id to use. Will automatically derive this if providing a custom rpc_address
                Without providing a custom rpc_address, Dragonchain manages and supports: 1=ETH Mainnet|3=ETH Ropsten|61=ETC Mainnet|2=ETC Morden

        Raises:
            TypeError: with bad parameters

        Returns:
            The updated ethereum interchain network
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        if private_key is not None and not isinstance(private_key, str):
            raise TypeError('Parameter "private_key" must be of type str.')
        if rpc_address is not None and not isinstance(rpc_address, str):
            raise TypeError('Parameter "rpc_address" must be of type str.')
        if chain_id is not None and not isinstance(chain_id, int):
            raise TypeError('Parameter "chain_id" must be of type int.')
        body = cast(Dict[str, Any], {"version": "1"})
        if private_key:
            body["private_key"] = private_key
        if rpc_address:
            body["rpc_address"] = rpc_address
        if chain_id is not None:
            body["chain_id"] = chain_id
        return self.request.patch("/v1/interchains/ethereum/{}".format(name), body)

    def sign_ethereum_transaction(
        self,
        name: str,
        to: str,
        value: str,
        data: Optional[str] = None,
        gas_price: Optional[str] = None,
        gas: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> "request_response":
        """Create and sign an ethereum transaction using your chain's interchain network

        Args:
            name (str): name of the ethereum network to use for signing
            to (str): hex of the address to send to
            value (str): hex value in wei to send
            data (str, optional): hex data to publish in the transaction
            gas_price (str, optional): hex value of the gas price to pay (in wei), if not supplied it will be estimated for you
            gas (str, optional): hex value of the maximum amount of gas allowed (gasLimit), if not supplied it will be estimated for you
            nonce (str, optional): hex value of the nonce ot use for this transaction, if not supplied it will be automatically determined

        Raises:
            TypeError: with bad parameter types

        Returns:
            The built and signed transaction
        """
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        transaction = _build_ethereum_transaction_body(to=to, value=value, data=data, gas_price=gas_price, gas=gas, nonce=nonce)
        return self.request.post("/v1/interchains/ethereum/{}/transaction".format(name), transaction)

    def get_interchain_network(self, blockchain: str, name: str) -> "request_response":
        """Get a configured interchain network/wallet from the chain

        Args:
            blockchain (str): The blockchain type to get (i.e. 'bitcoin', 'ethereum')
            name (str): The name of the that blockchain's network (set when creating the network)

        Raises:
            TypeError: with bad parameter types

        Returns:
            The saved interchain network (exact schema depends on blockchain)
        """
        if not isinstance(blockchain, str):
            raise TypeError('Parameter "blockchain" must be of type str.')
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        return self.request.get("/v1/interchains/{}/{}".format(blockchain, name))

    def delete_interchain_network(self, blockchain: str, name: str) -> "request_response":
        """Delete an interchain network/wallet from the chain

        Args:
            blockchain (str): The blockchain type to delete (i.e. 'bitcoin', 'ethereum')
            name (str): The name of the that blockchain's network (set when creating the network)

        Raises:
            TypeError: with bad parameter types

        Returns:
            Success message
        """
        if not isinstance(blockchain, str):
            raise TypeError('Parameter "blockchain" must be of type str.')
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        return self.request.delete("/v1/interchains/{}/{}".format(blockchain, name))

    def list_interchain_networks(self, blockchain: str) -> "request_response":
        """List all the interchain network/wallets for a blockchain type

        Args:
            blockchain (str): The blockchain type to get (i.e. 'bitcoin', 'ethereum')

        Raises:
            TypeError: with bad parameter type

        Returns:
            List of interchain networks for the specified blockchain type
        """
        if not isinstance(blockchain, str):
            raise TypeError('Parameter "blockchain" must be of type str.')
        return self.request.get("/v1/interchains/{}".format(blockchain))

    def set_default_interchain_network(self, blockchain: str, name: str) -> "request_response":
        """Set the default interchain network for the chain to use (L5 Only)

        Args:
            blockchain (str): The blockchain type to set (i.e. 'bitcoin', 'ethereum')
            name (str): The name of the that blockchain's network to use (set when creating the network)

        Raises:
            TypeError: with bad parameter type

        Returns:
            The interchain network which was set as default
        """
        if not isinstance(blockchain, str):
            raise TypeError('Parameter "blockchain" must be of type str.')
        if not isinstance(name, str):
            raise TypeError('Parameter "name" must be of type str.')
        return self.request.post("/v1/interchains/default", {"version": "1", "blockchain": blockchain, "name": name})

    def get_default_interchain_network(self) -> "request_response":
        """Get the set default interchain network for this chain (L5 Only)

        Returns:
            The interchain network which was set as default
        """
        return self.request.get("/v1/interchains/default")

    def create_bitcoin_transaction(
        self,
        network: str,
        satoshis_per_byte: Optional[int] = None,
        data: Optional[str] = None,
        change_address: Optional[str] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
    ) -> "request_response":
        """!This method is deprecated and should not be used!
        Backwards compatibility will exist for legacy chains, but will not work on new chains. sign_bitcoin_transaction should be used instead

        Create and sign a bitcoin transaction using your chain's private keys

        Args:
            network (str): network to create transaction for. Only valid values are ``BTC_MAINNET`` and ``BTC_TESTNET3``
            satoshis_per_byte (int, optional): fee to pay in satoshis/byte. If not supplied, it will be estimated for you.
            data (str, optional): string to embed in the transaction as null-data output type
            change_address (str, optional): address to send change to. If not supplied, it will default to the address you are sending from
            outputs (list, optional): (list of {'to': str, 'value': float} dictionaries. Value float is in BTC)

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            The built and signed transaction
        """
        logger.warning(
            "This method is deprecated. It will continue to work for legacy chains, but will not work on any new chains. Use sign_bitcoin_transaction instead"
        )
        valid_networks = ["BTC_MAINNET", "BTC_TESTNET3"]
        if network not in valid_networks:
            raise ValueError('Parameter "network" must be one of {}.'.format(valid_networks))
        transaction = _build_bitcoin_transaction_body(satoshis_per_byte=satoshis_per_byte, data=data, change_address=change_address, outputs=outputs)
        return self.request.post("/v1/public-blockchain-transaction", body={"network": network, "transaction": transaction})

    def create_ethereum_transaction(
        self, network: str, to: str, value: str, data: Optional[str] = None, gas_price: Optional[str] = None, gas: Optional[str] = None
    ) -> "request_response":
        """!This method is deprecated and should not be used!
        Backwards compatibility will exist for legacy chains, but will not work on new chains. sign_ethereum_transaction should be used instead

        Create and sign a public ethereum transaction using your chain's private keys

        Args:
            network (str): network to create transaction for. Only valid values are:
                ETH_MAINNET
                ETH_ROPSTEN
                ETC_MAINNET
                ETC_MORDEN

            to (str): hex of the address to send to
            value (str): hex value (in wei) to send
            data (str, optional): hex data to publish in the transaction
            gas_price (str, optional): hex value of the gas price to pay (in wei), if not supplied it will be estimated for you
            gas (str, optional): hex value of the maximum amount of gas allowed (gasLimit), if not supplied it will be estimated for you

        Raises:
            TypeError: with bad parameter types
            ValueError: with bad parameter values

        Returns:
            The built and signed transaction
        """
        logger.warning(
            "This method is deprecated. It will continue to work for legacy chains, but will not work on any new chains. Use sign_ethereum_transaction instead"
        )
        valid_networks = ["ETH_MAINNET", "ETH_ROPSTEN", "ETC_MAINNET", "ETC_MORDEN"]
        if network not in valid_networks:
            raise ValueError('Parameter "network" must be one of {}.'.format(valid_networks))
        transaction = _build_ethereum_transaction_body(to=to, value=value, data=data, gas_price=gas_price, gas=gas)
        return self.request.post("/v1/public-blockchain-transaction", body={"network": network, "transaction": transaction})

    def get_public_blockchain_addresses(self) -> "request_response":
        """!This method is deprecated and should not be used!
        Backwards compatibility will exist for legacy chains, but will not work on new chains. list_interchain_networks should be used instead

        Get interchain addresses for this Dragonchain node (L1 and L5 only)

        Returns:
            Dictionary containing addresses
        """
        logger.warning(
            "This method is deprecated. It will continue to work for legacy chains, but will not work on any new chains. Use list_interchain_networks instead"
        )
        return self.request.get("/v1/public-blockchain-address")


def _validate_and_build_custom_index_fields_array(  # noqa: C901
    custom_index_fields: Iterable["custom_index_fields_type"]
) -> List["custom_index_fields_type"]:
    """Validate a list of custom index fields and return a list which can be passed as a body for custom indexes to the chain

    Args:
        custom_index_fields: The iterable of the user-input custom index fields

    Raises:
        TypeError: with bad custom index parameters

    Returns:
        List of custom index fields to pass to the chain
    """
    return_list = []
    for cust_index in custom_index_fields:
        if not isinstance(cust_index, dict):
            raise TypeError('All items in "custom_index_fields" must be of type dict.')
        # Check all the required fields
        type_val = cust_index.get("type")
        path_val = cust_index.get("path")
        field_name_val = cust_index.get("field_name")
        options_val = cust_index.get("options")
        if not path_val or not isinstance(path_val, str):
            raise TypeError('All items in "custom_index_fields.path" must be of type str.')
        if type_val not in ["text", "tag", "number"]:
            raise TypeError('All items in "custom_index_fields.type" must be either "text", "tag", or "number".')
        if not field_name_val or not isinstance(field_name_val, str):
            raise TypeError('All items in "custom_index_fields.field_name" must be of type str.')
        # Check the (not required) options dict if it exists
        if options_val:
            if not isinstance(options_val, dict):
                raise TypeError('All items in "custom_index_fields.options" must be of type dict.')
            separator = options_val.get("separator")
            no_index = options_val.get("no_index")
            weight = options_val.get("weight")
            no_stem = options_val.get("no_stem")
            sortable = options_val.get("sortable")
            if separator and not isinstance(separator, str):
                raise TypeError('All items in "custom_index_fields.options.separator" must be of type str.')
            if no_index and not isinstance(no_index, bool):
                raise TypeError('All items in "custom_index_fields.options.no_index" must be of type bool.')
            if weight and not isinstance(weight, (int, float)):
                raise TypeError('All items in "custom_index_fields.options.weight" must be of type int or float.')
            if no_stem and not isinstance(no_stem, bool):
                raise TypeError('All items in "custom_index_fields.options.no_stem" must be of type bool.')
            if sortable and not isinstance(sortable, bool):
                raise TypeError('All items in "custom_index_fields.options.sortable" must be of type bool.')
            # Trim options val to only necessary values in case extras were passed in
            sending_options = {}
            if no_index is not None:
                sending_options["no_index"] = no_index
            if type_val == "tag":
                if separator is not None:
                    sending_options["separator"] = separator
            elif type_val == "number":
                if sortable is not None:
                    sending_options["sortable"] = sortable
            else:  # Text is only one left
                if no_stem is not None:
                    sending_options["no_stem"] = no_stem
                if weight is not None:
                    sending_options["weight"] = weight
                if sortable is not None:
                    sending_options["sortable"] = sortable
            options_val = sending_options
        return_list.append(
            cast("custom_index_fields_type", {"path": path_val, "type": type_val, "field_name": field_name_val, "options": options_val or {}})
        )
    return return_list


def _build_transaction_dict(transaction_type: str, payload: Union[str, Dict[Any, Any]], tag: Optional[str] = None) -> Dict[str, Any]:
    """Build the json (dictionary) body for a transaction given its inputs

    Args:
        transaction_type (str): The transaction type for this transaction
        payload (str, dict): The intended payload for this transaction
        tag (str, optional): The intended tag for this transaction

    Raises:
        TypeError: with bad parameter types

    Returns:
        Dictionary body to use for sending as a transaction
    """
    if not isinstance(transaction_type, str):
        raise TypeError('Parameter "transaction_type" must be of type str.')
    if not isinstance(payload, str) and not isinstance(payload, dict):
        raise TypeError('Parameter "payload" must be of type dict or str.')
    if tag is not None and not isinstance(tag, str):
        raise TypeError('Parameter "tag" must be of type str.')

    body = {"version": "1", "txn_type": transaction_type, "payload": payload}
    if tag:
        body["tag"] = tag

    return body


def _build_ethereum_transaction_body(
    to: str, value: str, data: Optional[str] = None, gas_price: Optional[str] = None, gas: Optional[str] = None, nonce: Optional[str] = None
) -> Dict[str, Any]:
    """Build the json (dictionary) body for an ethereum transaction given its inputs

    Args:
        to (str): hex of the address to send to
        value (str): hex value (in wei) to send
        data (str, optional): hex data to publish in the transaction
        gas_price (str, optional): hex value of the gas price to pay (in wei), if not supplied it will be estimated for you
        gas (str, optional): hex value of the maximum amount of gas allowed (gasLimit), if not supplied it will be estimated for you
        nonce (str, optional): hex value of the nonce ot use for this transaction, if not supplied it will be automatically determined

    Raises:
        TypeError: with bad parameter types

    Returns:
        Dictionary body to use for sending an ethereum transaction
    """
    if not isinstance(to, str):
        raise TypeError('Parameter "to" must be of type str.')
    if not isinstance(value, str):
        raise TypeError('Parameter "value" must be of type str.')
    if data is not None and not isinstance(data, str):
        raise TypeError('Parameter "data" must be of type str.')
    if gas_price is not None and not isinstance(gas_price, str):
        raise TypeError('Parameter "gas_price" must be of type str.')
    if gas is not None and not isinstance(gas, str):
        raise TypeError('Parameter "gas" must be of type str.')
    if nonce is not None and not isinstance(nonce, str):
        raise TypeError('Parameter "nonce" must be of type str.')

    body = cast(Dict[str, Any], {"version": "1", "to": to, "value": value})
    if data:
        body["data"] = data
    if gas_price:
        body["gasPrice"] = gas_price
    if gas:
        body["gas"] = gas
    if nonce:
        body["nonce"] = nonce

    return body


def _build_bitcoin_transaction_body(
    satoshis_per_byte: Optional[int] = None,
    data: Optional[str] = None,
    change_address: Optional[str] = None,
    outputs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build the json (dictionary) body for a bitcoin transaction given its inputs

    Args:
        satoshis_per_byte (int, optional): fee to pay in satoshis/byte. If not supplied, it will be estimated for you.
        data (str, optional): string to embed in the transaction as null-data output type
        change_address (str, optional): address to send change to. If not supplied, it will default to the address you are sending from
        outputs (list, optional): (list of {'to': str, 'value': float} dictionaries. Value float is in BTC)

    Raises:
        TypeError: with bad parameter types

    Returns:
        Dictionary body to use for sending a bitcoin transaction
    """
    if satoshis_per_byte is not None and not isinstance(satoshis_per_byte, int):
        raise TypeError('Parameter "satoshis_per_byte" must be of type int.')
    if data is not None and not isinstance(data, str):
        raise TypeError('Parameter "data" must be of type str.')
    if change_address is not None and not isinstance(change_address, str):
        raise TypeError('Parameter "change_address" must be of type str.')
    if outputs is not None and not isinstance(outputs, list):
        raise TypeError('Parameter "outputs" must be of type list.')

    body = cast(Dict[str, Any], {"version": "1"})
    if outputs:
        body["outputs"] = outputs
    if satoshis_per_byte:
        body["fee"] = satoshis_per_byte
    if data:
        body["data"] = data
    if change_address:
        body["change"] = change_address

    return body
