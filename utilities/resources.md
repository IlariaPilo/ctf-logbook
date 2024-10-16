## AI - ML
If you need to gaslight some AI model, look no further!
- [Prompt injection cheat sheet](https://blog.seclify.com/prompt-injection-cheat-sheet/) → start here;
- [The Big Prompt Library](https://github.com/0xeb/TheBigPromptLibrary).

## Crypto

### RSA




## pwn

### ret2libc
Disable ASLR (until reboot):
```sh
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
```
Run with a given libc instance:
```sh
# run
LD_PRELOAD=./libc.so.6 ./chall
# debug
gdb chall
gef➤  set environment LD_PRELOAD=./libc.so.6
gef➤  run
```
Step-by-step tutorials:
- [32-bit Linux, no ASLR](https://www.ired.team/offensive-security/code-injection-process-injection/binary-exploitation/return-to-libc-ret2libc);
- [64-bit Linux, no ASLR](https://blog.techorganic.com/2015/04/21/64-bit-linux-stack-smashing-tutorial-part-2/);
- [64-bit Linux, ASLR](https://corruptedprotocol.medium.com/h-cktivitycon-2021-ctf-the-library-ret2libc-aslr-bypass-a83a8207f237).

## Web

