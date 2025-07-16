import sys


# import subprocess
# def gen_requirements_txt():
#     subprocess.check_call([sys.executable, "-m", "pip", "freeze", ">", "requirements.txt"])
# gen_requirements_txt()


from PySide6.QtWidgets import QApplication

from lib import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(500, 50, 600, 400)
    window.show()
    sys.exit(app.exec())
    