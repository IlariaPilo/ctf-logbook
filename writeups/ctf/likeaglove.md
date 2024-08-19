# [Like a Glove](https://app.hackthebox.com/challenges/Like%2520a%2520Glove) Writeup [HTB]
_AI - ML_

## Introducing the challenge
This challenge is based on a textual file, which used embeddings generated with the `glove-twitter-25` model. The file contains a list of 84 peculiar analogies:
```
Like non-mainstream is to efl, battery-powered is to?
Like sycophancy is to بالشهادة, cont is to?
Like беспощадно is to indépendance, rs is to?
Like ajaajjajaja is to hahahahahahahahaahah, ２ is to?
Like bahno is to arbus, duit is to?
Like 잡히지 is to ਮੈਂ, 年度第 is to?
Like usaar is to est-ce-que, ７ is to?
[...]
```
## From words to numbers (vectors, actually)
From the description of the challenge, I deduce that the response to each analogy is likely a single character. Concatenating all responses will return the flag.

Embedding models like [Glove](https://nlp.stanford.edu/projects/glove/) work by converting every word into a vector. Then, we can use all the mathematic operations defined on vectors to infer relationships between the underlying words. For example, "man - woman" will have a similar vector as "king - queen", or "mister - miss".

Let's put this example into a more readable analogy:
```
Like man is to woman, king is to?
```
How do we get "queen"?

First, we need to represent _Like man is to woman_. The distance between them can be seen as a _subtraction_ between the correspondent vectors:
```py
like_man_is_to_woman = vector_man - vector_woman
```
To make the analogy work, the second pair should be _as similar_ as the first one:
```py
king_is_to_XXX == like_man_is_to_woman
```
If we make explicit the subtraction on both sides, we get:
```py
king_is_to_XXX == (vector_man - vector_woman)
(vector_king - vector_XXX) == (vector_man - vector_woman)
## meaning
vector_XXX == vector_king - (vector_man - vector_woman) 
```
Now that we computed our target vector, we simply need to extract the word having the most similar vector, and the analogy is solved!

## Letting the AI do the work
A simple Google search returns me the [`glove-twitter-25`](https://huggingface.co/Gensim/glove-twitter-25) model. Problem is, I don't have any idea on how to interact with it in Python.

Since this is an AI challenge, I think it's fitting to take out ChatGPT and make it do the dirty work. I describe my algorithm and ask Chat how to implement it with `glove-twitter-25`. I add some basic instructions to read the file and parse the analogies, then run the script and get the flag!

When the flag is printed on the terminal, I notice all the digits are written in a weird font. Following the advice in the challenge description, I have to convert them to ASCII before submitting the flag.

## Full Python script (thanks ChatGPT!)
```py
import gensim.downloader as api
import re

info = api.info()  # show info about available models/datasets
model = api.load("glove-twitter-25")  # download the model and return as object 

pattern = r"Like (.*) is to (.*), (.*) is to\?"
flag = '' 

with open('chal.txt', 'r') as file:
    for analogy in file:
        # Use re.search to find the components
        match = re.search(pattern, analogy)

        if match:
            XXX = match.group(1)
            YYY = match.group(2)
            ZZZ = match.group(3)
 
            # Ensure the words exist in the GloVe vocabulary
            if XXX in model.key_to_index and YYY in model.key_to_index and ZZZ in model.key_to_index:
                # Get the word vectors
                vector_xxx = model[XXX]
                vector_yyy = model[YYY]
                vector_zzz = model[ZZZ]
                # Calculate the transformation vector
                vector_diff = vector_xxx - vector_yyy
                # Apply the transformation to ZZZ
                vector_result = vector_zzz - vector_diff
                # Find the most similar word to the resulting vector
                similar_words = model.similar_by_vector(vector_result, topn=1)
                # Output the closest word
                flag += similar_words[0][0]
            else:
                print("One or more words are not in the GloVe vocabulary.")
                exit(1)
flag = ''.join(flag.split())
print(flag)
```