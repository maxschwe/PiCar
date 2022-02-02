from tkinter.ttk import *
from tkinter import Toplevel
from tkinter.constants import *

from ..configuration.const import *


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

    action = Combobox(fr_config, values=ACTION.list(), state="readonly")
    action.grid(row=1, column=1, padx=10)

    lbl_msg = Label(fr_config, text="Message:")
    lbl_msg.grid(row=0, column=2)

    msg = Entry(fr_config)
    msg.grid(row=1, column=2, padx=10)

    lbl_ret = Label(fr_config, text="Return Type:")
    lbl_ret.grid(row=0, column=3)

    ret = Combobox(fr_config, values=RETURN.list(), state="readonly")
    ret.grid(row=1, column=3, padx=10)

    if not action_btn:
        lbl_active = Label(fr_config, text="Active:")
        lbl_active.grid(row=0, column=4)

        active = Checkbutton(fr_config)
        active.grid(row=1, column=4, padx=10)

    if not new:
        action.current(ACTION.list().index(kwargs["action"]))
        msg.delete(0, "end")
        msg.insert(0, kwargs["msg"])
        ret.current(RETURN.list().index(kwargs["ret"]))
        if not action_btn:
            act = kwargs["active"]
            if act == 0:
                active.state(['!alternate'])
            elif act == 1:
                active.state(["selected"])
    else:
        action.current(0)
        ret.current(0)
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

    data = {"action": action.current(), "msg": msg.get(), "ret": ret.current()}

    if not action_btn:
        active = 0 if active.state() == () else 1
        data["active"] = active
    name = name.get()
    win.destroy()
    return name, data
