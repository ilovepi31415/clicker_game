import random

class Quiz():
    operations = ['+', '-', '*']
    def __init__(self):
        self.answer = None
        self.options = [None] * 3
        self.problem = ''

    def generate_problem(self):
        value = random.randint(1, 9)
        message = str(value)
        options = set()
        for _ in range(3):
            op = random.choice(self.operations)
            num = random.randint(1, 9)
            message += f' {op} {num}'
            match op:
                case '+':
                    value += num
                case '-':
                    value -= num
                case '*':
                    value *= num
        message += ' = ?'
        self.answer = value
        self.problem = message
        options.add(value)
        while len(options) < 3:
            options.add(value + random.randint(-5, 5))
        self.options = list(options)

def main():
    print("Welcome to the math quiz")
    quiz = Quiz()
    while True:
        quiz.generate_problem()
        print(quiz.problem)
        guess = input("")
        if int(guess) != quiz.answer:
            print(f"wrong, it was {quiz.answer}")
            break


if __name__ == "__main__":
    main()