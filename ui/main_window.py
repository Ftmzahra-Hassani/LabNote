"""Main Tkinter interface for LabNote."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from database.db_manager import DatabaseManager
from core.experiment_manager import ExperimentManager
from core.calculations import describe, linear_regression
from utils.exporters import export_experiment_csv
from ui.styles import *


class LabNoteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LabNote | Scientific Data Manager")
        self.geometry("1120x720")
        self.minsize(900, 600)
        self.configure(bg=BG)

        self.database = DatabaseManager()
        self.manager = ExperimentManager(self.database)
        self.current_page = None

        self._configure_styles()
        self._build_shell()
        self.show_dashboard()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=FONT,
                        background=CARD, fieldbackground=CARD, foreground=TEXT)
        style.configure("Treeview.Heading", font=FONT_BOLD,
                        background="#E8EDF4", foreground=TEXT)
        style.map("Treeview", background=[("selected", "#D7E8FA")],
                  foreground=[("selected", TEXT)])
        style.configure("TEntry", padding=7)
        style.configure("TCombobox", padding=6)

    def _build_shell(self):
        self.sidebar = tk.Frame(self, bg=SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="LabNote", bg=SIDEBAR, fg="white",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=22, pady=(28, 2))
        tk.Label(self.sidebar, text="SCIENTIFIC WORKSPACE", bg=SIDEBAR,
                 fg="#AAB8CC", font=("Segoe UI", 8, "bold")).pack(
                     anchor="w", padx=23, pady=(0, 32))

        self._nav_button("Dashboard", self.show_dashboard)
        self._nav_button("Experiments", self.show_experiments)
        self._nav_button("Data Analysis", self.show_analysis)

        tk.Label(self.sidebar, text="OFFLINE • PYTHON STANDARD LIBRARY",
                 bg=SIDEBAR, fg="#AAB8CC", font=("Segoe UI", 7),
                 wraplength=165, justify="left").pack(
                     side="bottom", anchor="w", padx=20, pady=22)

        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _nav_button(self, label, command):
        button = tk.Button(
            self.sidebar, text="  " + label, command=command,
            anchor="w", relief="flat", bd=0, cursor="hand2",
            bg=SIDEBAR, fg="white", activebackground=SIDEBAR_ACTIVE,
            activeforeground="white", font=FONT_BOLD, padx=18, pady=13
        )
        button.pack(fill="x", padx=10, pady=3)

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _page_heading(self, title, subtitle):
        header = tk.Frame(self.content, bg=BG)
        header.pack(fill="x", padx=30, pady=(27, 20))
        tk.Label(header, text=title, bg=BG, fg=TEXT,
                 font=FONT_TITLE).pack(anchor="w")
        tk.Label(header, text=subtitle, bg=BG, fg=MUTED,
                 font=FONT).pack(anchor="w", pady=(5, 0))

    def _card(self, parent, title, value):
        card = tk.Frame(parent, bg=CARD, highlightbackground=GRID,
                        highlightthickness=1, padx=18, pady=16)
        tk.Label(card, text=title.upper(), bg=CARD, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(card, text=str(value), bg=CARD, fg=TEXT,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(8, 0))
        return card

    def _primary_button(self, parent, text, command):
        return tk.Button(
            parent, text=text, command=command, bg=ACCENT, fg="white",
            activebackground=ACCENT_DARK, activeforeground="white",
            relief="flat", bd=0, padx=14, pady=8, cursor="hand2",
            font=FONT_BOLD
        )

    def show_dashboard(self):
        self._clear_content()
        self._page_heading("Dashboard", "Overview of your scientific workspace")
        summary = self.database.get_dashboard_summary()

        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x", padx=30)
        for title, value in [
            ("Experiments", summary["experiments"]),
            ("Measurements", summary["measurements"]),
            ("Latest experiment", summary["latest"]),
        ]:
            card = self._card(cards, title, value)
            card.pack(side="left", fill="both", expand=True, padx=(0, 12))

        panel = tk.Frame(self.content, bg=CARD, highlightbackground=GRID,
                         highlightthickness=1, padx=22, pady=20)
        panel.pack(fill="both", expand=True, padx=30, pady=22)
        tk.Label(panel, text="Recent experiments", bg=CARD, fg=TEXT,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 12))

        tree = self._experiment_tree(panel, height=9)
        tree.pack(fill="both", expand=True)
        for item in self.database.get_experiments()[:8]:
            tree.insert("", "end", values=(
                item["id"], item["title"], item["created_at"],
                item["measurement_count"]
            ))

    def _experiment_tree(self, parent, height=12):
        columns = ("id", "title", "created", "count")
        tree = ttk.Treeview(parent, columns=columns, show="headings",
                            height=height)
        headings = {
            "id": ("ID", 55), "title": ("Experiment", 280),
            "created": ("Created", 160), "count": ("Measurements", 120)
        }
        for key, (heading, width) in headings.items():
            tree.heading(key, text=heading)
            tree.column(key, width=width, anchor="w")
        return tree

    def show_experiments(self):
        self._clear_content()
        self._page_heading("Experiments", "Create, organize, and manage measurements")

        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", padx=30, pady=(0, 12))

        search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=search_var, width=30)
        search_entry.pack(side="left", ipady=3)
        tk.Label(toolbar, text="Search by title", bg=BG, fg=MUTED).pack(
            side="left", padx=9
        )

        tree = self._experiment_tree(self.content)
        tree.pack(fill="both", expand=True, padx=30, pady=(0, 12))

        actions = tk.Frame(self.content, bg=BG)
        actions.pack(fill="x", padx=30, pady=(0, 25))

        def refresh(*_):
            tree.delete(*tree.get_children())
            for item in self.database.get_experiments(search_var.get().strip()):
                tree.insert("", "end", values=(
                    item["id"], item["title"], item["created_at"],
                    item["measurement_count"]
                ))

        def selected_id():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Select experiment", "Choose an experiment first.")
                return None
            return int(tree.item(selection[0], "values")[0])

        def add():
            self._experiment_dialog(refresh)

        def edit():
            experiment_id = selected_id()
            if experiment_id is not None:
                self._experiment_dialog(refresh, experiment_id)

        def measurements():
            experiment_id = selected_id()
            if experiment_id is not None:
                self._measurement_dialog(experiment_id, refresh)

        def delete():
            experiment_id = selected_id()
            if experiment_id is None:
                return
            if messagebox.askyesno(
                "Delete experiment",
                "Delete this experiment and all its measurements?"
            ):
                self.database.delete_experiment(experiment_id)
                refresh()

        def export():
            experiment_id = selected_id()
            if experiment_id is None:
                return
            experiment = self.database.get_experiment(experiment_id)
            measurements_list = self.database.get_measurements(experiment_id)
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile="experiment_data.csv"
            )
            if path:
                export_experiment_csv(experiment, measurements_list, path)
                messagebox.showinfo("Export complete", "CSV file exported successfully.")

        self._primary_button(actions, "＋ New Experiment", add).pack(side="left", padx=(0, 8))
        tk.Button(actions, text="Edit", command=edit).pack(side="left", padx=4)
        tk.Button(actions, text="Measurements", command=measurements).pack(side="left", padx=4)
        tk.Button(actions, text="Delete", command=delete).pack(side="left", padx=4)
        tk.Button(actions, text="Export CSV", command=export).pack(side="left", padx=4)

        search_var.trace_add("write", refresh)
        refresh()

    def _experiment_dialog(self, refresh, experiment_id=None):
        existing = self.database.get_experiment(experiment_id) if experiment_id else None
        dialog = tk.Toplevel(self)
        dialog.title("Edit experiment" if existing else "New experiment")
        dialog.geometry("440x330")
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Experiment title", bg=BG, fg=TEXT,
                 font=FONT_BOLD).pack(anchor="w", padx=22, pady=(22, 5))
        title_var = tk.StringVar(value=existing["title"] if existing else "")
        title_entry = ttk.Entry(dialog, textvariable=title_var)
        title_entry.pack(fill="x", padx=22)

        tk.Label(dialog, text="Description", bg=BG, fg=TEXT,
                 font=FONT_BOLD).pack(anchor="w", padx=22, pady=(15, 5))
        description = tk.Text(dialog, height=5, font=FONT, wrap="word")
        description.pack(fill="both", expand=True, padx=22)
        if existing:
            description.insert("1.0", existing["description"])

        def save():
            try:
                if existing:
                    self.manager.update(
                        experiment_id, title_var.get(),
                        description.get("1.0", "end").strip()
                    )
                else:
                    self.manager.create(
                        title_var.get(), description.get("1.0", "end").strip()
                    )
            except ValueError as error:
                messagebox.showerror("Invalid data", str(error), parent=dialog)
                return
            dialog.destroy()
            refresh()

        self._primary_button(dialog, "Save experiment", save).pack(
            anchor="e", padx=22, pady=18
        )
        title_entry.focus_set()

    def _measurement_dialog(self, experiment_id, refresh_parent=None):
        experiment = self.database.get_experiment(experiment_id)
        dialog = tk.Toplevel(self)
        dialog.title(f"Measurements | {experiment['title']}")
        dialog.geometry("720x520")
        dialog.configure(bg=BG)
        dialog.transient(self)

        tk.Label(dialog, text=experiment["title"], bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=15)

        form = tk.Frame(dialog, bg=BG)
        form.pack(fill="x", padx=20)

        label_var = tk.StringVar()
        x_var = tk.StringVar()
        y_var = tk.StringVar()

        for column, (label, variable) in enumerate([
            ("Label", label_var), ("X value", x_var), ("Y value", y_var)
        ]):
            block = tk.Frame(form, bg=BG)
            block.grid(row=0, column=column, sticky="ew", padx=(0, 10))
            tk.Label(block, text=label, bg=BG, fg=MUTED).pack(anchor="w")
            ttk.Entry(block, textvariable=variable).pack(fill="x", pady=5)
            form.grid_columnconfigure(column, weight=1)

        tree = ttk.Treeview(dialog, columns=("id", "label", "x", "y"),
                            show="headings", height=11)
        for key, heading, width in [
            ("id", "ID", 55), ("label", "Label", 220),
            ("x", "X value", 150), ("y", "Y value", 150)
        ]:
            tree.heading(key, text=heading)
            tree.column(key, width=width, anchor="w")
        tree.pack(fill="both", expand=True, padx=20, pady=12)

        def refresh():
            tree.delete(*tree.get_children())
            for item in self.database.get_measurements(experiment_id):
                tree.insert("", "end", values=(
                    item["id"], item["label"], item["x_value"], item["y_value"]
                ))

        def add():
            try:
                self.manager.add_measurement(
                    experiment_id, label_var.get(), x_var.get(), y_var.get()
                )
            except ValueError as error:
                messagebox.showerror("Invalid measurement", str(error), parent=dialog)
                return
            label_var.set("")
            x_var.set("")
            y_var.set("")
            refresh()
            if refresh_parent:
                refresh_parent()

        def delete():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Select row", "Choose a measurement first.")
                return
            measurement_id = int(tree.item(selection[0], "values")[0])
            self.database.delete_measurement(measurement_id)
            refresh()
            if refresh_parent:
                refresh_parent()

        buttons = tk.Frame(dialog, bg=BG)
        buttons.pack(fill="x", padx=20, pady=(0, 18))
        self._primary_button(buttons, "Add measurement", add).pack(side="left")
        tk.Button(buttons, text="Delete selected", command=delete).pack(side="left", padx=8)
        refresh()

    def show_analysis(self):
        self._clear_content()
        self._page_heading("Data Analysis", "Descriptive statistics and linear regression")

        experiments = self.database.get_experiments()
        if not experiments:
            tk.Label(self.content, text="Create an experiment and add measurements to begin.",
                     bg=BG, fg=MUTED, font=FONT).pack(pady=60)
            return

        selector = tk.Frame(self.content, bg=BG)
        selector.pack(fill="x", padx=30, pady=(0, 15))
        tk.Label(selector, text="Select experiment:", bg=BG, fg=TEXT,
                 font=FONT_BOLD).pack(side="left")
        options = {f"{item['id']} — {item['title']}": item["id"] for item in experiments}
        selected = tk.StringVar(value=next(iter(options)))
        combo = ttk.Combobox(selector, textvariable=selected,
                             values=list(options), state="readonly", width=38)
        combo.pack(side="left", padx=10)

        result_panel = tk.Frame(self.content, bg=CARD, highlightbackground=GRID,
                                highlightthickness=1, padx=20, pady=18)
        result_panel.pack(fill="x", padx=30, pady=8)

        chart_panel = tk.Frame(self.content, bg=CARD, highlightbackground=GRID,
                               highlightthickness=1, padx=15, pady=12)
        chart_panel.pack(fill="both", expand=True, padx=30, pady=15)

        def analyze(*_):
            for child in result_panel.winfo_children():
                child.destroy()
            for child in chart_panel.winfo_children():
                child.destroy()

            experiment_id = options[selected.get()]
            rows = self.database.get_measurements(experiment_id)
            if not rows:
                tk.Label(result_panel, text="No measurements available.",
                         bg=CARD, fg=MUTED).pack(anchor="w")
                return

            x_values = [float(row["x_value"]) for row in rows]
            y_values = [float(row["y_value"]) for row in rows]
            y_stats = describe(y_values)

            tk.Label(result_panel, text="Y VALUE SUMMARY", bg=CARD, fg=MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            summary = (
                f"Count: {y_stats['count']}     "
                f"Mean: {y_stats['mean']:.4f}     "
                f"Median: {y_stats['median']:.4f}     "
                f"Std. deviation: {y_stats['stdev']:.4f}"
            )
            tk.Label(result_panel, text=summary, bg=CARD, fg=TEXT,
                     font=FONT).pack(anchor="w", pady=8)

            try:
                fit = linear_regression(x_values, y_values)
                fit_text = (
                    f"Linear model: y = {fit['slope']:.5f}x "
                    f"+ {fit['intercept']:.5f}     "
                    f"R² = {fit['r_squared']:.5f}"
                )
                tk.Label(result_panel, text=fit_text, bg=CARD, fg=ACCENT,
                         font=FONT_BOLD).pack(anchor="w")
                self._draw_chart(chart_panel, x_values, y_values, fit)
            except ValueError as error:
                tk.Label(result_panel, text=str(error), bg=CARD,
                         fg=DANGER).pack(anchor="w")

        combo.bind("<<ComboboxSelected>>", analyze)
        self._primary_button(selector, "Analyze", analyze).pack(side="left", padx=5)
        analyze()

    def _draw_chart(self, parent, x_values, y_values, fit):
        """Draw a scatter plot and regression line using Tkinter Canvas."""
        canvas = tk.Canvas(parent, bg=CARD, highlightthickness=0, height=300)
        canvas.pack(fill="both", expand=True)

        width, height = 650, 280
        left, right, top, bottom = 55, 25, 20, 42
        plot_width = width - left - right
        plot_height = height - top - bottom

        x_min, x_max = min(x_values), max(x_values)
        y_min, y_max = min(y_values), max(y_values)
        y_fit = [fit["slope"] * x + fit["intercept"] for x in x_values]
        y_min = min(y_min, min(y_fit))
        y_max = max(y_max, max(y_fit))

        if x_min == x_max:
            x_min -= 1
            x_max += 1
        if y_min == y_max:
            y_min -= 1
            y_max += 1

        def point(x, y):
            px = left + (x - x_min) / (x_max - x_min) * plot_width
            py = top + plot_height - (y - y_min) / (y_max - y_min) * plot_height
            return px, py

        canvas.create_line(left, top, left, top + plot_height, fill=MUTED)
        canvas.create_line(left, top + plot_height, left + plot_width,
                           top + plot_height, fill=MUTED)
        for step in range(5):
            y = top + step * plot_height / 4
            canvas.create_line(left, y, left + plot_width, y,
                               fill="#E9EDF2", dash=(2, 3))
        canvas.create_text(left + plot_width / 2, height - 8,
                           text="X values", fill=MUTED)
        canvas.create_text(15, top + plot_height / 2,
                           text="Y", fill=MUTED, angle=90)

        # Draw regression line between the smallest and largest X values.
        line_start = point(x_min, fit["slope"] * x_min + fit["intercept"])
        line_end = point(x_max, fit["slope"] * x_max + fit["intercept"])
        canvas.create_line(*line_start, *line_end, fill=ACCENT, width=2)

        for x, y in zip(x_values, y_values):
            px, py = point(x, y)
            canvas.create_oval(px - 5, py - 5, px + 5, py + 5,
                               fill="#E58B36", outline="white", width=1)


if __name__ == "__main__":
    LabNoteApp().mainloop()
