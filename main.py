'''
Created on May 1, 2024

@author: KnowbodyKnowNothing
'''
import socket
import threading
import os
import sys

resp = False
user = ""


def receive_messages(client_socket):  # Function to handle receiving messages
    global resp, user
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # If the message is introduction
                if message[:7] == "Welcome":
                    # Gets the users role from intro message
                    user = message[-6:-2]
                # If the received message should have a response from client
                elif message[:5] == "The A" or message[:4] == "User" or message[:5] == "Wait." or message[-10:] == "connected." or message[:5] == "You h":
                    resp = True
                print(message)
                # Checks if the game has ended and the sever is restarting
                if "Restarting." in message:
                    restart_program()
        except Exception as e:  # Restarts the program if user wants to reatempt connectionq
            print("Error receiving message:", e)
            if 'y' not in input("Would you like to try connecting again? (yes/no): ").lower():
                break
            restart_program()


def send_messages(client_socket):  # Function to handle sending messages
    global resp, user
    while True:
        try:
            if resp:  # Checks if the user can respond
                message = input("You: ")
                client_socket.send(message.encode('utf-8'))
                resp = False
        except Exception as e:  # Restarts the program if user wants to reattempt connection
            print("Error sending message:", e)
            if 'y' not in input("Would you like to try connecting again? (yes/no): ").lower():
                break
            restart_program()


def restart_program():
    print("Restarting program...")
    os.execv(sys.executable, ['python'] + sys.argv)


def main():
    # Set up socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = input("Server ip: ")
    try:
        server_port = int(55555)
        client_socket.connect((server_ip, server_port))
        print("Connected to server.")
    except Exception as e:  # If connection error ask for restart
        print("Error connecting to server:", e)
        if "y" in input("Would you like to try again? (yes/no)").lower():
            restart_program()
        exit()

    # Start threads for sending and receiving messages
    receive_thread = threading.Thread(
        target=receive_messages, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))
    receive_thread.start()
    send_thread.start()


if __name__ == '__main__':
    main()
