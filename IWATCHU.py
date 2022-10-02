import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('WATCH Analyzer')   # 창 띄우기
        self.setWindowIcon(QIcon('watch.png'))    # 어플리케이션 아이콘 넣기
        self.setGeometry(300, 150, 1280, 720)
        self.show()

        loadAction = QAction('load image file', self)
        loadAction.triggered.connect(self.Fileload)

        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        # 메뉴바 만들기
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(loadAction)
        filemenu.addAction(exitAction)

        editmenu = menubar.addMenu('&Edit')
        #editmenu.addAction(??) 액션 추가
        viewmenu = menubar.addMenu('&View')
        toolsmenu = menubar.addMenu('&Tools')
        settingsmenu = menubar.addMenu('&Settings')
        helpmenu = menubar.addMenu('&Help')

    def Fileload(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './')

        if fname[0]:
            f = open(fname[0], 'r')

            with f:
                data = f.read()
                # self.setText(data)

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())