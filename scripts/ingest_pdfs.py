#!/usr/bin/env python3
"""
Script d'ingestion automatique des PDFs depuis data/pdfs/
"""

import os
import sys
import requests
from pathlib import Path
import time

DOCUMENT_SERVICE_URL = "http://localhost:8001"
DATA_FOLDER = "../data/pdfs"

def get_pdf_files(folder):
    pdf_folder = Path(folder)
    if not pdf_folder.exists():
        print(f"❌ Dossier introuvable : {folder}")
        return []
    pdf_files = list(pdf_folder.glob("*.pdf"))
    print(f"📁 Trouvé {len(pdf_files)} fichiers PDF")
    return pdf_files

def get_existing_documents():
    try:
        response = requests.get(f"{DOCUMENT_SERVICE_URL}/documents", timeout=10)
        if response.status_code == 200:
            docs = response.json()
            return {doc['filename'] for doc in docs}
        return set()
    except:
        return set()

def ingest_pdf(pdf_path):
    filename = pdf_path.name
    title = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()
    
    try:
        print(f"\n📄 Ingestion : {filename}")
        with open(pdf_path, 'rb') as f:
            files = {'file': (filename, f, 'application/pdf')}
            data = {'title': title}
            response = requests.post(
                f"{DOCUMENT_SERVICE_URL}/ingest",
                files=files,
                data=data,
                timeout=120
            )
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Succès ! ID: {result.get('id')}, Pages: {result.get('pages_count')}")
                return True
            else:
                print(f"   ❌ Erreur {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Erreur : {e}")
        return False

def main():
    print("🚀 INGESTION AUTOMATIQUE DES PDFs")
    print("=" * 50)
    
    # Vérifier connectivité
    try:
        requests.get(f"{DOCUMENT_SERVICE_URL}/health", timeout=5)
        print("✅ Document-service accessible\n")
    except:
        print("❌ Document-service non disponible")
        sys.exit(1)
    
    # Récupérer documents existants
    existing = get_existing_documents()
    print(f"📋 {len(existing)} documents déjà ingérés\n")
    
    # Récupérer PDFs
    pdf_files = get_pdf_files(DATA_FOLDER)
    if not pdf_files:
        print("❌ Aucun PDF trouvé")
        sys.exit(1)
    
    # Ingérer
    success = 0
    skipped = 0
    failed = 0
    
    for i, pdf in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] {pdf.name}")
        if pdf.name in existing:
            print("   ⏭️  Déjà ingéré")
            skipped += 1
            continue
        
        if ingest_pdf(pdf):
            success += 1
            time.sleep(1)
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Réussis : {success}")
    print(f"⏭️  Ignorés : {skipped}")
    print(f"❌ Échoués : {failed}")
    print("✨ Terminé !")

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()

