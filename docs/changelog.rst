Changelog
=========

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
