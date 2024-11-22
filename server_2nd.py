import socket
import threading

# Server settings
HOST = "192.168.0.4"
PORT = int(input("Please enter the server port number: "))

# Data structures to store user info, online clients, and game rooms
users = {}  # {username: password}
online_clients = {}  # {username: client_socket}
game_rooms = {}  # {room_name: {'owner': username, 'type': game_type, 'port': port, 'public': is_public, 'players': list, 'game_started': bool}}

def handle_client(client_socket):
    current_user = None
    while True:
        try:
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
                        'public': is_public,
                        'players': [current_user],  # Add the owner as the first player
                        'game_started': False,
                        'choices': {}  # Stores choices for each player
                    }
                    client_socket.send(f"Public room '{room_name}' created. Waiting for another player to join...\n".encode())

                    # Wait for another player to join the room
                    while len(game_rooms[room_name]['players']) < 2:
                        pass  # Keep the thread running while waiting for player B to join

                    # Notify both players that the game is starting
                    for player in game_rooms[room_name]['players']:
                        online_clients[player].send("Player has joined. The game is starting.\n".encode())

                    game_rooms[room_name]['game_started'] = True
                    start_game(room_name)

                elif command == "JOIN_ROOM":
                    room_name = parts[1]
                    if room_name in game_rooms and len(game_rooms[room_name]['players']) < 2:
                        game_rooms[room_name]['players'].append(current_user)
                        client_socket.send(f"Player {current_user} has joined. The game is starting.\n".encode())
                        # Notify the owner and other player that game is starting
                        online_clients[game_rooms[room_name]['owner']].send(f"Player {current_user} has joined. The game is starting.\n".encode())
                        if len(game_rooms[room_name]['players']) == 2:
                            game_rooms[room_name]['game_started'] = True
                            start_game(room_name)
                    else:
                        client_socket.send("Room is full or does not exist.\n".encode())

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

def start_game(room_name):
    """當兩位玩家都加入時開始遊戲"""
    room = game_rooms[room_name]

    # 僅在兩位玩家到齊時才發送「遊戲開始」
    if len(room['players']) == 2:
        # 通知所有玩家遊戲開始一次
        for player in room['players']:
            online_clients[player].send("Player has joined. The game is starting.\n".encode())

        # 開始收集每位玩家的選擇
        moves = {}
        for player in room['players']:
            #online_clients[player].send("It's your turn! Please choose Rock, Paper, or Scissors.\n".encode())
            move = online_clients[player].recv(1024).decode().strip()
            moves[player] = move

        # 計算結果
        result = determine_winner(moves, room['players'])
        
        # 發送遊戲結果給玩家
        for player in room['players']:
            online_clients[player].send(result.encode())

        # 清理房間數據，準備下一場
        room['game_started'] = False
        room['players'].clear()



def determine_winner(moves, players):
    """比較兩位玩家的選擇並返回結果訊息"""
    player1, player2 = players
    move1, move2 = moves[player1], moves[player2]

    if move1 == move2:
        return f"Both players chose {move1}. It's a tie!\n"
    elif (move1, move2) in [('Rock', 'Scissors'), ('Scissors', 'Paper'), ('Paper', 'Rock')]:
    #elif (move1=='Rock' and move2=='Scissors') or (move1=='Scissors' and move2=='Paper') or (move1=='Paper' and move2=='Rock'):
        return f"{player1} wins with {move1} against {player2}'s {move2}!!\n"
    else:
        return f"{player2} wins with {move2} against {player1}'s {move1}!\n"

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
