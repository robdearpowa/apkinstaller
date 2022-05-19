from time import sleep
import PySimpleGUI as sg
import os
import subprocess
from configparser import ConfigParser
from threading import Thread

sg.LOOK_AND_FEEL_TABLE["Marketwall"] = {
    "BACKGROUND": "#424242",
    "TEXT": "#FFFFFF",
    "INPUT": "#656565",
    "TEXT_INPUT": "#656565",
    "SCROLL": "#212121",
    "BUTTON": ("#FFFFFF", "#4595F7"),
    "PROGRESS": ("#656565", "#4595F7"),
    "BORDER": 1, "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0,
}
  
sg.theme('Marketwall')

class DeviceModel:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        pass

    def __str__(self) -> str:
        return self.name

class App:

    def __init__(self) -> None:
        layout = [
            [sg.Text("Apk path")],
            [sg.Input(key="-APKPATH-", readonly=True, disabled_readonly_text_color=sg.theme_input_text_color(), disabled_readonly_background_color=sg.theme_input_background_color()), sg.FileBrowse(key="-FBAPK-", file_types=[("APK", "*.apk")])],
            [sg.Text("Adb path")],
            [sg.Input(key="-ADBPATH-", readonly=True, disabled_readonly_text_color=sg.theme_input_text_color(), disabled_readonly_background_color=sg.theme_input_background_color()), sg.FileBrowse(key="-FBADB-", file_types=[("ADB", "*.exe")])],
            [sg.Text("Device")],
            [sg.Combo(key="-DEVICES-", values=[], size=(30, None), readonly=True), sg.Button(key="-REFRESH-", button_text="Refresh")],
            [sg.Button(key="-INSTALL-", button_text="Install"), sg.Text(key="-STATE-")],
            [sg.Multiline(key="-CONSOLE-", size=(None, 10), disabled=True, autoscroll=True, horizontal_scroll=True, visible=False)]
        ]

        self.window = sg.Window("Apk Installer", layout=layout, finalize=True)

        self.apk_input = self.window["-APKPATH-"]
        self.adb_input = self.window["-ADBPATH-"]
        self.txt_state = self.window["-STATE-"]
        self.console = self.window["-CONSOLE-"]
        self.device_selector = self.window["-DEVICES-"]
        self.device_list = []

        self.carica_configurazione()
        self.check_devices()

        pass
    
    def get_adb_path(self) -> str:
        return self.adb_input.get().rstrip()
    
    def check_adb_path(self) -> bool:
        return self.get_adb_path() and self.get_adb_path() != "" and os.path.exists(self.get_adb_path())

    def get_apk_path(self) -> str:
        return self.apk_input.get().rstrip()

    def check_apk_path(self) -> bool:
        return self.get_apk_path() and self.get_apk_path != "" and os.path.exists(self.get_adb_path())

    def get_selected_device(self) -> DeviceModel:
        return self.device_selector.get()

    def check_selected_device(self) -> bool:
        return self.get_selected_device() and self.get_selected_device().id and self.get_selected_device().id != ""

    def start(self) -> None:
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED or event == "Cancel":
                self.salva_configurazione()
                break

            if event == "-INSTALL-":
                self.installa_apk()

            if event == "-FBADB-" or event == "-REFRESH-":
                self.check_devices()


        self.window.close()
        pass

    #def set_path

    def installa_apk(self) -> None:
        if not self.check_adb_path() and not self.check_selected_device() and not self.check_apk_path(): return

        try:
            self.txt_state.update(value="Installing...")

            thread = Thread(target=self.installa_async)

            thread.start()

        finally:
            pass

    def installa_async(self) -> None:
        
        cmd = f'{self.get_adb_path()} -s {self.get_selected_device().id} install -t "{self.get_apk_path()}"'
        print(cmd)

        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        output = ""
        for line in p.stdout:
            line = line.decode().rstrip()
            print(line)
            output += f"{line}\n"
            self.console.update(value=output, visible=True)
            self.window.refresh()

        p.wait()

        print(p.returncode)

        if p.returncode == 0:
            self.txt_state.update(value="Done!")
        else:
            self.txt_state.update(value="Error :(")

    def salva_configurazione(self):
        config = ConfigParser()
        config.read("config.ini")
        
        config["config"] = {
            "apk_path": self.get_apk_path(),
            "adb_path": self.get_adb_path()
        }

        with open("config.ini", "w") as f:
            config.write(f)

    def carica_configurazione(self) -> None:
        if os.path.exists("config.ini"):
            config = ConfigParser()
            config.read("config.ini")

            apk_path = ""
            adb_path = ""

            if "config" in config:

                if "apk_path" in config["config"]:
                    apk_path = config["config"]["apk_path"]

                if "adb_path" in config["config"]:
                    adb_path = config["config"]["adb_path"]

            self.apk_input.update(value=apk_path)
            self.adb_input.update(value=adb_path)
        pass

    def check_devices(self) -> None:

        self.device_list.clear()

        if not self.check_adb_path(): return

        cmd = f'{self.adb_input.get()} devices -l'
        print(cmd)

        p = subprocess.Popen(args=cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        for line in p.stdout:
            line = line.decode().rstrip()
            print(line)
            if "model:" in line:

                sections = line.split(" ")

                id = sections[0].rstrip()
                name = id

                for record in sections:
                    if "model:" in record:
                        model = record.removeprefix("model:").rstrip()
                        name = model if model and model != "" else id

                self.device_list.append(DeviceModel(id=id, name=name))

        p.wait()

        self.device_selector.update(values=self.device_list, set_to_index=0)
        pass


app = App()

app.start()