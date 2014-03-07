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
  """A class that provide a easy tool, transfer
  ADS one column data to Origin style multi column data"""
  #member variable
  data = None 
  title = None
  charttype = None
  Z0 = 50
  smithsuffix = ["_real", "_imag"]
  pushChars = "<({["
  popChars = ">)}]"

  genoutname = lambda self,x : os.path.splitext(x)[0] + "_plot.txt"

  def __init__(self):
    self.data = []
    self.title = []
    self.charttype = "rectangle"

  def checkBalanced(self, token):
    stack = []
    for c in token:
      if c in self.pushChars:
        stack.append(c)
      elif c in self.popChars:
        if not len(stack):
          return False
        else:
          stackTop = stack.pop()
          balancingBracket = self.pushChars[self.popChars.index(c)]
          if stackTop != balancingBracket:
            return False
    return not stack

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
    self.title = []
    self.readfile(filename)
    outname = self.genoutname(filename)
    basename = os.path.basename(filename)

    #verify data
    datalength = len(self.data[0])
    identical = True
    for col in self.data[1:]:
      if datalength != len(col):
        identical = False
        break;
    if not identical:
      print("The data length in file %s is not identical" % (basename))
      print("Output file will be incorrect")

    #output file
    self.writefile(outname)

    print("convert %s, file type %s" % (basename, self.charttype))

  def readfile(self, filename):
    """readfile, read a block separated by blank line"""
    titlecol = []
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
            titlecol = self.processTitle(block[0], block[1], isFirstBlock)
            idxcol,valcol = self.processBlock(block[1:])
            if isFirstBlock:
              isFirstBlock = False
              self.data.append([copy.copy(x) for x in idxcol])
            if self.charttype == "rectangle":
              self.data.append([copy.copy(x) for x in valcol])
            elif self.charttype == "smith":
              self.data.append([copy.copy(x) for x in valcol[0]])
              self.data.append([copy.copy(x) for x in valcol[1]])
            self.title += titlecol
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

  def processTitle(self, line, dataline, isFirstBlock):
    validlist = []
    titlelist = []
    validname = ""
    # parse title
    # title is block[0][0]=block[1][0],block[0][1]=block[1][1]....
    # in smith chart format, we need to duplicate title for real / imaginary
    for token in line:
      validname += token
      if self.checkBalanced(validname):
        validlist.append(validname)
        validname = ""

    if len(validlist) == 2:
      if isFirstBlock:
        titlelist.append(validlist[0])
      if self.charttype == "rectangle":
        titlelist.append(validlist[1])
      elif self.charttype == "smith":
        for i in range(2):
          titlelist.append(validlist[1]+self.smithsuffix[i])
    elif len(validlist) > 2:
      token = []
      token.append(validlist[-1])
      if isFirstBlock:
        titlelist.append(validlist[-2])
      if self.charttype == "rectangle":
        for row0,row1 in zip(validlist[0:-2], dataline[0:-2]):
          token.append("%s=%s" % (row0, row1))
        titlelist.append(",".join(token))
      elif self.charttype == "smith":
        for row0,row1 in zip(validlist[0:-2], dataline[0:-2]):
          token.append("%s=%s" % (row0, row1))
        titlelist.append(",".join(token))

    return titlelist

  def processBlock(self, block):
    """read one block, and add item to idxlist and vallist"""
    # parse block
    idxlist = [ 0 for i in range(len(block))]
    if self.charttype == "rectangle":
      vallist = [ 0 for i in range(len(block))]
    elif self.charttype == "smith":
      vallist = [[0 for i in range(len(block))],[0 for i in range(len(block))]]

    # parse data, different behavior with rectangle or smith chart
    # in rectangle, simply use last two column as index and value column
    # in smith chart, we need to change magnitude / phase into real img 
    if self.charttype == "rectangle":
      for i in range(0,len(block)):
        idxlist[i] = block[i][-2]
        vallist[i] = block[i][-1]
    elif self.charttype == "smith":
      idxid = (len(block))/3
      for i in range(0, len(block)):
        idxlist[i] = block[i][0]
        vallist[0][i], vallist[1][i-1] = self.MP2RI(block[i][-3], block[i][-1])

    return idxlist,vallist

  def writefile(self, filename):
    """write loaded data into output file"""
    try:
      outfile = open(filename, mode='w')
      outfile.write("%s\n" % ("\t".join(self.title)))
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
