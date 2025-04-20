import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

data = {
    "text": [
        "Women are not good at leadership.",
        "Girls can't handle technical work.",
        "Men are better coders.",
        "She is too emotional for management.",
        "He is more logical than her.",
        "Women should focus on soft skills.",
        "Men are naturally better at programming.",
        "She's too aggressive for a woman.",
        "Women aren't suited for tech roles.",
        "Men make better engineers.",
        "Women are less analytical.",
        "Females don't have the right mindset for coding.",
        "Women lack the aptitude for STEM.",
        "Men are more dedicated to their careers.",
        "Women are better at supporting roles than leading.",
        
    
        "Everyone should be treated equally.",
        "Women are excelling in technology.",
        "She is a brilliant engineer.",
        "Gender does not define capability.",
        "We need more women in leadership.",
        "How do I prepare for a behavioral interview?",
        "What are good LinkedIn profile tips?",
        "Are there scholarships for women in coding?",
        "How can women advance in tech careers?",
        "What mentorship opportunities exist?",
        "Tips for resume writing",
        "How to build a strong profile on LinkedIn",
        "Preparing for job interviews",
        "Career advancement strategies",
        "Networking tips for professionals",
        "Working remotely best practices",
        "Skills needed for tech leadership",
        "Negotiating salary advice",
        "Work-life balance strategies",
        "Professional development courses",
        "Mentorship programs for career growth",
        "How to find a tech community",
        "Learning resources for developers",
        "Tips for giving presentations",
        "Public speaking skills development",
        "Women in tech leadership roles",
        "Diversity in tech workforce",
        "Tech conference recommendations",
        "Job search strategies in 2023",
        "Remote work opportunities"
    ],
    "label": [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]
}

df = pd.DataFrame(data)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.2, random_state=42)

# Create and train the model
model = Pipeline(memory=None, steps=[
    ('tfidf', TfidfVectorizer(min_df=2, max_features=5000, ngram_range=(1, 2))),
    ('clf', LogisticRegression(C=5, class_weight='balanced'))
])

model.fit(X_train, y_train)

# Evaluate the model
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Example predictions
test_queries = [
    "How do I build a strong LinkedIn profile?",
    "Are there scholarships for women coders?",
    "Help me prepare for a behavioral interview.",
    "Women can't code as well as men.",
    "Men are naturally better at leadership."
]

for query in test_queries:
    prob = model.predict_proba([query])[0]
    print(f"Query: '{query}'")
    print(f"Prediction: {'Biased' if model.predict([query])[0] == 1 else 'Not biased'}")
    print(f"Probability of bias: {prob[1]:.4f}\n")


joblib.dump(model, "bias_model.pkl")
print("Model saved as 'bias_model.pkl'")