# user interface
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from main_page import MainPage
from plot_page import PlotPage

class Application(ThemedTk):
    def __init__(self):
        super().__init__(theme="plastick")
        self.title("Anaerobic Digestion Model Simulator") 
        self.geometry("800x750")   
        
        style = ttk.Style(self)
        background_color = '#ffffff'
        # font_set = ("Computer Modern", 11)
        style.configure('TLabel', background=background_color)
        style.configure('TEntry', fieldbackground=background_color)
        style.configure('TButton', background=background_color)
        style.configure('TRadiobutton', background=background_color)
        style.configure('TCheckbutton', background=background_color)
        style.configure('TFrame', background=background_color)
        style.configure('TLabelframe.Label', font=("Computer Modern", 12, "bold"), foreground="#005A9E")
        self.configure(background=background_color) 

        # container frame setup
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # initialize frames
        self.frames = {}
        # create pages
        # for F in (MainPage, AdvancedPageInf, AdvancedPagePara, PlotPage):
        for F in (MainPage, PlotPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

if __name__ == "__main__":
    app = Application()
    app.mainloop()