from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss


def check_stationarity(series, alpha=0.05):
    result = adfuller(series)
    is_stationary = result[1] < alpha

    print("\n" + "═" * 40)
    print("📊 TEST ADF - AUGMENTED DICKEY-FULLER")
    print("═" * 40)
    print(f"Hypothèse nulle (H0) : La série a une racine unitaire (non stationnaire)\n")
    print(f"Statistique ADF : {result[0]:.4f}")
    print(f"p-value : {result[1]:.4f}")
    print("Valeurs critiques :")

    for key, value in result[4].items():
        print(f"  {key}% : {value:.4f}")

    print(f"\nConclusion ADF : {'Stationnaire' if is_stationary else 'Non stationnaire'} (α={alpha})")

    return is_stationary

def check_stationarity_kpss(series, alpha=0.05):
    import warnings
    from statsmodels.tools.sm_exceptions import InterpolationWarning
    warnings.filterwarnings("ignore", category=InterpolationWarning)

    """Test KPSS avec interprétation détaillée."""
    import warnings
    from statsmodels.tools.sm_exceptions import InterpolationWarning
    warnings.filterwarnings("ignore", category=InterpolationWarning)

    kpss_stat, p_value, _, critical_values = kpss(series, regression='c')
    is_stationary = p_value > alpha

    print("\n" + "═" * 40)
    print("📈 TEST KPSS - KWiatkowski-Phillips-Schmidt-Shin")
    print("═" * 40)
    print(f"Hypothèse nulle (H0) : La série est stationnaire autour d'une constante\n")
    print(f"Statistique KPSS : {kpss_stat:.4f}")
    print(f"p-value : {p_value:.4f}")
    print("Valeurs critiques :")

    for key, value in critical_values.items():
        print(f"  {key}% : {value:.4f}")

    print(f"\nConclusion KPSS : {'Stationnaire' if is_stationary else 'Non stationnaire'} (α={alpha})")

    return is_stationary
