# Created by Chad Morgenstern, Sr. Performance Systems Engineer, NetApp
# No official support for this script
#!/usr/bin/python
from multiprocessing import Process
import os, datetime,platform, time,argparse, socket
 
 
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
    for basedir in range(0,1000):
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
    for subdir in range(0,1000):
        os.mkdir(topdir + '/subdir_' + str(subdir))
        os.chdir(topdir + '/subdir_' + str(subdir))
        for item in range(0,5000000):
                with open("shining{}.txt".format(item), "w") as f:
                        f.write("All work and no play make Jack a dull boy")
                        f.close()
 
multiproc(command_line())
