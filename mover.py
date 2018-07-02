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
                             QMessageBox,
                             )
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, QObject, pyqtSlot, pyqtSignal


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
    signal_progressbar = pyqtSignal(int)
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
        total_files_size = 0
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
                total_files_size += path.getsize(path.join(file_path_from,
                                                           file_name))
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

            # import threading

            # threading.Thread(target=self.update_progress,
            #                 args=(total_files_size,)
            #                 ).start()
            # percentage = 0
            # print(n_files)
            # while percentage <= n_files:
            #     percentage += 100 / n_files
            #     self.slot_progressbar.emit(percentage)

            # Break after the first execution so just the folders in
            # current folder are moved
            return n_files

    # def update_progress(self, total_files_size):
    #     """ Update function for the progressbar """        
    #     completed = 0
    #     while completed <= 100:
    #         completed += 100 / total_files_size
    #         self.progress.setValue(completed)

class MainFrame(QMainWindow):
    """ The main frame of the app """
    def __init__(self):
        super(MainFrame, self).__init__()
        self.setGeometry(50, 50, 700, 350)
        self.setWindowTitle('Mover - Move Your Files')
        logo_path = path.join(os.path.dirname(sys.modules[__name__].__file__),
                              'logo.png')
        self.setWindowIcon(QIcon(logo_path))

        self.style_choice('cleanlooks')

        # Defaults
        self.checked_options = []
        self.statusBar()

        self.ckb_music_text = 'Music files'
        self.ckb_doc_text = 'Text files'
        self.ckb_video_text = 'Video files'
        self.ckb_pictures_text = 'Image files'
        self.ckb_zip_text = 'Remove zip files that are already extracted'

        # Setup the menu bar
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        # File exit action
        file_exit_action = QAction('&Exit', self)
        file_exit_action.setShortcut("Ctrl+Q")
        file_exit_action.setStatusTip('Close the app')
        file_exit_action.triggered.connect(self.close_application)

        # Add actions to the menu
        file_menu.addAction(file_exit_action)

        # Build the UI
        self.build_ui()

    def build_ui(self):
        """ Build the UI design for the application """
        # Define components
        # Labels
        lbl_from = QLabel('From: ')
        lbl_to = QLabel('To: ')
        lbl_options = QLabel('Options: ')

        # Line edits for the paths
        self.le_from = QLineEdit()
        self.le_to = QLineEdit()

        # Browse buttons
        self.btn_browse_from = QPushButton('Browse...', self)
        self.btn_browse_to = QPushButton('Browse...', self)

        # Buttons for move files and switch paths
        self.btn_move_files = QPushButton('Move files', self)
        self.btn_switch = QPushButton('Switch paths', self)

        # Checkbox options
        ckb_music_option = QCheckBox(self.ckb_music_text, self)
        ckb_doc_option = QCheckBox(self.ckb_doc_text, self)
        ckb_video_option = QCheckBox(self.ckb_video_text, self)
        ckb_pictures_option = QCheckBox(self.ckb_pictures_text, self)
        ckb_zip_option = QCheckBox(self.ckb_zip_text, self)

        # progres bar
        self.progress = QProgressBar(self)

        # Events
        # Browse buttons
        self.btn_browse_from.clicked.connect(self.file_open_le_from)
        self.btn_browse_to.clicked.connect(self.file_open_le_to)

        # Move files button
        self.btn_move_files.setMaximumSize(100, 40)
        self.btn_move_files.clicked.connect(self.move_files)

        # Switch paths button
        self.btn_switch.clicked.connect(self.switch_paths)

        # Checkboxes events
        ckb_music_option.stateChanged\
                        .connect(lambda: self.checkbox_state(ckb_music_option))
        ckb_doc_option.stateChanged\
                      .connect(lambda: self.checkbox_state(ckb_doc_option))
        ckb_video_option.stateChanged\
                        .connect(lambda: self.checkbox_state(ckb_video_option))
        ckb_pictures_option.stateChanged\
                           .connect(lambda: self.checkbox_state(ckb_pictures_option))
        ckb_zip_option.stateChanged\
                      .connect(lambda: self.checkbox_state(ckb_zip_option))

        # Layouts
        # Define layouts
        blayout_chkbx_options = QVBoxLayout()
        blayout_path_from = QHBoxLayout()
        blayout_path_to = QHBoxLayout()
        flayout_paths = QFormLayout()
        blayout_main = QVBoxLayout()
        blayout_move_switch_btn = QHBoxLayout()

        # Populate layouts
        # Paths layout
        blayout_path_from.addWidget(self.le_from)
        blayout_path_from.addWidget(self.btn_browse_from)

        blayout_path_to.addWidget(self.le_to)
        blayout_path_to.addWidget(self.btn_browse_to)

        # Checkbox options layout
        blayout_chkbx_options.addWidget(ckb_doc_option)
        blayout_chkbx_options.addWidget(ckb_music_option)
        blayout_chkbx_options.addWidget(ckb_pictures_option)
        blayout_chkbx_options.addWidget(ckb_video_option)
        blayout_chkbx_options.addWidget(ckb_zip_option)

        # Include paths and checkbox layouts to a form layout
        flayout_paths.addRow(lbl_from, blayout_path_from)
        flayout_paths.addRow(lbl_to, blayout_path_to)
        flayout_paths.addRow(lbl_options, blayout_chkbx_options)

        # Switch and move buttons layout
        blayout_move_switch_btn.addStretch()
        blayout_move_switch_btn.addWidget(self.btn_switch)
        blayout_move_switch_btn.addWidget(self.btn_move_files)
        blayout_move_switch_btn.addStretch()

        # Put all layouts together in a main layout
        blayout_main.addLayout(flayout_paths)
        blayout_main.addStretch()
        blayout_main.addLayout(blayout_move_switch_btn)
        blayout_main.addWidget(self.progress)

        # Add the main layout to the central widget
        central_widget = QWidget()
        central_widget.setLayout(blayout_main)
        self.setCentralWidget(central_widget)

        # Set the defaults for options and paths
        if not path.exists('.cachedpaths'):
            # Set initial checkbox states
            ckb_music_option.setChecked(True)
            ckb_doc_option.setChecked(True)
            ckb_video_option.setChecked(True)
            ckb_pictures_option.setChecked(True)
            ckb_zip_option.setChecked(False)
        else:
            # Set paths and checkbox states based on the file
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
        if checkbox.text() == self.ckb_music_text:
            if checkbox.isChecked():
                self.checked_options.append(MUSIC_EXTENSIONS)
            else:
                self.checked_options.remove(MUSIC_EXTENSIONS)

        if checkbox.text() == self.ckb_doc_text:
            if checkbox.isChecked():
                self.checked_options.append(DOCUMENTS_EXTENSIONS)
            else:
                self.checked_options.remove(DOCUMENTS_EXTENSIONS)

        if checkbox.text() == self.ckb_video_text:
            if checkbox.isChecked():
                self.checked_options.append(VIDEO_EXTENSIONS)
            else:
                self.checked_options.remove(VIDEO_EXTENSIONS)

        if checkbox.text() == self.ckb_pictures_text:
            if checkbox.isChecked():
                self.checked_options.append(PICTURES_EXTENSIONS)
            else:
                self.checked_options.remove(PICTURES_EXTENSIONS)

        if checkbox.text() == self.ckb_zip_text:
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
                    .showMessage(f'Done. {result} files were affected.')
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