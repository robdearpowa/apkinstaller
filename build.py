
import shutil
import PyInstaller.__main__
        
def build():
    PyInstaller.__main__.run(['apkinstaller.spec'])

build()
    