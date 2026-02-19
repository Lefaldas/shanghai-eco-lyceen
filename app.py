"""
CALCULATEUR D'EMPREINTE CARBONE - VERSION SIMPLE
Projet NSI : Transition Écologique à Shanghai

Ce script Python utilise Flask pour créer une application web
permettant de calculer l'empreinte carbone basée sur plusieurs catégories.

Auteur: Lycéen NSI
Date: 2026
"""

from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# ============================================================================
# FACTEURS D'ÉMISSION (kg CO2 par unité)
# Source: ADEME et données du mix énergétique chinois
# ============================================================================

EMISSION_FACTORS = {
    # Transport (kg CO2 par km)
    "voiture": 0.21,           # Voiture essence/diesel
    "bus": 0.05,               # Transport en commun
    "velo": 0,                 # Zéro émission
    "marche": 0,               # Zéro émission
    "avion": 0.255,            # Avion (très polluant)
    
    # Énergie (kg CO2 par kWh)
    "electricite": 0.55,       # Mix énergétique chinois
    "chauffage_gaz": 0.23,     # Chauffage au gaz
    "chauffage_fuel": 0.32,    # Chauffage au fioul
    
    # Alimentation (kg CO2 par portion/100g)
    "viande_rouge": 2.5,       # Boeuf, agneau
    "viande_blanche": 1.2,     # Poulet, dinde
    "poisson": 1.5,            # Poisson
    "produits_laitiers": 0.8,  # Lait, fromage, yaourt
    "legumes": 0.2,            # Légumes locaux
    "fruits": 0.3,             # Fruits
    "riz": 0.4,                # Riz
    "pain": 0.5,               # Pain
    
    # Consommation (kg CO2 par article)
    "vetements": 5,            # Un vêtement neuf
    "electronique": 50,        # Un téléphone, ordinateur
    "livres": 1,               # Un livre
    "papier": 0.01,            # Une feuille de papier
    
    # Eau (kg CO2 par m3)
    "eau_chaude": 2.5,         # Eau chaude
    "eau_froide": 0.3,         # Eau froide
    
    # Déchets (kg CO2 par kg)
    "dechets_recycles": 0.1,   # Déchets recyclés
    "dechets_non_recycles": 0.5, # Déchets non recyclés
}

# ============================================================================
# FONCTIONS DE CALCUL
# ============================================================================

def calculate_transport_emissions(data):
    """Calcule les émissions de transport"""
    emissions = 0
    
    # Transport voiture
    if "voiture_km" in data:
        emissions += float(data.get("voiture_km", 0)) * EMISSION_FACTORS["voiture"]
    
    # Transport bus
    if "bus_km" in data:
        emissions += float(data.get("bus_km", 0)) * EMISSION_FACTORS["bus"]
    
    # Transport avion
    if "avion_km" in data:
        emissions += float(data.get("avion_km", 0)) * EMISSION_FACTORS["avion"]
    
    return emissions


def calculate_energy_emissions(data):
    """Calcule les émissions d'énergie"""
    emissions = 0
    
    # Électricité
    if "electricite_kwh" in data:
        emissions += float(data.get("electricite_kwh", 0)) * EMISSION_FACTORS["electricite"]
    
    # Chauffage gaz
    if "chauffage_gaz_kwh" in data:
        emissions += float(data.get("chauffage_gaz_kwh", 0)) * EMISSION_FACTORS["chauffage_gaz"]
    
    # Chauffage fioul
    if "chauffage_fuel_kwh" in data:
        emissions += float(data.get("chauffage_fuel_kwh", 0)) * EMISSION_FACTORS["chauffage_fuel"]
    
    return emissions


def calculate_food_emissions(data):
    """Calcule les émissions d'alimentation"""
    emissions = 0
    
    # Viande rouge (portions par semaine)
    if "viande_rouge_portions" in data:
        emissions += float(data.get("viande_rouge_portions", 0)) * EMISSION_FACTORS["viande_rouge"]
    
    # Viande blanche
    if "viande_blanche_portions" in data:
        emissions += float(data.get("viande_blanche_portions", 0)) * EMISSION_FACTORS["viande_blanche"]
    
    # Poisson
    if "poisson_portions" in data:
        emissions += float(data.get("poisson_portions", 0)) * EMISSION_FACTORS["poisson"]
    
    # Produits laitiers
    if "produits_laitiers_portions" in data:
        emissions += float(data.get("produits_laitiers_portions", 0)) * EMISSION_FACTORS["produits_laitiers"]
    
    # Légumes
    if "legumes_portions" in data:
        emissions += float(data.get("legumes_portions", 0)) * EMISSION_FACTORS["legumes"]
    
    return emissions


def calculate_consumption_emissions(data):
    """Calcule les émissions de consommation"""
    emissions = 0
    
    # Vêtements neufs par an
    if "vetements_par_an" in data:
        emissions += float(data.get("vetements_par_an", 0)) * EMISSION_FACTORS["vetements"] / 12
    
    # Électronique neuve par an
    if "electronique_par_an" in data:
        emissions += float(data.get("electronique_par_an", 0)) * EMISSION_FACTORS["electronique"] / 12
    
    # Livres par an
    if "livres_par_an" in data:
        emissions += float(data.get("livres_par_an", 0)) * EMISSION_FACTORS["livres"] / 12
    
    return emissions


def calculate_water_emissions(data):
    """Calcule les émissions liées à l'eau"""
    emissions = 0
    
    # Eau chaude (litres par jour)
    if "eau_chaude_litres" in data:
        emissions += float(data.get("eau_chaude_litres", 0)) * EMISSION_FACTORS["eau_chaude"] / 1000 * 30
    
    # Eau froide
    if "eau_froide_litres" in data:
        emissions += float(data.get("eau_froide_litres", 0)) * EMISSION_FACTORS["eau_froide"] / 1000 * 30
    
    return emissions


def calculate_waste_emissions(data):
    """Calcule les émissions liées aux déchets"""
    emissions = 0
    
    # Déchets recyclés (kg par mois)
    if "dechets_recycles_kg" in data:
        emissions += float(data.get("dechets_recycles_kg", 0)) * EMISSION_FACTORS["dechets_recycles"]
    
    # Déchets non recyclés
    if "dechets_non_recycles_kg" in data:
        emissions += float(data.get("dechets_non_recycles_kg", 0)) * EMISSION_FACTORS["dechets_non_recycles"]
    
    return emissions


def calculate_total_emissions(data):
    """Calcule l'empreinte carbone totale"""
    transport = calculate_transport_emissions(data)
    energy = calculate_energy_emissions(data)
    food = calculate_food_emissions(data)
    consumption = calculate_consumption_emissions(data)
    water = calculate_water_emissions(data)
    waste = calculate_waste_emissions(data)
    
    total = transport + energy + food + consumption + water + waste
    
    return {
        "total": round(total, 2),
        "transport": round(transport, 2),
        "energy": round(energy, 2),
        "food": round(food, 2),
        "consumption": round(consumption, 2),
        "water": round(water, 2),
        "waste": round(waste, 2),
    }


# ============================================================================
# ROUTES FLASK
# ============================================================================

@app.route("/")
def index():
    """Page d'accueil"""
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    """API pour calculer l'empreinte carbone"""
    try:
        data = request.get_json()
        results = calculate_total_emissions(data)
        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/factors", methods=["GET"])
def get_factors():
    """API pour obtenir les facteurs d'émission"""
    return jsonify(EMISSION_FACTORS)


# ============================================================================
# LANCEMENT DE L'APPLICATION
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CALCULATEUR D'EMPREINTE CARBONE - SHANGHAI ECO-LYCÉEN")
    print("=" * 60)
    print("\nApplication lancée sur http://localhost:5000")
    print("Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    app.run(debug=True, host="0.0.0.0", port=5000)
