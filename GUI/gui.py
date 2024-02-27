from operator import truediv
import PySimpleGUI as sg
import os, json, re
import copy
from natsort import natsorted
import hashlib
import subprocess, sys
import time
from datetime import timedelta
import psutil
import signal
class Config(object):

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

    def items(self):
        return [f"{val}_{key}" for key, vals in self.methods.items() for val in vals]

    def as_json(self):
        return {
            "pypydir": self.pypydir,
            "methods": self.methods,
            "listlength": self.listlength,
            "listcount": self.listcount,
            "outputFilePath": self.outputFilePath,
            "insertion": self.insertion,
            "data_types": self.data_types,
            "data_sizes": self.data_sizes,
        }

    def set_config(self, data):
        if data:
            for key in [
                "pypydir",
                "methods",
                "listlength",
                "listcount",
                "outputFilePath",
                "insertion",
                "data_types",
                "data_sizes",
            ]:
                setattr(self, key, data.get(key, getattr(self, key)))

    def get_methodNames(self):
        if pdir := os.listdir(self.pypydir):
            return sorted(
                {re.findall(r"_(.*)$", x[6:])[0] for x in pdir if x != "timsort_timsort"}
            )
        else:
            raise FileNotFoundError("PyPy not in directory. Check config")

    def get_all_methods(self):
        tempv = os.listdir(self.pypydir)
        pvm = {
            v: natsorted([x[: -len(v) - 1] for x in tempv if x.endswith(v)])
            for v in self.methodNames
        }
        pvs = {v: [] for v in self.methodNames}
        return pvs, pvm


class QueueConfig(object):
    def __init__(self):
        self.queue = []
        self.filename = "config.json"
        self.get_q_fromFile()

    def __getitem__(self, item):
        return self.queue[item]

    def __setitem__(self, idx, value):
        self.queue[idx] = value

    def __getattr__(self, name):
        return getattr(self.queue[0], name)

    def get_q_fromFile(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
            self.queue = [Config(config_item) for config_item in data.get("queue", [])]
        except (Exception, FileNotFoundError):
            self.queue = [Config()]

    def saveQueue(self):
        with open(self.filename, "w") as f:
            outputfile = {"queue": [config.as_json() for config in self.queue]}
            json.dump(outputfile, f, indent=4)

    def new_config(self, data=None, i=1):
        if data is None:
            data = {}
        for _ in range(i):
            self.queue.insert(0, Config(data))

    def remove_duplicates(self):
        seen_hashes = set()
        self.queue = [
            config
            for config in self.queue
            if not (
                config_hash := hashlib.md5(
                    json.dumps(config.as_json(), separators=(",", ":")).encode("utf-8")
                ).hexdigest()
            )
            in seen_hashes
            and not seen_hashes.add(config_hash)
        ]


import PySimpleGUI as sg


class SortingHelperGUI:
    def __init__(self):
        self.q = QueueConfig()
        self.window = None
        self.window2 = None
        self.prev_var = ""
        self.prev_method = ""
        self.methodCommand = []
        self.startTime = 0
        self.iters = 0
        self.count = 0
        self.psProcess = None

    def run(self):
        self.setup_window()
        self.event_loop()
        # self.window.close()

    def setup_window(self):
        sg.theme("DarkAmber")
        layout = [
            [
                self.create_listbox(
                    "methods_var",
                    self.q.methodNames,
                    self.q.methodNames[0],
                    "LISTBOX_SELECT_MODE_SINGLE",
                ),
                self.create_listbox(
                    "method_imps",
                    self.q.all_methods[self.q.methodNames[0]],
                    self.q.methods[self.q.methodNames[0]],
                    sg.LISTBOX_SELECT_MODE_MULTIPLE,
                ),
                self.create_listbox(
                    "methods_selected",
                    self.q.items(),
                    [],
                    sg.LISTBOX_SELECT_MODE_SINGLE,
                ),
            ],
            [
                self.create_column("Data Type:", self.q.data_types),
                self.create_column("Data Size:", self.q.data_sizes),
                sg.Column(self.create_input_labels(), size=(100, 100)),
                sg.Column(self.create_inputs(), size=(200, 100)),
            ],
            [
                [
                    sg.Button("Update Output", key="update_button"),
                    sg.Button("Save", key="save_config"),
                    sg.Button("Sort", key="start_sorting"),
                    sg.Button("Queue", key="add_queue"),
                    sg.Button("Clear Queue", key="clear_queue"),
                    sg.Button("View Next", key="next_queue"),
                    sg.Button("Delete item", key="del_queue"),
                    sg.Text(str(len(self.q.queue)), key="queuelen"),
                ],
            ],
        ]
        self.window = sg.Window("Sorting Helper", layout, location=(500, 500))

    def create_listbox(self, key, values, default_values, select_mode):
        return sg.Listbox(
            values,
            size=(max(map(len, self.q.methodNames)) + 2, len(self.q.methodNames)),
            expand_y=True,
            default_values=default_values,
            enable_events=True,
            key=key,
            select_mode=select_mode,
            bind_return_key=True,
        )

    def create_column(self, title, options):
        return sg.Column(
            [[sg.Text(title)]]
            + [
                [sg.Checkbox(text, default=options[text], key=text, enable_events=True)]
                for text in options
            ]
        )

    def create_input_labels(self):
        return [
            [sg.Text(label)]
            for label in [
                "List length (l)",
                "List count (n)",
                "Output file (o)",
                "Insertion test (s)",
            ]
        ]

    def create_inputs(self):
        return [
            [sg.InputText(self.q.listlength, key="listlength", enable_events=True)],
            [sg.InputText(self.q.listcount, key="listcount", enable_events=True)],
            [sg.InputText(os.path.basename(self.q.outputFilePath), key="output_filename", visible=True)],
            [
                sg.Checkbox(
                    "", default=self.q.insertion, key="insertion", enable_events=True
                )
            ],
        ]

    def event_loop(self):
        event_handlers = {
            "methods_var": self.mindouble,
            "method_imps": self.maxevent,
            "methods_selected": self.methodevent,
            "listcount": self.update_listcount,
            "listlength": self.update_listlength,
            "update_button": self.get_output,
            "save_config": self.save_config_and_queue,
            "start_sorting": self.start_sorting,
            "add_queue": self.add_queue,
            "clear_queue": self.clear_queue,
            "next_queue": self.next_queue,
            "del_queue": self.del_queue,
        }
        while True:
            event, values = self.window.read()
            if event in [sg.WIN_CLOSED, "Cancel"]:
                break
            if handler := event_handlers.get(event):
                handler()
    def del_queue(self):
        if len(self.q.queue) == 1:
            return
        del self.q.queue[0]
        self.saveQueue()
        self.window.close()
        self.setup_window()

    def next_queue(self):
        self.q.queue.append(copy.deepcopy(self.q.queue[0]))
        del self.q.queue[0]
        self.saveQueue()
        self.window.close()
        self.setup_window()

    def saveQueue(self):
        self.get_checkboxes()
        self.q.remove_duplicates()
        self.q.saveQueue()

    def save_config_and_queue(self):
        self.get_output(force=True)
        self.saveQueue()

    def start_sorting(self):
        if self.window["output_filename"].get() == "":
            self.get_output()
        self.saveQueue()
        self.window.close()
        self.setup_window_2()
        self.event_loop2()

    def add_queue(self):
        if self.window["output_filename"].get() == "":
            self.get_output()
        self.get_output(force=True)
        self.saveQueue()
        self.q.new_config()
        self.q.queue[0] = copy.deepcopy(self.q.queue[1])
        self.window["queuelen"].update(len(self.q.queue))

    def clear_queue(self):
        self.q.queue = []
        self.q.new_config()
        self.get_output()
        self.saveQueue()
        self.clearitems()
        self.window["queuelen"].update(len(self.q.queue))

    def update_listcount(self):
        val = (
            re.sub("[^0-9]", "", self.window["listcount"].get())
            if self.window["listcount"].get() != ""
            else 0
        )
        val = min(1000000, max(0, int(val)))
        self.window["listcount"].update(val)
        self.q[0].listcount = val

    def update_listlength(self):
        val = re.sub("[^0-9, ]", "", self.window["listlength"].get()).replace(" ", "")
        self.q[0].listlength = [int(x.strip()) for x in val.split(",") if x.strip()]
        self.window["listlength"].update(
            ", ".join(map(str, self.q[0].listlength))
            + ("," if val.endswith(",") else "")
        )

    def methodevent(self):
        for key in self.q.methods.keys():
            vals = list(self.q.methods[key])
            for val in vals:
                option = f"{val}_{key}"
                selection = (
                    self.window["methods_selected"].get()[0]
                    if len(self.window["methods_selected"].get()) > 0
                    else ""
                )
                if selection == option:
                    if self.prev_method == self.window["methods_selected"].get()[0]:
                        self.q.methods[key].remove(val)
                        self.window["method_imps"].set_value(
                            [x for x in self.window["method_imps"].get() if x != val]
                        )
                        self.window["methods_selected"].update(self.q.items())
                        self.prev_method = ""
                    else:
                        self.prev_method = self.window["methods_selected"].get()[0]
                        self.window["methods_var"].set_value(
                            [
                                key,
                            ]
                        )
                    self.minevent(self.window["methods_var"].get()[0], False)
                    return self.prev_method

    def maxevent(self):
        self.q.methods[self.window["methods_var"].get()[0]] = self.window[
            "method_imps"
        ].get()
        items = []
        for key in self.q.methods.keys():
            items.extend(f"{val}_{key}" for val in self.q.methods[key])
        self.window["methods_selected"].update(items)

    def minevent(self, curr, reset=True):
        self.window["method_imps"].update(self.q.all_methods[curr])
        self.window["method_imps"].set_value(self.q.methods[curr] or [])
        if reset:
            self.window["methods_selected"].set_value([])

    def mindouble(self):
        curr_var = self.window["methods_var"].get()[0]
        if self.prev_var == curr_var:
            self.window["method_imps"].update(self.q.all_methods[curr_var])
            if self.q.all_methods[curr_var] == self.q.methods[curr_var]:
                self.window["method_imps"].set_value([])
            else:
                self.window["method_imps"].set_value(self.q.all_methods[curr_var])
            self.maxevent()
            self.prev_var = ""
        else:
            self.minevent(curr_var)
            self.prev_var = curr_var

    def get_checkboxes(self):

        self.q[0].insertion = self.window["insertion"].get()
        for cb in list(self.q.data_types.keys()):
            self.q.data_types[cb] = self.window[cb].get()
        for cb in list(self.q.data_sizes.keys()):
            self.q.data_sizes[cb] = self.window[cb].get()

    def get_filename(self, name):
        path = os.path.join("/home/will/dissertation/sort_times", f"{name}_0.json")
        uniq = 0
        while os.path.exists(path) or path in [
            x.outputFilePath for x in self.q.queue if x.outputFilePath
        ]:
            path = os.path.join(
                "/home/will/dissertation/sort_times", f"{name}_{str(uniq)}.json"
            )
            uniq += 1
        return path

    def get_output(self, force=False):
        methods = [key for key in self.q.methods.keys() if self.q.methods[key]]
        if not methods:
            return
        filename = self.window["output_filename"].get()
        if filename and force:
            path = os.path.join("/home/will/dissertation/sort_times", filename)
        else:
            method_name = "_".join(methods) if len(methods) > 1 else methods[0]
            path = self.get_filename(method_name)
        self.window["output_filename"].update(os.path.basename(path))
        self.q[0].outputFilePath = path

    def get_endPath(self, file_path):
        return os.path.basename(file_path)

    def clearitems(self):
        for key in [
            "Few Unique",
            "Sorted",
            "Reverse Sorted",
            "Nearly Sorted",
            "Random",
            "large",
            "med",
            "small",
            "tiny",
            "insertion",
        ]:
            self.window[f"{key}"].update(False)
        self.window["listlength"].update(self.q.listlength)
        self.window["listcount"].update(self.q.listcount)
        self.window["methods_var"].set_value(self.q.methodNames[0])
        self.window["method_imps"].set_value([])
        self.window["method_imps"].update(self.q.all_methods[self.q.methodNames[0]])
        self.window["methods_selected"].update([])
        self.window["output_filename"].update(self.get_endPath(self.q.outputFilePath))

    def get_commands(self, m, c):
        data_sizes = ["large", "med", "small", "tiny"]
        data_types = [
            "Few Unique",
            "Sorted",
            "Reverse Sorted",
            "Nearly Sorted",
            "Random",
        ]
        sizes = [f"{str(size)}" for size in data_sizes if not c.data_sizes[size]]     
        sizesstr = str(sizes)[1:-1].replace(",", "")
        types = [f"{str(t)}" for t in data_types if not c.data_types[t]]
        tyesstr = str(types)[
            1:-1
        ].replace(",", "")
        
        internal_lengths = [int(x) for x in c.listlength]
        if c.insertion:
            self.iters += (len(internal_lengths) * (len(data_types)-len(types)) * (len(data_sizes) -len(sizes)))*1000
        else:
            self.iters += (len(internal_lengths) * (len(data_types)-len(types)) * (len(data_sizes) -len(sizes)))*1
        # if self.q.insertion == True:
        #     self.iters *= len(list(range((internal_lengths[0]+1)//1000, internal_lengths[0]+1, (internal_lengths[0]+1)//1000)))
        lengths = str(internal_lengths)[1:-1].replace(",", "")

        methodname = re.findall(r"([^\/]+$)", m)[0]
        yield f' sort_timer_gendata_pipe.py -m {methodname} -o {c.outputFilePath} -n {c.listcount} -l {lengths} -et {tyesstr} -es {sizesstr} {"-s" if c.insertion==True else ""}'

    def get_methodCommand(self):
        methodCommand = []
        for c in self.q:
            for method in c.items():
                path = f"/home/will/dissertation/pypy_versions/{method}/bin/pypy"
                methodCommand.extend(
                    (path, command, method) for command in self.get_commands(method, c)
                )
        self.methodCommand = methodCommand

    def setup_window_2(self):
        qlen = len(self.q.queue)
        self.get_methodCommand()
        multilinecol = [
            [
                sg.Multiline(
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
                    f"{len(self.methodCommand)} items. self.q length: {qlen}",
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
            [sg.Column([[sg.Text("", key="iters")], [sg.Text("", key="elapsed")], [sg.Text("", key="remaining")]])],
        ]
        self.window2 = sg.Window(
            "Sorting Helper 2", layout2, location=(500, 500), finalize=True
        )
        for l in self.q.items():
            self.window2["completed"].print(
                str(l),
                end="\n",
                text_color="Yellow",
                autoscroll=True,
            )
        self.startTime = time.time()
        for count, (path, command, method) in enumerate(self.methodCommand, start=1):
            self.runCommand(f"{path} {command}", method, window=self.window2)

    def get_outpout(self, items, method, count):
        if match := re.match(r"(.*?\d+)+", method):
            method = match[1]
        if items[0] == "count":
            return (
                "Green",
                f"{method}\t {items[1]} {items[2]} \t {items[3]}/{items[4]}",
            )
        elif items[0] == "warming":
            return ("Cyan", f"{method}\t Warming up: \t{items[1]}/{items[2]}")
        elif items[0] == "eval":
            insr = f"{items[4]}" if items[6] == "1" else f"{count}/{items[6]}"
            return (
                "Red",
                f'{method} {items[1]} {items[2]} {items[3]} s\t{insr}\t\t {"" if items[5] else "error"}',
            )
        elif items[0] == "Total":
            return ("Purple", f"{method} Total time: {items[1]}")
        else:
            return ("White", str(items))

    def runCommand(self, cmd, method, window=None):
        p = subprocess.Popen(
            cmd, shell=True, cwd="/home/will/dissertation", stdout=subprocess.PIPE
        )
        psProcess = psutil.Process(p.pid)
        out = ""
        cont = True
        count=1
        paused = False
        while cont:
            cont = p.poll() is None
            out += p.stdout.read(1 if cont else -1).decode(
                errors="replace" if (sys.version_info) < (3, 5) else "backslashreplace"
            )
            if "\n" in out:
                for o in out.split("\n"):
                    colour, text = self.get_outpout(o.split(","), method, count)
                    if colour == "White":
                        continue
                    elif colour in ["Red", "Purple"]:
                        count+=1
                        window["completed"].print(
                            text,
                            end="\n",
                            text_color=colour,
                            autoscroll=True,
                        )
                        window["-MLINE-"].update("", append=False)
                        if colour == "Red":
                            self.count += 1
                            ctime = timedelta(seconds=time.time() - self.startTime)
                            remtime = (ctime / self.count) * (self.iters - self.count)
                            self.window2["iters"].update(
                                value=f"{self.count}/{self.iters}"
                            )
                            self.window2["elapsed"].update(value=f"Elapsed:  {self.dhm(ctime)}")
                            self.window2["remaining"].update(value=f"Remaining:  {self.dhm(remtime)}")
                            # event, values = self.window2.read(timeout=1)
                            # if event == "pause":
                            #     print('event')
                            #     if paused:
                            #         signal.pause(psProcess)
                            #         # psProcess.resume()
                            #         window['pause'].update('pause')
                            #         paused=False
                            #     elif paused==False:
                            #         signal.pause(psProcess)
                            #         # psProcess.suspend()
                            #         window['pause'].update('resume')
                            #         paused=True
                        else:
                            count=0
                    else:
                        window["-MLINE-"].update(
                            text,
                            text_color_for_value=colour,
                            append=False,
                            autoscroll=True,
                        )
                    out = out[out.find("\n") + 1 :]
            window.Refresh()

    def dhm(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours}h : {minutes}m : {seconds}s"

    def event_loop2(self):
        paused = False
        while True:
            event, values = self.window2.read()
            if event in [sg.WIN_CLOSED, "Cancel"]:
                break

                


sorting_helper_gui = SortingHelperGUI()
sorting_helper_gui.run()
