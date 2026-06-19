# main page design for user interface
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import pandas as pd
import os

from adm1_runfile import adm1_run
from plot_page import PlotPage

import traceback
from dataclasses import asdict
from ad_influent import influent
from ad_initial_conditions import initial
from chara_page import AdvancedCharacterizationWindow


class TopSectionFrame(tk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.configure(background="#00A6D6")
        self.name_label = tk.Label(
            self, 
            text=title, 
            font=("Segoe UI", 14, "bold"), 
            fg="white", 
            background='#00A6D6'
        )
        self.name_label.grid(row=0, column=0, padx=20, pady=10, sticky='e')
        self.grid_columnconfigure(0, weight=1)

class NavigationFrame(tk.Frame):
    def __init__(self, parent, run_command, plot_command, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.configure(background='#00A6D6', highlightbackground='#00A6D6', highlightthickness=1.5)
        self.grid(row=35, column=0, sticky='ew', columnspan=parent.grid_size()[0])
        # buttons
        self.run_button = ttk.Button(self, text="Run Model", command=run_command)
        self.run_button.grid(row=0, column=1, sticky='e', padx=(10, 10), pady=10)

        self.plot_button = ttk.Button(self, text="Generate Plots", command=plot_command)
        self.plot_button.grid(row=0, column=2, sticky='e', padx=(0, 20), pady=10)

        # configure the grid within NavigationFrame to align the buttons properly
        self.grid_columnconfigure(0, weight=1)  
        self.grid_columnconfigure(1, weight=0) 
        self.grid_columnconfigure(2, weight=0)

class ToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self):
        "Display text in tooltip window"

        if self.tipwindow or not self.text:
            return
        
        self.x, self.y, cx, cy = self.widget.bbox("insert")
        self.x += self.widget.winfo_rootx() + 25
        self.y += self.widget.winfo_rooty() + 20

        self.tipwindow = tk.Toplevel(self.widget)

        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry("+%d+%d" % (self.x, self.y))

        label = tk.Label(self.tipwindow, text=self.text, justify=tk.LEFT,
                      background="#ffffff", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None
        
def create_tooltip(widget, text):
        tool_tip = ToolTip(widget, text)
        widget.bind('<Enter>', lambda event: tool_tip.show_tip())
        widget.bind('<Leave>', lambda event: tool_tip.hide_tip())
        widget.bind('<ButtonPress>', lambda event: tool_tip.hide_tip()) 
        widget.bind('<FocusOut>', lambda event: tool_tip.hide_tip())

class MainPage(ttk.Frame):

    def setup_scrollable_area(self):
        # Create the main container frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0, background='#ffffff')
        self.canvas.grid(row=0, column=0, sticky='nsew')

        self.v_scrollbar = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky='ns')

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        self.canvas.bind('<Configure>', self.on_canvas_configure)
        self.inner_frame.bind('<Configure>', self.on_frame_configure)

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def validate_integer(self, P):
        if P == "": return True
        if P.isdigit():
            return True
        else:
            self.bell() 
            return False
        
    def validate_float(self, P):
        if P == "": return True
        try: 
            value = float(P)
            if value >= 0 : return True
            else: return False
        except ValueError:
            self.bell()  
            return False
        
    def on_next_button(self):
        AdvancedCharacterizationWindow(self)

    def on_param_adaptation(self):
        mb.showinfo("Info", "Parameters Adaptation and Uncertainty features coming soon!")
        
    def run_model(self):
        model_mode = self.model_mode_var.get()
        ph_mode = self.ph_mode_var.get()
        temp_str = self.temp_var.get()
        temp = 35 if temp_str == "Mesophilic" else 55
        time = self.sim_time_var.get()
        kinetics_mode = self.kinetics_mode_var.get()

        try:
            u = float(self.inflow_var.get())
            v_liq = float(self.liq_vol_var.get())
            v_gas = float(self.gas_vol_var.get())
            carbo = float(self.carbo_var.get())
            lipid = float(self.lipid_var.get())
            protein = float(self.protein_var.get())
            sol_ox = float(self.sol_ox_var.get())
            
            influent_ph = float(self.influent_ph_var.get())
            Hion = 10**(-influent_ph)
            
        except ValueError:
            mb.showerror("Input Error", "Please ensure all fields contain valid numbers.")
            return  

        t_simulation = [time, 0.1]                                
        operational_para = [v_gas, v_liq]  
        influent_corr = [carbo, lipid, protein, sol_ox, Hion] 
        
        if temp == 35:
            para_corr = [10.0, 10.0, 10.0, 30.0, 50.0, 6.0, 20.0, 13.0, 8.0]
        else:
            para_corr = [10.0, 10.0, 10.0, 70.0, 70.0, 10.0, 30.0, 20.0, 16.0]


        try:
            # Generate default filename (e.g., ADM1_Mesophilic.xlsx or Batch_(BMP)_Thermophilic.xlsx)
            # clean_model_name = model_mode.replace(" ", "_")
            # default_filename = f"{clean_model_name}-{temp_str}.xlsx"

            # filepath = fd.asksaveasfilename(
            #     initialfile=default_filename,
            #     defaultextension=".xlsx",
            #     filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            #     title="Save Results As"
            # )
            
            # if not filepath:
            #     return 

            # Run the actual model
            t, outputs, gas_flow, inhibitions, sh_all = adm1_run(
                model_mode, ph_mode, temp, kinetics_mode, 
                t_simulation, u, operational_para, influent_corr, para_corr)

            # Prepare the DataFrames for the 3 sheets
            # Results
            df_results = pd.DataFrame({"Time_days": t})
            df_results["pH"] = sh_all
            for key, val in outputs.items(): df_results[key] = val
            for key, val in gas_flow.items(): df_results[f"GasFlow_{key}"] = val
            for key, val in inhibitions.items(): df_results[f"Inhib_{key}"] = val

            # Initial Conditions 
            df_initial = pd.DataFrame([asdict(initial())]).T.reset_index()
            df_initial.columns = ['Parameter', 'Value']

            # Influents 
            df_influent = pd.DataFrame([asdict(influent())]).T.reset_index()
            df_influent.columns = ['Parameter', 'Value']

            temp_filepath = os.path.join(os.getcwd(), "temp_simulation_results.xlsx")
            with pd.ExcelWriter(temp_filepath) as writer:
                df_results.to_excel(writer, sheet_name='Results', index=False)
                df_initial.to_excel(writer, sheet_name='Initial Conditions', index=False)
                df_influent.to_excel(writer, sheet_name='Influents', index=False)

            clean_model_name = model_mode.replace(" ", "_")
            default_filename = f"{clean_model_name}_{temp_str}.xlsx"

            self.controller.frames["PlotPage"].set_excel_file(temp_filepath, default_filename)

            mb.showinfo("Success", "Simulation complete!\nClick 'Generate Plots' below to view and download the results.")
        except Exception as e:
            traceback.print_exc()
            mb.showerror("Simulation Error", f"A technical error occurred during the simulation. Please check your terminal for the detailed traceback.\n\nBrief Error: {str(e)}")
        
    def on_config_change(self, event=None):
        # Handle Constant pH visibility
        # if self.ph_mode_var.get() == "Constant":
        #     self.custom_ph_label.grid(row=5, column=2, padx=(30, 10), pady=10, sticky='w')
        #     self.custom_ph_entry.grid(row=5, column=3, sticky='w')
        #     create_tooltip(self.custom_ph_entry, "Enter specific pH value (e.g., 7.0)")
        # else:
        #     self.custom_ph_label.grid_remove()
        #     self.custom_ph_entry.grid_remove()

        # Handle Soluble Oxygen active/disabled state
        # We also disable the label so it greys out visually!
        if self.model_mode_var.get() == "ADM1Ox":
            self.sol_ox_label.configure(state='normal')
            self.sol_ox_entry.configure(state='normal')
        else:
            self.sol_ox_label.configure(state='disabled')
            self.sol_ox_entry.configure(state='disabled')

        if self.model_mode_var.get() == "Batch (BMP)":
            if "PlotPage" in self.controller.frames:
                self.controller.frames["PlotPage"].chk_cum_var.set(True)
                self.controller.frames["PlotPage"].chk_cum.config(state="normal")
            # Set the default Batch values
            self.sim_time_var.set(35)
            self.inflow_var.set("0.0")
            self.liq_vol_var.set("0.4")
            self.gas_vol_var.set("0.15")
            self.carbo_var.set("0.0")
            self.lipid_var.set("0.0")
            self.protein_var.set("0.0")
            # Lock the inflow entry so the user can't change it
            self.inflow_entry.configure(state='disabled')
            self.carb_entry.configure(state='disabled')
            self.lip_entry.configure(state='disabled')
            self.pr_entry.configure(state='disabled')
        else:
            if "PlotPage" in self.controller.frames:
                self.controller.frames["PlotPage"].chk_cum_var.set(False)
                self.controller.frames["PlotPage"].chk_cum.config(state="disabled")
            # Unlock the inflow entry if they switch back to ADM1 or ADM1Ox
            self.sim_time_var.set(50)
            self.inflow_var.set("170.0")
            self.liq_vol_var.set("3400.0")
            self.gas_vol_var.set("400.0")
            self.carbo_var.set("5.0")
            self.lipid_var.set("5.0")
            self.protein_var.set("20.0")
            self.inflow_entry.configure(state='normal')
            self.carb_entry.configure(state='normal')
            self.lip_entry.configure(state='normal')
            self.pr_entry.configure(state='normal')

        if self.model_mode_var.get() == "Start-up":
            self.kinetics_mode_var.set("Varying")
            self.kinetics_radio1.configure(state='disabled')
            self.kinetics_radio2.configure(state='disabled')
        else:
            self.kinetics_mode_var.set("Constant")
            self.kinetics_radio1.configure(state='normal')
            self.kinetics_radio2.configure(state='normal')


    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=0)  
        self.grid_rowconfigure(1, weight=1)  
        self.grid_rowconfigure(2, weight=0)  
        self.grid_columnconfigure(0, weight=1)

        self.top_section = TopSectionFrame(self, "TU Delft")
        self.top_section.grid(row=0, column=0, columnspan=4, sticky='ew')

        self.setup_scrollable_area()

        self.nav_frame = NavigationFrame(self, 
                                         run_command=self.run_model,
                                         plot_command=lambda: self.controller.show_frame("PlotPage"))
        self.nav_frame.grid(row=30, column=0, columnspan=4, sticky='ew')

        self.subtitle_font = tkFont.Font(family="Segoe UI", size=11, weight="bold")

        # model configuration
        self.title_label = ttk.Label(self.inner_frame, text="1. Model Configuration", font=self.subtitle_font, style='TLabel')
        self.title_label.grid(row=1, column=0, columnspan=2, padx=10, pady=(15, 5), sticky='w')

        self.model_mode_var = tk.StringVar(value="ADM1")
        self.ph_mode_var = tk.StringVar(value="Differential")
        self.kinetics_mode_var = tk.StringVar(value="Constant")
        self.temp_var = tk.StringVar(value="Mesophilic")

        # model version
        ttk.Label(self.inner_frame, text="Process model:", anchor='w').grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.model_cb = ttk.Combobox(self.inner_frame, textvariable=self.model_mode_var, values=["ADM1", "ADM1Ox", "Batch (BMP)", "Start-up"], state="readonly")
        self.model_cb.grid(row=3, column=1, sticky='w')
        self.model_cb.bind("<<ComboboxSelected>>", self.on_config_change)
        create_tooltip(self.model_cb, "Select a process model for anaerobic digestion")

        # pH calculation method
        ttk.Label(self.inner_frame, text="pH calculation method:", anchor='w').grid(row=4, column=0, padx=10, pady=10, sticky='w')
        self.ph_cb = ttk.Combobox(self.inner_frame, textvariable=self.ph_mode_var, values=["Differential", "Algebraic", "Constant"], state="readonly")
        self.ph_cb.grid(row=4, column=1, sticky='w')
        # self.ph_cb.bind("<<ComboboxSelected>>", self.on_config_change)
        create_tooltip(self.ph_cb, "Select the mathematical approach for pH calculation")

        # temperature condition
        ttk.Label(self.inner_frame, text="Temperature regime:", anchor='w').grid(row=5, column=0, padx=10, pady=10, sticky='w')
        self.temp_cb = ttk.Combobox(self.inner_frame, textvariable=self.temp_var, values=["Mesophilic", "Thermophilic"], state="readonly")
        self.temp_cb.grid(row=5, column=1, sticky='w')
        create_tooltip(self.temp_cb, "Select the operating temperature of the digester")

        # simulation run time
        ttk.Label(self.inner_frame, text="Simulation run time [Days]:", anchor='w',style='TLabel').grid(row=6, column=0, padx=10, pady=10, sticky='w')
        self.sim_time_var = tk.IntVar(value=50)
        vcmd = (self.register(self.validate_integer), '%P')
        self.time_cb = ttk.Entry(self.inner_frame, textvariable=self.sim_time_var, validate='key', validatecommand=vcmd)
        self.time_cb.grid(row=6, column=1, sticky='w')
        create_tooltip(self.time_cb, "Enter the duration of the simulation in days")

        separator_1 = ttk.Separator(self.inner_frame, orient='horizontal')
        separator_1.grid(row=7, column=0, columnspan=4, sticky='ew', padx=10, pady=15)

        # Influent & Operational Parameters
        self.title_label = ttk.Label(self.inner_frame, text="2. Operational Parameters & Influent Characterization", font=self.subtitle_font)
        self.title_label.grid(row=8, column=0, columnspan=2, padx=10, pady=(10, 5), sticky='w')

        self.sec2_frame = ttk.Frame(self.inner_frame)
        self.sec2_frame.grid(row=9, column=0, columnspan=4, sticky='w', padx=10, pady=10)

        vcmd_float = (self.register(self.validate_float), '%P')

        # Define the Variables
        self.inflow_var      = tk.StringVar(value="170.0")
        self.liq_vol_var     = tk.StringVar(value="3400.0")
        self.gas_vol_var     = tk.StringVar(value="300.0")
        self.carbo_var       = tk.StringVar(value="5.0")
        self.lipid_var       = tk.StringVar(value="5.0")
        self.protein_var     = tk.StringVar(value="20.0")
        self.influent_ph_var = tk.StringVar(value="7.097")
        self.sol_ox_var      = tk.StringVar(value="1")

        # Inflow, Liquid Vol, Gas Vol
        ttk.Label(self.sec2_frame, text="Inflow rate [m³/d]:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.inflow_entry = ttk.Entry(self.sec2_frame, textvariable=self.inflow_var, width=12, validate='key', validatecommand=vcmd_float)
        self.inflow_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.sec2_frame, text="Liquid volume [m³]:").grid(row=0, column=2, padx=(20, 5), pady=5, sticky='w')
        ttk.Entry(self.sec2_frame, textvariable=self.liq_vol_var, width=12, validate='key', validatecommand=vcmd_float).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(self.sec2_frame, text="Gas volume [m³]:").grid(row=0, column=4, padx=(20, 5), pady=5, sticky='w')
        ttk.Entry(self.sec2_frame, textvariable=self.gas_vol_var, width=12, validate='key', validatecommand=vcmd_float).grid(row=0, column=5, padx=5, pady=5)

        # Row 2: Carbohydrate, Lipid, Protein
        ttk.Label(self.sec2_frame, text="Carbohydrate [kgCOD/m³]:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.carb_entry = ttk.Entry(self.sec2_frame, textvariable=self.carbo_var, width=12, validate='key', validatecommand=vcmd_float)
        self.carb_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.sec2_frame, text="Lipid [kgCOD/m³]:").grid(row=1, column=2, padx=(20, 5), pady=5, sticky='w')
        self.lip_entry = ttk.Entry(self.sec2_frame, textvariable=self.lipid_var, width=12, validate='key', validatecommand=vcmd_float)
        self.lip_entry.grid(row=1, column=3, padx=5, pady=5) 

        ttk.Label(self.sec2_frame, text="Protein [kgCOD/m³]:").grid(row=1, column=4, padx=(20, 5), pady=5, sticky='w')
        self.pr_entry = ttk.Entry(self.sec2_frame, textvariable=self.protein_var, width=12, validate='key', validatecommand=vcmd_float)
        self.pr_entry.grid(row=1, column=5, padx=5, pady=5)

        # pH, Soluble Oxygen
        ttk.Label(self.sec2_frame, text="pH:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(self.sec2_frame, textvariable=self.influent_ph_var, width=12, validate='key', validatecommand=vcmd_float).grid(row=2, column=1, padx=5, pady=5)

        self.sol_ox_label = ttk.Label(self.sec2_frame, text="Soluble Oxygen [mg/L]:")
        self.sol_ox_label.grid(row=2, column=2, padx=(20, 5), pady=5, sticky='w')
        self.sol_ox_entry = ttk.Entry(self.sec2_frame, textvariable=self.sol_ox_var, width=12, validate='key', validatecommand=vcmd_float)
        self.sol_ox_entry.grid(row=2, column=3, padx=5, pady=5)

        # Advanced Features Frame
        self.advanced_frame = ttk.Frame(self.inner_frame)
        self.advanced_frame.grid(row=10, column=0, padx=10, pady=10, sticky='w')

        self.advanced_button = ttk.Button(self.advanced_frame, text="Advanced Characterization", command=self.on_next_button)
        self.advanced_button.grid(row=0, column=0, padx=5, pady=5)

        separator_2 = ttk.Separator(self.inner_frame, orient='horizontal')
        separator_2.grid(row=11, column=0, columnspan=4, sticky='ew', padx=10, pady=15)

        # Create a Sub-Frame for Section 3 to keep it organized
        self.title_label = ttk.Label(self.inner_frame, text="3. Kinetic Parameters", font=self.subtitle_font)
        self.title_label.grid(row=12, column=0, columnspan=2, padx=10, pady=(10, 5), sticky='w')

        self.sec3_frame = ttk.Frame(self.inner_frame)
        self.sec3_frame.grid(row=13, column=0, columnspan=4, sticky='w', padx=10, pady=(0, 10))

        # Kinetics Rate Radiobuttons
        self.kinetics_mode_var = tk.StringVar(value="Constant")
        ttk.Label(self.sec3_frame, text="Kinetics Parameters:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.kinetics_radio1 = ttk.Radiobutton(self.sec3_frame, text="Constant", variable=self.kinetics_mode_var, value="Constant")
        self.kinetics_radio1.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        # The text says 'Dynamic', but the backend model expects the value 'Varying'
        self.kinetics_radio2 = ttk.Radiobutton(self.sec3_frame, text="Dynamic", variable=self.kinetics_mode_var, value="Varying")
        self.kinetics_radio2.grid(row=0, column=2, padx=10, pady=5, sticky='w')
        
        # Parameters adaptation and uncertainty Button
        # self.param_adapt_button = ttk.Button(self.sec3_frame, text="Parameters Adaptation & Uncertainty", command=self.on_param_adaptation)
        # self.param_adapt_button.grid(row=1, column=0, columnspan=3, padx=5, pady=15, sticky='w')
        
        
        # Call on_config_change once to ensure correct initial state
        self.on_config_change()