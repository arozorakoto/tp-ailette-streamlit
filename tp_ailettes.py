import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="TP Ailette", layout="wide")
st.title("TP Virtuel – Ailette en régime permanent (simulation expérimentale)")

# --- SÉLECTION DE FORMES ET PARAMÈTRES GÉNÉRAUX ---
col1, col2, col3 = st.columns(3)
with col1:
    forme = st.selectbox("Forme", ["Rectangulaire", "Cylindrique", "Conique"])
with col2:
    materiau = st.selectbox("Matériau", ["Aluminium", "Cuivre", "Acier"])
with col3:
    L = st.number_input("Longueur (m)", value=0.1, step=0.01, min_value=0.01)

materiaux = {"Aluminium": 205, "Cuivre": 385, "Acier": 50}
k = materiaux[materiau]

# --- GÉOMÉTRIE SPÉCIFIQUE ---
st.markdown("### Paramètres géométriques")
if forme == "Rectangulaire":
    e = st.columns(1)[0].number_input("Épaisseur e (m)", value=0.005)
elif forme == "Cylindrique":
    r = st.columns(1)[0].number_input("Rayon r (m)", value=0.005)
elif forme == "Conique":
    colg = st.columns(2)
    r_base = colg[0].number_input("Rayon à la base (m)", value=0.005)
    r_tip = colg[1].number_input("Rayon à l’extrémité (m)", value=0.001)

# --- THERMIQUE ---
st.markdown("### Paramètres thermiques")
colt = st.columns(3)
T_base = colt[0].number_input("T_base (°C)", value=100.0)
T_inf = colt[1].number_input("T_ambiante (°C)", value=25.0)
h = colt[2].number_input("h (W/m²·K)", value=50.0)

# --- Curseur interactif ---
x_cible = st.slider("Position sur l’ailette (mm)", 0, int(L * 1000), 40) / 1000

# --- CALCUL THÉORIQUE (exact) ---
x = np.linspace(0, L, 300)

if forme == "Rectangulaire":
    P = 4 * e
    S = e * e
    m = np.sqrt((h * P) / (k * S))
    theta = (T_base - T_inf) * np.cosh(m * (L - x)) / np.cosh(m * L)
    T_theorique = T_inf + theta
    T_cible_exact = np.interp(x_cible, x, T_theorique)

elif forme == "Cylindrique":
    mL = np.sqrt((4 * h) / (k * r))
    m = mL / L
    theta = (T_base - T_inf) * np.sinh(m * (L - x)) / np.sinh(m * L)
    T_theorique = T_inf + theta
    T_cible_exact = np.interp(x_cible, x, T_theorique)

elif forme == "Conique":
    r_moyen = (r_base + r_tip) / 2
    P = 2 * np.pi * r_moyen
    S = np.pi * r_moyen**2
    m = np.sqrt((h * P) / (k * S))
    theta = (T_base - T_inf) * np.cosh(m * (L - x)) / np.cosh(m * L)
    T_theorique = T_inf + theta
    T_cible_exact = np.interp(x_cible, x, T_theorique)
    r_cible = r_base - (r_base - r_tip) * (x_cible / L)

# --- SIMULATION DE MESURE EXPÉRIMENTALE ---
# On simule une erreur expérimentale de ±3 %
np.random.seed(int(x_cible * 10000))  # pour un résultat stable
erreur_relative = np.random.uniform(-0.03, 0.03)  # ±3 %
T_cible_exp = T_cible_exact * (1 + erreur_relative)

# --- AFFICHAGE DU SCHÉMA ---
st.markdown("### Schéma de l’ailette avec température mesurée")

fig, ax = plt.subplots(figsize=(6, 4))

if forme == "Rectangulaire":
    ax.plot([0, e*1000, e*1000, 0, 0], [0, 0, L*1000, L*1000, 0], color="black")
    ax.hlines(x_cible*1000, 0, e*1000, colors='red', linestyle='--', linewidth=2)
    ax.text(e*1000 + 1, x_cible*1000, f"{T_cible_exp:.1f} °C", color='red')

elif forme == "Cylindrique":
    ax.plot([0], [0], 'o', color='black')
    ax.plot([0, 0], [0, L*1000], color="gray", linestyle="--")
    ax.hlines(x_cible*1000, -5, 5, colors='red', linestyle='--', linewidth=2)
    ax.text(6, x_cible*1000, f"{T_cible_exp:.1f} °C", color='red')

elif forme == "Conique":
    r_x = r_base - (r_base - r_tip) * (x / L)
    ax.plot(r_x * 1000, x * 1000, color="black")
    ax.plot(-r_x * 1000, x * 1000, color="black")
    r_cible = r_base - (r_base - r_tip) * (x_cible / L)
    ax.plot([-r_cible*1000, r_cible*1000], [x_cible*1000]*2, 'r--')
    ax.text(r_cible*1000 + 2, x_cible*1000, f"{T_cible_exp:.1f} °C", color='red')
    ax.invert_yaxis()

ax.set_xlabel("Largeur ou rayon (mm)")
ax.set_ylabel("Longueur (mm)")
ax.set_title(f"Ailette {forme.lower()} – x = {x_cible*1000:.0f} mm")
st.pyplot(fig)

# --- AFFICHAGE DES TEMPÉRATURES ---
colt2 = st.columns(2)
colt2[0].success(f"🌡️ **Résultat simulé (mesuré)** : {T_cible_exp:.2f} °C")
colt2[1].info(f"🧠 **Valeur exacte (théorique)** : {T_cible_exact:.2f} °C")
