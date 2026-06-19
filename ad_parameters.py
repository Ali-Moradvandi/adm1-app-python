#model parameters
from dataclasses import dataclass, field
import math

@dataclass
class parameter:

    Temp: int
    
    #stoichimetry parameters
    f_sI_xc :float = 0.1           #0.0
    f_xI_xc :float = 0.2           #0.1
    f_ch_xc :float = 0.2           #0.275
    f_pr_xc :float = 0.2           #0.275
    f_li_xc :float = 0.3           #0.350          #Note: 1 - f_sI_xc - f_xI_xc - f_ch_xc - f_pr_xc - f_li_xc == 0
    N_xc    :float = 0.0376/14.0   #0.006153       #kmol N / kg COD
    N_I     :float = 0.06/14.0     #N_sI/14.0      #kmol N / kg COD
    N_aa    :float = 0.007         #0.007903       #kmol N / kg COD
    C_xc    :float = 0.02786       #0.03051        #kmol C / kg COD
    C_sI    :float = 0.03          #C_sI/12.0      #kmol C / kg COD
    C_ch    :float = 0.0313        #0.03125        #kmol C / kg COD
    C_pr    :float = 0.03          #0.03074        #kmol C / kg COD
    C_li    :float = 0.022         #0.021926       #kmol C / kg COD
    C_xI    :float = 0.03          #C_sI/12.0      #kmol C / kg COD
    #-----------------------------------------------------------------------------------------------------#
    C_su    :float = 0.0313        #0.03125        #kmol C / kg COD
    #-----------------------------------------------------------------------------------------------------#
    C_aa    :float = 0.03          #0.03074        #kmol C / kg COD
    #-----------------------------------------------------------------------------------------------------#
    f_fa_li :float = 0.95          #0.95
    C_fa    :float = 0.0217        #0.02140        #kmol C / kg COD
    #-----------------------------------------------------------------------------------------------------#
    f_h2_su :float = 0.19          #0.1906
    f_bu_su :float = 0.13          #0.1328
    f_pro_su:float = 0.27          #0.2691
    f_ac_su :float = 0.41          #0.4076
    N_bac   :float = 0.08/14.0     #N_BM/14.0      #kmol N / kg COD
    C_bu    :float = 0.025         #0.025          #kmol C / kg COD
    C_pro   :float = 0.0268        #0.02678        #kmol C / kg COD
    C_ac    :float = 0.0313        #0.03125        #kmol C / kg COD
    C_bac   :float = 0.0313        #C_XB/12        #kmol C / kg COD
    Y_su    :float = 0.1
    #-----------------------------------------------------------------------------------------------------#
    f_h2_aa :float = 0.06          #0.06
    f_va_aa :float = 0.23          #0.23
    f_bu_aa :float = 0.26          #0.26
    f_pro_aa:float = 0.05          #0.05
    f_ac_aa :float = 0.40          #0.40
    C_va    :float = 0.024         #0.02404        #kmol C / kg COD
    Y_aa    :float = 0.08          #0.08
    #-----------------------------------------------------------------------------------------------------#
    Y_fa    :float = 0.06          #0.06
    #-----------------------------------------------------------------------------------------------------#
    Y_c4    :float = 0.06          #0.06
    #-----------------------------------------------------------------------------------------------------#
    Y_pro   :float = 0.04          #0.04
    #-----------------------------------------------------------------------------------------------------#
    C_ch4   :float = 0.0156        #0.01563        #kmol C / kg COD
    Y_ac    :float = 0.05          #0.05
    #-----------------------------------------------------------------------------------------------------#
    Y_h2    :float = 0.06          #0.06
    #Oxygen stoichiometry---------------------------------------------------------------------------------#
    #Ox1
    C_1     :float = 0.03125                       #kmol
    C_2     :float = 0.03000                       #kmol
    C_3     :float = 0.02170                       #kmol
    Y_su_aer:float = 0.5
    Y_fa_aer:float = 0.3
    Y_aa_aer:float = 0.4
    O_su_aer:float = -1.1
    O_aa_aer:float = -1.2
    O_fa_aer:float = -2.03
    #Ox2
    C_va_aer:float = 0.0240                        #kmol
    C_bu_aer:float = 0.0250                        #kmol
    C_pro_aer:float= 0.0268                        #kmol
    C_ac_aer:float = 0.0313                        #kmol
    Y_va_aer:float = 0.3 
    Y_bu_aer:float = 0.3
    Y_pro_aer:float= 0.2
    Y_ac_aer:float = 0.25           #0.89
    O_va_aer:float = -2.04
    O_bu_aer:float = -1.82
    O_pro_aer:float= -1.51
    O_ac_aer:float = -1.07

    #Biochemical parameters
    k_dis         : float = field(init=False)            #1/d
    k_hyd_ch_base : float = field(init=False)            #1/d
    k_hyd_pr_base : float = field(init=False)            #1/d
    k_hyd_li_base : float = field(init=False)            #1/d
    #-----------------------------------------------------------------------------------------------------#
    K_S_IN        : float = field(init=False)            #M
    #-----------------------------------------------------------------------------------------------------#
    k_m_su_base   : float = field(init=False)            #1/d
    K_S_su        : float = field(init=False)            #kg COD/ m^3
    pH_UL_aa      : float = field(init=False)
    pH_LL_aa      : float = field(init=False)
    #-----------------------------------------------------------------------------------------------------#
    k_m_aa_base   : float = field(init=False)            #1/d
    K_S_aa        : float = field(init=False)            #kg COD/ m^3
    #-----------------------------------------------------------------------------------------------------#
    k_m_fa_base   : float = field(init=False)            #1/d
    K_S_fa        : float = field(init=False)            #kg COD/ m^3
    K_Ih2_fa      : float = field(init=False)            #kg COD/ m^3
    #-----------------------------------------------------------------------------------------------------#
    k_m_c4_base   : float = field(init=False)            #1/d
    K_S_c4        : float = field(init=False)            #kg COD/ m^3
    K_Ih2_c4      : float = field(init=False)            #kg COD/ m^3
    #-----------------------------------------------------------------------------------------------------#
    k_m_pro_base  : float = field(init=False)            #1/d
    K_S_pro       : float = field(init=False)            #kg COD/ m^3
    K_Ih2_pro     : float = field(init=False)            #kg COD/ m^3
    #-----------------------------------------------------------------------------------------------------#
    k_m_ac_base   : float = field(init=False)            #1/d
    K_S_ac        : float = field(init=False)            #kg COD/ m^3
    K_I_nh3       : float = field(init=False)            #M
    pH_UL_ac      : float = field(init=False)
    pH_LL_ac      : float = field(init=False)
    #-----------------------------------------------------------------------------------------------------#
    k_m_h2_base   : float = field(init=False)            #1/d
    K_S_h2        : float = field(init=False)            #kg COD/ m^3
    pH_UL_h2      : float = field(init=False)
    pH_LL_h2      : float = field(init=False)
    #-----------------------------------------------------------------------------------------------------#
    k_dec_Xsu     : float = field(init=False)            #1/d
    k_dec_Xaa     : float = field(init=False)            #1/d
    k_dec_Xfa     : float = field(init=False)            #1/d
    k_dec_Xc4     : float = field(init=False)            #1/d
    k_dec_Xpro    : float = field(init=False)            #1/d
    k_dec_Xac     : float = field(init=False)            #1/d
    k_dec_Xh2     : float = field(init=False)            #1/d
    #Oxygen related---------------------------------------------------------------------------------#
    #Ox1
    k_m_aa_aer    : float = field(init=False)            #1/d
    k_m_fa_aer    : float = field(init=False)            #1/d
    k_m_su_aer    : float = field(init=False)            #1/d
    K_S_aa_aer    : float = field(init=False)            #kg COD/ m^3
    K_S_fa_aer    : float = field(init=False)            #kg COD/ m^3
    K_S_su_aer    : float = field(init=False)            #kg COD/ m^3
    K_I_o2        : float = field(init=False)            #kmol O2/m^3        #Note: in ADM1-S/O it's 0.25
    #Ox2
    K_S_va_aer    : float = field(init=False)            #Note: 20% of values used in the feremntation
    K_S_bu_aer    : float = field(init=False)
    K_S_pro_aer   : float = field(init=False)
    K_S_ac_aer    : float = field(init=False)

    #Coefficients for dynamic kinetics-----------------------------------------------------------------#
    k_hyd_ch_in :float = 0                    #1/d
    k_hyd_pr_in :float = 0
    k_hyd_li_in :float = 0
    k_m_su_in   :float = 0
    k_m_aa_in   :float = 0
    k_m_fa_in   :float = 0
    k_m_c4_in   :float = 0
    k_m_pro_in  :float = 0
    k_m_ac_in   :float = 0
    k_m_h2_in   :float = 0

    k_hyd_ch_acc:float = 0.039                 #1/d^2
    k_hyd_pr_acc:float = 0.039
    k_hyd_li_acc:float = 0.039
    k_m_su_acc  :float = 0.088
    k_m_aa_acc  :float = 0.025
    k_m_fa_acc  :float = 0.025
    k_m_c4_acc  :float = 0.069
    k_m_pro_acc :float = 0.009
    k_m_ac_acc  :float = 0.063
    k_m_h2_acc  :float = 0.098

    t_hyd_ch_lag:float = 0                    #d
    t_hyd_pr_lag:float = 0
    t_hyd_li_lag:float = 0
    t_m_su_lag  :float = 0
    t_m_aa_lag  :float = 0
    t_m_fa_lag  :float = 0
    t_m_c4_lag  :float = 0
    t_m_pro_lag :float = 0
    t_m_ac_lag  :float = 0
    t_m_h2_lag  :float = 0

    #Physiochemical Parameter Values------------------------------------------------------------
    R           :float = 0.083145           #bar/M K
    T_base      :float = 298.15             #K
    T_feed      :float = 308.15             #K        # Temperature of influent
    T_op        :float = field(init=False)
    #-----------------------------------------------------------------------------------------------------#
    pK_w_base    :float = 13.997             #14
    pK_a_va_base :float = 4.86
    pK_a_bu_base :float = 4.82
    pK_a_pro_base:float = 4.88
    pK_a_ac_base :float = 4.76
    pK_a_co2_base:float = 6.35
    pK_a_IN_base :float = 9.25
    #-----------------------------------------------------------------------------------------------------#
    k_A_Bva      :float = 1.0e10            #1/ M d
    k_A_Bbu      :float = 1.0e10            #1/ M d
    k_A_Bpro     :float = 1.0e10            #1/ M d
    k_A_Bac      :float = 1.0e10            #1/ M d
    k_A_Bco2     :float = 1.0e10            #1/ M d
    k_A_BIN      :float = 1.0e10            #1/ M d
    #-----------------------------------------------------------------------------------------------------#
    K_H_h2o_base :float = 0.0313
    K_H_co2_base :float = 0.035
    K_H_ch4_base :float = 0.0014
    K_H_h2_base  :float = 7.8e-4
    K_H_o2_base  :float = 1.3e-3
    #-----------------------------------------------------------------------------------------------------#
    P_atm        :float = 1.013             #bar
    k_P          :float = 5.0e4             #m^3/d bar
    #-----------------------------------------------------------------------------------------------------#
    kLa_base     :float = 200               #1/d
    F_corr_kla   :float = 1
    #Oxygen related---------------------------------------------------------------------------------------#
    KLa_o2_base  :float = 0.000
    theta        :float = 1.024             # appendix adm1-s/o    
    #Physical Parameter Values---------------------------------------------------------------------------------
    V_liq        :float = 3400              #m^3
    V_gas        :float = 300               #m^3
   
    def __post_init__(self):
        
        if self.Temp == 35:
            self.k_dis         = 0.5
            self.k_hyd_ch_base = 10.0
            self.k_hyd_pr_base = 10.0
            self.k_hyd_li_base = 10.0
            #-----------------------------------------------------------------------------------------------------#
            self.K_S_IN        = 1.0e-4
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_su_base   = 30.0
            self.K_S_su        = 0.5
            self.pH_UL_aa      = 5.5
            self.pH_LL_aa      = 4.0
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_aa_base   = 50.0
            self.K_S_aa        = 0.3
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_fa_base   = 6.0
            self.K_S_fa        = 0.4
            self.K_Ih2_fa      = 5.0e-6
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_c4_base   = 20.0
            self.K_S_c4        = 0.2
            self.K_Ih2_c4      = 1.0e-5
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_pro_base  = 13.0
            self.K_S_pro       = 0.1
            self.K_Ih2_pro     = 3.5e-6
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_ac_base   = 8.0
            self.K_S_ac        = 0.15
            self.K_I_nh3       = 0.0018
            self.pH_UL_ac      = 7.0
            self.pH_LL_ac      = 6.0
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_h2_base   = 35.0
            self.K_S_h2        = 7.0e-6
            self.pH_UL_h2      = 6.0
            self.pH_LL_h2      = 5.0
            #-----------------------------------------------------------------------------------------------------#
            self.k_dec_Xsu     = 0.02
            self.k_dec_Xaa     = 0.02
            self.k_dec_Xfa     = 0.02
            self.k_dec_Xc4     = 0.02
            self.k_dec_Xpro    = 0.02
            self.k_dec_Xac     = 0.02
            self.k_dec_Xh2     = 0.02
            #Oxygen related---------------------------------------------------------------------------------#
            #Ox1
            self.k_m_aa_aer    = 50.0
            self.k_m_fa_aer    = 6.0
            self.k_m_su_aer    = 30.0
            self.K_S_aa_aer    = 0.06
            self.K_S_fa_aer    = 0.08
            self.K_S_su_aer    = 0.1
            self.K_I_o2        = 0.2    
            #Ox2
            self.K_S_va_aer    = 0.04
            self.K_S_bu_aer    = 0.04
            self.K_S_pro_aer   = 0.02
            self.K_S_ac_aer    = 0.03
        elif self.Temp == 55:
            self.k_dis         = 1.0
            self.k_hyd_ch_base = 10.0
            self.k_hyd_pr_base = 10.0
            self.k_hyd_li_base = 10.0
            #-----------------------------------------------------------------------------------------------------#
            self.K_S_IN        = 1.0e-4
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_su_base   = 70.0
            self.K_S_su        = 1.0
            self.pH_UL_aa      = 5.5  
            self.pH_LL_aa      = 4.0  
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_aa_base   = 70.0
            self.K_S_aa        = 0.3
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_fa_base   = 10.0
            self.K_S_fa        = 0.4
            self.K_Ih2_fa      = 5.0e-6
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_c4_base   = 30.0
            self.K_S_c4        = 0.4
            self.K_Ih2_c4      = 3.0e-5
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_pro_base  = 20.0
            self.K_S_pro       = 0.3
            self.K_Ih2_pro     = 1.0e-5
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_ac_base   = 16.0
            self.K_S_ac        = 0.30
            self.K_I_nh3       = 0.011
            self.pH_UL_ac      = 7.0 
            self.pH_LL_ac      = 6.0
            #-----------------------------------------------------------------------------------------------------#
            self.k_m_h2_base   = 35.0
            self.K_S_h2        = 5.0e-5
            self.pH_UL_h2      = 6.0
            self.pH_LL_h2      = 5.0
            #-----------------------------------------------------------------------------------------------------#
            self.k_dec_Xsu     = 0.04
            self.k_dec_Xaa     = 0.04
            self.k_dec_Xfa     = 0.04
            self.k_dec_Xc4     = 0.04
            self.k_dec_Xpro    = 0.04
            self.k_dec_Xac     = 0.04
            self.k_dec_Xh2     = 0.04
            #Oxygen related----------------------------------------------------------------------------------------#
            #Ox1
            self.k_m_aa_aer    = 70.0
            self.k_m_fa_aer    = 10.0
            self.k_m_su_aer    = 70.0
            self.K_S_aa_aer    = 0.06
            self.K_S_fa_aer    = 0.08
            self.K_S_su_aer    = 0.2
            self.K_I_o2        = 0.2
            #Ox2
            self.K_S_va_aer    = 0.08
            self.K_S_bu_aer    = 0.08       
            self.K_S_pro_aer   = 0.03
            self.K_S_ac_aer    = 0.03
        
        self.T_op = self.Temp + 273.15
        self.K_w          = 10.0**-self.pK_w_base * math.exp(55900/(self.R*100)*(1/self.T_base - 1/self.T_op))   #M
        self.K_a_va       = 10.0**-self.pK_a_va_base                                                             #M
        self.K_a_bu       = 10.0**-self.pK_a_bu_base                                                             #M
        self.K_a_pro      = 10.0**-self.pK_a_pro_base                                                            #M
        self.K_a_ac       = 10.0**-self.pK_a_ac_base                                                             #M
        self.K_a_co2      = 10.0**-self.pK_a_co2_base * math.exp(7646/(self.R*100)*(1/self.T_base - 1/self.T_op))    #M
        self.K_a_IN       = 10.0**-self.pK_a_IN_base  * math.exp(51965/(self.R*100)*(1/self.T_base - 1/self.T_op))   #M

        self.p_gas_h2o    = self.K_H_h2o_base * math.exp(5290*(1/self.T_base - 1/self.T_op))
        self.K_H_co2      = self.K_H_co2_base * math.exp(-19410/(self.R*100)*(1/self.T_base - 1/self.T_op))               #Mliq/bar
        self.K_H_ch4      = self.K_H_ch4_base * math.exp(-14240/(self.R*100)*(1/self.T_base - 1/self.T_op))               #Mliq/bar
        self.K_H_h2       = self.K_H_h2_base  * math.exp(-4180/(self.R*100)*(1/self.T_base - 1/self.T_op))                #Mliq/bar
        self.K_H_o2       = self.K_H_o2_base  * math.exp(-1700*(1/self.T_base - 1/self.T_op))                             #Mliq/bar
        
    