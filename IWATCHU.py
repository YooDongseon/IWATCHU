import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.Qt import QFileSystemModel

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('WATCH Analyzer')   # 창 띄우기
        self.setWindowIcon(QIcon('watch.png'))    # 어플리케이션 아이콘 넣기
        self.setGeometry(300, 150, 1280, 720)

        loadAction = QAction('load image file', self)
        loadAction.triggered.connect(self.Fileload)

        exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        # 메뉴바 만들기 -----------------------------------------------------
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

        # 창 나누기 ---------------------------------------------------------
        left = QFrame()
        left.setFrameShape(QFrame.Box)
        # left.setFrameShadow(QFrame.Sunken)

        right = QFrame()
        right.setFrameShape(QFrame.Box)

        bottom = QFrame()
        bottom.setFrameShape(QFrame.Box)

        self.splitter1 = QSplitter(Qt.Vertical, self)
        self.splitter1.addWidget(right)
        self.splitter1.addWidget(bottom)

        self.splitter2 = QSplitter(Qt.Horizontal, self)
        self.splitter2.setGeometry(10, 40, 1260, 670)
        self.splitter2.addWidget(left)
        self.splitter2.addWidget(self.splitter1)

        self.splitter1.setSizes([200, 100])
        self.splitter2.setSizes([100, 400])

        # 파일 트리뷰 --------------------------------------------------------
        self.path_root = QtCore.QDir.rootPath() # 기본 C 드라이브 경로... 추후 수정
        self.model = QFileSystemModel()
        self.model.setRootPath(self.path_root)

        self.index_root = self.model.index(self.model.rootPath())

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.index_root)
        self.tree_view.clicked.connect(self.on_treeView_clicked)

        # self.setCentralWidget(self.tree_view)

    @pyqtSlot(QtCore.QModelIndex)
    def on_treeView_clicked(self, index):
        indexItem = self.model.index(index.row(), 0, index.parent())

        fileName = self.model.fileName(indexItem)
        filePath = self.model.filePath(indexItem)

        print(fileName)
        print(filePath)

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
   ex.show()
   sys.exit(app.exec_())