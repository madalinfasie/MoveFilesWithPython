import shutil
import os
import sys
from PyQt4 import QtGui, QtCore


class MainFrame(QtGui.QMainWindow):
    def __init__(self):
        super(MainFrame, self).__init__()
        self.setGeometry(50, 50, 700, 350)
        self.setWindowTitle('Mover - Move Your Files')

        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'logo.png')
        self.setWindowIcon(QtGui.QIcon(path))

        # set style
        self.style_choice('cleanlooks')

        # set a menu bar
        # create the actions for the menu

        # file exit action
        fileExitAction = QtGui.QAction('&Exit', self)
        fileExitAction.setShortcut("Ctrl+Q")
        fileExitAction.setStatusTip('Close the app')
        fileExitAction.triggered.connect(self.close_application)

        self.statusBar()
        # create the actual menu
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(fileExitAction)
        self.home()

    def home(self):
        # set labels
        lblFrom = QtGui.QLabel('From: ')
        lblTo = QtGui.QLabel('To: ')
        lblOptions = QtGui.QLabel('Options: ')

        # set the line edits for from and to file paths
        self.leFrom = QtGui.QLineEdit()
        self.leTo = QtGui.QLineEdit()

        # set browse buttons
        self.btnBrowseFrom = QtGui.QPushButton('Browse...', self)
        self.btnBrowseTo = QtGui.QPushButton('Browse...', self)

        # set action for browse buttons
        self.btnBrowseFrom.clicked.connect(self.file_open_leFrom)
        self.btnBrowseTo.clicked.connect(self.file_open_leTo)

        # set option checkboxes
        ckbMusicOption = QtGui.QCheckBox('Music files', self)
        ckbDocOption = QtGui.QCheckBox('Text files', self)
        ckbVideoOption = QtGui.QCheckBox('Video files', self)
        ckbPicturesOption = QtGui.QCheckBox('Image files', self)
        ckbZipOption = QtGui.QCheckBox('Remove zip files that are already extracted', self)

        # supported extensions
        self.MUSIC_EXTENSIONS = ('.mp3','.ogg', '.wav')
        self.VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mkv', '.flv')
        self.PICTURES_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.gif', '.bmt')
        self.DOCUMENTS_EXTENSIONS = ('.pdf', '.doc', '.docx', '.odt', '.txt', 'ppt', 'pptx', 'xls', 'xlsx')
        self.ZIP_EXTENSIONS = ('.zip', '.tar.gz', '.rar')

        # set actions for checkboxes and create the list of options
        self.checkedOptions = [self.MUSIC_EXTENSIONS, self.VIDEO_EXTENSIONS, self.PICTURES_EXTENSIONS,
                               self.DOCUMENTS_EXTENSIONS]

        ckbMusicOption.setChecked(True)
        ckbMusicOption.stateChanged.connect(lambda: self.checkbox_state(ckbMusicOption))

        ckbDocOption.setChecked(True)
        ckbDocOption.stateChanged.connect(lambda: self.checkbox_state(ckbDocOption))

        ckbVideoOption.setChecked(True)
        ckbVideoOption.stateChanged.connect(lambda: self.checkbox_state(ckbVideoOption))

        ckbPicturesOption.setChecked(True)
        ckbPicturesOption.stateChanged.connect(lambda: self.checkbox_state(ckbPicturesOption))

        ckbZipOption.toggled.connect(lambda: self.checkbox_state(ckbZipOption))

        # progres bar
        self.progress = QtGui.QProgressBar(self)

        # move files button
        self.btnMoveFiles = QtGui.QPushButton('Move files', self)
        self.btnMoveFiles.setMaximumSize(100, 40)
        self.btnMoveFiles.clicked.connect(self.move_files)

        # create a box layout that contains the options
        boxOptions = QtGui.QVBoxLayout()
        boxOptions.addWidget(ckbDocOption)
        boxOptions.addWidget(ckbMusicOption)
        boxOptions.addWidget(ckbPicturesOption)
        boxOptions.addWidget(ckbVideoOption)
        boxOptions.addWidget(ckbZipOption)

        # create box layout with browse buttons and line edit so I can add a form row with more than two parameters
        boxFrom = QtGui.QHBoxLayout()
        boxFrom.addWidget(self.leFrom)
        boxFrom.addWidget(self.btnBrowseFrom)

        boxTo = QtGui.QHBoxLayout()
        boxTo.addWidget(self.leTo)
        boxTo.addWidget(self.btnBrowseTo)

        # create a form layout that contains the options for the user
        formLayout = QtGui.QFormLayout()
        formLayout.addRow(lblFrom, boxFrom)
        formLayout.addRow(lblTo, boxTo)
        formLayout.addRow(lblOptions, boxOptions)

        boxLayoutHorizontal = QtGui.QHBoxLayout()
        boxLayoutHorizontal.addWidget(self.btnMoveFiles)

        # add the form, move files button and progress bar to a box layout
        boxLayout = QtGui.QVBoxLayout()
        boxLayout.addLayout(formLayout)
        boxLayout.addStretch()
        boxLayout.addLayout(boxLayoutHorizontal)
        boxLayout.addWidget(self.progress)

        # add the box layout containing all the components to a central widget
        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(boxLayout)

        # set the central widget as the layout of the window
        self.setCentralWidget(centralWidget)

        self.show()

    # checkbox state changed
    def checkbox_state(self, checkbox):
        if checkbox.text() == "Music files":
            if checkbox.isChecked():
                self.checkedOptions.append(self.MUSIC_EXTENSIONS)
            else:
                self.checkedOptions.remove(self.MUSIC_EXTENSIONS)

        if checkbox.text() == "Text files":
            if checkbox.isChecked():
                self.checkedOptions.append(self.DOCUMENTS_EXTENSIONS)
            else:
                self.checkedOptions.remove(self.DOCUMENTS_EXTENSIONS)

        if checkbox.text() == "Video files":
            if checkbox.isChecked():
                self.checkedOptions.append(self.VIDEO_EXTENSIONS)
            else:
                self.checkedOptions.remove(self.VIDEO_EXTENSIONS)

        if checkbox.text() == "Image files":
            if checkbox.isChecked():
                self.checkedOptions.append(self.PICTURES_EXTENSIONS)
            else:
                self.checkedOptions.remove(self.PICTURES_EXTENSIONS)

        if checkbox.text() == "Remove zip files that are already extracted":
            if checkbox.isChecked():
                self.checkedOptions.append(self.ZIP_EXTENSIONS)
            else:
                self.checkedOptions.remove(self.ZIP_EXTENSIONS)

    # open file
    def file_open_leFrom(self):
        directoryPath = QtGui.QFileDialog.getExistingDirectory(self, 'Select directory')
        self.leFrom.setText(directoryPath)

    # open file
    def file_open_leTo(self):
        directoryPath = QtGui.QFileDialog.getExistingDirectory(self, 'Select directory')
        self.leTo.setText(directoryPath)

    # progress bar function
    def move_files(self):
        # show a warning before moving files
        choice = QtGui.QMessageBox.question(self,
                                            'Warning!',
                                            'Are you sure you want to move this files?',
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            self.run_move_files(self.leFrom.text(), self.leTo.text(), self.checkedOptions)
        else:
            pass

    # close application
    def close_application(self):
        # Warning message
        choice = QtGui.QMessageBox.question(self,
                                            'Warning!',
                                            'Are you sure you want to exit?',
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    # choose style
    @staticmethod
    def style_choice(text):
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(text))

    def run_move_files(self, file_path_from, file_path_to, file_extensions):
        duplicate = 1
        n_files = 0

        # count all the files affected
        for extensions in file_extensions:
            for root, dirs, files in os.walk(file_path_from):
                for file_name in files:
                    if file_name.endswith(extensions) and root == file_path_from:
                        n_files += 1

        # execute the operation
        for extensions in file_extensions:
            for root, dirs, files in os.walk(file_path_from):
                for file_name in files:
                    if file_name.endswith(extensions) and root == file_path_from and not file_name.endswith(
                            self.ZIP_EXTENSIONS):
                        file_path = file_path_from + '/' + file_name
                        while os.path.exists(file_path_to + '/' + file_name):
                            file_name = file_name[:file_name.rfind('.')] + '_' + str(duplicate) + file_name[
                                                                                                  file_name.rfind('.'):]
                            duplicate += 1

                        shutil.move(file_path, file_path_to + '/' + file_name)
                    elif file_name.endswith(self.ZIP_EXTENSIONS) and root == file_path_from:
                        for mydir in dirs:
                            if mydir == file_name[:file_name.rfind('.zip')] or \
                                            mydir == file_name[:file_name.rfind('.tar.gz')] or \
                                            mydir == file_name[:file_name.rfind('.rar')]:
                                file_path = root + '/' + file_name
                                os.remove(file_path)

        self.completed = 0
        while self.completed < 100:
            self.completed += 100 / n_files
            self.progress.setValue(self.completed)


def run():
    app = QtGui.QApplication(sys.argv)
    buildGui = MainFrame()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()
