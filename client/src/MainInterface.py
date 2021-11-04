# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainInterface.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1288, 795)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.IP_address = QtWidgets.QLineEdit(self.centralwidget)
        self.IP_address.setGeometry(QtCore.QRect(80, 20, 121, 21))
        self.IP_address.setObjectName("IP_address")
        self.username = QtWidgets.QLineEdit(self.centralwidget)
        self.username.setGeometry(QtCore.QRect(280, 20, 113, 21))
        self.username.setObjectName("username")
        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setGeometry(QtCore.QRect(460, 20, 113, 21))
        self.password.setObjectName("password")
        self.port = QtWidgets.QLineEdit(self.centralwidget)
        self.port.setGeometry(QtCore.QRect(650, 20, 41, 21))
        self.port.setObjectName("port")
        self.login = QtWidgets.QPushButton(self.centralwidget)
        self.login.setGeometry(QtCore.QRect(696, 15, 91, 32))
        self.login.setObjectName("login")
        self.label_host = QtWidgets.QLabel(self.centralwidget)
        self.label_host.setGeometry(QtCore.QRect(20, 20, 58, 16))
        self.label_host.setObjectName("label_host")
        self.label_username = QtWidgets.QLabel(self.centralwidget)
        self.label_username.setGeometry(QtCore.QRect(210, 20, 58, 16))
        self.label_username.setObjectName("label_username")
        self.label_password = QtWidgets.QLabel(self.centralwidget)
        self.label_password.setGeometry(QtCore.QRect(400, 20, 58, 16))
        self.label_password.setObjectName("label_password")
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setGeometry(QtCore.QRect(590, 20, 58, 16))
        self.label_port.setObjectName("label_port")
        self.command_info = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.command_info.setGeometry(QtCore.QRect(20, 60, 1241, 261))
        self.command_info.setObjectName("command_info")
        self.logout = QtWidgets.QPushButton(self.centralwidget)
        self.logout.setGeometry(QtCore.QRect(790, 15, 91, 32))
        self.logout.setObjectName("logout")
        self.label_currentDir = QtWidgets.QLabel(self.centralwidget)
        self.label_currentDir.setGeometry(QtCore.QRect(23, 380, 81, 16))
        self.label_currentDir.setObjectName("label_currentDir")
        self.current_Directory = QtWidgets.QLineEdit(self.centralwidget)
        self.current_Directory.setGeometry(QtCore.QRect(110, 378, 371, 21))
        self.current_Directory.setReadOnly(True)
        self.current_Directory.setObjectName("current_Directory")
        self.edit_currentDir = QtWidgets.QPushButton(self.centralwidget)
        self.edit_currentDir.setGeometry(QtCore.QRect(480, 374, 91, 32))
        self.edit_currentDir.setObjectName("edit_currentDir")
        self.edit_currentDir_up = QtWidgets.QPushButton(self.centralwidget)
        self.edit_currentDir_up.setGeometry(QtCore.QRect(570, 374, 91, 32))
        self.edit_currentDir_up.setObjectName("edit_currentDir_up")
        self.label_currentDir_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_currentDir_2.setGeometry(QtCore.QRect(50, 410, 61, 16))
        self.label_currentDir_2.setObjectName("label_currentDir_2")
        self.upload = QtWidgets.QPushButton(self.centralwidget)
        self.upload.setGeometry(QtCore.QRect(660, 560, 91, 32))
        self.upload.setObjectName("upload")
        self.delete_file = QtWidgets.QPushButton(self.centralwidget)
        self.delete_file.setGeometry(QtCore.QRect(660, 590, 91, 32))
        self.delete_file.setObjectName("delete_file")
        self.download = QtWidgets.QPushButton(self.centralwidget)
        self.download.setGeometry(QtCore.QRect(660, 530, 91, 32))
        self.download.setObjectName("download")
        self.rename = QtWidgets.QPushButton(self.centralwidget)
        self.rename.setGeometry(QtCore.QRect(660, 500, 91, 32))
        self.rename.setObjectName("rename")
        self.LIST = QtWidgets.QPushButton(self.centralwidget)
        self.LIST.setGeometry(QtCore.QRect(660, 410, 91, 32))
        self.LIST.setObjectName("LIST")
        self.NewFile = QtWidgets.QPushButton(self.centralwidget)
        self.NewFile.setGeometry(QtCore.QRect(660, 470, 91, 32))
        self.NewFile.setObjectName("NewFile")
        self.label_currentDir_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_currentDir_3.setGeometry(QtCore.QRect(48, 347, 61, 16))
        self.label_currentDir_3.setObjectName("label_currentDir_3")
        self.connection_mode = QtWidgets.QComboBox(self.centralwidget)
        self.connection_mode.setGeometry(QtCore.QRect(106, 341, 91, 32))
        self.connection_mode.setObjectName("connection_mode")
        self.IP_address_PORT = QtWidgets.QLineEdit(self.centralwidget)
        self.IP_address_PORT.setEnabled(True)
        self.IP_address_PORT.setGeometry(QtCore.QRect(225, 345, 111, 21))
        self.IP_address_PORT.setDragEnabled(False)
        self.IP_address_PORT.setReadOnly(True)
        self.IP_address_PORT.setClearButtonEnabled(False)
        self.IP_address_PORT.setObjectName("IP_address_PORT")
        self.label_host_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_host_2.setGeometry(QtCore.QRect(205, 347, 21, 16))
        self.label_host_2.setObjectName("label_host_2")
        self.label_port_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_port_2.setGeometry(QtCore.QRect(343, 347, 31, 16))
        self.label_port_2.setObjectName("label_port_2")
        self.port_PORT = QtWidgets.QLineEdit(self.centralwidget)
        self.port_PORT.setEnabled(True)
        self.port_PORT.setGeometry(QtCore.QRect(377, 345, 61, 21))
        self.port_PORT.setReadOnly(True)
        self.port_PORT.setObjectName("port_PORT")
        self.file_list = QtWidgets.QTreeWidget(self.centralwidget)
        self.file_list.setGeometry(QtCore.QRect(110, 410, 541, 321))
        self.file_list.setTextElideMode(QtCore.Qt.ElideRight)
        self.file_list.setIndentation(0)
        self.file_list.setColumnCount(4)
        self.file_list.setObjectName("file_list")
        self.file_list.headerItem().setText(0, "1")
        self.file_list.headerItem().setText(1, "2")
        self.file_list.headerItem().setText(2, "3")
        self.file_list.headerItem().setText(3, "4")
        self.file_list.header().setStretchLastSection(True)
        self.edit_currentDir_enter = QtWidgets.QPushButton(self.centralwidget)
        self.edit_currentDir_enter.setGeometry(QtCore.QRect(660, 440, 91, 32))
        self.edit_currentDir_enter.setObjectName("edit_currentDir_enter")
        self.filetransfer = QtWidgets.QTableWidget(self.centralwidget)
        self.filetransfer.setGeometry(QtCore.QRect(760, 380, 501, 351))
        self.filetransfer.setGridStyle(QtCore.Qt.NoPen)
        self.filetransfer.setObjectName("filetransfer")
        self.filetransfer.setColumnCount(0)
        self.filetransfer.setRowCount(0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1288, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.login.setText(_translate("MainWindow", "登录"))
        self.label_host.setText(_translate("MainWindow", "主机(H)"))
        self.label_username.setText(_translate("MainWindow", "用户名(U)"))
        self.label_password.setText(_translate("MainWindow", "密码(W)"))
        self.label_port.setText(_translate("MainWindow", "端口(P)"))
        self.logout.setText(_translate("MainWindow", "退出"))
        self.label_currentDir.setText(_translate("MainWindow", "当前工作路径"))
        self.edit_currentDir.setText(_translate("MainWindow", "修改"))
        self.edit_currentDir_up.setText(_translate("MainWindow", "回到上一级"))
        self.label_currentDir_2.setText(_translate("MainWindow", "当前目录"))
        self.upload.setText(_translate("MainWindow", "上传文件..."))
        self.delete_file.setText(_translate("MainWindow", "删除"))
        self.download.setText(_translate("MainWindow", "下载文件..."))
        self.rename.setText(_translate("MainWindow", "重命名"))
        self.LIST.setText(_translate("MainWindow", "获取列表"))
        self.NewFile.setText(_translate("MainWindow", "新建文件夹"))
        self.label_currentDir_3.setText(_translate("MainWindow", "连接模式"))
        self.label_host_2.setText(_translate("MainWindow", "IP"))
        self.label_port_2.setText(_translate("MainWindow", "Port"))
        self.edit_currentDir_enter.setText(_translate("MainWindow", "进入"))