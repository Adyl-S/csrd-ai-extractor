import os
import json
from openai import OpenAI
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class OpenAIExtractor:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # High intelligence, fast, multimodal capable

    def extract_indicator(self, context: str, indicator: Dict, company_info: Dict) -> Dict:
        """
        Extracts a specific ESG indicator using OpenAI Structured Outputs.
        """
        
        system_prompt = f"""
        You are an expert Sustainability Data Auditor. 
        Your job is to extract precise data points from Corporate Sustainability Reports (CSRD).
        
        You must output valid JSON.
        """

        user_prompt = f"""
        Analyze the text below from {company_info['name']}'s {company_info['year']} report.
        
        TARGET DATA POINT:
        - Indicator: {indicator['name']}
        - Desired Unit: {indicator['unit']}
        - Search Hints: {indicator.get('hints', '')}

        RULES:
        1. Extract the numeric value for the year {company_info['year']}.
        2. If the exact unit differs (e.g., MWh vs GJ), convert it if trivial, or note it.
        3. If not found, set value to null.
        4. Confidence score: 1.0 (Certain), 0.5 (Ambiguous), 0.0 (Not found).
        
        Return JSON strictly matching this schema:
        {{
            "value": "string or number",
            "unit": "string",
            "source_page": int (best guess based on Page markers),
            "notes": "string (context or why validation failed)",
            "confidence": float
        }}

        --- REPORT CONTEXT ---
        {context}
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0, # Deterministic for data extraction
                response_format={ "type": "json_object" }
            )

            result = json.loads(response.choices[0].message.content)
            
            # Merge metadata
            return {
                "company": company_info['name'],
                "year": company_info['year'],
                "indicator_name": indicator['name'],
                **result
            }

        except Exception as e:
            print(f"Error processing {indicator['name']}: {e}")
            return {
                "company": company_info['name'],
                "year": company_info['year'],
                "indicator_name": indicator['name'],
                "value": None,
                "unit": indicator['unit'],
                "confidence": 0.0,
                "source_page": 0,
                "notes": f"Error: {str(e)}"
            }