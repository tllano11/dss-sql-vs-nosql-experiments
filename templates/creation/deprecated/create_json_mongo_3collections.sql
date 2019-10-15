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
select row_to_json(l) from
    (select
             json_build_object(
			'l_orderkey', l_orderkey,
			'l_linenumber', l_linenumber
             ) as _id,
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
             scale1.lineitem) l \g json_data_lineitem.json

select row_to_json(o) from
    (select
             o_orderkey as _id,
             o_custkey,
             o_orderstatus,
             o_totalprice,
             json_build_object('$date', to_char(o_orderdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')) as o_orderdate,
             o_orderpriority::text,
             o_clerk::text,
             o_shippriority,
             o_comment
     from
             scale1.orders) o \g json_data_orders.json

select row_to_json(c) from
     (select 
      	       c_custkey as _id,
	       c_name,
	       c_address,
	       c_nationkey,
	       c_phone::text,
	       c_acctbal,
	       c_mktsegment::text,
	       c_comment
      from
               scale1.customer) c \g json_data_customer.json
