import socket
import threading
from tkinter import *
from PIL import Image, ImageTk

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
FORMAT = 'utf-8'


class Client:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        is_allow = self.client.recv(1024).decode(FORMAT)

        if is_allow == "NO":
            self.client.close()

        elif is_allow.split(",")[0] == "YES":
            print(f"Player {is_allow.split(',')[1]}\n")
            self.player = is_allow.split(',')[1]
            self._stop = False
            self.player_color = self.client.recv(1024).decode(FORMAT)
            self.turn = "BLUE"

            if self.player_color == "BLUE":
                print("You're blue\n")
            elif self.player_color == "RED":
                print("You're red\n")

            self.running = True

            receive_thread = threading.Thread(target=self.receive_loop)
            receive_thread.start()

    def gui_loop(self):
        self.window = Tk()
        self.window.title("Connect4")
        self.window.geometry("600x600+100+100")
        self.window.minsize(600, 600)
        self.window.resizable(False, False)
        self.window['bg'] = '#17202A'
        self.window.protocol("WM_DELETE_WINDOW", self.close)

        self.empty_image = ImageTk.PhotoImage(Image.open("Images/empty.png"))
        self.blue_image = ImageTk.PhotoImage(Image.open("Images/Blue.png"))
        self.red_image = ImageTk.PhotoImage(Image.open("Images/Red.png"))
        self.redSmall_image = ImageTk.PhotoImage(Image.open("Images/Red.png").resize((25, 25)), Image.Resampling.LANCZOS)
        self.blueSmall_image = ImageTk.PhotoImage(Image.open("Images/Blue.png").resize((25, 25)), Image.Resampling.LANCZOS)

        self.profile_label = Label(self.window, text=f"Player {self.player} - {self.player_color}", font=("Roboto", 8), bg="#17202A", fg="white", justify=CENTER)
        self.profile_label.place(x=60, y=30, anchor=CENTER)

        self.turn_label = Label(self.window, text=" ", font=("Roboto", 14), bg="#17202A", fg="white", justify=CENTER)
        self.turn_label.place(x=300, y=30, anchor=CENTER)

        self.score_label = Label(self.window, text="Player 1 [0:0] Player 2", font=("Roboto", 10), bg="#17202A", fg="white", justify=CENTER)
        self.score_label.place(x=300, y=60, anchor=CENTER)

        self.table = Frame(self.window, bg="#17202A")
        self.table.place(x=300, y=330, anchor=CENTER)

        if self.player_color == "BLUE":
            self.turn_label.config(text=" Your turn", image=self.blueSmall_image, compound=LEFT)
        elif self.player_color == "RED":
            self.turn_label.config(text=" Opponent's turn", image=self.blueSmall_image, compound=LEFT)

        print("Game started!\n")

        self.creating_buttons()
        self.window.mainloop()

    def creating_buttons(self):
        self.buttons = [[" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "],
                        [" ", " ", " ", " ", " ", " "]]

        for column in range(7):
            for row in range(5, -1, -1):
                self.buttons[column][row] = Button(self.table, text=" ",
                                                   image=self.empty_image,
                                                   width=70,
                                                   height=70,
                                                   borderwidth=2,
                                                   command=lambda column=column, row=row: self.drop_piece(column,),
                                                   compound=CENTER)
                self.buttons[column][row].grid(row=row, column=column, padx=1, pady=1)

    def close(self):
        try:
            self.client.send("CLOSE".encode(FORMAT))
        except:
            self.running = False
            self.client.close()
            self.window.quit()

    def drop_piece(self, column):
        self.client.send(f"{column}".encode(FORMAT))

    def reset(self):
        self.turn = "BLUE"
        self.player_color = self.client.recv(1024).decode(FORMAT)

        if self.player_color == "BLUE":
            self.turn_label.config(text=" Your turn", image=self.blueSmall_image, compound=LEFT)
        elif self.player_color == "RED":
            self.turn_label.config(text=" Opponent's turn", image=self.blueSmall_image, compound=LEFT)

        self.profile_label.config(text=f"Player {self.player} - {self.player_color}")

        for column in range(7):
            for row in range(5, -1, -1):
                self.buttons[column][row].config(text=" ",
                                                 fg="#5DADE2",
                                                 activeforeground="#5DADE2",
                                                 image=self.empty_image)

    def receive_loop(self):
        while self.running:
            try:
                message = self.client.recv(1024).decode(FORMAT)

                if message == "START":
                    gui_thread = threading.Thread(target=self.gui_loop)
                    gui_thread.start()

                elif message == "CLOSE":
                    print("Closing!")
                    self.running = False
                    self.client.close()
                    self.window.quit()

                elif message == "NEW":
                    self.reset()

                elif message == "RED":
                    self.turn_label['text'] = " Red wins!"
                    self.turn_label["image"] = self.redSmall_image
                    score = self.client.recv(1024).decode(FORMAT)
                    self.score_label['text'] = score

                elif message == "BLUE":
                    self.turn_label['text'] = " Blue wins!"
                    self.turn_label["image"] = self.blueSmall_image
                    score = self.client.recv(1024).decode(FORMAT)
                    self.score_label['text'] = score

                elif message == "TIE":
                    self.turn_label['text'] = "Tie!"

                else:
                    column = int(message.split(",")[0])
                    row = int(message.split(",")[1])

                    if message.split(",")[2] == "BLUE":
                        self.buttons[column][row].config(text="BLUE",
                                                            fg="#5DADE2",
                                                            activeforeground="#5DADE2",
                                                            image=self.blue_image)
                    elif message.split(",")[2] == "RED":
                        self.buttons[column][row].config(text="RED",
                                                            fg="#EC7063",
                                                            activeforeground="#EC7063",
                                                            image=self.red_image)

                    if self.turn_label["text"] == " Your turn":
                        self.turn_label["text"] = " Opponent's turn"
                    elif self.turn_label["text"] == " Opponent's turn":
                        self.turn_label["text"] = " Your turn"

                    if self.turn == "BLUE":
                        self.turn = "RED"
                        self.turn_label["image"] = self.redSmall_image
                    elif self.turn == "RED":
                        self.turn = "BLUE"
                        self.turn_label["image"] = self.blueSmall_image


            except:
                print("Error")
                self.running = False
                self.client.close()
                self.window.quit()


Client(HOST, PORT)
