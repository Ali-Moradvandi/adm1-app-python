# main function of adm1
import numpy as np
from types import SimpleNamespace
import copy

class adm1model:
    def __init__(self, states, parameters):

        self.s = states
        self.p = parameters
        self.p_orig = copy.deepcopy(parameters)

        idx = {state: i for i, state in enumerate(self.s)}
        self.idx = SimpleNamespace(**idx)

    def adm1_solved(self, t, y, yin, Hion, u, model_mode, pH_mode, kinetics_mode):

        dy, *_ = self.adm1_eqs(t, y, yin, Hion, u, model_mode, pH_mode, kinetics_mode)
        return dy
    
    def adm1_eqs(self, t, y, yin, Hion, u, model_mode, pH_mode, kinetics_mode):

        # input flow rate
        q_in = u

        # dummy state assignment
        S_hco3 = y[self.idx.S_hco3]
        S_nh3 = y[self.idx.S_nh3]
        S_co2 = y[self.idx.S_IC] - S_hco3
        S_nh4 = y[self.idx.S_IN] - S_nh3

        dy = np.zeros_like(y)
        sh = 0

        # assign model_mode
        if model_mode in ["ADM1", "Start-up", "Batch (BMP)"]:
            S_o2 = 0
            if pH_mode == "Differential":
                sh = y[self.idx.S_h_ion]
            elif pH_mode == "Algebraic":
                theta = (y[self.idx.S_cat] + S_nh4 -S_hco3 - - y[self.idx.S_ac_ion]/64 - 
                         y[self.idx.S_pro_ion]/112 - y[self.idx.S_bu_ion]/160 - 
                         y[self.idx.S_va_ion]/208 - y[self.idx.S_an])
                if theta*theta + 4*self.p.K_w < 0:
                    sh = Hion
                else:
                    sh = -theta/2 + 0.5*np.sqrt(theta*theta + 4*self.p.K_w)
            elif pH_mode == "Constant":
                sh = Hion

        elif model_mode == "ADM1Ox":
            S_o2 = y[self.idx.S_o2]
            if pH_mode == "Differential":
                sh = y[self.idx.S_h_ion]
            elif pH_mode == "Algebraic":
                theta = (y[self.idx.S_cat] + S_nh4 - S_hco3 - y[self.idx.S_ac_ion]/64 - 
                         y[self.idx.S_pro_ion]/112 - y[self.idx.S_bu_ion]/160 - 
                         y[self.idx.S_va_ion]/208 - y[self.idx.S_an])
                if theta*theta + 4*self.p.K_w < 0:
                    sh = Hion
                else:
                    sh = -theta/2 + 0.5*np.sqrt(theta*theta + 4*self.p.K_w)
            elif pH_mode == "Constant":
                sh = Hion

        # dynamic kinetics correction
        # if kinetics_mode == 'Varying':
        #     self.p.k_hyd_ch_base = (self.p.k_hyd_ch_base - self.p.k_hyd_ch_in)*(1 - np.exp(-self.p.k_hyd_ch_acc*(t - self.p.t_hyd_ch_lag))) + self.p.k_hyd_ch_in
        #     self.p.k_hyd_pr_base = (self.p.k_hyd_pr_base - self.p.k_hyd_pr_in)*(1 - np.exp(-self.p.k_hyd_pr_acc*(t - self.p.t_hyd_pr_lag))) + self.p.k_hyd_pr_in
        #     self.p.k_hyd_li_base = (self.p.k_hyd_li_base - self.p.k_hyd_li_in)*(1 - np.exp(-self.p.k_hyd_li_acc*(t - self.p.t_hyd_li_lag))) + self.p.k_hyd_li_in
        #     self.p.k_m_su_base   = (self.p.k_m_su_base - self.p.k_m_su_in)*(1 - np.exp(-self.p.k_m_su_acc*(t - self.p.t_m_su_lag))) + self.p.k_m_su_in
        #     self.p.k_m_aa_base   = (self.p.k_m_aa_base - self.p.k_m_aa_in)*(1 - np.exp(-self.p.k_m_aa_acc*(t - self.p.t_m_aa_lag))) + self.p.k_m_aa_in
        #     self.p.k_m_fa_base   = (self.p.k_m_fa_base - self.p.k_m_fa_in)*(1 - np.exp(-self.p.k_m_fa_acc*(t - self.p.t_m_fa_lag))) + self.p.k_m_fa_in
        #     self.p.k_m_c4_base   = (self.p.k_m_c4_base - self.p.k_m_c4_in)*(1 - np.exp(-self.p.k_m_c4_acc*(t - self.p.t_m_c4_lag))) + self.p.k_m_c4_in
        #     self.p.k_m_pro_base  = (self.p.k_m_pro_base - self.p.k_m_pro_in)*(1 - np.exp(-self.p.k_m_pro_acc*(t - self.p.t_m_pro_lag))) + self.p.k_m_pro_in
        #     self.p.k_m_ac_base   = (self.p.k_m_ac_base - self.p.k_m_ac_in)*(1 - np.exp(-self.p.k_m_ac_acc*(t - self.p.t_m_ac_lag))) + self.p.k_m_ac_in
        #     self.p.k_m_h2_base   = (self.p.k_m_h2_base - self.p.k_m_h2_in)*(1 - np.exp(-self.p.k_m_h2_acc*(t - self.p.t_m_h2_lag))) + self.p.k_m_h2_in    
        if kinetics_mode == 'Varying':
            self.p.k_hyd_ch_base = (self.p_orig.k_hyd_ch_base - self.p.k_hyd_ch_in)*(1 - np.exp(-self.p.k_hyd_ch_acc*(t - self.p.t_hyd_ch_lag))) + self.p.k_hyd_ch_in
            self.p.k_hyd_pr_base = (self.p_orig.k_hyd_pr_base - self.p.k_hyd_pr_in)*(1 - np.exp(-self.p.k_hyd_pr_acc*(t - self.p.t_hyd_pr_lag))) + self.p.k_hyd_pr_in
            self.p.k_hyd_li_base = (self.p_orig.k_hyd_li_base - self.p.k_hyd_li_in)*(1 - np.exp(-self.p.k_hyd_li_acc*(t - self.p.t_hyd_li_lag))) + self.p.k_hyd_li_in
            self.p.k_m_su_base   = (self.p_orig.k_m_su_base - self.p.k_m_su_in)*(1 - np.exp(-self.p.k_m_su_acc*(t - self.p.t_m_su_lag))) + self.p.k_m_su_in
            self.p.k_m_aa_base   = (self.p_orig.k_m_aa_base - self.p.k_m_aa_in)*(1 - np.exp(-self.p.k_m_aa_acc*(t - self.p.t_m_aa_lag))) + self.p.k_m_aa_in
            self.p.k_m_fa_base   = (self.p_orig.k_m_fa_base - self.p.k_m_fa_in)*(1 - np.exp(-self.p.k_m_fa_acc*(t - self.p.t_m_fa_lag))) + self.p.k_m_fa_in
            self.p.k_m_c4_base   = (self.p_orig.k_m_c4_base - self.p.k_m_c4_in)*(1 - np.exp(-self.p.k_m_c4_acc*(t - self.p.t_m_c4_lag))) + self.p.k_m_c4_in
            self.p.k_m_pro_base  = (self.p_orig.k_m_pro_base - self.p.k_m_pro_in)*(1 - np.exp(-self.p.k_m_pro_acc*(t - self.p.t_m_pro_lag))) + self.p.k_m_pro_in
            self.p.k_m_ac_base   = (self.p_orig.k_m_ac_base - self.p.k_m_ac_in)*(1 - np.exp(-self.p.k_m_ac_acc*(t - self.p.t_m_ac_lag))) + self.p.k_m_ac_in
            self.p.k_m_h2_base   = (self.p_orig.k_m_h2_base - self.p.k_m_h2_in)*(1 - np.exp(-self.p.k_m_h2_acc*(t - self.p.t_m_h2_lag))) + self.p.k_m_h2_in
        else:
            self.p.k_hyd_ch_base = self.p_orig.k_hyd_ch_base
            self.p.k_hyd_pr_base = self.p_orig.k_hyd_pr_base
            self.p.k_hyd_li_base = self.p_orig.k_hyd_li_base
            self.p.k_m_su_base   = self.p_orig.k_m_su_base
            self.p.k_m_aa_base   = self.p_orig.k_m_aa_base
            self.p.k_m_fa_base   = self.p_orig.k_m_fa_base
            self.p.k_m_c4_base   = self.p_orig.k_m_c4_base
            self.p.k_m_pro_base  = self.p_orig.k_m_pro_base
            self.p.k_m_ac_base   = self.p_orig.k_m_ac_base
            self.p.k_m_h2_base   = self.p_orig.k_m_h2_base

        # inhibition functions
        inh = SimpleNamespace()

        # pH inhibition based on Hill functions
        pHLim_aa = 10 ** (-(self.p.pH_LL_aa + self.p.pH_UL_aa) / 2)
        pHLim_ac = 10 ** (-(self.p.pH_LL_ac + self.p.pH_UL_ac) / 2)
        pHLim_h2 = 10 ** (-(self.p.pH_LL_h2 + self.p.pH_UL_h2) / 2)
        
        n_aa = 3.0 / (self.p.pH_UL_aa - self.p.pH_LL_aa)
        n_ac = 3.0 / (self.p.pH_UL_ac - self.p.pH_LL_ac)
        n_h2 = 3.0 / (self.p.pH_UL_h2 - self.p.pH_LL_h2)
        
        inh.I_pH_aa  = (pHLim_aa ** n_aa) / ((sh ** n_aa) + (pHLim_aa ** n_aa))
        inh.I_pH_ac  = (pHLim_ac ** n_ac) / ((sh ** n_ac) + (pHLim_ac ** n_ac))
        inh.I_pH_h2  = (pHLim_h2 ** n_h2) / ((sh ** n_h2) + (pHLim_h2 ** n_h2))
        
        # basis of inhibition functions
        inh.I_IN_lim = 1.0 / (1.0 + self.p.K_S_IN / y[self.idx.S_IN])
        inh.I_h2_fa  = 1.0 / (1.0 + y[self.idx.S_h2] / self.p.K_Ih2_fa)
        inh.I_h2_c4  = 1.0 / (1.0 + y[self.idx.S_h2] / self.p.K_Ih2_c4)
        inh.I_h2_pro = 1.0 / (1.0 + y[self.idx.S_h2] / self.p.K_Ih2_pro)
        inh.I_nh3    = 1.0 / (1.0 + y[self.idx.S_nh3] / self.p.K_I_nh3)
        inh.I_o2     = 1.0 / (1.0 + S_o2 / self.p.K_I_o2)
        
        # process inhibition functions
        inhib_su        = inh.I_pH_aa * inh.I_IN_lim * inh.I_o2
        inhib_aa        = inhib_su
        inhib_fa        = inh.I_pH_aa * inh.I_IN_lim * inh.I_h2_fa * inh.I_o2
        inhib_su_aer    = inh.I_pH_aa * inh.I_IN_lim
        inhib_aa_aer    = inhib_su_aer
        inhib_fa_aer    = inh.I_pH_aa * inh.I_IN_lim * inh.I_h2_fa
        inhib_va        = inh.I_pH_aa * inh.I_IN_lim * inh.I_h2_c4 * inh.I_o2
        inhib_bu        = inhib_va
        inhib_pro       = inh.I_pH_aa * inh.I_IN_lim * inh.I_h2_pro * inh.I_o2
        inhib_ac        = inh.I_pH_ac * inh.I_IN_lim * inh.I_nh3 * inh.I_o2
        inhib_h2        = inh.I_pH_h2 * inh.I_IN_lim * inh.I_o2

        # process rates
        ro_dis = self.p.k_dis * y[self.idx.X_xc]
        
        if model_mode == "ADM1Ox":
        # if hasattr(self.idx, 'S_o2'):
            k_hyd_ch  = 10 * self.p.k_hyd_ch_base
            k_hyd_pr  = 10 * self.p.k_hyd_pr_base
            k_hyd_li  = 10 * self.p.k_hyd_li_base
            ro_hyd_ch = k_hyd_ch * y[self.idx.X_ch] * y[self.idx.X_su]
            ro_hyd_pr = k_hyd_pr * y[self.idx.X_pr] * y[self.idx.X_aa]
            ro_hyd_li = k_hyd_li * y[self.idx.X_li] * y[self.idx.X_fa]
        else:
            ro_hyd_ch = self.p.k_hyd_ch_base * y[self.idx.X_ch]
            ro_hyd_pr = self.p.k_hyd_pr_base * y[self.idx.X_pr]
            ro_hyd_li = self.p.k_hyd_li_base * y[self.idx.X_li]
            
        ro_up_su   = self.p.k_m_su_base  * (y[self.idx.S_su]  / (self.p.K_S_su  + y[self.idx.S_su]))  * y[self.idx.X_su]  * inhib_su
        ro_up_aa   = self.p.k_m_aa_base  * (y[self.idx.S_aa]  / (self.p.K_S_aa  + y[self.idx.S_aa]))  * y[self.idx.X_aa]  * inhib_aa
        ro_up_fa   = self.p.k_m_fa_base  * (y[self.idx.S_fa]  / (self.p.K_S_fa  + y[self.idx.S_fa]))  * y[self.idx.X_fa]  * inhib_fa
        ro_aer_su  = self.p.k_m_su_base  * (y[self.idx.S_su]  / (self.p.K_S_su  + y[self.idx.S_su]))  * y[self.idx.X_su]  * (1 - inh.I_o2) * inhib_su_aer
        ro_aer_aa  = self.p.k_m_aa_base  * (y[self.idx.S_aa]  / (self.p.K_S_aa  + y[self.idx.S_aa]))  * y[self.idx.X_aa]  * (1 - inh.I_o2) * inhib_aa_aer
        ro_aer_fa  = self.p.k_m_fa_base  * (y[self.idx.S_fa]  / (self.p.K_S_fa  + y[self.idx.S_fa]))  * y[self.idx.X_fa]  * (1 - inh.I_o2) * inhib_fa_aer
        ro_up_va   = self.p.k_m_c4_base  * (y[self.idx.S_va]  / (self.p.K_S_c4  + y[self.idx.S_va]))  * y[self.idx.X_c4]  * (y[self.idx.S_va] / (y[self.idx.S_bu] + y[self.idx.S_va] + 1.0e-6)) * inhib_va
        ro_up_bu   = self.p.k_m_c4_base  * (y[self.idx.S_bu]  / (self.p.K_S_c4  + y[self.idx.S_bu]))  * y[self.idx.X_c4]  * (y[self.idx.S_bu] / (y[self.idx.S_va] + y[self.idx.S_bu] + 1.0e-6)) * inhib_bu
        ro_up_pro  = self.p.k_m_pro_base * (y[self.idx.S_pro] / (self.p.K_S_pro + y[self.idx.S_pro])) * y[self.idx.X_pro] * inhib_pro
        ro_up_ac   = self.p.k_m_ac_base  * (y[self.idx.S_ac]  / (self.p.K_S_ac  + y[self.idx.S_ac]))  * y[self.idx.X_ac]  * inhib_ac
        
        ro_aer_va  = (self.p.k_m_su_base * y[self.idx.X_su] * inhib_su_aer + self.p.k_m_aa_base * y[self.idx.X_aa] * inhib_aa_aer + self.p.k_m_fa_base * y[self.idx.X_fa] * inhib_fa_aer) * (y[self.idx.S_va] / (self.p.K_S_va_aer + y[self.idx.S_va])) * (1 - inh.I_o2)
        ro_aer_bu  = (self.p.k_m_su_base * y[self.idx.X_su] * inhib_su_aer + self.p.k_m_aa_base * y[self.idx.X_aa] * inhib_aa_aer + self.p.k_m_fa_base * y[self.idx.X_fa] * inhib_fa_aer) * (y[self.idx.S_bu] / (self.p.K_S_bu_aer + y[self.idx.S_bu])) * (1 - inh.I_o2)
        ro_aer_pro = (self.p.k_m_su_base * y[self.idx.X_su] * inhib_su_aer + self.p.k_m_aa_base * y[self.idx.X_aa] * inhib_aa_aer + self.p.k_m_fa_base * y[self.idx.X_fa] * inhib_fa_aer) * (y[self.idx.S_pro] / (self.p.K_S_pro_aer + y[self.idx.S_pro])) * (1 - inh.I_o2)
        ro_aer_ac  = (self.p.k_m_su_base * y[self.idx.X_su] * inhib_su_aer + self.p.k_m_aa_base * y[self.idx.X_aa] * inhib_aa_aer + self.p.k_m_fa_base * y[self.idx.X_fa] * inhib_fa_aer) * (y[self.idx.S_ac] / (self.p.K_S_ac_aer + y[self.idx.S_ac])) * (1 - inh.I_o2)
        ro_up_h2   = self.p.k_m_h2_base  * (y[self.idx.S_h2]  / (self.p.K_S_h2  + y[self.idx.S_h2]))  * y[self.idx.X_h2]  * inhib_h2
        
        ro_dec_su  = self.p.k_dec_Xsu  * y[self.idx.X_su]
        ro_dec_aa  = self.p.k_dec_Xaa  * y[self.idx.X_aa]
        ro_dec_fa  = self.p.k_dec_Xfa  * y[self.idx.X_fa]
        ro_dec_c4  = self.p.k_dec_Xc4  * y[self.idx.X_c4]
        ro_dec_pro = self.p.k_dec_Xpro * y[self.idx.X_pro]
        ro_dec_ac  = self.p.k_dec_Xac  * y[self.idx.X_ac]
        ro_dec_h2  = self.p.k_dec_Xh2  * y[self.idx.X_h2]

        ro_A_va  = self.p.k_A_Bva  * (y[self.idx.S_va_ion]  * (self.p.K_a_va  + sh) - self.p.K_a_va  * y[self.idx.S_va])
        ro_A_bu  = self.p.k_A_Bbu  * (y[self.idx.S_bu_ion]  * (self.p.K_a_bu  + sh) - self.p.K_a_bu  * y[self.idx.S_bu])
        ro_A_pro = self.p.k_A_Bpro * (y[self.idx.S_pro_ion] * (self.p.K_a_pro + sh) - self.p.K_a_pro * y[self.idx.S_pro])
        ro_A_ac  = self.p.k_A_Bac  * (y[self.idx.S_ac_ion]  * (self.p.K_a_ac  + sh) - self.p.K_a_ac  * y[self.idx.S_ac])
        ro_A_IC  = self.p.k_A_Bco2 * (y[self.idx.S_hco3]    * (self.p.K_a_co2 + sh) - self.p.K_a_co2 * y[self.idx.S_IC])
        ro_A_IN  = self.p.k_A_BIN  * (y[self.idx.S_nh3]     * (self.p.K_a_IN  + sh) - self.p.K_a_IN  * y[self.idx.S_IN])

        pressure = SimpleNamespace()
        pressure.p_gas_h2o = self.p.p_gas_h2o
        pressure.p_gas_h2  = y[self.idx.S_h2_gas]  * self.p.R * self.p.T_op / 16
        pressure.p_gas_ch4 = y[self.idx.S_ch4_gas] * self.p.R * self.p.T_op / 64
        pressure.p_gas_co2 = y[self.idx.S_co2_gas] * self.p.R * self.p.T_op
        if hasattr(self.idx, 'S_o2_gas'):
            pressure.p_gas_o2 = y[self.idx.S_o2_gas] * self.p.R * self.p.T_op
            
        gas_rate = SimpleNamespace()
        gas_rate.ro_T_h2  = self.p.kLa_base * (y[self.idx.S_h2]  - 16 * self.p.K_H_h2  * pressure.p_gas_h2)
        gas_rate.ro_T_ch4 = self.p.kLa_base * (y[self.idx.S_ch4] - 64 * self.p.K_H_ch4 * pressure.p_gas_ch4)
        gas_rate.ro_T_co2 = self.p.kLa_base * (S_co2 - self.p.K_H_co2 * pressure.p_gas_co2)
        if hasattr(self.idx, 'S_o2'):
            gas_rate.ro_T_o2 = self.p.kLa_base * 0 * (y[self.idx.S_o2] - self.p.K_H_o2 * pressure.p_gas_o2) # it's zero
            
        pressure.p_gas = pressure.p_gas_h2 + pressure.p_gas_ch4 + pressure.p_gas_co2 + pressure.p_gas_h2o

        gas_flow = SimpleNamespace()
        gas_flow.q_gas = self.p.k_P * (pressure.p_gas - self.p.P_atm)
        if gas_flow.q_gas < 0:
            gas_flow.q_gas = 0
            
        gas_flow.q_ch4 = gas_flow.q_gas * (pressure.p_gas_ch4 / pressure.p_gas)
        gas_flow.q_co2 = gas_flow.q_gas * (pressure.p_gas_co2 / pressure.p_gas)

        # carbon stochiometery
        sto_dis    = -self.p.C_xc + self.p.f_sI_xc*self.p.C_sI + self.p.f_ch_xc*self.p.C_ch + self.p.f_pr_xc*self.p.C_pr + self.p.f_li_xc*self.p.C_li + self.p.f_xI_xc*self.p.C_xI
        sto_hyd_ch = -self.p.C_ch + self.p.C_su
        sto_hyd_pr = -self.p.C_pr + self.p.C_aa
        sto_hyd_li = -self.p.C_li + (1 - self.p.f_fa_li)*self.p.C_su + self.p.f_fa_li*self.p.C_fa
        sto_up_su  = -self.p.C_su + (1 - self.p.Y_su)*(self.p.f_bu_su*self.p.C_bu + self.p.f_pro_su*self.p.C_pro + self.p.f_ac_su*self.p.C_ac) + self.p.Y_su*self.p.C_bac
        sto_up_aa  = -self.p.C_aa + (1 - self.p.Y_aa)*(self.p.f_va_aa*self.p.C_va + self.p.f_bu_aa*self.p.C_bu + self.p.f_pro_aa*self.p.C_pro + self.p.f_ac_aa*self.p.C_ac) + self.p.Y_aa*self.p.C_bac
        sto_up_fa  = -self.p.C_fa + (1 - self.p.Y_fa)*0.7*self.p.C_ac + self.p.Y_fa*self.p.C_bac
        sto_up_va  = -self.p.C_va + (1 - self.p.Y_c4)*0.54*self.p.C_pro + (1 - self.p.Y_c4)*0.31*self.p.C_ac + self.p.Y_c4*self.p.C_bac
        sto_up_bu  = -self.p.C_bu + (1 - self.p.Y_c4)*0.8*self.p.C_ac + self.p.Y_c4*self.p.C_bac
        sto_up_pro = -self.p.C_pro + (1 - self.p.Y_pro)*0.57*self.p.C_ac + self.p.Y_pro*self.p.C_bac
        sto_up_ac  = -self.p.C_ac + (1 - self.p.Y_ac)*self.p.C_ch4 + self.p.Y_ac*self.p.C_bac
        sto_up_h2  = (1 - self.p.Y_h2)*self.p.C_ch4 + self.p.Y_h2*self.p.C_bac
        sto_dec    = -self.p.C_bac + self.p.C_xc
        sto_aer_su = self.p.C_1 * (1 - self.p.Y_su_aer)
        sto_aer_aa = self.p.C_2 * (1 - self.p.Y_aa_aer)
        sto_aer_fa = self.p.C_3 * (1 - self.p.Y_fa_aer)
        sto_aer_va = self.p.C_va_aer * (1 - self.p.Y_va_aer)
        sto_aer_bu = self.p.C_bu_aer * (1 - self.p.Y_bu_aer)
        sto_aer_pro= self.p.C_pro_aer * (1 - self.p.Y_pro_aer)
        sto_aer_ac = self.p.C_ac_aer * (1 - self.p.Y_ac_aer)

        # differential equations
        # sugar
        dy[self.idx.S_su]  = q_in/self.p.V_liq*(yin.S_su - y[self.idx.S_su]) + ro_hyd_ch + (1 - self.p.f_fa_li)*ro_hyd_li - ro_up_su - ro_aer_su
        # amino acid
        dy[self.idx.S_aa]  = q_in/self.p.V_liq*(yin.S_aa - y[self.idx.S_aa]) + ro_hyd_pr - ro_up_aa - ro_aer_aa
        # fatty acid
        dy[self.idx.S_fa]  = q_in/self.p.V_liq*(yin.S_fa - y[self.idx.S_fa]) + self.p.f_fa_li*ro_hyd_li - ro_up_fa - ro_aer_fa
        # valerate
        dy[self.idx.S_va]  = q_in/self.p.V_liq*(yin.S_va - y[self.idx.S_va]) + (1 - self.p.Y_aa)*self.p.f_va_aa*ro_up_aa - ro_aer_va - ro_up_va
        # butyrate
        dy[self.idx.S_bu]  = q_in/self.p.V_liq*(yin.S_bu - y[self.idx.S_bu]) + (1 - self.p.Y_su)*self.p.f_bu_su*ro_up_su + (1 - self.p.Y_aa)*self.p.f_bu_aa*ro_up_aa - ro_aer_bu - ro_up_bu
        # propionate
        dy[self.idx.S_pro] = q_in/self.p.V_liq*(yin.S_pro- y[self.idx.S_pro]) + (1 - self.p.Y_su)*self.p.f_pro_su*ro_up_su + (1 - self.p.Y_aa)*self.p.f_pro_aa*ro_up_aa - ro_aer_pro + (1 - self.p.Y_c4)*0.54*ro_up_va - ro_up_pro
        # acetate
        dy[self.idx.S_ac]  = q_in/self.p.V_liq*(yin.S_ac  - y[self.idx.S_ac]) + (1 - self.p.Y_su)*self.p.f_ac_su*ro_up_su + (1 - self.p.Y_aa)*self.p.f_ac_aa*ro_up_aa + (1 - self.p.Y_fa)*0.7*ro_up_fa - ro_aer_ac + (1 - self.p.Y_c4)*0.31*ro_up_va + (1 - self.p.Y_c4)*0.8*ro_up_bu + (1 - self.p.Y_pro)*0.57*ro_up_pro - ro_up_ac
        # hydrogen
        dy[self.idx.S_h2]  = q_in/self.p.V_liq*(yin.S_h2 - y[self.idx.S_h2]) + (1 - self.p.Y_su)*self.p.f_h2_su*ro_up_su + (1 - self.p.Y_aa)*self.p.f_h2_aa*ro_up_aa + (1 - self.p.Y_fa)*0.3*ro_up_fa + (1 - self.p.Y_c4)*0.15*ro_up_va + (1 - self.p.Y_c4)*0.2*ro_up_bu + (1 - self.p.Y_pro)*0.43*ro_up_pro - ro_up_h2 - gas_rate.ro_T_h2
        # methane
        dy[self.idx.S_ch4] = q_in/self.p.V_liq*(yin.S_ch4 - y[self.idx.S_ch4]) + (1 - self.p.Y_ac)*ro_up_ac + (1 - self.p.Y_h2)*ro_up_h2 - gas_rate.ro_T_ch4
        # inorganic carbon
        dy[self.idx.S_IC]  = (q_in/self.p.V_liq*(yin.S_IC  - y[self.idx.S_IC]) - sto_dis*ro_dis - sto_hyd_ch*ro_hyd_ch - sto_hyd_pr*ro_hyd_pr - sto_hyd_li*ro_hyd_li
                            - sto_up_su*ro_up_su - sto_up_aa*ro_up_aa - sto_up_fa*ro_up_fa - sto_up_va*ro_up_va - sto_up_bu*ro_up_bu
                            - sto_up_pro*ro_up_pro - sto_up_ac*ro_up_ac - sto_up_h2*ro_up_h2 - sto_dec*ro_dec_su - sto_dec*ro_dec_aa 
                            - sto_dec*ro_dec_fa - sto_dec*ro_dec_c4 - sto_dec*ro_dec_pro - sto_dec*ro_dec_ac - sto_dec*ro_dec_h2 - gas_rate.ro_T_co2
                            + sto_aer_su*ro_aer_su + sto_aer_aa*ro_aer_aa + sto_aer_fa*ro_aer_fa + sto_aer_va*ro_aer_va + sto_aer_bu*ro_aer_bu + sto_aer_pro*ro_aer_pro + sto_aer_ac*ro_aer_ac)
        # inorganic nitrogen
        dy[self.idx.S_IN]  = (q_in/self.p.V_liq*(yin.S_IN - y[self.idx.S_IN]) - self.p.Y_su*self.p.N_bac*ro_up_su + (self.p.N_aa - self.p.Y_aa*self.p.N_bac)*ro_up_aa - self.p.Y_fa*self.p.N_bac*ro_up_fa
                            - self.p.Y_c4*self.p.N_bac*ro_up_va - self.p.Y_c4*self.p.N_bac*ro_up_bu - self.p.Y_pro*self.p.N_bac*ro_up_pro - self.p.Y_ac*self.p.N_bac*ro_up_ac - self.p.Y_h2*self.p.N_bac*ro_up_h2
                            + (self.p.N_bac - self.p.N_xc)*(ro_dec_su + ro_dec_aa + ro_dec_fa + ro_dec_c4 + ro_dec_pro + ro_dec_ac + ro_dec_h2)
                            + (self.p.N_xc - self.p.f_xI_xc*self.p.N_I - self.p.f_sI_xc*self.p.N_I - self.p.f_pr_xc*self.p.N_aa)*ro_dis
                            - self.p.Y_su_aer*self.p.N_bac*ro_aer_su - (self.p.N_aa - self.p.Y_aa_aer*self.p.N_bac)*ro_aer_aa - self.p.Y_fa_aer*self.p.N_bac*ro_aer_fa
                            - self.p.Y_va_aer*self.p.N_bac*ro_aer_va - self.p.Y_bu_aer*self.p.N_bac*ro_aer_bu - self.p.Y_pro_aer*self.p.N_bac*ro_aer_pro - self.p.Y_ac_aer*self.p.N_bac*ro_aer_ac)

        # oxygen
        if hasattr(self.idx, 'S_o2'):
            dS_o2 = q_in/self.p.V_liq*(yin.S_o2 - S_o2) - 1.1*ro_aer_su - 1.2*ro_aer_aa - 2.03*ro_aer_fa - 2.04*ro_aer_va - 1.82*ro_aer_bu - 1.51*ro_aer_pro - 1.07*ro_aer_ac - gas_rate.ro_T_o2
            dy[self.idx.S_o2] = dS_o2

        # inert
        dy[self.idx.S_I]    = q_in/self.p.V_liq*(yin.S_I - y[self.idx.S_I]) + self.p.f_sI_xc*ro_dis
        # composite
        dy[self.idx.X_xc]   = q_in/self.p.V_liq*(yin.X_xc - y[self.idx.X_xc]) - ro_dis + ro_dec_su + ro_dec_aa + ro_dec_fa + ro_dec_c4 + ro_dec_pro + ro_dec_ac + ro_dec_h2
        # carbohydrates
        dy[self.idx.X_ch]   = q_in/self.p.V_liq*(yin.X_ch - y[self.idx.X_ch]) + self.p.f_ch_xc*ro_dis - ro_hyd_ch
        # protein
        dy[self.idx.X_pr]   = q_in/self.p.V_liq*(yin.X_pr - y[self.idx.X_pr]) + self.p.f_pr_xc*ro_dis - ro_hyd_pr
        # lipid
        dy[self.idx.X_li]   = q_in/self.p.V_liq*(yin.X_li - y[self.idx.X_li]) + self.p.f_li_xc*ro_dis - ro_hyd_li
        # sugar X
        dy[self.idx.X_su]   = q_in/self.p.V_liq*(yin.X_su - y[self.idx.X_su]) + self.p.Y_su*ro_up_su + self.p.Y_su_aer*ro_aer_su + 1/3*(self.p.Y_va_aer*ro_aer_va + self.p.Y_bu_aer*ro_aer_bu + self.p.Y_pro_aer*ro_aer_pro + self.p.Y_ac_aer*ro_aer_ac) - ro_dec_su
        # amino acid X
        dy[self.idx.X_aa]   = q_in/self.p.V_liq*(yin.X_aa - y[self.idx.X_aa]) + self.p.Y_aa*ro_up_aa + self.p.Y_aa_aer*ro_aer_aa + 1/3*(self.p.Y_va_aer*ro_aer_va + self.p.Y_bu_aer*ro_aer_bu + self.p.Y_pro_aer*ro_aer_pro + self.p.Y_ac_aer*ro_aer_ac) - ro_dec_aa
        # fatty acid X
        dy[self.idx.X_fa]   = q_in/self.p.V_liq*(yin.X_fa - y[self.idx.X_fa]) + self.p.Y_fa*ro_up_fa + self.p.Y_fa_aer*ro_aer_fa + 1/3*(self.p.Y_va_aer*ro_aer_va + self.p.Y_bu_aer*ro_aer_bu + self.p.Y_pro_aer*ro_aer_pro + self.p.Y_ac_aer*ro_aer_ac) - ro_dec_fa
        # c4
        dy[self.idx.X_c4]   = q_in/self.p.V_liq*(yin.X_c4 - y[self.idx.X_c4]) + self.p.Y_c4*ro_up_va + self.p.Y_c4*ro_up_bu - ro_dec_c4
        # propionate X
        dy[self.idx.X_pro]  = q_in/self.p.V_liq*(yin.X_pro - y[self.idx.X_pro]) + self.p.Y_pro*ro_up_pro - ro_dec_pro
        # acetate X
        dy[self.idx.X_ac]   = q_in/self.p.V_liq*(yin.X_ac - y[self.idx.X_ac]) + self.p.Y_ac*ro_up_ac - ro_dec_ac
        # hydrogen X
        dy[self.idx.X_h2]   = q_in/self.p.V_liq*(yin.X_h2 - y[self.idx.X_h2]) + self.p.Y_h2*ro_up_h2 - ro_dec_h2
        # inert X
        dy[self.idx.X_I]    = q_in/self.p.V_liq*(yin.X_I - y[self.idx.X_I]) + self.p.f_xI_xc*ro_dis
        # cation
        dy[self.idx.S_cat]  = q_in/self.p.V_liq*(yin.S_cat - y[self.idx.S_cat])
        # anion
        dy[self.idx.S_an]   = q_in/self.p.V_liq*(yin.S_an - y[self.idx.S_an])
        # ions
        dy[self.idx.S_va_ion]  = -ro_A_va
        dy[self.idx.S_bu_ion]  = -ro_A_bu
        dy[self.idx.S_pro_ion] = -ro_A_pro
        dy[self.idx.S_ac_ion]  = -ro_A_ac
        dy[self.idx.S_hco3]    = -ro_A_IC
        dy[self.idx.S_nh3]     = -ro_A_IN
        # gas
        dy[self.idx.S_h2_gas]  = -gas_flow.q_gas/self.p.V_gas*y[self.idx.S_h2_gas]  + gas_rate.ro_T_h2 *self.p.V_liq/self.p.V_gas
        dy[self.idx.S_ch4_gas] = -gas_flow.q_gas/self.p.V_gas*y[self.idx.S_ch4_gas] + gas_rate.ro_T_ch4*self.p.V_liq/self.p.V_gas
        dy[self.idx.S_co2_gas] = -gas_flow.q_gas/self.p.V_gas*y[self.idx.S_co2_gas] + gas_rate.ro_T_co2*self.p.V_liq/self.p.V_gas

        if hasattr(self.idx, 'S_o2_gas'):
            dy[self.idx.S_o2_gas] = -gas_flow.q_gas/self.p.V_gas*y[self.idx.S_o2_gas] + gas_rate.ro_T_o2*self.p.V_liq/self.p.V_gas

        # h_ion
        if hasattr(self.idx, 'S_h_ion'):
            num = (dy[self.idx.S_an] + dy[self.idx.S_IN]*self.p.K_a_IN/(self.p.K_a_IN + sh) + 
                   dy[self.idx.S_IC]*self.p.K_a_co2/(self.p.K_a_co2 + sh) + 
                   (1/64)*dy[self.idx.S_ac]*self.p.K_a_ac/(self.p.K_a_ac + sh) + 
                   (1/112)*dy[self.idx.S_pro]*self.p.K_a_pro/(self.p.K_a_pro + sh) +
                   (1/160)*dy[self.idx.S_bu]*self.p.K_a_bu/(self.p.K_a_bu + sh) + 
                   (1/208)*dy[self.idx.S_va]*self.p.K_a_va/(self.p.K_a_va + sh) - 
                   dy[self.idx.S_IN] - dy[self.idx.S_cat])
        
            den = (1 + self.p.K_a_IN *y[self.idx.S_IN]/((self.p.K_a_IN  + sh)**2) +
                   self.p.K_a_co2*y[self.idx.S_IC]/((self.p.K_a_co2 + sh)**2) +
                   (1/64) *self.p.K_a_ac *y[self.idx.S_ac]  /((self.p.K_a_ac  + sh)**2) +
                   (1/112)*self.p.K_a_pro*y[self.idx.S_pro] /((self.p.K_a_pro + sh)**2) +
                   (1/160)*self.p.K_a_bu *y[self.idx.S_bu]  /((self.p.K_a_bu  + sh)**2) +
                   (1/208)*self.p.K_a_va *y[self.idx.S_va]  /((self.p.K_a_va  + sh)**2) +
                   self.p.K_w/(sh**2))
            
            dy[self.idx.S_h_ion] = num/den

        # Cumulative gas production ODEs
        if hasattr(self.idx, 'V_gas_cum'):
            dy[self.idx.V_gas_cum] = gas_flow.q_gas
            dy[self.idx.V_ch4_cum] = gas_flow.q_ch4

        return dy, gas_flow, inh, sh, gas_rate