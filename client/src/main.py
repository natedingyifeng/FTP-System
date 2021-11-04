import sys
from ClientConnection import Connection
import MainInterface
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = MainInterface.Ui_MainWindow()
    ui.setupUi(MainWindow)
    client = Connection(ui, MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
