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
import math

class ADSToOrigin():
  """A clas that provide a easy tool, transfer
  ADS one column data to Origin style multi column data"""
  #member variable
  data = None 
  tital = None
  charttype = None
  genoutname = lambda self,x : os.path.splitext(x)[0] + "_plot.txt"

  def __init__(self):
    self.data = []
    self.tital = []
    self.charttype = "rectangle"
    self.Z0 = 50
    self.smithsuffix = ["_real", "_imag"]

  def MP2RI(self, magnitude, phase):
    """return real, imaginary part from magnitude, phase"""
    mag = float(magnitude)
    phz = float(phase) * math.pi / 180
    R = mag * math.cos(phz)
    X = mag * math.sin(phz)
    denom = (1-2*R+R**2+X**2)
    return str(self.Z0 * (1-R**2-X**2)/denom), str(self.Z0 * 2*X/denom)

  def convert(self, filename):
    """pack of read and write file"""
    self.data = []
    self.tital = []
    self.readfile(filename)

    #verify data
    datalength = len(self.data[0])
    identical = True
    for col in self.data[1:]:
      if datalength != len(col):
        identical = False
        break;
    if not identical:
      print("The data length in file %s is not identical" % (filename))
      print("Output file will be incorrect")

    #output file
    outname = self.genoutname(filename)
    self.writefile(outname)

  def readfile(self, filename):
    """readfile, read a block separated by blank line"""
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
        if self.charttype == "rectangle" and line.find('/') != -1:
          self.charttype = "smith"

        line = line.strip().strip('\n').split()
        if not line:
          if hasData:
            titalcol,idxcol,valcol = self.processBlock(block, isFirstBlock)
            if isFirstBlock:
              isFirstBlock = False
              self.data.append([copy.copy(x) for x in idxcol])
            if self.charttype == "rectangle":
              self.data.append([copy.copy(x) for x in valcol])
            elif self.charttype == "smith":
              self.data.append([copy.copy(x) for x in valcol[0]])
              self.data.append([copy.copy(x) for x in valcol[1]])
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
      print("convert %s, file type %s" % (filename, self.charttype))
      if infile is not None:
        infile.close()

  def processBlock(self, block, isFirstBlock):
    """read one block, and add item to titallist, idxlist and vallist"""
    # parse block
    # tital is block[0][0]=block[1][0],block[0][1]=block[1][1]....
    idxlist = [ 0 for i in range(len(block)-1)]
    if self.charttype == "rectangle":
      vallist = [ 0 for i in range(len(block)-1)]
    elif self.charttype == "smith":
      vallist = [[0 for i in range(len(block)-1)],[0 for i in range(len(block)-1)]]
    titallist = []

    # parse tital
    # tital is block[0][0]=block[1][0],block[0][1]=block[1][1]....
    # in smith chart format, we need to duplicate tital for real / imaginary
    # and duplicate tital 
    if len(block[0]) <2:
      sys.stderr.write("There are some error in this ADS file")
    elif len(block[0]) == 2:
      if isFirstBlock:
        titallist.append(block[0][0])
      if self.charttype == "rectangle":
        titallist.append(block[0][1])
      elif self.charttype == "smith":
        titallist.append("\t".join(block[0][1]+self.smithsuffix[i] for i in range(2)))
      tital = "\t".join(titallist)
    elif len(block[0]) > 2:
      if self.charttype == "rectangle":
        for row0,row1 in zip(block[0][0:-2], block[1][0:-2]):
          titallist.append("%s=%s" % (row0, row1))
        tital = ",".join(titallist)
      elif self.charttype == "smith":
        for row0,row1 in zip(block[0][0:-2], block[1][0:-2]):
          titallist.append("%s=%s" % (row0, row1))
        titalstem = ",".join(titallist)
        tital = "\t".join(titalstem+self.smithsuffix[i] for i in range(2))
      if isFirstBlock:
        tital = ("%s " %(block[0][-2])) + tital 
    
    # parse data, different behavior with rectangle or smith chart
    # in rectangle, simply use last two column as index and value column
    # in smith chart, we need to change magnitude / phase into real img 
    if self.charttype == "rectangle":
      for i in range(1,len(block)):
        idxlist[i-1] = block[i][-2]
        vallist[i-1] = block[i][-1]
    elif self.charttype == "smith":
      idxid = (len(block)-1)/3
      for i in range(1, len(block)):
        idxlist[i-1] = block[i][0]
        vallist[0][i-1], vallist[1][i-1] = self.MP2RI(block[i][-3], block[i][-1])

    return tital,idxlist,vallist

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
  raw_input("convert complete. (Press any key to continue...)\n")
