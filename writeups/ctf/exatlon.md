# [Exatlon](https://app.hackthebox.com/challenges/Exatlon) Writeup [HTB]
_Reverse_

## Unpacking the executable
This challenge's executable is a statically linked program, `exatlon_v1`. As per usual, I run `strings` to see if I can get some hints.
```sh
$ strings exatlon_v1
[...]
1`EP_o
9, 0o/
? _0
USQRH
PROT_EXEC|PROT_WRITE failed.
$Info: This file is packed with the UPX executable packer http://upx.sf.net $
$Id: UPX 3.95 Copyright (C) 1996-2018 the UPX Team. All Rights Reserved. $
_j<X
RPI)
WQM)
j"AZR^j
[...]
```
Interestingly, the vast majority of the output consists of scrambled characters, which hints to the fact that the file is packed or compressed. Luckily, I know what was used to pack it:
```
$Info: This file is packed with the UPX executable packer http://upx.sf.net $
$Id: UPX 3.95 Copyright (C) 1996-2018 the UPX Team. All Rights Reserved. $
```
I download the correct version of UPX and unpack the executable. This reveals the following:
- The program is not stripped. This is great, since it's also statically linked (which means I would have had to search for the main and other relevant functions in the sea of library methods);
- The program is written in C++. This is less great, since decompiling C++ is more painful than standard C.

I also run the program to see what it does:
```sh
$ ./exatlon_v1 

███████╗██╗  ██╗ █████╗ ████████╗██╗      ██████╗ ███╗   ██╗       ██╗   ██╗ ██╗
██╔════╝╚██╗██╔╝██╔══██╗╚══██╔══╝██║     ██╔═══██╗████╗  ██║       ██║   ██║███║
█████╗   ╚███╔╝ ███████║   ██║   ██║     ██║   ██║██╔██╗ ██║       ██║   ██║╚██║
██╔══╝   ██╔██╗ ██╔══██║   ██║   ██║     ██║   ██║██║╚██╗██║       ╚██╗ ██╔╝ ██║
███████╗██╔╝ ██╗██║  ██║   ██║   ███████╗╚██████╔╝██║ ╚████║███████╗╚████╔╝  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝ ╚═══╝   ╚═╝


[+] Enter Exatlon Password  : 42
[-] ;(
```
I likely have to understand the password validation logic in order to get the flag.
Time to take out Ghidra!

## Decompiling the program
As I already expected, the program contains hundreds of functions. Luckily it's not stripped, so I can easily find the main. After some code cleaning and variable renaming, the main function looks like this:
```cpp
undefined4 main(void) {
    bool is_correct;
    basic_string<char,std::char_traits<char>,std::allocator<char>> pwd [32];
    basic_string manipulated_pwd [32];
    
    do {
        /* print program name [redacted for simplicity] */
        std::operator<<((basic_ostream *)std::cout,"[+] Enter Exatlon Password  : ");
        std::operator>>((basic_istream *)std::cin,(basic_string *)pwd);
        // reads the provided password and manipulates it (return value in `manupulated_pwd`)
        manipulated_pwd = exatlon(pwd);
        // checks if the password is correct
        is_correct = std::operator==(manipulated_pwd,
                                    "1152 1344 1056 1968 1728 816 1648 784 1584 816 1728 1520 1840 1664  784 1632 1856 1520 1728 816 1632 1856 1520 784 1760 1840 1824 816 15 84 1856 784 1776 1760 528 528 2000 "
                                );
        if (is_correct) {
            std::operator<<((basic_ostream *)std::cout,"[+] Looks Good ^_^ \n\n\n");
        }
        else {
            // checks if the user wants to quit (they wrote "q")
            is_correct = std::operator==((basic_string *)pwd,"q");
            // if the password is wrong and the user doesn't want to quit, print sad emoticon :c
            if (!is_correct) {
                std::operator<<((basic_ostream *)std::cout,"[-] ;(\n");
            }
        }
    } while (!is_correct);
    return 0;
}
```

Overall, I must check what's the transformation undergone by the password, to invert it and recover the flag from the array `"1152 1344 1056 1968 1728 816 1648 784 1584 816 1728 1520 1840 1664  784 1632 1856 1520 1728 816 1632 1856 1520 784 1760 1840 1824 816 15 84 1856 784 1776 1760 528 528 2000 "`. To do so, I have to study the `exatlon` function.

```cpp
basic_string * exatlon(basic_string *pwd) {
    basic_string<char,std::char_traits<char>,std::allocator<char>> *manipulated_pwd;
    undefined8 it, end_it;
    bool is_done;
    char ch;
    char *ch_addr;
    __cxx11 ch_str [39];
    
    /* allocate variables [redacted for simplicity] */
    it = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::begin(pwd);
    end_it = std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::end(pwd);
    // for each character in `pwd`
    while( true ) {
        // check if `it` is equal to `end_it` (i.e., check if the array is finished)
        is_done = __gnu_cxx::operator==
                                ((__normal_iterator *)&it,(__normal_iterator *)&end_it);
        if (is_done) break;
        // get the character in the current position
        ch_addr = (char *)__gnu_cxx::
                        __normal_iterator<char_const*,std::__cxx11::basic_string<char,std::char_traits< char>,std::allocator<char>>>
                        ::operator*((__normal_iterator<char_const*,std::__cxx11::basic_string<char,std: :char_traits<char>,std::allocator<char>>>
                                    *)&it);
        ch = *ch_addr;
        // cast the char to int, multiply by 16 and save the result as a string
        std::__cxx11::to_string(ch_str,(int)ch << 4);
        // concatenate the string to the result
        std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>::operator+=
                ((basic_string<char,std::char_traits<char>,std::allocator<char>> *)manipulated_pwd,ch_str);
        // increment the iterator
        __gnu_cxx::
        __normal_iterator<char_const*,std::__cxx11::basic_string<char,std::char_traits<char>,std::alloca tor<char>>>
        ::operator++((__normal_iterator<char_const*,std::__cxx11::basic_string<char,std::char_traits<cha r>,std::allocator<char>>>
                    *)&it);
    }
    return manipulated_pwd;
}
```
## Inverting `exatlon`
Luckily, all this C++ mumbo-jumbo simply translates to:
```py
def exatlon(pwd):
    manipulated_pwd = ''
    for c in pwd:
        # convert c to its integer representation, then left shift
        manipulated_c = ord(c) << 4
        manipulated_pwd += f'{manipulated_c} '
    return manipulated_pwd
```
Meaning that the invert is just as easy:
```py
def rev_exatlon(manipulated_pwd):
    pwd = ''
    manipulated_pwd = manipulated_pwd.split()
    for n in manipulated_pwd:
        # cast to int, then right shift
        manipulated_c = int(n) >> 4
        # convert back to char representation
        pwd += chr(manipulated_c)
    return pwd

pwd = rev_exatlon('1152 1344 1056 1968 1728 816 1648 784 1584 816 1728 1520 1840 1664  784 1632 1856 1520 1728 816 1632 1856 1520 784 1760 1840 1824 816 15 84 1856 784 1776 1760 528 528 2000')
print(pwd)
```
Running this tiny Python script reveals the flag!
