#initial conditions/digester initial states
from dataclasses import dataclass

@dataclass
class initial:
    S_su: float = 0.0119
    S_aa: float = 0.0053
    S_fa: float = 0.0986
    S_va: float = 0.0116
    S_bu: float = 0.0132
    S_pro:float = 0.0158
    S_ac: float = 0.1976
    S_h2: float = 2.3e-7
    S_ch4:float = 0.0551
    S_IC: float = 0.1527
    S_IN: float = 0.1302
    S_o2: float = 0.1
    S_I : float = 0.3287

    X_xc: float = 0.3087
    X_ch: float = 0.0279
    X_pr: float = 0.1026
    X_li: float = 0.0295
    X_su: float = 0.4201
    X_aa: float = 1.1792
    X_fa: float = 0.2430
    X_c4: float = 0.4319
    X_pro:float = 0.1373
    X_ac: float = 0.7606
    X_h2: float = 0.3170
    X_I : float = 25.617

    S_cat:float = 0.04
    S_an: float = 0.02

    S_va_ion :float = 0.0116
    S_bu_ion :float = 0.0132
    S_pro_ion:float = 0.0157
    S_ac_ion :float = 0.1972             
    S_hco3   :float = 0.1428             
    S_nh3    :float = 0.0041             
    S_h2_gas :float = 1e-5              
    S_ch4_gas:float = 1.6256             
    S_co2_gas:float = 0.0141              
    S_o2_gas :float = 0.0000   
    S_h_ion  :float = 3.4e-8 

    # Cumulative gas production
    V_gas_cum: float = 0.0
    V_ch4_cum: float = 0.0  