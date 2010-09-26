#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import re
import urllib
from urlparse import urlparse

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db

class Selector(db.Model):
  domain = db.StringProperty(required=True)
  pathReg = db.StringProperty(required=True)
  value = db.StringProperty(required=True)

  @staticmethod
  def findByUrl(url):
    url = urlparse(url)
    selectors = db.Query(Selector).filter('domain =', url.netloc)
    matches = [selector for selector in selectors
      if re.compile(selector.pathReg).match(url.path)]

    if len(matches) > 0:
      return matches[0]
    else:
      return None
    
class SelectorListHandler(webapp.RequestHandler):
  def get(self):
    selectors = Selector.all().fetch(limit=20)
    self.response.out.write(template.render(
      os.path.join(os.path.dirname(__file__), 'templates', 'list.html'),
      {'selectors': selectors}
    ))

  def post(self):
    domain = self.request.get('domain')
    pathReg = self.request.get('pathReg')
    value = self.request.get('value')
    selector = Selector(domain=domain,
                        pathReg=pathReg,
                        value=value)
    selector.put()
    self.redirect('/maindish')
    
class GetMainContentHandler(webapp.RequestHandler):
  def get(self, url):
    url = urllib.unquote_plus(url)
    selector = Selector.findByUrl(url)

    if(selector):
      self.response.out.write(selector.value)
    else:
      self.error(404)

def main():
  application = webapp.WSGIApplication([
        ('/maindish', SelectorListHandler),
        (r'/maindish/(.*)', GetMainContentHandler)
      ], debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
