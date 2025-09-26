import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, colorchooser, simpledialog, filedialog
import time, threading, random, json, os

# ------------------------
# Settings persistence
# ------------------------
CONFIG_FILE = "win31_settings.json"

default_settings = {
    "background_color": "lightgray"
}

def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            return default_settings.copy()
    return default_settings.copy()

def save_settings():
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()

# ------------------------
# Main App
# ------------------------
root = tk.Tk()
root.title("Windows 3.1 Simulation")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())

current_frame = None
taskbar_buttons = {}

def switch_frame(new_frame):
    global current_frame
    if current_frame:
        current_frame.pack_forget()
    current_frame = new_frame
    new_frame.pack(fill="both", expand=True)

# ------------------------
# Boot -> Program Manager
# ------------------------
def start_system():
    switch_frame(second_boot_frame)
    threading.Thread(target=boot_sequence).start()

def boot_sequence():
    time.sleep(3)
    show_program_manager()

def show_program_manager():
    switch_frame(pm_frame)
    apply_settings()

# ------------------------
# Apps
# ------------------------
def open_app(app_name):
    app_win = tk.Toplevel(root)
    app_win.title(app_name)
    app_win.geometry("500x400")

    title_frame = tk.Frame(app_win)
    title_frame.pack(fill="x")

    def close_app():
        app_win.destroy()
        if app_name in taskbar_buttons:
            taskbar_buttons[app_name].destroy()
            del taskbar_buttons[app_name]

    def minimize_app():
        app_win.withdraw()
        if app_name not in taskbar_buttons:
            btn = tk.Button(taskbar, text=app_name, command=lambda: restore_app(app_name, app_win))
            btn.pack(side="left")
            taskbar_buttons[app_name] = btn

    tk.Button(title_frame, text="_", command=minimize_app).pack(side="right")
    tk.Button(title_frame, text="X", command=close_app).pack(side="right")

    # ---------------- Notepad ----------------
    if app_name == "Notepad":
        text_area = tk.Text(app_win, wrap="word")
        text_area.pack(fill="both", expand=True)

        def save_file():
            file = filedialog.asksaveasfilename(defaultextension=".txt")
            if file:
                with open(file, "w") as f:
                    f.write(text_area.get("1.0", tk.END))

        def open_file():
            file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
            if file:
                with open(file, "r") as f:
                    text_area.delete("1.0", tk.END)
                    text_area.insert(tk.END, f.read())

        menu = tk.Menu(app_win)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=open_file)
        file_menu.add_command(label="Save", command=save_file)
        menu.add_cascade(label="File", menu=file_menu)
        app_win.config(menu=menu)

    # ---------------- Paint ----------------
    elif app_name == "Paint":
        canvas = tk.Canvas(app_win, bg="white")
        canvas.pack(fill="both", expand=True)

        color = "black"

        def set_color(new_color):
            nonlocal color
            color = new_color

        def paint(event):
            x1, y1 = (event.x - 2), (event.y - 2)
            x2, y2 = (event.x + 2), (event.y + 2)
            canvas.create_oval(x1, y1, x2, y2, fill=color, outline=color)

        canvas.bind("<B1-Motion>", paint)

        color_frame = tk.Frame(app_win)
        color_frame.pack()

        for c in ["black", "red", "green", "blue", "yellow"]:
            tk.Button(color_frame, bg=c, width=3, command=lambda c=c: set_color(c)).pack(side="left")

    # ---------------- Calculator ----------------
    elif app_name == "Calculator":
        expr = tk.StringVar()

        def press(num):
            expr.set(expr.get() + str(num))

        def clear():
            expr.set("")

        def calculate():
            try:
                expr.set(str(eval(expr.get())))
            except:
                expr.set("Error")

        entry = tk.Entry(app_win, textvariable=expr, font=("Arial", 18))
        entry.pack()

        buttons = [
            ["7", "8", "9", "+"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "*"],
            ["0", "C", "=", "/"]
        ]

        for row in buttons:
            f = tk.Frame(app_win)
            f.pack()
            for b in row:
                if b == "C":
                    cmd = clear
                elif b == "=":
                    cmd = calculate
                else:
                    cmd = lambda x=b: press(x)
                tk.Button(f, text=b, width=5, height=2, command=cmd).pack(side="left")

    # ---------------- Control Panel ----------------
    elif app_name == "Control Panel":
        tk.Label(app_win, text="Control Panel", font=("Arial", 14)).pack(pady=10)

        def change_background():
            color = colorchooser.askcolor()[1]
            if color:
                settings["background_color"] = color
                apply_settings()
                save_settings()

        def system_performance():
            usage = f"CPU Usage: {random.randint(1,100)}%\nMemory Usage: {random.randint(100,8000)} MB"
            messagebox.showinfo("System Performance", usage)

        def system_info():
            info = "Microsoft Windows 3.1 Simulation\nCPU: 486DX\nRAM: 8MB\nGraphics: VGA"
            messagebox.showinfo("System Information", info)

        tk.Button(app_win, text="Change Background", command=change_background).pack(pady=5)
        tk.Button(app_win, text="System Performance", command=system_performance).pack(pady=5)
        tk.Button(app_win, text="System Information", command=system_info).pack(pady=5)

# ------------------------
# Helpers
# ------------------------
def restore_app(app_name, app_win):
    app_win.deiconify()
    taskbar_buttons[app_name].destroy()
    del taskbar_buttons[app_name]

def apply_settings():
    color = settings.get("background_color", "lightgray")
    pm_frame.configure(bg=color)
    prog_area.configure(bg=color)
    manager_area.configure(bg=color)

def exit_session():
    answer = messagebox.askyesno("Exit Windows", "Are you sure you want to exit your Windows session?")
    if answer:
        save_settings()
        root.destroy()

# ------------------------
# Boot Screen
# ------------------------
second_boot_frame = tk.Frame(root, bg="black")
boot_rect = tk.Frame(second_boot_frame, bg="lightblue", width=800, height=400)
boot_rect.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(boot_rect, text="🏳️ Windows Flag", bg="lightblue", fg="black", font=("Arial", 18)).pack(side="top", pady=10)
tk.Label(boot_rect, text="Microsoft Windows 3.1", bg="lightblue", fg="black", font=("Arial", 28)).pack(expand=True)
tk.Label(boot_rect, text="1985 - 1992", bg="lightblue", fg="black", font=("Arial", 14)).pack(side="bottom", pady=10)

# ------------------------
# Program Manager
# ------------------------
pm_frame = tk.Frame(root, bg=settings["background_color"])
tk.Label(pm_frame, text="Program Manager", font=("Arial", 18)).pack(pady=5)

prog_area = tk.Frame(pm_frame, bg=settings["background_color"])
prog_area.pack(pady=10)
tk.Button(prog_area, text="Notepad", width=20, command=lambda: open_app("Notepad")).pack(pady=5)
tk.Button(prog_area, text="Control Panel", width=20, command=lambda: open_app("Control Panel")).pack(pady=5)

tk.Label(pm_frame, text="Manager", font=("Arial", 18)).pack(pady=5)
manager_area = tk.Frame(pm_frame, bg=settings["background_color"])
manager_area.pack(pady=10)
tk.Button(manager_area, text="Calculator", width=20, command=lambda: open_app("Calculator")).pack(pady=5)
tk.Button(manager_area, text="Paint", width=20, command=lambda: open_app("Paint")).pack(pady=5)

taskbar = tk.Frame(pm_frame, bg="darkgray", height=40)
taskbar.pack(side="bottom", fill="x")

exit_button = tk.Button(taskbar, text="Exit Session", command=exit_session)
exit_button.pack(side="right")

# ------------------------
# Start
# ------------------------
start_system()
root.mainloop()
