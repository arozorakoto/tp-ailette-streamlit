#import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="TP Ailette", layout="wide")

# --- Arrière-plan filigrane ---
st.markdown("""
<div style='
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: #f0f0f0;
    z-index: 0;
    opacity: 0.05;
    pointer-events: none;
    user-select: none;
    font-size: 0.8rem;
    font-family: Arial, sans-serif;
    display: flex;
    flex-direction: column;
    flex-wrap: nowrap;
'>
""" + "".join([
    "<div style='display: flex; flex-wrap: nowrap;'>"
    + " Aro-Zo software 2025 " * 60 +
    "</div>" for _ in range(120)
]) + "</div>", unsafe_allow_html=True)

# --- CSS global ---
st.markdown("""
<style>
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    padding-left: 10rem !important;
    padding-right: 10rem !important;
}
html, body, [class*="css"] {
    font-size: 12px !important;
}
div[data-baseweb="select"] > div {
    max-width: 140px !important;
    min-width: 100px !important;
}
input[type="number"] {
    max-width: 130px !important;
}
</style>
""", unsafe_allow_html=True)

# --- Titre ---
st.markdown("<h1 style='text-align: center;'>TP Virtuel – Ailette en régime permanent</h1>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- Colonnes principales ---
col_left, spacer, col_right = st.columns([1, 0.1, 1])

# ================================
#           COLONNE GAUCHE
# ================================
with col_left:
    st.markdown("### Paramètres géométriques")

    # Sélecteurs
    sel1, sel2, sel3 = st.columns(3)
    with sel1:
        forme = st.selectbox("Forme", ["Rectangulaire", "Cylindrique", "Conique"])
    with sel2:
        materiau = st.selectbox("Matériau", ["Aluminium", "Cuivre", "Acier"])
    with sel3:
        L = st.number_input("Longueur (m)", value=0.1, step=0.01, min_value=0.01, format="%.3f")

    # Propriétés thermiques
    materiaux = {"Aluminium": 205, "Cuivre": 385, "Acier": 50}
    k = materiaux[materiau]

    # Initialisation des variables géométriques
    e, r, r_base, r_tip = None, None, None, None

    # Paramètres selon la forme
    if forme == "Rectangulaire":
        e = st.number_input("Épaisseur e (m)", value=0.005, format="%.4f")
    elif forme == "Cylindrique":
        r = st.number_input("Rayon r (m)", value=0.005, format="%.4f")
    elif forme == "Conique":
        col1, col2 = st.columns(2)
        r_base = col1.number_input("Rayon à la base (m)", value=0.005, format="%.4f")
        r_tip = col2.number_input("Rayon à l’extrémité (m)", value=0.001, format="%.4f")

    st.markdown("### Paramètres thermiques")
    T_base, T_inf, h = st.columns(3)
    T_base = T_base.number_input("T_base (°C)", value=100.0, format="%.1f")
    T_inf = T_inf.number_input("T_ambiante (°C)", value=25.0, format="%.1f")
    h = h.number_input("h (W/m²·K)", value=50.0, format="%.1f")

    # Position cible
    x_cible = st.slider("Position x sur l’ailette (mm)", 0, int(L * 1000), 40) / 1000

# ================================
#           COLONNE DROITE
# ================================
with col_right:
    # Calculs
    x = np.linspace(0, L, 300)

    if forme == "Rectangulaire":
        P = 4 * e
        S = e * e
        m = np.sqrt((h * P) / (k * S))
        theta = (T_base - T_inf) * np.cosh(m * (L - x)) / np.cosh(m * L)

    elif forme == "Cylindrique":
        m = np.sqrt((4 * h) / (k * r))
        theta = (T_base - T_inf) * np.sinh(m * (L - x)) / np.sinh(m * L)

    elif forme == "Conique":
        r_moyen = (r_base + r_tip) / 2
        P = 2 * np.pi * r_moyen
        S = np.pi * r_moyen**2
        m = np.sqrt((h * P) / (k * S))
        theta = (T_base - T_inf) * np.cosh(m * (L - x)) / np.cosh(m * L)

    T_theorique = T_inf + theta
    T_cible_exact = np.interp(x_cible, x, T_theorique)

    # Simulation expérimentale
    np.random.seed(int(x_cible * 10000))
    erreur_relative = np.random.uniform(-0.03, 0.03)
    T_cible_exp = T_cible_exact * (1 + erreur_relative)

    # --- Schéma ---
    st.markdown("<h4 style='text-align: center;'>Schéma de l’ailette avec température expérimentale mesurée</h4>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(5, 3.5))

    if forme == "Rectangulaire":
        ax.plot([0, 0, L*1000, L*1000, 0], [0, e*1000, e*1000, 0, 0], color="black")
        ax.vlines(x_cible*1000, 0, e*1000, colors='red', linestyle='--', linewidth=2)
        ax.text(x_cible*1000, e*1000 + 1, f"{T_cible_exp:.1f} °C", color='red', fontsize=9, ha='center')

    elif forme == "Cylindrique":
        ax.plot([0, L*1000], [0, 0], color="gray", linestyle="--")
        ax.vlines(x_cible*1000, -5, 5, colors='red', linestyle='--', linewidth=2)
        ax.text(x_cible*1000, 6, f"{T_cible_exp:.1f} °C", color='red', fontsize=9, ha='center')

    elif forme == "Conique":
        r_x = r_base - (r_base - r_tip) * (x / L)
        ax.plot(x * 1000, r_x * 1000, color="black")
        ax.plot(x * 1000, -r_x * 1000, color="black")
        r_cible = r_base - (r_base - r_tip) * (x_cible / L)
        ax.plot([x_cible*1000]*2, [-r_cible*1000, r_cible*1000], 'r--')
        ax.text(x_cible*1000, r_cible*1000 + 2, f"{T_cible_exp:.1f} °C", color='red', fontsize=9, ha='center')
        ax.invert_yaxis()

    ax.set_xlabel("Position x sur l'ailette (mm)", fontsize=9)
    ax.set_ylabel("Largeur ou rayon (mm)", fontsize=9)
    ax.tick_params(axis='both', labelsize=8)
    fig.subplots_adjust(left=0.12, right=0.96, top=0.85, bottom=0.15)
    st.pyplot(fig)

    # --- Résultats ---
    col_res1, col_res2 = st.columns(2)
 #   col_res1.success(f"🌡️ **Résultat simulé (mesuré)** : {T_cible_exp:.2f} °C")
 #   col_res2.info(f"🧠 **Valeur exacte (théorique)** : {T_cible_exact:.2f} °C")
