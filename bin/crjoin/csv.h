#pragma once
#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <memory>
#include <stddef.h>

#define name(variable) (#variable)

using namespace std;

enum Operation {
		 CREATE_C_JOIN_O_JOIN_L,
		 CREATE_O_JOIN_L,
		 CREATE_SINGLE,
		 CREATE_PSQL_JSON
};

class Record {
public:
  static Operation* context;
  virtual string toJson() = 0;
};

class Lineitem : public Record {
public:
  int l_orderkey;
  int l_partkey;
  int l_suppkey;
  int l_linenumber;
  float l_quantity;
  float l_extendedprice;
  float l_discount;
  float l_tax;
  string l_returnflag;
  string l_linestatus;
  string l_shipdate;
  string l_commitdate;
  string l_receiptdate;
  string l_shipinstruct;
  string l_shipmode;
  string l_comment;
  Lineitem(string *line);
  string toJson();
};

class BaseOrder : public Record {
 public:
  int o_orderkey;
  int o_custkey;
  string o_orderstatus;
  float o_totalprice;
  string o_orderdate;
  string o_orderpriority;
  string o_clerk;
  int o_shippriority;
  string o_comment;
  BaseOrder(string *line);
};

class Order : public BaseOrder {
  public:
  Order(string *line);
  string toJson();
};

class OrderLitem : public BaseOrder {
  public:
  vector<unique_ptr<Lineitem>> o_lineitems;
  OrderLitem(string *line);
  ~OrderLitem();
  string toJson();
};

class BaseCustomer : public Record {
  public:
  int c_custkey;
  string c_name;
  string c_address;
  int c_nationkey;
  string c_phone;
  float c_acctbal;
  string c_mktsegment;
  string c_comment;
  BaseCustomer(string *line);
};

class Customer : public BaseCustomer {
  public:
  Customer(string *line);
  string toJson();
};

class CustomerOrder : public BaseCustomer {
  public:
  vector<unique_ptr<OrderLitem>> c_orders;
  CustomerOrder(string *line);
  ~CustomerOrder();
  string toJson();
};
