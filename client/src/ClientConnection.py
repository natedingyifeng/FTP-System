import sys
import os
import socket
import MainInterface
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QTreeWidgetItem, QInputDialog, QFileDialog, \
    QHeaderView, QTableWidgetItem, QProgressBar, QLabel, QMessageBox
from PyQt5.QtCore import Qt, QEventLoop, QCoreApplication, QThread, pyqtSignal
from PyQt5.Qt import QTextCursor, QStandardItemModel
import threading
import re
import time
import random


def GetStatusCode(msg):
    lines = msg.split(' ')
    return lines[0]


def GetWorkingDirectory(msg):
    lines = msg.split('"')
    return lines[1]


def PasvConnectionParse(msg):
    result = [0, 0, 0, 0, 0, 0]
    lines = re.findall(r'[(](.*?)[)]', msg)
    if len(lines) == 1:
        ip_port = lines[0].split(',')
        if len(ip_port) == 6:
            for i in range(6):
                if ip_port[i].isdigit() is True:
                    result[i] = int(ip_port[i])
                else:
                    return -1, -1
            ip = str(result[0]) + "." + str(result[1]) + "." + str(result[2]) + "." + str(result[3])
            port = result[4] * 256 + result[5]
            return ip, port
        else:
            return -1, -1
    else:
        return -1, -1


def HandleListReturn(msg):
    lines = msg.split('\r\n')
    return lines[0], lines[1]


def CheckFilenameValidation(name):
    if len(name) == 0:
        return False
    else:
        for item in name:
            if item == '\n' or item == '\r' or item == ' ':
                return False
    return True


def CheckDirectoryValidation(dir):
    if len(dir) == 0:
        return False
    else:
        for item in dir:
            if item == '_' or item.isalnum():
                return False
    return True


class Connection:
    def __init__(self, ui, MainWindow):
        # necessary variables
        self.commands = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_transfer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_mode = "None"
        self.transfer_IP = ""
        self.transfer_port = -1
        self.current_host = socket.gethostbyname(socket.gethostname())
        self.current_Dir = "/"
        self.is_connected = False
        self.is_login = False
        self.ui = ui
        self.MainWindow = MainWindow
        self.server_IP = ""
        self.server_port = -1
        self.username = ""
        self.password = ""
        self.file_root = []
        self.LIST_info = ""
        self.current_filename = ""
        self.current_filename_size = -1
        self.file_dic = {}
        self.local_upload_filepath = ""
        self.local_upload_filename = ""
        self.local_download_filepath = ""
        self.file_transfer_list = []
        # widget settings
        self.MainWindow.setWindowTitle("FTP Client")
        self.ui.password.setEchoMode(QLineEdit.Password)
        self.ui.IP_address.setAlignment(Qt.AlignLeft)
        self.ui.command_info.setReadOnly(True)
        self.ui.command_info.verticalScrollBar().setSliderPosition(self.ui.command_info.verticalScrollBar().maximum())
        self.ui.connection_mode.addItems(['PORT', 'PASV'])
        self.ui.connection_mode.setCurrentIndex(-1)
        self.ui.file_list.setHeaderLabels(['Name', 'Type', 'Size', 'Date Modified'])
        self.ui.file_list.setColumnWidth(0, 209)
        self.ui.file_list.setColumnWidth(1, 90)
        self.ui.file_list.setColumnWidth(2, 89)
        self.ui.file_list.setColumnWidth(3, 150)
        self.ui.filetransfer.setColumnCount(4)
        self.ui.filetransfer.setHorizontalHeaderLabels(['文件名', '方向', '远程路径', '进度'])
        self.ui.filetransfer.horizontalHeader().setStretchLastSection(True)
        self.ui.filetransfer.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.login.setEnabled(True)
        self.ui.logout.setEnabled(False)
        self.ui.edit_currentDir.setEnabled(False)
        self.ui.edit_currentDir_up.setEnabled(False)
        self.ui.LIST.setEnabled(False)
        self.ui.upload.setEnabled(False)
        self.ui.delete_file.setEnabled(False)
        self.ui.download.setEnabled(False)
        self.ui.rename.setEnabled(False)
        self.ui.NewFile.setEnabled(False)
        self.ui.edit_currentDir_enter.setEnabled(False)
        self.ui.connection_mode.setEnabled(False)
        # self.ui.IP_address.setText("10.211.55.3")
        self.ui.IP_address.setText("139.196.81.14")
        # self.ui.username.setText("anonymous")
        self.ui.username.setText("ssast")
        self.ui.password.setText("ssast")
        self.ui.port.setText("21")
        # signal and slot
        self.ui.login.clicked.connect(self.LoggingIn)
        self.ui.logout.clicked.connect(self.LoggingOut)
        self.ui.connection_mode.currentIndexChanged.connect(self.BuildTransferConnection)
        self.ui.edit_currentDir.clicked.connect(self.ChangeCurrentWorkingDirectory)
        self.ui.NewFile.clicked.connect(self.CreateNewDirectory)
        self.ui.file_list.itemClicked.connect(self.RecordCurrentFileNameClicked)
        self.ui.file_list.itemDoubleClicked.connect(self.RecordCurrentFileNameDoubleClicked)
        self.ui.delete_file.clicked.connect(self.RemoveDirectory)
        self.ui.rename.clicked.connect(self.RenameDirectory)
        self.ui.LIST.clicked.connect(self.ShowLIST)
        self.ui.edit_currentDir_enter.clicked.connect(self.EnterSelectedDirectory)
        self.ui.edit_currentDir_up.clicked.connect(self.EnterBackSpace)
        self.ui.download.clicked.connect(self.GetLocal)
        self.ui.upload.clicked.connect(self.OpenLocal)

    def CommandInfoUpdate(self, msg, source):
        msg = msg.replace('\n', '').replace('\r', '')
        if source == 0:
            msg = "CLIENT: " + msg
        elif source == 1:
            msg = "SERVER: " + msg
        elif source == 2:
            msg = msg
        self.ui.command_info.appendPlainText(msg)

    def ConnectionRestart(self, connection):
        if connection == "commands":
            self.commands.close()
            self.commands = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif connection == "file_transfer":
            self.file_transfer.close()
            self.file_transfer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def LoggingIn(self):
        if self.is_login is False:
            IP_tem = self.ui.IP_address.text()
            username_tem = self.ui.username.text()
            password_tem = self.ui.password.text()
            port_tem = int(self.ui.port.text())
            self.is_connected = True
            if self.commands.connect_ex((IP_tem, port_tem)) != 0:
                connection_fail = self.commands.recv(8192).decode()
                self.CommandInfoUpdate(connection_fail, 1)
                QApplication.processEvents()
                self.is_connected = False
            if self.is_connected is True:
                connection_succeed = self.commands.recv(8192).decode()
                self.CommandInfoUpdate(connection_succeed, 1)
                QApplication.processEvents()
                USER_command = "USER " + username_tem + "\r\n"
                self.commands.send(USER_command.encode())
                self.CommandInfoUpdate(USER_command, 0)
                QApplication.processEvents()
                USER_return = self.commands.recv(8192).decode()
                self.CommandInfoUpdate(USER_return, 1)
                if GetStatusCode(USER_return) == "331":
                    PASS_command = "PASS " + password_tem + "\r\n"
                    self.commands.send(PASS_command.encode())
                    self.CommandInfoUpdate(PASS_command, 0)
                    QApplication.processEvents()
                    PASS_return = self.commands.recv(8192).decode()
                    self.CommandInfoUpdate(PASS_return, 1)
                    QApplication.processEvents()
                    if GetStatusCode(PASS_return) == "230":
                        self.is_login = True
                        self.server_IP = IP_tem
                        self.server_port = port_tem
                        self.username = username_tem
                        self.password = password_tem
                    else:
                        self.is_login = False
                        self.is_connected = False
                        self.ConnectionRestart("commands")
                else:
                    self.is_login = False
                    self.is_connected = False
                    self.ConnectionRestart("commands")
            SYST_command = "SYST\r\n"
            self.commands.send(SYST_command.encode())
            self.CommandInfoUpdate(SYST_command, 0)
            QApplication.processEvents()
            SYST_return = self.commands.recv(8192).decode()
            self.CommandInfoUpdate(SYST_return, 1)
            TYPE_command = "TYPE I\r\n"
            self.commands.send(TYPE_command.encode())
            self.CommandInfoUpdate(TYPE_command, 0)
            QApplication.processEvents()
            TYPE_return = self.commands.recv(8192).decode()
            self.CommandInfoUpdate(TYPE_return, 1)
            self.ui.login.setEnabled(False)
            self.ui.logout.setEnabled(True)
            self.ui.edit_currentDir.setEnabled(False)
            self.ui.edit_currentDir_up.setEnabled(False)
            self.ui.connection_mode.setEnabled(True)
            self.ui.LIST.setEnabled(True)
            self.ui.upload.setEnabled(False)
            self.ui.delete_file.setEnabled(False)
            self.ui.download.setEnabled(False)
            self.ui.rename.setEnabled(False)
            self.ui.NewFile.setEnabled(False)
            self.ui.edit_currentDir_enter.setEnabled(False)

    def LoggingOut(self):
        if self.is_login is True:
            QUIT_command = "QUIT\r\n"
            self.commands.send(QUIT_command.encode())
            self.CommandInfoUpdate(QUIT_command, 0)
            QApplication.processEvents()
            QUIT_return = self.commands.recv(8192).decode()
            self.CommandInfoUpdate(QUIT_return, 1)
            QApplication.processEvents()
            if GetStatusCode(QUIT_return) == "221":
                self.is_login = False
                self.is_connected = False
                self.ConnectionRestart("commands")
                self.ConnectionRestart("file_transfer")
                self.connection_mode = "None"
                self.transfer_IP = ""
                self.transfer_port = -1
                self.ui.connection_mode.setCurrentIndex(-1)
                self.cleanTransferComponentsContent()
                self.ui.file_list.clear()
                self.ui.filetransfer.clear()
                self.ui.current_Directory.setText("")
                self.ui.login.setEnabled(True)
                self.ui.logout.setEnabled(False)
                self.ui.edit_currentDir.setEnabled(False)
                self.ui.edit_currentDir_up.setEnabled(False)
                self.ui.connection_mode.setEnabled(False)
                self.ui.LIST.setEnabled(False)
                self.ui.upload.setEnabled(False)
                self.ui.delete_file.setEnabled(False)
                self.ui.download.setEnabled(False)
                self.ui.rename.setEnabled(False)
                self.ui.NewFile.setEnabled(False)
                self.ui.edit_currentDir_enter.setEnabled(False)

    def BuildTransferConnection(self):
        if self.is_login is True:
            if self.ui.connection_mode.currentText() == 'PORT':
                self.connection_mode = "PORT"
            elif self.ui.connection_mode.currentText() == 'PASV':
                self.connection_mode = "PASV"

    def setTransferComponentsContent(self):
        self.ui.IP_address_PORT.setText(self.transfer_IP)
        self.ui.port_PORT.setText(str(self.transfer_port))
        QApplication.processEvents()

    def cleanTransferComponentsContent(self):
        self.ui.IP_address_PORT.setText("")
        self.ui.port_PORT.setText("")

    def BuildPortConnection(self):
        self.ConnectionRestart("file_transfer")
        lines = self.commands.getsockname()
        ip_port = [0, 0, 0, 0, 0, 0]
        IP_tem = lines[0]
        port_tem = random.sample(range(20000, 65535), 1)[0]
        IP_lines = IP_tem.split('.')
        if len(IP_lines) == 4:
            for i in range(4):
                if IP_lines[i].isdigit() is True:
                    ip_port[i] = int(IP_lines[i])
        ip_port[4] = port_tem // 256
        ip_port[5] = port_tem % 256
        PORT_command = "PORT " + str(ip_port[0]) + "," + str(ip_port[1]) + "," + str(ip_port[2]) + "," \
                       + str(ip_port[3]) + "," + str(ip_port[4]) + "," + str(ip_port[5]) + "\r\n"
        self.commands.send(PORT_command.encode())
        self.CommandInfoUpdate(PORT_command, 0)
        QApplication.processEvents()
        PORT_return = self.commands.recv(8192).decode()
        self.CommandInfoUpdate(PORT_return, 1)
        QApplication.processEvents()
        if GetStatusCode(PORT_return) == "200":
            self.connection_mode = "PORT"
            self.transfer_IP = IP_tem
            self.transfer_port = port_tem
            try:
                self.file_transfer.bind((self.transfer_IP, self.transfer_port))
                self.file_transfer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.file_transfer.listen(64)
                self.setTransferComponentsContent()
                self.GetCurrentWorkingDirectory()
            except:
                PORT_fail = "PORT fail"
                self.cleanTransferComponentsContent()
                self.CommandInfoUpdate(PORT_fail, 2)
                QApplication.processEvents()
                self.connection_mode = "None"
                self.transfer_IP = ""
                self.ui.connection_mode.setCurrentIndex(-1)
        else:
            self.connection_mode = "None"
            self.transfer_IP = ""
            self.transfer_port = -1
            self.ui.connection_mode.setCurrentIndex(-1)

    def BuildPasvConnection(self):
        self.ConnectionRestart("file_transfer")
        PASV_command = "PASV\r\n"
        self.commands.send(PASV_command.encode())
        self.CommandInfoUpdate(PASV_command, 0)
        QApplication.processEvents()
        PASV_return = self.commands.recv(8192).decode()
        self.CommandInfoUpdate(PASV_return, 1)
        QApplication.processEvents()
        if GetStatusCode(PASV_return) == "227":
            ip, port = PasvConnectionParse(PASV_return)
            if ip != -1 or port != -1:
                self.connection_mode = "PASV"
                self.transfer_IP = ip
                self.transfer_port = port
                self.file_transfer.connect((self.transfer_IP, self.transfer_port))
                self.setTransferComponentsContent()
                self.GetCurrentWorkingDirectory()
            else:
                self.connection_mode = "None"
                self.transfer_IP = ""
                self.transfer_port = -1
                self.ui.connection_mode.setCurrentIndex(-1)
        else:
            self.connection_mode = "None"
            self.transfer_IP = ""
            self.transfer_port = -1
            self.ui.connection_mode.setCurrentIndex(-1)

    def ShowLIST(self):
        if self.connection_mode == "PORT":
            self.BuildPortConnection()
            self.ShowWorkingDirectoryList()
        elif self.connection_mode == "PASV":
            self.BuildPasvConnection()
            self.ShowWorkingDirectoryList()
        self.ui.edit_currentDir.setEnabled(True)
        self.ui.edit_currentDir_up.setEnabled(True)
        self.ui.LIST.setEnabled(True)
        self.ui.upload.setEnabled(True)
        self.ui.NewFile.setEnabled(True)
        self.ui.delete_file.setEnabled(False)
        self.ui.download.setEnabled(False)
        self.ui.rename.setEnabled(False)
        self.ui.edit_currentDir_enter.setEnabled(False)

    def ShowWorkingDirectoryList(self):
        if self.connection_mode == "PORT":
            LIST_command = "LIST\r\n"
            self.commands.send(LIST_command.encode())
            self.CommandInfoUpdate(LIST_command, 0)
            LIST_succeed = self.commands.recv(8192).decode()
            self.CommandInfoUpdate(LIST_succeed, 1)
            if GetStatusCode(LIST_succeed) == "150":
                try:
                    conn, addr = self.file_transfer.accept()
                    LIST_info = conn.recv(8192, socket.MSG_WAITALL).decode()
                    self.ShowFileList(LIST_info)
                    LIST_finish = self.commands.recv(8192).decode()
                    self.CommandInfoUpdate(LIST_finish, 1)
                    conn.close()
                except:
                    PORT_fail = "PORT fail"
                    self.cleanTransferComponentsContent()
                    self.CommandInfoUpdate(PORT_fail, 2)
                    QApplication.processEvents()
                    self.connection_mode = "None"
                    self.transfer_IP = ""
                    self.transfer_port = -1
                    self.ui.connection_mode.setCurrentIndex(-1)
        elif self.connection_mode == "PASV":
            LIST_command = "LIST\r\n"
            self.file_transfer.connect_ex((self.transfer_IP, self.transfer_port))
            self.commands.send(LIST_command.encode())
            self.CommandInfoUpdate(LIST_command, 0)
            LIST_succeed = self.commands.recv(8192).decode()
            self.CommandInfoUpdate(LIST_succeed, 1)
            if GetStatusCode(LIST_succeed) == "150":
                LIST_info = self.file_transfer.recv(8192, socket.MSG_WAITALL).decode()
                self.ShowFileList(LIST_info)
                LIST_finish = self.commands.recv(8192).decode()
                self.CommandInfoUpdate(LIST_finish, 1)
            self.ConnectionRestart("file_transfer")

    def ShowFileList(self, LIST_info):
        lines = LIST_info.split('\n')
        result = [[] for _ in range(len(lines))]
        dictionary_content = []
        self.file_dic.clear()
        for i in range(len(lines)):
            item = []
            result[i] = lines[i].split()
            if len(result[i]) == 9:
                item.append(result[i][8])
                if result[i][0][0] == 'd':
                    item.append("Directory")
                elif result[i][0][0] == '-':
                    item.append("File")
                else:
                    item.append("Other")
                create_time = str(result[i][5]) + " " + str(result[i][6]) + " " + str(result[i][7])
                file_size = result[i][4]
                item.append(file_size)
                item.append(create_time)
                dictionary_content.append(item)
                self.file_dic[result[i][8]] = file_size
        root = []
        self.ui.file_list.clear()
        for i in range(len(dictionary_content)):
            root.append(QTreeWidgetItem(self.ui.file_list))
            root[i].setText(0, dictionary_content[i][0])
            root[i].setText(1, dictionary_content[i][1])
            root[i].setText(2, dictionary_content[i][2])
            root[i].setText(3, dictionary_content[i][3])

    def GetCurrentWorkingDirectory(self):
        if self.is_login is True:
            PWD_command = "PWD\r\n"
            self.commands.send(PWD_command.encode())
            self.CommandInfoUpdate(PWD_command, 0)
            QApplication.processEvents()
            PWD_return = self.commands.recv(8192).decode("utf-8", "ignore")
            self.CommandInfoUpdate(PWD_return, 1)
            QApplication.processEvents()
            if GetStatusCode(PWD_return) == "257":
                self.current_Dir = GetWorkingDirectory(PWD_return)
                self.ui.current_Directory.setText(self.current_Dir)

    def ChangeCurrentWorkingDirectory(self):
        if self.is_login is True:
            current_Dir_tem, ok = QInputDialog.getText(self.MainWindow, "Change Working Directory", "Please input the new "
                                                                                                    "working directory:",
                                                       QLineEdit.Normal, "")
            if ok is True:
                CWD_command = "CWD " + current_Dir_tem + "\r\n"
                self.commands.send(CWD_command.encode())
                self.CommandInfoUpdate(CWD_command, 0)
                QApplication.processEvents()
                CWD_return = self.commands.recv(8192).decode()
                self.CommandInfoUpdate(CWD_return, 1)
                QApplication.processEvents()
                if GetStatusCode(CWD_return) == "250":
                    self.current_Dir = current_Dir_tem
                    self.ui.current_Directory.setText(self.current_Dir)
                    self.ShowLIST()
        else:
            QMessageBox.warning(self.MainWindow, 'Warning', "Please log in first!", QMessageBox.Yes)

    def EnterSelectedDirectory(self):
        CWD_command = "CWD " + self.current_filename + "\r\n"
        self.commands.send(CWD_command.encode())
        self.CommandInfoUpdate(CWD_command, 0)
        QApplication.processEvents()
        CWD_return = self.commands.recv(8192).decode()
        self.CommandInfoUpdate(CWD_return, 1)
        QApplication.processEvents()
        if GetStatusCode(CWD_return) == "250":
            self.current_Dir = self.current_filename
            self.ui.current_Directory.setText(self.current_Dir)
            self.ShowLIST()

    def EnterBackSpace(self):
        CWD_command = "CWD ..\r\n"
        self.commands.send(CWD_command.encode())
        self.CommandInfoUpdate(CWD_command, 0)
        QApplication.processEvents()
        CWD_return = self.commands.recv(8192).decode()
        self.CommandInfoUpdate(CWD_return, 1)
        QApplication.processEvents()
        if GetStatusCode(CWD_return) == "250":
            self.current_Dir = self.current_filename
            self.ui.current_Directory.setText(self.current_Dir)
            self.ShowLIST()

    def RecordCurrentFileNameClicked(self, item, column):
        self.current_filename = item.text(0)
        self.current_filename_size = int(item.text(2))
        self.ui.delete_file.setEnabled(True)
        self.ui.download.setEnabled(True)
        self.ui.rename.setEnabled(True)
        self.ui.edit_currentDir_enter.setEnabled(True)

    def RecordCurrentFileNameDoubleClicked(self, item, column):
        self.current_filename = item.text(0)
        self.current_filename_size = int(item.text(2))
        self.ui.delete_file.setEnabled(True)
        self.ui.download.setEnabled(True)
        self.ui.rename.setEnabled(True)
        self.ui.edit_currentDir_enter.setEnabled(True)
        self.EnterSelectedDirectory()

    def CreateNewDirectory(self):
        new_Dir, ok = QInputDialog.getText(self.MainWindow, "Create New Directory", "Please input the new directory's "
                                                                                    "name:", QLineEdit.Normal, "")
        if ok is True:
            if True:
                MKD_command = "MKD " + new_Dir + "\r\n"
                self.commands.send(MKD_command.encode())
                self.CommandInfoUpdate(MKD_command, 0)
                QApplication.processEvents()
                MKD_return = self.commands.recv(8192).decode("utf8","ignore")
                self.CommandInfoUpdate(MKD_return, 1)
                QApplication.processEvents()
                self.ShowLIST()

    def RemoveDirectory(self):
        RMD_command = "RMD " + self.current_filename + "\r\n"
        self.commands.send(RMD_command.encode())
        self.CommandInfoUpdate(RMD_command, 0)
        QApplication.processEvents()
        RMD_return = self.commands.recv(8192).decode()
        self.CommandInfoUpdate(RMD_return, 1)
        QApplication.processEvents()
        self.ShowLIST()

    def RenameDirectory(self):
        rename_Dir, ok = QInputDialog.getText(self.MainWindow, "Rename Directory", "Please input the new "
                                                                                   "name:", QLineEdit.Normal, "")
        if ok is True:
            if True:
                RNFR_command = "RNFR " + self.current_filename + "\r\n"
                self.commands.send(RNFR_command.encode())
                self.CommandInfoUpdate(RNFR_command, 0)
                QApplication.processEvents()
                RNFR_return = self.commands.recv(8192).decode()
                self.CommandInfoUpdate(RNFR_return, 1)
                QApplication.processEvents()
                if GetStatusCode(RNFR_return) == "350":
                    RNTO_command = "RNTO " + rename_Dir + "\r\n"
                    self.commands.send(RNTO_command.encode())
                    self.CommandInfoUpdate(RNTO_command, 0)
                    QApplication.processEvents()
                    RNTO_return = self.commands.recv(8192).decode()
                    self.CommandInfoUpdate(RNTO_return, 1)
                    QApplication.processEvents()
                    self.ShowLIST()

    def GetLocal(self):
        dictionary = QFileDialog.getExistingDirectory(self.MainWindow, "选取文件夹", os.getcwd())
        if dictionary != "":
            self.local_download_filepath = dictionary
            self.RETRDownload()

    def RETRDownload(self):
        self.download_file_thread = Download(self.local_download_filepath, self.current_filename, self.connection_mode,
                                             self.server_IP, self.server_port, self.username, self.password,
                                             self.commands, self.current_filename_size, self.current_Dir)
        self.download_file_thread.start()
        self.download_file_thread.RETR_command.connect(self.STORClient)
        self.download_file_thread.RETR_return.connect(self.RETRServer)
        self.download_file_thread.RETR_progress.connect(self.RETRSetProgress)
        self.download_file_thread.RETR_finish.connect(self.STORFinish)

    def OpenLocal(self):
        fileName, fileType = QFileDialog.getOpenFileName(self.MainWindow, "选取文件", os.getcwd(), "All Files(*)")
        if fileName != "":
            self.local_upload_filepath = fileName
            lines = self.local_upload_filepath.split('/')
            self.local_upload_filename = lines[len(lines) - 1]
            self.STORUpload()

    def STORUpload(self):
        if CheckFilenameValidation(self.local_upload_filename) is True:
            self.upload_file_thread = Upload(self.local_upload_filepath, self.local_upload_filename, self.connection_mode,
                                             self.server_IP, self.server_port, self.username, self.password, self.commands, self.current_Dir)
            self.upload_file_thread.start()
            self.upload_file_thread.STOR_command.connect(self.STORClient)
            self.upload_file_thread.STOR_return.connect(self.STORServer)
            self.upload_file_thread.STOR_progress.connect(self.STORSetProgress)
            self.upload_file_thread.STOR_finish.connect(self.STORFinish)

    def RETRServer(self, msg, name, style, size):
        self.CommandInfoUpdate(msg, 1)
        QApplication.processEvents()
        tem = [name, style, self.current_Dir, size, 0]
        self.file_transfer_list.append(tem)
        self.ui.filetransfer.clearContents()
        self.ui.filetransfer.setRowCount(len(self.file_transfer_list))
        for i in range(len(self.file_transfer_list)):
            name = QTableWidgetItem(self.file_transfer_list[i][0])
            self.ui.filetransfer.setItem(i, 0, name)
            style = QLabel(self.file_transfer_list[i][1])
            self.ui.filetransfer.setCellWidget(i, 1, style)
            curDir = QLabel(self.file_transfer_list[i][2])
            self.ui.filetransfer.setCellWidget(i, 2, curDir)
            progress = QProgressBar(self.MainWindow)
            if int(self.file_transfer_list[i][3]) != 0:
                progress.setValue(int(round((100 * int(self.file_transfer_list[i][4]) / int(self.file_transfer_list[i][3])))))
            else:
                progress.setValue(1)
            self.ui.filetransfer.setCellWidget(i, 3, progress)
            self.ui.filetransfer.updateGeometries()

    def RETRSetProgress(self, name, p):
        for i in range(len(self.file_transfer_list)):
            if self.file_transfer_list[i][0] == name:
                self.file_transfer_list[i][4] = self.file_transfer_list[i][4]+p
                progress = self.ui.filetransfer.cellWidget(i, 3)
                if int(self.file_transfer_list[i][3]) != 0:
                    progress.setValue(int(round((100 * int(self.file_transfer_list[i][4]) / int(self.file_transfer_list[i][3])))))
                else:
                    progress.setValue(1)
                self.ui.filetransfer.updateGeometries()
                break

    def STORClient(self, msg):
        self.CommandInfoUpdate(msg, 0)
        QApplication.processEvents()

    def STORServer(self, msg, name, style, size):
        self.CommandInfoUpdate(msg, 1)
        QApplication.processEvents()
        tem = [name, style, self.current_Dir, size, 0]
        self.file_transfer_list.append(tem)
        self.ui.filetransfer.clearContents()
        self.ui.filetransfer.setRowCount(len(self.file_transfer_list))
        for i in range(len(self.file_transfer_list)):
            name = QTableWidgetItem(self.file_transfer_list[i][0])
            self.ui.filetransfer.setItem(i, 0, name)
            style = QLabel(self.file_transfer_list[i][1])
            self.ui.filetransfer.setCellWidget(i, 1, style)
            curDir = QLabel(self.file_transfer_list[i][2])
            self.ui.filetransfer.setCellWidget(i, 2, curDir)
            progress = QProgressBar(self.MainWindow)
            if int(self.file_transfer_list[i][3]) != 0:
                progress.setValue(int(round((100 * int(self.file_transfer_list[i][4]) / int(self.file_transfer_list[i][3])))))
            else:
                progress.setValue(1)
            self.ui.filetransfer.setCellWidget(i, 3, progress)
            self.ui.filetransfer.updateGeometries()

    def STORSetProgress(self, name, p):
        for i in range(len(self.file_transfer_list)):
            if self.file_transfer_list[i][0] == name:
                self.file_transfer_list[i][4] = self.file_transfer_list[i][4]+p
                progress = self.ui.filetransfer.cellWidget(i, 3)
                if int(self.file_transfer_list[i][3]) != 0:
                    progress.setValue(int(round((100 * int(self.file_transfer_list[i][4]) / int(self.file_transfer_list[i][3])))))
                else:
                    progress.setValue(1)
                self.ui.filetransfer.updateGeometries()
                break

    def STORFinish(self, msg, name, Finish):
        if Finish is True:
            self.CommandInfoUpdate(msg, 1)
            self.ShowLIST()
            for i in range(len(self.file_transfer_list)):
                if self.file_transfer_list[i][0] == name:
                    self.file_transfer_list.pop(i)
                    self.ui.filetransfer.removeRow(i)
                    self.ui.filetransfer.updateGeometries()
                    break


class Download(QThread):
    RETR_command = pyqtSignal(str)
    RETR_return = pyqtSignal(str, str, str, int)
    RETR_progress = pyqtSignal(str, int)
    RETR_finish = pyqtSignal(str, str, bool)

    def __init__(self, filepath, filename, mode, IP, port, username, password, command, size, curDir):
        super(Download, self).__init__()
        self.filename = filename
        self.filepath = filepath
        self.listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commands = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_mode = mode
        self.transfer_IP = ""
        self.transfer_port = -1
        self.IP = IP
        self.port = port
        self.username = username
        self.password = password
        self.size = size
        self.curDir = curDir

    def run(self):
        self.commands.connect((self.IP, self.port))
        self.commands.recv(8192).decode()
        USER_command = "USER " + self.username + "\r\n"
        self.commands.send(USER_command.encode())
        USER_return = self.commands.recv(8192).decode()
        if GetStatusCode(USER_return) == "331":
            PASS_command = "PASS " + self.password + "\r\n"
            self.commands.send(PASS_command.encode())
            self.commands.recv(8192).decode()
        CWD_command = "CWD " + self.curDir + "\r\n"
        self.commands.send(CWD_command.encode())
        self.commands.recv(8192).decode()
        if self.connection_mode == "PORT":
            lines = self.commands.getsockname()
            ip_port = [0, 0, 0, 0, 0, 0]
            IP_tem = lines[0]
            port_tem = random.sample(range(20000, 65535), 1)[0]
            IP_lines = IP_tem.split('.')
            if len(IP_lines) == 4:
                for i in range(4):
                    if IP_lines[i].isdigit() is True:
                        ip_port[i] = int(IP_lines[i])
            ip_port[4] = port_tem // 256
            ip_port[5] = port_tem % 256
            PORT_command = "PORT " + str(ip_port[0]) + "," + str(ip_port[1]) + "," + str(ip_port[2]) + "," \
                           + str(ip_port[3]) + "," + str(ip_port[4]) + "," + str(ip_port[5]) + "\r\n"
            self.commands.send(PORT_command.encode())
            PORT_return = self.commands.recv(8192).decode()
            if GetStatusCode(PORT_return) == "200":
                self.connection_mode = "PORT"
                self.transfer_IP = IP_tem
                self.transfer_port = port_tem
                self.listen.bind((self.transfer_IP, self.transfer_port))
                self.listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.listen.listen(64)
        elif self.connection_mode == "PASV":
            PASV_command = "PASV\r\n"
            self.commands.send(PASV_command.encode())
            PASV_return = self.commands.recv(8192).decode()
            if GetStatusCode(PASV_return) == "227":
                ip, port = PasvConnectionParse(PASV_return)
                if ip != -1 or port != -1:
                    self.connection_mode = "PASV"
                    self.transfer_IP = ip
                    self.transfer_port = port
                    self.fd.connect((self.transfer_IP, self.transfer_port))

        RETR_command = "RETR " + self.filename + "\r\n"
        self.commands.send(RETR_command.encode())
        self.RETR_command.emit(RETR_command)
        RETR_return = self.commands.recv(8192).decode()
        self.RETR_return.emit(RETR_return, self.filename, "Download", self.size)

        if GetStatusCode(RETR_return) == "150":
            if self.connection_mode == "PORT":
                self.fd, addr = self.listen.accept()
            path = self.filepath + "/" + self.filename
            fd = open(path, "wb+")
            while 1:
                try:
                    file_transfer = self.fd.recv(8192)
                except:
                    break
                if file_transfer is None or len(file_transfer) <= 0:
                    break
                else:
                    fd.write(file_transfer)
                    self.RETR_progress.emit(self.filename, len(file_transfer))
                    continue
            fd.close()
            self.fd.close()
            if self.connection_mode == "PORT":
                self.listen.close()
            RETR_finish = self.commands.recv(8192).decode()
            self.RETR_finish.emit(RETR_finish, self.filename, True)
            self.exit()


class Upload(QThread):
    STOR_command = pyqtSignal(str)
    STOR_return = pyqtSignal(str, str, str, int)
    STOR_progress = pyqtSignal(str, int)
    STOR_finish = pyqtSignal(str, str, bool)

    def __init__(self, filepath, filename, mode, IP, port, username, password, command, curDir):
        super(Upload, self).__init__()
        self.filename = filename
        self.filepath = filepath
        self.listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.commands = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection_mode = mode
        self.transfer_IP = ""
        self.transfer_port = -1
        self.IP = IP
        self.port = port
        self.username = username
        self.password = password
        self.curDir = curDir

    def run(self):
        self.commands.connect((self.IP, self.port))
        self.commands.recv(8192).decode()
        USER_command = "USER " + self.username + "\r\n"
        self.commands.send(USER_command.encode())
        USER_return = self.commands.recv(8192).decode()
        if GetStatusCode(USER_return) == "331":
            PASS_command = "PASS " + self.password + "\r\n"
            self.commands.send(PASS_command.encode())
            self.commands.recv(8192).decode()
        CWD_command = "CWD " + self.curDir + "\r\n"
        self.commands.send(CWD_command.encode())
        self.commands.recv(8192).decode()
        if self.connection_mode == "PORT":
            lines = self.commands.getsockname()
            ip_port = [0, 0, 0, 0, 0, 0]
            IP_tem = lines[0]
            port_tem = random.sample(range(20000, 65535), 1)[0]
            IP_lines = IP_tem.split('.')
            if len(IP_lines) == 4:
                for i in range(4):
                    if IP_lines[i].isdigit() is True:
                        ip_port[i] = int(IP_lines[i])
            ip_port[4] = port_tem // 256
            ip_port[5] = port_tem % 256
            PORT_command = "PORT " + str(ip_port[0]) + "," + str(ip_port[1]) + "," + str(ip_port[2]) + "," \
                           + str(ip_port[3]) + "," + str(ip_port[4]) + "," + str(ip_port[5]) + "\r\n"
            self.commands.send(PORT_command.encode())
            PORT_return = self.commands.recv(8192).decode("utf-8", "ignore")
            if GetStatusCode(PORT_return) == "200":
                self.connection_mode = "PORT"
                self.transfer_IP = IP_tem
                self.transfer_port = port_tem
                self.listen.bind((self.transfer_IP, self.transfer_port))
                self.listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.listen.listen(64)
        elif self.connection_mode == "PASV":
            PASV_command = "PASV\r\n"
            self.commands.send(PASV_command.encode())
            PASV_return = self.commands.recv(8192).decode()
            if GetStatusCode(PASV_return) == "227":
                ip, port = PasvConnectionParse(PASV_return)
                if ip != -1 or port != -1:
                    self.connection_mode = "PASV"
                    self.transfer_IP = ip
                    self.transfer_port = port
                    self.fd.connect((self.transfer_IP, self.transfer_port))

        STOR_command = "STOR " + self.filename + "\r\n"
        self.commands.send(STOR_command.encode())
        self.STOR_command.emit(STOR_command)
        STOR_return = self.commands.recv(8192).decode()
        try:
            size = os.path.getsize(self.filepath)
        except:
            size = 0
        self.STOR_return.emit(STOR_return, self.filename, "Upload", size)

        if GetStatusCode(STOR_return) == "150":
            if self.connection_mode == "PORT":
                self.fd, addr = self.listen.accept()
            ft = open(self.filepath, "rb+")
            while 1:
                file_transfer = ft.read(8192)
                if file_transfer is None or len(file_transfer) <= 0:
                    break
                else:
                    self.fd.send(file_transfer)
                    self.STOR_progress.emit(self.filename, len(file_transfer))
                    continue
            ft.close()
            self.fd.close()
            if self.connection_mode == "PORT":
                self.listen.close()
            STOR_finish = self.commands.recv(8192).decode()
            self.STOR_finish.emit(STOR_finish, self.filename, True)
            self.exit()
