from tkinter.ttk import *
from tkinter.constants import *
from tkinter import BooleanVar


class ActionButton(Button):
    def __init__(self, master, name, exec, action, edit, params="", *args, **kwargs):
        self.name = name
        self.exec = exec
        self.action = action
        self.edit = edit
        self.params = params
        super().__init__(master, command=self.on_click, text=self.name, *args, **kwargs)
        self.bind("<Button-3>", self.on_right_click)

    def edit_data(self, name, action, params):
        self.name = name
        self.action = action
        self.params = params

    def on_right_click(self, _):
        self.edit(self.index)

    def on_click(self):
        self.exec(action=self.action, params=self.params)

    def get_data(self, decoded=False):
        return {"name": self.name, "action": self.action.value if decoded else self.action, "params": self.params}


class ConfigButton(Checkbutton):
    def __init__(self, master, name, active, exec, action, edit, *args, **kwargs):
        self.name = name
        self._exec = exec
        self.action = action
        self.active = active
        self.edit = edit
        var = BooleanVar(value=self.active)
        super().__init__(master, command=self.on_click,
                         style="Toggle.TButton", variable=var, text=self.name, *args, **kwargs)
        self.bind("<Button-3>", self.on_right_click)

    def edit_data(self, name, action, active):
        self.name = name
        self.action = action
        self.active = active
        self.exec()

    def on_click(self):
        self.active = not self.active
        self.exec()

    def on_right_click(self, _):
        self.edit(self.index)

    def exec(self):
        self._exec(action=self.action, params=[self.active])

    def get_data(self, decoded=False):
        return {"name": self.name, "action": self.action.value if decoded else self.action, "active": self.active}
