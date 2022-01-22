import tkinter as tk
from tkinter.constants import *
from tkinter.ttk import *

from .slider import Slider
from .buttons import ActionButton, ConfigButton
from .. import ACTION

ACTION_BTN = {"1m straight": ACTION.STRAIGHT,
              "turn 90": ACTION.TURN, "1m backwards": ACTION.BACKWARD, "2m straight": ACTION.STRAIGHT,
              "turn 180": ACTION.TURN, "2m backwards": ACTION.BACKWARD}

CONFIG_BTN = {"1m straight": [ACTION.STRAIGHT, True],
              "turn 90": [ACTION.TURN, True], "1m backwards": [ACTION.BACKWARD, False]}

COL1 = "#171717"
COL2 = "#444444"
COL3 = "#DA0037"
COL4 = "#EDEDED"


class Window(tk.Tk):
    def __init__(self, width=1200, height=700):
        super().__init__()
        x = int(self.winfo_screenwidth()/2 - width/2)
        y = max(0, int(self.winfo_screenheight()/2 - height/2 - 40))
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.title("PiCar Controller")

        self.tk.call("source", "src/gui/Sun-Valley-ttk-theme/sun-valley.tcl")
        self.tk.call("set_theme", "dark")
        self.widgets()

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
        self.fr_action_btn.pack(fill=X, padx=10, pady=20)
        self.fr_action_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_action_btn.columnconfigure(1, weight=1, uniform='fred')

        row = col = 0
        for btn_text, action in ACTION_BTN.items():
            btn = ActionButton(self.fr_action_btn, text=btn_text,
                               exec=self.execute, action=action)
            btn.grid(row=row, column=col, sticky=EW, padx=3, pady=3)
            col += 1
            if col > 1:
                col = 0
                row += 1

        self.fr_config_btn = LabelFrame(
            self.fr_btn, text="Config Buttons")
        self.fr_config_btn.pack(fill=X, padx=10, pady=20)
        self.fr_config_btn.columnconfigure(0, weight=1, uniform='fred')
        self.fr_config_btn.columnconfigure(1, weight=1, uniform='fred')

        row = col = 0
        for btn_text, (action, active) in CONFIG_BTN.items():
            btn = ConfigButton(self.fr_config_btn, text=btn_text, active=active,
                               exec=self.execute, action=action)
            btn.grid(row=row, column=col, sticky=EW, padx=3, pady=3)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def execute(self, action, val=""):
        print(action, val)

    def close(self):
        self.destroy()
