import math
import re
import tkinter as tk
from tkinter import ttk, messagebox


GRAPH_WIDTH = 600
GRAPH_HEIGHT = 600
WINDOW_WIDTH = GRAPH_WIDTH + 300
WINDOW_HEIGHT = GRAPH_HEIGHT + 50
GRAPH_X0 = 20 # the x-coordinate of the top-left corner of the graph area
GRAPH_Y0 = 40 # y coord of top-left corner of graph area
GRAPH_X1 = GRAPH_X0 + GRAPH_WIDTH # bottom right x
GRAPH_Y1 = GRAPH_Y0 + GRAPH_HEIGHT # bottom right y
BUTTON_COLOR = "#3c7ae6"
BUTTON_COLOR_2 = "#e03c3c"

class GraphCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graphing Calculator")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.statmode = False
        self.degmode = False
        self.polarmode = False

        self.view = {
            "x_min": -10.0,
            "x_max": 10.0,
            "y_min": -10.0,
            "y_max": 10.0,
        }

        user_variables = {
            "A": None,
            "B": None,
            "C": None,
            "D": None,
            "E": None,
            "F": None,
        }
        self.functions = []

        self.setup_ui()
        self.draw_graph()

    def setup_ui(self):
        self.root.configure(bg="#1f1f1f")

        top_frame = tk.Frame(self.root, bg="#232222", padx=10, pady=8)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Function:", bg="#141414", fg="white", font=("Segoe UI", 11)).pack(side="left")

        self.function_entry = tk.Entry(top_frame, width=40, font=("Segoe UI", 11))
        self.function_entry.insert(0, "sin(x)")
        self.function_entry.pack(side="left", padx=(6, 10))

        add_button = tk.Button(top_frame, text="Add", command=self.add_function, bg=BUTTON_COLOR, fg="white", relief="flat")
        add_button.pack(side="left", padx=(0, 8))

        reset_button = tk.Button(top_frame, text="Reset View", command=self.reset_view, bg=BUTTON_COLOR, fg="white", relief="flat")
        reset_button.pack(side="left", padx=(0, 8))

        zoom_in_button = tk.Button(top_frame, text="Zoom +", command=lambda: self.zoom(1.25), bg=BUTTON_COLOR, fg="white", relief="flat")
        zoom_in_button.pack(side="left", padx=(0, 8))

        zoom_out_button = tk.Button(top_frame, text="Zoom -", command=lambda: self.zoom(0.8), bg=BUTTON_COLOR, fg="white", relief="flat")
        zoom_out_button.pack(side="left", padx=(0, 8))

        left_button = tk.Button(top_frame, text="<-", command=lambda: self.pan(-0.2, 0), bg=BUTTON_COLOR, fg="white", relief="flat")
        left_button.pack(side="left", padx=(0, 4))
        right_button = tk.Button(top_frame, text="->", command=lambda: self.pan(0.2, 0), bg=BUTTON_COLOR, fg="white", relief="flat")
        right_button.pack(side="left", padx=4)
        up_button = tk.Button(top_frame, text="^", command=lambda: self.pan(0, -0.2), bg=BUTTON_COLOR, fg="white", relief="flat")
        up_button.pack(side="left", padx=4)
        down_button = tk.Button(top_frame, text="v", command=lambda: self.pan(0, 0.2), bg=BUTTON_COLOR, fg="white", relief="flat")
        down_button.pack(side="left", padx=4)

        main_area = tk.Frame(self.root, bg="#1f1f1f")
        main_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(main_area, width=GRAPH_WIDTH, height=GRAPH_HEIGHT, bg="white", highlightthickness=0, cursor="crosshair")
        self.canvas.pack(side="left", fill="both", expand=True)

        sidebar = tk.Frame(main_area, width=200, bg="#2a2a2a", padx=8, pady=8)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Functions:", bg="#2a2a2a", fg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        self.function_list = tk.Listbox(sidebar, width=22, height=22, bg="#1c1c1c", fg="white", selectbackground="#3c7ae6")
        self.function_list.pack(fill="both", expand=True)

        remove_button = tk.Button(sidebar, text="Remove Selected", command=self.remove_selected_function, bg=BUTTON_COLOR_2, fg="white", relief="flat")
        remove_button.pack(fill="x", pady=(8, 0))

        # draw the window menu bar
        self.menubar = tk.Menu(self.root)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="Import Functions", command=self.root.quit)
        file_menu.add_command(label="Export Functions", command=self.root.quit)
        file_menu.add_separator()
        file_menu.add_command(label="Exit App", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Clear Functions", command=self.clear_functions)
        edit_menu.add_command(label="Variables", command=self.open_variables_window)
        edit_menu.add_command(label="Polar / Rect", command=self.root.quit)
        edit_menu.add_command(label="Deg / Rad", command=self.root.quit)
        self.menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Zoom In", command=lambda: self.zoom(1.25))
        view_menu.add_command(label="Zoom Out", command=lambda: self.zoom(0.8))
        view_menu.add_command(label="Reset View", command=self.reset_view)
        view_menu.add_command(label="Resize Graph", command=self.root.quit)
        view_menu.add_command(label="Toggle Grid", command=self.root.quit)
        self.menubar.add_cascade(label="View", menu=view_menu)

        calc_menu = tk.Menu(self.menubar, tearoff=0)
        # each command opens a messagebox windoow giving inputs and options and then when submitted calculates the result and displays it in the main window and/or same messagebox
        calc_menu.add_command(label="Trace Function", command=self.root.quit)
        calc_menu.add_command(label="Y-Intercepts", command=self.root.quit)
        calc_menu.add_command(label="X-Intercepts", command=self.root.quit)
        calc_menu.add_command(label="Maxima / Minima", command=self.root.quit)
        calc_menu.add_command(label="Intersection", command=self.root.quit)
        calc_menu.add_command(label="Limit", command=self.root.quit)
        calc_menu.add_command(label="Derivative", command=self.root.quit)
        calc_menu.add_command(label="Integral", command=self.root.quit)
        self.menubar.add_cascade(label="Calculate", menu=calc_menu)

        table_menu = tk.Menu(self.menubar, tearoff=0)
        table_menu.add_command(label="Generate Table", command=self.root.quit)
        table_menu.add_command(label="Export Table", command=self.root.quit)
        table_menu.add_command(label="Import Table", command=self.root.quit)
        table_menu.add_command(label="Compare Functions", command=self.root.quit)
        self.menubar.add_cascade(label="Table", menu=table_menu)

        statistics_menu = tk.Menu(self.menubar, tearoff=0)
        statistics_menu.add_command(label="Scatter Plot", command=self.root.quit)
        statistics_menu.add_command(label="Regression", command=self.root.quit)
        statistics_menu.add_command(label="Correlation", command=self.root.quit)
        self.menubar.add_cascade(label="Statistics", menu=statistics_menu)

        exit_menu = tk.Menu(self.menubar, tearoff=0)
        exit_menu.add_command(label="Exit App", command=self.root.quit)
        self.menubar.add_cascade(label="Exit", menu=exit_menu)

        self.root.config(menu=self.menubar)

        # scrolling and resizing events
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel) # zoom in/out with mouse wheel
        self.canvas.bind("<ButtonPress-1>", self.start_pan) # start panning on left mouse button press
        self.canvas.bind("<B1-Motion>", self.pan_with_mouse) # pan with mouse


        self.canvas.bind("<Configure>", lambda event: self.draw_graph()) # redraw graph when window is resized. configure event is triggered when the canvas size changes

    def add_function(self):
        string = self.function_entry.get().strip()
        if string not in self.functions and string != "":
            self.functions.append(string) # internal list
            self.function_list.insert(tk.END, string) # visual list
            self.draw_graph()

    def remove_selected_function(self):
        selected_indices = self.function_list.curselection()
        if selected_indices < self.function_entry.size() and selected_indices:
            index = selected_indices[0]
            self.functions.pop(index) # internal list
            self.function_list.delete(index) # visual list
            self.draw_graph() # update graph

    def clear_functions(self):
        self.functions.clear() # internal list
        self.function_list.delete(0, tk.END) # visual list
        self.draw_graph() # update graph

    def open_variables_window(self):
        var_window = tk.Toplevel(self.root)
        var_window.title("Variables")
        var_window.geometry("300x300")
        var_window.resizable(False, False)
        var_window.configure(bg="#1f1f1f")

        tk.Label(var_window, text="Variables:", bg="#1f1f1f", fg="white", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 5), padx=10)

        variables_frame = tk.Frame(var_window, bg="#1f1f1f")
        variables_frame.pack(fill="both", expand=True, padx=10)

        self.variable_entries = {}
        for var in ["A", "B", "C", "D", "E", "F"]:
            row_frame = tk.Frame(variables_frame, bg="#1f1f1f")
            row_frame.pack(fill="x", pady=5)

            tk.Label(row_frame, text=f"{var}:", bg="#1f1f1f", fg="white", font=("Segoe UI", 11)).pack(side="left")

            entry = tk.Entry(row_frame, width=20, font=("Segoe UI", 11))
            entry.pack(side="left", padx=(5, 0))
            self.variable_entries[var] = entry

        save_button = tk.Button(var_window, text="Save Variables", command=self.save_variables, bg=BUTTON_COLOR, fg="white", relief="flat")
        save_button.pack(pady=10)

    def save_variables(self):
        for var, entry in self.variable_entries.items():
            value = entry.get().strip()
            if value:
                self.variables[var] = float(value)
            else:
                self.variables[var] = None

    def parse_function(self, funcstr, x) -> float:
        names = {
            "sin": "math.sin",
            "cos": "math.cos",
            "tan": "math.tan",
            "sqrt": "math.sqrt",
            "log": "math.log",
            "exp": "math.exp",
            "pi": "math.pi",
            "e": "math.e",
            "abs": "abs",
            "^": "**"
        }
        # replace every instance of the keys in names with their corresponding values
        pattern = r"\|(.*?)\|" # replace |x| notation first with abs(x)
        funcstr = re.sub(pattern, r"abs(\1)", funcstr)

        for key, value in names.items():
            if key in funcstr: 
                funcstr = funcstr.replace(key, value)

        funcstr = funcstr.replace("x", f"({x})") # replace x with the value of x
        # now check if x is next to a number or a closing parenthesis, if so, add a multiplication sign between them
        funcstr = re.sub(r"(\d)(\()", r"\1*\2", funcstr) # number followed by opening parenthesis
        funcstr = re.sub(r"(\))(\d)", r"\1*\2", funcstr) # closing parenthesis followed by number
        evaluated_func = eval(funcstr)
        
        return evaluated_func

    def draw_function(self, funcstr):
        width = max(self.canvas.winfo_width(), 1)
        step = (self.view["x_max"] - self.view["x_min"]) / width
        previous_point = None
        for i in range(width + 1):
            x = self.view["x_min"] + i * step
            y = self.parse_function(funcstr, x)
            if self.view["y_min"] <= y <= self.view["y_max"]:
                point = (self.map_x(x), self.map_y(y))
                if previous_point is not None:
                    self.canvas.create_line(
                        *previous_point, *point,
                        fill=self.get_color(funcstr), width=2
                    )
                previous_point = point
            else:
                previous_point = None

    def map_x(self, x): # 
        width = max(self.canvas.winfo_width() - 1, 1)
        return (x - self.view["x_min"]) / (self.view["x_max"] - self.view["x_min"]) * width # more easily thought of as ((x - xmin) / span) * width aka percentage of span that x is times width

    def map_y(self, y):
        height = max(self.canvas.winfo_height() - 1, 1)
        return (self.view["y_max"] - y) / (self.view["y_max"] - self.view["y_min"]) * height

    def get_color(self, funcstr):
        idx = self.functions.index(funcstr)
        colors = ["#e03c3c", "#3c7ae6", "#3ce03c", "#e0e03c", "#e03ce0", "#3ce0e0"]
        return colors[idx % len(colors)]

    def draw_axes(self):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        x_ticks = self.get_ticks("x", width)
        y_ticks = self.get_ticks("y", height)

        # Draw x-axis
        if self.view["y_min"] < 0 < self.view["y_max"]:
            y0 = self.map_y(0)
            self.canvas.create_line(0, y0, width, y0, fill="black", width=2)
            for x in x_ticks:
                if x != 0:
                    x_pos = self.map_x(x)
                    self.canvas.create_line(x_pos, y0 - 5, x_pos, y0 + 5, fill="black")
                    self.canvas.create_text(x_pos, y0 + 15, text=f"{x:g}", fill="black", font=("Segoe UI", 10))

        # Draw y-axis
        if self.view["x_min"] < 0 < self.view["x_max"]:
            x0 = self.map_x(0)
            self.canvas.create_line(x0, 0, x0, height, fill="black", width=2)
            for y in y_ticks:
                if y != 0:
                    y_pos = self.map_y(y)
                    self.canvas.create_line(x0 - 5, y_pos, x0 + 5, y_pos, fill="black")
                    self.canvas.create_text(x0 - 15, y_pos, text=f"{y:g}", fill="black", font=("Segoe UI", 10))

    def get_ticks(self, axis, pixel_size): # ticks are the values at which to draw grid lines and labels on the axes. This function calculates the appropriate tick values based on the current view and pixel size.
        minimum = self.view[f"{axis}_min"]
        maximum = self.view[f"{axis}_max"]
        target_spacing = 60
        raw_step = (maximum - minimum) * target_spacing / max(pixel_size, 1)
        magnitude = 10 ** math.floor(math.log10(raw_step))
        normalized_step = raw_step / magnitude
        step = next(
            (candidate * magnitude for candidate in (1, 2, 2.5, 5, 10) if candidate >= normalized_step),
            10 * magnitude,
        )
        first_tick = math.ceil(minimum / step)
        last_tick = math.floor(maximum / step)
        return [tick * step for tick in range(first_tick, last_tick + 1)]

    def draw_grid(self):
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        for x in self.get_ticks("x", width):
            if x != 0:
                x_pos = self.map_x(x)
                self.canvas.create_line(x_pos, 0, x_pos, height, fill="#e0e0e0", dash=(2, 4))
        for y in self.get_ticks("y", height):
            if y != 0:
                y_pos = self.map_y(y)
                self.canvas.create_line(0, y_pos, width, y_pos, fill="#e0e0e0", dash=(2, 4))
        

    def reset_view(self):
        self.view = {
            "x_min": -10.0,
            "x_max": 10.0,
            "y_min": -10.0,
            "y_max": 10.0,
        }
        self.draw_graph()

    def get_point_at_cursor_x(self, cursor_x): # returns the point at the cursor's x position in the graph's coordinate system. 
        graph_x = self.view["x_min"] + (cursor_x / self.canvas.winfo_width()) * (self.view["x_max"] - self.view["x_min"])
        return graph_x

    def trace_function(self, event): # only when right-click dragging. left click is for panning
        graph_x = self.get_point_at_cursor_x(event.x)
        trace_info = []
        for func in self.functions:
            try:
                y_value = self.parse_function(func, graph_x)
                if self.view["y_min"] <= y_value <= self.view["y_max"]:
                    trace_info.append(f"{func} = {y_value:.2f}")
            except Exception as e:
                trace_info.append(f"{func} = Error")
        # depending on selected function display x and y in label that follows the point on the graph.

    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def pan_with_mouse(self, event):
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        self.pan(dx / self.canvas.winfo_width(), -dy / self.canvas.winfo_height())
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom(1.25)
        else:
            self.zoom(0.8)

    def zoom(self, factor):
        x_center = (self.view["x_min"] + self.view["x_max"]) / 2
        y_center = (self.view["y_min"] + self.view["y_max"]) / 2
        x_span = (self.view["x_max"] - self.view["x_min"]) * factor
        y_span = (self.view["y_max"] - self.view["y_min"]) * factor
        self.view["x_min"] = x_center - x_span / 2
        self.view["x_max"] = x_center + x_span / 2
        self.view["y_min"] = y_center - y_span / 2
        self.view["y_max"] = y_center + y_span / 2
        self.draw_graph()

    def pan(self, dx, dy):
        x_span = self.view["x_max"] - self.view["x_min"]
        y_span = self.view["y_max"] - self.view["y_min"]
        self.view["x_min"] += dx * x_span
        self.view["x_max"] += dx * x_span
        self.view["y_min"] += dy * y_span
        self.view["y_max"] += dy * y_span
        self.draw_graph()

    def draw_graph(self):
        self.canvas.delete("all")
        self.draw_axes()
        self.draw_grid()
        for func in self.functions:
            self.draw_function(func)

    

def main():
    root = tk.Tk()
    app = GraphCalculatorApp(root)
    root.config(menu=app.menubar)
    root.mainloop()


if __name__ == "__main__":
    main()
