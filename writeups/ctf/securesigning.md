# [Secure Signing](https://app.hackthebox.com/challenges/Secure%2520Signing) Writeup [HTB]
_Crypto_

## Analyzing the encryption
This challenge gives me access to yet another server. I can send messages to it, and get back a hash.
The computation logic of such a hash is quite straightforward:
```py
sha256(xor(message, FLAG)).digest()
```
Since the server uses a library implementation of `sha256`, I exclude the possibility of a vulnerability in it. However, the `xor` function is custom, and it looks like this:
```py
def xor(a, b):
    return bytes([i ^ j for i, j in zip(a, b)])
```
The choice of `zip` is very interesting, since if `a` and `b` have different lengths, the longer one will be cut to the length of the shorter one. This means that, for example:
```py
print(xor('HTB{',FLAG))
# b'\x00\x00\x00\x00'
```
Interesting, isn't it?

## Bruteforcing!!!
So, I already know the first 4 letters of the flag. Let's look at the fifth one. 

If I manage to guess it correctly, and if I send the 5-char flag as a message, the result of the xor will be `\x00\x00\x00\x00\x00`. Then, I'll get back the following hash:
```
Hash: 8855508aade16ec573d21e6a485dfd0a7624085c1a14b5ecdd6485de0c6839a4
```
This is great, since now I know what the hash of the first 5 letters looks like. I can append every single ASCII character after `HTB{`, one by one, and wait until I see the `\x00\x00\x00\x00\x00` hash. The letter that generated it is the correct fifth one!
```
Enter your message: HTB{q
Hash: 016a682d1df4f869b32c48b0a9b442a1493949fb85d951d121c1143bd3d5c1af
--> the hash is different, 'q' is wrong
Enter your message: HTB{r
Hash: 8855508aade16ec573d21e6a485dfd0a7624085c1a14b5ecdd6485de0c6839a4
--> the fifth letter is 'r'!
```

This approach can be iterated until the `}` character is found, and the flag is completed!
```py
from hashlib import sha256
from pwn import *
import string

sock = remote('94.237.59.63', 35718)

flag = 'HTB{'
zeros = b'\x00'*len(flag)
chars = string.printable[:-6]

for i in range(len(flag)+1,100):
    if len(flag)!=(i-1):
        # we didn't find a char in the previous iteration
        print('\n*panic*')
        exit(1)
    if flag[-1] == '}':
        # done
        print()
        exit(0)
    zeros += b'\x00'
    target_sha = sha256(zeros).digest().hex()
    # start bruteforcing this position
    for ch in chars:
        print(f'\r{flag}{ch}', end='', flush=True)
        # Fetch menu
        _ = sock.recvuntil(b">", timeout=1).decode()
        sock.sendline(b'1')
        # Enter message
        _ = sock.recvuntil(b":", timeout=1).decode()
        try_flag = flag + ch
        sock.sendline(try_flag.encode())
        # Get sha
        sha = sock.recvline_contains(b"Hash:", timeout=1).decode().split()[-1]
        if target_sha == sha:
            flag += ch
            break
```
