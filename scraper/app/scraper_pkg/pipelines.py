from bs4 import BeautifulSoup
import pandas as pd




def clean_and_normalize(title: str, text: str) -> dict:
    """Very small example of normalization using pandas to collect some metrics.
    Returns a dictionary with simple analytics and normalized fields.
    """
    # simple text cleanup
    soup = BeautifulSoup(text, 'html.parser')
    raw_text = soup.get_text(separator=' ', strip=True)


    # token counts / basic stats
    words = raw_text.split()
    df = pd.DataFrame({'word': words})
    word_counts = df['word'].value_counts().head(20).to_dict()


    return {
        'title': title.strip(),
        'word_count': len(words),
        'top_words': word_counts,
    }