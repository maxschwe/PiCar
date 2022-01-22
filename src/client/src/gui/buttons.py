from tkinter.ttk import *
from tkinter.constants import *
from tkinter import IntVar


class ActionButton(Button):
    def __init__(self, master, exec, action, *args, **kwargs):
        self.exec = exec
        self.action = action
        super().__init__(master, command=self.on_click, *args, **kwargs)

    def on_click(self):
        self.exec(self.action)


class ConfigButton(Checkbutton):
    def __init__(self, master, active, exec, action, *args, **kwargs):
        self.exec = exec
        self.action = action
        self.active = active
        var = IntVar(master, 1 if self.active else 0)
        super().__init__(master, command=self.on_click,
                         style="Toggle.TButton", variable=var, *args, **kwargs)

    def on_click(self):
        self.active = not self.active
        self.exec(self.action, val=self.active)
