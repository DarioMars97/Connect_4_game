# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import json
import dola
from time import sleep
from random import randint


HUMAN = 0
BOT = 1


class ConnectFourBoard:
    game_over = 0
    winner = 0

    def __init__(self):
        self.board = np.zeros((6, 7))

    def set_level(self, level):
        self.level = level

    def drop(self, col, player):
        for row in range(6):
            if self.board[row][col] == 0:
                self.board[row][col] = player+1

                return row

        return -1


    def winning_move(self, player):
        for row in range(6):#horizontal win
             for col in range(4):
                 if self.board[row][col] == self.board[row][col+1] == self.board[row][col+2] ==self.board[row][col+3] !=0:
                     self.game_over = 1
                     self.winner = player
                     return [[row,col],[row,col+1],[row,col+2],[row,col+3]]



        for col in range(7):#virtical win
            for row in range(3):
                if self.board[row][col] == self.board[row+1][col] == self.board[row+2][col] == self.board[row+3][col] !=0:
                    self.game_over = 1
                    self.winner = player
                    return [[row,col],[row+1,col],[row+2,col],[row+3,col]]



        for col in range(4):
            for row in range(6):
                if row < 3 :
                    if self.board[row][col] == self.board[row+1][col+1] == self.board[row+2][col+2] == self.board[row+3][col+3] != 0:
                        self.game_over = 1
                        self.winner = player
                        return [[row,col],[row+1,col+1],[row+2,col+2],[row+2,col+3]]

                else:
                    if self.board[row][col] == self.board[row-1][col+1] == self.board[row-2][col+2] == self.board[row-3][col+3] != 0:
                        self.game_over = 1
                        self.winner = player
                        return [[row,col],[row-1,col+1],[row-2,col+2],[row-3,col+3]]


        return []


class ConnectFourDola(QMainWindow, dola.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.player = randint(0, 1)

        if self.player == 1:
            self.turnLabel.setText("Computer Turn!")
        elif self.player == 0:
            self.turnLabel.setText("Your Turn!")

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().hide()

        self.startButton.clicked.connect(self.start)
        self.saveButton.clicked.connect(self.browse_and_save)
        self.loadButton.clicked.connect(self.load)

        self.pushButtons = [
            [self.pb00, self.pb01, self.pb02, self.pb03, self.pb04, self.pb05, self.pb06],
            [self.pb10, self.pb11, self.pb12, self.pb13, self.pb14, self.pb15, self.pb16],
            [self.pb20, self.pb21, self.pb22, self.pb23, self.pb24, self.pb25, self.pb26],
            [self.pb30, self.pb31, self.pb32, self.pb33, self.pb34, self.pb35, self.pb36],
            [self.pb40, self.pb41, self.pb42, self.pb43, self.pb44, self.pb45, self.pb46],
            [self.pb50, self.pb51, self.pb52, self.pb53, self.pb54, self.pb55, self.pb56],
        ]
        self.pb50.clicked.connect(lambda: self.drop(0))
        self.pb40.clicked.connect(lambda: self.drop(0))
        self.pb30.clicked.connect(lambda: self.drop(0))
        self.pb20.clicked.connect(lambda: self.drop(0))
        self.pb10.clicked.connect(lambda: self.drop(0))
        self.pb00.clicked.connect(lambda: self.drop(0))

        self.pb51.clicked.connect(lambda: self.drop(1))
        self.pb41.clicked.connect(lambda: self.drop(1))
        self.pb31.clicked.connect(lambda: self.drop(1))
        self.pb21.clicked.connect(lambda: self.drop(1))
        self.pb11.clicked.connect(lambda: self.drop(1))
        self.pb01.clicked.connect(lambda: self.drop(1))

        self.pb52.clicked.connect(lambda: self.drop(2))
        self.pb42.clicked.connect(lambda: self.drop(2))
        self.pb32.clicked.connect(lambda: self.drop(2))
        self.pb22.clicked.connect(lambda: self.drop(2))
        self.pb12.clicked.connect(lambda: self.drop(2))
        self.pb02.clicked.connect(lambda: self.drop(2))

        self.pb53.clicked.connect(lambda: self.drop(3))
        self.pb43.clicked.connect(lambda: self.drop(3))
        self.pb33.clicked.connect(lambda: self.drop(3))
        self.pb23.clicked.connect(lambda: self.drop(3))
        self.pb13.clicked.connect(lambda: self.drop(3))
        self.pb03.clicked.connect(lambda: self.drop(3))

        self.pb54.clicked.connect(lambda: self.drop(4))
        self.pb44.clicked.connect(lambda: self.drop(4))
        self.pb34.clicked.connect(lambda: self.drop(4))
        self.pb24.clicked.connect(lambda: self.drop(4))
        self.pb14.clicked.connect(lambda: self.drop(4))
        self.pb04.clicked.connect(lambda: self.drop(4))

        self.pb55.clicked.connect(lambda: self.drop(5))
        self.pb45.clicked.connect(lambda: self.drop(5))
        self.pb35.clicked.connect(lambda: self.drop(5))
        self.pb25.clicked.connect(lambda: self.drop(5))
        self.pb15.clicked.connect(lambda: self.drop(5))
        self.pb05.clicked.connect(lambda: self.drop(5))

        self.pb56.clicked.connect(lambda: self.drop(6))
        self.pb46.clicked.connect(lambda: self.drop(6))
        self.pb36.clicked.connect(lambda: self.drop(6))
        self.pb26.clicked.connect(lambda: self.drop(6))
        self.pb16.clicked.connect(lambda: self.drop(6))
        self.pb06.clicked.connect(lambda: self.drop(6))

    def start(self):
        self.tabWidget.setCurrentIndex(1)
        self.connect_four_board = ConnectFourBoard()
        if self.levelComboBox.currentText() == "Easy":
            self.connect_four_board.set_level(1)
        elif self.levelComboBox.currentText() == "Medium":
            self.connect_four_board.set_level(2)
        elif self.levelComboBox.currentText() == "Hard":
            self.connect_four_board.set_level(3)

    def load(self):
        name, _ = QFileDialog.getOpenFileName(self, 'Open File')
        my_file = open(name, 'r')
        # json_obj = codecs.open(name, 'r', encoding='utf-8').read()
        json_obj = my_file.read()
        board_board = json.loads(json_obj)
        my_file.close()

        self.tabWidget.setCurrentIndex(1)
        self.connect_four_board = ConnectFourBoard()
        self.connect_four_board.board = np.array(board_board["board"])
        self.player = board_board["player"]

        if self.levelComboBox.currentText() == "Easy":
            self.connect_four_board.set_level(1)
        elif self.levelComboBox.currentText() == "Medium":
            self.connect_four_board.set_level(2)
        elif self.levelComboBox.currentText() == "Hard":
            self.connect_four_board.set_level(3)
        for r in range(6):
            for c in range(7):
                if self.connect_four_board.board[r][c] == 1:
                    self.pushButtons[r][c].setStyleSheet("background-color: red;")
                elif self.connect_four_board.board[r][c] == 2:
                    self.pushButtons[r][c].setStyleSheet("background-color: yellow;")


    def browse_and_save(self):
        save_file, _ = QFileDialog.getSaveFileName(caption="Save File As", directory=".",
                                                filter=".txt")
        with open(save_file, 'w') as outfile:
            board_bourd = self.connect_four_board.board.tolist()
            player = self.player
            board = {"board": board_bourd, "player": player}
            json.dump(board, outfile)


    def flip_turn(self):
        if self.player == 1:
            self.turnLabel.setText("Computer Turn!")

        elif self.player == 0:
            self.turnLabel.setText("Your Turn!")


    def drop(self, col):
        if self.connect_four_board.game_over == 1:
            return
        row = self.connect_four_board.drop(col, self.player)

        if row == -1:
            return
        if self.player == HUMAN:
            self.pushButtons[row][col].setStyleSheet("background-color: red;")
            self.player = (self.player + 1) % 2
            win_pos_list = self.connect_four_board.winning_move(self.player)


            self.flip_turn()
            for i in win_pos_list:
                self.pushButtons[i[0]][i[1]].setStyleSheet(self.pushButtons[i[0]][i[1]].styleSheet() +"border: 10px solid #660066;" );
                self.winLabel.setText("You WoN !!!")
                self.turnLabel.setText("")


        elif self.player == BOT:
            self.pushButtons[row][col].setStyleSheet("background-color: yellow;")
            self.player = (self.player + 1) % 2
            win_pos_list = self.connect_four_board.winning_move(self.player)

            self.flip_turn()

            for i in win_pos_list:
                self.pushButtons[i[0]][i[1]].setStyleSheet(self.pushButtons[i[0]][i[1]].styleSheet() +"border: 10px solid #660066;" );
                self.winLabel.setText("Computer WoN !!!")
                self.turnLabel.setText("")



app = QApplication(sys.argv)
game = ConnectFourDola()
game.show()
app.exec_()
