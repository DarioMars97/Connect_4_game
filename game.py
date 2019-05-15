from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
import json
import GUI
from random import shuffle, choice
from math import inf
from time import sleep


HUMAN = 0
BOT = 1
BEST_COL = -1
CUSTOM_BOARD_FLAG = True
VERBOSE_MODE = {"max_depth": 0,
                "average_branching_factor": [],
                "leaf_nodes": [],
                "cutoffs": []}


class WriteThread(QThread):
    def __init__(self, gui):
        super(WriteThread, self).__init__()
        self.quit_flag = False
        self.gui = gui

    def run(self):
        while True:
            if not self.quit_flag:
                main_table = self.gui.mainTable
                nodes_table = self.gui.nodesTable
                cutoffs_table = self.gui.cutoffsTable
                branching_factor = VERBOSE_MODE["average_branching_factor"]
                avg = sum(branching_factor)//len(branching_factor)
                nodes_no = len(VERBOSE_MODE["leaf_nodes"])
                cutoffs_no = len(VERBOSE_MODE["cutoffs"])
                main_table.setItem(0, 1, QTableWidgetItem(str(avg)))
                main_table.setItem(-1, 1, QTableWidgetItem(str(VERBOSE_MODE["max_depth"])))
                main_table.setItem(1, 1, QTableWidgetItem(str(nodes_no)))
                main_table.setItem(2, 1, QTableWidgetItem(str(cutoffs_no)))

                nodes_table.setRowCount(0)
                nodes_table.setRowCount(nodes_no)
                for i in range(nodes_no):
                    node = VERBOSE_MODE["leaf_nodes"][i]
                    position = (node["node_level"], node["node_number"])
                    score = node["score"]
                    nodes_table.setItem(i, 0, QTableWidgetItem(str(position)))
                    nodes_table.setItem(i, 1, QTableWidgetItem(str(score)))

                cutoffs_table.setRowCount(0)
                cutoffs_table.setRowCount(cutoffs_no)
                for i in range(cutoffs_no):
                    cutoffs = VERBOSE_MODE["cutoffs"][i]
                    type = cutoffs["type"]
                    level = cutoffs["level"]
                    cutoffs_table.setItem(i, 0, QTableWidgetItem(type))
                    cutoffs_table.setItem(i, 1, QTableWidgetItem(str(level)))

                sleep(1)
                self.gui.tabWidget.setCurrentIndex(2)
                VERBOSE_MODE["max_depth"] = 0
                VERBOSE_MODE["average_branching_factor"].clear()
                VERBOSE_MODE["leaf_nodes"].clear()
                VERBOSE_MODE["cutoffs"].clear()
                self.quit_flag = True
            else:
                break

        self.quit()
        self.wait()


class TimeThread(QThread):
    def __init__(self, gui):
        super(TimeThread, self).__init__()
        self.quit_flag = False
        self.gui = gui
        self.bro_thread = self.gui.mythread

    def run(self):
        while True:
            if not self.quit_flag:
                value = self.gui.spinBox.value()
                sleep(value)
                self.quit_flag = True
                if BEST_COL != -1:
                    self.bro_thread.stop(from_thread= True)
            else:
                break

        self.quit()
        self.wait()


class MyThread(QThread):
    def __init__(self, gui, connectFour):
        super(MyThread, self).__init__()
        self.quit_flag = False
        self.connect_four = connectFour
        self.gui = gui
        self.gui.playNowButton.setEnabled(True)

    def run(self):
        global BEST_COL
        while True:
            if not self.quit_flag:
                self.connect_four.game_over = 1
                board_copy = self.connect_four.board.copy()
                _, col = self.connect_four.minimax(board_copy, self.connect_four.level, -inf, inf, maximizer=True)
                self.connect_four.best_col = col
                self.quit_flag = True
                # self.connect_four.drop(col, BOT)
                self.gui.pushButtons[0][col].click()
                self.gui.playNowButton.setEnabled(False)
                self.connect_four.game_over = 0
                self.gui.spinBox.setEnabled(True)
                # self.gui.spinBox.setValue(0)
                BEST_COL = -1
            else:
                break

        self.quit()
        self.wait()

    def stop(self, from_thread=False):
        # print(BEST_COL)
        global BEST_COL
        if BEST_COL != -1 and not self.isFinished():
            if self.isRunning():
                self.terminate()
                self.wait()
            self.quit_flag = True
            self.connect_four.game_over = 0
            self.gui.pushButtons[0][BEST_COL].click()
            self.gui.playNowButton.setEnabled(False)
            self.gui.spinBox.setEnabled(True)
            # self.gui.spinBox.setValue(0)
            BEST_COL = -1
        if self.gui.spinBox.value() > 0 and not from_thread:
            self.gui.time_thread.terminate()
            self.gui.time_thread.wait()



class ConnectFourBoard:
    game_over = 0
    winner = 0
    level = 0
    best_col = -1

    def __init__(self):
        self.board = np.zeros((6, 7))

    def clear(self):
        self.board.fill(0)
        self.game_over = 0
        self.winner = 0
        self.best_col = -1

    def set_level(self, level):
        self.level = level

    def drop(self, col, player):
        for row in range(6):
            if self.board[row][col] == 0:
                self.board[row][col] = player+1

                return row

        return -1

    def drop_simulate(self, board_copy, col, player):
        for row in range(6):
            if board_copy[row][col] == 0:
                board_copy[row][col] = player+1

                return row

        return -1


    def board_score(self,window, piece):
    	score = 0
    	opp_piece = HUMAN
    	if piece == HUMAN:
    		opp_piece = BOT

    	if window.count(piece) == 4:
    		score += 100
    	elif window.count(piece) == 3 and window.count(0) == 1:
    		score += 5
    	elif window.count(piece) == 2 and window.count(0) == 2:
    		score += 2

    	if window.count(opp_piece) == 3 and window.count(0) == 1:
    		score -= 4

    	return score

    def win_percent(self,board,piece):
        score = 0

    	## Score center column
        center_array = [int(i) for i in list(board[:,7//2])]
        center_count = center_array.count(piece)
        score += center_count * 3
    	## Score Horizontal
        for r in range(6):
            row_array = [int(i) for i in list(board[r,:])]
            for c in range(7-3):
                window = row_array[c:c+4]
                score += self.board_score(window, piece)

        ## Score Vertical
        for c in range(7):
            col_array = [int(i) for i in list(board[:,c])]
            for r in range(6-3):
                window = col_array[r:r+4]
                score += self.board_score(window, piece)

        ## Score posiive sloped diagonal
        for r in range(6-3):
            for c in range(7-3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.board_score(window, piece)

        for r in range(6-3):
            for c in range(7-3):
                window = [board[r+3-i][c+i] for i in range(4)]
                score += self.board_score(window, piece)

        return score


    def get_valid_locations(self, board_copy):
        valid_locations = []
        for col in range(7):
            for row in range(6):
                if board_copy[row][col] == 0:
                    valid_locations.append(col)
                    break
        return valid_locations

    def terminal_node(self, board_copy):
        return self.winning_move(board_copy)[1] or len(self.get_valid_locations(board_copy)) == 0

    def minimax(self, board_copy, depth, alpha, beta, maximizer=False, minimizer=False):
        terminal_node = self.terminal_node(board_copy)
        global BEST_COL
        global VERBOSE_MODE
        VERBOSE_MODE["max_depth"] = max(VERBOSE_MODE["max_depth"], depth)
        if depth == 0 or terminal_node:
            if terminal_node:
                win_places, is_winning = self.winning_move(board_copy)
                if is_winning:
                    [row, col] = win_places[0]
                    player = board_copy[row][col] - 1
                    if player == HUMAN:
                        return -99999, None
                    elif player == BOT:
                        return 99999, None
                else:
                    return 0, None
            else:
                return self.win_percent(board_copy,BOT+1), None
        if maximizer:
            value = -inf
            valid_locations = self.get_valid_locations(board_copy)
            VERBOSE_MODE["average_branching_factor"].append(len(valid_locations))
            shuffle(valid_locations)
            best_col = choice(valid_locations)
            for col in valid_locations:
                copy_board = board_copy.copy()
                self.drop_simulate(copy_board, col, BOT)
                score = self.minimax(copy_board, depth-1, alpha, beta, minimizer=True)[0]
                node = {"node_level": depth,
                        "node_number": valid_locations.index(col),
                        "score": score}
                VERBOSE_MODE["leaf_nodes"].append(node)
                if score > value:
                    best_col = col
                    BEST_COL = best_col
                value = max(value, score)
                alpha = max(alpha, value)
                # print(value)
                if alpha >= beta:
                    cutoff = {"type": "beta",
                              "level": depth}
                    VERBOSE_MODE["cutoffs"].append(cutoff)
                    break
            # print(value)
            return value, best_col
        elif minimizer:
            value = inf
            valid_locations = self.get_valid_locations(board_copy)
            shuffle(valid_locations)
            best_col = choice(valid_locations)
            for col in valid_locations:
                copy_board = board_copy.copy()
                self.drop_simulate(copy_board, col, HUMAN)
                score = self.minimax(copy_board, depth-1, alpha, beta, maximizer=True)[0]
                node = {"node_level": depth,
                        "node_number": valid_locations.index(col),
                        "score": score}
                VERBOSE_MODE["leaf_nodes"].append(node)
                if score < value:
                    best_col = col
                    BEST_COL = best_col
                value = min(value, score)
                beta = min(value, beta)
                # print(value)
                if alpha >= beta:
                    cutoff = {"type": "alpha",
                              "level": depth}
                    VERBOSE_MODE["cutoffs"].append(cutoff)
                    break
            # print(value)
            return value, best_col

    def winning_move(self, board):
        for row in range(6): # horizontal win
             for col in range(4):
                 if board[row][col] == board[row][col+1] == board[row][col+2] ==board[row][col+3] !=0:
                     return [[row, col], [row, col+1], [row, col+2], [row, col+3]], True

        for col in range(7): # virtical win
            for row in range(3):
                if board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col] !=0:
                    return [[row, col], [row+1, col], [row+2, col], [row+3, col]], True

        for col in range(4):
            for row in range(6):
                if row < 3 :
                    if board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3] != 0:
                        return [[row, col], [row+1, col+1], [row+2, col+2], [row+3, col+3]], True

                else:
                    if board[row][col] == board[row-1][col+1] == board[row-2][col+2] == board[row-3][col+3] != 0:
                        return [[row, col], [row-1, col+1], [row-2, col+2], [row-3, col+3]], True

        return [], False


class ConnectFourGUI(QMainWindow, GUI.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.firstturnstart.setChecked(True)
        self.checkBox_2.setChecked(True)
        self.player = HUMAN
        self.mythread = None
        self.time_thread = None
        self.turnLabel.setText("Your Turn!")
        self.playNowButton.setEnabled(False)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().hide()

        self.startButton.clicked.connect(self.start)
        self.saveButton.clicked.connect(self.browse_and_save)
        self.loadButton.clicked.connect(self.load)
        self.radioButton.setChecked(True)
        self.playNowButton.clicked.connect(self.terminate)
        self.custom.clicked.connect(self.custom_board)
        self.playAgainButton.clicked.connect(self.play_again)
        self.okb.clicked.connect(self.creat_custom)
        self.returnButton.clicked.connect(self.return_from_verbose_mode)
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

    def terminate(self):
        self.mythread.stop()

    def start(self):
        self.tabWidget.setCurrentIndex(1)
        self.connect_four_board = ConnectFourBoard()
        if self.levelComboBox.currentText() == "Easy":
            self.connect_four_board.set_level(3)
            self.curlevel.setText("Easy")
        elif self.levelComboBox.currentText() == "Medium":
            self.connect_four_board.set_level(5)
            self.curlevel.setText("Medium")
        elif self.levelComboBox.currentText() == "Hard":
            self.connect_four_board.set_level(7)
            self.curlevel.setText("Hard")
        self.okb.hide()
        if self.secondeturnstart.isChecked():
            self.player = BOT
            self.turnLabel.setText("Computer Turn!")
            self.spinBox.setEnabled(False)
            self.mythread = MyThread(self, self.connect_four_board)
            self.mythread.start()

    def play_again(self):
        self.winLabel.setText("")
        if self.mythread is not None:
            self.mythread.terminate()
        if self.time_thread is not None:
            self.time_thread.terminate()
        if self.radioButton.isChecked():
            self.connect_four_board.level = 3
            self.curlevel.setText("Easy")
        elif self.radioButton_2.isChecked():
            self.connect_four_board.level = 5
            self.curlevel.setText("Medium")
        else:
            self.connect_four_board.level = 7
            self.curlevel.setText("Hard")
        # print(self.connect_four_board.level)
        self.connect_four_board.clear()
        if not self.checkBox_2.isChecked():
            self.player = BOT
            self.turnLabel.setText("Computer Turn!")
            self.spinBox.setEnabled(False)
            self.mythread = MyThread(self, self.connect_four_board)
            self.mythread.start()

        else:
            self.player = HUMAN
            self.turnLabel.setText("Your Turn!")
            self.winLabel.setText("")

        for r in range(6):
            for c in range(7):
                self.pushButtons[r][c].setStyleSheet("background-color: gray;")

    def load(self):
        if self.mythread is not None:
            self.mythread.terminate()
        if self.time_thread is not None:
            self.time_thread.terminate()
        name, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if name is '':
            return
        my_file = open(name, 'r')
        # json_obj = codecs.open(name, 'r', encoding='utf-8').read()
        json_obj = my_file.read()
        board_board = json.loads(json_obj)
        my_file.close()
        self.connect_four_board = ConnectFourBoard()
        self.connect_four_board.board = np.array(board_board["board"])
        self.player = board_board["player"]
        self.connect_four_board.set_level(board_board["level"])
        if board_board["level"] == 3:
            self.curlevel.setText("Easy")
        elif board_board["level"] == 5:
            self.curlevel.setText("Medium")
        else:
            self.curlevel.setText("Hard")
        for r in range(6):
            for c in range(7):
                if self.connect_four_board.board[r][c] == 1:
                    self.pushButtons[r][c].setStyleSheet("background-color: red;")
                elif self.connect_four_board.board[r][c] == 2:
                    self.pushButtons[r][c].setStyleSheet("background-color: yellow;")
                else:
                    self.pushButtons[r][c].setStyleSheet("background-color: gray;")

        if self.player == HUMAN:
            self.turnLabel.setText("Your Turn!")

        elif self.player == BOT:
            self.turnLabel.setText("Computer Turn!")

        if self.player == BOT:
            self.spinBox.setEnabled(False)
            self.mythread = MyThread(self, self.connect_four_board)
            self.mythread.start()

    def browse_and_save(self):
        save_file, _ = QFileDialog.getSaveFileName(caption="Save File As", directory=".",
                                                filter=".txt")
        if save_file is '':
            return
        with open(save_file, 'w') as outfile:
            board_bourd = self.connect_four_board.board.tolist()
            player = self.player
            board = {"board": board_bourd, "player": player, "level": self.connect_four_board.level}
            json.dump(board, outfile)

    def flip_turn(self):
        # self.player is the previous player
        if self.player == HUMAN:
            self.turnLabel.setText("Computer Turn!")

        elif self.player == BOT:
            self.turnLabel.setText("Your Turn!")

    def custom_board(self,):
        if self.mythread is not None:
            self.mythread.terminate()
        if self.time_thread is not None:
            self.time_thread.terminate()
        global CUSTOM_BOARD_FLAG
        self.connect_four_board.clear()
        self.player = HUMAN
        self.turnLabel.setText("Your Turn!")

        self.winLabel.setText("")

        for r in range(6):
            for c in range(7):
                self.pushButtons[r][c].setStyleSheet("background-color: gray;")
        self.playAgainButton.hide()
        self.custom.hide()
        self.loadButton.hide()
        self.playNowButton.hide()
        self.saveButton.hide()
        self.label.hide()
        self.spinBox.hide()
        self.okb.show()
        self.curlevel.hide()
        self.label_3.hide()
        CUSTOM_BOARD_FLAG = False

    def return_from_verbose_mode(self):
        self.tabWidget.setCurrentIndex(1)

    def creat_custom(self):
        global CUSTOM_BOARD_FLAG
        CUSTOM_BOARD_FLAG = True
        self.playAgainButton.show()
        self.custom.show()
        self.loadButton.show()
        self.playNowButton.show()
        self.saveButton.show()
        self.label.show()
        self.spinBox.show()
        self.okb.hide()
        self.curlevel.show()
        self.label_3.show()
        if self.radioButton.isChecked():
            self.connect_four_board.level = 3
            self.curlevel.setText("Easy")
        elif self.radioButton_2.isChecked():
            self.connect_four_board.level = 5
            self.curlevel.setText("Medium")
        else:
            self.connect_four_board.level = 7
            self.curlevel.setText("Hard")
        if self.player == BOT:
            self.spinBox.setEnabled(False)
            self.mythread = MyThread(self, self.connect_four_board)
            self.mythread.start()

    def drop(self, col):
        # self.playNowButton.hide()
        global CUSTOM_BOARD_FLAG
        if CUSTOM_BOARD_FLAG:
            if self.connect_four_board.game_over == 1:
                return
            row = self.connect_four_board.drop(col, self.player)

            if row == -1:
                return
            if self.player == HUMAN:
                self.pushButtons[row][col].setStyleSheet("background-color: red;")
                win_pos_list = self.connect_four_board.winning_move(self.connect_four_board.board)[0]
                # print(self.connect_four_board.win_percent(self.connect_four_board.board))

                if len(win_pos_list) is not 0:
                    self.turnLabel.setText("")
                    self.winLabel.setText("You WoN !!!")
                    self.connect_four_board.game_over=1
                    for i in win_pos_list:
                        self.pushButtons[i[0]][i[1]].setStyleSheet(self.pushButtons[i[0]][i[1]].styleSheet() +"border: 10px solid black;" )
                    return

                self.flip_turn()
                self.player = (self.player + 1) % 2
                self.spinBox.setEnabled(False)
                self.mythread = MyThread(self, self.connect_four_board)
                self.mythread.start()
                if self.spinBox.value() > 0:
                    self.time_thread = TimeThread(self)
                    self.time_thread.start()

            elif self.player == BOT:
                self.pushButtons[row][col].setStyleSheet("background-color: yellow;")
                win_pos_list = self.connect_four_board.winning_move(self.connect_four_board.board)[0]
                # print(self.connect_four_board.win_percent(self.connect_four_board.board))

                if len(win_pos_list) is not 0:
                    self.winLabel.setText("Computer WoN !!!")
                    self.turnLabel.setText("")
                    self.connect_four_board.game_over = 1
                    for i in win_pos_list:
                        self.pushButtons[i[0]][i[1]].setStyleSheet(self.pushButtons[i[0]][i[1]].styleSheet() +"border: 10px solid black;" )
                    return

                self.flip_turn()
                self.player = (self.player + 1) % 2
                if self.checkBox.isChecked():
                    self.write = WriteThread(self)
                    self.write.start()

        else:
            if self.connect_four_board.game_over == 1:
                return
            row = self.connect_four_board.drop(col, self.player)

            if row == -1:
                return
            if self.player == HUMAN:
                self.pushButtons[row][col].setStyleSheet("background-color: red;")
                win_pos_list = self.connect_four_board.winning_move(self.connect_four_board.board)[0]
                # print(self.connect_four_board.win_percent(self.connect_four_board.board))

                if len(win_pos_list) is not 0:
                    self.turnLabel.setText("")
                    self.winLabel.setText("You WoN !!!")
                    self.connect_four_board.game_over=1
                    for i in win_pos_list:
                        self.pushButtons[i[0]][i[1]].setStyleSheet(self.pushButtons[i[0]][i[1]].styleSheet() +"border: 10px solid black;" )
                    return

                self.flip_turn()
                self.player = (self.player + 1) % 2

            elif self.player == BOT:
                self.pushButtons[row][col].setStyleSheet("background-color: yellow;")
                win_pos_list = self.connect_four_board.winning_move(self.connect_four_board.board)[0]
                # print(self.connect_four_board.win_percent(self.connect_four_board.board))

                if len(win_pos_list) is not 0:
                    self.winLabel.setText("Computer WoN !!!")
                    self.turnLabel.setText("")
                    self.connect_four_board.game_over = 1
                    for i in win_pos_list:
                        self.pushButtons[i[0]][i[1]].setStyleSheet(self.pushButtons[i[0]][i[1]].styleSheet() +"border: 10px solid black;" )
                    return

                self.flip_turn()
                self.player = (self.player + 1) % 2


app = QApplication(sys.argv)
game = ConnectFourGUI()
game.show()
app.exec_()
