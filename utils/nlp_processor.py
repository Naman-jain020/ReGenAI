import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Dict
import re

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self._initialize_matchers()
    
    def _initialize_matchers(self):
        # Initialize matchers for different types of medical information
        self.deficiency_matcher = PhraseMatcher(self.nlp.vocab)
        deficiency_terms = [
            "deficiency", "low", "below normal", "insufficient", 
            "borderline", "deficient", "inadequate"
        ]
        patterns = [self.nlp(text) for text in deficiency_terms]
        self.deficiency_matcher.add("DEFICIENCY", patterns)
        
        self.test_matcher = PhraseMatcher(self.nlp.vocab)
        test_terms = [
            "vitamin d", "vitamin b12", "iron", "hemoglobin", 
            "calcium", "magnesium", "potassium", "sodium"
        ]
        patterns = [self.nlp(text) for text in test_terms]
        self.test_matcher.add("TEST", patterns)
    
    def extract_medical_info(self, text: str) -> Dict[str, List[str]]:
        doc = self.nlp(text)
        
        # Find deficiency mentions
        deficiencies = []
        matches = self.deficiency_matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            deficiencies.append(span.text)
        
        # Find test names and values
        tests = {}
        matches = self.test_matcher(doc)
        for match_id, start, end in matches:
            test_name = doc[start:end].text
            # Look for values near the test name
            for token in doc[end:end+10]:  # Look ahead 10 tokens
                if re.match(r'\d+\.?\d*', token.text):
                    tests[test_name] = token.text
                    break
        
        return {
            'deficiency_mentions': deficiencies,
            'test_results': tests
        }