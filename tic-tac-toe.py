class GameBoard():
    markers = [' ', 'X', 'O']

    def __init__(self):
        self.state = [0] * 9
        self.human_turn = True

    def place(self, tile):
        self.state[tile] = 1

    def move_human(self):
        move = None
        while not move:
            move = input("Move: ")
        self.place(int(move))

    def move_ai(self):
        pass

    def display(self):
        for row in range(3):
            for col in range(3):
                print(GameBoard.markers[self.state[row*3 + col]], end='')
            print()

def main():
    print("hi tic tac toe")
    board = GameBoard()
    while True:
        if board.human_turn:
            board.move_human()
        else:
            board.move_ai()
        board.display()

        

if __name__ == "__main__":
    main()