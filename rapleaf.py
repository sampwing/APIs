from __future__ import division
from base64 import b64decode
from re import search, compile
from sys import exit
from urllib2 import urlopen

from BeautifulSoup import BeautifulSoup
from rapleafApi import RapleafApi

__version__ = "$Id: rapleaf.py,v 1.9 2012/02/17 00:17:20 sampwing Exp sampwing $"

class HTMLReader(object):
   """Wrapper for some BeautifulSoup functionality"""

   def __init__(self, text, url=True):
      """assumes that text contains a url unless otherwise specified by the flag"""
      if url: self.soup_html(text)
      else: self.soup_text(text)
   def soup_html(self, url):
      """create a soup by downloading remote html content"""
      raw_html = urlopen(url).read()
      self.soup = BeautifulSoup(raw_html)
   def soup_text(self, text):
      """create a soup from text containing html content"""
      self.soup = BeautifulSoup(text)
   def first_element(self, *params):
      """return just the first element matching the parameters"""
      return self.soup(params)[0]
   def get_elements(self, *params):
      """return all elements matching the parameters"""
      return self.soup(params)


class Records(object):
   """Dict-Dict object with some built in functionality"""

   def __init__(self):
      self.store = dict()
   def add(self, dictionary):
      """add elements of dictionary to store, create innerdicts when necessary"""
      for key, value in dictionary.iteritems():
         child = self.store.setdefault(key, dict())
         child[value] = child.setdefault(value, 0) + 1
   def count(self, key):
      child = self.store.setdefault(key, dict())
      return sum(child.values())
   def keys(self):
      return self.store.keys()
   def __str__(self, output=""):
      """generate a report like output from the contents of store"""
      for key, value in self.store.iteritems():
         output += "%s\n" % key
         records = self.count(key)
         child = self.store[key]
         for innerkey, innervalue in child.iteritems():
            output += "\t%s: %.2f%%\n" % (innerkey, innervalue / records * 100)
      return output


def ucsc_professor_statistics():
   """
   This will utilize the classes created above in combination with the rapleaf
   api.  It will navigate to my school's engineering department's faculty
   listing.  It will first parse out each professors email address, and then
   attempt to use the rapleaf api to gather information about them.  It will
   then place any information found into the Records class which will adjust
   to whatever type of result was found.  I believe that my api key only gives
   me access to age and gender. (Would be interesting to see what the other
   fields would reveal.)
   """
   api = RapleafApi.RapleafApi('d7485a1125c22bfe18799af7448bacd3')
   reader = HTMLReader("http://www.soe.ucsc.edu/people/faculty")
   records = Records()
   professors = reader.get_elements('script', {'type': 'text/javascript'})
   for professor in professors:
      message_encoded = search(r"\'(.*)\'", professor.text)
      if message_encoded == None: continue
      message = b64decode(message_encoded.group(1))
      reader.soup_text(message)
      email = reader.first_element('a').text
      response = api.query_by_email(email)
      if response: records.add(response)
   print "Statistics of Professors in the Engineering Dept. of UC Santa Cruz"
   print records

if __name__ == '__main__':
   exit(ucsc_professor_statistics())
