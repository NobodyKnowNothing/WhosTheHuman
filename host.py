'''
Created on May 1, 2024

@author: KnowbodyKnowNothing
'''
import socket
import threading
import requests
import json
import random
import os
import sys

ans1, ans2 = "", ""
expectanswer = False
host = None
user = None
spectators = [] # Unused place to store any connections past 2
clients = {}
disg = []
usermsg = ""
guesses = 2
server = True

def restart_program(): # Restarts program
    print("Restarting program...")
    os.execv(sys.executable, ['python'] + sys.argv)

def handle_client(client_socket, client_address):
    global expectanswer, host, user, spectators, clients, ans1, ans2, disq, usermsg, server 
    
    while len(disg) < 3 and host is None: # Sets the random usernames 
            x = random.randint(1, 3)
            if x not in disg:
                disg.append(x)
    
    
    if clients == {}: # Sets the first connection to the host
        host = client_socket
    elif len(clients) == 1: # Sets the second connection to the user
        user = client_socket
    else: # Adds any excess connections to a list
        spectator.append(client_socket)
    
    
    print(f"Connection from {client_address}")

    def handle_disconnect(client_socket):
        try:
            # Close the client socket
            client_socket.close()

            # Remove the client socket from the list of connected clients
            if client_socket in clients:
                del clients[client_socket]

            print("Client disconnected.")
        except Exception as e:
            print("Error handling disconnect:", e)

    # Function to handle receiving data from the client
    def receive_messages():
        global expectanswer, host, user, spectators, clients, ans1, ans2, disg, usermsg, guesses
        
        while True:
            try: 
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    if host == client_socket: # If client is host
                        if not expectanswer:
                            if "user" in message.lower() and len(message) == 5: # Checks if host has made a guess attempt
                                if f"user{disg[0]}" in message.lower(): # If the guess was correct
                                    broadcast_message("Correct.\nYou win!", host)
                                    broadcast_message("The host guessed you :(\nYou lose.", user)
                                    broadcast_message("Restarting.", user)
                                    broadcast_message("Restarting.", host)
                                    restart_program()
                                else: # If the guess was wrong
                                    guesses -= 1
                                    broadcast_message(f"You have {guesses} guesses left.", host)
                                    broadcast_message(f"The host has {guesses} guesses left.", user)
                                if guesses <= 0: # If there is no guesses left
                                    broadcast_message("Host ran out of guesses.\nYou win!", user)
                                    broadcast_message("You ran out of guesses. :(\nYou lose.", host)
                                    broadcast_message("Restarting.", user)
                                    broadcast_message("Restarting.", host)
                                    restart_program()
                            else:
                                broadcast_message("Host: " + message, user) # Host asks a question
                                off = True
                                while off: # In case api request limit is reached, it reattempts until limit reset
                                    try:
                                        ans1, ans2 = prompt(message), prompt(message)
                                        off = False
                                    except:
                                        print("Failure to get messages from API. Trying again.")
                                broadcast_message("The AIs said:\n" + f"User{disg[1]}: " + ans1 + f"\nUser{disg[2]}: " + ans2, user)
                                expectanswer = True
                        else:
                            broadcast_message("Wait for a response.", host) # Not hosts turn to speak
                    elif user == client_socket: # If client is user
                        if expectanswer: # If client is expected to speak
                            usermsg = ""
                            temp = [f"User{disg[0]}: " + message + "\n", f"User{disg[1]}: " + ans1 + "\n", f"User{disg[2]}: " + ans2 + "\n"]
                            for i in disg: # Randomizes user response order
                                usermsg += temp[i-1]
                            broadcast_message(usermsg[:-1], host)
                            expectanswer = False
                        else:
                            broadcast_message("Wait.", user)
                    else:
                        broadcast_message("This is an ongoing game. You have been placed in purgatory!", client_socket) 
                        
            except Exception as e:
                print(f"Error receiving message from {client_address}: {e}")
                break

    # Function to broadcast a message to specified client
    def broadcast_message(message, sock):
        global guesses, user, host
        try:
            sock.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error broadcasting message to {
                  clients[sock]}: {e}")
            # Call handle_disconnect function if an error occurs
            handle_disconnect(client_socket)
    # Add client socket to list of clients
    clients[client_socket] = client_address
    if client_socket == host: # Intro message for the host
        broadcast_message(f"Welcome, you are a host. ", client_socket)
        broadcast_message(f"You are tasked with asking questions and guessing which user is the human one based on their response.\nType in only their name to guess, you have 5 guesses.\nPlease wait while a user connects.", client_socket)
    elif client_socket == user:# Intro message for the user
        broadcast_message(f"Welcome, you are a user. ", client_socket)
        broadcast_message(f"A user has connected.", host)
        broadcast_message(f"You are tasked with answering questions and trying to not be guessed as human based on your answers, the host has 5 guesses.\nPlease wait while the host asks a question and the AI responses are prepared.", client_socket)
    else: # Intro message for excess users
        broadcast_message(f"Welcome, this game is full, you will not be able to play.", client_socket)
    # Start thread for receiving messages
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()
    
def prompt(prompt): # AI api call
    prompt = f"Your a unkown human text messager pretending like your a LLM pretending to be human for a game, respond like text or direct message (not stereotyped, genuine human text with no punctuation and text grammar), respond in less then 2 sentences, original and human. Respond to the following: " + \
        str(prompt)
    url = "https://api.awanllm.com/v1/chat/completions"

    payload = json.dumps({
        "model": "Meta-Llama-3-8B-Instruct-Dolfin-v0.1",
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer 213c2cad-e6b2-469d-988f-1a015fbde4bc"
    }

    return requests.request("POST", url, headers=headers, data=payload).json()["choices"][0]["message"]["content"]


def main():
    # Set up server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "0.0.0.0"

    try: # Try to open server
        server_port = int(55555)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(5)
        print("Server is listening...")
    except Exception as e:
        print("Error starting server:", e)
        return

    # Accept and handle client connections
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(
            client_socket, client_address)).start()

if __name__ == "__main__":
    main()
