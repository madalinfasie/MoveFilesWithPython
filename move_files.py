#! /usr/bin/python3

import os
import shutil

SOURCE_PATH = '/home/madalin/Downloads'
MUSIC_DESTINATION = '/home/madalin/Music'
PICTURES_DESTINATION = '/home/madalin/Pictures'
VIDEO_DESTINATION = '/home/madalin/Videos'
DOCUMENTS_DESTINATION = '/home/madalin/Documents'

MUSIC_EXTENSIONS = ('.mp3',)
VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mkv')
PICTURES_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.gif')
DOCUMENTS_EXTENSIONS = ('.pdf', '.doc', '.docx', '.odt', '.txt')
ZIP_EXTENSIONS = ('.zip', '.tar.gz')

def move_all_files():
    dup_music = 1; dup_video = 1; dup_documents = 1; dup_pictures = 1
    for root, dirs, files in os.walk(SOURCE_PATH):
        for file_name in files:
            # move music files
            if file_name.endswith(MUSIC_EXTENSIONS) and root == SOURCE_PATH:
                file_path = SOURCE_PATH + '/' + file_name
                while os.path.exists(MUSIC_DESTINATION+'/'+file_name):
                    file_name = file_name[:file_name.rfind('.')] + '_' + str(dup_music) + file_name[file_name.rfind('.'):]
                    dup_music = dup_music + 1

                shutil.move(file_path, MUSIC_DESTINATION+'/'+file_name)
                print('File {} was moved from {} to {}'.format(file_name, root,MUSIC_DESTINATION))

            # move pictures files
            if file_name.endswith(PICTURES_EXTENSIONS) and root == SOURCE_PATH:
                file_path = SOURCE_PATH + '/' + file_name
                while os.path.exists(PICTURES_DESTINATION+'/'+file_name):
                    file_name = file_name[:file_name.rfind('.')] + '_' + str(dup_pictures) + file_name[file_name.rfind('.'):]
                    dup_pictures = dup_pictures + 1

                shutil.move(file_path, PICTURES_DESTINATION+'/'+file_name)
                print('File {} was moved from {} to {}'.format(file_name, root,PICTURES_DESTINATION))

            # move video files
            if file_name.endswith(VIDEO_EXTENSIONS) and root == SOURCE_PATH:
                file_path = SOURCE_PATH + '/' + file_name
                while os.path.exists(VIDEO_DESTINATION+'/'+file_name):
                    file_name = file_name[:file_name.rfind('.')] + '_' + str(dup_video) + file_name[file_name.rfind('.'):]
                    dup_video = dup_video + 1

                shutil.move(file_path, VIDEO_DESTINATION+'/'+file_name)
                print('File {} was moved from {} to {}'.format(file_name, root,VIDEO_DESTINATION))

            # move document files
            if file_name.endswith(DOCUMENTS_EXTENSIONS) and root == SOURCE_PATH:
                file_path = SOURCE_PATH + '/' + file_name
                while os.path.exists(DOCUMENTS_DESTINATION+'/'+file_name):
                    file_name = file_name[:file_name.rfind('.')] + '_' + str(dup_documents) + file_name[file_name.rfind('.'):]
                    dup_documents = dup_documents + 1
                    
                shutil.move(file_path, DOCUMENTS_DESTINATION+'/'+file_name)
                print('File {} was moved from {} to {}'.format(file_name, root,DOCUMENTS_DESTINATION))


def delete_extracted_zip():
    for root, dirs, files in os.walk(SOURCE_PATH):
        for file_name in files:
            # delete extracted zip files files
            if file_name.endswith(ZIP_EXTENSIONS):
                for mydir in dirs:
                    if mydir == file_name[:file_name.rfind('.zip')] or mydir == file_name[:file_name.rfind('.tar.gz')]:
                            file_path = root + '/' + file_name
                            os.remove(file_path)
                            print('File {} was removed'.format(file_name))

if __name__ == '__main__':
    move_all_files()
    delete_extracted_zip()








                
