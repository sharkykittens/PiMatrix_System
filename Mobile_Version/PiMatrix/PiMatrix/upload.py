from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from matrix_lite import led

def upload_file(pimatrix):
        # Find the specific file ID you want
        fileList = pimatrix.drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        for file in fileList:
            print('Title: %s, ID: %s' % (file['title'], file['id']))
            # Get the folder ID that you want
            if(file['title'] == "FYP_PiMatrix_Recordings"):
                fileID = file['id']
        led.set(pimatrix.purple)
        for filename in pimatrix.session_file_list:
            file_title = filename[28:]
            audiofile = pimatrix.drive.CreateFile(
                {'parents': [{'id': fileID}], 'title': file_title})
            audiofile.SetContentFile(filename)
            try:
                audiofile.Upload()
            except:
                print("error uploading file")
                led.set(pimatrix.red)

        print("Uploading completed!")
        led.set(pimatrix.blue)