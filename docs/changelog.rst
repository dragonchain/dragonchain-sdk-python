Changelog
=========

4.1.0
-----

Features:
  * Add Binance interchain support
Development:
  * Add integration tests for Binance feature
  * Add/Update integration tests for Dragonchain 4.2.0

4.0.1
-----

Packaging:
  * Officially support python 3.8 in packaged release
Development:
  * Fix unit tests for proper async context mocking with python 3.8+
  * Add integration tests for Dragonchain 4.1.0 features and changes

4.0.0
-----

Because Dragonchain has a breaking change to replace its indexing solution,
this is also a breaking SDK change for queries and custom indexing.

The following are worth noting when transitioning from 3.X.X to 4.X.X:

* Custom indexes have changed for a new redisearch schema. Transaction types
  can no longer be updated, and custom indexes must be provided upfront when
  creating a transaction type or smart contract. If updating is desired,
  simply delete and recreate the relevant transaction type/smart contract
  with the new desired custom indexes.
* A transaction type's indexes are now removed when the transaction type is
  deleted. You can no longer query for transactions from a deleted transaction
  type (or smart contract). (The transactions still exist and can be retrieved
  directly by transaction id, they simply can't be searched with a query)
* Querying blocks and transactions are completely different, and now use
  `Redisearch queries <https://oss.redislabs.com/redisearch/Query_Syntax.html>`_.
  Check their client functions for argument reference. Note the response schema
  of queries remain unchanged.
* Smart contract querying has been removed, and instead replaced with a generic
  ``list_smart_contracts`` which simply returns all contracts.

Check `the docs <https://python-sdk-docs.dragonchain.com/latest/migrating_v4.html>`_
for more details on migrating from v3 to v4.

Features:
  * Support new query endpoints/parameters for redisearch replacement on
    dragonchain
  * Support adding custom indexes for smart contracts on creation
  * Support optionally fetching ids only (not entire documents) for querying
  * Support list smart contracts
  * Support disable schedule for ``update_smart_contract``
  * Support new smart contract logs endpoint
Documentation:
  * Added docs for migrating from v3 to v4
Development:
  * Modify integration test suite to integrate with new/modified endpoints
Packaging:
  * Update packaged metadata to indicate supported OS and stable/typed
  * Enforce stricter rules when building docs

3.3.0
-----

Features:
  * Add deprecation warnings for ``create_bitcoin_transaction``,
    ``create_ethereum_transaction`` and ``get_public_blockchain_addresses``
  * Add support for new interchain management endpoints

    * ``create_bitcoin_interchain``
    * ``update_bitcoin_interchain``
    * ``sign_bitcoin_transaction``
    * ``create_ethereum_interchain``
    * ``update_ethereum_interchain``
    * ``sign_ethereum_transaction``
    * ``get_interchain_network``
    * ``delete_interchain_network``
    * ``list_interchain_networks``
    * ``set_default_interchain_network``
    * ``get_default_interchain_network``
Packaging:
  * Moved repository to `new location <https://github.com/dragonchain/dragonchain-sdk-python>`_

3.2.0
-----

Features:
  * Use new versioned api endpoints
  * Add support for pending verifications endpoint
Packaging:
  * Specify explicit support for PyPy

3.1.1
-----

Features:
  * Support the addition of nicknames to api keys on chain
Bugs:
  * Fixed a bug relating to a trailing `/` used in the find command when
    running unit tests on mac

3.1.0
-----

Features:
  * Support for async/await with the ``create_aio_client`` function
    (refer to the docs for more details)
Documentation:
  * Added docs related to asyncio support
Packaging:
  * Added aiohttp as a dependency when installing ``aio``
    extras. Install ``dragonchain-sdk[aio]`` for
    async/await support.

3.0.4
-----

Bugs:
  * Fixed a bug for ``create_ethereum_transaction``
    to work with a custom gas price
  * Stop sending unsolicited HTTP bodies and
    Content-Type headers when not necessary
Documentation:
  * Restructure documentation site layout
  * Add new docs for installation, configuration, getting started,
    etc (no longer use README.rst for docs)
  * Added Changelog
  * Switch to readthedocs theme
Packaging:
  * Added ``typing`` as a dependency for python < 3.5
    to fix distribution for python 3.4
  * Become compliant with `PEP 561 <https://www.python.org/dev/peps/pep-0561/>`_ typing distribution
Development:
  * Added and started enforcing stricter typing
  * Added a full suite of integration tests
  * Added code owners which are required for PR review
  * Added issue and PR templates for github
