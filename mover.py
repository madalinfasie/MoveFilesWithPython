import shutil
import sys
import os
from os import path
from subprocess import check_call
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
                  '.rar',
                  '.gzip',
                  '.7z')


class Mover:
    """ Moves files from one folder to another """
    def __init__(self, progressbar):
        self.progress = progressbar

    @staticmethod
    def __flatten_list(list_):
        """ Flatten a list of lists (only one level) """
        return [extension for ext_tuple in list_ for extension in ext_tuple]

    def run_move_files(self, file_path_from, file_path_to, file_extensions):
        """ The logic for moving the files from one location to another
        It takes as parameters the two locations and a list with the
        extensions for the files that will be moved """
        n_files = 0
        remove_zips = False

        # If zip option is checked, remove the extensions from list
        # and mark remove_zips as True
        if ZIP_EXTENSIONS in file_extensions:
            remove_zips = True
            file_extensions.remove(ZIP_EXTENSIONS)

        # Flatten the list of extensions
        file_extensions = Mover.__flatten_list(file_extensions)

        # Get file count for the source folder
        for _, _, files in os.walk(file_path_from):
            n_files = len([file for file in files
                           if file.endswith(tuple(file_extensions))])
            break

        # Return if there are no files in the folder
        if not n_files:
            return -1

        # Move files and remove archives that were already unzipped
        for _, dirs, files in os.walk(file_path_from):
            for file_name in files:
                if file_name.endswith(tuple(file_extensions)):
                    duplicate = 0
                    file_name_dest = file_name
                    while path.exists(path.join(file_path_to, file_name_dest)):
                        duplicate += 1
                        f_name, extension = path.splitext(file_name)
                        file_name_dest = f'{f_name} ({duplicate}){extension}'

                    shutil.move(path.join(file_path_from, file_name),
                                path.join(file_path_to, file_name_dest))

                if remove_zips:
                    for dir_name in dirs:
                        if dir_name == path.splitext(file_name):
                            os.remove(path.join(file_path_from, file_name))

            completed = 0
            while completed <= 100:
                completed += 100 / n_files
                self.progress.setValue(completed)

            # Break after the first execution so just the folders in
            # current folder are moved
            return n_files


class MainFrame(QMainWindow):
    """ The main frame of the app """
    def __init__(self):
        super(MainFrame, self).__init__()
        self.setGeometry(50, 50, 700, 350)
        self.setWindowTitle('Mover - Move Your Files')

        logo_path = path.join(os.path.dirname(sys.modules[__name__].__file__),
                              'logo.png')
        self.setWindowIcon(QIcon(logo_path))

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
        self.btn_switch = QPushButton('Switch', self)

        # set action for browse buttons
        self.btn_browse_from.clicked.connect(self.file_open_le_from)
        self.btn_browse_to.clicked.connect(self.file_open_le_to)
        self.btn_switch.clicked.connect(self.switch_paths)

        # set option checkboxes
        ckb_music_option = QCheckBox('Music files', self)
        ckb_doc_option = QCheckBox('Text files', self)
        ckb_video_option = QCheckBox('Video files', self)
        ckb_pictures_option = QCheckBox('Image files', self)
        ckb_zip_option = QCheckBox('Remove zip files that are already extracted',
                                   self)

        # set actions for checkboxes and create the list of options
        self.checked_options = [MUSIC_EXTENSIONS,
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
        box_layout_horizontal_switch = QHBoxLayout()
        box_layout_horizontal_switch.addWidget(self.btn_switch)

        # add the form, move files button and progress bar to a box layout
        box_layout = QVBoxLayout()
        box_layout.addLayout(form_layout)
        box_layout.addStretch()
        box_layout.addLayout(box_layout_horizontal)
        box_layout.addLayout(box_layout_horizontal_switch)
        box_layout.addWidget(self.progress)

        # add the box layout containing all the components to a central widget
        central_widget = QWidget()
        central_widget.setLayout(box_layout)

        # set the central widget as the layout of the window
        self.setCentralWidget(central_widget)

        # Set the defaults from cache file
        if path.exists('.cachedpaths'):
            with open('.cachedpaths', 'r') as cache:
                lines = cache.readlines()
                self.le_from.setText(lines[0].strip())
                self.le_to.setText(lines[1].strip())

                # Get a list of tuples of all the options from the cache
                options = [tuple(line[1:-2].replace("'", '').split(', '))\
                           for line in lines[2:]]
                if MUSIC_EXTENSIONS in options:
                    ckb_music_option.setChecked(True)
                else:
                    ckb_music_option.setChecked(False)

                if DOCUMENTS_EXTENSIONS in options:
                    ckb_doc_option.setChecked(True)
                else:
                    ckb_doc_option.setChecked(False)

                if PICTURES_EXTENSIONS in options:
                    ckb_pictures_option.setChecked(True)
                else:
                    ckb_pictures_option.setChecked(False)

                if VIDEO_EXTENSIONS in options:
                    ckb_video_option.setChecked(True)
                else:
                    ckb_video_option.setChecked(False)

                if ZIP_EXTENSIONS in options:
                    ckb_zip_option.setChecked(True)
                else:
                    ckb_zip_option.setChecked(False)

        self.show()

    # checkbox state changed
    def checkbox_state(self, checkbox):
        """ Add to the options list the checked checkboxes """
        if checkbox.text() == "Music files":
            if checkbox.isChecked():
                self.checked_options.append(MUSIC_EXTENSIONS)
            else:
                self.checked_options.remove(MUSIC_EXTENSIONS)

        if checkbox.text() == "Text files":
            if checkbox.isChecked():
                self.checked_options.append(DOCUMENTS_EXTENSIONS)
            else:
                self.checked_options.remove(DOCUMENTS_EXTENSIONS)

        if checkbox.text() == "Video files":
            if checkbox.isChecked():
                self.checked_options.append(VIDEO_EXTENSIONS)
            else:
                self.checked_options.remove(VIDEO_EXTENSIONS)

        if checkbox.text() == "Image files":
            if checkbox.isChecked():
                self.checked_options.append(PICTURES_EXTENSIONS)
            else:
                self.checked_options.remove(PICTURES_EXTENSIONS)

        if checkbox.text() == "Remove zip files that are already extracted":
            if checkbox.isChecked():
                self.checked_options.append(ZIP_EXTENSIONS)
            else:
                self.checked_options.remove(ZIP_EXTENSIONS)

    def file_open_le_from(self):
        """ Open the directory browser to select the from directory """
        directory_path = QFileDialog.getExistingDirectory(self,
                                                          'Select directory')
        self.le_from.setText(directory_path)

    def file_open_le_to(self):
        """ Open the directory browser to select the to directory """
        directory_path = QFileDialog.getExistingDirectory(self,
                                                          'Select directory')
        self.le_to.setText(directory_path)

    def switch_paths(self):
        """ Switch from and to paths """
        path_from = self.le_from.text()
        path_to = self.le_to.text()

        self.le_from.setText(path_to)
        self.le_to.setText(path_from)

    @staticmethod
    def cache_paths(path_from, path_to, checkbox_options):
        """Save current configuration and make the file hidden"""
        if path.exists('.cachedpaths'):
            os.remove('.cachedpaths')

        with open('.cachedpaths', 'w') as cache:
            cache.write(f'{path_from}\n{path_to}\n')
            for options in checkbox_options:
                cache.write(f'{options}\n')

        if os.name == 'nt':
            check_call(['attrib', '+H', '.cachedpaths'])

    def move_files(self):
        """ Move the files and give an alert to get user's approval """
        # show a warning before moving files
        choice = QMessageBox.question(self,
                                      'Warning!',
                                      'Are you sure you want to move these files?',
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            self.progress.reset()
            # Save paths to cache
            MainFrame.cache_paths(self.le_from.text(),
                                  self.le_to.text(),
                                  self.checked_options)

            # Move the files
            mover = Mover(self.progress)
            result = mover.run_move_files(self.le_from.text(),
                                          self.le_to.text(),
                                          self.checked_options)

            if result > 0:
                self.statusBar()\
                    .showMessage(f'Done. {result} files have been moved.')
            elif result == -1:
                self.statusBar()\
                    .showMessage('No files to move.')
            else:
                self.statusBar()\
                    .showMessage('Something went wrong. Please try again.')

    def close_application(self):
        """ Close the app """
        # Warning message
        choice = QMessageBox.question(self,
                                      'Warning!',
                                      'Are you sure you want to exit?',
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()

    @staticmethod
    def style_choice(text):
        """ Set the style provided as a parameter """
        QApplication.setStyle(QStyleFactory.create(text))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    build_gui = MainFrame()
    sys.exit(app.exec_())