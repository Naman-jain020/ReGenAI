from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import GooglePalm
from models.deficiency import Deficiency
from utils.gemini_client import GeminiClient
import re
from typing import List, Tuple
import os
from config import Config
from utils.nlp_processor import NLPProcessor
from dotenv import load_dotenv
import logging

load_dotenv()

class ReportAnalyzer:
    def __init__(self):
        self.gemini_client = GeminiClient()
        self.nlp_processor = NLPProcessor()
        self.logger = logging.getLogger(__name__)
        
    def analyze_report(self, file_path: str) -> List[Deficiency]:
        """
        Analyze a medical report file and identify deficiencies.
        Supports PDF, DOCX, and text files with multiple encodings.
        """
        try:
            self.logger.info(f"Starting analysis of file: {file_path}")
            
            # Get file content based on type
            report_content = self._extract_file_content(file_path)
            
            # Use NLP to extract key information
            extracted_data = self.nlp_processor.extract_medical_info(report_content)
            
            # Use Gemini to analyze deficiencies
            deficiencies = self._analyze_with_gemini(report_content)
            
            self.logger.info(f"Found {len(deficiencies)} deficiencies")
            return deficiencies
            
        except Exception as e:
            self.logger.error(f"Error analyzing report: {str(e)}")
            raise ValueError(f"Failed to analyze report: {str(e)}")

    def _extract_file_content(self, file_path: str) -> str:
        """Extract text content from different file types"""
        _, ext = os.path.splitext(file_path.lower())
        
        if ext == '.pdf':
            return self._extract_pdf_text(file_path)
        elif ext == '.docx':
            return self._extract_docx_text(file_path)
        else:  # Assume text file
            return self._extract_text_file(file_path)

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files using PyPDF2"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""  # Handle None returns
                return text
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {str(e)}")
            raise ValueError("Failed to extract text from PDF file")

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files using python-docx"""
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs if para.text])
        except Exception as e:
            self.logger.error(f"DOCX extraction failed: {str(e)}")
            raise ValueError("Failed to extract text from DOCX file")

    def _extract_text_file(self, file_path: str) -> str:
        """Handle various text file encodings"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError("Could not decode the text file with any supported encoding")

    def _analyze_with_gemini(self, report_content: str) -> List[Deficiency]:
        """Analyze report content using Gemini API"""
        prompt = f"""
        Analyze this medical report and identify all deficiencies and border values:
        {report_content}
        
        For each deficiency found, provide:
        - Name of the deficiency
        - Current value
        - Normal range
        - Severity (low, medium, high)
        - Whether it's a border value (true/false)
        
        Format as JSON:
        {{
            "deficiencies": [
                {{
                    "name": "Vitamin D",
                    "current_value": "15 ng/mL",
                    "normal_range": "30-100 ng/mL",
                    "severity": "medium",
                    "is_border_value": false
                }},
                ...
            ]
        }}
        """
        
        response = self.gemini_client.generate_text(prompt)
        return self._parse_deficiency_response(response)
    
    def calculate_recovery_time(self, deficiencies: List[Deficiency]) -> Tuple[int, int]:
        """Calculate estimated recovery time range based on deficiencies"""
        min_days = 0
        max_days = 0
        
        for deficiency in deficiencies:
            if deficiency.severity == "low":
                min_days += 7
                max_days += 14
            elif deficiency.severity == "medium":
                min_days += 14
                max_days += 30
            else:  # high severity
                min_days += 30
                max_days += 60
        
        # Apply adjustments for multiple deficiencies
        if len(deficiencies) > 1:
            min_days = int(min_days * 0.9)  # 10% faster for overlapping treatments
            max_days = int(max_days * 1.1)  # 10% slower for interactions
        
        return min_days, max_days
    
    def _parse_deficiency_response(self, response: str) -> List[Deficiency]:
        """Parse Gemini response into Deficiency objects"""
        deficiencies = []
        
        try:
            # Extract JSON part from the response
            json_str = re.search(r'\{.*\}', response, re.DOTALL).group()
            import json
            data = json.loads(json_str)
            
            for item in data.get('deficiencies', []):
                deficiency = Deficiency(
                    name=item['name'],
                    current_value=item['current_value'],
                    normal_range=item['normal_range'],
                    severity=item['severity'],
                    is_border_value=item['is_border_value']
                )
                deficiencies.append(deficiency)
        except Exception as e:
            self.logger.warning(f"Failed to parse JSON response: {str(e)}")
            # Fallback to simple parsing if JSON fails
            deficiencies = self._fallback_parse(response)
        
        return deficiencies

    def _fallback_parse(self, response: str) -> List[Deficiency]:
        """Fallback parsing when JSON parsing fails"""
        deficiencies = []
        lines = response.split('\n')
        
        for line in lines:
            if ":" in line and any(keyword in line.lower() for keyword in ['deficiency', 'low', 'high', 'border']):
                parts = line.split(":")
                name = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ""
                
                # Determine severity based on keywords
                severity = "medium"
                if "low" in line.lower():
                    severity = "low"
                elif "high" in line.lower():
                    severity = "high"
                
                deficiency = Deficiency(
                    name=name,
                    current_value=value,
                    normal_range="",
                    severity=severity,
                    is_border_value="border" in line.lower()
                )
                deficiencies.append(deficiency)
        
        return deficiencies