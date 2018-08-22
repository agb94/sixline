from __future__ import print_function
import httplib2
import os
import sys
import ftplib
import magic
import apiclient

from ftplib import FTP
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload 

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

service = None
folder_ids = {'/': 'root'}
file_names = []
folder_ids_file = open('folder_ids', 'a')
file_names_file = open('file_names_file', 'a')
ftp = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_mime_type(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)

def get_drive_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('drive', 'v3', http=http)

def create_folder(name, folder_id='root'):
    global service
    file_metadata = { 'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [folder_id]
    }
    file = service.files().create(body=file_metadata,
                                    fields='id').execute()
    return file.get('id')

def upload(file_path, folder_id='root'):
    global service
    file_name = os.path.basename(file_path)
    file_metadata = { 'name': file_name, 'parents': [folder_id] }
    media = MediaFileUpload(file_path, mimetype=get_mime_type(file_path), chunksize=1048576, resumable=True)
    request = service.files().create(body=file_metadata, media_body=media, fields='id')
    while True:
        try:
            response = None
            progress = 0
            while response is None:
                status, response = request.next_chunk()
                if status:
                    if int(status.progress() * 100) > progress:
                        delta = int(status.progress() * 100) - progress
                        progress = int(status.progress() * 100)
                        print(str(progress)+'%')
            break
        except apiclient.errors.HttpError as e:
            if e.resp.status in [404]:
                print ('404 Error: ' + file_path)
                break
            elif e.resp.status in [500, 502, 503, 504]:
                continue
            else:
                print ('Error: ' + file_path)
                break
    return file_path

def connect_ftp():
    ftp = FTP()
    ftp.connect("sixline.kaist.ac.kr", 81)
    ftp.encoding='utf-8'
    ftp.login("sixline_ftp", "!2#4")
    return ftp

def recursively_generate_folders(path):
    global folder_ids
    global folder_ids_file
    global ftp

    ftp.cwd(path)
    filelist = ftp.nlst()
    for f in filelist:
        try:
            folder_path = path + f + '/'
            ftp.cwd(path)
            if folder_path not in folder_ids:
                folder_id = create_folder(f, folder_ids[path])
                print (folder_path, end='\t')
                print (folder_id)
                folder_ids_file.write(folder_path+'\t')
                folder_ids_file.write(folder_id+'\n')
                folder_ids[folder_path] = folder_id
            recursively_generate_folders(folder_path)
        except ftplib.error_perm:
            continue
    return 

def recursively_upload_files(path):
    global folder_ids
    global folder_ids_file
    global file_names_file
    global ftp

    ftp.cwd(path)
    filelist = ftp.nlst()
    for f in filelist:
        folder_path = path + f + '/'
        if folder_path not in folder_ids:
            file_path = path+f
            if file_path not in file_names:
                # f is file
                print ('Download ' + file_path)
                if not os.path.exists(os.path.join('tmp',f)):
                    ftp.retrbinary("RETR "+f, open(os.path.join('tmp',f),"wb").write)
                print (os.path.join('tmp',f) + ' downloaded')
                file_name = upload(os.path.join('tmp',f), folder_ids[path])
                print (file_path+' uploaded')
                file_names.append(file_name)
                file_names_file.write(file_path+'\n')
                os.remove(os.path.join('tmp',f))
        else:
            recursively_upload_files(folder_path)
    return

def read_folder_ids():
    global folder_ids
    f = open('folder_ids', 'r')
    for l in f.readlines():
        if len(l.strip()) > 0:
            name = l.split('\t')[0].strip()
            forder_id = l.split('\t')[1].strip()
            folder_ids[name] = forder_id
    f.close()
    return

def read_file_names():
    global file_names
    f = open('file_names_file', 'r')
    for l in f.readlines():
        if len(l.strip()) > 0:
            file_names.append(l.strip())
    f.close()
    return

def main():
    global service
    global ftp
    global folder_ids
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)    
    ftp = connect_ftp()
    read_folder_ids()
    read_file_names()
    recursively_generate_folders('/')
    #recursively_upload_files('/기타악보/')

if __name__ == '__main__':
    main()
    folder_ids_file.close()
    file_names_file.close()
