# JSONProxy

A Python Flask based proxy to turn JSON endpoints into JSONP for cross-domain requests.  Meant to be easily deployed to Heroku.  Allows for caching and whitelisting.

## Similar applications

There are a number of similar applications, but most of them do not whitelist of requests or cache results.  Whitelisting is important as a wide-open proxy can easily be abused and cause damage to your own application as well as others.  Caching adds a bit of performance boost.

* http://jsonp.jit.su/
* https://github.com/okfn/dataproxy
* https://github.com/greenisus/jsonp-proxy
* https://github.com/mvanholstyn/jsonp-proxy
* https://github.com/clintandrewhall/node-jsonp-proxy
* https://github.com/TomDemeranville/jsonprox

## Install and run locally

1. (optional) Create a virtualenv
2. ```pip install -r requirements.txt```
3. Set domain whitelist regex (defaults to Amazon's S3 ```s3\.amazonaws\.com$```):  ```export JSONPROXY_DOMAIN_WL_REGEX='<REGEX>'```
3. Set path whitelist regex (defaults to open ```.```):  ```export JSONPROXY_PATH_WL_REGEX='<REGEX>'```
4. Set how many minutes to keep cached values (default is ```1```): ```export JSONPROXY_CACHE=<MINUTES>```
5. Run locally: ```python app.py```
6. Go to http://localhost:5000

## Deploy on Heroku

For Heroku.

1. Setup and install Heroku command line tools
1. Create Heroku app with whatever name you want: ```heroku apps:create <APP_NAME>```
3. Set domain whitelist regex (defaults to Amazon's S3 ```s3\.amazonaws\.com$```):  ```heroku config:set JSONPROXY_DOMAIN_WL_REGEX='<REGEX>'```
3. Set path whitelist regex (defaults to open ```.```):  ```heroku config:set JSONPROXY_PATH_WL_REGEX='<REGEX>'```
4. Set how many minutes to keep cached values (default is ```1```): ```heroku config:set JSONPROXY_CACHE=<MINUTES>```
1. Push up code: ```git push heroku master```
1. You can open the app with ```heroku open```
1. Use in your application by making a request like the following.  Make sure to encode the proxy url parameter. ```http://<APP_NAME>.herokuapp.com/proxy?callback=<CALLBACK_NAME>&url=https%3A//http://jsonip.com/```