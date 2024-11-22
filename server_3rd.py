import socket
import threading
import random

# Server settings
HOST = "192.168.0.4"
PORT = int(input("Please enter the server port number: "))

# Data structures to store user info, online clients, and game rooms
users = {}  # {username: password}
online_clients = {}  # {username: client_socket}
game_rooms = {}  # {room_name: {'owner': username, 'type': game_type, 'port': port, 'public': is_public}}

def generate_secret_number():
    digits = random.sample(range(0, 10), 4)
    return ''.join(map(str, digits))

# Function to calculate bulls (A) and cows (B)
def calculate_bulls_and_cows(secret, guess):
    bulls = sum(s == g for s, g in zip(secret, guess))
    cows = len(set(secret) & set(guess)) - bulls
    return bulls, cows

# Game handler for 1A2B
def handle_1a2b_game(room, player_sockets):
    print(f"Starting 1A2B game in room {room}")
    secret_number = generate_secret_number()
    print(f"Secret number for room {room}: {secret_number}")

    current_player = 0
    while True:
        # Notify the current player to make a guess
        player_sockets[current_player].send("Your turn! Enter a 4-digit guess: ".encode())
        guess = player_sockets[current_player].recv(1024).decode().strip()

        # Validate guess
        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            player_sockets[current_player].send("Invalid guess. Please enter a unique 4-digit number.\n".encode())
            continue

        # Calculate bulls and cows
        bulls, cows = calculate_bulls_and_cows(secret_number, guess)
        player_sockets[current_player].send(f"Result: {bulls}A{cows}B\n".encode())

        # Check for win condition
        if bulls == 4:
            player_sockets[current_player].send("Congratulations! You won!\n".encode())
            other_player = 1 - current_player
            player_sockets[other_player].send("You lost. The game is over.\n".encode())
            break

        # Notify the other player of the guess
        other_player = 1 - current_player
        player_sockets[other_player].send(f"Opponent guessed: {guess}. Result: {bulls}A{cows}B\n".encode())

        # Switch turns
        current_player = other_player
# In the server code
def handle_client(client_socket):
    current_user = None
    while True:
        try:
            # Receive a command from the client
            message = client_socket.recv(1024).decode()
            if message:
                parts = message.split()
                command = parts[0]

                if command == "REGISTER":
                    username = parts[1]
                    password = parts[2]
                    if username in users:
                        client_socket.send("Username already exists.\n".encode())
                    else:
                        users[username] = password
                        client_socket.send("Register success.\n".encode())

                elif command == "LOGIN":
                    username = parts[1]
                    password = parts[2]
                    if username in users and users[username] == password:
                        current_user = username
                        online_clients[username] = client_socket
                        client_socket.send("Login success.\n".encode())
                    else:
                        client_socket.send("Login failed.\n".encode())

                elif command == "LOGOUT":
                    if current_user and current_user in online_clients:
                        del online_clients[current_user]
                        client_socket.send("Logout success.\n".encode())
                    break  # Close the connection after logout

                elif command == "LIST_ROOM":
                    # Combine online players and room list into one response
                    send_room_and_player_list(client_socket, current_user)

                elif command == "CREATE_ROOM":
                    room_name = parts[1]
                    game_type = parts[2]
                    is_public = parts[3] == "1"  # "1" for YES, "2" for NO
                    port = int(parts[4]) if is_public else None
                    game_rooms[room_name] = {
                        'owner': current_user,
                        'type': game_type,
                        'port': port,
                        'public': is_public
                    }
                    client_socket.send(f"Public room '{room_name}' created.\n".encode())

                else:
                    client_socket.send("Unknown command.\n".encode())
            else:
                break
        except Exception as e:
            print(f"Error: {e}")
            break

    if current_user and current_user in online_clients:
        del online_clients[current_user]
    client_socket.close()

def send_room_and_player_list(client_socket, current_user):
    """Send a list of online players and game rooms to the client"""
    online_list = "Online players:\n"
    online_list += "\n".join([user for user in online_clients.keys() if user != current_user]) or "No other online player available"
    
    room_list = "Game rooms:\n"
    room_list += "\n".join([f"{name} - {'Public' if details['public'] else 'Private'}" for name, details in game_rooms.items() if details['public']]) or "No game room available"
    
    # Send combined information as a single message
    client_socket.send((online_list + "\n" + room_list + "\n").encode())


def send_online_players(client_socket, current_user):
    online_list = "Online players:\n"
    online_list += "\n".join([user for user in online_clients.keys() if user != current_user]) or "No other online player available"
    client_socket.send(online_list.encode())



def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server started on {HOST}:{PORT}")
    
    while True:
        client_socket, address = server_socket.accept()
        print(f"New connection from {address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    start_server()
