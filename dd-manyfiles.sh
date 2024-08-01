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

declare -a CLIENTS=(10.193.67.225)

TARGET=/mnt/dir_11
ITERATIONS=10000000
BLOCKS=1
BLOCKSIZE=4KB
#FILESIZE = BLOCKS * BLOCKSIZE
FILESIZE=4K
EXTENSION=vhd
USER=root
#/dev/urandom or /dev/zero
DEV=/dev/urandom

# -------------------------------------------------------------------

TESTSCRIPT=`pwd`/$0
PROCS=$1

function test_master()
{
  NUM_CLIENTS=${#CLIENTS[*]}

  mkdir -p results
  RESULT_FILE=results/`date +%Y-%m-%dT%H:%M:%S`

  echo >$RESULT_FILE "# Starting at `date` with $PROCS processes across $NUM_CLIENTS clients, $ITERATIONS iterations, $BLOCKS MiB per file, $BLOCKSIZE blocksize, target path = $TARGET"

  echo "Starting clients..."
  n=0
  while [ $n -lt $PROCS ] ; do
    cnum=$(($n % $NUM_CLIENTS))
    ssh $USER@${CLIENTS[$cnum]} "$TESTSCRIPT $PROCS c${n} w" &
    n=$(($n + 1))
  done
  echo "Writing..."
  wait

 # n=0
 # while [ $n -lt $PROCS ] ; do
 #   cnum=$(($n % $NUM_CLIENTS))
 #   ssh $USER@${CLIENTS[$cnum]} "$TESTSCRIPT $PROCS c${n} r" &
 #   n=$(($n + 1))
 # done
 # echo "Reading..."
 # wait

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
      dd if=$DEV count=$BLOCKS bs=$BLOCKSIZE conv=fsync of=F${COUNT}-$FILESIZE.$EXTENSION >>$LOG 2>&1
    else
      dd if=F${COUNT}-$FILESIZE.$EXTENSION count=$BLOCKS bs=$BLOCKSIZE of=/dev/null >>$LOG 2>&1
    fi
    COUNT=$(($COUNT + 1))
  done
  T_FINISH=$SECONDS
}

if [ $# == 1 ] ; then
  test_master $1
elif [ $# == 3 ] ; then
  test_client $1 $2 $3
else
  echo "Usage: $0 <num_processes>"
  exit 1
fi
