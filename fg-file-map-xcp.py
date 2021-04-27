##
# fg-file-map-xcp.py
#
# Copyright (c) 2021 NetApp Inc. - All Rights Reserved
# This sample code is provided AS IS, with no support or warranties of any kind, including but not limited to warranties of merchantability or fitness of any kind, expressed or implied.
#

# The run function allows this module to be called via xcp diag -run fgid.py
# Note: a quirk of running it this way is that the log file will be 'xcp.x1.log', and/or logging may not work right.
def run(argv):
	xcp.xcp(argv)

# TODO: implement in cython
def REVERSE32(i):
 	flip4 = [
		0x0,0x8,0x4,0xC,0x2,0xA,0x6,0xE,0x1,0x9,0x5,0xD,0x3,0xB,0x7,0xF
	]
	return (
		flip4[ i & 0xF ] << 28) | \
		(flip4[ (i>>4) & 0xF ] << 24) | \
		(flip4[ (i>>8) & 0xF ] << 20) | \
		(flip4[ (i>>12) & 0xF ] << 16) | \
		(flip4[ (i>>16) & 0xF ] << 12) | \
		(flip4[ (i>>20) & 0xF ] << 8) | \
		(flip4[ (i>>24) & 0xF ] << 4) | \
		(flip4[ (i>>28) & 0xF ]
	)

 
def fileid_to_msid(fileid):
	if ((fileid >> 32) == 0):
		return REVERSE32(fileid) & 0x0FFF

	return (fileid >> 32) & 0x0FFF

MAX_FGINDEX = 1000

def fgid(x):
	if not x.mount or not x.mount.root:
		return 0

	base_msid = fileid_to_msid(x.mount.root.a.fileid)
	msid = fileid_to_msid(x.a.fileid)

	if msid > base_msid:
		return min(msid - base_msid + 1, MAX_FGINDEX)
	if msid < base_msid:
		return min(base_msid - msid + 1, MAX_FGINDEX)
	return 1

if __name__ == "__main__":
	import sys
	for s in sys.argv[1:]:
		i = int(s, 0)
		print("s {} i {} msid {}".format(s, i, fileid_to_msid(i)))
else:
	# Modules from the xcp engine
	import xcp
	import xfilter

	# Add the function to the xfilter namespace for use in -match and -fmt
	xfilter.fgid = fgid
