import shutil
import os
import sys
from PyQt5.QtWidgets import (QApplication,
                             QMainWindow,
                             QAction,
                             QLabel,
                             QLineEdit,
                             QPushButton,
                             QCheckBox,
                             QProgressBar,
                             QVBoxLayout,
                             QHBoxLayout,
                             QFormLayout,
                             QFileDialog,
                             QWidget,
                             QStyleFactory,
                             QMessageBox)
from PyQt5.QtGui import (QIcon,)


# supported extensions
MUSIC_EXTENSIONS = ('.mp3',
                    '.ogg',
                    '.wav')
VIDEO_EXTENSIONS = ('.mp4',
                    '.avi',
                    '.mkv',
                    '.flv')
PICTURES_EXTENSIONS = ('.jpg',
                       '.jpeg',
                       '.png',
                       '.tiff',
                       '.gif',
                       '.bmt')
DOCUMENTS_EXTENSIONS = ('',
                        '.pdf',
                        '.doc',
                        '.docx',
                        '.odt',
                        '.txt',
                        '.ppt',
                        '.pptx',
                        '.xls',
                        '.xlsx')
ZIP_EXTENSIONS = ('.zip',
                  '.tar.gz',
                  '.rar')

class Mover:
    def __init__(self, progressbar):
        self.progress = progressbar

    def run_move_files(self, file_path_from, file_path_to, file_extensions):
        """ The logic for moving the files from one location to another
        It takes as parameters the two locations and a list with the
        extensions for the files that will be moved """
        duplicate = 1
        n_files = 0

        # count all the files affected
        for extensions in file_extensions:
            for root, dirs, files in os.walk(file_path_from):
                for file_name in files:
                    if file_name.endswith(extensions)\
                        and root == file_path_from:
                        n_files += 1

        if n_files > 0:
            # execute the operation
            for extensions in file_extensions:
                for root, dirs, files in os.walk(file_path_from):
                    for file_name in files:
                        if file_name.endswith(extensions)\
                            and root == file_path_from\
                            and not file_name.endswith(ZIP_EXTENSIONS):

                            file_path = file_path_from + '/' + file_name
                            while os.path\
                                    .exists(file_path_to + '/' + file_name):
                                file_name = file_name[:file_name.rfind('.')]\
                                            + '_'\
                                            + str(duplicate)\
                                            + file_name[file_name.rfind('.'):]
                                duplicate += 1

                            shutil.move(file_path,
                                        file_path_to\
                                        + '/'\
                                        + file_name)
                        elif file_name.endswith(ZIP_EXTENSIONS)\
                            and root == file_path_from:

                            for mydir in dirs:
                                if mydir == file_name[:file_name.rfind('.zip')]\
                                    or mydir == file_name[:file_name.rfind('.tar.gz')]\
                                    or mydir == file_name[:file_name.rfind('.rar')]:

                                    file_path = root + '/' + file_name
                                    os.remove(file_path)

            completed = 0
            while completed <= 100:
                completed += 100 / n_files
                self.progress.setValue(completed)


class MainFrame(QMainWindow):
    """ The main frame of the app """
    def __init__(self):
        super(MainFrame, self).__init__()
        self.setGeometry(50, 50, 700, 350)
        self.setWindowTitle('Mover - Move Your Files')

        path = os.path.join(os.path.dirname(sys.modules[__name__].__file__),
                            'logo.png')
        self.setWindowIcon(QIcon(path))

        # set style
        self.style_choice('cleanlooks')

        # set a menu bar
        # create the actions for the menu

        # file exit action
        file_exit_action = QAction('&Exit', self)
        file_exit_action.setShortcut("Ctrl+Q")
        file_exit_action.setStatusTip('Close the app')
        file_exit_action.triggered.connect(self.close_application)

        self.statusBar()
        # create the actual menu
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(file_exit_action)
        self.home()

    def home(self):
        """ Build the UI design for the application """
        # set labels
        lbl_from = QLabel('From: ')
        lbl_to = QLabel('To: ')
        lbl_options = QLabel('Options: ')

        # set the line edits for from and to file paths
        self.le_from = QLineEdit()
        self.le_to = QLineEdit()

        # set browse buttons
        self.btn_browse_from = QPushButton('Browse...', self)
        self.btn_browse_to = QPushButton('Browse...', self)

        # set action for browse buttons
        self.btn_browse_from.clicked.connect(self.file_open_le_from)
        self.btn_browse_to.clicked.connect(self.file_open_le_to)

        # set option checkboxes
        ckb_music_option = QCheckBox('Music files', self)
        ckb_doc_option = QCheckBox('Text files', self)
        ckb_video_option = QCheckBox('Video files', self)
        ckb_pictures_option = QCheckBox('Image files', self)
        ckb_zip_option = QCheckBox('Remove zip files that are already extracted',
                                   self)

        # set actions for checkboxes and create the list of options
        self.checkedOptions = [MUSIC_EXTENSIONS,
                               VIDEO_EXTENSIONS,
                               PICTURES_EXTENSIONS,
                               DOCUMENTS_EXTENSIONS]

        ckb_music_option.setChecked(True)
        ckb_music_option.stateChanged\
                        .connect(lambda: self.checkbox_state(ckb_music_option))

        ckb_doc_option.setChecked(True)
        ckb_doc_option.stateChanged\
                      .connect(lambda: self.checkbox_state(ckb_doc_option))

        ckb_video_option.setChecked(True)
        ckb_video_option.stateChanged\
                        .connect(lambda: self.checkbox_state(ckb_video_option))

        ckb_pictures_option.setChecked(True)
        ckb_pictures_option.stateChanged\
                           .connect(lambda: self.checkbox_state(ckb_pictures_option))

        ckb_zip_option.toggled\
                      .connect(lambda: self.checkbox_state(ckb_zip_option))

        # progres bar
        self.progress = QProgressBar(self)

        # move files button
        self.btn_move_files = QPushButton('Move files', self)
        self.btn_move_files.setMaximumSize(100, 40)
        self.btn_move_files.clicked.connect(self.move_files)

        # create a box layout that contains the options
        box_options = QVBoxLayout()
        box_options.addWidget(ckb_doc_option)
        box_options.addWidget(ckb_music_option)
        box_options.addWidget(ckb_pictures_option)
        box_options.addWidget(ckb_video_option)
        box_options.addWidget(ckb_zip_option)

        # create box layout with browse buttons and line edit
        # so I can add a form row with more than two parameters
        box_from = QHBoxLayout()
        box_from.addWidget(self.le_from)
        box_from.addWidget(self.btn_browse_from)

        box_to = QHBoxLayout()
        box_to.addWidget(self.le_to)
        box_to.addWidget(self.btn_browse_to)

        # create a form layout that contains the options for the user
        form_layout = QFormLayout()
        form_layout.addRow(lbl_from, box_from)
        form_layout.addRow(lbl_to, box_to)
        form_layout.addRow(lbl_options, box_options)

        box_layout_horizontal = QHBoxLayout()
        box_layout_horizontal.addWidget(self.btn_move_files)

        # add the form, move files button and progress bar to a box layout
        box_layout = QVBoxLayout()
        box_layout.addLayout(form_layout)
        box_layout.addStretch()
        box_layout.addLayout(box_layout_horizontal)
        box_layout.addWidget(self.progress)

        # add the box layout containing all the components to a central widget
        central_widget = QWidget()
        central_widget.setLayout(box_layout)

        # set the central widget as the layout of the window
        self.setCentralWidget(central_widget)

        self.show()

    # checkbox state changed
    def checkbox_state(self, checkbox):
        """ Add to the options list the checked checkboxes """
        if checkbox.text() == "Music files":
            if checkbox.isChecked():
                self.checkedOptions.append(MUSIC_EXTENSIONS)
            else:
                self.checkedOptions.remove(MUSIC_EXTENSIONS)

        if checkbox.text() == "Text files":
            if checkbox.isChecked():
                self.checkedOptions.append(DOCUMENTS_EXTENSIONS)
            else:
                self.checkedOptions.remove(DOCUMENTS_EXTENSIONS)

        if checkbox.text() == "Video files":
            if checkbox.isChecked():
                self.checkedOptions.append(VIDEO_EXTENSIONS)
            else:
                self.checkedOptions.remove(VIDEO_EXTENSIONS)

        if checkbox.text() == "Image files":
            if checkbox.isChecked():
                self.checkedOptions.append(PICTURES_EXTENSIONS)
            else:
                self.checkedOptions.remove(PICTURES_EXTENSIONS)

        if checkbox.text() == "Remove zip files that are already extracted":
            if checkbox.isChecked():
                self.checkedOptions.append(ZIP_EXTENSIONS)
            else:
                self.checkedOptions.remove(ZIP_EXTENSIONS)

    # open file
    def file_open_le_from(self):
        """ Open the directory browser to select the from directory """
        directory_path = QFileDialog.getExistingDirectory(self,
                                                          'Select directory')
        self.le_from.setText(directory_path)

    # open file
    def file_open_le_to(self):
        """ Open the directory browser to select the to directory """
        directory_path = QFileDialog.getExistingDirectory(self,
                                                          'Select directory')
        self.le_to.setText(directory_path)

    # progress bar function
    def move_files(self):
        """ Move the files and give an alert to get user's approval """
        # show a warning before moving files
        choice = QMessageBox.question(self,
                                      'Warning!',
                                      'Are you sure you want to move this files?',
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            mover = Mover(self.progress)
            mover.run_move_files(self.le_from.text(),
                                self.le_to.text(),
                                self.checkedOptions)
        else:
            pass

    # close application
    def close_application(self):
        """ Close the app """
        # Warning message
        choice = QMessageBox.question(self,
                                      'Warning!',
                                      'Are you sure you want to exit?',
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    # choose style
    @staticmethod
    def style_choice(text):
        """ Set the style provided as a parameter """
        QApplication.setStyle(QStyleFactory.create(text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    build_gui = MainFrame()
    sys.exit(app.exec_())
