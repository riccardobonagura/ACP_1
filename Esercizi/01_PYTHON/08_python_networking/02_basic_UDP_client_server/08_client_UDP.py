import socket           # Import the socket module to enable network communication
import sys              # Import sys module to access command-line arguments and system functions
import time             # Import time module for measuring latency

def client(port):
    # Message that the client will send to the server
    msgClient = "Ciao server!"
    # Define the server address and port as a tuple
    serverAddressPort = ("localhost", port)
    # Size of the buffer for receiving data (in bytes)
    bufferSize = 1024

    # Create a UDP socket using IPv4 addressing (AF_INET)
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Print the message that is about to be sent to the server
    print("[Client]: Invio dati al server. msg:", msgClient)

    # Record the current time before sending the message (for latency calculation)
    start_time = time.time()  
    # Encode the message to bytes using UTF-8 and send it to the server's address and port
    s.sendto(msgClient.encode("utf-8"), serverAddressPort)

    # Wait to receive a reply from the server; returns (data, address)
    msgServer, addr = s.recvfrom(bufferSize)
    # Record the time immediately after receiving the reply
    end_time = time.time()  

    # Calculate the round-trip latency in milliseconds
    latency = (end_time - start_time) * 1000  

    # Print the response received from the server (decoded from bytes to string)
    print("[Client]: Risposta server:", msgServer.decode("utf-8"))
    # Print the measured round-trip latency formatted to 3 decimal places
    print(f"[Client]: Round-trip latency: {latency:.3f} ms")

    # Close the socket to release the resources
    s.close()

if __name__ == "__main__":
    try:
        # Try to read the port number from command-line arguments and convert it to integer
        port = int(sys.argv[1])  
    except (IndexError, ValueError):
        # Print error message and exit if argument is missing or not a valid integer
        print("Please specify a valid PORT as an argument.")
        sys.exit(1)

    # Call the client function with the specified port
    client(port)
