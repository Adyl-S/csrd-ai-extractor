import time
from tqdm import tqdm
from database import CSRDDatabase
from pdf_parser import PDFParser
from extractor import OpenAIExtractor

# --- CONFIGURATION ---
BANKS = [
    {"name": "AIB", "year": 2024, "file": "data/reports/AIB_2024.pdf"},
    {"name": "BBVA", "year": 2024, "file": "data/reports/BBVA_2024.pdf"},
    {"name": "BPCE", "year": 2024, "file": "data/reports/BPCE_2024.pdf"},
]

INDICATORS = [
    # Environmental
    {"name": "Total Scope 1 GHG Emissions", "unit": "tCO2e", "hints": "direct emissions, gross direct"},
    {"name": "Total Scope 2 GHG Emissions", "unit": "tCO2e", "hints": "market-based, location-based, indirect"},
    {"name": "Total Scope 3 GHG Emissions", "unit": "tCO2e", "hints": "value chain, financed emissions, category 1-15"},
    {"name": "GHG Emissions Intensity", "unit": "tCO2e/€M", "hints": "intensity ratio, carbon footprint per revenue"},
    {"name": "Total Energy Consumption", "unit": "MWh", "hints": "gigajoules, electricity, gas, oil"},
    {"name": "Renewable Energy Percentage", "unit": "%", "hints": "green electricity, renewable sources"},
    {"name": "Net Zero Target Year", "unit": "Year", "hints": "carbon neutrality, ambition"},
    {"name": "Green Financing Volume", "unit": "€ Millions", "hints": "sustainable finance, green bonds, mobilization"},
    # Social
    {"name": "Total Employees", "unit": "FTE", "hints": "headcount, workforce, full time equivalent"},
    {"name": "Female Employees", "unit": "%", "hints": "women, gender balance, diversity"},
    {"name": "Gender Pay Gap", "unit": "%", "hints": "equal pay, remuneration difference"},
    {"name": "Training Hours per Employee", "unit": "Hours", "hints": "learning, development, average training"},
    {"name": "Employee Turnover Rate", "unit": "%", "hints": "attrition, departure, new hires"},
    {"name": "Work-Related Accidents", "unit": "Count", "hints": "injuries, frequency rate, LTIR"},
    {"name": "Collective Bargaining Coverage", "unit": "%", "hints": "union, labor agreement, social dialogue"},
    # Governance
    {"name": "Board Female Representation", "unit": "%", "hints": "women on board, director diversity"},
    {"name": "Board Meetings", "unit": "Count", "hints": "attendance, number of meetings"},
    {"name": "Corruption Incidents", "unit": "Count", "hints": "bribery, whistleblowing, ethics violations"},
    {"name": "Avg Payment Period to Suppliers", "unit": "Days", "hints": "payment terms, invoices"},
    {"name": "Suppliers Screened for ESG", "unit": "%", "hints": "procurement, supply chain audits, eco-vadis"},
]

def main():
    print("🚀 Starting OpenAI CSRD Extractor...")
    
    # Initialize DB (Check connection immediately)
    try:
        db = CSRDDatabase()
    except Exception as e:
        print(f"❌ FATAL: Could not initialize database. {e}")
        return

    ai = OpenAIExtractor()
    
    for bank in BANKS:
        print(f"\n🏦 Processing {bank['name']}...")
        
        # Check if file exists
        import os
        if not os.path.exists(bank['file']):
            print(f"   ⚠️ File not found: {bank['file']} - Skipping.")
            continue

        try:
            # 1. Parse PDF
            parser = PDFParser(bank['file'])
            
            # 2. Loop through indicators
            for ind in tqdm(INDICATORS, desc=f"Extracting {bank['name']}"):
                try:
                    # Dynamic Context Retrieval
                    keywords = ind['name'].split() + ind['hints'].split(', ')
                    context = parser.get_relevant_context(keywords, max_pages=15)
                    
                    # AI Extraction
                    data = ai.extract_indicator(context, ind, bank)
                    
                    # Save
                    db.save_extraction(data)
                    
                except Exception as inner_e:
                    # If one indicator fails, log it and continue to the next!
                    print(f"   ⚠️ Error extracting '{ind['name']}': {inner_e}")
                    
        except Exception as e:
            print(f"❌ Critical error processing {bank['name']}: {e}")

    # Final Export
    print("\n💾 Exporting results...")
    db.export_csv()
    print("✅ Done!")

if __name__ == "__main__":
    main()