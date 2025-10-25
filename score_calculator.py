from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(resume_text, jd_text):
    texts = [resume_text, jd_text]
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(texts)
    score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
    return round(score * 100, 2)
