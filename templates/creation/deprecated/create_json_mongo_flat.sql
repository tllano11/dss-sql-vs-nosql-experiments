/*
        Export TPC-H's customer, order and lineitems tables in MongoDB's
        extended JSON format
*/
\c tpch
-- Remove headers
\t on
-- Remove spacing between the results
\pset format unaligned
-- Convert relational data to JSON

select row_to_json(r) from
(select
    c_custkey,
    c_name,
    c_address,
    c_nationkey,
    c_phone::text,
    c_acctbal,
    c_mktsegment::text,
    c_comment,
    o_orderkey,
    o_orderstatus,
    o_totalprice,
    o_oderdate,
    o_orderpriority::text,
    o_clerk::text,
    o_shippriority,
    o_comment,
    l_partkey,
    l_suppkey,
    l_quantity,
    l_extendedprice,
    l_discount,
    l_tax,
    l_returnflag,
    l_linestatus,
    l_shipdate,
    l_commitdate,
    l_receiptdate,
    l_shipinstruct::text,
    l_shipmode::text,
    l_comment
 from
    (select
             o_custkey,
             o_orderkey,
             o_orderstatus,
             o_totalprice,
             json_build_object('$date', to_char(o.o_orderdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')) as o_oderdate,
             o_orderpriority::text,
             o_clerk::text,
             o_shippriority,
             o_comment,
	     l_linenumber,
             l_partkey,
             l_suppkey,
             l_quantity,
             l_extendedprice,
             l_discount,
             l_tax,
             l_returnflag,
             l_linestatus,
             json_build_object('$date', to_char(l_shipdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')) as l_shipdate,
             json_build_object('$date', to_char(l_commitdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')) as l_commitdate,
             json_build_object('$date', to_char(l_receiptdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')) as l_receiptdate,
             l_shipinstruct::text,
             l_shipmode::text,
             l_comment
     from
             scale1.orders o full outer join scale1.lineitem l
             on o.o_orderkey = l.l_orderkey) o full outer join scale1.customer c
             on o.o_custkey = c.c_custkey) r \g json_data_flat.json
