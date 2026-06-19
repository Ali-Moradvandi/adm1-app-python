# plot page design for user interface
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
import tkinter.messagebox as mb
import tkinter.filedialog as fd
import pandas as pd
import matplotlib.pyplot as plt
import shutil
import os
from scipy.integrate import cumulative_trapezoid


class TopSectionFrame(tk.Frame):
    def __init__(self, parent, title, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(background="#00A6D6")
        self.name_label = tk.Label(self, text=title, font=("Segoe UI", 14, "bold"), fg="white", background='#00A6D6')
        self.name_label.grid(row=0, column=0, padx=20, pady=10, sticky='w')
        self.grid_columnconfigure(0, weight=1)


class NavigationFrame(tk.Frame):
    def __init__(self, parent, back_command, plot_command, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(background='#00A6D6', highlightbackground='#00A6D6', highlightthickness=1.5)
        
        # Back Button 
        self.back_button = ttk.Button(self, text="Back to Configuration", command=back_command)
        self.back_button.grid(row=0, column=0, sticky='w', padx=(20, 10), pady=10)

        # Plot Button 
        self.plot_button = ttk.Button(self, text="Generate Plots", command=plot_command)
        self.plot_button.grid(row=0, column=2, sticky='e', padx=(10, 20), pady=10)

        self.grid_columnconfigure(0, weight=0)  
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=0)


class PlotPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.temp_filepath = None
        self.default_filename = "Results.xlsx"
        
        self.grid_rowconfigure(0, weight=0)  
        self.grid_rowconfigure(1, weight=1)  
        self.grid_rowconfigure(2, weight=0)  
        self.grid_columnconfigure(0, weight=1)
        
        self.top_section = TopSectionFrame(self, "Data Visualization and Plotting")
        self.top_section.grid(row=0, column=0, sticky='ew')
        
        self.inner_frame = ttk.Frame(self)
        self.inner_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        
        self.subtitle_font = tkFont.Font(size=10, weight="bold")
        
        self.file_label = ttk.Label(self.inner_frame, text="No simulation data loaded. Run the model.", font=("Helvetica", 10, "italic"), foreground="gray")
        self.file_label.grid(row=0, column=0, pady=(10, 10), sticky="w")
        
        self.btn_download = ttk.Button(self.inner_frame, text="Download Results", command=self.download_excel, state="disabled")
        self.btn_download.grid(row=1, column=0, pady=(0, 20), sticky="w")
        
        separator = ttk.Separator(self.inner_frame, orient='horizontal')
        separator.grid(row=2, column=0, sticky='ew', pady=10)

        ttk.Label(self.inner_frame, text="Select Plots to Generate:", font=self.subtitle_font).grid(row=3, column=0, pady=(10, 10), sticky="w")
        
        self.chk_biogas_var = tk.BooleanVar(value=True)
        self.chk_vfa_var = tk.BooleanVar(value=False)
        self.chk_ph_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(self.inner_frame, text="Biogas Production (Flow & Composition)", variable=self.chk_biogas_var, command=self.toggle_subitems).grid(row=4, column=0, sticky="w", pady=(8, 2), padx=10)
        
        self.biogas_opt_frame = ttk.Frame(self.inner_frame)
        self.biogas_opt_frame.grid(row=5, column=0, sticky="w", padx=35, pady=(0, 10))

        self.biogas_flow_var = tk.StringVar(value="Total gas")
        ttk.Radiobutton(self.biogas_opt_frame, text="Total Gas", variable=self.biogas_flow_var, value="Total gas").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(self.biogas_opt_frame, text="Methane", variable=self.biogas_flow_var, value="Methane").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(self.biogas_opt_frame, text="Carbon Dioxide", variable=self.biogas_flow_var, value="Carbon dioxide").grid(row=0, column=2, padx=5)

        ttk.Checkbutton(self.inner_frame, text="VFAs Concentration (Total & Individual)", variable=self.chk_vfa_var, command=self.toggle_subitems).grid(row=6, column=0, sticky="w", pady=8, padx=10)
        self.vfa_opt_frame = ttk.Frame(self.inner_frame)
        self.vfa_opt_frame.grid(row=7, column=0, sticky="w", padx=35, pady=(0, 10))

        self.vfa_frac_var = tk.StringVar(value="Acetate")
        ttk.Radiobutton(self.vfa_opt_frame, text="Valerate", variable=self.vfa_frac_var, value="Valerate").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(self.vfa_opt_frame, text="Butyrate", variable=self.vfa_frac_var, value="Butyrate").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(self.vfa_opt_frame, text="Propionate", variable=self.vfa_frac_var, value="Propionate").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(self.vfa_opt_frame, text="Acetate", variable=self.vfa_frac_var, value="Acetate").grid(row=0, column=3, padx=5)
        
        ttk.Checkbutton(self.inner_frame, text="pH & pH Inhibition to uptake of", variable=self.chk_ph_var, command=self.toggle_subitems).grid(row=8, column=0, sticky="w", pady=8, padx=10)
        self.ph_opt_frame = ttk.Frame(self.inner_frame)
        self.ph_opt_frame.grid(row=9, column=0, sticky="w", padx=35, pady=(0, 10))
        self.ph_inhib_var = tk.StringVar(value="Amino Acids")
        ttk.Radiobutton(self.ph_opt_frame, text="Amino Acids", variable=self.ph_inhib_var, value="Amino Acids").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(self.ph_opt_frame, text="Acetate", variable=self.ph_inhib_var, value="Acetate").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(self.ph_opt_frame, text="Hydrogen", variable=self.ph_inhib_var, value="Hydrogen").grid(row=0, column=2, padx=5)

        self.chk_nitro_var = tk.BooleanVar(value=False) # Add variable
        ttk.Checkbutton(self.inner_frame, text="Nitrogen Concentration & Inhibition", variable=self.chk_nitro_var, command=self.toggle_subitems).grid(row=10, column=0, sticky="w", pady=(8, 2), padx=10)
        self.nitro_opt_frame = ttk.Frame(self.inner_frame)
        self.nitro_opt_frame.grid(row=11, column=0, sticky="w", padx=35, pady=(0, 10))
        self.nitro_opt_var = tk.StringVar(value="Ammonia")
        ttk.Radiobutton(self.nitro_opt_frame, text="Ammonia (NH3)", variable=self.nitro_opt_var, value="Ammonia").grid(row=0, column=0, padx=5)
        ttk.Radiobutton(self.nitro_opt_frame, text="Inorganic Nitrogen (IN)", variable=self.nitro_opt_var, value="Inorganic Nitrogen").grid(row=0, column=1, padx=5)

        self.chk_oxy_var = tk.BooleanVar(value=False) # Add variable
        self.chk_oxy = ttk.Checkbutton(self.inner_frame, text="Oxygen Concentration & Inhibition", variable=self.chk_oxy_var, state="disabled")
        self.chk_oxy.grid(row=12, column=0, sticky="w", pady=8, padx=10)

        self.chk_cum_var = tk.BooleanVar(value=False)
        self.chk_cum = ttk.Checkbutton(self.inner_frame, text="Cumulative Biogas production (for BMP)", variable=self.chk_cum_var, state="disabled")
        self.chk_cum.grid(row=13, column=0, sticky="w", pady=8, padx=10)

        self.nav_frame = NavigationFrame(
            self, 
            back_command=lambda: self.controller.show_frame("MainPage"),
            plot_command=self.generate_plots
        )
        self.nav_frame.grid(row=2, column=0, sticky='ew')

        self.toggle_subitems()

    def toggle_subitems(self):
        """Enables or disables radio buttons based on their parent checkbox state."""
        state_bio = "normal" if self.chk_biogas_var.get() else "disabled"
        for child in self.biogas_opt_frame.winfo_children(): child.configure(state=state_bio)

        state_vfa = "normal" if self.chk_vfa_var.get() else "disabled"
        for child in self.vfa_opt_frame.winfo_children(): child.configure(state=state_vfa)

        state_ph = "normal" if self.chk_ph_var.get() else "disabled"
        for child in self.ph_opt_frame.winfo_children(): child.configure(state=state_ph)

        state_nitro = "normal" if self.chk_nitro_var.get() else "disabled"
        for child in self.nitro_opt_frame.winfo_children(): child.configure(state=state_nitro)

    def set_excel_file(self, filepath, default_filename):
        """Receives the background file from the Run Model button."""
        self.temp_filepath = filepath
        self.default_filename = default_filename
        self.file_label.config(text="Simulation data loaded successfully! Ready for plotting or download.", foreground="green")
        self.btn_download.config(state="normal")

        try:
            df_check = pd.read_excel(filepath, sheet_name="Results", nrows=0)
            if "S_o2" in df_check.columns:
                self.chk_oxy.config(state="normal")
            else:
                self.chk_oxy.config(state="disabled")
                self.chk_oxy_var.set(False)
        except Exception:
            pass
        
    def download_excel(self):
        """Allows the user to save the temp file wherever they want."""
        if not self.temp_filepath or not os.path.exists(self.temp_filepath):
            mb.showerror("Error", "No data file found to download.")
            return
        
        save_path = fd.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Results As",
            initialfile=self.default_filename
        )
        
        if save_path:
            try:
                shutil.copy(self.temp_filepath, save_path)
                mb.showinfo("Success", f"File saved successfully to:\n{save_path}")
            except Exception as e:
                mb.showerror("Error", f"Failed to save file:\n{str(e)}")

    def generate_plots(self):
        if not self.temp_filepath:
            mb.showerror("Error", "No data file found. Please run the model first.")
            return
            
        try:
            df = pd.read_excel(self.temp_filepath, sheet_name="Results")
        except Exception as e:
            mb.showerror("Error", f"Failed to load Excel file:\n{str(e)}")
            return
            
        time = df["Time_days"]
        
        if self.chk_biogas_var.get():
            fig_bio, axs = plt.subplots(figsize=(7, 4))
            fig_bio.canvas.manager.set_window_title('Biogas Production')
            
            flow_choice = self.biogas_flow_var.get()
            if flow_choice == "Total gas":
                y_data = df.get("GasFlow_q_gas", pd.Series([0]*len(time)))
                plot_label = 'Total gas'
            elif flow_choice == "Methane":
                y_data = df.get("GasFlow_q_ch4", pd.Series([0]*len(time)))
                plot_label = 'CH4 flow'
            else:
                y_data = df.get("GasFlow_q_co2", pd.Series([0]*len(time)))
                plot_label = 'CO2 flow'

            axs.plot(time, y_data, label=plot_label, color='tab:blue', linewidth=2)
            axs.set_title('Biogas Production')
            axs.set_xlabel('Time (days)')
            axs.set_ylabel('Flow rate (m³/d)', color='tab:blue')
            axs.grid(True, linestyle='--', alpha=0.7)
            axs.tick_params(axis='y', colors='tab:blue') 

            ax2 = axs.twinx() 

            safe_q_gas = df.get("GasFlow_q_gas", pd.Series([1]*len(time))).replace(0, 1e-10)
            
            ch4_comp = df.get("GasFlow_q_ch4", 0) / safe_q_gas
            co2_comp = df.get("GasFlow_q_co2", 0) / safe_q_gas

            ax2.plot(time, ch4_comp, label='CH4%', color='tab:orange', linewidth=2, linestyle='--')
            ax2.plot(time, co2_comp, label='CO2%', color='tab:orange', linewidth=2, linestyle=':')
            ax2.set_ylabel('Gas Composition (%)', color='tab:orange')
            ax2.tick_params(axis='y', colors='tab:orange')

            lines, labels = axs.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc='best')
                
            plt.tight_layout()
            
        if self.chk_vfa_var.get():
            fig_vfa, ax_vfa = plt.subplots(figsize=(7, 4))
            fig_vfa.canvas.manager.set_window_title('VFA Concentration')
            
            vfa_cols_map = {
                "Valerate": "S_va", 
                "Butyrate": "S_bu", 
                "Propionate": "S_pro", 
                "Acetate": "S_ac"
            }
            
            present_cols = [c for c in vfa_cols_map.values() if c in df.columns]
            
            if present_cols:
                df["VFA_Total"] = df[present_cols].sum(axis=1)
                
                ax_vfa.plot(time, df["VFA_Total"], label="Total VFA", color='tab:blue', linewidth=2)
                ax_vfa.set_title("Volatile Fatty Acids (VFA) Concentration")
                ax_vfa.set_xlabel("Time (days)")
                ax_vfa.set_ylabel("Total VFA (kgCOD/m³)", color='tab:blue')
                ax_vfa.grid(True, linestyle='--', alpha=0.7)
                ax_vfa.tick_params(axis='y', colors='tab:blue') 

                ax2_vfa = ax_vfa.twinx() 
                frac_choice = self.vfa_frac_var.get()
                col_name = vfa_cols_map[frac_choice]

                if col_name in df.columns:
                    ax2_vfa.plot(time, df[col_name], label=f"{frac_choice}", color='tab:orange', linewidth=2, linestyle='--')
                
                ax2_vfa.set_ylabel(f'{frac_choice} Concentration (kgCOD/m³)', color='tab:orange')
                ax2_vfa.tick_params(axis='y', colors='tab:orange')

                lines, labels = ax_vfa.get_legend_handles_labels()
                lines2, labels2 = ax2_vfa.get_legend_handles_labels()
                ax2_vfa.legend(lines + lines2, labels + labels2, loc='best')
                    
            plt.tight_layout()
                
        if self.chk_ph_var.get():
            fig_ph, ax_ph = plt.subplots(figsize=(7, 4))
            fig_ph.canvas.manager.set_window_title('pH & Its Inhibition')
            
            if "pH" in df.columns:
                ax_ph.plot(time, df["pH"], label="pH", color='tab:blue', linewidth=2)
                ax_ph.set_title("pH and Its Inhibition")
                ax_ph.set_xlabel("Time (days)")
                ax_ph.set_ylabel("pH", color='tab:purple')
                ax_ph.grid(True, linestyle='--', alpha=0.7)
                ax_ph.tick_params(axis='y', colors='tab:blue')

                ax2_ph = ax_ph.twinx()
                ph_choice = self.ph_inhib_var.get()
                inhib_map = {"Amino Acids": "Inhib_I_pH_aa", "Acetate": "Inhib_I_pH_ac", "Hydrogen": "Inhib_I_pH_h2"}
                col_name = inhib_map[ph_choice]
                
                if col_name in df.columns:
                    ax2_ph.plot(time, df[col_name], label=f"{ph_choice} Inhibition", color='tab:orange', linewidth=2, linestyle='--')
                    ax2_ph.set_ylabel('Inhibition', color='tab:orange')
                    ax2_ph.tick_params(axis='y', colors='tab:orange')
                    ax2_ph.set_ylim(-0.05, 1.05)

                lines, labels = ax_ph.get_legend_handles_labels()
                lines2, labels2 = ax2_ph.get_legend_handles_labels()
                ax2_ph.legend(lines + lines2, labels + labels2, loc='best')
            plt.tight_layout()

        if self.chk_nitro_var.get():
            fig_n, ax_n = plt.subplots(figsize=(7, 4))
            fig_n.canvas.manager.set_window_title('Nitrogen & Inhibition')
            
            n_choice = self.nitro_opt_var.get()
            if n_choice == "Ammonia":
                conc_col, inhib_col, plot_label = "S_nh3", "Inhib_I_nh3", "Ammonia (NH3)"
            else:
                conc_col, inhib_col, plot_label = "S_IN", "Inhib_I_IN_lim", "Inorganic Nitrogen (IN)"
                
            if conc_col in df.columns:
                ax_n.plot(time, df[conc_col], label=f"{plot_label} Conc.", color='tab:blue', linewidth=2)
                ax_n.set_title(f"{plot_label} Profile")
                ax_n.set_xlabel("Time (days)")
                ax_n.set_ylabel("Concentration (M or kg/m³)", color='tab:blue')
                ax_n.grid(True, linestyle='--', alpha=0.7)
                ax_n.tick_params(axis='y', colors='tab:blue')

                ax2_n = ax_n.twinx()
                if inhib_col in df.columns:
                    ax2_n.plot(time, df[inhib_col], label="Inhibition", color='tab:orange', linewidth=2, linestyle='--')
                    ax2_n.set_ylabel('Inhibition Factor (0-1)', color='tab:orange')
                    ax2_n.tick_params(axis='y', colors='tab:orange')
                    ax2_n.set_ylim(-0.05, 1.05)

                lines, labels = ax_n.get_legend_handles_labels()
                lines2, labels2 = ax2_n.get_legend_handles_labels()
                ax2_n.legend(lines + lines2, labels + labels2, loc='best')
            plt.tight_layout()

        if self.chk_oxy_var.get():
            fig_o, ax_o = plt.subplots(figsize=(7, 4))
            fig_o.canvas.manager.set_window_title('Oxygen & Inhibition')
            
            if "S_o2" in df.columns:
                ax_o.plot(time, df["S_o2"], label="Oxygen Conc.", color='tab:blue', linewidth=2)
                ax_o.set_title("Soluble Oxygen")
                ax_o.set_xlabel("Time (days)")
                ax_o.set_ylabel("Concentration (mg/L)", color='tab:blue')
                ax_o.grid(True, linestyle='--', alpha=0.7)
                ax_o.tick_params(axis='y', colors='tab:blue')

                ax2_o = ax_o.twinx()
                if "Inhib_I_o2" in df.columns:
                    ax2_o.plot(time, df["Inhib_I_o2"], label="O2 Inhibition", color='tab:orange', linewidth=2, linestyle='--')
                    ax2_o.set_ylabel('Inhibition', color='tab:orange')
                    ax2_o.tick_params(axis='y', colors='tab:orange')
                    ax2_o.set_ylim(-0.05, 1.05)

                lines, labels = ax_o.get_legend_handles_labels()
                lines2, labels2 = ax2_o.get_legend_handles_labels()
                ax2_o.legend(lines + lines2, labels + labels2, loc='best')
            plt.tight_layout()

        if getattr(self, 'chk_cum_var', None) and self.chk_cum_var.get():
            fig_cum, ax_cum = plt.subplots(figsize=(7, 4))
            fig_cum.canvas.manager.set_window_title('Cumulative Biogas Production')
            
            # Extract rates (default to 0 if they don't exist)
            # q_gas = df.get("GasFlow_q_gas", pd.Series([0]*len(time)))
            # q_ch4 = df.get("GasFlow_q_ch4", pd.Series([0]*len(time)))
            
            # # Integrate rate (m3/d) over time (d) to get cumulative volume (m3)
            # cum_gas = cumulative_trapezoid(q_gas, x=time, initial=0)
            # cum_ch4 = cumulative_trapezoid(q_ch4, x=time, initial=0)

            # Read the cumulative states directly from the ODE solver output
            cum_gas = df.get("V_gas_cum", pd.Series([0]*len(time)))
            cum_ch4 = df.get("V_ch4_cum", pd.Series([0]*len(time)))
            
            ax_cum.plot(time, cum_gas, label="Total Cumulative Gas", color='tab:blue', linewidth=2)
            ax_cum.plot(time, cum_ch4, label="Cumulative Methane (CH4)", color='tab:orange', linewidth=2, linestyle='--')
            
            ax_cum.set_title("Cumulative Biogas & Methane Production")
            ax_cum.set_xlabel("Time (days)")
            ax_cum.set_ylabel("Cumulative Volume (m³)")
            ax_cum.grid(True, linestyle='--', alpha=0.7)
            ax_cum.legend(loc='best')
            plt.tight_layout()
                
        plt.show()