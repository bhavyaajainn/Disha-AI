# services/nlp_engines.py
import spacy
import re
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = spacy.blank("en")
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
        doc = self.nlp(text)
        entities = {entity_type: [] for entity_type in self.career_entities}
        text_lower = text.lower()
        for entity_type, entity_list in self.career_entities.items():
            for entity in entity_list:
                if entity.lower() in text_lower:
                    pattern = r'\b' + re.escape(entity) + r'\b'
                    if re.search(pattern, text, re.IGNORECASE):
                        entities[entity_type].append(entity)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                entities.setdefault("ORGANIZATION", []).append(ent.text)
            elif ent.label_ == "GPE":
                entities.setdefault("LOCATION", []).append(ent.text)
        return {k: list(set(v)) for k, v in entities.items() if v}
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
       
        doc = self.nlp(text)
        
        
        keywords = [token.lemma_.lower() for token in doc 
                   if not token.is_stop and not token.is_punct 
                   and token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"]]
        
       
        keyword_freq = Counter(keywords)
        return [word for word, count in keyword_freq.most_common(top_n)]
    
    def determine_intent(self, text: str) -> Tuple[str, float]:
       
        text_lower = text.lower()
        intent_scores = {intent: self._calculate_intent_score(text_lower, patterns) 
                         for intent, patterns in self.intent_patterns.items()}
        
        if not intent_scores or max(intent_scores.values()) < 0.3:
            return "GENERAL_QUERY", 0.0
            
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent

    def _calculate_intent_score(self, text_lower: str, patterns: List[str]) -> float:
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            score += len(matches) * 0.3
            if matches:
                for starter in ["need", "want", "looking", "help", "advice", "how"]:
                    if text_lower.startswith(starter):
                        score += 0.2
                        break
        return score
    
    def extract_sentiment(self, text: str) -> Tuple[str, float]:
        doc = self.nlp(text)
        
        positive_words = set(["good", "great", "excellent", "impressive", "happy", 
                             "positive", "helpful", "excited", "opportunity", "hope"])
        negative_words = set(["bad", "terrible", "poor", "disappointed", "unhappy",
                             "negative", "frustrated", "concerned", "worried", "problem"])
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
        doc = self.nlp(text)
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
        analysis = self.analyze_text(text)
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
        context = self.get_query_context(original_query)
        intent = context["intent"]
        if context["intent_confidence"] < 0.5:
            return original_query
        if intent == "FIND_JOB":
            return self._optimize_find_job_prompt(context)
        elif intent == "INTERVIEW_PREP":
            return self._optimize_interview_prep_prompt(context)
        elif intent == "RESUME_HELP":
            return self._optimize_resume_help_prompt(context)
        return original_query

    def _optimize_find_job_prompt(self, context: Dict) -> str:
        job_titles = context["primary_entities"].get("JOB_TITLE", [])
        skills = context["primary_entities"].get("SKILL", [])
        industry = context["primary_entities"].get("INDUSTRY", [])
        
        if job_titles and (skills or industry):
            return f"Find {' or '.join(job_titles)} jobs " + \
                   (f"requiring {', '.join(skills)} skills " if skills else "") + \
                   (f"in the {', '.join(industry)} industry" if industry else "")
        return ""

    def _optimize_interview_prep_prompt(self, context: Dict) -> str:
        job_titles = context["primary_entities"].get("JOB_TITLE", [])
        if job_titles:
            return f"What are common interview questions for {job_titles[0]} positions and how should I prepare for them?"
        return ""

    def _optimize_resume_help_prompt(self, context: Dict) -> str:
        job_titles = context["primary_entities"].get("JOB_TITLE", [])
        if job_titles:
            return f"How can I improve my resume for {job_titles[0]} positions? What should I highlight?"
        return ""