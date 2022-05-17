from time import sleep
from weakref import finalize
import PySimpleGUI as sg
import os
import subprocess
from configparser import ConfigParser

sg.theme("Default")


class App:

    def __init__(self) -> None:
        layout = [
            [sg.Text("Apk path")],
            [sg.Input(key="-APKPATH-", readonly=True), sg.FileBrowse(key="-FBAPK-", file_types=[("APK", "*.apk")])],
            [sg.Text("Adb path")],
            [sg.Input(key="-ADBPATH-", readonly=True), sg.FileBrowse(key="-FBADB-", file_types=[("ADB", "*.exe")])],
            [sg.Button(key="-INSTALL-", button_text="Install"), sg.Text(key="-STATE-")],
        ]

        self.window = sg.Window("Apk Installer", layout=layout, finalize=True)

        self.apk_input = self.window["-APKPATH-"]
        self.adb_input = self.window["-ADBPATH-"]
        self.txt_state = self.window["-STATE-"]

        self.carica_configurazione()

        pass

    def start(self) -> None:
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                self.salva_configurazione()
                break

            if event == "-INSTALL-":
                self.installa_apk()


        self.window.close()
        pass

    #def set_path

    def installa_apk(self):

        if (self.adb_input.get().rstrip() != "" and self.apk_input.get().rstrip() != ""):
            try:
                self.txt_state.update(value="Installing...")

                code = subprocess.call(args=f'{self.adb_input.get()} install -t "{self.apk_input.get()}"', shell=True)
                print(code)

                if (code == 0):
                    self.txt_state.update(value="Done!")
                else:
                    self.txt_state.update(value="Error :(")
            finally:
                pass

    def salva_configurazione(self):
        config = ConfigParser()
        config.read("config.ini")
        if not config.has_section("config"):
            config.add_section("config")
        config.set("config", "apk_path", self.apk_input.get())
        config.set("config", "adb_path", self.adb_input.get())

        with open("config.ini", "w") as f:
            config.write(f)

    def carica_configurazione(self):


        if os.path.exists("config.ini"):
            config = ConfigParser()
            config.read("config.ini")

            apk_path = ""
            adb_path = ""

            if config.has_section("config"):

                if config.has_option("config", "apk_path"):
                    apk_path = config.get("config", "apk_path")

                if config.has_option("config", "adb_path"):
                    adb_path = config.get("config", "adb_path")

            self.apk_input.update(value=apk_path)
            self.adb_input.update(value=adb_path)
        pass


app = App()

app.start()