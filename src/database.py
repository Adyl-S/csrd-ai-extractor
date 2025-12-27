import sqlite3
import pandas as pd
import os
from typing import Dict
from pathlib import Path

class CSRDDatabase:
    def __init__(self, db_name="csrd_data.db"):
        # FORCE ABSOLUTE PATH: resolves to csrd_openai/data/csrd_data.db
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = base_dir / "data"
        self.db_path = self.data_dir / db_name
        
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔌 Connecting to database at: {self.db_path}")
        self.init_database()

    def init_database(self):
        """Creates tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main storage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extractions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT,
                    year INTEGER,
                    indicator_name TEXT,
                    value TEXT,
                    unit TEXT,
                    confidence REAL,
                    source_page INTEGER,
                    notes TEXT,
                    UNIQUE(company, year, indicator_name)
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"🔥 Database Initialization Failed: {e}")
            raise e

    def save_extraction(self, data: Dict):
        """Saves a single extraction result."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO extractions 
                (company, report_year, indicator_name, value, unit, confidence, source_page, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['company'], data['year'], data['indicator_name'],
                str(data['value']), data['unit'], data['confidence'],
                data['source_page'], data['notes']
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Save Error ({data['indicator_name']}): {e}")

    def export_csv(self, filename="csrd_results_openai.csv"):
        """Exports data to CSV."""
        output_path = self.data_dir / filename
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql("SELECT * FROM extractions ORDER BY company, indicator_name", conn)
            df.to_csv(output_path, index=False)
            conn.close()
            print(f"✅ Data exported to: {output_path}")
            return df
        except Exception as e:
            print(f"❌ Export Failed: {e}")
            return pd.DataFrame() # Return empty DF on failure