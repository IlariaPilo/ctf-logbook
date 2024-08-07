# Tools

## Web

### nmap
A tool to scan the open ports, the services they expose and their versions. Versions are useful to look for known vulnerabilities and exploits.
```
nmap -p- -sC -sV -A --min-rate=5000 10.10.11.8
```

### feroxbuster
A tool to bruteforce directories in a website.
```
feroxbuster --url http://10.10.11.8:5000 -w ~/snap/feroxbuster/common/raft-medium-directories.txt                                    
```

### ffuf
A fuzzing tool that can be used to perform all kinds of exploration.
```
ffuf -w big.txt -u http://permx.htb -H "Host: FUZZ.permx.htb" -fw 18
```