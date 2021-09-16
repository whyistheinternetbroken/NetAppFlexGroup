#!/usr/bin/python
from multiprocessing import Process
import os, datetime,platform, time,argparse, socket, subprocess

# How many files per folder?
filecount = 1

# How many directories? This will also be the number of simultaneous processes that run.
dircount = 2

# Blocksize for dd (use friendly values like 1MB, 4KB, etc... this impacts file names)
blocksize = "64K"
# Number of blocks
n = "163840"
# Output file name
outputfile = "/disk"
# /dev/urandom (random data written for "real" space usage) or /dev/null
inputfile = "/dev/urandom"

extension = "vhd"

print()
print("=======================================================")
print("Directories per client to be created: " + str(dircount))
print("Files per client to be created: " + str(dircount*filecount) + " (" + str(filecount) + " per directory)")
print("Total files and folders per client: " + str(dircount*filecount+dircount))
print("Client: " + socket.gethostname())
print("=======================================================")
print()
print()

def command_line():
    parser = argparse.ArgumentParser(prog='hfc.py',description='%(prog)s is used to create high file counts with a single top level directory structure for FlexGroup testing')
    parser.add_argument('topdir', type=str, help='Enter a valid top level directory from which new files will dangle')
    arg = vars(parser.parse_args())

    if not (os.path.isdir(arg['topdir'])):
        print ('\n\n\tError: The entered topdir %s does not exist, plase remedy and try again\n\n' % (arg['topdir']))
        quit()
    if arg['topdir'][-1] == '/':
        topdir = arg['topdir'][0:-1]
    else:
        topdir = arg['topdir']
    return topdir

def multiproc(topdir):
    process_list=[]
    for basedir in range(0,dircount):
       targetdir=topdir + '/dir_' + str(basedir)
       p = Process(target=files,args=(targetdir,))
       process_list.append(p)

    start=time.time()
    print()
    print("===================================================")
    print('Starting overall work: %s' % (datetime.datetime.now()))
    print("===================================================")
    print()
    for element in process_list:
        element.start()

    for element in process_list:
        element.join()
    print()
    print("===================================================")
    print('End overall work: %s' % (datetime.datetime.now()))
    print('Total time: %s' % (time.time() - start))
    print("Client: " + socket.gethostname())
    print("===================================================")
    print()

def files(topdir):
 os.mkdir(topdir)
 os.chdir(topdir)
 for item in range(0,filecount):
##Higher ops, more getattrs
#  with open("moarfiles{}.txt".format(item), "w") as f:
#   num_chars = 256
#   f.write('All work no play' * num_chars)
## Fewer getattrs, dd operation
   subprocess.run(["dd", "if=" + inputfile, "of=" + topdir + outputfile + blocksize + "_" + str(item) + "." + extension, "bs=" + blocksize, "count=" + n, "status=none"])

multiproc(command_line())
