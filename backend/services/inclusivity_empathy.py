# services/inclusivity_empathy.py
import re
from typing import Dict, List, Tuple

class InclusivityEmpathyService:
    """Service for enhancing Disha's responses with inclusivity and empathy"""
    
    def __init__(self):
        # Patterns that might indicate emotional states
        self.emotion_patterns = {
            'frustration': [r'(frustrated|annoying|not working|tired of|fed up)', 0.8],
            'anxiety': [r'(worried|anxious|nervous|scared|fear|stress)', 0.8],
            'excitement': [r'(excited|thrilled|looking forward|can\'t wait)', 0.7],
            'confusion': [r'(confused|don\'t understand|what does|how does|unclear)', 0.8],
            'disappointment': [r'(disappointed|sad|upset|let down)', 0.8]
        }
        
        # Cultural context detection patterns
        self.cultural_contexts = {
            'india_specific': [
                r'(india|indian|bangalore|delhi|mumbai|hyderabad|pune|chennai)',
                r'(iit|nit|bits|iisc|iim|upsc|gate|cat exam)',
                r'(rupees|inr|lakh|crore)',
                r'(startup india|digital india)'
            ]
        }
        
        # Inclusive language patterns
        self.inclusive_swaps = {
            r'\b(mankind|manpower|manmade)\b': 'humanity|workforce|artificial',
            r'\b(chairman|policeman|fireman)\b': 'chair|police officer|firefighter',
            r'\b(guys)\b': 'everyone|folks|team',
            r'\b(he|his|him)\b when referring to unknown': 'they|their|them',
            r'\bhe or she\b': 'they',
            r'\bhis or her\b': 'their'
        }
        
        # Career milestones for empathetic responses
        self.career_milestones = [
            'first job', 'job search', 'applying', 'interview', 'rejected', 
            'offer', 'negotiation', 'starting new job', 'promotion', 'raise',
            'fired', 'laid off', 'quit', 'resignation', 'career change'
        ]
    
    def detect_emotion(self, text: str) -> Tuple[str, float]:
        """Detect potential emotional state from text"""
        text = text.lower()
        detected = []
        
        for emotion, (pattern, confidence) in self.emotion_patterns.items():
            if re.search(pattern, text):
                detected.append((emotion, confidence))
        
        # Return the emotion with highest confidence or None
        if detected:
            return max(detected, key=lambda x: x[1])
        return (None, 0.0)
    
    def detect_cultural_context(self, text: str) -> List[str]:
        """Detect potential cultural contexts from text"""
        text = text.lower()
        detected = []
        
        for context, patterns in self.cultural_contexts.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected.append(context)
                    break
                    
        return detected
    
    def detect_career_milestone(self, text: str) -> str:
        """Detect if user is discussing a career milestone"""
        text = text.lower()
        
        for milestone in self.career_milestones:
            if milestone in text:
                return milestone
                
        return None
        
    def enhance_empathy(self, response: str, emotion: str = None, 
                         milestone: str = None, cultural_contexts: List[str] = None) -> str:
        """Enhance response with appropriate empathetic elements"""
        
        empathy_phrases = {
            'frustration': [
                "I understand this can be frustrating.",
                "It's completely normal to feel frustrated about this.",
                "Navigating this challenge can be difficult."
            ],
            'anxiety': [
                "It's natural to feel concerned about this.",
                "Many people feel anxious about this part of their career journey.",
                "Taking things one step at a time can help manage these concerns."
            ],
            'confusion': [
                "This can definitely be confusing to navigate.",
                "Let me try to clarify this for you.",
                "Many people find this aspect challenging to understand."
            ],
            'disappointment': [
                "I'm sorry to hear about this setback.",
                "This must be disappointing, but remember that setbacks are temporary.",
                "Many successful professionals have faced similar challenges."
            ],
            'excitement': [
                "It's wonderful to see your enthusiasm!",
                "This is definitely an exciting opportunity.",
                "Your positive energy will serve you well in this new chapter."
            ]
        }
        
        milestone_phrases = {
            'job search': "The job search process requires persistence, but I'm here to help you through it.",
            'interview': "Interviews can be challenging, but with preparation, you can showcase your strengths effectively.",
            'rejected': "Rejection is never easy, but it's often just a step toward finding the right opportunity.",
            'offer': "Receiving an offer is a significant achievement - congratulations!",
            'laid off': "Being laid off can be very difficult. Remember that this reflects market conditions, not your value."
        }
        
        cultural_phrases = {
            'india_specific': [
                "In the Indian job market, networking is particularly valuable.", 
                "Many Indian tech companies value both technical skills and cultural fit."
            ]
        }
        
        enhanced = response
        
        # Add empathy phrase if emotion detected
        if emotion and emotion in empathy_phrases:
            phrases = empathy_phrases[emotion]
            enhanced = f"{phrases[0]} {enhanced}"
        
        # Add milestone-specific guidance
        if milestone and milestone in milestone_phrases:
            enhanced = f"{enhanced}\n\n{milestone_phrases[milestone]}"
            
        # Add culturally relevant information
        if cultural_contexts:
            for context in cultural_contexts:
                if context in cultural_phrases and cultural_phrases[context]:
                    enhanced = f"{enhanced}\n\n{cultural_phrases[context][0]}"
        
        return enhanced
    
    def make_language_inclusive(self, text: str) -> str:
        """Replace non-inclusive language with inclusive alternatives"""
        result = text
        
        for pattern, replacements in self.inclusive_swaps.items():
            replacement_options = replacements.split('|')
            if len(replacement_options) > 0:
                replacement = replacement_options[0]  # Take first option
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                
        return result
    
    def process_response(self, user_prompt: str, response: str) -> str:
        """Process a response to add inclusivity and empathy"""
        emotion, conf = self.detect_emotion(user_prompt)
        milestone = self.detect_career_milestone(user_prompt)
        cultural_contexts = self.detect_cultural_context(user_prompt)
        
        # First make language inclusive
        inclusive_response = self.make_language_inclusive(response)
        
        # Then enhance with empathy
        enhanced_response = self.enhance_empathy(
            inclusive_response, 
            emotion=emotion if conf > 0.7 else None,
            milestone=milestone,
            cultural_contexts=cultural_contexts
        )
        
        return enhanced_response