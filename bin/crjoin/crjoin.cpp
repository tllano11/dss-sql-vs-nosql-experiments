#include <string>
#include <iostream>
#include <fstream>
#include <unistd.h>
#include <stddef.h>
#include "csv.h"

using namespace std;

struct EOFReached : public exception {
   const char * what () const throw () {
      return "EOF Reached Exception";
   }
};

template <class T> unique_ptr<T> next (ifstream *file) {
  string line;
  getline(*file, line);
  // Ignore blank lines
  while (line.length() == 0 && file->good()) {
    getline(*file, line);
  }
  if (!file->good()) {
    throw EOFReached();
  }
  unique_ptr<T> res = make_unique<T>(&line);
  return res;
}

void write(string json, ofstream *outFile) {
  *outFile << json;
  *outFile << "\n";
}

void create_json_1collection(ifstream *cfile, ifstream *ofile, ifstream *lfile, ofstream *outFile) {
  unique_ptr<Lineitem> litem = next<Lineitem>(lfile);
  unique_ptr<OrderLitem> order = next<OrderLitem>(ofile);
  unique_ptr<CustomerOrder> customer = next<CustomerOrder>(cfile);
  while(cfile->good()) {
      try {
	while(ofile->good() && lfile->good()) {
	  if (customer->c_custkey == order->o_custkey) {
	    if (order->o_orderkey == litem->l_orderkey) {
	      // Append lineitem
	      order->o_lineitems.push_back(move(litem));
	      litem = next<Lineitem>(lfile);
	    } else {
	      // Append order
	      customer->c_orders.push_back(move(order));
	      order = next<OrderLitem>(ofile);
	    }
	  } else if (customer->c_custkey < order->o_custkey) {
	    write(customer->toJson(), outFile);
	    customer.reset();
	    customer = next<CustomerOrder>(cfile);
	  } else {
	    order = next<OrderLitem>(ofile);
	  }
	}
	write(customer->toJson(), outFile);
	customer.reset();
	customer = next<CustomerOrder>(cfile);
    } catch (EOFReached &e) {continue;}
  }
}

void create_json_2collections(ifstream *ofile, ifstream *lfile, ofstream *outFile) {
  unique_ptr<Lineitem> litem = next<Lineitem>(lfile);
  unique_ptr<OrderLitem> order = next<OrderLitem>(ofile);
  while(ofile->good()) {
      try {
	while(lfile->good()) {
	  if (order->o_orderkey == litem->l_orderkey) {
	    // Append lineitem
	    order->o_lineitems.push_back(move(litem));
	    litem = next<Lineitem>(lfile);
	  } else if (order->o_orderkey < litem->l_orderkey) {
	    write(order->toJson(), outFile);
	    order.reset();
	    order = next<OrderLitem>(ofile);
	  } else {
	    litem = next<Lineitem>(lfile);
	  }
	}
	write(order->toJson(), outFile);
	order.reset();
	order = next<OrderLitem>(ofile);
    } catch (EOFReached &e) {continue;}
  }
}

template <class T> void create_json_3collections(ifstream *file, ofstream *outFile) {
  unique_ptr<T> record = next<T>(file);
  try {
    while (file->good()) {
      write(record->toJson(), outFile);
      record.reset();
      record = next<T>(file);
    }
  } catch (EOFReached &e) {}
}

void print_usage() {
  cout << "Arguments:" << endl <<
    "-m    Operation mode:" << endl <<
    "        " << CREATE_SINGLE << " produces a single json (no joins) based on the table selected" << endl <<
    "        " << CREATE_O_JOIN_L << " produces the json representation of orders join lineitem" << endl <<
    "        " << CREATE_C_JOIN_O_JOIN_L << " produces the json representation of customer join orders join lineitem" << endl <<
    "        " << CREATE_PSQL_JSON << " produces a postgresql compatible json" << endl <<
    "-c    Name of csv file containing customer" << endl <<
    "-o    Name of csv file containing orders" << endl <<
    "-l    Name of csv file containing lineitems" << endl <<
    "-r    Name of json file in which to store result" << endl <<
    "-h    Display this help message" << endl;
}

int main(int argc, char *argv[]) {
  const char *cfname = NULL;
  const char *ofname = NULL;
  const char *lfname = NULL;
  const char *outfname;
  int operation = -1;
  int c;
  while ((c = getopt(argc, argv, "m:c:o:l:r:h")) != -1) {
      switch (c) {
      case 'm':
	operation = atoi(optarg);
	break;
      case 'c':
	cfname = optarg;
	break;
      case 'o':
	ofname = optarg;
	break;
      case 'l':
	lfname = optarg;
	break;
      case 'r':
	outfname = optarg;
	break;
      case 'h':
	print_usage();
	exit(0);
      case ':':
	cerr << "Option -" << optopt << " requires an argument." << endl
	     << "Use -h to display a help message." << endl;
	exit(1);
      case '?':
	print_usage();
	exit(1);
      }
  }
  if ((operation == -1) 
      || (cfname == NULL && ofname == NULL && lfname == NULL)) {
    print_usage();
    exit(1);
  }
  ifstream cfile (cfname, ifstream::in);
  ifstream ofile (ofname, ifstream::in);
  ifstream lfile (lfname, ifstream::in);
  ofstream outFile;
  outFile.open(outfname, ios_base::app);
  Operation op;
  switch (operation) {
  case CREATE_SINGLE:
    op = CREATE_SINGLE;
    Record::context = &op;
    if (cfname != NULL) {
      create_json_3collections<Customer>(&cfile, &outFile);
    }
    if (ofname != NULL) {
      create_json_3collections<Order>(&ofile, &outFile);
    }
    if (lfname != NULL) {
      create_json_3collections<Lineitem>(&lfile, &outFile);
    }
    break;
  case CREATE_O_JOIN_L:
    op = CREATE_O_JOIN_L;
    Record::context = &op;
    create_json_2collections(&ofile, &lfile, &outFile);
    break;
  case CREATE_C_JOIN_O_JOIN_L:
    op = CREATE_C_JOIN_O_JOIN_L;
    Record::context = &op;
    create_json_1collection(&cfile, &ofile, &lfile, &outFile);
    break;
  case CREATE_PSQL_JSON:
    op = CREATE_PSQL_JSON;
    Record::context = &op;
    create_json_1collection(&cfile, &ofile, &lfile, &outFile);
    break;
  }
}
