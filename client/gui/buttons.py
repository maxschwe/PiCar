from tkinter.ttk import *
from tkinter.constants import *
from tkinter import BooleanVar


class ActionButton(Button):
    def __init__(self, master, exec, action, msg="", ret=None, *args, **kwargs):
        self.exec = exec
        self.action = action
        self.msg = msg
        self.ret = ret
        super().__init__(master, command=self.on_click, *args, **kwargs)

    def on_click(self):
        self.exec(action=self.action, params=self.msg)


class ConfigButton(Checkbutton):
    def __init__(self, master, active, exec, action, ret, *args, **kwargs):
        self._exec = exec
        self.action = action
        self.ret = ret
        self.active = active
        var = BooleanVar(value=self.active)
        super().__init__(master, command=self.on_click,
                         style="Toggle.TButton", variable=var, *args, **kwargs)

    def on_click(self):
        self.active = not self.active
        self.exec()

    def exec(self):
        self._exec(action=self.action, params=self.active)
