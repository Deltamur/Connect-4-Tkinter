import socket
import threading
import random
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
FORMAT = 'utf-8'


class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))

        print("Server started!\n")

        self.clients = []
        self.players = ["", ""]
        self.score = [0, 0]
        self.turn = "BLUE"
        self.is_stop = False
        self.buttons = [[" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "]]
        self.receive()

    def giving_color(self):
        if random.randint(1, 2) == 1:
            self.players[0] = "BLUE"
            self.players[1] = "RED"
        else:
            self.players[0] = "RED"
            self.players[1] = "BLUE"

    def check_table(self):
        is_full = True
        for column in range(7):
            for row in range(6):
                if self.buttons[column][row] == " ":
                    is_full = False
                    break
            if not is_full:
                break

        return is_full

    def check_vertical(self, column, row):
        is_win = False
        try:
            if self.buttons[column][row] == self.buttons[column][row + 1] == self.buttons[column][row + 2] == self.buttons[column][row + 3]:
                is_win = True
        except:
            pass
        return is_win

    def check_diagonal(self, column, row):
        is_win = False

        try:
            if self.buttons[column][row] == self.buttons[column+1][row+1] == self.buttons[column+2][row+2] == self.buttons[column+3][row+3]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column-1][row-1] == self.buttons[column][row] == self.buttons[column+1][row+1] == self.buttons[column+2][row+2]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column-2][row-2] == self.buttons[column-1][row-1] == self.buttons[column][row] == self.buttons[column+1][row+1]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column-3][row-3] == self.buttons[column-2][row-2] == self.buttons[column-1][row-1] == self.buttons[column][row]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column][row] == self.buttons[column+1][row-1] == self.buttons[column+2][row-2] == self.buttons[column+3][row-3]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column-1][row+1] == self.buttons[column][row] == self.buttons[column+1][row-1] == self.buttons[column+2][row-2]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column-2][row+2] == self.buttons[column-1][row+1] == self.buttons[column][row] == self.buttons[column+1][row-1]:
                is_win = True
        except:
            pass

        try:
            if self.buttons[column-3][row+3] == self.buttons[column-2][row+2] == self.buttons[column-1][row+1] == self.buttons[column][row]:
                is_win = True
        except:
            pass

        return is_win

    def check_horizontal(self, column, row):
        is_win = False

        try:
            if self.buttons[column][row] == self.buttons[column+1][row] == self.buttons[column+2][row] == self.buttons[column+3][row]:
                is_win = True
        except:
            pass


        if column >= 3:
            try:
                if self.buttons[column-1][row] == self.buttons[column][row] == self.buttons[column+1][row] == self.buttons[column+2][row]:
                    is_win = True
            except:
                pass

            try:
                if self.buttons[column-2][row] == self.buttons[column-1][row] == self.buttons[column][row] == self.buttons[column+1][row]:
                    is_win = True
            except:
                pass

            try:
                if self.buttons[column-3][row] == self.buttons[column-2][row] == self.buttons[column-1][row] == self.buttons[column][row]:
                    is_win = True
            except:
                pass

        return is_win

    def check_winner(self, column, row):
        is_full = self.check_table()
        is_win = False

        is_win = self.check_vertical(column, row)

        if not is_win:
            is_win = self.check_horizontal(column, row)

        if not is_win:
            is_win = self.check_diagonal(column, row)

        if is_full and not is_win:
            return "TIE"

        elif is_full and is_win or not is_full and is_win:
            return True

        elif not is_full and not is_win:
            return False

    def broadcast(self, message):
        for client in self.clients:
            client.send(f"{message}".encode(FORMAT))

    def switch_turn(self):
        if self.turn == "BLUE":
            self.turn = "RED"
        elif self.turn == "RED":
            self.turn = "BLUE"

    def update_score(self, client):
        self.score[self.clients.index(client)] += 1
        print(f"Player 1 [{self.score[0]}:{self.score[1]}] Player 2\n")
        self.broadcast(f"Player 1 [{self.score[0]}:{self.score[1]}] Player 2")

    def new_match(self, client):
        self.broadcast("NEW")
        self.buttons = [[" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "]]
        self.turn = "BLUE"
        self.giving_color()
        self.client1.send(f"{self.players[0]}".encode(FORMAT))
        self.client2.send(f"{self.players[1]}".encode(FORMAT))

        self.is_stop = False

    def drop_piece(self, column, row, client):
        self.buttons[column][row] = self.players[self.clients.index(client)]
        self.broadcast(f"{column},{row},{self.players[self.clients.index(client)]}")
        print(f"Player {self.clients.index(client) + 1}: {column}, {row}, {self.players[self.clients.index(client)]}\n")

        if self.check_winner(column, row) == "TIE":
            self.is_stop = True
            print("Tie!\n")
            self.broadcast("TIE")
            time.sleep(3)
            self.new_match(client)

        elif self.check_winner(column, row):
            self.is_stop = True
            print(f"Player {self.clients.index(client)+1} wins!\n")
            self.broadcast(self.turn)
            time.sleep(1)
            self.update_score(client)
            time.sleep(3)
            self.new_match(client)

        elif not self.check_winner(column, row):
            self.switch_turn()

    def reset(self):
        self.buttons = [[" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "]]
        self.clients = []
        self.turn = "BLUE"
        self.players = ["", ""]
        self.is_stop = False
        self.score = [0, 0]

    def stop(self):
        print("Game ended!\n")
        for client in self.clients:
            client.send("CLOSE".encode(FORMAT))
            client.close()
        self.reset()

    def handle(self, client):
        while True:
            try:
                message = client.recv(1024).decode(FORMAT)
                if message == "CLOSE":
                    self.stop()
                    break
                else:
                    if self.players[self.clients.index(client)] == self.turn:
                        column = int(message)
                        for row in range(5, -1, -1):
                            if self.buttons[column][row] == " " and not self.is_stop:
                                self.drop_piece(column, row, client)
                                break
            except:
                self.reset()
                print(f"Players: {len(self.clients)}\n")
                print("Waiting for players...\n")
                break

    def receive(self):
        print("Waiting for players...\n")
        while True:
            self.server.listen()
            self.client, self.address = self.server.accept()

            if len(self.clients) == 0:
                self.client1 = self.client

                self.client1.send("YES,1".encode(FORMAT))
                self.clients.append(self.client1)

                print(f"Players: {len(self.clients)}\n")

                thread = threading.Thread(target=self.handle, args=(self.client1,))
                thread.start()

            elif len(self.clients) == 1:
                self.client2 = self.client
                self.client2.send("YES,2".encode(FORMAT))
                self.clients.append(self.client2)

                print(f"Players: {len(self.clients)}\n")

                self.giving_color()

                self.client1.send(f"{self.players[0]}".encode(FORMAT))

                print(f"Player 1: {self.players[0]}")

                self.client2.send(f"{self.players[1]}".encode(FORMAT))

                print(f"Player 2: {self.players[1]}\n")

                for client in self.clients:
                    try:
                        client.send("START".encode(FORMAT))
                    except:
                        self.clients.remove(client)

                thread = threading.Thread(target=self.handle, args=(self.client2,))
                thread.start()

                print("Game started!\n")
                print("Player: column, row, color\n")

            elif len(self.clients) >= 2:
                self.client.send("NO".encode(FORMAT))
                self.client.close()


Server(HOST, PORT)
