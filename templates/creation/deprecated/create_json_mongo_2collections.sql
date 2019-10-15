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
select row_to_json(o) from
     (select 
             o_orderkey as _id,
             o_custkey,
             o_orderstatus,
             o_totalprice,
             json_build_object('$date', to_char(o.o_orderdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')) as o_orderdate,
             o_orderpriority::text,
             o_clerk::text,
             o_shippriority,
             o_comment,
             coalesce(json_agg(json_build_object(
                       'l_partkey', l.l_partkey,
                       'l_suppkey', l.l_suppkey,
                       'l_linenumber', l.l_linenumber,
                       'l_quantity', l.l_quantity,
                       'l_extendedprice', l.l_extendedprice,
                       'l_discount', l.l_discount,
                       'l_tax', l.l_tax,
                       'l_returnflag', l.l_returnflag,
                       'l_linestatus', l.l_linestatus,
                       'l_shipdate', json_build_object('$date', to_char(l.l_shipdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')),
                       'l_commitdate', json_build_object('$date', to_char(l.l_commitdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')),
                       'l_receiptdate', json_build_object('$date', to_char(l.l_receiptdate,'YYYY-MM-DD"T"HH24:MI:SS"Z"')),
                       'l_shipinstruct', l.l_shipinstruct::text,
                       'l_shipmode', l.l_shipmode::text,
                       'l_comment', l.l_comment    
             )) filter (where l.l_linenumber is not null), '[]') as o_lineitems
      from 
           scale1.orders o left outer join scale1.lineitem l
           on o.o_orderkey = l.l_orderkey 
      group by 
            _id, 
	    o_custkey,
            o_orderstatus, 
            o_totalprice, 
            o_orderdate, 
            o_orderpriority, 
            o_clerk, 
            o_shippriority, 
            o_comment, 
            o_custkey) o \g json_data_order-litems.json

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

