import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    slots = []
    pawns = []
    white_pawn_count = black_pawn_count = 0
    white_turn = True

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.centralWidget = QWidget()

        self.setFixedSize(600, 600)
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle("Checkers")

        self.background = QGridLayout(self.centralWidget)
        self.background.setSpacing(0)
        self.setLayout(self.background)

        self.reset_game()
        self.draw_ui()
        self.show()

    def reset_game(self):
        self.slots: list[list] = []
        self.pawns = []
        self.white_pawn_count = self.black_pawn_count = 0
        self.white_turn = True

        self.draw_board()
        self.init_pawns()

    def draw_board(self):
        for i in range(9):
            self.slots.append([])

            for j in range(9):
                label = QLabel(self.centralWidget)

                if i == 0:
                    if j != 0:
                        label.setText(chr(ord('A') + j-1))
                        label.setAlignment(QtCore.Qt.AlignCenter)
                        label.setMaximumHeight(18)
                else:
                    if j == 0:
                        label.setText(str(i))
                        label.setAlignment(QtCore.Qt.AlignCenter)
                        label.setMaximumWidth(18)
                    else:
                        if (i + j) % 2 == 0:
                            label.setStyleSheet("background: #c9c7c7")
                        else:
                            label.setStyleSheet("background: black")
                        self.slots[i-1].append(label)

                self.background.addWidget(label, i, j)

    def init_pawns(self):
        for i in range(3):
            if i % 2 == 0:
                for j in range(0, 7, 2):
                    self.create_new_black_pawn(j, i)
            else:
                for j in range(1, 8, 2):
                    self.create_new_black_pawn(j, i)

        for i in range(5, 8):
            if i % 2 == 0:
                for j in range(1, 8, 2):
                    self.create_new_white_pawn(j, i)
            else:
                for j in range(0, 7, 2):
                    self.create_new_white_pawn(j, i)

    def create_new_white_pawn(self, x: int, y: int):
        self.create_new_pawn_on(x, y, "#c9c7c7")

    def create_new_black_pawn(self, x: int, y: int):
        self.create_new_pawn_on(x, y, "black")

    def create_new_pawn_on(self, x: int, y: int, color: str):
        pawn = QPushButton(self.slots[y][x])
        pawn.setStyleSheet("background: " + color + "; border-radius: 30;")
        pawn.setGeometry(5, 4, 60, 60)
        pawn.clicked.connect(self.scream)
        self.pawns.append(pawn)

    def move_pawn_to(self, pawn: QWidget, x: int, y: int):
        pawn.setParent(self.slots[y][x])

    def draw_ui(self):
        reset_button = QPushButton(self.centralWidget)
        reset_button.setText("RESET")
        self.background.addWidget(reset_button, 9, 4, 1, 2)

    @staticmethod
    def scream():
        print("AHH!")


stylesheet = """
    MainWindow {
        background-color: #275c0a;
    }
"""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    win = MainWindow()
    sys.exit(app.exec_())
