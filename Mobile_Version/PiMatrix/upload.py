from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from matrix_lite import led
import socket
import time
import datetime

def upload_file(pimatrix):
        # Find the specific file ID you want
        fileList = pimatrix.drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        for file in fileList:
            print('Title: %s, ID: %s' % (file['title'], file['id']))
            # Get the folder ID that you want
            if(file['title'] == "FYP_PiMatrix_Recordings"):
                rootfolderID = file['id']
                #create a folder inside this root folder
                folder_name = ("recordings_"+socket.gethostname()+"_"+str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')))
                folder_metadata = {
                    'title': folder_name,
                    'parents':[{'id':rootfolderID}],
                    'mimeType' : 'application/vnd.google-apps.folder'
                }
                folder = pimatrix.drive.CreateFile(folder_metadata)
                folder.Upload()
                #Get ID of the specific folder
                folder_id = folder['id']
                print("folder id is " + str(folder_id)) #debug

        led.set(pimatrix.purple)
        for filename in pimatrix.session_file_list:
            file_title = filename[28:]
            audiofile = pimatrix.drive.CreateFile(
                {'parents': [{'id': folder_id}], 'title': file_title})
            audiofile.SetContentFile(filename)
            try:
                audiofile.Upload()
            except:
                print("error uploading file")
                led.set(pimatrix.red)

        print("Uploading completed!")
        led.set(pimatrix.blue)