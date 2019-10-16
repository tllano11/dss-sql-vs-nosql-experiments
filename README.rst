Description
===========
This repository contains the queries and scripts used for the experiments described
on the paper: "Experimental Comparison of Relational and NoSQL Systems: the Case of 
Decision Support"

Directory structure
===================

results
-------
Contains the results for each experiment on different scale factors. The sub-directory
structure follows the form ``<experiment>/<scale>/``; where the file ``results.csv`` in 
``<scale>`` contains the average running time of each query, and the files ``<query>.explain``
the query plan for a given query in each run.  If
the experiments involve indexes then the sub-directory structure becomes
``<experiment>/<idx|noIdx>/<scale>/``, where results in ``idx`` used indexes
and results in ``noIdx`` did not.

templates
---------
Contains the ``jinja2`` templates of all **queries** and scripts involved in the
creation of the schemas used during experimentation. The ``vars.yml`` file
has all variables required to render such templates.

bin
---
Contains the scripts used to create and run the experiments. Queries are rendered using
the ``create_queries.py`` script (use ``-h`` option for help) and then run using the
``run_experiment.sh`` script (use ``-h`` option for help). The ``crjoin`` sub-folder contains
the ``C++`` source code of a program we designed to transform the TPCH tables: customer,
orders, and lineitem, produced by DBGEN to MongoDB's extended json format. The program
was originally built using GCCv8.3.0 and can be compiled using ``make``.

**NOTE:** It is assumed MongoDB's access control is disabled.
The scripts only work (as they are) on a MongoDB deployment that does not enforce
authentication.

