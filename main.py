import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import shutil
import subprocess
import os
import sys
import time
import ctypes
import re


ver = "v1.0.0"

here = os.path.dirname(os.path.abspath(__file__))

luau = os.path.join(here, "bin", "luau")
vortex = os.path.join(here, "bin", "vortex")
cursor = os.path.join(here, "bin", "cursor")


jsonpatterns = [
    ("kw", r'"(?:\\.|[^"\\])*"(?=\s*:)'),
    ("str", r'"(?:\\.|[^"\\])*"'),
    ("bool", r'\b(?:true|false|null)\b'),
    ("num", r'-?\b\d+\.?\d*(?:[eE][+-]?\d+)?\b'),
]

luapatterns = [
    ("com", r'--.*'),
    ("str", r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\''),
    ("kw", r'\b(?:local|function|end|if|then|else|elseif|return|for|do|in|while|repeat|until|and|or|not|break)\b'),
    ("bool", r'\b(?:true|false|nil)\b'),
    ("num", r'\b\d+\.?\d*\b'),
]


bg = "#1e1e1e"
panel = "#252526"
panel2 = "#2d2d30"
fg = "#e0e0e0"
fgdim = "#9a9a9a"
accent = "#453a5c"
accenthover = "#544874"
accentlight = "#5e4f7d"
accentdark = "#332a45"
border = "#3c3c3c"
red = "#9e67eb"


def lerp(a, b, t):
    return int(a + (b - a) * t)


def gradient(c1, c2, steps):
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)

    colors = []

    for i in range(steps):
        t = i / max(steps - 1, 1)
        r = lerp(r1, r2, t)
        g = lerp(g1, g2, t)
        b = lerp(b1, b2, t)
        colors.append(f"#{r:02x}{g:02x}{b:02x}")

    return colors


class gradientbutton(tk.Canvas):
    def __init__(self, parent, text, command, width=170, height=32, top=accentlight, bottom=accentdark):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0
        )

        self.command = command
        self.top = top
        self.bottom = bottom
        self.w = width
        self.h = height

        self.draw(top, bottom)

        self.label = self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=fg,
            font=("Segoe UI", 10)
        )

        self.bind("<Button-1>", self.click)
        self.bind("<Enter>", self.enter)
        self.bind("<Leave>", self.leave)


    def draw(self, top, bottom):
        self.delete("grad")

        colors = gradient(top, bottom, self.h)

        for i, c in enumerate(colors):
            self.create_line(
                0, i, self.w, i,
                fill=c,
                tags="grad"
            )

        self.tag_lower("grad")


    def enter(self, event):
        self.draw(accenthover, accentlight)


    def leave(self, event):
        self.draw(self.top, self.bottom)


    def click(self, event):
        self.command()


    def settext(self, text):
        self.itemconfig(self.label, text=text)


    def setcommand(self, command):
        self.command = command



class app(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True)
        self.geometry("650x530+300+150")
        self.configure(bg=bg)
        self.title("Utlitex")

        self.term = tk.BooleanVar()
        self.topmost = tk.BooleanVar(value=True)
        self.cursorprocess = None
        self.processes = []

        self.bind("<Map>", self.onrestore)
        self.protocol("WM_DELETE_WINDOW", self.closeapp)

        self.style()
        self.titlebar()
        self.make()

        self.attributes("-topmost", self.topmost.get())

        ctypes.windll.kernel32.FreeConsole()

        self.after(10, self.showintaskbar)


    def style(self):

        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(
            "TNotebook",
            background=bg,
            borderwidth=0
        )

        s.configure(
            "TNotebook.Tab",
            background=panel,
            foreground=fgdim,
            padding=(14, 6),
            borderwidth=0
        )

        s.map(
            "TNotebook.Tab",
            background=[("selected", accent)],
            foreground=[("selected", fg)]
        )

        s.layout(
            "TNotebook.Tab",
            [(
                "Notebook.tab",
                {
                    "sticky": "nswe",
                    "children": [(
                        "Notebook.padding",
                        {
                            "side": "top",
                            "sticky": "nswe",
                            "children": [(
                                "Notebook.label",
                                {"side": "top", "sticky": ""}
                            )]
                        }
                    )]
                }
            )]
        )

        s.configure(
            "TFrame",
            background=bg
        )

        s.configure(
            "TButton",
            background=accent,
            foreground=fg,
            borderwidth=0,
            focuscolor=accent,
            padding=(10, 6)
        )

        s.map(
            "TButton",
            background=[("active", accenthover)]
        )

        s.configure(
            "TCheckbutton",
            background=bg,
            foreground=fg,
            focuscolor=bg
        )

        s.map(
            "TCheckbutton",
            background=[("active", bg)],
            foreground=[("active", fg)]
        )



    def titlebar(self):

        bar = tk.Canvas(
            self,
            height=34,
            bg=panel,
            highlightthickness=0
        )

        bar.pack(
            fill="x",
            side="top"
        )

        self.after(10, lambda: self.drawbar(bar))
        bar.bind("<Configure>", lambda e: self.drawbar(bar))

        title = bar.create_text(
            14, 17,
            text="Utlitex",
            fill=fg,
            anchor="w",
            font=("Segoe UI", 11, "bold")
        )

        close = tk.Label(
            self,
            text="✕",
            bg=panel,
            fg=fgdim,
            font=("Segoe UI", 11),
            width=4
        )

        close.place(
            relx=1.0,
            x=0,
            y=0,
            anchor="ne",
            height=34
        )

        close.bind(
            "<Button-1>",
            lambda e: self.closeapp()
        )

        close.bind(
            "<Enter>",
            lambda e: close.config(bg=red, fg="#ffffff")
        )

        close.bind(
            "<Leave>",
            lambda e: close.config(bg=panel, fg=fgdim)
        )

        minb = tk.Label(
            self,
            text="—",
            bg=panel,
            fg=fgdim,
            font=("Segoe UI", 11),
            width=4
        )

        minb.place(
            relx=1.0,
            x=-40,
            y=0,
            anchor="ne",
            height=34
        )

        minb.bind(
            "<Button-1>",
            lambda e: self.minimize()
        )

        minb.bind(
            "<Enter>",
            lambda e: minb.config(bg=accenthover, fg=fg)
        )

        minb.bind(
            "<Leave>",
            lambda e: minb.config(bg=panel, fg=fgdim)
        )

        bar.bind("<ButtonPress-1>", self.startmove)
        bar.bind("<B1-Motion>", self.domove)



    def drawbar(self, bar):
        bar.delete("bggrad")

        w = bar.winfo_width()
        if w < 2:
            w = 650

        colors = gradient(accentdark, panel, w)

        for i, c in enumerate(colors):
            bar.create_line(
                i, 0, i, 34,
                fill=c,
                tags="bggrad"
            )

        bar.tag_lower("bggrad")



    def startmove(self, event):
        self.movex = event.x
        self.movey = event.y


    def domove(self, event):
        x = self.winfo_pointerx() - self.movex
        y = self.winfo_pointery() - self.movey
        self.geometry(f"+{x}+{y}")


    def toggleterminal(self):

        if self.term.get():
            ctypes.windll.kernel32.AllocConsole()
        else:
            ctypes.windll.kernel32.FreeConsole()


    def toggletopmost(self):
        self.attributes("-topmost", self.topmost.get())


    def minimize(self):
        self.overrideredirect(False)
        self.iconify()


    def closeapp(self):

        for p in self.processes:
            if p.poll() is None:
                p.kill()

        self.destroy()


    def onrestore(self, event=None):
        if self.state() == "normal":
            self.overrideredirect(True)


    def showintaskbar(self):

        gwlexstyle = -20
        wsexappwindow = 0x00040000
        wsextoolwindow = 0x00000080

        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())

        style = ctypes.windll.user32.GetWindowLongW(hwnd, gwlexstyle)
        style = style & ~wsextoolwindow
        style = style | wsexappwindow

        ctypes.windll.user32.SetWindowLongW(hwnd, gwlexstyle, style)

        self.withdraw()
        self.after(10, self.deiconify)



    def make(self):
        tabs = ttk.Notebook(self)

        home = ttk.Frame(tabs)
        luautab = ttk.Frame(tabs)
        vortextab = ttk.Frame(tabs)
        cursortab = ttk.Frame(tabs)
        settingstab = ttk.Frame(tabs)

        tabs.add(home, text="Home")
        tabs.add(luautab, text="Luau Converter")
        tabs.add(vortextab, text="Vortex Converter")
        tabs.add(cursortab, text="Custom Cursor")
        tabs.add(settingstab, text="Settings")

        tabs.pack(
            expand=True,
            fill="both"
        )


        tk.Label(
            home,
            text="Utlitex",
            bg=bg,
            fg=fg,
            font=("Segoe UI", 22, "bold")
        ).pack(pady=20)

        tk.Label(
            home,
            text=ver,
            bg=bg,
            fg=fgdim,
            font=("Segoe UI", 11)
        ).pack()


        tk.Label(
            home,
            text="Credits",
            bg=bg,
            fg=fg,
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(30, 0))

        tk.Label(
            home,
            text="Default Cursor by @friendlysmiles on Discord",
            bg=bg,
            fg=fgdim
        ).pack()

        tk.Label(
            home,
            text="coding by @nieotica on discord",
            bg=bg,
            fg=fgdim
        ).pack()



        self.makebox(
            luautab,
            "Drop model.json here",
            self.getjson
        )

        gradientbutton(
            luautab,
            "Execute",
            self.runluau
        ).pack(pady=5)


        self.out = self.makeout(luautab, "lua")



        tk.Label(
            vortextab,
            text="Experimental, do not use for final work.",
            bg=bg,
            fg=fgdim,
            font=("Segoe UI", 10)
        ).pack(pady=5)


        self.makebox(
            vortextab,
            "Drop model.rbxmx here",
            self.getvortex
        )

        gradientbutton(
            vortextab,
            "Execute",
            self.runvortex
        ).pack(pady=5)


        self.vortexout = self.makeout(vortextab, "json")



        self.makebox(
            cursortab,
            "Drop cursor file here",
            self.getcursor
        )


        self.cursorbutton = gradientbutton(
            cursortab,
            "Execute",
            self.runcursor
        )

        self.cursorbutton.pack(pady=5)


        gradientbutton(
            cursortab,
            "Reset Cursor",
            self.resetcursor
        ).pack(pady=5)



        ttk.Checkbutton(
            settingstab,
            text="Show Terminal",
            variable=self.term,
            command=self.toggleterminal
        ).pack(pady=20)

        ttk.Checkbutton(
            settingstab,
            text="Always on Top",
            variable=self.topmost,
            command=self.toggletopmost
        ).pack()



    def makeout(self, tab, lang="lua"):
        out = tk.Text(
            tab,
            bg=panel2,
            fg=fg,
            insertbackground=fg,
            relief="flat",
            highlightthickness=1,
            highlightbackground=border,
            highlightcolor=border,
            font=("Cascadia Code", 10),
            width=70,
            height=8
        )

        out.pack(
            padx=10,
            pady=10
        )

        out.lang = lang

        out.tag_configure("kw", foreground=accentlight)
        out.tag_configure("str", foreground="#ce9178")
        out.tag_configure("num", foreground="#b5cea8")
        out.tag_configure("bool", foreground=accentlight)
        out.tag_configure("com", foreground=fgdim)

        return out



    def makebox(self, tab, text, cmd):

        box = tk.Label(
            tab,
            text=text,
            bg=panel2,
            fg=fgdim,
            relief="solid",
            borderwidth=1,
            highlightbackground=border,
            width=30,
            height=3
        )

        box.pack(pady=10)


        box.bind(
            "<Button-1>",
            lambda e: cmd()
        )

        box.drop_target_register(
            DND_FILES
        )

        box.dnd_bind(
            "<<Drop>>",
            lambda e: cmd(e.data)
        )



    def getjson(self, file=None):

        if not file:
            file = filedialog.askopenfilename(
                filetypes=[("JSON", "*.json")]
            )

        if file:
            file = file.replace("{", "").replace("}", "")

            shutil.copy(
                file,
                os.path.join(
                    luau,
                    "model.json"
                )
            )



    def getvortex(self, file=None):

        if not file:
            file = filedialog.askopenfilename(
                filetypes=[("RBXMX", "*.rbxmx")]
            )

        if file:
            file = file.replace("{", "").replace("}", "")

            shutil.copy(
                file,
                os.path.join(
                    vortex,
                    "model.rbxmx"
                )
            )



    def getcursor(self, file=None):

        if not file:
            file = filedialog.askopenfilename(
                filetypes=[("Cursor files", "*.png *.gif")]
            )

        if file:
            file = file.replace("{", "").replace("}", "")

            ext = os.path.splitext(file)[1].lower()
            dest = "cursor.gif" if ext == ".gif" else "cursor.png"

            shutil.copy(
                file,
                os.path.join(cursor, dest)
            )

            stale = ["cursor.cur", "cursor.ani"]
            stale.append("cursor.png" if dest == "cursor.gif" else "cursor.gif")

            for name in stale:
                path = os.path.join(cursor, name)
                if os.path.exists(path):
                    os.remove(path)



    def resetcursor(self):

        shutil.copy(
            os.path.join(
                cursor,
                "defaultcursor.png"
            ),
            os.path.join(
                cursor,
                "cursor.png"
            )
        )

        for name in ["cursor.cur", "cursor.ani", "cursor.gif"]:
            path = os.path.join(cursor, name)
            if os.path.exists(path):
                os.remove(path)



    def runluau(self):

        self.run(
            os.path.join(
                luau,
                "convert.py"
            )
        )

        self.waitout(
            luau,
            self.out
        )



    def runvortex(self):

        self.run(
            os.path.join(
                vortex,
                "convert.py"
            )
        )

        self.waitout(
            vortex,
            self.vortexout,
            "output.json"
        )



    def highlight(self, box):

        box.tag_remove("kw", "1.0", "end")
        box.tag_remove("str", "1.0", "end")
        box.tag_remove("num", "1.0", "end")
        box.tag_remove("bool", "1.0", "end")
        box.tag_remove("com", "1.0", "end")

        content = box.get("1.0", "end-1c")
        mask = [False] * len(content)

        patterns = jsonpatterns if box.lang == "json" else luapatterns

        for tag, pattern in patterns:
            for m in re.finditer(pattern, content, re.MULTILINE):
                s, e = m.start(), m.end()

                if any(mask[s:e]):
                    continue

                for i in range(s, e):
                    mask[i] = True

                box.tag_add(tag, f"1.0+{s}c", f"1.0+{e}c")



    def waitout(self, folder, box, name="output.txt"):

        out = os.path.join(
            folder,
            name
        )

        wait = time.time() + 20

        while not os.path.exists(out):

            if time.time() > wait:
                messagebox.showerror(
                    "Error",
                    name + " not found"
                )
                return

            self.update()
            time.sleep(.1)


        with open(out, "r", encoding="utf-8") as f:
            text = f.read()


        box.delete(
            "1.0",
            tk.END
        )

        box.insert(
            tk.END,
            text
        )

        self.highlight(box)



    def runcursor(self):

        if self.cursorprocess:
            return


        file = os.path.join(
            cursor,
            "cursor.py"
        )


        flags = 0

        if not self.term.get():
            flags = subprocess.CREATE_NO_WINDOW


        self.cursorprocess = subprocess.Popen(
            [sys.executable, file],
            cwd=os.path.dirname(file),
            creationflags=flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.processes.append(self.cursorprocess)


        self.cursorbutton.settext("Stop")
        self.cursorbutton.setcommand(self.stopcursor)



    def stopcursor(self):

        if self.cursorprocess:
            self.cursorprocess.kill()
            self.cursorprocess = None


        self.cursorbutton.settext("Execute")
        self.cursorbutton.setcommand(self.runcursor)






    def run(self, file):

        flags = 0

        if not self.term.get():
            flags = subprocess.CREATE_NO_WINDOW


        p = subprocess.Popen(
            [sys.executable, file],
            cwd=os.path.dirname(file),
            creationflags=flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.processes.append(p)


app().mainloop()
