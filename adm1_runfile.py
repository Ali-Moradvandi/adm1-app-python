#main file to run the model
from ad_influent import influent
from ad_parameters import parameter
from ad_initial_conditions import initial
from adm1_main import adm1model
import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import asdict


def adm1_run(model_mode, pH_mode, temperature, kinetics_mode, t_simulation, u, operational_para, influent_corr, para_corr):
    
    # inputs
    u_val = u
    S_o2_in_val = influent_corr[3]
    Hion = influent_corr[4]

    # timesteps
    tspan = [0, t_simulation[0]]
    # tstep = np.arange(0, t_simulation[0]+1, t_simulation[1])
    tstep = np.arange(0, t_simulation[0] + (t_simulation[1] / 2), t_simulation[1])

    # invoke parameters and corrections
    p  = parameter(Temp=temperature)
    p.k_hyd_ch_base = para_corr[0]         
    p.k_hyd_pr_base = para_corr[1]        
    p.k_hyd_li_base = para_corr[2]
    p.k_m_su_base   = para_corr[3]
    p.k_m_aa_base   = para_corr[4]
    p.k_m_fa_base   = para_corr[5]
    p.k_m_c4_base   = para_corr[6]
    p.k_m_pro_base  = para_corr[7]
    p.k_m_ac_base   = para_corr[8]

    p.V_gas = operational_para[0]
    p.V_liq = operational_para[1]


    # invoke influent characteristics and corrections
    yin = influent()
    if model_mode == "ADM1Ox":
        yin.S_o2 = S_o2_in_val

    yin.X_ch = influent_corr[0]
    yin.X_li = influent_corr[1]
    yin.X_pr = influent_corr[2]

    # invoke initial conditions
    y0_obj = initial()
    y0_init= asdict(y0_obj)
    excludestates = []
    if model_mode in ["ADM1", "Start-up", "Batch (BMP)"]:
        excludestates.extend(['S_o2','S_o2_gas'])

    if pH_mode in ['Constant','Algebraic']:
        excludestates.append('S_h_ion')

    statename = [state for state in y0_init.keys() if state not in excludestates]
    y0 = np.array([y0_init[state] for state in statename])

    # initialize model
    adm1_sim = adm1model(statename, p)

    # run model
    sol = solve_ivp(lambda t, y: adm1_sim.adm1_solved(t, y, yin, Hion, u_val, model_mode, pH_mode, kinetics_mode),
                    tspan,
                    y0,
                    method='Radau',
                    t_eval=tstep,
                    rtol=1e-6,
                    atol=1e-8,
                    max_step=0.1)
    
    t = sol.t
    Y = sol.y

    # post processing
    outputs = {name: [] for name in statename}
    gas_flow = {}
    inhibitions = {}
    gas_rate = {}
    sh_all = []

    for i in range(len(t)):
        t_i = t[i]
        y_i = Y[:, i]
        
        for k, name in enumerate(statename):
            outputs[name].append(y_i[k])
            
        _, q_i, inh_i, sh_i, r_i = adm1_sim.adm1_eqs(t_i, y_i, yin, Hion, u, model_mode, pH_mode, kinetics_mode)
        
        for key, val in vars(q_i).items():
            if key not in gas_flow:
                gas_flow[key] = []
            gas_flow[key].append(val)
            
        for key, val in vars(inh_i).items():
            if key not in inhibitions:
                inhibitions[key] = []
            inhibitions[key].append(val)
            
        for key, val in vars(r_i).items():
            if key not in gas_rate:
                gas_rate[key] = []
            gas_rate[key].append(val)
            
        sh_all.append(-np.log10(sh_i))

    # Convert all output lists to numpy arrays for easier plotting/handling later
    for d in (outputs, gas_flow, inhibitions, gas_rate):
        for key in d:
            d[key] = np.array(d[key])
            
    sh_all = np.array(sh_all)

    return t, outputs, gas_flow, inhibitions, sh_all