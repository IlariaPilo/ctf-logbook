# [Golfer - Part 1](https://app.hackthebox.com/challenges/Golfer%2520-%2520Part%25201) Writeup [HTB]
[_Reverse_]

## Analyzing the executable
This challenge comes with a tiny executable file. I begin with the classic `strings` command, to see what's inside:
```sh
$ strings golfer 
a4fTUH}yR{l
g_30Br
```
It looks like the flag is there, but it's scrambled. I try to run the executable, but nothing happens. Time to disassemble with Ghidra!

## Patching the file
The disassembled code is pretty simple. At the beginning of the program, we jump to a function:
```assembly
0800004c e9 d6 00        JMP        FUN_08000127
         00 00
08000051 fe              ??         FEh
08000052 c3              ??         C3h
08000053 fe              ??         FEh
08000054 c2              ??         C2h
[...]

**************************************************************
*                        FUN_08000127                        *
**************************************************************  
08000127 30 c0           XOR        AL,AL
08000129 fe c0           INC        AL
0800012b b3 2a           MOV        BL,0x2a
0800012d cd 80           INT        0x80
0800012f 55              PUSH       EBP
08000130 89 e5           MOV        EBP,ESP
08000132 b0 04           MOV        AL,0x4
08000134 cd 80           INT        0x80
08000136 c9              LEAVE
08000137 c3              RET
```
This function is calling two system calls (`INT 0x80`), where the content of register AL is used to determine which system call is invoked (a list of values can be found [here](https://faculty.nps.edu/cseagle/assembly/sys_call.html)). More specifically, the register values for the first syscall are:
```assembly
XOR        AL,AL    ; AL = 0
INC        AL       ; AL++
MOV        BL,0x2a  ; BL = 42
INT        0x80
```
Now, system call number 1 is `exit()`. When we are invoking it, BL should store the exit code, meaning `FUN_08000127` is immediately calling `exit(42)` and the program ends.

This behavior is also confirmed by the fact that instructions after `JMP FUN_08000127` are never disassembled, meaning the dynamic disassembler doesn't reach that part of the code.

Since I don't want the program to immediately exit, I remove the `JMP FUN_08000127` instruction, patching it with 5 NOPs.

```assembly
; was
; 0800004c e9 d6 00        JMP        FUN_08000127
;          00 00
; now is
080004c 90              NOP    
080004d 90              NOP  
080004e 90              NOP  
080004f 90              NOP  
0800050 90              NOP    
```
I export the patched executable, run it and get the flag!

## Alternative solution: static analysis
It's also possible to solve this challenge by forcing Ghidra to disassemble the instructions after `JMP FUN_08000127`. This can be done by right-clicking on the first unknown instruction and choose the "Disassemble" option. After the code is disassembled, I analyze it and recover the content of the flag.

```assembly
INC        BL
INC        DL
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[1]
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_abiversion
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_flags
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[5]
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[3]
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+3
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[0]
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+1
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_version
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[4]
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+2
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+1
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_data
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+1
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+3
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[6]
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_osabi
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_shoff+2
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_flags+1
CALL       FUN_0800012f                                     
MOV        ECX,Elf32_Ehdr_08000000.e_ident_pad[2]
CALL       FUN_0800012f                                     
```

First thing first, I check the content of `FUN_0800012f`:
```assembly
0800012f 55              PUSH       EBP
08000130 89 e5           MOV        EBP,ESP
08000132 b0 04           MOV        AL,0x4
08000134 cd 80           INT        0x80
08000136 c9              LEAVE
08000137 c3              RET
```
Syscall 4 is `sys_write()`:
```c
sys_write(unsigned int fd, const char *buffer, size_t bytes);
// where
//  EBX <-- fd
//  ECX <-- buffer
//  EDX <-- bytes 
```
From the first lines of the code, we get that:
```assembly
INC        BL   ; fd = 1 (stdout)
INC        DL   ; bytes = 1
```
Overall, `FUN_0800012f` writes a single character on standard output. The character's address must be loaded in register `ECX`.

I check the code for the values of the characters:
```py
e_ident_pad = [0x55, 0x48, 0x7d, 0x79, 0x52, 0x7b, 0x6c]    # UH}yR{l
e_ident_abiversion = 0x54                                   # T
e_flags = [0x42, 0x72, 0xef, 0xbe]                          # Brï¾
e_shoff = [0x67, 0x5f, 0x33, 0x30]                          # g_30
e_ident_version = 0x34                                      # 4
e_ident_data = 0x61                                         # a
e_ident_osabi = 0x66                                        # f
```
Then, I just need to pick the correct characters and get the flag!
