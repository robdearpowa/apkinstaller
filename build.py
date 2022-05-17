
import shutil
import PyInstaller.__main__
        
def build():
    PyInstaller.__main__.run(["--onefile", "apkinstaller.py"])

build()
    