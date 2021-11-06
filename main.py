import sys

# import sip
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QApplication, QLabel, QMainWindow, QMessageBox


class FieldButton(QPushButton):
    x: int
    y: int
    is_white: bool

    def __init__(self, parent=None):
        super(FieldButton, self).__init__(parent)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y


class Pawn(QPushButton):
    is_white: bool
    can_go_back = False
    is_killed = False
    parent: FieldButton

    def __init__(self, parent: FieldButton = None):
        super(Pawn, self).__init__(parent)
        self.parent = parent

    def get_x(self):
        return self.parent.get_x()

    def get_y(self):
        return self.parent.get_y()

    def setParent(self, parent: FieldButton) -> None:
        super(Pawn, self).setParent(parent)
        self.parent = parent


class MainWindow(QMainWindow):
    slots: list
    field_buttons: list
    selected_pawn: Pawn
    white_pawn_count: int
    black_pawn_count: int
    white_turn = True
    pawn_streak = False
    white_color = "#c9c7c7"
    black_color = "#303030"

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

        self.turn_indicator_white = QLabel(self.centralWidget)
        self.turn_indicator_black = QLabel(self.centralWidget)
        self.background.addWidget(self.turn_indicator_white, 9, 0, 1, 4)
        self.background.addWidget(self.turn_indicator_black, 9, 6, 1, 3)
        self.flick_turn_indicator()

        reset_button = QPushButton(self.centralWidget)
        reset_button.setText("RESET")
        reset_button.clicked.connect(self.reset_game)
        self.background.addWidget(reset_button, 9, 4, 1, 2)

        self.show()

    def reset_game(self):
        self.slots: list[list] = []
        self.field_buttons: list[list[FieldButton]] = []
        self.selected_pawn = None
        self.white_pawn_count = self.black_pawn_count = 0
        if not self.white_turn:
            self.white_turn = True
            self.flick_turn_indicator()
        self.white_turn = True
        self.pawn_streak = False

        self.draw_board()
        self.init_pawns()

    def draw_board(self):
        for i in range(9):
            self.slots.append([])
            if i != 0:
                self.field_buttons.append([])

            for j in range(9):
                label = QLabel(self.centralWidget)

                if i == 0:
                    if j != 0:
                        label.setText(chr(ord('A') + j - 1))
                        label.setAlignment(QtCore.Qt.AlignCenter)
                        label.setMaximumHeight(18)
                else:
                    if j == 0:
                        label.setText(str(i))
                        label.setAlignment(QtCore.Qt.AlignCenter)
                        label.setMaximumWidth(18)
                    else:
                        field_button = FieldButton(label)
                        field_button.x = j - 1
                        field_button.y = i - 1
                        field_button.setGeometry(0, 0, 72, 68)
                        field_button.setStyleSheet("background: transparent;")
                        field_button.clicked.connect(
                            lambda _, x=field_button.x, y=field_button.y: self.field_method(x, y))

                        if (i + j) % 2 == 0:
                            label.setStyleSheet("background: #c9c7c7")
                            field_button.is_white = True
                        else:
                            label.setStyleSheet("background: black")
                            field_button.is_white = False

                        self.slots[i - 1].append(label)
                        self.field_buttons[i - 1].append(field_button)

                self.background.addWidget(label, i, j)

    def init_pawns(self):
        for i in range(3):
            if i % 2 == 1:
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
        self.create_new_pawn_on(x, y, True)
        self.white_pawn_count += 1

    def create_new_black_pawn(self, x: int, y: int):
        self.create_new_pawn_on(x, y, False)
        self.black_pawn_count += 1

    def create_new_pawn_on(self, x: int, y: int, is_white: bool):
        pawn = Pawn(self.field_buttons[y][x])
        pawn.is_white = is_white
        if is_white:
            pawn.setStyleSheet("background: " + self.white_color + "; border-radius: 30;")
        else:
            pawn.setStyleSheet("background: " + self.black_color + "; border-radius: 30;")
        pawn.setGeometry(5, 4, 60, 60)
        pawn.clicked.connect(lambda _, pobj=pawn: self.pawn_method(pobj))

    def move_pawn_to(self, x: int, y: int) -> bool:
        field: FieldButton = self.field_buttons[y][x]
        if len(field.children()) > 0 or self.selected_pawn is None:
            return False

        if field.is_white:
            return False

        x_diff = self.selected_pawn.get_x() - x
        y_diff = self.selected_pawn.get_y() - y

        if x_diff == 2 and y_diff == 2:
            if len(self.field_buttons[y + 1][x + 1].children()) > 0 and \
                    not self.is_teammate_to(self.selected_pawn, self.field_buttons[y + 1][x + 1].children()[0]):
                self.kill_pawn(self.field_buttons[y + 1][x + 1].children()[0])
                self.pawn_streak = True
            else:
                return False
        elif x_diff == 2 and y_diff == -2:
            if len(self.field_buttons[y - 1][x + 1].children()) > 0 and \
                    not self.is_teammate_to(self.selected_pawn, self.field_buttons[y - 1][x + 1].children()[0]):
                self.kill_pawn(self.field_buttons[y - 1][x + 1].children()[0])
                self.pawn_streak = True
            else:
                return False
        elif x_diff == -2 and y_diff == 2:
            if len(self.field_buttons[y + 1][x - 1].children()) > 0 and \
                    not self.is_teammate_to(self.selected_pawn, self.field_buttons[y + 1][x - 1].children()[0]):
                self.kill_pawn(self.field_buttons[y + 1][x - 1].children()[0])
                self.pawn_streak = True
            else:
                return False
        elif x_diff == -2 and y_diff == -2:
            if len(self.field_buttons[y - 1][x - 1].children()) > 0 and \
                    not self.is_teammate_to(self.selected_pawn, self.field_buttons[y - 1][x - 1].children()[0]):
                self.kill_pawn(self.field_buttons[y - 1][x - 1].children()[0])
                self.pawn_streak = True
            else:
                return False
        elif [x_diff, y_diff] not in [[1, 1], [1, -1], [-1, 1], [-1, -1]]:
            return False
        else:
            if self.selected_pawn.is_white:
                if self.selected_pawn.get_y() - y < 0:
                    if not self.selected_pawn.can_go_back:
                        return False
            else:
                if self.selected_pawn.get_y() - y > 0:
                    if not self.selected_pawn.can_go_back:
                        return False

        if self.selected_pawn.is_white and y == 0:
            self.selected_pawn.can_go_back = True
            self.selected_pawn.setStyleSheet("background: " + self.white_color + "; " +
                                             "border-radius: 30; border-style: solid; " +
                                             "border-color: #306ef2; border-width: 3")
        elif not self.selected_pawn.is_white and y == 7:
            self.selected_pawn.can_go_back = True
            self.selected_pawn.setStyleSheet("background: " + self.black_color + "; " +
                                             "border-radius: 30; border-style: solid; " +
                                             "border-color: #306ef2; border-width: 3")

        self.selected_pawn.setParent(field)
        self.selected_pawn.show()
        if self.has_available_kills(self.selected_pawn):
            if self.pawn_streak:
                return True
        else:
            self.pawn_streak = False

        self.selected_pawn = None
        self.white_turn = not self.white_turn
        self.flick_turn_indicator()

        return True

    def kill_pawn(self, pawn: Pawn):
        if pawn.is_white:
            self.white_pawn_count -= 1
        else:
            self.black_pawn_count -= 1

        pawn.is_killed = True
        pawn.setParent(None)

        if self.white_pawn_count == 0:
            self.announce_victory_for_color(False)
        elif self.black_pawn_count == 0:
            self.announce_victory_for_color(True)

    def has_available_kills(self, pawn: Pawn):
        x = pawn.get_x()
        y = pawn.get_y()

        if x > 1:
            if y > 1 and \
                    len(self.field_buttons[y - 1][x - 1].children()) > 0 and \
                    not self.is_teammate_to(pawn, self.field_buttons[y - 1][x - 1].children()[0]) and \
                    len(self.field_buttons[y - 2][x - 2].children()) == 0:
                return True
            if y < 6 and len(self.field_buttons[y + 1][x - 1].children()) > 0 and \
                    not self.is_teammate_to(pawn, self.field_buttons[y + 1][x - 1].children()[0]) and \
                    len(self.field_buttons[y + 2][x - 2].children()) == 0:
                return True
        if x < 6:
            if y > 1 and len(self.field_buttons[y - 1][x + 1].children()) > 0 and \
                    not self.is_teammate_to(pawn, self.field_buttons[y - 1][x + 1].children()[0]) and \
                    len(self.field_buttons[y - 2][x + 2].children()) == 0:
                return True
            if y < 6 and len(self.field_buttons[y + 1][x + 1].children()) > 0 and \
                    not self.is_teammate_to(pawn, self.field_buttons[y + 1][x + 1].children()[0]) and \
                    len(self.field_buttons[y + 2][x + 2].children()) == 0:
                return True

        return False

    @staticmethod
    def is_teammate_to(caller: Pawn, target: Pawn):
        return caller.is_white == target.is_white

    @staticmethod
    def field_has_pawn_of_color(field: FieldButton, is_white: bool):
        if len(field.children()) > 0:
            return False

        return field.children()[0].is_white == is_white

    def flick_turn_indicator(self):
        if self.white_turn:
            self.turn_indicator_white.setStyleSheet("background-color: white; color: black")
            self.turn_indicator_white.setText("WHITE MOVES!")
            self.turn_indicator_black.setStyleSheet("")
            self.turn_indicator_black.setText("")
        else:
            self.turn_indicator_black.setStyleSheet("background-color: black; color: white")
            self.turn_indicator_black.setText("BLACK MOVES!")
            self.turn_indicator_white.setStyleSheet("")
            self.turn_indicator_white.setText("")

    def pawn_method(self, pawn: Pawn):
        if self.pawn_streak:
            return

        if (self.white_turn and pawn.is_white) or (not self.white_turn and not pawn.is_white):
            self.selected_pawn = pawn

    def field_method(self, x: int, y: int):
        self.move_pawn_to(x, y)

    def announce_victory_for_color(self, is_white):
        text: str
        if is_white:
            text = "WHITE WON!"
        else:
            text = "BLACK WON"

        QMessageBox.warning(self, "Victory!", text, QMessageBox.Ok)


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
