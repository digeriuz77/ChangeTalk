import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rouge import Rouge
from bert_score import score
import numpy as np

nltk.download('vader_lexicon', quiet=True)

class OARSAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.tfidf = TfidfVectorizer()
        self.rouge = Rouge()
        self.change_talk_keywords = [
            'change', 'improve', 'better', 'start', 'stop', 'more', 'less', 'different',
            'want', 'need', 'desire', 'plan', 'could', 'should', 'would', 'will'
        ]

    def analyze_sentiment(self, text):
        return self.sia.polarity_scores(text)['compound']

    def identify_change_talk(self, text):
        text_lower = text.lower()
        return sum(1 for keyword in self.change_talk_keywords if keyword in text_lower)

    def evaluate_coherence(self, text1, text2):
        tfidf_matrix = self.tfidf.fit_transform([text1, text2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    def evaluate_summary(self, original, summary):
        rouge_scores = self.rouge.get_scores(summary, original)[0]
        return {
            'rouge-1': rouge_scores['rouge-1']['f'],
            'rouge-2': rouge_scores['rouge-2']['f'],
            'rouge-l': rouge_scores['rouge-l']['f']
        }

    def evaluate_semantic_similarity(self, text1, text2):
        P, R, F1 = score([text1], [text2], lang="en", verbose=False)
        return F1.numpy()[0]

    def generate_reflection(self, text):
        return f"It sounds like you're saying that {text}"

    def generate_affirmation(self, text):
        sentiment = self.analyze_sentiment(text)
        if sentiment > 0:
            return "That's great! You're making positive steps."
        elif sentiment < 0:
            return "I appreciate your honesty in sharing that. It takes courage to confront challenges."
        else:
            return "Thank you for sharing that. Your perspective is valuable."

    def generate_open_question(self, text):
        return f"Can you tell me more about why you feel that way about {text}?"

    def analyze_input(self, user_input, chat_history):
        sentiment = self.analyze_sentiment(user_input)
        change_talk_score = self.identify_change_talk(user_input)
        
        if chat_history:
            last_message = chat_history[-1]['content']
            coherence = self.evaluate_coherence(user_input, last_message)
            semantic_similarity = self.evaluate_semantic_similarity(user_input, last_message)
        else:
            coherence = 0
            semantic_similarity = 0
        
        reflection = self.generate_reflection(user_input)
        affirmation = self.generate_affirmation(user_input)
        open_question = self.generate_open_question(user_input)

        return {
            'sentiment': sentiment,
            'change_talk_score': change_talk_score,
            'coherence': coherence,
            'semantic_similarity': semantic_similarity,
            'reflection': reflection,
            'affirmation': affirmation,
            'open_question': open_question
        }
