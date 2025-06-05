"""
Script python pour générer un graphique de comparaison des prédictions
avec les données réelles observées.
"""

def match_val_predict(forcast, val, model_name):
    import matplotlib.pyplot as plt

    # Génération des prédictions
    predicted_mean = forcast.predicted_mean
    confidence_interval = forcast.conf_int()

    # Création du graphique
    plt.figure(figsize=(12, 6))
    plt.plot(val.index, val['y'], 'b-', label='Valeurs réelles (val)')
    plt.plot(val.index, predicted_mean, 'r--', label='Prédictions '+ model_name)
    # plt.fill_between(val.index,
    #                  confidence_interval.iloc[:, 0],
    #                  confidence_interval.iloc[:, 1],
    #                  color='gray', alpha=0.3, label='Intervalle de confiance 95%')

    plt.title('Comparaison des prédictions '+model_name+' avec le jeu de validation')
    plt.xlabel('Date')
    plt.ylabel('Valeur')
    plt.legend()
    plt.grid(True)
    plt.show()