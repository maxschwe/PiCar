import tkinter as tk
from tkinter.constants import *
from tkinter.ttk import *
import numpy as np
import cv2
from PIL import ImageTk, Image
from threading import Thread
import socket

import json
import traceback
import time
import ctypes
from functools import partial
import keyboard

from .slider import Slider
from .buttons import ActionButton, ConfigButton
from .add_btn import add_btn
from tcp import ACTIONS

FONT_INFO_LBL = ("Helvetica", 20)
SPEED = 40
PARAM_DELIMETER = ";"


class Window(tk.Tk):
    def __init__(self, client, width=1000, height=600, fps=30):
        super().__init__()
        self.tk.call("source", "gui/Sun-Valley-ttk-theme/sun-valley.tcl")
        self.tk.call("set_theme", "dark")

        self.fps = fps
        x = int(self.winfo_screenwidth()/2 - width/2)
        y = max(0, int(self.winfo_screenheight()/2 - height/2 - 40))
        # y = 0
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.title("PiCar Controller")

        self.client = client
        self.client.bind_log(self.log)
        self.connected = False
        self.new_outputs = []

        self.old_speed = 0
        self.old_steering = 0
        self.i = 0

        self.widgets()
        self.load_data()
        self.update_action_btn()
        self.update_config_btn()
        self.bind_keys()
        self.update()

    def widgets(self):
        self.fr_btn = Frame(self)
        self.fr_btn.place(relwidth=0.25, relheight=1)
        self.fr_info = Frame(self)
        self.fr_info.place(relx=0.25, relwidth=0.5,
                           relheight=1)
        self.fr_terminal = Frame(self)
        self.fr_terminal.place(relx=0.75, relwidth=0.25,
                               relheight=1)

        self.fr_driving = Frame(self.fr_btn)
        self.fr_driving.pack(fill=X, expand=True)
        self.fr_driving.columnconfigure(0, weight=1, uniform='fred')
        self.fr_driving.columnconfigure(1, weight=1, uniform='fred')
        self.slider_speed = Slider(
            self.fr_driving, "Speed: ", exec=self.execute, action=ACTIONS.SPEED, from_=-100, to=100, orient=VERTICAL)
        self.slider_speed.grid(row=0, column=0, padx=10, pady=10)
        self.slider_steering = Slider(self.fr_driving, "Steering: ", exec=self.execute,
                                      action=ACTIONS.STEERING, from_=-100, to=100, orient=HORIZONTAL)
        self.slider_steering.grid(row=0, column=1, padx=10, pady=10)

        self.fr_action_btn = LabelFrame(self.fr_btn, text="Action Buttons")
        self.fr_action_btn.pack(fill=X, padx=30, pady=30, ipady=3)
        self.fr_action_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_action_btn.columnconfigure(1, weight=1, uniform='fred')

        self.fr_config_btn = LabelFrame(
            self.fr_btn, text="Config Buttons")
        self.fr_config_btn.pack(fill=X, padx=30, pady=30, ipady=3)
        self.fr_config_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_config_btn.columnconfigure(1, weight=1, uniform='fred')

        self.fr_connection_btn = LabelFrame(
            self.fr_btn, text="Connection")
        self.fr_connection_btn.pack(fill=X, padx=30, pady=30, ipady=3)
        self.fr_connection_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_connection_btn.columnconfigure(1, weight=1, uniform='fred')

        self.btn_connect = Button(
            self.fr_connection_btn, text="Connect", command=self.connect, style="Accent.TButton")
        self.btn_connect.grid(row=0, column=0, sticky=EW, padx=5, pady=3)

        self.btn_ping = Button(
            self.fr_connection_btn, text="Ping", command=self.ping)
        self.btn_ping.grid(row=0, column=1, sticky=EW, padx=5, pady=3)

        self.btn_sync = Button(
            self.fr_connection_btn, text="Sync", command=self.sync)
        self.btn_sync.grid(row=1, column=0, sticky=EW, padx=5, pady=3)

        self.btn_sync_restart = Button(
            self.fr_connection_btn, text="Sync + Restart", command=self.sync_restart, style="Accent.TButton")
        self.btn_sync_restart.grid(row=1, column=1, sticky=EW, padx=5, pady=3)

        self.livestream = Label(self.fr_info)
        self.livestream.pack()
        self.lbl_fps = Label(self.fr_info, text="",
                             font=FONT_INFO_LBL, padding=(10, 10))

        self.action_add_btn = Button(
            self.fr_action_btn, text="+", style="Accent.TButton", command=self.action_add_clicked)
        self.action_btns = [self.action_add_btn]
        self.config_add_btn = Button(
            self.fr_config_btn, text="+", style="Accent.TButton", command=self.config_add_clicked)
        self.config_btns = [self.config_add_btn]

        self.fr_terminal_output = Frame(self.fr_terminal)
        self.fr_terminal_output.pack(
            side=TOP, expand=YES, fill=BOTH, padx=10, pady=10)
        self.terminal_output = tk.Text(
            self.fr_terminal_output)

        ys = Scrollbar(self.fr_terminal_output, orient='vertical',
                       command=self.terminal_output.yview)
        xs = Scrollbar(self.fr_terminal_output, orient='horizontal',
                       command=self.terminal_output.xview)
        self.terminal_output['yscrollcommand'] = ys.set
        self.terminal_output['xscrollcommand'] = xs.set

        self.terminal_output.grid(
            column=0, row=0, sticky='nwes')
        xs.grid(column=0, row=1, sticky='we')
        ys.grid(column=1, row=0, sticky='ns')
        self.fr_terminal_output.grid_columnconfigure(0, weight=1)
        self.fr_terminal_output.grid_rowconfigure(0, weight=1)

        self.fr_exec = Frame(self.fr_terminal)
        self.fr_exec.pack(padx=30, pady=30)
        self.fr_exec.columnconfigure(0, weight=1, uniform='fred')
        self.fr_exec.columnconfigure(1, weight=1, uniform='fred')

        self.cb_action = Combobox(
            self.fr_exec, values=ACTIONS.list(), state="readonly")
        self.cb_action.grid(row=0, column=0, padx=10, pady=10)
        self.cb_action.current(0)

        self.txt_params = Entry(self.fr_exec)
        self.txt_params.grid(row=0, column=1, padx=10, pady=10)

        self.btn_exec = Button(
            self.fr_exec, text="???", style="Accent.TButton", command=self.btn_exec_clicked)
        self.btn_exec.grid(row=0, column=2, padx=10, pady=10)

    def connect(self):
        self.client.try_connect().start()

    def ping(self):
        self.client.ping()

    def btn_exec_clicked(self):
        action = ACTIONS.decode(self.cb_action.current())
        params = self.txt_params.get()

        params = self._format_params(params)

        self.execute(action, params)

    def _format_params(self, params):
        params = params.split(PARAM_DELIMETER)
        if params != [""]:
            for i in range(len(params)):
                param = params[i]
                param = param.lstrip().rstrip()
                if len(param) > 0 and param[0] in ["'", '"']:
                    param = param[1:]
                    if param.endswith("'") or param.endswith('"'):
                        param = param[:-1]

                elif len(param) > 0 and param[0] in ["{"]:
                    try:
                        param = json.loads(param)
                    except:
                        traceback.print_exc()
                        self.log("!!!Json data wrong specified!!!")
                else:
                    param = param.replace(" ", "")
                    try:
                        param = int(param)
                    except ValueError:
                        try:
                            param = float(param)
                        except ValueError:
                            param = param == "True"
                params[i] = param
        else:
            params = ""
        return params

    def bind_keys(self):
        self.bind("<Escape>", self.close)

    def on_connect(self):
        synced_count = self.client.sync_dir(all=False)
        if synced_count > 0:
            self.client.exec_restart()
            return
        self.client.ping()
        self.client.load_status()
        self.slider_speed.reset()
        self.slider_steering.reset()

        for config_btn in self.config_btns[:-1]:
            config_btn.exec()

    def execute(self, action, params="", log=True, ack=True):
        if self.client.connected:
            try:
                resp = self.client.exec(
                    action=action, params=params, ack=ack, log=log)
                # received bool for ack
                if type(resp) != tuple:
                    return resp
                action, params = resp
                if action != ACTIONS.ERROR:
                    return action, params
            except socket.timeout:
                self.log("Client is not connected!")

    def sync(self):
        self.client.sync_dir(all=True)

    def sync_restart(self):
        self.sync()
        self.client.exec_restart()

    def load_data(self):
        try:
            with open("data/gui.json") as f:
                data = json.load(f)
            action_btns_data = data["action_btns"]
            config_btns_data = data["config_btns"]
        except:
            traceback.print_exc()
            action_btns_data = {}
            config_btns_data = {}
        for params in action_btns_data:
            self.add_action_btn(params)

        for params in config_btns_data:
            self.add_config_btn(params)

    def add_action_btn(self, params):
        action = ACTIONS.decode(params["action"])
        index = len(self.action_btns) - 1
        btn = ActionButton(self.fr_action_btn, name=params["name"],
                           exec=self.execute, action=action, params=params["params"], edit=self.edit_action_btn)
        self.action_btns.insert(index, btn)

    def add_config_btn(self, params):
        action = ACTIONS.decode(params["action"])
        index = len(self.config_btns)-1
        btn = ConfigButton(self.fr_config_btn, name=params["name"], active=params["active"],
                           exec=self.execute, action=action, edit=self.edit_config_btn)
        btn.exec()
        self.config_btns.insert(index, btn)

    def save_data(self):
        data = {"action_btns": [btn.get_data(decoded=True) for btn in self.action_btns[:-1]],
                "config_btns": [btn.get_data(decoded=True) for btn in self.config_btns[:-1]]}
        with open("data/gui.json", "w") as f:
            json.dump(data, f, indent=4)

    def update_action_btn(self):
        self.update_btns(self.action_btns)

    def update_config_btn(self):
        self.update_btns(self.config_btns)

    def update_btns(self, list):
        for index, btn in enumerate(list):
            btn.index = index
            btn.grid(row=index // 2, column=index %
                     2, sticky=EW, padx=5, pady=3)

    def update_livestream(self):
        width = self.fr_info.winfo_width()
        resp = self.execute(ACTIONS.LIVESTREAM, log=False)
        if resp is None:
            return
        _, msg = resp
        jpeg = np.frombuffer(msg, dtype=np.uint8)
        frame = cv2.imdecode(jpeg, cv2.IMREAD_COLOR)
        img = Image.fromarray(frame)
        factor = width / img.width
        resized_img = img.resize(
            (int(width), int(img.height * factor)), Image.ANTIALIAS)

        imgtk = ImageTk.PhotoImage(image=resized_img)
        self.livestream.imgtk = imgtk
        self.livestream.configure(image=imgtk)

    def update_move(self):
        new_speed = 0
        new_steering = 0
        if keyboard.is_pressed("Up"):
            new_speed = SPEED
        elif keyboard.is_pressed("Down"):
            new_speed = -1 * SPEED
        if keyboard.is_pressed("Right"):
            new_steering = 100
        elif keyboard.is_pressed("Left"):
            new_steering = -100
        if new_speed != self.old_speed:
            self.execute(ACTIONS.SPEED, params=new_speed)
        if new_steering != self.old_steering:
            self.execute(ACTIONS.STEERING, params=new_steering)
        self.old_speed = new_speed
        self.old_steering = new_steering

    def action_add_clicked(self):
        data = add_btn(self, action_btn=True, new=True)
        data["params"] = self._format_params(data["params"])
        self.add_action_btn(data)
        self.update_action_btn()
        self.save_data()

    def edit_action_btn(self, index):
        rel_btn = self.action_btns[index]
        prev_data = rel_btn.get_data()
        prev_data["params"] = ";".join(
            map(lambda x: f'"{x}"' if type(x) == str else str(x).replace("'", '"'), prev_data["params"]))
        data = add_btn(self, action_btn=True, new=False, **prev_data)
        if data is None:
            return
        elif data == "remove":
            removed_btn = self.action_btns.pop(index)
            removed_btn.grid_remove()
        else:
            data["params"] = self._format_params(data["params"])
            rel_btn.edit_data(**data)
        self.update_action_btn()
        self.save_data()

    def config_add_clicked(self):
        data = add_btn(self, action_btn=False, new=True)
        self.add_config_btn(data)
        self.update_config_btn()
        self.save_data()

    def edit_config_btn(self, index):
        rel_btn = self.config_btns[index]
        prev_data = rel_btn.get_data()
        data = add_btn(self, action_btn=False, new=False, **prev_data)
        if data is None:
            return
        elif data == "remove":
            if rel_btn.active:
                rel_btn.active = False
                rel_btn.exec()
            removed_btn = self.config_btns.pop(index)
            removed_btn.grid_remove()
        else:
            self.config_btns[index].edit_data(**data)
        self.update_config_btn()
        self.save_data()

    def close(self, *_):
        self.active = False
        self.destroy()

    def update_data(self):
        self.update_livestream()
        self.i += 1
        if self.i % 3 == 0:
            self.update_move()

        if self.i == 20:
            self.lbl_fps["text"] = str(self.fps) + " fps"
            self.lbl_fps.place(relx=0, rely=0)
            self.i = 0

    def mainloop(self):
        self.active = True
        time_between = 1 / self.fps

        try:
            while self.active:
                start = time.time()
                if not self.connected and self.client.connected:
                    self.connected = True
                    self.on_connect()
                if self.connected:
                    self.connected = self.client.connected
                    self.update_data()
                outputs = self.new_outputs.copy()
                for new_output in outputs:
                    self.terminal_output.config(state=NORMAL)
                    self.terminal_output.insert(END, new_output + "\n")
                    self.terminal_output.see("end")
                    self.terminal_output.config(state=DISABLED)
                    self.new_outputs.remove(new_output)

                self.update()
                self.fps = int(1 / max(0.00001, time.time() - start))
                # time.sleep(max(0, (time_between - (time.time() - start))))
        except tk.TclError:
            pass

    def log(self, msg, type="txt"):
        self.new_outputs += msg.split('\n')
