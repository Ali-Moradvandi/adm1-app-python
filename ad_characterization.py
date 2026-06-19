# characterization
from ad_influent import influent
from ad_initial_conditions import initial


def characterize_system(tCOD, VS, sub_type, mode="continuous", batch_type="fed", BMP=None, sludge_tCOD=None):
       
    # Group 1: Assumed fractions [f_ch, f_pr, f_li, f_xI, f_su, f_aa, f_fa, f_vfa, f_sI]
    group1 = {
        "default":        [0.25, 0.25, 0.25, 0.25],
        "cellulose":      [0.95, 0.00, 0.00, 0.05],
        "chicken manure": [0.25, 0.40, 0.10, 0.25],
        "potato starch":  [0.80, 0.10, 0.05, 0.05]
    }
    
    # Group 2: Reference-based fractions
    group2 = {
        "black water":            [0.198, 0.198, 0.254, 0.350, None, None, 0.213, 0.213, None],
        "grass silage":           [0.401, 0.187, 0.033, 0.379, None, None, None, None, None],
        "olive mill solid waste": [0.359, 0.076, 0.103, 0.462, None, None, None, None, None],
        "pear pulp":              [0.630, 0.025, 0.133, 0.212, None, None, None, None, 0.367],
        "sunflower":              [0.620, 0.243, 0.042, 0.095, None, None, None, None, 0.184] 
    }

    fractions = {**group1, **group2}
    sub_key = sub_type.lower()
    is_all_fraction_given = sub_key in group2
    raw_fracs = fractions.get(sub_key, group1["default"])

    yin = influent()
    yin.X_xc = 0.0

    if is_all_fraction_given:
        f_ch, f_pr, f_li, f_xI, f_su, f_aa, f_fa, f_vfa, f_sI = raw_fracs
        
        yin.X_ch = tCOD * f_ch
        yin.X_pr = tCOD * f_pr
        yin.X_li = tCOD * f_li
        yin.X_I  = tCOD * f_xI
        
        if f_su is not None:  yin.S_su = tCOD * f_su
        if f_aa is not None:  yin.S_aa = tCOD * f_aa
        if f_fa is not None:  yin.S_fa = tCOD * f_fa
        if f_vfa is not None: yin.S_ac = tCOD * f_vfa 
        if f_sI is not None:  yin.S_I  = tCOD * f_sI

    else:
        f_ch, f_pr, f_li, f_xI = fractions.get(sub_type.lower(), fractions["default"])
        
        # Set universal particulate assumption
        pCOD = 0.95 * tCOD
        
        # BIODEGRADABILITY AND CROSS-CHECKS
        if BMP is not None:
            # Step 3: BMP is given
            fd = (BMP * VS) / (350.0 * tCOD)
            XI = pCOD * (1.0 - fd)
            
            # Check deviation from assumed inert fraction
            calc_f_xI = XI / pCOD if pCOD > 0 else 0
            deviation = abs(calc_f_xI - f_xI)
            
            # Recalibrate if deviated (threshold > 0.01)
            if deviation > 0.01:
                remaining_biodegradable = 1.0 - calc_f_xI
                old_sum = f_ch + f_pr + f_li
                
                if old_sum > 0:
                    f_ch = f_ch * (remaining_biodegradable / old_sum)
                    f_pr = f_pr * (remaining_biodegradable / old_sum)
                    f_li = f_li * (remaining_biodegradable / old_sum)
                f_xI = calc_f_xI
                
        else:
            # BMP is NOT given
            XI = pCOD * f_xI
    
        # Apply fractions to particulate COD
        yin.X_ch = pCOD * f_ch
        yin.X_pr = pCOD * f_pr
        yin.X_li = pCOD * f_li
        yin.X_I  = XI
        
        # Cross Check Reporting
        xCOD1 = tCOD - yin.X_I
        xCOD2 = VS * ((f_ch * 1.07) + (f_pr * 1.4) + (f_li * 2.9))
    
        # print(f"--- Characterization Cross-Check ({sub_type}) ---")
        # print(f"xCOD1 (tCOD - XI): {xCOD1:.4f}")
        # print(f"xCOD2 (VS * factors): {xCOD2:.4f}")
    

    # SLUDGE CHARACTERIZATION (For Batch Mode)
    y0 = initial()
    
    if mode.lower() == "batch" and sludge_tCOD is not None:

        sludge_XI = 0.60 * sludge_tCOD
        sludge_Xxc = 0.25 * sludge_tCOD
        sludge_SI = 0.05 * sludge_tCOD
        
        biomass_each = (0.10 * sludge_tCOD) / 7.0

        if batch_type.lower() == "blank":

            y0.X_ch = 1e-8
            y0.X_pr = 1e-8
            y0.X_li = 1e-8
            y0.X_I  = sludge_XI
            y0.S_I  = sludge_SI 
            

        elif batch_type.lower() in ["positive", "fed"]:
        
            y0.X_ch = yin.X_ch
            y0.X_pr = yin.X_pr 
            y0.X_li = yin.X_li
            y0.X_I  = yin.X_I + sludge_XI
            y0.S_I  = yin.S_I + sludge_SI

        y0.X_xc  = sludge_Xxc   
        y0.X_su  = biomass_each 
        y0.X_aa  = biomass_each 
        y0.X_fa  = biomass_each 
        y0.X_c4  = biomass_each 
        y0.X_pro = biomass_each 
        y0.X_ac  = biomass_each 
        y0.X_h2  = biomass_each
            
    elif mode.lower() == "continuous":
        pass 

    return yin, y0