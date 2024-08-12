# A script to connect to a server via TCP, and automatically reply with whatever logic you want!
from pwn import *

def process(received_data):
    # Replace this function with the processing logic
    return ''

def main():
    sock = remote('94.237.59.199', 40534)
        
    while True:
        # Receive data from the server until `?`
        received_data = sock.recvuntil(b"?", timeout=1).decode()
        # or, get the line that contains `Message:`
        # received_data = sock.recvline_contains(b"Message:", timeout=1).decode()
        if not received_data:
            print("No data received, exiting...")
            break
        print(f"{received_data}")
        
        # Process the received string
        processed_data = process(received_data)
    
        # Send the processed data back to the server
        sock.sendline(processed_data.encode())
        print(f"{processed_data}")
        

if __name__ == "__main__":
    main()
