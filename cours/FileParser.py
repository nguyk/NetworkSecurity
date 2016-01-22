#!/usr/bin/env python
# -*- coding: utf-8 -*-

from RightEntry import *

class FileParser:
#    def __init__(self): # Notre méthode constructeur                                                                                                                                                     
    def openFile(self):
        self.file = open("config.spatch", "r")
        self.content = self.file.read()

    def closeFile(self):
        self.file.close()

    def parse(self):
        rightsEntries = []
        contentArray = self.content.split("\n")
        for line in contentArray:
            lineArray = line.split("|")
            i = 0
            rightEntry = RightEntry()
            for element in lineArray:
                if i == 0:
                    rightEntry.username = element
                if i == 1:
                    rightEntry.server = element
                if i == 2:
                    rightEntry.read = element
                if i == 3:
                    rightEntry.write = element
                if i == 4:
                    rightEntry.execute = element
                    rightsEntries.append(rightEntry)
                i = i + 1
        return rightsEntries
