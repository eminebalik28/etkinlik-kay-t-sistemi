import sys
from PyQt5.QtWidgets import QApplication
from database import DatabaseManager
from etkinlik_gui import LoginWindow, RegisterWindow, MainWindow


class Controller:
    def __init__(self):
        self.db = DatabaseManager()
        self.login_win = None
        self.reg_win = None
        self.main_win = None
        self.show_login()

    def show_login(self):
        self.login_win = LoginWindow(self.db)
        self.login_win.login_success.connect(self.show_main)
        self.login_win.go_to_register.connect(self.show_register)
        self.login_win.show()

    def show_register(self):
        self.reg_win = RegisterWindow(self.db)
        self.reg_win.go_to_login.connect(self.back_to_login)
        self.reg_win.show()
        self.login_win.hide()

    def back_to_login(self):
        if self.reg_win:
            self.reg_win.close()
        self.login_win.show()

    def show_main(self, rol):
        kadi = self.login_win.txt_kadi.text()
        self.main_win = MainWindow(self.db, rol, kadi)
        self.main_win.logout_signal.connect(self.handle_logout)
        self.main_win.show()
        self.login_win.close()

    def handle_logout(self):
        self.main_win.close()
        self.show_login()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ctrl = Controller()
    sys.exit(app.exec_())