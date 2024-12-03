from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def preprocess_data(df):
    """
    Preprocesses a DataFrame containing task descriptions for NLP tasks.

    Args:
        df (pandas.DataFrame): A DataFrame containing task data.

    Returns:
        pandas.DataFrame: The DataFrame with preprocessed descriptions and TF-IDF vectors.
    """

    # Import stopwords and stemmer
    stop_words = stopwords.words('english')
    stemmer = PorterStemmer()

    # Preprocess 'description' column
    df['preprocessed_description'] = df['description'].apply(lambda text: _preprocess_text(text, stop_words, stemmer))

    # Create TF-IDF vectors for preprocessed descriptions
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['preprocessed_description'])

    # Add TF-IDF matrix as a new column
    df['tfidf_vector'] = tfidf_matrix

    return df


def _preprocess_text(text, stop_words, stemmer):
    """
    Preprocesses a text string for NLP tasks.

    Args:
        text (str): The text to preprocess.
        stop_words (list): List of stop words to remove.
        stemmer (nltk.stem.PorterStemmer): Stemmer object for stemming.

    Returns:
        str: The preprocessed text.
    """

    # Lowercase the text
    text = text.lower()

    # Tokenize the text (split into words)
    tokens = text.split()

    # Remove stop words and perform stemming
    filtered_words = [stemmer.stem(word) for word in tokens if word not in stop_words]

    # Join the preprocessed words back into a string
    preprocessed_text = " ".join(filtered_words)

    return preprocessed_text


# Example usage (assuming your DataFrame is named 'df')
df = preprocess_data(df.copy())  # Operate on a copy to avoid modifying the original DataFrame

print(df[['description', 'preprocessed_description', 'tfidf_vector']])

"""
# For testing DataFrame
    print("Before:\n")
    print(df)

    # Fill missing values 
    df['description'] = df['description'].fillna("No description provided")
    #df['priority'] = df['priority'].fillna(df['priority'].mode()[0])  # Fill with most frequent value
    df['priority'] = df['priority'].fillna('1')
    
    # Ensure 'due_date' is in datetime format and fill missing dates 
    df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce') 
    df['due_date'].fillna(pd.to_datetime('2099-12-31'), inplace=True)

    df['due_time'] = df['due_time'].fillna(pd.to_datetime('00:00:00').time())  # Placeholder for missing times

    
    # Display the DataFrame after filling missing values 
    print("After:\n")
    print(df)

    # Label Encoding for priority 
    label_encoder = LabelEncoder() 
    df['priority'] = label_encoder.fit_transform(df['priority']) 
    
    # Extract year, month, day from 'due_date' 
    df['due_year'] = df['due_date'].dt.year 
    df['due_month'] = df['due_date'].dt.month 
    df['due_day'] = df['due_date'].dt.day 
     
    # Combine 'due_date' and 'due_time' to extract hour and minute 
    df['due_time'] = df.apply(lambda x: pd.to_datetime(f"{x['due_date'].date()} {x['due_time']}"), axis=1) 
    df['due_hour'] = df['due_time'].dt.hour 
    df['due_minute'] = df['due_time'].dt.minute 
    
    # Calculate the number of days until the due date 
    current_date = datetime.now() 
    df['days_until_due'] = (df['due_date'] - current_date).dt.days 
    
    # Add a column for the day of the week 
    df['due_weekday'] = df['due_date'].dt.dayofweek # Monday=0, Sunday=6 
    
    # Display the DataFrame after feature engineering 
    print("\n")
    print(df[['id', 'title', 'description', 'priority', 'due_date', 'due_time', 'due_year', 'due_month', 'due_day', 'due_hour', 'due_minute', 'days_until_due', 'due_weekday', 'is_completed']])
    
    # Vectorize task descriptions using TF-IDF
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['description'])
    print(tfidf_matrix)
"""