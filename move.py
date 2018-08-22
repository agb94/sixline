import sys
import ftplib
import os
from ftplib import FTP

forderidmaps = {}

forder_id = 0

ftp = FTP()
ftp.connect("sixline.kaist.ac.kr", 81)
ftp.encoding='utf-8'
ftp.login("sixline_ftp", "!2#4")

def downloadFiles(path,destination):
#path & destination are str of the form "/dir/folder/something/"
#path should be the abs path to the root FOLDER of the file tree to download
    global forder_id
    try:
        ftp.cwd(path)
        if path not in forderidmaps:
            forderidmaps[path] = forder_id
            forder_id += 1
        #clone path to destination
        #os.chdir(destination)
        #os.mkdir(destination[0:len(destination)-1]+path)
        #print(destination[0:len(destination)-1]+path+" built")
    except OSError:
        #folder already exists at destination
        pass
    except ftplib.error_perm:
        #invalid entry (ensure input form: "/dir/folder/something/")
        print("error: could not change to "+path)
        sys.exit("ending session")

    #list children:
    filelist=ftp.nlst()
    for file in filelist:
        try:
            #this will check if file is folder:
            ftp.cwd(path+file+"/")
            #if so, explore it:
            print (forderidmaps[path], end=' ')
            forderidmaps[path+file+'/'] = forder_id
            forder_id +=1
            print (path+file+"/ [" + str(forderidmaps[path+file+'/']) + ']')
            if "_임시 Upload" not in file:
                downloadFiles(path+file+"/",destination)
        except ftplib.error_perm:
            a = 1
            #not a folder with accessible content
            #download & return
            #os.chdir(destination[0:len(destination)-1]+path)
            #possibly need a permission exception catch:
            #ftp.retrbinary("RETR "+file, open(os.path.join(destination,file),"wb").write)
            #print(file + " downloaded")
    return

source="/"
dest="/Users/Gabin/Workspace/sixline/"
downloadFiles(source,dest)
