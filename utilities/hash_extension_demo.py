import HashTools
import base64

def encode64(raw_data: bytes):
    return base64.b64encode(raw_data)

def decode64(data):
    return base64.b64decode(data).decode('ascii')

# setup context
original_data = b'username=guest&isLoggedIn=False'
b64_signature = 'ZjQzYjU0ZjFhMGU0NzAwZjQxZDk0ZjRkNjVjZmU3MTc2NjkyZmIzZWI4YzU4YzA2NGY5YWMyZTM5YjYzNDFlY2EzOWM2ZmE2NWQ2NGQzOTViZTY0MWRmYmE2NjVhMDZiOTEyMzg4NzJmOTEzMmEwY2U2MWE1NDJlZDQ3NmE2MmU='
append_data = b'&isLoggedIn=True'
secret_length = 16
hash_method = 'sha512'

original_signature = decode64(b64_signature)

# attack
magic = HashTools.new(hash_method)
new_data, new_sig = magic.extension(
    secret_length=secret_length, original_data=original_data,
    append_data=append_data, signature=original_signature
)
print(encode64(new_data) + b'.' + encode64(new_sig.encode('utf-8')))
