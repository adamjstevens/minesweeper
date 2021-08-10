from random import randrange
import tkinter as tk
from tkinter import messagebox
from board import *
from functools import partial
from PIL import Image, ImageTk

TILE_SIZE = 30
INFO_HEIGHT = 60
SMILE_SIZE = INFO_HEIGHT

class MinesweeperApp(tk.Frame):
    def __init__(self, board, master=None):
        super().__init__(master)
        self.master = master 
        self.board = board
        self.frames = []
        self.labels = []
        self.seconds = -1
        self.firstClick = False
        self.gameEnded = False

        self.emptyTiles = self.board.width * self.board.height\
                - self.board.numBombs
        self.infoFrame = tk.Frame(master=self.master, 
                width=TILE_SIZE*self.board.width, 
                height=INFO_HEIGHT, border=0, padx=0, pady=0)
        self.gameFrame = tk.Frame(master=self.master, 
                width=TILE_SIZE*self.board.width,
                height=TILE_SIZE*self.board.height, padx=0, pady=0)
        
        self.winfo_toplevel().title("Minesweeper")

        # Loading images
        self.rst = tk.PhotoImage(file="res/rst.png")
        self.flag = tk.PhotoImage(file="res/flag.png")
        self.wflag = tk.PhotoImage(file="res/wf.png")
        self.bomb = tk.PhotoImage(file="res/b.png")
        self.thebomb = tk.PhotoImage(file="res/tb.png")
        self.non = tk.PhotoImage(file="res/non.png")
        self.zero = tk.PhotoImage(file="res/p0.png")
        self.one = tk.PhotoImage(file="res/p1.png")
        self.two = tk.PhotoImage(file="res/p2.png")
        self.three = tk.PhotoImage(file="res/p3.png")
        self.four = tk.PhotoImage(file="res/p4.png")
        self.five = tk.PhotoImage(file="res/p5.png")

        self.create_widgets()
        self.infoFrame.pack(side = tk.TOP)
        self.gameFrame.pack(side = tk.BOTTOM)

    def update_clock(self):
        if not self.gameEnded and self.firstClick:
            self.seconds += 1
            self.clock.config(text=str(self.seconds))
            self.master.after(1000, self.update_clock)

    def are_coords_valid(self, x, y):
        return not ((x < 0 or x > self.board.width - 1)\
            or (y < 0 or y > self.board.height - 1))

    def reveal_tile(self, x, y):
        tile = self.board.TileGrid[x][y]
        if tile.hasFlag(): return
        label = self.labels[x][y]
        if not tile.hasBomb(): 
            self.frames[x][y].unbind("<Button-1>")
            self.frames[x][y].unbind("<Button-3>")
            self.labels[x][y].unbind("<Button-1>")
            self.labels[x][y].unbind("<Button-3>")
        tile.reveal()
        if self.board.TileGrid[x][y].hasBomb():
            label.config(image=self.thebomb)
            self.finish(x, y)
        else:
            # Setting the photos of revelation
            numBombs = self.board.TileGrid[x][y].getSurrounding()
            if numBombs == 0: 
                label.config(image=self.zero)
            elif numBombs == 1:
                label.config(image=self.one)
            elif numBombs == 2: 
                label.config(image=self.two)
            elif numBombs == 3: 
                label.config(image=self.three)
            elif numBombs == 4: 
                label.config(image=self.four)
            elif numBombs == 5: 
                label.config(image=self.five)
            self.master.update_idletasks()
            
        self.emptyTiles -= 1

        if (self.emptyTiles == 0):
            messagebox.showinfo("You won!")
            self.finish(-1, -1)

        if (self.board.TileGrid[x][y].getSurrounding() in [0] and\
                not self.board.TileGrid[x][y].hasBomb()):
            self.reveal_empty_surrounding(x, y)

    def reveal_empty_surrounding(self, x, y):
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if not (i == 0 and j == 0):
                    if self.are_coords_valid(x + i, y + j):
                        if (not self.board.TileGrid[x + i][y + j].isRevealed()):
                            self.reveal_tile(x + i, y + j)

    def left_click(self, x, y, e):
        if self.gameEnded: return
        if not self.firstClick: 
            self.board.generate_bombs(x, y)
            self.firstClick = True
            self.update_clock()
        if not self.board.TileGrid[x][y].hasFlag(): self.reveal_tile(x, y)
        
    def right_click(self, x, y, e):
        if self.gameEnded: return
        hasFlag = self.board.TileGrid[x][y].toggleFlag()
        if hasFlag:
            self.labels[x][y].config(image=self.flag)
        else:
            self.labels[x][y].config(image=self.non)

    def finish(self, x, y):
        self.gameEnded = True
        for i in range(self.board.width):
            for j in range(self.board.height):
                if (i != x or j != y):
                    tile = self.board.TileGrid[i][j]
                    if (tile.hasBomb()):
                        self.labels[i][j].config(image = self.bomb)
                    if (tile.hasFlag() and not tile.hasBomb()):
                        self.labels[i][j].config(image = self.wflag)

    def reset(self):
        self.seconds = 0
        self.clock.config(text="0")
        self.emptyTiles = self.board.width * self.board.height\
                - self.board.numBombs
        self.board.reset()
        self.firstClick = False
        self.gameEnded = False
        for i in range(self.board.width):
            for j in range(self.board.height):
                tile = self.frames[i][j]
                label = self.labels[i][j]
                label.config(image=self.non)
                lclick_with_args = partial(self.left_click, i, j)
                rclick_with_args = partial(self.right_click, i, j)
                tile.bind("<Button-1>", lclick_with_args)
                label.bind("<Button-1>", lclick_with_args)
                tile.bind("<Button-3>", rclick_with_args)
                label.bind("<Button-3>", rclick_with_args)

    def create_widgets(self):
        # GAME FRAME
        for i in range(self.board.width):
            col_frames = []
            col_labels = []
            for j in range(self.board.height):
                lclick_with_args = partial(self.left_click, i, j)
                rclick_with_args = partial(self.right_click, i, j)

                tile = tk.Frame(self.gameFrame, height=TILE_SIZE, 
                    width=TILE_SIZE, relief="raised", padx=0, pady=0, 
                    highlightthickness=0, borderwidth=0)
                tile.pack_propagate(0)
                label = tk.Label(master=tile, width=TILE_SIZE, padx=0, pady=0,
                        image=self.non, highlightthickness=0, borderwidth=0)
                label.pack()

                tile.bind("<Button-1>", lclick_with_args)
                label.bind("<Button-1>", lclick_with_args)

                tile.bind("<Button-3>", rclick_with_args)
                label.bind("<Button-3>", rclick_with_args)

                tile.grid(column=i, row=j)
                col_frames.append(tile)
                col_labels.append(label)
                
            self.frames.append(col_frames)
            self.labels.append(col_labels)
        
        # INFO FRAME 
        resetBtn = tk.Button(master=self.infoFrame, image=self.rst, 
                width=SMILE_SIZE, height=SMILE_SIZE, command=self.reset,
                border=0, padx=0, pady=0)
        resetBtn.grid(column=2, row=0)
        padLbl = tk.Label(master=self.infoFrame, width=3)
        padLbl.grid(column=4,row=0)
        self.clock = tk.Label(master=self.infoFrame, text="0", 
                padx=0, pady=0, border=0)
        self.clock.grid(column=5, row=0)

def main():
    width = 30
    height = 16
    bombs = 99
    
    grid = Board(width, height, bombs)
    root = tk.Tk()
    root.resizable(False, False)
    root.geometry(f"{width*TILE_SIZE}x{INFO_HEIGHT + height*TILE_SIZE + 5}")
    msapp = MinesweeperApp(grid, master=root)
    msapp.mainloop()

if __name__ == "__main__":
    main()