# [ARMs Race](https://app.hackthebox.com/challenges/ARMs%2520Race) Writeup [HTB]
_Reverse_

## Connecting to the service
Even though this is a reverse challenge, there aren't any downloadable files. So, I immediately connect to the server, and get this:
```
Level 1/50: 370301e3bb1b0ae3c8194fe3492b0de3ee2a45e3900100e0900200e0721a04e3d01143e3ba2208e38a2b44e3000060e2a81d01e34a1e45e32f2c08e3802049e3010080e00200a0e027170ce3c11541e31a250de3862647e3010080e1020080e1d31a0ee375104be3b82c05e3342641e3010000e0020000e07c140ee3351b48e3df2804e355254ae3900100e0900200e0581204e3af1747e3492c00e3912148e3900100e0900200e0a81a0ae331194ee36b2a05e3432943e3010040e00200c0e0b51e0ce3051f4be3e62903e3c9224be3010000e0020000e0a0110fe34d1545e3df2f00e3c52c43e3900100e0900200e00d130ee39f1d46e395200ae3fd2a4ae3010080e1020080e1791b09e3a5164de3fe2f0fe36e2b42e3000060e2471c0de3641e45e3642a0fe3852b4ee3900100e0900200e0ca1b02e3881d48e3c42002e3542c40e3010080e00200a0e0ca1703e348134ce3ff2d08e3b2294ce3010020e0020020e03c1302e3b7154be3582502e3b42f40e3000060e2621b0ce3a1184ae345250ee3802a4de3010000e0020000e08e130fe3581545e3e22c06e38b244ae3010080e1020080e1f31507e3411c45e3792809e3ee2341e3010080e00200a0e0e71208e3a91f45e36b2706e3db2041e3900100e0900200e0
Register r0:  
```
The name of the challenge suggests that the hexadecimal string might be some ARM machine code, which I have to emulate to return the content of `r0`.

I use `pwntools` to verify this claim:
```py
context.arch = 'arm'
hex_asm = '370301e3[...]900200e0' 
asm = bytes.fromhex(hex_asm)
print(disasm(asm))
```
When executing it, I get a valid assembly code!
```
  0:   e3010337        movw    r0, #4919       ; 0x1337
  4:   e30a1bbb        movw    r1, #43963      ; 0xabbb
  8:   e34f19c8        movt    r1, #63944      ; 0xf9c8
  c:   e30d2b49        movw    r2, #56137      ; 0xdb49
   ;   [...]
1c8:   e306276b        movw    r2, #26475      ; 0x676b
1cc:   e34120db        movt    r2, #4315       ; 0x10db
1d0:   e0000190        mul     r0, r0, r1
1d4:   e0000290        mul     r0, r0, r2
```

## Emulating the code
I've never emulated ARM code on Python, but I have no doubt that it exists a library just for that. A quick Google search returns me `unicorn`. So I set up the unicorn environment to emulate my code:
```py
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM
from unicorn.arm_const import UC_ARM_REG_R0

ARM_CODE = asm
ADDRESS = 0x1000
mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
mu.mem_map(ADDRESS, 4 * 1024 * 1024)
mu.mem_write(ADDRESS, ARM_CODE)
mu.emu_start(ADDRESS, ADDRESS + len(ARM_CODE))
r0 = mu.reg_read(UC_ARM_REG_R0)
```

## Automating the process
There are 50 levels to this challenge, and I have no intention to do this process manually for every level. Therefore, I take out my faithful [connect](../../utilities/connect.py) script, and modify it to automate the process. 

```py
from pwn import *
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM
from unicorn.arm_const import UC_ARM_REG_R0

def process(received_data):
    hex_arm = received_data.split()[2]
    asm = bytes.fromhex(hex_arm)
    ARM_CODE = asm
    ADDRESS = 0x1000
    mu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    mu.mem_map(ADDRESS, 4 * 1024 * 1024)
    mu.mem_write(ADDRESS, ARM_CODE)
    mu.emu_start(ADDRESS, ADDRESS + len(ARM_CODE))
    r0 = mu.reg_read(UC_ARM_REG_R0)
    return f'{r0}'

def main():
    sock = remote('94.237.49.212', 32435)
        
    for _ in range(50):
        # Receive data from the server until `Register r0:`
        received_data = sock.recvuntil(b"Register r0:", timeout=1).decode()
        print(f"{received_data}")
        
        # Process the received string
        processed_data = process(received_data)
    
        # Send the processed data back to the server
        sock.sendline(processed_data.encode())
        print(f"{processed_data}")
    
    # Receive flag
    print(sock.recvline_contains(b"HTB", timeout=1).decode())
        

if __name__ == "__main__":
    main()
```

And there you have it, the flag is mine!

## Read more!
[➡️ Next challenge: xorxorxor](./xorxorxor.md)