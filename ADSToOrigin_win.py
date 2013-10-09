#!/usr/bin/env python2.7

import sys

def convert(filename):
	"""convert ADS export to multi column"""
	data = []
	first = True
	emptyLine = False
	infile = None
	outfile = None

	col1 = []
	col2 = []
	try:
		infile = open(filename, mode='r')
		for line in infile:
			line = line.strip()
			if not line:
				emptyLine = True
			else:
				if emptyLine == True:
					emptyLine = False
					if first == True:
						first = False
						data.append(col1)
						col1 = []
					data.append(col2)
					col2 = []
				line = line.strip('\n').split("\t")
				col1.append(line[0])
				col2.append(line[1])
		data.append(col2)
	except IOError:
		sys.stderr.write("can't open file\n")
		return(1)
	finally:
		if infile is not None:
			infile.close()

	outfilename = filename.rstrip(".txt") + "_origin.txt"
	try:
		outfile = open(outfilename, mode='w')
		for line in zip(*data):
			outfile.write("%s\n" %("\t".join(line)))
	except IOError:
		sys.stderr.write("can't open file\n")
		return(1)
	finally:
		if outfile is not None:
			outfile.close()

#if len(sys.argv) < 2:
#	sys.stderr.write("Usage: %s filename\n" % (sys.argv[0]))
#
#for name in sys.argv[1:]:
#	convert(name)
while 1:
	filename = raw_input("Please input the filename to convert(empty to end): ")
	if not filename:
		sys.exit(0)
	else: 
		filename = "./" + filename
		convert(filename)
