#!/usr/local/bin/python
import httplib, urllib
import os
import time
import re
import logging as log
import sys
from htmldom import htmldom

# DB Column names
colNames =['id','date','com','stat','money','taxid','addr','note']

# A Chinese string for "Record Not Found"
no_data_rec_str = '\xe6\x9f\xa5\xe7\x84\xa1\xe7\x99\xbc\xe7\xa5\xa8\xe9\x96\x8b\xe7\xab\x8b\xe8\xb3\x87\xe6\x96\x99'

class NoRecord(Exception):
    """ Query Success, but no Data """
    pass
class NotCorrectFormat(Exception):
    """ Query Failure, unexpected format """
    pass
class NotFoundResult(Exception):
    """ Query Failure, captcha error, cookie incomplete"""
    pass

class HTMLDataResolver(object):

    def __init__(self):
        pass

    def parseUTF8(self,instr):
        """ transform the text """
        outstr = ""
        if instr.find("&#") < 0:
            return instr.strip()
        chrs = re.split("[;&#]", instr)
        for ch in chrs:
            try:
                outstr += unichr(int(ch))
            except ValueError:
                continue
            except:
                log.warn("Unknown unichr error")
        return outstr

    def findtheData(self,items):
        """ find the sequence of data """
        text = {}
        for i in range(0,items.length()):
            if re.match("^[a-zA-Z]{2}\d{8}$", items[i].text()) is not None:
                j = 0
                for col in colNames:
                    try:
                        field = self.parseUTF8(items[i+j].text())
                    except Exception as e:
                        if text['com'] == no_data_rec_str:
                            log.warn("Record not found")
                            raise NoRecord
                        else:
                            raise NotCorrectFormat
                    text[col]=field
                    j += 1
                return text
        log.warn("Not found the number in response HTML")
        raise NotFoundResult

    def resolve(self, content):
        """resolve the html dom"""
        dom = htmldom.HtmlDom().createDom(content)

        items = dom.find("table[class=lpTb] tr td")
        if items.length is 0:
            return {}

        try:
            data = self.findtheData(items)
        except NotFoundResult:
            data = None
        except NoRecord:
            data = {}
        except NotCorrectFormat:
            data = None
        return data


if __name__ == "__main__":
    """give a .html retrived from the www.einvoice.nat.gov.tw """
    log.basicConfig(level=log.DEBUG)
    if sys.argv[1] is not None:
        infile = sys.argv[1]

    with open(infile, "r") as inFd:
        content = inFd.read()
    resolver = HTMLDataResolver()
    res = resolver.resolve(content)
    if res is not None:
        if not bool(res):
            print "No Record"
        for k,r in res.iteritems():
            print k+":"+r
    else:
        print "NO DATA"
    #pass
