#!/bin/bash
WDIR="$PWD"
ODIR="$PWD/$$"
QUERIES_DIR="../../queries/tpch"
RUNS=5

PGDIR='/usr/pgsql-10/bin'
PGDATA='/var/lib/pgsql/10/data'
PGUSER='postgres'
PGSERVICE='postgresql-10'

function abort {
    local lineno=$1
    local msg=$2
    echo >&2 '
***************
*** ABORTED ***
***************
'
    echo "An error occurred at line $lineno:" >&2
    echo "$msg" >&2
    exit 1
}

function usage {
    echo "usage: $0 -q queries [-s sourcedir] [-o outdir] [-r runs]"
    echo "       $0 -h"
    echo
    echo "  -q queries     queries to run list of comma separated numbers. e.g. 3,4,12,13,22"
    echo "  -s sourcedir   path to directory from where to get queries"
    echo "                 filenames must match *qQUERYNUMBER(v[0-9]+)?_*"
    echo "                   e.g. File containing Q1:"
    echo "                        q1_something.sql"
    echo "                   e.g. File containing version 2 of Q1:"
    echo "                        q1v2_something.js"
    echo "                 (Default: $QUERIES_DIR)"
    echo "  -o outdir      path to directory to where results will be written"
    echo "                 (Default: Directory named after the process id)"
    echo "  -r runs        Runs per query. Used to compute average runtime"
    echo "                 (Default: $RUNS)"
    echo "  -r runs        Runs per query. Used to compute average runtime"
    echo "  -h             Print this mesage"
}

function drop_psql_cache {
    password=$1
    cd /tmp
    # Stop PostgreSQL server
    echo $password | sudo -S  -u $PGUSER $PGDIR/pg_ctl stop -D $PGDATA
    # Drop system caches
    echo $password | sudo -S  bash -c 'sync && echo 3 > /proc/sys/vm/drop_caches'
    # Restart server
    echo $password | sudo -S  systemctl start $PGSERVICE
    # Wait for server to restart
    while ! echo $password | sudo -S  -u $PGUSER $PGDIR/pg_ctl status -D $PGDATA | grep -q 'server is running'; do
	sleep 3
    done
    cd $WDIR
}

function drop_mongo_cache {
    password=$1
    cd /tmp
    echo $password | sudo -S  systemctl stop mongod
    # Drop system caches
    echo $password | sudo -S  bash -c 'sync && echo 3 > /proc/sys/vm/drop_caches'
    echo $password | sudo -S  systemctl start mongod
    cd $WDIR
}

q_selected=false
while getopts ":o:s:q:r:h" opt; do
    case $opt in
	o)
	    ODIR="$OPTARG"
	    ;;
	s)
	    QUERIES_DIR="$OPTARG"
	    ;;
	q)
	    q_selected=true
	    IFS=, read -a QUERIES_TO_RUN <<< "$OPTARG"
	    ;;
	r)
	    RUNS=$OPTARG
	    ;;
	h)
	    usage
	    ;;
	\?)
	    echo "Unknown option: -$OPTARG" >&2; exit 1;;
	:)
	    echo "Missing argument for option: -$OPTARG" >&2; exit 1;;
    esac
done

if ! $q_selected; then
    echo "Please specify the queries to be run (-q option)" >&2
    echo "Use option -h to print usage" >&2    
    exit 1
fi

mkdir -p $ODIR
if [ $? -ne 0 ]; then
    echo "Could not create output dir: $ODIR" >&2
    exit 1
fi

echo "Enter sudo password:"
read -s password
echo "Enter PGPASSWORD"
read -s pgpassword

trap 'abort ${LINENO} "$BASH_COMMAND"' ERR
set -e

for q in ${QUERIES_TO_RUN[@]}; do
    for file in `find "$QUERIES_DIR" -type f -regextype awk -regex ".*q${q}(v[0-9]+)?_.*"`; do
	bname=`basename $file`
	extension="${bname##*.}"
	fname="${bname%%.*}"
	case "$extension" in
	    "sql")
	    	for ((i = 0; i < RUNS; i++)); do
	    	    drop_psql_cache "$password"
	    	    PGPASSWORD=$pgpassword $PGDIR/psql -U `whoami` -h localhost -f "$file" >> "$ODIR/$fname.out" &
	    	    wait $!
	    	    echo -e "\n" >> "$ODIR/$fname.out"
	    	done
	    	wt=`awk '/Execution time/{sum += $3; n++} END {print sum/n}' "$ODIR/$fname.out"`
	    	;;
	    "js")
		for ((i = 0; i < RUNS; i++)); do
		    drop_mongo_cache "$password"
		    mongo --quiet "$file" >> "$ODIR/$fname.out" &
		    wait $!
		    echo -e "\n" >> "$ODIR/$fname.out"
		done
		wt=`awk -F'[:,]' '/executionTimeMillis"/{sum += $2; n++} END {print sum/n}' "$ODIR/$fname.out"`
		;;
        esac
	echo "$fname $wt" >> "$ODIR/results.csv"
    done
done
