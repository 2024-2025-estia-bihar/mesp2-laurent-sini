"""
Script python pour générer un graphique de comparaison des prédictions
avec les données réelles observées.
"""

def match_val_predict(predicted_mean, val, model_name):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(val.index, val, 'b-', label='Valeurs réelles (val)')
    plt.plot(val.index, predicted_mean, 'r--', label='Prédictions '+ model_name)

    plt.title('Comparaison des prédictions '+model_name+' avec le jeu de validation')
    plt.xlabel('Date')
    plt.ylabel('Valeur')
    plt.legend()
    plt.grid(True)
    plt.show()