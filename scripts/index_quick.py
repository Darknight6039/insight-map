#!/usr/bin/env python3
"""
Script d'indexation rapide - indexe seulement 3 PDFs pour test
"""

import os
import requests
import time
from pathlib import Path

GATEWAY_URL = "http://localhost:8000"
PDF_DIR = "/Users/isaiaebongue/insight-mvp/data/pdfs"

def index_pdf(pdf_path: Path):
    """Index un PDF avec timeout plus long"""
    try:
        print(f"📄 Indexation: {pdf_path.name}")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            
            response = requests.post(
                f"{GATEWAY_URL}/documents/upload",
                files=files,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                doc_id = result.get('document', {}).get('id', 'N/A')
                print(f"✅ Succès: Document ID {doc_id}")
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text[:100]}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {str(e)[:100]}")
        return False

def main():
    """Index 3 PDFs seulement pour test"""
    pdf_dir = Path(PDF_DIR)
    pdf_files = list(pdf_dir.glob("*.pdf"))[:3]  # Seulement 3 pour commencer
    
    print(f"🔍 Indexation de {len(pdf_files)} PDFs pour test")
    
    success_count = 0
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] ", end="")
        
        if index_pdf(pdf_file):
            success_count += 1
        
        time.sleep(3)  # Pause entre chaque fichier
    
    print(f"\n🎉 Test terminé: {success_count}/{len(pdf_files)} succès")

if __name__ == "__main__":
    main()
