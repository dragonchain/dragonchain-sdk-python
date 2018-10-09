"""
Copyright 2018 Dragonchain, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
from configparser import ConfigParser
from pathlib import Path
from dc_sdk.lib.request import make_request, get_lucene_query_params

valid_runtimes = [
    'nodejs6.10',
    'nodejs8.10',
    'java8',
    'python2.7',
    'python3.6',
    'dotnetcore1.0',
    'dotnetcore2.0',
    'dotnetcore2.1',
    'go1.x'
]

valid_sc_types = [
    'transaction',
    'cron'
]


def get_auth_key(dragonchain_id=None):
    """
    Get an auth_key/auth_key_id pair
    First checks environment, then configuration files
    :type dragonchain_id: string
    :param dragonchain_id: (optional) dragonchain_id to get keys for (it pulling from config files)
    :return: Tuple where index 0 is the auth_key_id and index 1 is the auth_key
    """
    auth_key = os.environ.get('DRAGONCHAIN_AUTH_KEY')
    auth_key_id = os.environ.get('DRAGONCHAIN_AUTH_KEY_ID')
    if auth_key is None or auth_key_id is None:
        # If both keys aren't in environment variables, check config file
        if dragonchain_id is None:
            raise RuntimeError('Could not locate credentials for this client')
        cred_file_path = None
        if os.name == 'nt':
            cred_file_path = os.path.expandvars(r'%LOCALAPPDATA%\dragonchain\credentials')
        else:
            cred_file_path = '{}/.dragonchain/credentials'.format(Path.home())
        config = ConfigParser()
        config.read(cred_file_path)
        try:
            auth_key = config.get(dragonchain_id, 'auth_key')
            auth_key_id = config.get(dragonchain_id, 'auth_key_id')
            return auth_key_id, auth_key
        except Exception:
            raise RuntimeError('Could not locate credentials for this client')
    else:
        return auth_key_id, auth_key


def generate_dragonchain_endpoint(dragonchain_id):
    """
    Generate a dragonchain endpoint for a chain hosted by Dragonchain Inc
    :type dragonchain_id: string
    :param dragonchain_id: dragonchain id to generate the endpoint for
    :return: String of the dragonchain endpoint
    """
    return 'https://{}.api.dragonchain.com'.format(dragonchain_id)


def is_valid_runtime(runtime):
    """
    Checks if a runtime string is valid
    :type runtime: string
    :param runtime: runtime to validate
    :return: boolean if runtime is valid
    """
    if runtime not in valid_runtimes:
        return False
    return True


def is_valid_sc_type(sc_type):
    """
    Checks if a smart contract type string is valid
    :type sc_type: string
    :param sc_type: sc_type to validate
    :return: boolean if sc_type is valid
    """
    if sc_type not in valid_sc_types:
        return False
    return True


class Client(object):
    """
    A client that interfaces all functionality to a dragonchain with a given id and key
    """
    def __init__(self, dragonchain_id=None, auth_key_id=None,
                 auth_key=None, endpoint=None, verify=True):
        """
        Construct a new 'Client' object
        :type dragonchain_id: string
        :param dragonchain_id: dragonchain id to associate with this client
        :type auth_key_id: string
        :param auth_key_id: (Optional) Dragonchain authorization key ID
        :type auth_key: string
        :param auth_key: (Optional) Dragonchain authorization key
        :type endpoint: string
        :param endpoint: (Optional) Endpoint of the dragonchain
        :type verify: boolean
        :param verify: (Optional) Verify the TLS certificate of the dragonchain
        """
        if not isinstance(dragonchain_id, str):
            raise ValueError('Dragonchain ID must be specified as a string')
        self.dcid = dragonchain_id
        if auth_key is None or auth_key_id is None:
            self.auth_key_id, self.auth_key = get_auth_key(self.dcid)
        else:
            if not isinstance(auth_key, str) or not isinstance(auth_key_id, str):
                raise ValueError('auth_key and auth_key_id must be specified as a strings')
            self.auth_key = auth_key
            self.auth_key_id = auth_key_id
        if endpoint is None:
            self.endpoint = generate_dragonchain_endpoint(dragonchain_id)
        else:
            if not isinstance(endpoint, str):
                raise ValueError('endpoint must be specified as a string')
            self.endpoint = endpoint
        if not isinstance(verify, bool):
            raise ValueError('verify must be specified as a boolean')
        self.verify = verify

    def perform_get(self, path):
        """
        Make a GET request for this chain
        :type path: string
        :param path: path of the request (including any path query parameters)
        :return: response of the get request
        """
        return make_request(endpoint=self.endpoint, auth_key=self.auth_key,
                            auth_key_id=self.auth_key_id, dcid=self.dcid,
                            http_verb='GET', path=path, verify=self.verify)

    def perform_post(self, path, body):
        """
        Make a json body POST request for this chain
        :type path: string
        :param path: path of the request (including any path query parameters)
        :type body: JSON serializable dictionary
        :param body: body of the request as a python dictionary
        :return: response of the post request
        """
        return make_request(endpoint=self.endpoint, auth_key=self.auth_key,
                            auth_key_id=self.auth_key_id, dcid=self.dcid,
                            http_verb='POST', path=path, verify=self.verify, json=body)

    def get_status(self):
        """
        Get the status of a dragonchain
        :return: Parsed json response from the chain
        """
        return self.perform_get('/chain/status')

    def query_contracts(self, query=None, sort=None, offset=0, limit=10):
        """
        Preform a query on a chain's smart contracts
        :type query: string
        :param query: lucene query parameter (i.e.: is_serial:true)
        :type sort: string
        :param sort: sort syntax of 'field:direction' (i.e.: name:asc)
        :type offset: integer
        :param offset: pagination offset of query (default 0)
        :type limit: integer
        :param limit: pagination limit (default 10)
        :return: Parsed json response from the chain
        """
        query_params = get_lucene_query_params(query, sort, offset, limit)
        return self.perform_get('/chain/contract{}'.format(query_params))

    def get_contract(self, name):
        """
        Get a specific smart contract
        :type name: string
        :param name: name of the smart contract to get
        :return: Parsed json response from the chain
        """
        if not isinstance(name, str):
            raise ValueError('Smart contract name must be a string')
        return self.perform_get('/chain/contract/{}'.format(name))

    def post_custom_contract(self, name, code, runtime, sc_type, serial, env_vars=None):
        """
        Post a custom contract to a chain
        :type name: string
        :param name: name of the contract to create
        :type code: string
        :param code: base64 encoded zip of the code
        :type env_vars: dictionary
        :param env_vars: environment variables to set for the smart contract
        :type runtime: string
        :param runtime: string of the runtime for this smart contract
        :type sc_type: string
        :param sc_type: how the smart contract is invoked ('transaction' or 'cron')
        :type serial: boolean
        :param serial: whether or not the smart contract must be executed in serial
        :return: Parsed json response from the chain
        """
        if not isinstance(name, str):
            raise ValueError('name must be a string')
        if not isinstance(code, str):
            raise ValueError('code must be a string')
        if not isinstance(runtime, str) or not is_valid_runtime(runtime):
            raise ValueError('runtime must be a string and valid runtime from this list: {}'.format(valid_runtimes))
        if not isinstance(sc_type, str) or not is_valid_sc_type(sc_type):
            raise ValueError('sc_type must be either "transaction" or "cron"')
        if not isinstance(serial, bool):
            raise ValueError('serial must be a boolean')
        if env_vars and not isinstance(env_vars, dict):
            raise ValueError('env_vars must be a dictionary if set')
        body = {
            'version': '2',
            'origin': 'custom',
            'name': name,
            'code': code,
            'runtime': runtime,
            'sc_type': sc_type,
            'is_serial': serial
        }
        if env_vars:
            body['custom_environment_variables'] = env_vars
        return self.perform_post('/chain/contract', body)

    def query_transactions(self, query=None, sort=None, offset=0, limit=10):
        """
        Preform a query on a chain's transactions
        :type query: string
        :param query: lucene query parameter (i.e.: is_serial:true)
        :type sort: string
        :param sort: sort syntax of 'field:direction' (i.e.: name:asc)
        :type offset: integer
        :param offset: pagination offset of query (default 0)
        :type limit: integer
        :param limit: pagination limit (default 10)
        :return: Parsed json response from the chain
        """
        query_params = get_lucene_query_params(query, sort, offset, limit)
        return self.perform_get('/chain/transaction{}'.format(query_params))

    def get_transaction(self, txn_id):
        """
        Get a specific transaction by id
        :type txn_id: string
        :param txn_id: transaction id to get
        :return: Parsed json response from the chain
        """
        if not isinstance(txn_id, str):
            raise ValueError('txn_id must be a string')
        return self.perform_get('/chain/transaction/{}'.format(txn_id))

    def post_transaction(self, txn_type, payload, tag=None):
        """
        Post a transaction to a chain
        :type txn_type: string
        :param txn_type: the transaction type to create
        :type payload: string or dict
        :param payload: the payload of the transaction to create
        :type tag: string
        :param tag: (optional) the tag of the transaction to create
        :return: Parsed json response from the chain
        """
        if not isinstance(txn_type, str):
            raise ValueError('txn_type must be a string')
        if not (isinstance(payload, str) or isinstance(payload, dict)):
            raise ValueError('payload must be a dictionary or a string')
        if tag and not isinstance(tag, str):
            raise ValueError('tag must be a string')
        body = {
            'version': '1',
            'txn_type': txn_type,
            'payload': payload
        }
        if tag:
            body['tag'] = tag
        return self.perform_post('/chain/transaction', body)

    def query_blocks(self, query=None, sort=None, offset=0, limit=10):
        """
        Preform a query on a chain's blocks
        :type query: string
        :param query: lucene query parameter (i.e.: is_serial:true)
        :type sort: string
        :param sort: sort syntax of 'field:direction' (i.e.: name:asc)
        :type offset: integer
        :param offset: pagination offset of query (default 0)
        :type limit: integer
        :param limit: pagination limit (default 10)
        :return: Parsed json response from the chain
        """
        query_params = get_lucene_query_params(query, sort, offset, limit)
        return self.perform_get('/chain/block{}'.format(query_params))

    def get_block(self, block_id):
        """
        Get a specific block by id
        :type block_id: string
        :param block_id: block id to get
        :return: Parsed json response from the chain
        """
        if not isinstance(block_id, str):
            raise ValueError('block_id must be a string')
        return self.perform_get('/chain/block/{}'.format(block_id))
