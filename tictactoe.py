from random import randint

PLAYER = 1
AI = 2

class GameBoard():
    markers = [' ', 'X', 'O']

    def __init__(self):
        self.state = [0] * 9
        self.human_turn = True
        self.turn = 0

    def place(self, tile, player):
        self.state[tile] = player
        self.turn += 1

    def move_human(self, move=None):
        self.human_turn = False
        while not isinstance(move, int) or self.state[move]:
            move = int(input("Move: "))
        self.place(move, PLAYER)

    def move_ai_random(self):
        move = None
        while not isinstance(move, int) or self.state[move]:
            move = randint(0, 8)
        self.place(move, AI)
        self.human_turn = True

    def move_ai_block(self):
        for i in range(len(self.state)):
            if self.state[i] == 0:
                self.state[i] = AI
                if self.check_winner(AI):
                    self.place(i, AI)
                    return True
                self.state[i] = 0
        for i in range(len(self.state)):
            if self.state[i] == 0:
                self.state[i] = PLAYER
                if self.check_winner(PLAYER):
                    self.place(i, AI)
                    return True
                self.state[i] = 0

    def move_ai_naive(self):
        self.human_turn = True
        if not self.move_ai_block():
            self.move_ai_random()
    
    def move_ai_good(self):
        self.human_turn = True
        if self.move_ai_block():
            return
        if self.turn == 0:
            self.place(4, AI)
            return
        elif self.turn == 1:
            if self.state[4]:
                self.place(0, AI)
            else:
                self.place(4, AI)
            return
        elif self.turn == 3 and self.state[4] == AI:
            if (
                self.state[0] and self.state[8] or
                self.state[2] and self.state[6]
            ):
                self.place(1, AI)
                return
            elif not (self.state[1] or self.state[7]):
                self.place(7, AI)
                return
            elif not (self.state[3] or self.state[5]):
                self.place(3, AI)
                return
        self.move_ai_random()

    def display(self):
        for row in range(3):
            for col in range(3):
                print(GameBoard.markers[self.state[row*3 + col]], end='')
            print()
        print()

    def check_winner(self, player):
        return (
                # horizontal row
                self.state[0] == self.state[1] == self.state[2] == player or
                self.state[3] == self.state[4] == self.state[5] == player or
                self.state[6] == self.state[7] == self.state[8] == player
            ) or (
                # vertical row
                self.state[0] == self.state[3] == self.state[6] == player or
                self.state[1] == self.state[4] == self.state[7] == player or
                self.state[2] == self.state[5] == self.state[8] == player
            ) or (
                # diagonal
                self.state[0] == self.state[4] == self.state[8] == player or
                self.state[2] == self.state[4] == self.state[6] == player
            )
    
    def check_cat(self):
        return self.turn == 9
    
    def game_over(self):
        return self.check_cat() or self.check_winner(AI) or self.check_winner(PLAYER)

    def clear(self):
        for i in range(len(self.state)):
            self.state[i] = 0

def main():
    print("hi tic tac toe")
    board = GameBoard()
    while True:
        if board.human_turn:
            board.move_human()
            board.display()
            if board.check_winner(PLAYER):
                print("Player wins")
                break
        else:
            board.move_ai_good()
            board.display()
            if board.check_winner(AI):
                print("AI wins")
                break
        if board.turn == 9:
            print("Cat game")
            break

if __name__ == "__main__":
    main()