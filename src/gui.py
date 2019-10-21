import tkinter
from tkinter import ttk
from iGEM_Cell_Tracking import *
from CellTrack import *
root =tkinter.Tk()
root.title("Cell Checking GUI")
root.geometry("400x400+200+50")
root.iconbitmap("icon.ico")
tracker_type_lable = tkinter.Label(root,text="tracker type")
tracker_type_lable.pack()
tracker_type_setup = ttk.Combobox(root)
tracker_type_setup.config(state="readonly")
tracker_type_setup["value"] = ("BOOSTING","MIL","KCF","TLD","MEDIANFLOW","GOTURN","MOSSE","CSRT")
tracker_type_setup.current(7)
tracker_type_setup.pack()

showCrosshair_label = tkinter.Label(root,text="showCrosshair")
showCrosshair_label.pack()
showCrosshair_setup=ttk.Combobox(root)
showCrosshair_setup.config(state="readonly")
showCrosshair_setup["value"]=("True","False")
showCrosshair_setup.current(0)
showCrosshair_setup.pack()

fromCenter_lable = tkinter.Label(root,text="fromCenter")
fromCenter_lable.pack()
fromCenter_setup = ttk.Combobox(root)
fromCenter_setup.config(state="readonly")
fromCenter_setup["value"]=("True","False")
fromCenter_setup.current(0)
fromCenter_setup.pack()

max_cell_cnt_text= tkinter.Variable()
max_cell_cnt_lable=tkinter.Label(root,text="max_cell_cnt")
max_cell_cnt_lable.pack()
max_cell_cnt_setup=tkinter.Entry(root,textvariable=max_cell_cnt_text)
max_cell_cnt_text.set("5")
max_cell_cnt_setup.pack()

miss_tolerance_text= tkinter.Variable()
miss_tolerance_lable=tkinter.Label(root,text="miss_tolerance")
miss_tolerance_lable.pack()
miss_tolerance_setup=tkinter.Entry(root,textvariable=miss_tolerance_text)
miss_tolerance_text.set("0.5")
miss_tolerance_setup.pack()

dawdle_dist_def_text=tkinter.Variable()
dawdle_dist_def_lable=tkinter.Label(root,text="dawdle_dist_def")
dawdle_dist_def_lable.pack()
dawdle_dist_def_setup=tkinter.Entry(root,textvariable=dawdle_dist_def_text)
dawdle_dist_def_text.set("50")
dawdle_dist_def_setup.pack()

dawdle_threshold_text=tkinter.Variable()
dawdle_threshold_lable=tkinter.Label(root,text="dawdle_threshold")
dawdle_threshold_lable.pack()
dawdle_threshold_setup=tkinter.Entry(root,textvariable=dawdle_threshold_text)
dawdle_threshold_text.set("100")
dawdle_threshold_setup.pack()

valid_threshold_text=tkinter.Variable()
valid_threshold_lable=tkinter.Label(root,text="valid_threshold")
valid_threshold_lable.pack()
valid_threshold_setup=tkinter.Entry(root,textvariable=valid_threshold_text)
valid_threshold_text.set("150")
valid_threshold_setup.pack()

MISS_JUDGE__text=tkinter.Variable()
MISS_JUDGE_lable=tkinter.Label(root,text="MISS_JUDGE")
MISS_JUDGE_lable.pack()
MISS_JUDGE_setup=tkinter.Entry(root,textvariable=MISS_JUDGE__text)
MISS_JUDGE__text.set("0.0001")
MISS_JUDGE_setup.pack()
def func():
    tracker_type=tracker_type_setup.get()

    if showCrosshair_setup.get()=="True":
        showCrosshair=True
    else:
        showCrosshair=False

    if fromCenter_setup.get()=="True":
        fromCenter=True
    else:
        fromCenter=False

    max_cell_cnt=float(max_cell_cnt_setup.get())

    miss_tolerance = float(miss_tolerance_setup.get())

    dawdle_dist_def = float(dawdle_dist_def_setup.get())

    dawdle_threshold = float(dawdle_threshold_setup.get())

    valid_threshold = float(valid_threshold_setup.get())

    MISS_JUDGE = float(MISS_JUDGE_setup.get())

    track_go()



button = tkinter.Button(root,text = "Run!",command=func)
button.pack()
root.mainloop()
