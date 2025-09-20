#!/usr/bin/env python3
"""
Script pour indexer tous les PDFs du dossier data/pdfs
"""

import os
import requests
import time
import json
from pathlib import Path

GATEWAY_URL = "http://localhost:8000"
PDF_DIR = "/Users/isaiaebongue/insight-mvp/data/pdfs"

def index_pdf(pdf_path: Path):
    """Index un PDF via l'API"""
    try:
        print(f"📄 Indexation: {pdf_path.name}")
        
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path.name, f, 'application/pdf')}
            data = {
                'title': pdf_path.stem.replace('_', ' ').replace('-', ' ').title(),
                'description': f'Document financier - {pdf_path.stem}'
            }
            
            response = requests.post(
                f"{GATEWAY_URL}/documents/upload",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Succès: {result.get('document', {}).get('id', 'N/A')}")
                return True
            else:
                print(f"❌ Erreur {response.status_code}: {response.text[:100]}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Index tous les PDFs"""
    pdf_dir = Path(PDF_DIR)
    
    if not pdf_dir.exists():
        print(f"❌ Dossier non trouvé: {PDF_DIR}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"🔍 Trouvé {len(pdf_files)} fichiers PDF")
    
    success_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] ", end="")
        
        if index_pdf(pdf_file):
            success_count += 1
        
        # Pause pour éviter la surcharge
        time.sleep(2)
    
    print(f"\n🎉 Indexation terminée: {success_count}/{len(pdf_files)} succès")

if __name__ == "__main__":
    main()
