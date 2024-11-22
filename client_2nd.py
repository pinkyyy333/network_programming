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

def game_menu():
    print("---------")
    print("1. Rock")
    print("2. Paper")
    print("3. Scissors")
    print("---------")

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

            if "Login success" in response:
                while True:
                    post_login_menu()
                    choice = input("Choose an option: ")

                    if choice == '1':
                        client_socket.send(f"LOGOUT {username}".encode())
                        response = client_socket.recv(1024).decode()
                        print(response)
                        break

                    elif choice == '2':
                        client_socket.send("LIST_ROOM".encode())
                        response = client_socket.recv(1024).decode()
                        print(response)

                    elif choice == '3':
                        room_name = input("Please enter the room name: ")
                        game_type = input("Please enter your game type (1 for Rock Paper Scissors): ")
                        is_public = input("Is the room public (1 for YES, 2 for NO)? ")
                        if is_public == '1':
                            port = input("Please enter the port number to bind (10000-65536): ")
                            client_socket.send(f"CREATE_ROOM {room_name} {game_type} {is_public} {port}".encode())
                        else:
                            client_socket.send(f"CREATE_ROOM {room_name} {game_type} {is_public}".encode())

                        response = client_socket.recv(1024).decode()
                        print(response)

                        # Wait for game to start
                        response = client_socket.recv(1024).decode()
                        print(response)

                        if "The game is starting" in response:
                            game_menu()
                            client_socket.recv(1024).decode()
                            move_choice = input("Choose your move: ")
                            if move_choice == '1':
                                client_socket.send(f"MAKE_MOVE {room_name} Rock".encode())
                            elif move_choice == '2':
                                client_socket.send(f"MAKE_MOVE {room_name} Paper".encode())
                            elif move_choice == '3':
                                client_socket.send(f"MAKE_MOVE {room_name} Scissors".encode())
                            else:
                                break

                            # Wait for and print game result
                            result = client_socket.recv(1024).decode()
                            print(result)

                    # 在選擇加入房間的情況下，進行以下更改

                    elif choice == '4':
                        room_name = input("Enter the room name to join: ")
                        client_socket.send(f"JOIN_ROOM {room_name}".encode())
                        response = client_socket.recv(1024).decode()
                        print(response)

                        # 只當接收到「The game is starting」時進入選擇流程
                        if "The game is starting" in response:
                            # 顯示選擇畫面並讓玩家做出選擇
                            game_menu()
                            client_socket.recv(1024).decode()
                            move_choice = input("Choose your move: ")
                            if move_choice == '1':
                                client_socket.send(f"MAKE_MOVE {room_name} Rock".encode())
                            elif move_choice == '2':
                                client_socket.send(f"MAKE_MOVE {room_name} Paper".encode())
                            elif move_choice == '3':
                                client_socket.send(f"MAKE_MOVE {room_name} Scissors".encode())

                            # 接收並顯示遊戲結果
                            result = client_socket.recv(1024).decode()
                            print(result)




        elif choice == '3':
            print("Exiting the client.")
            break
        else:
            print("Invalid choice. Please select a valid option.")

    client_socket.close()

if __name__ == "__main__":
    main()
