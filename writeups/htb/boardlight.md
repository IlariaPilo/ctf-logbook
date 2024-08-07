# [BoardLight](https://app.hackthebox.com/machines/BoardLight) Writeup [HTB]
## 🧮 Usual enumeration
You get it, the first steps are always the same. 

I scan the exposed services using `nmap`, finding ports 22 (ssh) and 80 (http). 
The website presents the cybersecurity firm "BroadLight", and it's very similar to the [PermX](./permx.md) one (meaning that it's just an empty shell with no functionalities). 
However, the foot bar reveals the hostname to be `board.htb`, so I add it to the `/etc/hosts` file.

I then proceed with the classic `feroxbuster` run, hoping to discover some interesting content. The tool returns, among the already-known website pages, a suspicious `portfolio.php` file. 
The same file is hinted in an HTML comment, and trying to get it returns a weird _File not found_ message (which is different from the classic "404 Not Found" error page).

This whole `portfolio.php` situation looks worth investigating: I suspect the file actually exists, so I try to avoid the server (possible) checks by encoding the "portfolio.php" string in hexadecimal:
```
portfolio.php --> %70%6F%72%74%66%6F%6C%69%6F%2E%70%68%70
```
This doesn't work, as I keep getting the same message. After many attempts, I decide to let go and continue my enumeration.

Now that I know the hostname, I can run `ffuf` to look for possible subdomains. This is a good call, as I discover `crm.board.htb`!

## 🧠 ~~Getting the reverse shell~~ Losing my sanity [for 7 hours]
The `crm` subdomains is a Dolibarr login form, asking for username and password. The page is very kind, as it immediately tells me that the Dolibarr version is 17.0.0. 

A simple Google search returns a critical vulnerability for remote code execution, as well as its [POC](https://github.com/dollarboysushil/Dolibarr-17.0.0-Exploit-CVE-2023-30253). 
This vulnerability requires having low privilege access to Dolibarr. However, this is not a problem as the default `admin:admin` credentials work perfectly fine.

Now buckle up, because here is where it gets nasty! 

The Python exploit script doesn't seem to work. 
The website creation goes well, but attempting to make a new page triggers the request timeout. Trying to execute the exploit using the Dolibarr GUI is even less productive, as the server doesn't respond to any POST request.

After more than 5 hours spent on this issue, some gentle soul posts on the HTB official forum, sharing that the issue is actually the HTB VPN. 
1 hour and 9 VPN configurations later, I manage to find a working combination (*__SG FREE 1 with TCP__*), and the exploit works first try.

I finally have a shell!

## 🪪 Having an identity crisis
As per usual, I am now impersonating `www-data`. First thing first, I check which user I should become:
```sh
$ ls /home
larissa
```
I then start looking for the configuration file, hoping to find the `DB_PASSWORD` there. A quick internet search reveals that, in a Dolibarr application, this file can be found in `htdocs/conf/conf.php`. 

Sure enough, the password is exactly there!
```sh
$ cat ~/html/crm.board.htb/htdocs/conf/conf.php | grep pass
$dolibarr_main_db_pass='serverfun2$2023!!';
$ su - larissa
Password: serverfun2$2023!!
$ whoami
larissa
$ cat user.txt
<USER FLAG>
```

## 🔦 Finally seeing the light!
Now that I'm a proper user, I begin with searching for some `NOPASSWD` `sudo` permissions, but I don't find anything.

I then search for possible SUID files:
```sh
$ find / -perm -4000 -type f 2>/dev/null
/usr/lib/eject/dmcrypt-get-device
/usr/lib/xorg/Xorg.wrap
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_sys
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_ckpasswd
/usr/lib/x86_64-linux-gnu/enlightenment/utils/enlightenment_backlight
/usr/lib/x86_64-linux-gnu/enlightenment/modules/cpufreq/linux-gnu-x86_64-0.23.1/freqset
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign
/usr/sbin/pppd
/usr/bin/newgrp
/usr/bin/mount
/usr/bin/sudo
/usr/bin/su
/usr/bin/chfn
/usr/bin/umount
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/fusermount
/usr/bin/chsh
/usr/bin/vmware-user-suid-wrapper
```
Most of the results are classic scripts, but there is something interesting: a bunch of _enlightenment_ files. But wait, what was the name of the box again?

Since this looks suspicious to me, I decide to try [this exploit](https://github.com/MaherAzzouzi/CVE-2022-37706-LPE-exploit) for enlightenment. It works, and I get the flag!

## 🪦 Conclusions
The box was great for a noob like me! Big VPN L tho.

Thanks to @resort, who saved me from a fate of banging my head against a wall! xoxo
