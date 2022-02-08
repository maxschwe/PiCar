from tkinter.ttk import *
from tkinter import Toplevel
from tkinter.constants import *

from tcp import ACTIONS
import time


def add_btn(master, action_btn, new, **kwargs):
    btn_clicked = False

    def on_btn_clicked():
        nonlocal btn_clicked
        btn_clicked = True

    win = Toplevel(master)

    title, btn_txt = ("Add Button", "Add") if new else ("Edit Button", "Save")
    win.title(title)

    fr_config = Frame(win)
    fr_config.pack(padx=20, pady=(20, 0))

    lbl_name = Label(fr_config, text="Name:")
    lbl_name.grid(row=0, column=0)

    name = Entry(fr_config)
    name.grid(row=1, column=0, padx=10)

    lbl_action = Label(fr_config, text="Action:")
    lbl_action.grid(row=0, column=1, pady=5)

    action = Combobox(fr_config, values=ACTIONS.list(), state="readonly")
    action.grid(row=1, column=1, padx=10)

    lbl_msg = Label(fr_config, text="Params:")
    lbl_msg.grid(row=0, column=2)

    msg = Entry(fr_config)
    msg.grid(row=1, column=2, padx=10)

    if not action_btn:
        lbl_active = Label(fr_config, text="Active:")
        lbl_active.grid(row=0, column=3)

        active = Checkbutton(fr_config)
        active.grid(row=1, column=3, padx=10)

    if not new:
        action.current(ACTIONS.list().index(kwargs["action"]))
        msg.delete(0, "end")
        msg.insert(0, kwargs["msg"])
        if not action_btn:
            act = kwargs["active"]
            if act:
                active.state(["selected"])
            else:
                active.state(['!alternate'])
    else:
        action.current(0)
        if not action_btn:
            active.state(["!alternate"])

    btn = Button(win, command=on_btn_clicked,
                 style="Accent.TButton", text=btn_txt)
    btn.pack(side=RIGHT, padx=30, pady=20)
    win.update_idletasks()
    x = int(master.winfo_screenwidth()/2 - win.winfo_width()/2)
    y = max(0, int(master.winfo_screenheight()/2 - win.winfo_height()/2 - 40))
    win.geometry(f"+{x}+{y}")
    win.grab_set()
    while not btn_clicked:
        win.update()
        time.sleep(0.001)

    data = {"action": action.current(), "msg": msg.get()}

    if not action_btn:
        active = 0 if active.state() == () else 1
        data["active"] = active
    name = name.get()
    win.destroy()
    return name, data
