import socket

HOST = "192.168.0.4"
PORT = int(input("Please enter the server port number: "))

def main_menu():
    print("---------")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    print("---------")

def post_login_menu():
    print("---------")
    print("1. Logout")
    print("2. List Room")
    print("3. Create Room")
    print("4. Join Room")
    print("---------")
def play_1a2b_game(client_socket):
    print("You have joined the 1A2B game room. Waiting for the game to start...")
    while True:
        message = client_socket.recv(1024).decode()
        print(message)

        # Check if it's the player's turn
        if "Your turn" in message:
            guess = input("Enter your 4-digit guess: ")
            client_socket.send(guess.encode())

        # Check for game over
        if "Congratulations" in message or "You lost" in message:
            print("Game over.")
            break
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    while True:
        main_menu()
        choice = input("Choose an option: ")

        if choice == '1':
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")
            client_socket.send(f"REGISTER {username} {password}".encode())
            response = client_socket.recv(1024).decode()
            print(response)

        elif choice == '2':
            username = input("Please enter your username: ")
            password = input("Please enter your password: ")
            client_socket.send(f"LOGIN {username} {password}".encode())
            response = client_socket.recv(1024).decode()
            print(response)

            # Check if login was successful
            if "Login success" in response:
                # Start post-login options menu
                while True:
                    post_login_menu()
                    choice = input("Choose an option: ")

                    if choice == '1':  # Logout
                        client_socket.send(f"LOGOUT {username}".encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                        break  # Return to main menu after logout

                    elif choice == '2':  # List Room
                        client_socket.send("LIST_ROOM".encode())
                        response = client_socket.recv(1024).decode()
                        print(response)

                    elif choice == '3':  # Create Room
                        room_name = input("Please enter the room name: ")
                        game_type = input("Please enter your game type (1 for 21points, 2 for 1A2B): ")
                        is_public = input("Is the room public (1 for YES, 2 for NO)? ")

                        if is_public == '1':
                            port = input("Please enter the port number to bind (10000-65536): ")
                            client_socket.send(f"CREATE_ROOM {room_name} {game_type} {is_public} {port}".encode())
                        else:
                            client_socket.send(f"CREATE_ROOM {room_name} {game_type} {is_public}".encode())
                        
                        response = client_socket.recv(1024).decode()
                        print(response)

                    elif choice == '4':  # Join Room (Placeholder)
                        room_name = input("Room name to join: ")
                        client_socket.send(f"JOIN_ROOM {room_name}".encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                        if "Waiting" in response:
                            play_1a2b_game(client_socket)

                    else:
                        print("Invalid option. Please select a valid option.")

        elif choice == '3':
            print("Exiting the client.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

    client_socket.close()

if __name__ == "__main__":
    main()
