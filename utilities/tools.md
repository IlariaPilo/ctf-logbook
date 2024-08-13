# Tools

## Forensics

### volatility
A tool that can be used to navigate a memory dump. Volatility and forensics are almost synonyms! Here are some interesting links:
- [Guided quickstart](https://medium.com/@zemelusa/first-steps-to-volatile-memory-analysis-dcbd4d2d56a1);
- [File extraction](https://whiteheart0.medium.com/retrieving-files-from-memory-dump-34d9fa573033);
- [Cheatsheet](https://book.hacktricks.xyz/generic-methodologies-and-resources/basic-forensic-methodology/memory-dump-analysis/volatility-cheatsheet).

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
