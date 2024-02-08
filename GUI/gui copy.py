from operator import truediv
import PySimpleGUI as sg
import os, json, re
import copy


from operator import truediv
import PySimpleGUI as sg
import os, json, re
import copy
from natsort import natsorted
import hashlib
class config:
    def __init__(self, data=None):
        self.pypydir = "/home/will/dissertation/pypy_versions"
        self.methodNames = self.get_methodNames()
        self.methods, self.all_methods = self.get_all_methods()
        self.listlength = [1000]
        self.listcount = 100
        self.outputFilePath = ""
        self.insertion = False
        self.data_types = {
            "Few Unique": False,
            "Sorted": False,
            "Reverse Sorted": False,
            "Nearly Sorted": False,
            "Random": False,
        }
        self.data_sizes = {"large": False, "med": False, "small": False, "tiny": False}
        self.set_config(data)
        self.hash = ''

    def as_json(self):
        data = {"pypydir": self.pypydir, 
                "methods": self.methods,
                "listlength": self.listlength,
                "listcount": self.listcount,
                "outputFilePath": self.outputFilePath,
                "insertion": self.insertion,  
                "data_types": self.data_types,
                "data_sizes":self.data_sizes}
        # self.hash = 
        data['hash'] =hashlib.md5(json.dumps(data, separators=(",", ":")).encode("utf-8")).hexdigest() 
        return data
    def set_config(self, data):
        try:
            self.pypydir = data["pypy_versions"]
            self.methods = data["methods"]
            self.listlength = data["listlength"]
            self.listcount = data["listcount"]
            self.outputFilePath = data["output"]
            self.insertion = data["insertion"]
            self.data_types = data["data_types"]
            self.data_sizes = data["data_sizes"]
        except Exception as e:
            None
    def get_methodNames(self):
        try:
            pdir = os.listdir(self.pypydir)
            if len(pdir) < 1:
                raise FileNotFoundError("PyPy not in directory. Check config")
            return sorted(
                {
                    re.findall(r"_(.*)$", x[6:])[0]
                    for x in pdir
                    if x != "timsort_timsort"
                }
            )
        except Exception as f:
            print(f)
    def get_all_methods(self):
        pvs = {}
        pvm = {}
        tempv = os.listdir(self.pypydir)
        for v in self.methodNames:
            values = [x[: -len(v) - 1] for x in tempv if x[-len(v) :] == v]
            values = natsorted(values)
            pvm[v] = values
            pvs.setdefault(v, [])
            for m in pvm[v]:
                tempv.remove(f"{m}_{v}")
        return pvs, pvm




class QueueConfig:
    def __init__(self):
        self.queue = []
        self.methodNames = {}
        self.filename='config.json'
        
    def getQueue(self):
        with open(self.filename, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                self.queue=[config()]
                return
        self.queue = [config(config_item) for config_item in data["queue"]]
    def saveQueue(self):
        with open(self.filename, "w") as f:
            outputfile = {"queue" : []}
            for config in self.queue:                
                outputfile["queue"].append(config.as_json())
            outputfile
            json.dump(outputfile, f)
    def new_config(self):
        self.queue.insert(0,config())


defaultjson = {
    "queue": [
        {
            "pypy_versions": "/home/will/dissertation/pypy_versions",
            "methods": {},
            "listlength": "",
            "listcount": 0,
            "Few Unique": False,
            "Sorted": False,
            "Reverse Sorted": False,
            "Nearly Sorted": False,
            "Random": False,
            "large": False,
            "med": False,
            "small": False,
            "tiny": False,
            "output": "",
            "insertion": False,
        }
    ]
}
with open("config.json", "r") as f:
    try:
        data = json.load(f)
    except Exception:
        data = copy.deepcopy(defaultjson)
queue = data["queue"]


def sorted_nicely(l):
    """Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]
    return sorted(l, key=alphanum_key)


config = queue[0]
pypy_versions_dir = config["pypy_versions"]
pypy_versions_min = sorted(
    {
        re.findall(r"_(.*)$", x[6:])[0]
        for x in os.listdir(pypy_versions_dir)
        if x != "timsort_timsort"
    }
)
pypy_versions_max = {}
items = []
listbox_size = (max(map(len, pypy_versions_min)) + 2, len(pypy_versions_min))
previous_min = ""
previous_method = ""


def get_all_methods():
    pvs = {}
    pvm = {}
    global pypy_versions_min
    tempv = os.listdir(pypy_versions_dir)
    for v in pypy_versions_min:
        values = [x[: -len(v) - 1] for x in tempv if x[-len(v) :] == v]
        values = sorted_nicely(values)
        pvm[v] = values
        pvs.setdefault(v, [])
        for m in pvm[v]:
            tempv.remove(f"{m}_{v}")
    return pvs, pvm


pypy_versions_selected, pypy_versions_max = get_all_methods()
try:
    pypy_versions_selected = (
        config["methods"] if config["methods"] != {} else pypy_versions_selected
    )

    for key in pypy_versions_selected.keys():
        items.extend(f"{key}_{val}" for val in pypy_versions_selected[key])
except Exception as e:
    items = []


def removeduplicates(it):
    print(len(it))
    for c in it:
        print(c["methods"])
    print("---")
    filtered_json = []
    md5_list = []
    for item in it:
        temp = copy.deepcopy(item)
        temp["methods"] = hashlib.md5(
            json.dumps(temp["methods"], separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        md5_result = hashlib.md5(
            json.dumps(temp, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if md5_result not in md5_list:
            md5_list.append(md5_result)
            filtered_json.append(item)
    return filtered_json


sg.theme("DarkAmber")  # Add a touch of color
# All the stuff inside your window.
dt_column = [
    [sg.Text("Data Type:")],
    [
        sg.Checkbox(
            "Few Unique", default=config.get("Few Unique", True), key="Few Unique"
        )
    ],
    [sg.Checkbox("Sorted", default=config.get("Sorted", True), key="Sorted")],
    [
        sg.Checkbox(
            "Reverse Sorted",
            default=config.get("Reverse Sorted", True),
            key="Reverse Sorted",
        )
    ],
    [
        sg.Checkbox(
            "Nearly Sorted",
            default=config.get("Nearly Sorted", True),
            key="Nearly Sorted",
        )
    ],
    [sg.Checkbox("Random", default=config.get("Random", True), key="Random")],
]
ds_column = [
    [sg.Text("Data Size:")],
    [sg.Checkbox("large", default=config.get("large", True), key="large")],
    [sg.Checkbox("med", default=config.get("med", True), key="med")],
    [sg.Checkbox("small", default=config.get("small", True), key="small")],
    [sg.Checkbox("tiny", default=config.get("tiny", True), key="tiny")],
    [sg.Text("")],
]
input_labels = [
    [sg.Text("List length (l)")],
    [sg.Text("List count (n)")],
    [sg.Text("Output file (o)")],
    [sg.Text("Insertion test (s)")],
]
inputs = [
    [
        sg.InputText(
            config.get("listlength", 1000), key="listlength", enable_events=True
        )
    ],
    [sg.InputText(config.get("listcount", "100"), key="listcount", enable_events=True)],
    [sg.InputText(key="pretty_filename", visible=True)],
    [sg.Checkbox("", default=config.get("insertion", False), key="insertion")],
]

print()
layout = [
    [
        sg.Listbox(
            pypy_versions_min,
            size=listbox_size,
            expand_y=True,
            default_values=pypy_versions_min[0],
            enable_events=True,
            key="min",
            select_mode="LISTBOX_SELECT_MODE_SINGLE",
            bind_return_key=True,
        ),
        sg.Listbox(
            pypy_versions_max[pypy_versions_min[0]],
            default_values=pypy_versions_selected[pypy_versions_min[0]],
            size=listbox_size,
            expand_y=True,
            select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
            key="max",
            enable_events=True,
        ),
        sg.Listbox(
            items,
            size=listbox_size,
            expand_y=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            key="methods",
            metadata=[],
            enable_events=True,
            bind_return_key=True,
        ),
    ],
    [
        sg.Column(dt_column),
        sg.Column(ds_column),
        sg.Column(input_labels, size=(100, 100)),
        sg.Column(inputs, size=(200, 100)),
    ],
    [
        [
            sg.Button("Update Output", key="update_button"),
            sg.Button("Save", key="save_config"),
            sg.Button("Sort", key="start_sorting"),
            sg.Button("Queue", key="add_queue"),
            sg.Button("Clear Queue", key="clear_queue"),
            sg.Text(
                str(len([c for c in queue if c["listcount"] != 0])), key="queuelen"
            ),
        ],
        [sg.InputText(key="output_filename", visible=False)],
    ],
]


# Create the Window
window = sg.Window("Sorting Helper", layout, location=(500, 500))


# Event Loop to process "events" and get the "values" of the inputs
def methodevent():
    global previous_method
    for key in pypy_versions_selected.keys():
        vals = list(pypy_versions_selected[key])
        for val in vals:
            option = f"{key}_{val}"
            selection = (
                window["methods"].get()[0] if len(window["methods"].get()) > 0 else ""
            )
            if selection == option:
                if previous_method == window["methods"].get()[0]:
                    pypy_versions_selected[key].remove(val)
                    items = []
                    for key in pypy_versions_selected.keys():
                        items.extend(
                            f"{key}_{val}" for val in pypy_versions_selected[key]
                        )
                    window["methods"].update(items)
                    previous_method = ""
                else:
                    previous_method = window["methods"].get()[0]
                    window["min"].set_value(
                        [
                            key,
                        ]
                    )
                minevent(window["min"].get()[0], False)
                return


def maxevent():
    pypy_versions_selected[window["min"].get()[0]] = window["max"].get()
    items = []
    for key in pypy_versions_selected.keys():
        items.extend(f"{key}_{val}" for val in pypy_versions_selected[key])
    window["methods"].update(items)


def minevent(curr, reset=True):
    vals = pypy_versions_max[curr]
    default = pypy_versions_selected[curr] or []
    window["max"].update(vals)
    window["max"].set_value(default)
    if reset:
        window["methods"].set_value([])


def mindouble():
    global previous_min
    curr_min = window["min"].get()[0]
    if previous_min == curr_min:
        window["max"].update(pypy_versions_max[curr_min])
        if pypy_versions_max[curr_min] == pypy_versions_selected[curr_min]:
            window["max"].set_value([])
        else:
            window["max"].set_value(pypy_versions_max[curr_min])
        maxevent()
        previous_min = ""
    else:
        minevent(curr_min)
        previous_min = curr_min


import hashlib


def save_options(force=False):
    global queue
    global config
    c = {
        "methods": pypy_versions_selected,
        "listcount": int(window["listcount"].get()),
    }
    c["listlength"] = window["listlength"].get()
    c["Few Unique"] = window["Few Unique"].get()
    c["Sorted"] = window["Sorted"].get()
    c["Reverse Sorted"] = window["Reverse Sorted"].get()
    c["Nearly Sorted"] = window["Nearly Sorted"].get()
    c["Random"] = window["Random"].get()
    c["large"] = window["large"].get()
    c["med"] = window["med"].get()
    c["small"] = window["small"].get()
    c["tiny"] = window["tiny"].get()
    c["output"] = window["output_filename"].get()
    c["insertion"] = window["insertion"].get()  #
    queue.append(copy.deepcopy(c))
    config = copy.deepcopy(c)
    queue = [c for c in queue if c["listcount"] != 0]
    queue = removeduplicates(queue)


def get_filename(name):
    path = os.path.join("/home/will/dissertation/sort_times", f"{name}_0.json")
    uniq = 0
    while os.path.exists(path) or path in [x["output"] for x in queue if x["output"]]:
        path = os.path.join(
            "/home/will/dissertation/sort_times", f"{name}_{str(uniq)}.json"
        )
        uniq += 1
    return path


def get_output(force=False):
    methods = [
        key
        for key in pypy_versions_selected.keys()
        if len(pypy_versions_selected[key]) > 0
    ]
    if window["pretty_filename"].get() and force == True:
        path = "/home/will/dissertation/sort_times/" + window["pretty_filename"].get()
    else:
        path = (
            (
                get_filename("_".join(methods))
                if len(methods) > 1
                else get_filename(methods[0])
            )
            if methods
            else ""
        )
    window["output_filename"].update(path)
    window["pretty_filename"].update(re.findall(r"([^\/]+$)", path)[0])


def get_methods(c):
    for key in c["methods"].keys():
        for val in list(c["methods"][key]):
            yield (f"{val}_{key}")


while True:
    event, values = window.read()
    if event in [sg.WIN_CLOSED, "Cancel"]:  # if user closes window or clicks cancel
        save_options()
        break
    if event == "min":
        mindouble()
        previous_method = ""
    if event == "max":
        maxevent()
        previous_min = ""
        previous_method = ""
    if event == "methods":
        methodevent()
        previous_min = ""
    if event == "listcount":
        val = (
            re.sub("[^0-9]", "", window["listcount"].get())
            if window["listcount"].get() != ""
            else 0
        )
        val = min(1000000, max(0, int(val)))
        window["listcount"].update(val)
    if event == "listlength":
        val = re.sub("[^0-9, ]", "", window["listlength"].get()).replace(" ", "")
        end = val[-1] == "," if len(val) != 0 else False
        val = [int(x.strip()) for x in val.split(",") if x.strip() != ""]
        out = ", ".join(map(str, val))
        out = f"{out}," if end else out
        window["listlength"].update(out)
    if event == "update_button":
        get_output()
    if event == "save_config":
        get_output(force=True)
        save_options(force=True)
    if event == "start_sorting":
        if window["output_filename"].get() == "":
            get_output()
        save_options()
        break
    if event == "add_queue":
        if window["output_filename"].get() == "":
            get_output()
        save_options()
        window["queuelen"].update(len(queue))

    if event == "clear_queue":
        queue = copy.deepcopy(defaultjson["queue"])
window.close()
import itertools

data_sizes = ["large", "med", "small", "tiny"]
data_types = ["Few Unique", "Sorted", "Reverse Sorted", "Nearly Sorted", "Random"]


def get_commands(m, c):
    sizes = str([f"{str(size)}" for size in data_sizes if not c[size]])[1:-1].replace(
        ",", ""
    )
    types = str([f"{str(t)}" for t in data_types if not c[t]])[1:-1].replace(",", "")
    lengths = str([int(x) for x in c["listlength"].split(",")])[1:-1].replace(",", "")
    methodname = re.findall(r"([^\/]+$)", m)[0]
    yield f' sort_timer_gendata_pipe.py -m {methodname} -o {c["output"]} -n {c["listcount"]} -l {lengths} -et {types} -es {sizes} {"-s" if c["insertion"]==True else ""}'


def get_methodCommand():
    methodCommand = []
    for c in queue:
        for method in get_methods(c):
            path = f"/home/will/dissertation/pypy_versions/{method}/bin/pypy"
            methodCommand.extend(
                (path, command, method) for command in get_commands(method, c)
            )
    return methodCommand


qlen = len(queue)
methodCommand = get_methodCommand()
multilinecol = [
    [
        sg.Multiline(
            f"{queue}",
            size=(50, 30),
            echo_stdout_stderr=False,
            reroute_stdout=False,
            autoscroll=True,
            background_color="black",
            text_color="white",
            key="completed",
        )
    ],
    [
        sg.Multiline(
            f"{len(methodCommand)} items, Run to start. Queue length: {qlen}",
            size=(50, 2),
            echo_stdout_stderr=False,
            reroute_stdout=False,
            autoscroll=True,
            background_color="black",
            text_color="white",
            key="-MLINE-",
        )
    ],
]
layout2 = [
    [sg.Column(multilinecol)],
    [sg.Button("Run", bind_return_key=True), sg.Text("Completed: ", key="iters")],
]
window2 = sg.Window("Sorting Helper 2", layout2, location=(500, 500), finalize=True)

import subprocess, sys


def get_outpout(items, method):
    match = re.match(r"(.*?\d+)+", method)
    if match:
        method = match[1]
    if items[0] == "count":
        return ("Green", f"{method}\t {items[1]} {items[2]} \t {items[3]}/{items[4]}")
    elif items[0] == "warming":
        return ("Cyan", f"{method}\t Warming up: \t{items[1]}/{items[2]}")
    elif items[0] == "eval":
        insr = "" if items[6] == "1" else f"/{items[6]}"
        return (
            "Red",
            f'{method} {items[1]} {items[2]} {items[3]} s\t{items[4]}{insr}\t\t {"" if items[5] else "error"}',
        )
    elif items[0] == "Total":
        return ("Purple", f"{method} Total time: {items[1]}")
    else:
        return ("White", str(items))


def runCommand(cmd, method, timeout=None, window=None):
    print(cmd)
    p = subprocess.Popen(
        cmd, shell=True, cwd="/home/will/dissertation", stdout=subprocess.PIPE
    )
    out = ""
    cont = True
    while cont:
        cont = p.poll() is None
        out += p.stdout.read(1 if cont else -1).decode(
            errors="replace" if (sys.version_info) < (3, 5) else "backslashreplace"
        )
        if "\n" in out:
            for o in out.split("\n"):
                colour, text = get_outpout(o.split(","), method)
                if colour == "White":
                    continue
                elif colour == "Red" or colour == "Purple":
                    window["completed"].print(
                        text,
                        end="\n",
                        text_color=colour,
                        autoscroll=True,
                    )
                    window["-MLINE-"].update("", append=False)
                else:
                    window["-MLINE-"].update(
                        text,
                        text_color_for_value=colour,
                        append=False,
                        autoscroll=True,
                    )
                out = out[out.find("\n") + 1 :]
        window.Refresh()


import time
from datetime import timedelta


def dhm(duration):
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours}h : {minutes}m : {seconds}s"


while True:
    event, values = window2.read()
    if event in [sg.WIN_CLOSED, "Cancel"]:  # if user closes window or clicks cancel
        break
    elif event == "Run":
        t = time.time()
        for count, (path, command, method) in enumerate(methodCommand, start=1):
            runCommand(f"{path} {command}", method, window=window2)
            ctime = timedelta(seconds=time.time() - t)
            remtime = (ctime / count) * (len(methodCommand) - count)
            window2["iters"].update(
                value=f"Completed: {count}/{len(methodCommand)} Time used: {dhm(ctime)}  Remaining: {dhm(remtime)}"
            )
window2.close()
