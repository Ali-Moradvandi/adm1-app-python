import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from dataclasses import asdict


from ad_characterization import characterize_system

class AdvancedCharacterizationWindow(tk.Toplevel):
    def __init__(self, main_page):
        super().__init__(main_page)
        self.main_page = main_page
        self.title("Advanced Characterization")
        self.geometry("700x600")
        self.configure(background="white")

        self.transient(main_page) 
        self.grab_set()            
        self.focus_set()      
        self.main_root = self.main_page.winfo_toplevel() 
        self.main_root.attributes('-alpha', 0.8) 
        self.protocol("WM_DELETE_WINDOW", self.on_close)            
        
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1) 
        self.grid_rowconfigure(2, weight=0) 
        self.grid_columnconfigure(0, weight=1)
        
        self.sub_type_var = tk.StringVar(value="default")
        self.mode_var = tk.StringVar(value="continuous")
        self.batch_type_var = tk.StringVar(value="fed")
        self.tcod_var = tk.StringVar()
        self.vs_var = tk.StringVar()
        self.bmp_avail_var = tk.BooleanVar(value=False)
        self.bmp_var = tk.StringVar()
        self.sludge_tcod_var = tk.StringVar()
        
        self.yin_vars = {}
        self.y0_vars = {}
        
        self.setup_ui()
        self.build_input_page()

    def on_close(self):
        self.main_root.attributes('-alpha', 1.0)
        self.grab_release() 
        self.destroy()

    def setup_ui(self):
        
        self.top_ribbon = tk.Frame(self, background="#00A6D6", height=50)
        self.top_ribbon.grid(row=0, column=0, sticky="we")
        tk.Label(self.top_ribbon, text="Advanced Characterization", font=("Segoe UI", 14, "bold"), 
                 fg="white", background="#00A6D6").pack(side="left", padx=20, pady=10)
        
        
        self.middle_frame = ttk.Frame(self)
        self.middle_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.middle_frame.grid_rowconfigure(0, weight=1)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(self.middle_frame, highlightthickness=0, background="white")
        self.scrollbar = ttk.Scrollbar(self.middle_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_inner_frame = ttk.Frame(self.canvas)
        
        self.scrollable_inner_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        
        self.bottom_ribbon = tk.Frame(self, background="#00A6D6", height=60)
        self.bottom_ribbon.grid(row=2, column=0, sticky="ew")
        
        self.button_frame = tk.Frame(self.bottom_ribbon, background="#00A6D6")
        self.button_frame.pack(side="right", padx=20, pady=10)

    def clear_inner_frame(self):
        for widget in self.scrollable_inner_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def build_input_page(self):
        self.clear_inner_frame()
        vcmd = (self.register(self.main_page.validate_float), '%P')
        
        ttk.Label(self.scrollable_inner_frame, text="1. Characterization Basis", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        ttk.Label(self.scrollable_inner_frame, text="Substrate Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.sub_cb = ttk.Combobox(self.scrollable_inner_frame, textvariable=self.sub_type_var, state="readonly",
                              values=["default", "cellulose", "chicken manure", "potato starch", 
                                      "black water", "grass silage", "olive mill solid waste", "pear pulp", "sunflower"])
        self.sub_cb.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Label(self.scrollable_inner_frame, text="Process Type:").grid(row=2, column=0, sticky="w", pady=5)
        mode_cb = ttk.Combobox(self.scrollable_inner_frame, textvariable=self.mode_var, state="readonly", values=["continuous", "batch"])
        mode_cb.grid(row=2, column=1, sticky="w", pady=5)
        
        ttk.Label(self.scrollable_inner_frame, text="BMP Type:").grid(row=3, column=0, sticky="w", pady=5)
        self.batch_cb = ttk.Combobox(self.scrollable_inner_frame, textvariable=self.batch_type_var, state="readonly", values=["blank", "positive", "fed"])
        self.batch_cb.grid(row=3, column=1, sticky="w", pady=5)

        separator_1 = ttk.Separator(self.scrollable_inner_frame, orient='horizontal')
        separator_1.grid(row=4, column=0, columnspan=4, sticky='ew', padx=10, pady=15)
        
        # Parameters
        ttk.Label(self.scrollable_inner_frame, text="2. Characterization Parameters", font=("Segoe UI", 11, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", pady=(20, 5))
        
        # tCOD and VS on the same line
        param_frame = ttk.Frame(self.scrollable_inner_frame)
        param_frame.grid(row=6, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(param_frame, text="Total Substrate COD [gCOD/L]:").grid(row=0, column=0, sticky="w")
        ttk.Entry(param_frame, textvariable=self.tcod_var, validate='key', validatecommand=vcmd, width=10).grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(param_frame, text="VS of Substrate [gCOD/L]:").grid(row=0, column=2, sticky="w")
        ttk.Entry(param_frame, textvariable=self.vs_var, validate='key', validatecommand=vcmd, width=10).grid(row=0, column=3, padx=(5, 0))

        # BMP Checkbox and Entry
        bmp_frame = ttk.Frame(self.scrollable_inner_frame)
        bmp_frame.grid(row=7, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(bmp_frame, text="BMP Done", variable=self.bmp_avail_var, command=self.toggle_inputs).grid(row=0, column=0, sticky="w")
        ttk.Label(bmp_frame, text="BMP [mL CH4/g VS]:").grid(row=0, column=1, sticky="w", padx=(15, 5))
        self.bmp_entry = ttk.Entry(bmp_frame, textvariable=self.bmp_var, validate='key', validatecommand=vcmd, width=12)
        self.bmp_entry.grid(row=0, column=2, sticky="w")

        # Sludge tCOD
        ttk.Label(self.scrollable_inner_frame, text="Sludge COD [gCOD/L]:").grid(row=8, column=0, sticky="w", pady=5)
        self.sludge_entry = ttk.Entry(self.scrollable_inner_frame, textvariable=self.sludge_tcod_var, validate='key', validatecommand=vcmd)
        self.sludge_entry.grid(row=8, column=1, sticky="w", pady=5)

        # Buttons
        ttk.Button(self.button_frame, text="Cancel", command=self.on_close).grid(row=0, column=0, padx=5)
        ttk.Button(self.button_frame, text="Calculate", command=self.run_calculation).grid(row=0, column=1, padx=5)

        mode_cb.bind("<<ComboboxSelected>>", self.toggle_inputs)
        self.batch_cb.bind("<<ComboboxSelected>>", self.toggle_inputs)
        self.toggle_inputs()

    def toggle_inputs(self, event=None):
        mode = self.mode_var.get()
        batch_type = self.batch_type_var.get()

        if mode == "batch":
            self.batch_cb.configure(state="readonly")
            self.sludge_entry.configure(state="normal")
        else:
            self.batch_cb.configure(state="disabled")
            self.sludge_entry.configure(state="disabled")
            
        if mode == "batch" and batch_type == "positive":
            self.sub_type_var.set("cellulose")
            self.sub_cb.configure(state="disabled")
        else:
            self.sub_cb.configure(state="readonly")
            
        if self.bmp_avail_var.get():
            self.bmp_entry.configure(state="normal")
        else:
            self.bmp_entry.configure(state="disabled")

    def run_calculation(self):
        try:
            tcod = float(self.tcod_var.get())
            vs = float(self.vs_var.get())
            sub_type = self.sub_type_var.get()
            mode = self.mode_var.get()
            batch_type = self.batch_type_var.get()
            
            bmp = float(self.bmp_var.get()) if self.bmp_avail_var.get() else None
            sludge_tcod = float(self.sludge_tcod_var.get()) if mode == "batch" else None
            
            yin, y0 = characterize_system(tcod, vs, sub_type, mode, batch_type, bmp, sludge_tcod)
            
            self.build_results_page(yin, y0)
            
        except ValueError:
            mb.showerror("Input Error", "Please ensure required numeric fields (like tCOD and VS) are filled out correctly.", parent=self)

    def build_results_page(self, yin, y0):
        self.clear_inner_frame()
        
        yin_dict = asdict(yin)
        y0_dict = asdict(y0)

        if self.mode_var.get() == "batch":
            for key in yin_dict:
                yin_dict[key] = 0.0
        
        standard_adm1_states = {
            "S_su", "S_aa", "S_fa", "S_va", "S_bu", "S_pro", "S_ac", "S_h2", "S_ch4", "S_IC", "S_IN", "S_I",
            "X_xc", "X_ch", "X_pr", "X_li", "X_su", "X_aa", "X_fa", "X_c4", "X_pro", "X_ac", "X_h2", "X_I",
            "S_cat", "S_an"
        }
        
        ttk.Label(self.scrollable_inner_frame, text="Variable", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", padx=(0, 20))
        ttk.Label(self.scrollable_inner_frame, text="Influent", font=("Segoe UI", 10, "bold")).grid(row=1, column=1, sticky="w", padx=(5, 20))
        ttk.Label(self.scrollable_inner_frame, text="Initial Conditions", font=("Segoe UI", 10, "bold")).grid(row=1, column=2, sticky="w", padx=(5, 0))

        row = 2
        for key in yin_dict.keys():
            if key in standard_adm1_states:
                ttk.Label(self.scrollable_inner_frame, text=key).grid(row=row, column=0, sticky="w", pady=2, padx=(0, 20))
                
                val_yin = yin_dict[key]
                var_yin = tk.StringVar(value=f"{val_yin:.4f}" if isinstance(val_yin, float) else str(val_yin))
                ttk.Entry(self.scrollable_inner_frame, textvariable=var_yin, width=12).grid(row=row, column=1, sticky="w", pady=2, padx=(5, 20))
                self.yin_vars[key] = var_yin
                
                val_y0 = y0_dict.get(key, 0.0) 
                var_y0 = tk.StringVar(value=f"{val_y0:.4f}" if isinstance(val_y0, float) else str(val_y0))
                ttk.Entry(self.scrollable_inner_frame, textvariable=var_y0, width=12).grid(row=row, column=2, sticky="w", pady=2, padx=(5, 0))
                self.y0_vars[key] = var_y0
                
                row += 1

        ttk.Button(self.button_frame, text="Back", command=self.build_input_page).grid(row=0, column=0, padx=5)
        ttk.Button(self.button_frame, text="Apply", command=self.apply_and_close).grid(row=0, column=1, padx=5)

    def apply_and_close(self):
        try:
            self.main_page.carbo_var.set(self.yin_vars['X_ch'].get())
            self.main_page.lipid_var.set(self.yin_vars['X_li'].get())
            self.main_page.protein_var.set(self.yin_vars['X_pr'].get())
            self.on_close()
        except KeyError:
            mb.showerror("Error", "Could not map variables back to the main page.", parent=self)