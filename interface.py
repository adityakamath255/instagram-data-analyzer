from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from analysis import ConversationAnalyzer, FollowAnalyzer
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

BG_COLOR = "#f0f0f0"
PRIMARY_COLOR = "#2196F3"
SECONDARY_COLOR = "#ffffff"
TEXT_COLOR = "#333333"
PADDING = 10

class SocialMediaAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Instagram Data Analyzer")
        self.geometry("800x600")
        self.configure(bg = BG_COLOR)
        
        self.selected_files = []
        self.setup_ui()

    def setup_ui(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.dm_tab = DMAnalysisTab(self.notebook)
        self.unfollower_tab = UnfollowerAnalysisTab(self.notebook)

        self.notebook.add(self.dm_tab, text="Direct Messages Analysis")
        self.notebook.add(self.unfollower_tab, text="Unfollower Check")

class DMAnalysisTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.message_files = []
        self.analyzer = None

    def setup_ui(self):
        self.file_frame = ttk.LabelFrame(self, text="Select Message Files", padding=PADDING)
        self.file_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)

        self.file_btn = ttk.Button(
            self.file_frame, 
            text="Choose Files", 
            command=self.select_files
        )
        self.file_btn.pack(side=tk.LEFT, padx=5)

        self.file_label = ttk.Label(self.file_frame, text="No files selected")
        self.file_label.pack(side=tk.LEFT, padx=5)

        self.analyze_frame = ttk.Frame(self)
        self.analyze_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)

        self.analyze_btn = ttk.Button(
            self.analyze_frame,
            text="Analyze Messages",
            command=self.analyze_messages,
            state=tk.DISABLED
        )
        self.analyze_btn.pack()

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Message Files",
            filetypes=[("JSON files", "*.json")]
        )
        
        if files:
            self.message_files = [Path(f) for f in files]
            self.file_label.config(text=f"{len(files)} files selected")
            self.analyze_btn.config(state=tk.NORMAL)
        else:
            self.file_label.config(text="No files selected")
            self.analyze_btn.config(state=tk.DISABLED)

    def analyze_messages(self):
        try:
            self.analyzer = ConversationAnalyzer.from_json_files(self.message_files)
            metrics = self.analyzer.get_activity_metrics()
            self.show_visualizations(metrics)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze messages: {str(e)}")

    def show_visualizations(self, metrics):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        notebook = ttk.Notebook(self.results_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        daily_fig = self._create_plot_figure(metrics['daily'], "Daily Activity", "Dates", "Messages")
        hourly_fig = self._create_plot_figure(metrics['hourly'], "Hourly Activity", "Hours", "Messages")
        monthly_fig = self._create_plot_figure(metrics['monthly'], "Monthly Activity", "Months", "Messages")

        self._add_figure_to_tab(notebook, daily_fig, "Daily Activity")
        self._add_figure_to_tab(notebook, hourly_fig, "Hourly Activity")
        self._add_figure_to_tab(notebook, monthly_fig, "Monthly Activity")

    def _create_plot_figure(self, data, title, xlabel, ylabel):
        figure = Figure(figsize=(6, 4))
        ax = figure.add_subplot(111)
        
        if data:
            x, y = zip(*sorted(data.items()))
            ax.bar(x, y)
        
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis='x', rotation=45)
        
        return figure

    def _add_figure_to_tab(self, notebook, figure, tab_name):
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=tab_name)

        canvas = FigureCanvasTkAgg(figure, master=tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

class UnfollowerAnalysisTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.following_file = None
        self.followers_file = None
        self.setup_ui()

    def setup_ui(self):
        self.following_frame = ttk.LabelFrame(self, text="Select Following File", padding=PADDING)
        self.following_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)

        self.following_btn = ttk.Button(
            self.following_frame,
            text="Choose File",
            command=self.select_following_file
        )
        self.following_btn.pack(side=tk.LEFT, padx=5)

        self.following_label = ttk.Label(self.following_frame, text="No file selected")
        self.following_label.pack(side=tk.LEFT, padx=5)

        self.followers_frame = ttk.LabelFrame(self, text="Select Followers File", padding=PADDING)
        self.followers_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)

        self.followers_btn = ttk.Button(
            self.followers_frame,
            text="Choose File",
            command=self.select_followers_file
        )
        self.followers_btn.pack(side=tk.LEFT, padx=5)

        self.followers_label = ttk.Label(self.followers_frame, text="No file selected")
        self.followers_label.pack(side=tk.LEFT, padx=5)

        self.analyze_frame = ttk.Frame(self)
        self.analyze_frame.pack(fill=tk.X, padx=PADDING, pady=PADDING)

        self.analyze_btn = ttk.Button(
            self.analyze_frame,
            text="Find Unfollowers",
            command=self.analyze_unfollowers,
            state=tk.DISABLED
        )
        self.analyze_btn.pack()

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD, height=10)
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def select_following_file(self):
        file = filedialog.askopenfilename(
            title="Select following.json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file:
            self.following_file = Path(file)
            self.following_label.config(text=self.following_file.name)
            self.check_files()

    def select_followers_file(self):
        file = filedialog.askopenfilename(
            title="Select followers.json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file:
            self.followers_file = Path(file)
            self.followers_label.config(text=self.followers_file.name)
            self.check_files()

    def check_files(self):
        if self.following_file and self.followers_file:
            self.analyze_btn.config(state=tk.NORMAL)
        else:
            self.analyze_btn.config(state=tk.DISABLED)

    def analyze_unfollowers(self):
        try:
            unfollowers = FollowAnalyzer.identify_unfollowers(
                self.following_file,
                self.followers_file
            )
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "Users who don't follow you back:\n\n")
            for user in unfollowers:
                self.results_text.insert(tk.END, f"- @{user}\n")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze unfollowers: {str(e)}")

def main():
    app = SocialMediaAnalyzer()
    app.mainloop()

if __name__ == "__main__":
    main()
