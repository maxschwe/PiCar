from tkinter.ttk import *
from tkinter.constants import *
from tkinter import IntVar


class Slider(LabelFrame):
    def __init__(self, master, label, exec, action, from_, to, orient=HORIZONTAL, initial_val=0, *args, **kwargs):
        self.exec = exec
        self.action = action
        self.from_ = from_
        self.to = to

        self.initial_val = self.last_val = initial_val
        self.label = ""
        self.val = IntVar(value=initial_val)
        self.entry_val = IntVar(value=initial_val)
        super().__init__(master)

        self.fr_main = Frame(self)
        self.fr_main.pack(padx=30, pady=30)
        self.fr_input = Frame(self.fr_main)
        self.lbl = Label(self.fr_input, text=label)

        self.entry = Entry(self.fr_input, textvariable=self.entry_val, width=5)

        self.entry.bind("<FocusOut>", self.on_focus_out)
        self.entry.bind(
            "<FocusIn>", self.validate_int)
        self.entry.bind("<KeyRelease>", self.validate_int)
        self.entry.bind("<Return>", self.on_return)

        if orient == VERTICAL:
            from_, to = to, from_

        self.slider = Scale(self.fr_main, variable=self.val,
                            command=self.on_change, orient=orient, from_=from_, to=to, *args, **kwargs)

        if orient == HORIZONTAL:
            self.btn_reset = Button(
                self.fr_main, text="Reset", command=self.reset)
            self.fr_input.pack(side=TOP)
            self.lbl.pack(side=LEFT)
            self.entry.pack(side=LEFT)
            self.slider.pack(side=TOP, pady=10)
            self.btn_reset.pack(side=TOP)
        else:
            self.btn_reset = Button(
                self.fr_input, text="Reset", command=self.reset)
            self.fr_input.pack(side=LEFT)
            self.lbl.pack(side=TOP)
            self.entry.pack(side=TOP, pady=5)
            self.btn_reset.pack(side=LEFT, expand=True, pady=(10, 5))
            self.slider.pack(side=RIGHT, padx=10)

        self.on_change(self.initial_val)

    def validate_int(self, *_):
        if self.entry.get() == "":
            self.entry.state(["invalid"])
            return False
        else:
            try:
                val = int(self.entry.get())
                if self.from_ <= val <= self.to:
                    self.entry.state(["!invalid"])
                    return True
                else:
                    self.entry.state(["invalid"])
                    return False
            except ValueError:
                self.entry.state(["invalid"])
                return False

    def on_focus_out(self, *_):
        if not self.validate_int():
            self.entry_val.set(int(float(self.slider.get())))
            self.validate_int()

    def on_return(self, *_):
        if self.validate_int():
            new_val = int(self.entry_val.get())
            self.val.set(new_val)
            self.on_change(new_val)

    def on_change(self, val):
        val = int(float(val))
        self.val.set(val)
        self.entry_val.set(val)

        # send if value changed
        if self.last_val != val:
            self.last_val = val
            self.exec(action=self.action, params=val)

    def reset(self):
        self.val.set(self.initial_val)
        self.entry_val.set(self.initial_val)
        self.on_change(self.initial_val)
