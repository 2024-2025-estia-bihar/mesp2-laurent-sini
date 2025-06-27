import re

from bs4 import BeautifulSoup
from bs4 import MarkupResemblesLocatorWarning
import warnings

from cleantext import clean
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def check_html_code(df):
    pattern = r'<\s*(p|div|span|br)\s*[^>]*?>'
    for review in df['review']:
        if re.search(pattern, review, re.IGNORECASE):
            print("Balise HTML détectée:", review)
            break
    else:
        print("Aucune balise HTML détectée dans les critiques.")


def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def clean_review(text):
    if not isinstance(text, str):
        return ""
    return clean(
        text,
        lower=True,            # tout en minuscules
        no_urls=True,          # supprime les URLs
        no_emails=True,        # supprime les emails
        no_phone_numbers=True, # supprime les numéros de téléphone
        no_numbers=True,       # supprime les nombres
        no_punct=True,         # supprime la ponctuation
        replace_with_url="",
        replace_with_email="",
        replace_with_phone_number="",
        replace_with_number="",
        lang="fr"              # français
    )

def metric_result(y_val, y_pred):
    print("Accuracy:", accuracy_score(y_val, y_pred))
    print("Precision:", precision_score(y_val, y_pred))
    print("Recall:", recall_score(y_val, y_pred))
    print("F1-score:", f1_score(y_val, y_pred))