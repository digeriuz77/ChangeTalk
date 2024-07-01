import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

nltk.download('vader_lexicon', quiet=True)
nlp = spacy.load('en_core_web_sm')

class OARSAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.tfidf = TfidfVectorizer()
        self.change_talk_keywords = [
            'change', 'improve', 'better', 'start', 'stop', 'more', 'less', 'different',
            'want', 'need', 'desire', 'plan', 'could', 'should', 'would', 'will'
        ]

    def analyze_sentiment(self, text):
        return self.sia.polarity_scores(text)['compound']

    def identify_change_talk(self, text):
        doc = nlp(text.lower())
        return sum(1 for token in doc if token.lemma_ in self.change_talk_keywords)

    def analyze_input(self, user_input, chat_history):
        sentiment = self.analyze_sentiment(user_input)
        change_talk_score = self.identify_change_talk(user_input)
        
        if chat_history:
            last_message = chat_history[-1]['content']
            coherence = self.calculate_coherence(user_input, last_message)
        else:
            coherence = 0
        
        entities = self.extract_entities(user_input)
        
        return {
            'sentiment': sentiment,
            'change_talk_score': change_talk_score,
            'coherence': coherence,
            'entities': entities
        }

    def calculate_coherence(self, text1, text2):
        tfidf_matrix = self.tfidf.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    def extract_entities(self, text):
        doc = nlp(text)
        return [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
