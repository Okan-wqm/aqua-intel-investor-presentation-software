"""
Carbonate chemistry calculations for Deffeyes diagram.
Ported from CarbCalc.R (iQuaCalc) — Millero et al. (2006), Mucci (1983).
All internal calculations on FREE pH scale; user input assumed NBS.
Temperature passed as Celsius, converted to Kelvin internally.
"""
import math


# ── Helpers ──────────────────────────────────────────────────────────────────

def _ionic_strength(sal):
    """Ionic strength (molal) from salinity."""
    return 19.924 * sal / (1000.0 - 1.005 * sal)


def _calc_ts(sal):
    return 0.0008067267 * sal


def _calc_tf(sal):
    return 0.0000019522 * sal


def _calc_ks_dickson(tk, sal):
    """Bisulfate dissociation (Dickson 1990), FREE scale, mol/kg-soln."""
    mu = _ionic_strength(sal)
    sf1 = 141.328 - 4276.1 / tk
    sf2 = -23.093 * math.log(tk)
    sf3 = (324.57 - 47.986 * math.log(tk) - 13856.0 / tk) * math.sqrt(mu)
    sf4 = (-771.54 + 114.723 * math.log(tk) + 35474.0 / tk) * mu
    sf5 = -2698.0 * mu**1.5 / tk
    sf6 = 1776.0 * mu**2 / tk
    m2m = math.log(1.0 - 0.001005 * sal)
    return math.exp(sf1 + sf2 + sf3 + sf4 + sf5 + sf6 + m2m)


def _calc_kf_dickson(tk, sal):
    """Fluoride dissociation (Dickson & Riley), FREE scale."""
    mu = _ionic_strength(sal)
    ff1 = 1590.2 / tk
    ff2 = -12.641
    ff3 = 1.525 * math.sqrt(mu)
    m2m = math.log(1.0 - 0.001005 * sal)
    return math.exp(ff1 + ff2 + ff3 + m2m)


def _ah_free_to_sws(sal, tk):
    ks = _calc_ks_dickson(tk, sal)
    kf = _calc_kf_dickson(tk, sal)
    return 1.0 + (_calc_ts(sal) / ks) + (_calc_tf(sal) / kf)


def _ah_free_to_tot(sal, tk):
    ks = _calc_ks_dickson(tk, sal)
    return 1.0 + (_calc_ts(sal) / ks)


def _proton_activity_coeff(tk, sal):
    mu = _ionic_strength(sal)
    root_mu = math.sqrt(mu)
    fh = 1820000.0 * (79.0 * tk)**(-1.5)
    fh = fh * ((root_mu / (1.0 + root_mu)) - 0.2 * mu)
    return 10.0**(-fh)


def _ah_sws_to_nbs(sal, tk):
    return _proton_activity_coeff(tk, sal) / (1.0 - 0.001005 * sal)


def ph_nbs_to_free(ph_nbs, sal, tk):
    """Convert pH from NBS scale to FREE scale."""
    return (ph_nbs
            + math.log10(_ah_sws_to_nbs(sal, tk))
            + math.log10(_ah_free_to_sws(sal, tk)))


# ── Equilibrium Constants (returned on FREE pH scale) ───────────────────────

def calc_k1(tk, sal):
    """K1 carbonic acid, Millero (2006). SWS→FREE."""
    sqrt_s = math.sqrt(sal)
    ln_t = math.log(tk)
    pk1z = -126.34048 + 6320.813 / tk + 19.568224 * ln_t
    a = 13.4191 * sqrt_s + 0.0331 * sal - 5.33e-5 * sal * sal
    b = -530.123 * sqrt_s - 6.103 * sal
    c = -2.06950 * sqrt_s
    pk1 = pk1z + a + b / tk + c * ln_t
    # SWS → FREE
    pk1 += math.log10(_ah_free_to_sws(sal, tk))
    return 10.0**(-pk1)


def calc_k2(tk, sal):
    """K2 carbonic acid, Millero (2006). SWS→FREE."""
    sqrt_s = math.sqrt(sal)
    ln_t = math.log(tk)
    pk2z = -90.18333 + 5143.692 / tk + 14.613358 * ln_t
    a = 21.0894 * sqrt_s + 0.1248 * sal - 3.687e-4 * sal * sal
    b = -772.483 * sqrt_s - 20.051 * sal
    c = -3.3336 * sqrt_s
    pk2 = pk2z + a + b / tk + c * ln_t
    pk2 += math.log10(_ah_free_to_sws(sal, tk))
    return 10.0**(-pk2)


def calc_kw(tk, sal):
    """Kw, Dickson & Goyet (1994), TOTAL→FREE."""
    ln_kw = (148.9652 - 13847.26 / tk - 23.6521 * math.log(tk)
             + (-5.977 + 118.67 / tk + 1.0495 * math.log(tk)) * math.sqrt(sal)
             - 0.01615 * sal)
    kw_tot = math.exp(ln_kw)
    pkw_tot = -math.log10(kw_tot)
    pkw_free = pkw_tot + math.log10(_ah_free_to_tot(sal, tk))
    return 10.0**(-pkw_free)


def calc_kb(tk, sal):
    """Borate dissociation constant, FREE scale."""
    sqrt_s = math.sqrt(sal)
    a = 148.0248 + 137.1942 * sqrt_s + 1.62142 * sal
    b = -8966.90 - 2890.53 * sqrt_s - 77.942 * sal + 1.728 * sal**1.5 - 0.0996 * sal * sal
    c = -24.4344 - 25.085 * sqrt_s - 0.2474 * sal
    d = 0.053105 * sqrt_s
    k_boh3 = math.exp(a + b / tk + c * math.log(tk) + d * tk)
    pk = -math.log10(k_boh3) + math.log10(_ah_free_to_tot(sal, tk))
    return 10.0**(-pk)


def calc_knh4(tk, sal):
    """NH4+ dissociation, Millero (1995). SWS→FREE."""
    sqrt_s = math.sqrt(sal)
    a = -0.25444 + 0.46532 * sqrt_s - 0.01992 * sal
    b = -6285.33 - 123.7184 * sqrt_s + 3.17556 * sal
    d = 0.0001635
    ln_k = a + b / tk + d * tk
    pk = -math.log10(math.exp(ln_k))
    pk_free = pk + math.log10(_ah_free_to_sws(sal, tk))
    return 10.0**(-pk_free)


# ── Borate concentration ────────────────────────────────────────────────────

def borate_conc(sal):
    return 0.000232 * sal / (10.811 * 1.80655)


def calc_borate(ph_free, tk, sal):
    conc_b = borate_conc(sal)
    kb = calc_kb(tk, sal)
    h = 10.0**(-ph_free)
    return kb * conc_b / (kb + h)


# ── Density (UNESCO EOS-80) ─────────────────────────────────────────────────

def calc_rho_fw(tk):
    t = tk - 273.15
    rho = 999.842594 + 0.06793952 * t
    rho += -0.009095290 * t * t
    rho += 1.001685e-4 * t**3
    rho += -1.120083e-6 * t**4
    rho += 6.536332e-9 * t**5
    return rho


def calc_rho(tk, sal):
    t = tk - 273.15
    a = 0.824493 - 0.0040899 * t + 7.6438e-5 * t * t - 8.2467e-7 * t**3 + 5.3875e-9 * t**4
    b = -0.00572466 + 1.0227e-4 * t - 1.6546e-6 * t * t
    c = 4.8314e-4
    return calc_rho_fw(tk) + a * sal + b * sal**1.5 + c * sal * sal


# ── Ksp (Mucci 1983) ────────────────────────────────────────────────────────

def calc_ksp_calcite(tk, sal):
    sqrt_s = math.sqrt(sal)
    log_ksp = (-171.9065 - 0.77712 * sqrt_s - 0.07711 * sal
               + 0.0041249 * sal**1.5
               + (2839.319 + 178.34 * sqrt_s) / tk
               + 71.595 * math.log10(tk)
               + (-0.077993 + 0.0028426 * sqrt_s) * tk)
    return 10.0**log_ksp


def calc_ksp_aragonite(tk, sal):
    sqrt_s = math.sqrt(sal)
    log_ksp = (-171.945 - 0.068393 * sqrt_s - 0.10018 * sal
               + 0.0059415 * sal**1.5
               + (2903.293 + 88.135 * sqrt_s) / tk
               + 71.595 * math.log10(tk)
               + (-0.077993 + 0.0017276 * sqrt_s) * tk)
    return 10.0**log_ksp


# ── Alpha fractions (FREE scale pH) ─────────────────────────────────────────

def _alpha_denom(h, k1, k2):
    return h * h + k1 * h + k1 * k2


def alpha_zero(h, k1, k2):
    return (h * h) / _alpha_denom(h, k1, k2)


def alpha_one(h, k1, k2):
    return (k1 * h) / _alpha_denom(h, k1, k2)


def alpha_two(h, k1, k2):
    return (k1 * k2) / _alpha_denom(h, k1, k2)


# ── Alkalinity & DIC (all on FREE scale) ────────────────────────────────────

def calc_alk_of_dic(dic, ph_free, tk, sal):
    """Alkalinity (mol/kg) from DIC (mol/kg) and pH (FREE)."""
    h = 10.0**(-ph_free)
    k1 = calc_k1(tk, sal)
    k2 = calc_k2(tk, sal)
    kw = calc_kw(tk, sal)
    a1 = alpha_one(h, k1, k2)
    a2 = alpha_two(h, k1, k2)
    alk = dic * (a1 + 2 * a2)
    alk += kw / h      # OH-
    alk -= h            # H+
    alk += calc_borate(ph_free, tk, sal)
    return alk


def calc_dic_of_alk(alk, ph_free, tk, sal):
    """DIC (mol/kg) from alkalinity (mol/kg) and pH (FREE)."""
    h = 10.0**(-ph_free)
    k1 = calc_k1(tk, sal)
    k2 = calc_k2(tk, sal)
    kw = calc_kw(tk, sal)
    m = alpha_one(h, k1, k2) + 2 * alpha_two(h, k1, k2)
    dic = (alk - kw / h + h - calc_borate(ph_free, tk, sal)) / m
    return dic


# ── Ca conversion ───────────────────────────────────────────────────────────

def ca_mg_l_to_mol_kg(ca_mg_l, tk, sal):
    """Convert Ca from mg/L to mol/kg-soln."""
    return ca_mg_l / 40.078 / calc_rho(tk, sal)


# ── CO2 boundary (from R: calcPhForCritCO2FromDIC) ──────────────────────────

def calc_ph_for_crit_co2(dic_mol, co2_crit_mol, tk, sal):
    """pH (FREE) where CO2(aq) = co2_crit for given DIC. Quadratic solution."""
    if dic_mol <= co2_crit_mol:
        return None
    k1 = calc_k1(tk, sal)
    k2 = calc_k2(tk, sal)
    a = co2_crit_mol - dic_mol
    b = co2_crit_mol * k1
    c = co2_crit_mol * k1 * k2
    discrim = b * b - 4.0 * a * c
    if discrim < 0:
        return None
    x = (-b - math.sqrt(discrim)) / (2.0 * a)
    if x <= 0:
        return None
    return -math.log10(x)


# ── Omega boundary (from R: calcPhTotForOmegaCa — quadratic) ────────────────

def calc_ph_for_omega_ca(omega, dic_mol, ca_mol, tk, sal):
    """pH (FREE) for omega-calcite = omega at given DIC. Quadratic formula."""
    k1 = calc_k1(tk, sal)
    k2 = calc_k2(tk, sal)
    ksp = calc_ksp_calcite(tk, sal)
    q2 = 1.0
    q1 = k1
    q0 = k1 * k2 * (1.0 - (ca_mol * dic_mol) / (omega * ksp))
    discrim = q1 * q1 - 4.0 * q2 * q0
    if discrim < 0:
        return None
    root = (-q1 + math.sqrt(discrim)) / (2.0 * q2)
    if root <= 0:
        return None
    return -math.log10(root)


# ── TAN / Critical NH3 pH (from R: critPhFreeForTanMillero) ─────────────────

def calc_crit_ph_nh3(tan_mg_l, uia_limit_mg_l, tk, sal):
    """pH (FREE) at which UIA reaches the limit, Millero (1995)."""
    if tan_mg_l <= 0 or uia_limit_mg_l <= 0 or tan_mg_l <= uia_limit_mg_l:
        return None
    k_nh4 = calc_knh4(tk, sal)
    return -math.log10((tan_mg_l / uia_limit_mg_l) - 1.0) - math.log10(k_nh4)


# ── Chart data generation ───────────────────────────────────────────────────

def generate_ph_isopleths(tk, sal, dic_min_mmol, dic_max_mmol, ph_nbs_values):
    """Generate pH isopleth lines. Inputs: pH on NBS, DIC in mmol/kg."""
    isopleths = []
    steps = 60
    for ph_nbs in ph_nbs_values:
        ph_free = ph_nbs_to_free(ph_nbs, sal, tk)
        points = []
        for i in range(steps + 1):
            dic_mmol = dic_min_mmol + i * (dic_max_mmol - dic_min_mmol) / steps
            dic_mol = dic_mmol / 1000.0
            alk_mol = calc_alk_of_dic(dic_mol, ph_free, tk, sal)
            alk_meq = alk_mol * 1000.0
            points.append({'x': round(dic_mmol, 4), 'y': round(alk_meq, 4)})
        isopleths.append({'ph': ph_nbs, 'points': points})
    return isopleths


def generate_omega_boundary(tk, sal, ca_mol, dic_min_mmol, dic_max_mmol):
    """Omega = 1.0 boundary curve."""
    boundary = []
    steps = 80
    ksp = calc_ksp_calcite(tk, sal)
    # minimum DIC where omega=1 is possible
    dic_start = max(dic_min_mmol, 0.01)
    for i in range(steps + 1):
        dic_mmol = dic_start + i * (dic_max_mmol - dic_start) / steps
        dic_mol = dic_mmol / 1000.0
        ph_free = calc_ph_for_omega_ca(1.0, dic_mol, ca_mol, tk, sal)
        if ph_free is None:
            continue
        alk_mol = calc_alk_of_dic(dic_mol, ph_free, tk, sal)
        alk_meq = alk_mol * 1000.0
        boundary.append({'x': round(dic_mmol, 4), 'y': round(alk_meq, 4)})
    return boundary


def generate_uia_boundary(tk, sal, tan_mg_l, uia_limit_mg_l, dic_min_mmol, dic_max_mmol):
    """Toxic NH3 boundary — a single pH isopleth at critical pH."""
    crit_ph_free = calc_crit_ph_nh3(tan_mg_l, uia_limit_mg_l, tk, sal)
    if crit_ph_free is None:
        return None
    # Convert back to approximate NBS for display
    # ph_nbs ≈ ph_free - log10(ahFreeToSws) - log10(ahSwsToNbs)
    sf = (math.log10(_ah_free_to_sws(sal, tk))
          + math.log10(_ah_sws_to_nbs(sal, tk)))
    ph_nbs_approx = crit_ph_free - sf

    steps = 60
    points = []
    for i in range(steps + 1):
        dic_mmol = dic_min_mmol + i * (dic_max_mmol - dic_min_mmol) / steps
        dic_mol = dic_mmol / 1000.0
        alk_mol = calc_alk_of_dic(dic_mol, crit_ph_free, tk, sal)
        alk_meq = alk_mol * 1000.0
        points.append({'x': round(dic_mmol, 4), 'y': round(alk_meq, 4)})
    return {'critical_ph': round(ph_nbs_approx, 2), 'points': points}


def generate_co2_boundary(tk, sal, co2_limit_mg_l, dic_min_mmol, dic_max_mmol):
    """CO2 danger zone boundary."""
    if co2_limit_mg_l <= 0:
        return None
    co2_crit_mol = co2_limit_mg_l / 44009.6  # mg/L → mol/kg (approx, using mg/kg ≈ mg/L for density ~1)
    # Better: convert using density
    rho = calc_rho(tk, sal)
    co2_crit_mol = (co2_limit_mg_l / rho) / 44.0096  # mg/L → g/kg → mol/kg

    steps = 60
    points = []
    for i in range(steps + 1):
        dic_mmol = dic_min_mmol + i * (dic_max_mmol - dic_min_mmol) / steps
        dic_mol = dic_mmol / 1000.0
        ph_free = calc_ph_for_crit_co2(dic_mol, co2_crit_mol, tk, sal)
        if ph_free is None:
            continue
        alk_mol = calc_alk_of_dic(dic_mol, ph_free, tk, sal)
        alk_meq = alk_mol * 1000.0
        points.append({'x': round(dic_mmol, 4), 'y': round(alk_meq, 4)})

    if not points:
        return None
    return {'points': points}


# ── Reagent adjustment (from adjustReagents.R) ──────────────────────────────

REAGENTS = [
    {'name': 'nahco3',   'cmpd': 'NaHCO\u2083',  'mw': 84.00661,  'meq_mmol': 1, 'm': 1,       'mRad': math.pi / 4},
    {'name': 'na2co3',   'cmpd': 'Na\u2082CO\u2083', 'mw': 105.98844, 'meq_mmol': 2, 'm': 2,       'mRad': math.atan(2)},
    {'name': 'naoh',     'cmpd': 'NaOH',          'mw': 39.99711,  'meq_mmol': 1, 'm': 1e6,     'mRad': math.pi / 2},
    {'name': 'caco3',    'cmpd': 'CaCO\u2083',    'mw': 100.0869,  'meq_mmol': 2, 'm': 2,       'mRad': math.atan(2)},
    {'name': 'caoh2',    'cmpd': 'Ca(OH)\u2082',  'mw': 74.09268,  'meq_mmol': 2, 'm': 1e6,     'mRad': math.pi / 2},
    {'name': 'cao',      'cmpd': 'CaO',           'mw': 56.0774,   'meq_mmol': 2, 'm': 1e6,     'mRad': math.pi / 2},
    {'name': 'plusCo2',  'cmpd': '+CO\u2082',      'mw': 44.0096,   'meq_mmol': 0, 'm': 0,       'mRad': 0.0},
    {'name': 'minusCo2', 'cmpd': '-CO\u2082',      'mw': 44.0096,   'meq_mmol': 0, 'm': 0,       'mRad': math.pi},
    {'name': 'hcl',      'cmpd': 'HCl',           'mw': 36.46094,  'meq_mmol': 1, 'm': 1e6,     'mRad': 3 * math.pi / 2},
]

REAGENT_MAP = {r['name']: r for r in REAGENTS}

# HCl muriatic acid conversion
_MURIATIC_POSTO = 0.3145
_MURIATIC_SPGR = 1.16
_MURIATIC_MASS_PER_L = _MURIATIC_POSTO * _MURIATIC_SPGR


def calc_adjustment(init_dic, init_alk, final_dic, final_alk, vol_l,
                    reagent1_name, reagent2_name):
    """Calculate reagent amounts to move from initial to final waypoint.

    All DIC/Alk in mmol/kg or meq/L (same numeric scale).
    Returns dict with reagent names, compounds, amounts (grams), and
    the intermediate adjustment point (dic_star, alk_star).
    """
    r1 = REAGENT_MAP.get(reagent1_name)
    r2 = REAGENT_MAP.get(reagent2_name)
    if not r1 or not r2:
        return {'error': 'Unknown reagent'}

    delta_dic = final_dic - init_dic
    delta_alk = final_alk - init_alk

    if abs(delta_dic) < 1e-12 and abs(delta_alk) < 1e-12:
        return {
            'reagent1': {'name': r1['name'], 'cmpd': r1['cmpd'], 'amount_g': 0},
            'reagent2': {'name': r2['name'], 'cmpd': r2['cmpd'], 'amount_g': 0},
            'adjustment_point': {'dic': init_dic, 'alk': init_alk},
            'feasible': True,
        }

    # Determine lower / higher reagent by mRad
    if r1['mRad'] < r2['mRad']:
        lower, higher = r1, r2
    else:
        lower, higher = r2, r1

    # Waypoint slope in radians
    wp_slope_rad = math.atan2(delta_alk, delta_dic)
    if wp_slope_rad < 0:
        wp_slope_rad += 2 * math.pi

    # Check feasibility
    feasible = True
    if higher['mRad'] - lower['mRad'] < math.pi:
        if not (lower['mRad'] <= wp_slope_rad <= higher['mRad']):
            feasible = False
    else:
        if not (wp_slope_rad >= higher['mRad'] or wp_slope_rad <= lower['mRad']):
            feasible = False

    if not feasible:
        return {
            'reagent1': {'name': lower['name'], 'cmpd': lower['cmpd'], 'amount_g': 0},
            'reagent2': {'name': higher['name'], 'cmpd': higher['cmpd'], 'amount_g': 0},
            'adjustment_point': None,
            'feasible': False,
        }

    # Re-sort by slope value (m) for intersection calc
    if r1['m'] < r2['m']:
        lower, higher = r1, r2
    else:
        lower, higher = r2, r1

    # Compute intersection point (dic_star, alk_star)
    if higher['m'] > 2:
        # NaOH, Ca(OH)2, CaO, HCl — vertical reagent
        dic_star = final_dic
        alk_star = lower['m'] * (final_dic - init_dic) + init_alk
    else:
        dic_star = (init_alk - lower['m'] * init_dic
                    - final_alk + higher['m'] * final_dic) / (higher['m'] - lower['m'])
        alk_star = lower['m'] * (dic_star - init_dic) + init_alk

    # Amount of reagent 1 (lower slope): grams
    # [mmol/kg] * [g/mol] * [L] / 1000 → but DIC is in mmol/kg, mw in g/mol
    # (dic_star - init_dic) is in mmol/kg, mw in g/mol, vol in L
    # mmol/kg * g/mol * L = mmol * g / (mol * kg) ... need to be careful
    # In the R code: (dicStar - initDic) * mw * vol → units: [mol/kg]*[g/mol]*[L] = g
    # So DIC must be in mol/kg. Our DIC is in mmol/kg, so divide by 1000.
    chem1_g = abs((dic_star - init_dic) / 1000.0 * lower['mw'] * vol_l)

    # Amount of reagent 2 (higher slope): from alkalinity deficit
    alk_deficit = abs(final_alk - alk_star)
    if higher['meq_mmol'] > 0:
        chem2_g = alk_deficit / 1000.0 * (higher['mw'] / higher['meq_mmol']) * vol_l
    else:
        chem2_g = 0

    # HCl conversion: mass → volume (L of muriatic acid)
    chem1_unit = 'g'
    chem2_unit = 'g'
    if lower['name'] == 'hcl':
        chem1_g /= _MURIATIC_MASS_PER_L
        chem1_unit = 'mL'
        chem1_g *= 1000  # kg→L→mL
    if higher['name'] == 'hcl':
        chem2_g /= _MURIATIC_MASS_PER_L
        chem2_unit = 'mL'
        chem2_g *= 1000

    return {
        'reagent1': {
            'name': lower['name'], 'cmpd': lower['cmpd'],
            'amount': round(chem1_g, 4), 'unit': chem1_unit,
        },
        'reagent2': {
            'name': higher['name'], 'cmpd': higher['cmpd'],
            'amount': round(chem2_g, 4), 'unit': chem2_unit,
        },
        'adjustment_point': {
            'dic': round(dic_star, 4),
            'alk': round(alk_star, 4),
        },
        'feasible': True,
    }


def generate_deffeyes_data(temp_c=25.0, salinity=35.0, ca_mg_l=412.0,
                           initial_ph=7.5, initial_alk=2.0,
                           target_ph=8.2, target_alk=3.2,
                           dic_min=0.0, dic_max=6.0,
                           alk_min=0.0, alk_max=6.0,
                           tan_mg_l=0.0, uia_limit=0.02,
                           co2_limit_mg_l=0.0,
                           volume_l=1000.0):
    """Generate all Deffeyes diagram data. pH inputs on NBS scale."""

    tk = temp_c + 273.15
    sal = salinity

    # Ca in mol/kg
    ca_mol = ca_mg_l_to_mol_kg(ca_mg_l, tk, sal)

    # pH isopleths (NBS values)
    ph_major = [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]
    ph_minor = [4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5]

    major_iso = generate_ph_isopleths(tk, sal, dic_min, dic_max, ph_major)
    minor_iso = generate_ph_isopleths(tk, sal, dic_min, dic_max, ph_minor)

    # Omega boundary
    omega_bound = generate_omega_boundary(tk, sal, ca_mol, dic_min, dic_max)

    # UIA boundary
    uia_data = None
    if tan_mg_l > 0 and uia_limit > 0:
        uia_data = generate_uia_boundary(tk, sal, tan_mg_l, uia_limit, dic_min, dic_max)

    # CO2 boundary
    co2_data = None
    if co2_limit_mg_l > 0:
        co2_data = generate_co2_boundary(tk, sal, co2_limit_mg_l, dic_min, dic_max)

    # Waypoints — convert NBS pH to FREE for DIC calc
    init_ph_free = ph_nbs_to_free(initial_ph, sal, tk)
    tgt_ph_free = ph_nbs_to_free(target_ph, sal, tk)
    init_alk_mol = initial_alk / 1000.0
    tgt_alk_mol = target_alk / 1000.0
    init_dic_mol = calc_dic_of_alk(init_alk_mol, init_ph_free, tk, sal)
    tgt_dic_mol = calc_dic_of_alk(tgt_alk_mol, tgt_ph_free, tk, sal)

    return {
        'major_isopleths': major_iso,
        'minor_isopleths': minor_iso,
        'omega_boundary': omega_bound,
        'uia_boundary': uia_data,
        'co2_boundary': co2_data,
        'initial_waypoint': {
            'dic': round(init_dic_mol * 1000.0, 4),
            'alk': round(initial_alk, 4),
            'ph': initial_ph,
        },
        'target_waypoint': {
            'dic': round(tgt_dic_mol * 1000.0, 4),
            'alk': round(target_alk, 4),
            'ph': target_ph,
        },
        'axes': {
            'dic_min': dic_min, 'dic_max': dic_max,
            'alk_min': alk_min, 'alk_max': alk_max,
        },
        'params': {
            'temp_c': temp_c, 'salinity': salinity,
            'ca_mg_l': ca_mg_l, 'volume_l': volume_l,
        },
    }
