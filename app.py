import os
import json
import datetime
import re
import urlparse
import urllib
import requests
from flask import Flask, Response, render_template, request, abort
from flask.ext.cache import Cache

# Get environement variables
debug_app = 'DEBUG_APP' in os.environ

# Domain regex
domain_regex = '.*s3\.amazonaws\.com$'
if 'JSONPROXY_DOMAIN_WL_REGEX' in os.environ:
  domain_regex = os.environ['JSONPROXY_DOMAIN_WL_REGEX']
domain_regex = re.compile(domain_regex, re.I)

# Path regex
path_regex = '.*'
if 'JSONPROXY_PATH_WL_REGEX' in os.environ:
  path_regex = os.environ['JSONPROXY_PATH_WL_REGEX']
path_regex = re.compile(path_regex, re.I)

# Cache time (in minutes)
proxy_cache = 1
if 'JSONPROXY_CACHE' in os.environ:
  proxy_cache = int(os.environ['JSONPROXY_CACHE'])
  
  
# Other application wide variables
jsonp_header_overrides = {
  'content-type': 'text/javascript; charset=UTF-8',
  'Access-Control-Allow-Origin': '*'
}

# Make and configure the Flask app
app = Flask(__name__)
if debug_app:
  app.debug = True


# Set up cache
cache_config = {
  'CACHE_TYPE': 'filesystem',
  'CACHE_THRESHOLD': 1000,
  'CACHE_DIR': 'cache'
}
cache = Cache(config = cache_config)
cache.init_app(app, config = cache_config)



# Just a default route
@app.route('/')
@cache.cached(timeout = 500)
def index():
  return 'This is a whitelisted JSON to JSONP proxy.'
    

# Proxy route
@app.route('/proxy')
def handle_proxy():
  request_url = request.args.get('url', '')
  callback = request.args.get('callback', '')
  request_parsed = urlparse.urlparse(request_url)
  
  # Check to make sure we have the right sort of request
  if not request_url or not callback:
    abort(404)

  # Check if valid proxy url
  if not is_valid_url(request_parsed):
    abort(404)
  
  # Get value from proxied url (this is the cached part)
  proxy_request = make_proxy(request_url)
  if proxy_request['status_code'] != requests.codes.ok:
    abort(proxy_request['status_code'])
  
  # Wrap callback
  proxy_request['text'] = '%s(%s);' % (callback, proxy_request['text'])
  
  # Override some headers
  proxy_request['headers'] = dict(proxy_request['headers'].items() + jsonp_header_overrides.items())
  
  return Response(proxy_request['text'], proxy_request['status_code'], proxy_request['headers'])


# Get proxy URL and cache the results
@cache.memoize(proxy_cache * 60)
def make_proxy(url):
  if app.debug:
    print 'Cache missed: %s' % url

  r = requests.get(url)
  return {
    'text': r.text,
    'status_code': r.status_code,
    'headers': r.headers,
  }


# Check if valid key is in url
def is_valid_url(url_parsed):
  # Make sure the the domain and path pass the
  # check.
  found = True
  
  if app.debug:
    print 'Domain: %s' % url_parsed.netloc
    print 'Domain regex: %s' % domain_regex.pattern
    print 'Domain not match: %s' % (domain_regex.match(url_parsed.netloc) is None)
    print 'Path: %s' % url_parsed.path
    print 'Path regex: %s' % path_regex.pattern
    print 'Path not match: %s' % (path_regex.match(url_parsed.path) is None)
  
  # Check domain
  domain_match = domain_regex.match(url_parsed.netloc)
  if domain_match is None:
    found = False
  
  # Check path
  if found:
    path_match = path_regex.match(url_parsed.path)
    if path_match is None:
      found = False

  return found;


# Start Flask App
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)