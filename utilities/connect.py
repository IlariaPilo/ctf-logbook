# A script to connect to a server via TCP, and automatically reply with whatever logic you want!
import socket

def process(received_data):
    # Replace this function with the processing logic
    return ''

def main():
    server_address = ('94.237.59.199', 40534)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(server_address)
        
        while True:
            # Receive data from the server
            received_data = sock.recv(1024).decode('utf-8')
            if not received_data:
                print("No data received, exiting...")
                break
            print(f"{received_data}")
            
            # Process the received string
            processed_data = process(received_data)
        
            # Send the processed data back to the server
            sock.sendall(processed_data.encode('utf-8'))
            print(f"{processed_data}")
            

if __name__ == "__main__":
    main()
