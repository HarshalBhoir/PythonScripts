from bs4 import BeautifulSoup
import json
import requests
import urllib2

r  = urllib2.Request("http://api.fixer.io/latest")
response = json.load(urllib2.urlopen(r))
print response
print json.dumps(response,indent=2)
