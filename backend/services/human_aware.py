# services/human_aware.py
import re
import random
from typing import List, Dict, Tuple

class HumanAwareService:
    """Makes AI responses sound more natural and human-aware"""
    
    def __init__(self):
        # Natural speech patterns
        self.speech_patterns = {
            'interjections': [
                "Hey", "Actually", "You know what", "Look", "I think", 
                "Hmm", "Well", "Right", "So", "Oh"
            ],
            'hedges': [
                "kind of", "sort of", "a bit", "pretty much", "basically",
                "more or less", "in a way", "I'd say", "probably", "maybe"
            ],
            'contractions': [
                (r'\b(can not)\b', "can't"),
                (r'\b(will not)\b', "won't"),
                (r'\b(do not)\b', "don't"),
                (r'\b(does not)\b', "doesn't"),
                (r'\b(did not)\b', "didn't"),
                (r'\b(is not)\b', "isn't"),
                (r'\b(are not)\b', "aren't"),
                (r'\b(would not)\b', "wouldn't"),
                (r'\b(could not)\b', "couldn't"),
                (r'\b(should not)\b', "shouldn't"),
                (r'\b(I am)\b', "I'm"),
                (r'\b(You are)\b', "You're"),
                (r'\b(They are)\b', "They're"),
                (r'\b(We are)\b', "We're"),
                (r'\b(He is)\b', "He's"),
                (r'\b(She is)\b', "She's"),
                (r'\b(It is)\b', "It's"),
                (r'\b(That is)\b', "That's"),
                (r'\b(There is)\b', "There's"),
                (r'\b(Here is)\b', "Here's"),
                (r'\b(I will)\b', "I'll"),
                (r'\b(You will)\b', "You'll"),
                (r'\b(They will)\b', "They'll"),
                (r'\b(We will)\b', "We'll"),
                (r'\b(He will)\b', "He'll"),
                (r'\b(She will)\b', "She'll"),
                (r'\b(It will)\b', "It'll"),
                (r'\b(That will)\b', "That'll"),
                (r'\b(There will)\b', "There'll"),
                (r'\b(I have)\b', "I've"),
                (r'\b(You have)\b', "You've"),
                (r'\b(They have)\b', "They've"),
                (r'\b(We have)\b', "We've"),
                (r'\b(He has)\b', "He's"),
                (r'\b(She has)\b', "She's"),
                (r'\b(It has)\b', "It's")
            ],
            'fillers': [
                "um", "uh", "like", "you know", "I mean", "actually", "basically",
                "literally", "honestly"
            ],
            'discourse_markers': [
                "anyway", "so", "now", "then", "you see", "I guess", 
                "as I was saying", "where was I", "as I mentioned"
            ]
        }
        
        # Conversational acknowledgers
        self.acknowledgers = [
            "I get what you're saying about {topic}.",
            "I hear you on the {topic} front.",
            "That's a great point about {topic}.",
            "I understand your concerns about {topic}.",
            "You've got a good perspective on {topic}.",
            "I see where you're coming from with {topic}."
        ]
        
        # Personal anecdote frames
        self.anecdote_frames = [
            "I've worked with someone who {situation}.",
            "One of my contacts in the industry {situation}.",
            "I recently heard about a professional who {situation}.",
            "There was a case where {situation}.",
            "Many people I've spoken with have {situation}."
        ]
        
        # Situation-specific anecdotes (career focused)
        self.anecdotes = {
            "job search": [
                "spent months applying before landing their dream role",
                "completely changed their resume format and saw immediate results",
                "found their best opportunities through networking rather than job boards"
            ],
            "interview": [
                "was asked an unexpected question and turned it into a chance to showcase their skills",
                "prepared specific stories that demonstrated their experience",
                "followed up with a thoughtful thank you note that sealed the deal"
            ],
            "negotiation": [
                "negotiated a 20% higher salary by researching market rates",
                "asked for additional benefits when the salary couldn't be increased",
                "took time to consider the offer instead of accepting immediately"
            ],
            "career change": [
                "transitioned from marketing to UX design through targeted courses",
                "leveraged transferable skills to enter a completely new industry",
                "started with freelance projects to build a portfolio in their new field"
            ]
        }
        
        # Response variants for common questions
        self.response_variants = {
            "greeting": [
                "Hey there! How can I help with your career today?",
                "Hi! What career questions are on your mind?",
                "Hello! Looking for some career guidance?",
                "Hey! What can I help you with in your professional journey?"
            ],
            "not_understood": [
                "Hmm, I'm not quite following. Could you rephrase that?",
                "I'm not sure I caught that. Can you explain differently?",
                "Sorry, I didn't quite get that. Could you say it another way?",
                "I'm not completely understanding your question. Can you try again?"
            ],
            "thanks": [
                "No problem at all!",
                "Happy to help!",
                "Glad I could assist!",
                "Anytime! That's what I'm here for.",
                "You're welcome! Let me know if you need anything else."
            ]
        }
    
    def extract_topics(self, text: str) -> List[str]:
        """Simple topic extraction using common nouns in the text"""
        # In a real implementation, this would use proper NLP
        # This is a simplified version
        words = text.lower().split()
        career_topics = [
            "resume", "interview", "job", "career", "skills", 
            "networking", "salary", "promotion", "application",
            "recruiting", "hiring", "portfolio", "education",
            "experience", "qualification", "leadership"
        ]
        
        found_topics = [word for word in words if word in career_topics]
        if found_topics:
            return found_topics
        return ["your question"]  # Default
        
    def add_contractions(self, text: str) -> str:
        """Convert formal language to contractions"""
        result = text
        
        # Randomly apply contractions (not all at once to maintain variability)
        contractions = random.sample(
            self.speech_patterns['contractions'], 
            k=min(len(self.speech_patterns['contractions']), 
                  random.randint(3, 10))
        )
        
        for pattern, replacement in contractions:
            result = re.sub(pattern, replacement, result)
            
        return result
        
    def add_interjection(self, text: str) -> str:
        """Add conversational interjection to the beginning"""
        # Only add sometimes (70% chance)
        if random.random() > 0.3:
            interjection = random.choice(self.speech_patterns['interjections'])
            # Make sure to add proper punctuation
            return f"{interjection}, {text[0].lower()}{text[1:]}"
        return text
        
    def add_hedge(self, text: str) -> str:
        """Add hedging language to make statement less absolute"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) < 2:
            return text
            
        # Pick a random sentence (not first or last) to add hedge
        if len(sentences) > 2:
            idx = random.randint(1, len(sentences) - 2)
        else:
            idx = 0
            
        # Only add sometimes (50% chance)
        if random.random() > 0.5:
            hedge = random.choice(self.speech_patterns['hedges'])
            sentence = sentences[idx]
            # Insert hedge at beginning of sentence
            modified = f"{sentence.split(' ')[0]} {hedge} {' '.join(sentence.split(' ')[1:])}"
            sentences[idx] = modified
            
        return ' '.join(sentences)
        
    def add_filler(self, text: str) -> str:
        """Add filler words to make text sound more natural"""
        # Only add sometimes (30% chance)
        if random.random() > 0.7:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            if len(sentences) < 2:
                return text
                
            # Pick a random sentence to add filler
            idx = random.randint(0, len(sentences) - 1)
            filler = random.choice(self.speech_patterns['fillers'])
            
            words = sentences[idx].split()
            if len(words) < 4:
                return text
                
            # Insert filler at a natural position (after 2-5 words)
            insert_pos = random.randint(2, min(5, len(words) - 1))
            words.insert(insert_pos, filler)
            sentences[idx] = ' '.join(words)
            
            return ' '.join(sentences)
        return text
        
    def add_discourse_marker(self, text: str) -> str:
        """Add discourse markers between paragraphs"""
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 2:
            return text
            
        # Pick a random paragraph (not first) to add marker at beginning
        idx = random.randint(1, len(paragraphs) - 1)
        marker = random.choice(self.speech_patterns['discourse_markers'])
        
        # Add marker to beginning of paragraph
        paragraphs[idx] = f"{marker.capitalize()}, {paragraphs[idx][0].lower()}{paragraphs[idx][1:]}"
        
        return '\n\n'.join(paragraphs)
        
    def add_acknowledgment(self, text: str, user_prompt: str) -> str:
        """Add an acknowledgment of the user's perspective"""
        # Only add sometimes (60% chance)
        if random.random() > 0.4:
            topics = self.extract_topics(user_prompt)
            if topics:
                topic = random.choice(topics)
                acknowledgment = random.choice(self.acknowledgers).format(topic=topic)
                
                # Add at beginning of response
                return f"{acknowledgment} {text}"
        return text
        
    def add_anecdote(self, text: str, user_prompt: str) -> str:
        """Add a relevant anecdote or example"""
        # Only add sometimes (40% chance)
        if random.random() > 0.6:
            # Identify relevant situation
            situation_keywords = {
                "job search": ["job search", "looking for", "application", "resume", "CV", "apply"],
                "interview": ["interview", "hiring", "meeting", "question"],
                "negotiation": ["offer", "salary", "negotiate", "compensation", "benefits"],
                "career change": ["change career", "transition", "new field", "pivot", "switch jobs"]
            }
            
            detected_situation = None
            for situation, keywords in situation_keywords.items():
                if any(keyword in user_prompt.lower() for keyword in keywords):
                    detected_situation = situation
                    break
                    
            if detected_situation and detected_situation in self.anecdotes:
                anecdote_frame = random.choice(self.anecdote_frames)
                anecdote_content = random.choice(self.anecdotes[detected_situation])
                anecdote = anecdote_frame.format(situation=anecdote_content)
                
                # Add to the appropriate location in text
                paragraphs = text.split('\n\n')
                if len(paragraphs) > 1:
                    # Insert after first paragraph
                    paragraphs.insert(1, anecdote)
                    return '\n\n'.join(paragraphs)
                else:
                    # Add to end if only one paragraph
                    return f"{text}\n\n{anecdote}"
        return text
        
    def get_response_variant(self, variant_type: str) -> str:
        """Get a random variant for common responses"""
        if variant_type in self.response_variants:
            return random.choice(self.response_variants[variant_type])
        return ""
        
    def humanize(self, response: str, user_prompt: str) -> str:
        """Apply a series of transformations to make text more human-like"""
        # Skip transformation for extremely short responses
        if len(response) < 30:
            return response
            
        result = response
        
        # Apply transformations that maintain meaning but sound more natural
        result = self.add_contractions(result)
        result = self.add_interjection(result)
        result = self.add_hedge(result)
        result = self.add_filler(result)  
        result = self.add_discourse_marker(result)
        result = self.add_acknowledgment(result, user_prompt)
        result = self.add_anecdote(result, user_prompt)
        
        return result