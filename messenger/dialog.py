# from client import Client
from PyQt5 import QtWidgets
from MyForm import Ui_MyForm
import sys

class MyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_MyForm()
        self.ui.setupUi(self)
        # self.client = Client('localhost', 7777)
        # self.client.go()
        # self.ui.btnOk.clicked.connect(self.dialog_ok)
        # self.textEdit = QtWidgets.QTextEdit
        # self.textEdit.read

    # def dialog_ok(self):
    #     name = self.ui.lineEdit.text()
    #     self.client.user_name = name
    #     self.client.go()

# if __name__ == '__main__':
#     app = QtWidgets.QApplication(sys.argv)
#     dialog = MyDialog()
#     dialog.show()
#     # dialog.client.go()
#     sys.exit(app.exec_())