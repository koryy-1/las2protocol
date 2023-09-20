import sys
from PyQt5.QtWidgets import QApplication

from LASFileAnalyzer import LASFileAnalyzer


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LASFileAnalyzer()
    window.show()
    sys.exit(app.exec_())
