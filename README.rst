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

Query Generation
================
Queries can be rendered using the ``create_queries.py`` script under ``./bin``. For
instance, to generate all queries from the ``TPCH`` experiment one could
execute::

  ./bin/create_queries.py -t ./templates/tpch_experiment -o /path/to/output/dir

TPCH dataset generation
==================
The first step is to render the scripts inside the ``templates/creation`` folder. To do
so you can use the ``create_queries.py`` script. An example is shown below.::

  ./bin/create_queries.py -t ./templates/creation -o /path/to/output/dir

Then, follow the instructions for each database below.

PostgreSQL
----------
1. Execute ``./dbgen -s <scale factor>`` inside ``/path/to/TPC\_H/dbgen/``.
2. Remove the extra ``|`` at the end of each line from each ``.tbl`` file produced 
   in the previous step. For example, as shown below.::

     for i in`ls *.tbl`; do sed -i's/|$//'$i; done

3. Import the data into PostgreSQL using the rendered ``create_rdb.sql`` script
   from the ``creation`` templates.

MongoDB
-------
1. Sort order by ``custkey``::

     # sort stores temporary files in /tmp by default. If the
     # data is considerably big, one may need to use the -T option.
     sort -kn 2 -t '|' orders.tbl > orders_sorted.csv

2. Sort lineitems by orderkey taken into consideration the new order produced from the
   previous step::

     awk -F'|' 'NR==FNR{o[$1]=FNR; next} {print o[$1] ``|'' $0}' \
     <(awk -F'|' '{print $1}' orders_sorted.csv | uniq) \
     lineitem.tbl | sort -t '|' -nk1 | cut -d'|' -f2- > \
     lineitem_sorted.csv

3. Compile the program under ``./bin/crjoin``.
4. Manually create the desired schemas using the program from the previous step and import
   the produced json file/s to MongoDB. You can use the rendered ``build.sh`` script 
   (use the ``-h`` option for help) from the ``creation`` templates as a guide.
