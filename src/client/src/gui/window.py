import tkinter as tk
from tkinter.constants import *
from tkinter.ttk import *
import numpy as np
import cv2
from PIL import ImageTk, Image
from threading import Thread

import json
import traceback
import time

from .slider import Slider
from .buttons import ActionButton, ConfigButton
from .add_btn import add_btn
from .. import ACTION, RETURN
from ..client.sync import sync_dir


class Window(tk.Tk):
    def __init__(self, client, width=1000, height=600):
        super().__init__()
        x = int(self.winfo_screenwidth()/2 - width/2)
        y = max(0, int(self.winfo_screenheight()/2 - height/2 - 40))
        y = 0
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.title("PiCar Controller")

        self.tk.call("source", "src/gui/Sun-Valley-ttk-theme/sun-valley.tcl")
        self.tk.call("set_theme", "dark")

        self.client = client
        self.active = True

        self.load_data()
        self.widgets()
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
        self.slider_speed = Slider(
            self.fr_driving, "Speed: ", exec=self.execute, action=ACTION.SPEED, from_=-100, to=100, orient=VERTICAL)
        self.slider_speed.pack(side=LEFT, expand=True, padx=5, pady=5)
        self.slider_steering = Slider(self.fr_driving, "Steering: ", exec=self.execute,
                                      action=ACTION.STEERING, from_=-100, to=100, orient=HORIZONTAL)
        self.slider_steering.pack(side=LEFT, expand=True, padx=5, pady=5)

        self.fr_action_btn = LabelFrame(self.fr_btn, text="Action Buttons")
        self.fr_action_btn.pack(fill=X, padx=10, pady=10, ipady=3)
        self.fr_action_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_action_btn.columnconfigure(1, weight=1, uniform='fred')

        self.fr_config_btn = LabelFrame(
            self.fr_btn, text="Config Buttons")
        self.fr_config_btn.pack(fill=X, padx=10, pady=10, ipady=3)
        self.fr_config_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_config_btn.columnconfigure(1, weight=1, uniform='fred')

        self.fr_sync_btn = LabelFrame(
            self.fr_btn, text="Sync")
        self.fr_sync_btn.pack(fill=X, padx=10, pady=10, ipady=3)
        self.fr_sync_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_sync_btn.columnconfigure(1, weight=1, uniform='fred')

        self.btn_sync = Button(
            self.fr_sync_btn, text="Sync", command=self.sync)
        self.btn_sync.grid(row=0, column=0, sticky=EW, padx=5, pady=3)

        self.btn_sync_restart = Button(
            self.fr_sync_btn, text="Sync and Restart", command=self.sync_restart, style="Accent.TButton")
        self.btn_sync_restart.grid(row=0, column=1, sticky=EW, padx=5, pady=3)

        self.livestream = Label(self.fr_info)
        self.livestream.pack()

        self.update_action_btn()
        self.update_config_btn()

    def bind_keys(self):
        self.bind("<Escape>", self.close)

    def execute(self, action, msg="", ret=RETURN.ACK):
        if self.client is not None:
            msg = self.client.exec(action=action, msg=msg, ret_type=ret)

    def sync(self):
        sync_dir(self.client, all=True)

    def sync_restart(self):
        self.sync()
        self.client.exec_restart()

    def load_data(self):
        try:
            with open("data/gui.json") as f:
                data = json.load(f)
            self.action_btns = data["action_btns"]
            self.config_btns = data["config_btns"]
        except:
            traceback.print_exc()
            self.action_btns = {}
            self.config_btns = {}

    def save_data(self):
        data = {"action_btns": self.action_btns,
                "config_btns": self.config_btns}
        print(data)
        with open("data/gui.json", "w") as f:
            json.dump(data, f, indent=4)

    def update_action_btn(self):
        index = 0
        for btn_text, params in self.action_btns.items():
            btn = ActionButton(self.fr_action_btn, text=btn_text,
                               exec=self.execute, action=params["action"], msg=params["msg"], ret=params["ret"])
            btn.grid(row=index // 2, column=index %
                     2, sticky=EW, padx=5, pady=3)
            index += 1
        self.action_add = Button(
            self.fr_action_btn, text="+", style="Accent.TButton", command=self.action_add_clicked)
        self.action_add.grid(row=index // 2,
                             column=index % 2, padx=3, pady=3)

    def update_config_btn(self):
        index = 0
        for btn_text, params in self.config_btns.items():
            btn = ConfigButton(self.fr_config_btn, text=btn_text, active=params["active"],
                               exec=self.execute, action=params["action"], ret=params["ret"])
            btn.grid(row=index // 2, column=index %
                     2, sticky=EW, padx=5, pady=3)
            index += 1
        self.config_add = Button(
            self.fr_config_btn, text="+", style="Accent.TButton", command=self.config_add_clicked)
        self.config_add.grid(row=index // 2, column=index % 2, padx=3, pady=3)

    def update_livestream(self):
        if self.client is not None:
            width = self.fr_info.winfo_width()
            msg = self.client.exec(
                ACTION.LIVESTREAM, ret_type=RETURN.JPG, decode=False, log=False)
            jpeg = np.frombuffer(msg, dtype=np.uint8)
            frame = cv2.imdecode(jpeg, cv2.IMREAD_COLOR)
            img = Image.fromarray(frame)
            factor = width / img.width
            resized_img = img.resize(
                (int(width), int(img.height * factor)), Image.ANTIALIAS)

            imgtk = ImageTk.PhotoImage(image=resized_img)
            self.livestream.imgtk = imgtk
            self.livestream.configure(image=imgtk)

    def action_add_clicked(self):
        name, data = add_btn(self, action_btn=True, new=True)
        self.action_btns[name] = data
        self.update_action_btn()
        self.save_data()

    def config_add_clicked(self):
        name, data = add_btn(self, action_btn=False, new=True)
        print(name, data)
        self.config_btns[name] = data
        print(self.config_btns)
        self.update_config_btn()
        print("oki")
        self.save_data()

    def close(self, *_):
        self.active = False
        self.destroy()
