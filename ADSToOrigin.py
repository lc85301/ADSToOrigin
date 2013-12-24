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

  genoutname = lambda self,x : os.path.splitext(x)[0] + "_origin.txt"

  def __init__(self):
    self.data = []

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
    firstsec = True
    firstempty = False
    firstline = True
    infile = None

    try:
      infile = open(filename, mode='r')
      for line in infile:
        line = line.strip().strip('\n')
        if not line:
          if firstempty:
            firstempty = False
          else:
            if firstsec == True:
              firstsec = False
              self.data.append([copy.copy(x) for x in idxcol])
              del idxcol[:]
            self.data.append([copy.copy(x) for x in valcol]);
            del valcol[:]
        else:
          firstempty = True
          line = line.split()
          if firstsec == True:
            idxcol.append(line[-2])
          valcol.append(line[-1])
    except IOError:
			sys.stderr.write("can't open input ADS style file\n")
			sys.stderr.write("file %s doesn't exist\n" % (filename))
			return(1)
    finally:
      if infile is not None:
        infile.close()

  def writefile(self, filename):
    """write loaded data into output file"""
    try:
      outfile = open(filename, mode='w')
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

