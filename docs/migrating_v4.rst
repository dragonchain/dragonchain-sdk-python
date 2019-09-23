Migrating From v3 to v4
=======================

Dragonchain 4.0.0 and later requires the python SDK 4.0.0 or later in order to
support all functionality properly.

This SDK follows `Semantic Versioning <https://semver.org>`_, which means that
v4 introduced backwards-incompatible changes. If you are were previously using
the v3 version of this SDK, then the following are some considerations that
should be taken before upgrading.

General Changes
---------------

If you update your dragonchain from version 3.X.X to version 4.0.0 or later,
you will lose access to your version 3.X.X custom indexes. More information can
be found `here <https://dragonchain-core-docs.dragonchain.com/latest/deployment/migrating_v4.html>`_.

Transactions from before this update will still exist, and blockchain integrity
will not be compromised. If there are important transactions that you would
like to query from before the update, we suggest saving the transaction ids and
getting the transactions directly. If you rely on custom indexes and queries,
this section will guide you through key differences.

Custom Indexing in version 4.0.0 and later uses Redisearch. To create a custom
index in these versions, you must create a new index using
`redisearch fields <https://oss.redislabs.com/redisearch/Commands.html#field_options>`_.
Dragonchain version 4.0.0 supports the use of ``text``, ``tag``, and ``number``
fields. Your custom indexes may further be customized by specifying options.
Options for ``text`` fields include ``weight``, ``noStem``, ``sortable``, and
``noIndex``. Options for ``tag`` fields include ``separator`` and ``noIndex``.
Options for ``number`` fields include `sortable` and `noIndex`. Just like with
the previous indexing solution, each field must have a ``path`` and a
``fieldName`` (previously ``key``) to uniquely identify it within a payload.

Querying on version 4.0.0 and later uses a different query syntax. Redisearch
query syntax can be `found here <https://oss.redislabs.com/redisearch/Query_Syntax.html>`_.

Dragonchains of version 4.0.0 or later will not support updating of custom
indexes. Instead, an index must be deleted and then re-created to change its
indexes. When an index is deleted, all indexed items will be permanently
removed. Be cautious when deleting indexes as they cannot be recovered. Custom
indexes for smart contracts and transaction types must be declared when they
are created.

Method Changes
--------------

The following are the actual api (function) changes:

* ``query_transactions`` method signature has changed from (lucene_query, sort,
  offset, limit) to (transaction_type, redisearch_query, verbatim, offset,
  limit, sort_by, sort_ascending, ids_only). `verbatim <https://oss.redislabs.com/redisearch/Commands.html#ftsearch>`_
  means that the query will not use stems and ``ids_only`` improves performance
  by returning only the transaction ids that match the query, rather than the
  full object. Though the input parameters have changed, the return schema of
  query methods has not changed.

* ``query_blocks`` method signature has changed from (lucene_query, sort,
  offset, limit) to (redisearch_query, offset, limit, sort_by, sort_ascending,
  ids_only). It has the same behavior as query_transactions.

* ``custom_index_fields`` has replaced ``custom_indexes`` in
  ``create_transaction_type``.

* ``custom_index_fields`` has been added to ``create_smart_contract``. This
  allows you to create custom indexes on the transaction type created by a
  smart contract in one step, which is required for custom indexes. The type is
  the same as the ``custom_index_fields`` from the ``create_transaction_type``
  object.

* ``query_smart_contracts`` has been removed. ``list_smart_contracts`` has been
  provided as an alternative and returns a list of all smart contracts on the
  chain.

* ``update_transaction_type`` has been removed.
