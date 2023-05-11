import tkinter as tk
import threading
import ctypes
import pickle


class Socket_TTT(threading.Thread):
    def __init__(self, P1='Player1', P2='Player2', Sock=None, Turn='Player1'):
        threading.Thread.__init__(self)

        self.Player_One = P1
        self.Player_Two = P2
        self.Sock = Sock
        self.FirstTurn = Turn
        self.Turn = Turn
        self.All_Points = []
        self.Player1_Moves = []
        self.Player2_Moves = []

        self.winning_possibilities = [
            self.WinningPossibility(1, 1, 1, 2, 1, 3),
            self.WinningPossibility(2, 1, 2, 2, 2, 3),
            self.WinningPossibility(3, 1, 3, 2, 3, 3),
            self.WinningPossibility(1, 1, 2, 1, 3, 1),
            self.WinningPossibility(1, 2, 2, 2, 3, 2),
            self.WinningPossibility(1, 3, 2, 3, 3, 3),
            self.WinningPossibility(1, 1, 2, 2, 3, 3),
            self.WinningPossibility(3, 1, 2, 2, 1, 3)
        ]

    def run(self):
        self.My_ttt = tk.Tk()
        self.My_ttt.resizable(False, False)
        self.My_ttt.title("Game Board")
        self.My_ttt.configure(bg='#000000')

        tk.Label(self.My_ttt, text="Online Dooz!    " + self.Player_One, bg='#000000', fg='#FF006E', font=('comic sans ms', 25)).pack()

        self.status_label = tk.Label(self.My_ttt, text=self.Turn + "'s turn", font=('comic sans ms', 15), bg='#000000', fg='#FFFFFF')

        self.status_label.pack(fill=tk.X, padx=25)

        self.play_again_button = tk.Button(self.My_ttt, text='Play again', bg='#000000', fg='#FFFFFF', font=('comic sans ms', 15), command=self.play_again)
        
        self.Area = tk.Frame(self.My_ttt, width=300, height=300, bg='white')

        for x in range(1, 4):
            for y in range(1, 4):
                self.All_Points.append(self.Noghat(self, x, y))

        self.Area.pack(pady=10, padx=10)

        self.Exit_button = tk.Button(self.My_ttt, text='Exit', bg='#000000', fg='#FFFFFF' ,font=('comic sans ms', 15), command=self.finish).pack()

        self.My_ttt.mainloop()

    def play_again(self):
        self.Turn = self.FirstTurn

        for point in self.All_Points:
            point.button.configure(state=tk.NORMAL)
            point.reset(self)

        self.status_label.configure(text=self.Turn + "'s turn")
        self.play_again_button.pack_forget()

    def finish(self):
        try:
            self.Sock.send(pickle.dumps('finish'))
        except OSError:
            pass
        self.raise_exception()
        self.Sock.close()
        self.My_ttt.destroy()

    def disable_game(self):
        for point in self.All_Points:
            point.button.configure(state=tk.DISABLED)

        self.play_again_button.pack()

    def check_win(self):
        for possibility in self.winning_possibilities:
            if possibility.check(self, self.Player_One):
                self.status_label.configure(text=self.Player_One + " won!")
                self.disable_game()
                return
            elif possibility.check(self, self.Player_Two):
                self.status_label.configure(text=self.Player_Two + " won!")
                self.disable_game()
                return

        if len(self.Player1_Moves) + len(self.Player2_Moves) == 9:
            self.status_label.configure(text="Draw!")
            self.disable_game()

    def set_with_code(self, code):
        self.All_Points[code].set_two()

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    class Noghat:
        def __init__(self, inherit1, x, y):
            self.x = x
            self.y = y
            self.value = None
            self.inherit = inherit1
            self.button = tk.Button(inherit1.Area, text="", border=1, highlightbackground='black',
                                    bg='white', width=20, height=10, command=self.set_one)
            self.button.grid(row=x, column=y)

        def set_one(self):
            if not self.value:

                if self.inherit.Turn == self.inherit.Player_One:
                    self.value = self.inherit.Turn
                    self.button.configure(text=self.inherit.Turn, bg='#a322df', fg='#FFFFFF')
                    self.inherit.Player1_Moves.append(self)
                    self.inherit.Turn = self.inherit.Player_Two
                    self.inherit.status_label.configure(text=self.inherit.Player_Two + "'s turn")
                    self.inherit.Sock.send(pickle.dumps(str((self.x-1)*3+self.y-1)))

            self.inherit.check_win()

        def set_two(self):
            if not self.value:

                if self.inherit.Turn == self.inherit.Player_Two:
                    self.value = self.inherit.Turn
                    self.button.configure(text=self.inherit.Turn, bg='#19e0ee', fg='#000000')
                    self.inherit.Player2_Moves.append(self)
                    self.inherit.Turn = self.inherit.Player_One
                    self.inherit.status_label.configure(text=self.inherit.Player_One + "'s turn")

            self.inherit.check_win()

        def reset(self, inherit):
            self.button.configure(text="", bg='white')
            if self.value == inherit.Player_One:
                inherit.Player1_Moves.remove(self)
            elif self.value == inherit.Player_Two:
                inherit.Player2_Moves.remove(self)
            self.value = None

    class WinningPossibility:

        def __init__(self, x1, y1, x2, y2, x3, y3):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
            self.x3 = x3
            self.y3 = y3

        def check(self, inherit, for_chr):
            p1_satisfied = False
            p2_satisfied = False
            p3_satisfied = False

            if for_chr == inherit.Player_One:
                for point in inherit.Player1_Moves:
                    if point.x == self.x1 and point.y == self.y1:
                        p1_satisfied = True
                    elif point.x == self.x2 and point.y == self.y2:
                        p2_satisfied = True
                    elif point.x == self.x3 and point.y == self.y3:
                        p3_satisfied = True

            elif for_chr == inherit.Player_Two:
                for point in inherit.Player2_Moves:
                    if point.x == self.x1 and point.y == self.y1:
                        p1_satisfied = True
                    elif point.x == self.x2 and point.y == self.y2:
                        p2_satisfied = True
                    elif point.x == self.x3 and point.y == self.y3:
                        p3_satisfied = True

            return all([p1_satisfied, p2_satisfied, p3_satisfied])

class FirstPage(threading.Thread):
    def __init__(self, My_Sock, thread, name):
        threading.Thread.__init__(self)
        self.My_Sock = My_Sock
        self.thread = thread
        self.name = name

    def run(self):
        self.My_ttt = tk.Tk()
        self.My_ttt.geometry("500x500")
        self.My_ttt.resizable(False, False)
        self.My_ttt.title("Mat Project")
        self.My_ttt.configure(bg='#000000')


        tk.Label(self.My_ttt, text=self.name, width=15, height=2, bg='#000000', fg='#FF006E', font=('comic sans ms', 25)).pack(pady=10)

        tk.Button(self.My_ttt, text="New Game", width=15, height=2, bg='#FFFFFF', fg='#FF006E', font=('comic sans ms', 25), command=self.new_game).pack(pady=50)

        tk.Button(self.My_ttt, text="Exit", width=15, height=2, bg='#FFFFFF', fg='#FF006E', font=('comic sans ms', 25), command=self.close).pack()

        self.My_ttt.mainloop()

    def new_game(self):
        self.My_Sock.send(pickle.dumps('NewGame'))

    def close(self):
        self.My_Sock.send(pickle.dumps('Exit'))
        self.raise_exception()
        self.My_Sock.close()
        self.My_ttt.destroy()

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

class ShowActiveNodes(threading.Thread):
    def __init__(self, ActiveNodes, src_addr, sock):
        threading.Thread.__init__(self)
        self.ActiveNodes = ActiveNodes
        self.addr = src_addr
        self.My_Sock = sock

    def run(self):
        self.My_ttt = tk.Tk()
        self.My_ttt.geometry("500x500")
        self.My_ttt.resizable(False, False)
        self.My_ttt.title("Select Partner")
        self.My_ttt.configure(bg='#000000')

        self.Area = tk.Frame(self.My_ttt, width=300, height=300, bg='white')

        if len(self.ActiveNodes) > 1:
            for addr in self.ActiveNodes:
                if addr != self.addr:
                    self.create_rows(self, addr)
                    self.Area.pack()
        else:
            self.No_Player = tk.Label(self.My_ttt, text='No Player').pack()

        self.Exit_button = tk.Button(self.My_ttt, text='Exit', bg='#000000', fg='#FFFFFF' ,font=('comic sans ms', 15), command=self.finish).pack(side='bottom')

        self.My_ttt.mainloop()

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')

    def finish(self):
        self.raise_exception()
        self.My_ttt.destroy()

    class create_rows:
        def __init__(self, inherit, addr):
            self.addr = addr
            self.inherit = inherit

            self.Area1 = tk.Frame(inherit.Area, bg='#000000', width=300, height=300)

            self.name_and_address = tk.Label(self.Area1, text=addr[2], bg='#000000', fg='#FF006E', font=('comic sans ms', 25)).pack(side=tk.LEFT, padx=15, pady=10)
            
            self.connect = tk.Button(self.Area1, text='Connect', bg='#FFFFFF', fg='#FF006E', font=('comic sans ms', 25), command=self.set).pack(side=tk.RIGHT, padx=15, pady=10)
            
            self.Area1.pack()

        def set(self):
            self.inherit.My_Sock.send(pickle.dumps(
                'select ' + self.addr[0] + ' ' + str(self.addr[1]) + ' ' + self.addr[2]))
