#!/usr/bin/env python2.7

#----------------------------------------------------------------------------------
#-*- coding: utf-8 -*-
# 
# Filename: ADSToOrigin
#
# Copyright (C) 2013 -  You-Tang Lee (YodaLee) <lc85301@gmail.com>
# All Rights reserved.
#
# This file is part of project: ADSToOrigin.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#---------------------------------------------------------------------------------

import sys
import os.path
import copy

class ADSToOrigin():
  """A clas that provide a easy tool, transfer
  ADS one column data to Origin style multi column data"""
  #member variable
  data = None 
  tital = None

  genoutname = lambda self,x : os.path.splitext(x)[0] + "_origin.txt"

  def __init__(self):
    self.data = []
    self.tital = []

  def prompt(self,):
		"""prompt ask user input file name, then call convert
		to generate new-style file """
		while True:
			filename = raw_input("Please input the filename to convert(empty to exit): ")
			if not filename :
				sys.exit(0)
			else:
				filename = "./" + filename
				self.history.append(filename)
				self.convert(filename)

  def convert(self, filename):
    """pack of read and write file"""
    self.readfile(filename)
    print(self.tital)
    outname = self.genoutname(filename)
    self.writefile(outname)

  def readfile(self, filename):
    """read file into list, ADS file is record in following format
    sweepvar1 ... sweepvar_n-1 sweepvarn ... data
    var1_1    ... varn-1_1     varn_1    ... data_1
    var1_1    ... varn-1_1     varn_2    ... data_2
    var1_1    ... varn-1_1     varn_3    ... data_3
    ...           
    var1_1    ... varn-1_1     varn_m    ... data_m
    
    sweepvar1 ... sweepvar_n-1 sweepvarn ... data
    var1_1    ... varn-1_2     varn_1    ... data_1
    var1_1    ... varn-1_2     varn_2    ... data_2
    var1_1    ... varn-1_2     varn_3    ... data_3
    ...           
    var1_1    ... varn-1_2     varn_m    ... data_m
    """
    titalcol = []
    idxcol = []
    valcol = []
    infile = None
    hasData = False
    isFirstBlock = True
    block = []

    try:
      infile = open(filename, mode='r')
      for line in infile:
        line = line.strip().strip('\n').split()
        if not line:
          if hasData:
            titalcol,idxcol,valcol = self.processBlock(block, isFirstBlock)
            if isFirstBlock:
              isFirstBlock = False
              self.data.append([copy.copy(x) for x in idxcol])
            self.data.append([copy.copy(x) for x in valcol])
            self.tital.append(titalcol)
            hasData = False
            del block[:]
            del idxcol[:]
            del valcol[:]
        else:
          hasData = True
          block.append(line)
    except IOError:
			sys.stderr.write("can't open input ADS style file\n")
			sys.stderr.write("file %s doesn't exist\n" % (filename))
			return(1)
    finally:
      if infile is not None:
        infile.close()

  def processBlock(self, block, isFirstBlock):
    """read one block, and add item to titalcol, idxcol and valcol"""
    # parse block
    # tital is block[0][0]=block[1][0],block[0][1]=block[1][1]....
    idxlist = [ 0 for i in range(len(block)-1)]
    vallist = [ 0 for i in range(len(block)-1)]
    titallist = []
    if len(block[0]) <2:
      sys.stderr.write("There are some error in this ADS file")
    elif len(block[0]) == 2:
      if isFirstBlock:
        titallist.append(block[0][0])
      titallist.append(block[0][1])
      tital = " ".join(titallist)
    elif len(block[0]) > 2:
      for i,(row0,row1) in enumerate(zip(block[0][0:-2], block[1][0:-2])):
        titallist.append("%s=%s" % (row0, row1))
      tital = ",".join(titallist)
      if isFirstBlock:
        tital = ("%s " %(block[0][-2])) + tital 
    for i in range(1,len(block)):
      idxlist[i-1] = block[i][-2]
      vallist[i-1] = block[i][-1]

    return tital,idxlist, vallist

  def writefile(self, filename):
    """write loaded data into output file"""
    try:
      outfile = open(filename, mode='w')
      outfile.write("%s\n" % ("\t".join(self.tital)))
      for line in zip(*(self.data)):
        outfile.write("%s\n" %("\t".join(line)))
    except IOError:
      sys.stderr.write("can't open output Origin style file\n")
      sys.stderr.write("file %s doesn't exist\n" % (outfilename))
      return(1)
    finally:
      if outfile is not None:
        outfile.close()

if __name__ == '__main__':
  converter = ADSToOrigin()
  for inarg in sys.argv[1:]:
    converter.convert(inarg)
  #converter.prompt()

