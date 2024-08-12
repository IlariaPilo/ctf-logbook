# [Encryption Bot](https://app.hackthebox.com/challenges/encryption-bot) Writeup [HTB]
_Reverse_

## Analyzing the files
The challenge provides an executable file, together with what's likely the encrypted flag.

To know more about the nature of the program, I run the classic:
```sh
$ strings chall
[...]
This is the real flag :
HTB{I_4M_R3v3rse_EnG1ne3eR}
```
I have very low hopes, but I still try to input the flag in HTB. Clearly, it's wrong. Time to open my faithful Ghidra!

## Studying the encryption
Even though the file is stripped, identifying the `main` isn't a huge problem. I study its content and rename variables and functions for the sake of clarity. I also remove some function calls that do nothing.

```c
int main() {
    undefined text_to_encrypt [32];
    FILE *DATA_FP;
    
    print_logo();
    printf("\n\nEnter the text to encrypt : ");
    __isoc99_scanf(&DAT_0010230f,text_to_encrypt);

    // if `data.dat` exists, remove it
    DATA_FP = fopen("data.dat","r");
    if (DATA_FP != (FILE *)0x0) {
        system("rm data.dat");
    }
    // check if the text to encrypt is 27 characters long
    // if not, exit
    is_len_1b(text_to_encrypt);

    iterate_and_encrypt(text_to_encrypt);
    encrypt_p2();

    system("rm data.dat");

    return 0;
}
```
It looks like the encryption logic is separated in two functions, which I call `iterate_and_encrypt` and `encrypt_p2`. Let's look more into them.

### `iterate_and_encrypt`
Similarly to `main`, I rename variables and remove useless code to improve readability.
```c
void iterate_and_encrypt(char *cleartext) {
    size_t len;
    int cleartext_int [31];
    int i;
    
    // for each character of `cleartext`, convert it into an integer
    // and pass it to the `encrypt` function
    i = 0;
    while( true ) {
        len = strlen(cleartext);
        if (len <= i) break;
        cleartext_int[i] = (int)cleartext[i];
        encrypt(cleartext_int[i]);
        i = i + 1;
    }
}

void encrypt(int ch_int) {
    uint bin [20];
    FILE *DATA_FP;
    int i, j;
    
    DATA_FP = fopen("data.dat","a");
    // convert `ch_int` in its binary representation, little endian
    // e.g. 4 --> [0, 0, 1, 0, 0, 0, 0, 0]
    for (i=0; i<8; i++) {
        bin[i] = ch_int % 2;
        ch_int = ch_int / 2;
    }
    // append it to `data.dat`, big endian
    for (j=7; j>-1; j--) {
        fprintf(DATA_FP,"%d",(ulong)bin[j]);
    }
    fclose(DATA_FP);
}
```
Overall, this function converts the cleartext into binary, and dumps it on the `data.dat` file using a big endian representation. Notice that, since the cleartext has necessarily 27 characters, the size of `data.dat` will be of 27*8 = 216 B.

### `encrypt_p2`
In my opinion, this is the most complex function of the program.

```c
void encrypt_p2() {
    int buf [400];
    int i, j, pow_j, i_6, idx;
    char O_or_1;
    FILE *DATA_FP;
    
    DATA_FP = fopen("data.dat","r+");

    // for each character in `data.dat`
    // (notice we know they are exactly 216)
    for (i=1; i<217; i++) {
        // first, we convert them to actual digits
        O_or_1 = (char)fgetc(DATA_FP);
        if (O_or_1 == '0')
            buf[i-1] = 0;
        else if (O_or_1 == '1')
            buf[i-1] = 1;
        // every 6 characters, consider the last processed batch (big
        // endian) and convert it to its decimal representation `idx`
        // then, pass `idx` to the `weird_pointer_stuff` function
        if (i % 6 == 0) {
            idx = 0;
            i_6 = i-1;
            for (j=0; j<6; i_6--, j++) {
                pow_j = pow2(j);
                idx = idx + buf[i_6] * pow_j;
            }
            weird_pointer_stuff(idx);
        }
    }
    fclose(DATA_FP);
}

void weird_pointer_stuff(int idx) {
    undefined8 local_198 = 0x5958575655545352;
    undefined8 local_190 = 0x363534333231305a;
    undefined8 local_188 = 0x4544434241393837;
    undefined8 local_180 = 0x4d4c4b4a49484746;
    undefined8 local_178 = 0x6463626151504f4e;
    undefined8 local_170 = 0x6c6b6a6968676665;
    undefined8 local_168 = 0x74737271706f6e6d;
    undefined8 local_160 = 0x7a7978777675;
    
    putchar((int)*(char *)((long)&local_198 + (long)idx));
}
```
It all comes down to understanding what `weird_pointer_stuff` does. Luckily, pointers are my strong suite!

First, I analyze the `putchar` instruction incrementally:
- `a = (long)&local_198` : take the address of `local_198` (the first variable of the batch) and treat it as a `long`;
- `b = a + (long)idx` : add the index value (spoiler: there's a reason why I called it `idx`);
- `c = (char *)b` : treat this value as an address to a char (that is, a single-byte variable);
- `d = *c` : get the char at that address;
- `e = (int)d` : convert that char to an int;
- `putchar(e)` : print it (as a char)!

It's clear that all those local variables are being treated as a big characters array. Moreover, all the hexadecimal bytes are printable characters!
I convert every `local_XXX` variable from hexadecimal to string, reversing it due to the little endianess of the architecture. Concatenating them returns the following string:
```c
char s[] = "RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopqrstuvwxyz";
```
Overall, the behavior of `weird_pointer_stuff` can be simplified as follows:
```c
void weird_pointer_stuff(int idx) {
    char s[] = "RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopqrstuvwxyz";
    putchar(s[idx]);
}
```

## Writing the decryption function
Let's recap the encryption algorithm in Python:
```py
def encrypt(cleartext):
    s = 'RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopqrstuvwxyz'
    # 1. check the cleartext length
    if len(cleartext) != 27:
        exit(1)
    # 2. convert each character to its binary representation
    #    (`iterate_and_encrypt`)
    data_dat = []
    for ch in cleartext:
        data_dat += get_bin(ord(ch), is_big_endian=True, bit_num=8)
    # 3. read `data_dat` 6 bits at a time, and convert them back to decimal
    #    (`encrypt_p2`)
    for i in range(0,216,6):
        idx = get_int(data_dat[i:i+6], is_big_endian=True)
        # 4. fetch the correct entry of `s`
        #    (`weird_pointer_stuff`)
        print(s[idx], end='')
    print() 
```
To decrypt it, I simply need to invert every single operation, and compute them in the reverse order.
```py
def decrypt(ciphertext):
    s = 'RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopqrstuvwxyz'
    data_dat = []
    # 4r. for each character, fetch the index it appears in `s`
    for ch in ciphertext:
        idx = s.index(ch)
        # 3r. convert it to its binary representation on 6 bits
        data_dat += get_bin(idx, is_big_endian=True, bit_num=6)
    # at this point, we reconstructed `data_dat`
    # 2r. convert each byte of `data_dat` to character
    for i in range(0,216,8):
        ch = chr(get_int(data_dat[i:i+8], is_big_endian=True))
        print(ch, end='')
    print()
```
Running `decrypt` on the encrypted flag solves the challenge!

## Complete Python script
I add here the complete encrypt and decrypt script, for complexity.

Happy hacking!

```py
def get_bin(answ, is_big_endian=False, bit_num=8):
    bin = []
    for _ in range(bit_num):
        bin.append(answ % 2)
        answ = answ // 2
    if is_big_endian:
        bin = bin[::-1]
    return bin

def get_int(bin, is_big_endian=False):
    answ = 0
    if not is_big_endian:
        bin = bin[::-1]
    for b in bin:
        answ *= 2
        answ += b
    return answ

def encrypt(cleartext):
    s = 'RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopqrstuvwxyz'
    # 1. check the cleartext length
    if len(cleartext) != 27:
        exit(1)
    # 2. convert each character to its binary representation
    #    (`iterate_and_encrypt`)
    data_dat = []
    for ch in cleartext:
        data_dat += get_bin(ord(ch), is_big_endian=True, bit_num=8)
    # 3. read `data_dat` 6 bits at a time, and convert them back to decimal
    #    (`encrypt_p2`)
    for i in range(0,216,6):
        idx = get_int(data_dat[i:i+6], is_big_endian=True)
        # 4. fetch the correct entry of `s`
        #    (`weird_pointer_stuff`)
        print(s[idx], end='')
    print() 

def decrypt(ciphertext):
    s = 'RSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQabcdefghijklmnopqrstuvwxyz'
    data_dat = []
    # 4r. for each character, fetch the index it appears in `s`
    for ch in ciphertext:
        idx = s.index(ch)
        # 3r. convert it to its binary representation on 6 bits
        data_dat += get_bin(idx, is_big_endian=True, bit_num=6)
    # at this point, we reconstructed `data_dat`
    # 2r. convert each byte of `data_dat` to character
    for i in range(0,216,8):
        ch = chr(get_int(data_dat[i:i+8], is_big_endian=True))
        print(ch, end='')
    print()


ENCRYPTED = '9W8TLp4k7t0vJW7n3VvMCpWq9WzT3C8pZ9Wz'
decrypt(ENCRYPTED)
```