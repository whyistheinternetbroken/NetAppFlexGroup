#!/bin/bash
set -e
# set -x

# Edit these parameters as needed. The testbed must be configured to allow
# passwordless SSH from the master client to the other clients. This script
# must be installed at the same path on each client.
# A 'results' subdirectory will be created on the master client. Fields in
# the ouptput file are: client, direction, MiB/s rate, total seconds
#
# The script takes one parameter for the number of processes. This number
# may be larger than the number of clients.
#
# This script is intended to provide a proper method for testing a single threaded operation (such as dd) to
# more accurately measure the performance and capabilities of a NetApp FlexGroup volume.
#
# Run this script against a FlexVol volume for comparison.

declare -a CLIENTS=(client1,client2,client3)
# Change the values in {brackets} to desired values. Remove brackets.

TARGET={/path}
ITERATIONS={N}
BLOCKS={N for blocks}
# Block size is 1 MiB

# -------------------------------------------------------------------

TESTSCRIPT=`pwd`/$0
PROCS=$1

function test_master()
{
  NUM_CLIENTS=${#CLIENTS[*]}

  mkdir -p results
  RESULT_FILE=results/`date +%Y-%m-%dT%H:%M:%S`

  echo >$RESULT_FILE "# Starting at `date` with $PROCS processes across $NUM_CLIENTS clients, $ITERATIONS iterations, $BLOCKS MiB per file, target path = $TARGET"

  echo "Starting clients..."
  n=0
  while [ $n -lt $PROCS ] ; do
    cnum=$(($n % $NUM_CLIENTS))
    ssh ${CLIENTS[$cnum]} "$TESTSCRIPT $PROCS c${n} w" &
    n=$(($n + 1))
  done
  echo "Writing..."
  wait

  n=0
  while [ $n -lt $PROCS ] ; do
    cnum=$(($n % $NUM_CLIENTS))
    ssh ${CLIENTS[$cnum]} "$TESTSCRIPT $PROCS c${n} r" &
    n=$(($n + 1))
  done
  echo "Reading..."
  wait

  echo "Collecting results..."
  n=0
  while [ $n -lt $PROCS ] ; do
    cat $TARGET/c${n}/c${n}.out >>$RESULT_FILE
    n=$(($n + 1))
  done
  awk 'BEGIN { FS="," } NR > 1 { if($2=="r") { r=r+$3; nr++; } else { w=w+$3; nw++; } } END { print "#Average MiB/s: read",r/nr,"write",w/nw}' $RESULT_FILE >>$RESULT_FILE
  echo "Done"
}


function test_client()
{
  CLIENT_ID=$2
  RW=$3

  MYDIR=$TARGET/$CLIENT_ID
  mkdir -p $MYDIR
  LOG=$MYDIR/$CLIENT_ID.log
  OUT=$MYDIR/$CLIENT_ID.out

  if [ $RW == "w" ] ; then
    > $LOG
    > $OUT
  fi

  COUNT=1

  T_START=$SECONDS
  cd $MYDIR

  while [ $COUNT -le $ITERATIONS ] ; do
    if [ $RW == "w" ] ; then
      dd if=/dev/zero bs=1048576 count=$BLOCKS conv=fsync of=F${COUNT}.dat >>$LOG 2>&1
    else
      dd if=F${COUNT}.dat bs=1048576 count=$BLOCKS of=/dev/null >>$LOG 2>&1
    fi
    COUNT=$(($COUNT + 1))
  done
  T_FINISH=$SECONDS
  echo >> $OUT "$CLIENT_ID,$RW,$(( ($BLOCKS * $ITERATIONS) / ($T_FINISH - $T_START) )),$(($T_FINISH - $T_START))"

  if [ $RW == "r" ] ; then
    # cleanup
    rm -f F*.dat
  fi
}

if [ $# == 1 ] ; then
  test_master $1
elif [ $# == 3 ] ; then
  test_client $1 $2 $3
else
  echo "Usage: $0 <num_processes>"
  exit 1
fi
