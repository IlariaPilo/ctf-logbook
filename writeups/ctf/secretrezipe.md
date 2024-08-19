# [SecretRezipe](https://app.hackthebox.com/challenges/SecretRezipe) Writeup [HTB]
_Misc_

## Analyzing the website
This challenge provides a website for a soft drink startup. 
The website is basically functionless, except for a form to write an ingredient list. After the form is sent I get back the full list, zipped and protected by password.

Since the code of the website is available, I check it to know more about the compression procedure.
```js
router.post('/ingredients', (req, res) => {
  let data = `Secret: ${FLAG}`
  if (req.body.ingredients) {
    data += `\n${req.body.ingredients}`
  }
  const tempPath = os.tmpdir() + '/' + crypto.randomBytes(16).toString('hex')
  fs.mkdirSync(tempPath);
  fs.writeFileSync(tempPath + '/ingredients.txt', data)
  child_process.execSync(`zip -P ${PASSWORD} ${tempPath}/ingredients.zip ${tempPath}/ingredients.txt`)
  return res.sendFile(tempPath + '/ingredients.zip')
})
```
So, suppose my input is:
```
Ingredient: blended pineapple pizza
Ingredient: 42l of mayonnaise
Ingredient: love
```
Then, `ingredients.txt` will look like this:
```
Secret: HTB{<the flag, unknown>}
Ingredient: blended pineapple pizza
Ingredient: 42l of mayonnaise
Ingredient: love
```
Great! This means that the only obstacle between me and the flag is the password.

## Bypassing the password
According to the source code, the password is generated as follows:
```js
module.exports = {
  FLAG: FLAG,
  PASSWORD: crypto.randomUUID()
}
// for example, "36b8f84d-df4e-4d49-b662-bcde71a8764f"
```
Given the structure of the password, bruteforcing it seems unfeasible to me. 
There isn't really anything more that I can work with, so I decide to investigate the zip format. More specifically, I'm looking for a vulnerability that somehow allows bypassing the password.

A quick search on Google returns an interesting article, "[Stop using Zip to compress sensitive files, even with password protection](https://medium.com/@ethan_hou/stop-using-zip-to-compress-sensitive-files-even-with-password-protection-170d48374067)". Among the listed security issues, there is a vulnerability to known-plaintext attacks:

> Zip encryption is susceptible to known-plaintext attacks, which can reveal the encryption key when an attacker has access to both the encrypted and unencrypted versions of the same file.

This looks promising, especially since I know how most of the encrypted file looks like! 

## Exploiting the vulnerability
To run the attack, I use [`bkcrack`](https://github.com/kimci86/bkcrack). First, I read the metadata of the archive.
```sh
$ bkcrack -L ingredients.zip 
bkcrack 1.7.0 - 2024-05-26
Archive: ingredients.zip
Index Encryption Compression CRC32    Uncompressed  Packed size Name
----- ---------- ----------- -------- ------------ ------------ ----------------
    0 ZipCrypto  Store       f24a8841           75           87 tmp/7e03dc1e253fe2a22e326d6f5da7c72d/ingredients.txt
```
From this output, I discover that:
1. The name of the file I want to extract is `tmp/7e03dc1e253fe2a22e326d6f5da7c72d/ingredients.txt`;
2. Since the encryption type is _ZipCrypto_, the archive is actually vulnerable to the attack;
3. Since compression is _Store_ (and not _Deflate_), the file was simply encrypted, and not compressed. 

The third point is especially important, since having a deflated file makes this attack exponentially more complex (check the [official tutorial](https://github.com/kimci86/bkcrack/blob/master/example/tutorial.md) to know more about this).

Then, I need at least 12 bytes of known plaintext. 

As my first attempt, I try to add a few ingredients to the form, to increase the plaintext size and make the attack faster. However, this approach fails. I then decide to send an empty form, and simply use "Secret: HTB{" (which is exactly 12B) as known plaintext. This time, it works!

```sh
$ echo -n "Secret: HTB{" > plain
$ bkcrack -C ingredients.zip -c tmp/7e03dc1e253fe2a22e326d6f5da7c72d/ingredients.txt -p plain
bkcrack 1.7.0 - 2024-05-26
[17:05:30] Z reduction using 5 bytes of known plaintext
100.0 % (5 / 5)
[17:05:31] Attack on 1114527 Z values at index 6
Keys: c1dcd6ee ed71e97d 8fde64f7
26.0 % (289298 / 1114527)
Found a solution. Stopping.
You may resume the attack with the option: --continue-attack 289298
[17:21:47] Keys
c1dcd6ee ed71e97d 8fde64f7
```
Once I know the encryption keys, I can use them to extract the file and recover the flag!
```sh
$ bkcrack -C ingredients.zip -c tmp/7e03dc1e253fe2a22e326d6f5da7c72d/ingredients.txt -k c1dcd6ee ed71e97d 8fde64f7 -d flag.txt
bkcrack 1.7.0 - 2024-05-26
[17:26:33] Writing deciphered data flag.txt
Wrote deciphered data (not compressed).
$ cat flag.txt 
Secret: HTB{<REDACTED>}
```
