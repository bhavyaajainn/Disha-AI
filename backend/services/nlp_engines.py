# services/nlp_engines.py
import spacy
import re
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter

class NLPProcessor:
    """NLP processing capabilities for Disha AI"""
    
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback to small model
            self.nlp = spacy.blank("en")
            print("Warning: Using blank English model. For full NLP capabilities, install en_core_web_sm")
        
        # Career domain entities
        self.career_entities = {
            "JOB_TITLE": [
                "software engineer", "product manager", "data scientist", 
                "UX designer", "project manager", "frontend developer",
                "backend developer", "full stack developer", "tech lead",
                "CTO", "CEO", "director", "VP of", "head of", "manager"
            ],
            "SKILL": [
                "Python", "JavaScript", "React", "Node.js", "SQL", "Java",
                "leadership", "communication", "project management", "design",
                "research", "marketing", "sales", "writing", "analytics"
            ],
            "INDUSTRY": [
                "tech", "finance", "healthcare", "education", "retail",
                "e-commerce", "consulting", "manufacturing", "media"
            ],
            "DOCUMENT": [
                "resume", "CV", "cover letter", "portfolio", "LinkedIn profile",
                "GitHub profile", "recommendation", "reference letter"
            ],
            "PROCESS": [
                "interview", "application", "assessment", "onboarding",
                "job search", "networking", "promotion", "performance review"
            ]
        }
        
        # Intent classification patterns
        self.intent_patterns = {
            "FIND_JOB": [
                r"(looking|search|find).*job",
                r"(job|career).*opportunities",
                r"(apply|application).*position"
            ],
            "INTERVIEW_PREP": [
                r"(prepare|preparing|prep).*interview",
                r"interview.*(question|prep|advice)",
                r"(what|how).*interview"
            ],
            "SKILL_DEVELOPMENT": [
                r"(learn|improve|develop).*skill",
                r"(how|best way).*learn",
                r"(course|training|certificate|certification)"
            ],
            "CAREER_CHANGE": [
                r"(change|switch|transition|pivot).*(career|job|field)",
                r"(move|moving) into",
                r"(career|professional).*(transition|change)"
            ],
            "SALARY_NEGOTIATION": [
                r"(negotiate|negotiation|ask).*salary",
                r"(compensation|pay|offer|raise).*negotiation",
                r"(what|how much).*(ask|worth|expect).*salary"
            ],
            "MENTORSHIP": [
                r"(find|get|seek).*mentor",
                r"(mentorship|coaching|guidance)",
                r"(career|professional).*(advice|guidance)"
            ],
            "RESUME_HELP": [
                r"(improve|enhance|update|write).*resume",
                r"(resume|CV).*(review|feedback|advice)",
                r"(help|advice).*resume"
            ]
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract domain-specific career entities from text"""
        doc = self.nlp(text)
        entities = {entity_type: [] for entity_type in self.career_entities}
        
        # Extract custom entity types
        text_lower = text.lower()
        for entity_type, entity_list in self.career_entities.items():
            for entity in entity_list:
                if entity.lower() in text_lower:
                    # Check for word boundaries to avoid partial matches
                    pattern = r'\b' + re.escape(entity) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        entities[entity_type].append(entity)
        
        # Extract standard NER entities from spaCy
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities.setdefault("ORGANIZATION", []).append(ent.text)
            elif ent.label_ == "GPE":
                entities.setdefault("LOCATION", []).append(ent.text)
                
        # Remove empty categories and deduplicate
        return {k: list(set(v)) for k, v in entities.items() if v}
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract important keywords from text"""
        doc = self.nlp(text)
        
        # Filter for meaningful parts of speech
        keywords = [token.lemma_.lower() for token in doc 
                   if not token.is_stop and not token.is_punct 
                   and token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]]
        
        # Count frequencies and return top N
        keyword_freq = Counter(keywords)
        return [word for word, count in keyword_freq.most_common(top_n)]
    
    def determine_intent(self, text: str) -> Tuple[str, float]:
        """Classify user intent using pattern matching"""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                score += len(matches) * 0.3
                if matches:
                    # Boost score for initial intention words
                    for starter in ["need", "want", "looking", "help", "advice", "how"]:
                        if text_lower.startswith(starter):
                            score += 0.2
                            break
            intent_scores[intent] = score
        
        # Find highest scoring intent
        if not intent_scores or max(intent_scores.values()) < 0.3:
            return "GENERAL_QUERY", 0.0
            
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent
    
    def extract_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of text - simple version without ML model"""
        doc = self.nlp(text)
        
        # Simple word-based sentiment analysis
        positive_words = set(["good", "great", "excellent", "impressive", "happy", 
                             "positive", "helpful", "excited", "opportunity", "hope"])
        negative_words = set(["bad", "terrible", "poor", "disappointed", "unhappy",
                             "negative", "frustrated", "concerned", "worried", "problem"])
        
        # Count sentiment words
        pos_count = sum(1 for token in doc if token.lemma_.lower() in positive_words)
        neg_count = sum(1 for token in doc if token.lemma_.lower() in negative_words)
        
        total = pos_count + neg_count
        if total == 0:
            return "NEUTRAL", 0.5
            
        pos_score = pos_count / total
        if pos_score > 0.6:
            return "POSITIVE", pos_score
        elif pos_score < 0.4:
            return "NEGATIVE", 1 - pos_score
        else:
            return "NEUTRAL", 0.5
    
    def analyze_text(self, text: str) -> Dict:
        """Comprehensive NLP analysis of text"""
        doc = self.nlp(text)
        
        # Base analysis output
        analysis = {
            "entities": self.extract_entities(text),
            "keywords": self.extract_keywords(text),
            "intent": self.determine_intent(text),
            "sentiment": self.extract_sentiment(text),
            "complexity": {
                "avg_word_length": sum(len(token.text) for token in doc if not token.is_punct) / max(1, sum(1 for token in doc if not token.is_punct)),
                "sentence_count": len(list(doc.sents)),
                "word_count": len([token for token in doc if not token.is_punct and not token.is_space])
            }
        }
        
        return analysis
    
    def get_query_context(self, text: str) -> Dict:
        """Extract context from query to improve response relevance"""
        analysis = self.analyze_text(text)
        
        # Extract career stage if possible
        career_stage = "unknown"
        starter_indicators = ["new grad", "recent graduate", "entry level", "junior", "starting"]
        mid_indicators = ["3 years", "4 years", "5 years", "experienced", "mid level", "senior"]
        leader_indicators = ["manager", "director", "lead", "head of", "leadership"]
        
        for indicator in starter_indicators:
            if indicator in text.lower():
                career_stage = "entry_level"
                break
                
        for indicator in mid_indicators:
            if indicator in text.lower():
                career_stage = "mid_career"
                break
                
        for indicator in leader_indicators:
            if indicator in text.lower():
                career_stage = "leadership"
                break
        
        return {
            "intent": analysis["intent"][0],
            "intent_confidence": analysis["intent"][1],
            "primary_entities": {k: v for k, v in analysis["entities"].items() if k in ["JOB_TITLE", "INDUSTRY", "SKILL"]},
            "keywords": analysis["keywords"][:3],
            "sentiment": analysis["sentiment"][0],
            "career_stage": career_stage
        }
    
    def optimize_prompt(self, original_query: str) -> str:
        """
        Optimize user query into a more effective prompt by:
        - Clarifying ambiguous terms
        - Adding context based on detected entities
        - Structuring the query for better responses
        """
        context = self.get_query_context(original_query)
        intent = context["intent"]
        
        # Keep original query if we don't have high confidence
        if context["intent_confidence"] < 0.5:
            return original_query
            
        # Build optimized prompt based on intent
        if intent == "FIND_JOB":
            job_titles = context["primary_entities"].get("JOB_TITLE", [])
            skills = context["primary_entities"].get("SKILL", [])
            industry = context["primary_entities"].get("INDUSTRY", [])
            
            if job_titles and (skills or industry):
                return f"Find {' or '.join(job_titles)} jobs " + \
                       (f"requiring {', '.join(skills)} skills " if skills else "") + \
                       (f"in the {', '.join(industry)} industry" if industry else "")
        
        elif intent == "INTERVIEW_PREP":
            job_titles = context["primary_entities"].get("JOB_TITLE", [])
            if job_titles:
                return f"What are common interview questions for {job_titles[0]} positions and how should I prepare for them?"
                
        elif intent == "RESUME_HELP":
            job_titles = context["primary_entities"].get("JOB_TITLE", [])
            if job_titles:
                return f"How can I improve my resume for {job_titles[0]} positions? What should I highlight?"
        
        # Default to original query if no optimization applied
        return original_query