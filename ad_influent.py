#influent_charactristic
from dataclasses import dataclass

@dataclass
class influent:
    S_su: float = 0.01
    S_aa: float = 0.001
    S_fa: float = 0.001
    S_va: float = 0.001
    S_bu: float = 0.001
    S_pro:float = 0.001
    S_ac: float = 0.001
    S_h2: float = 1.0e-8
    S_ch4:float = 1.0e-5
    S_IC: float = 0.04
    S_IN: float = 0.01
    S_o2: float = 0.1
    S_I : float = 0.02

    X_xc: float = 2.0
    X_ch: float = 5.0
    X_pr: float = 20.0
    X_li: float = 5.0
    X_su: float = 0.0
    X_aa: float = 0.01
    X_fa: float = 0.01
    X_c4: float = 0.01
    X_pro:float = 0.01
    X_ac: float = 0.01
    X_h2: float = 0.01
    X_I : float = 25.0

    S_cat:float = 0.04
    S_an: float = 0.02