# [Insomnia](https://app.hackthebox.com/challenges/Insomnia) Writeup [HTB]
_Web_

<style>
.spoiler, .spoiler2, .spoiler a, .spoiler2 a{ 
  color: black; 
  background-color: black;
}

.spoiler:hover, .spoiler:hover a {
  color: white;
}

.spoiler2:hover, .spoiler2:hover a { 
 background-color:white; 
}
</style>

## Investigating the website
This challenge provides us with a vaporwave-looking website. 
It looks very simple, the only working parts are a sign-in and a sign-up form.

I first try to create an account for myself. After I log in, I get assigned a token in my cookies, and I receive a nice welcome message. Nothing more.

Time to look at the source code!

## Analyzing the source code
First, I search the code base for "flag", to see what I have to do in order to get it.
```php
$key = (string) getenv("JWT_SECRET");
$jwt_decode = JWT::decode($token, new Key($key, "HS256"));
$username = $jwt_decode->username;
if ($username == "administrator") {
    return view("ProfilePage", [
        "username" => $username,
        "content" => $flag,
    ]);
}
```
It looks like I have to log in as the administrator, or at least get its token. 

I decide to take a look at the login procedure. First, I analyze the token generation procedure, hoping to find a way to forge the token. However, it requires knowing a secret key, which I don't have and don't know how to get.

I then decide to focus on the database query:
```php
public function login() {
    $db = db_connect();
    $json_data = request()->getJSON(true);
    if (!count($json_data) == 2) {
        return $this->respond("Please provide username and password", 404);
    }
    $query = $db->table("users")->getWhere($json_data, 1, 0);
    $result = $query->getRowArray();
    if (!$result) {
        return $this->respond("User not found", 404);
    } else {
        /* Generate token and send it */
    }
}
```

## Finding the exploit
I don't know much PHP, so I start analyzing the function line-by-line.
- `request()->getJSON(true)` simply takes the body of the HTTP request and put it into a PHP associative array;
- The "if" clause checks whether the array has two elements; <span class="spoiler" >...or does it?</span>
- `$db->table("users")->getWhere($json_data, 1, 0)` queries the database.

More specifically, the query works as follows. Suppose we are passing as credentials:
```json
{
    "username": "p1ll0w",
    "password": "so_safe"
}
```
Then, the `getWhere` function will run the following query:
```sql
SELECT *
FROM users
WHERE username="p1ll0w" AND password="so_safe"
```

But what if we passed the following?
```json
{
    "username": "administrator"
}
```
We could be able to get the admin credentials without even needing a password! Too bad the "if" is making sure the JSON object we are passing has 2 and only 2 fields... <span class="spoiler" >But is it really?</span>

I double-check the "if" condition. Now that I focus on it, it does look weird. Why is it not using `!=`? I search on the Internet and discover that yes, PHP has the classic "not equal" operator, meaning this is just a _not_ and an _equal_ combined. 

The [PHP operator precedence list](https://www.php.net/manual/en/language.operators.precedence.php) reveals the trick: `!` is executed *__before__* `==`, meaning that the condition is evaluated as:
```php
(!count($json_data)) == 2
```
which basically translates the "if" to:
```php
if (count($json_data) == 0) {
        return $this->respond("Please provide username and password", 404);
}
```

I simply send a `/login` request with only the username, log in as admin and get the flag!
