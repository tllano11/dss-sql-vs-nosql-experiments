import sys
import os
import csv

class QFactory:
    class __QFactory:
        queries = {}
        def add(self, qname, query):
            self.queries[qname] = query
        def get(self, qname):
            return self.queries[qname]
    instance = None
    def __init__(self):
        if not QFactory.instance:
            QFactory.instance = QFactory.__QFactory()
    def __getattr__(self, name):
        return getattr(self.instance, name)

class Query:
    runtimes = {}
    def __init__(self, query):
        self.qnum, self.qtype, self.qver = self.__classify(query)
        
    def __classify(self, query):
        #parts = re.split('v|_', query)
        parts = query.split('_')
        qnumber = parts[0]
        qver = ''
        tmp = qnumber.split('v')
        if len(tmp) > 1:
            qnumber = tmp[0]
            qver = tmp[1]
        qtype = parts[-1]
        return qnumber, qtype, qver
    
    def set_runtime(self, size, runtime):
        self.runtimes[size] = runtime
        
def read(fname):
    global qfactory
    size = os.path.splitext(fname)[0]
    with open(fname) as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ')
        for row in csvreader:
            qname = row[0]
            runtime = float(row[1])
            query = Query(qname)
            query.set_runtime(size, runtime)
            qfactory.add(qname, query)

qfactory = None
def main(argv):
    global qfactory
    qfactory = QFactory()
    read(argv[1])
    print(qfactory.queries)

if __name__ == '__main__':
    main(sys.argv)
