#This script creates [n] top level directories, [n] sub directories and 10 files per directory.
#Adjust the directory counts using the topdircount and subdircount variables.

#!/usr/bin/python
from multiprocessing import Process
import os, datetime,platform, time,argparse, socket
topdircount = 1000
subdircount = 100
dircount = topdircount*subdircount
filecount = dircount*10
totalcount = dircount+filecount

#This prints out how many directories and files we create in the script
print("Directories:")
print(dircount)

print("Files:")
print(filecount)

print("Total files and folders:")
print(totalcount)

def command_line():
    parser = argparse.ArgumentParser(prog='usaf_fg.py',description='%(prog)s is used to create a high filecount directory structure for the usaf')
    parser.add_argument('topdir', type=str, help='Enter a valid top level directory from which new directories will dangle')
    arg = vars(parser.parse_args())

    #Error if aws aws and onprem and azure are set, only one is allowed
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
    for basedir in range(0,topdircount):
       dir=topdir + '/topdir_' + str(basedir)
       p = Process(target=sub_dir,args=(dir,))
       process_list.append(p)

    start=time.time()
    print('Starting overall work: %s' % (datetime.datetime.now()))
    for element in process_list:
        element.start()

    for element in process_list:
        element.join()
    print('End overall work: %s' % (datetime.datetime.now()))
    print('total time: %s' % (time.time() - start))


def sub_dir(topdir):
    os.mkdir(topdir)
    os.chdir(topdir)
    for subdir in range(0,subdircount):
        os.mkdir(topdir + '/subdir_' + str(subdir))
        os.chdir(topdir + '/subdir_' + str(subdir))
        f1 = open('file1', 'w')
        f2 = open('file2', 'w')
        f3 = open('file3', 'w')
        f4 = open('file4', 'w')
        f5 = open('file5', 'w')
        f6 = open('file6', 'w')
        f7 = open('file7', 'w')
        f8 = open('file8', 'w')
        f9 = open('file9', 'w')
        f10 = open('file10', 'w')
        f1.write(topdir + '\n')
        f2.write(topdir + '/subdir_' + str(subdir) + '\n')
        f3.write(str(datetime.datetime.now()) + '\n')
        f4.write(platform.uname()[0] + '\n')
        f5.write(socket.gethostname() + '\n')
        f6.write(topdir + '\n')
        f7.write(topdir + '/subdir_' + str(subdir) + '\n')
        f8.write(str(datetime.datetime.now()) + '\n')
        f9.write(platform.uname()[0] + '\n')
        f10.write(socket.gethostname() + '\n')
        f1.close()
        f2.close()
        f3.close()
        f4.close()
        f5.close()
        f6.close()
        f7.close()
        f8.close()
        f9.close()
        f10.close()


multiproc(command_line())
