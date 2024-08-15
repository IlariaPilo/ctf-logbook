# [xorxorxor](https://app.hackthebox.com/challenges/xorxorxor) Writeup [HTB]
_Crypto_

## Analyzing the encryption
So. I'm _terrible_ at crypto challenges. So terrible that I decided to start with the challenge with most solves. 
And you are reading this, you know I managed!

Let's start with the basics. The challenge provides the encryption Python code, as well as the file containing the ciphertext flag.
The encryption is very basic:
```py
class XOR:
    def __init__(self):
        # four random bytes
        self.key = os.urandom(4)
    def encrypt(self, data: bytes) -> bytes:
        xored = b''
        for i in range(len(data)):
            xored += bytes([data[i] ^ self.key[i % len(self.key)]])
        return xored
    def decrypt(self, data: bytes) -> bytes:
        return self.encrypt(data)
```
Each byte of the flag is xored with the corresponding byte of the key. Since the key has only 4 bytes, we use each byte cyclically (byte 0 of the key is used for bytes 0, 4, 8, ... of the flag).

### Recovering the flag
Even though I know nothing about crypto, I'm aware of this xor property:
```
xor_b = flag_b ^ key_b
(flag_b ^ xor_b) == key_b 
```
This means that, if I knew 4 consecutive bytes of the flag, we could recover the key and decode the whole message. Too bad I don't have them...or do I?

Well, since all flags start with `HTB{`, I have just enough information to recover the key:
```py
def key_recovery():
    flag = 'HTB{'.encode()
    ciphertext_first_4 = b'\x13\x4a\xf6\xe1'
    key = b''
    for i in range(4):
        key += bytes([flag[i]^ciphertext_first_4[i]])
    return key
```
I just set the key to this value, run the already provided `decode` function and get the flag!

## Read more!
[➡️ Next challenge: Secure Signing](./securesigning.md)