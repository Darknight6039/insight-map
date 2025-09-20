"""
API Client for Insight MVP Frontend
Handles communication with backend microservices
"""

import httpx
import json
from typing import Dict, List, Optional, Any
from loguru import logger
import asyncio
from pathlib import Path

class InsightAPIClient:
    def __init__(self, gateway_url: str = "http://localhost:8000"):
        self.gateway_url = gateway_url
        self.timeout = 60.0
        
    async def upload_document(self, file_path: str, title: str, description: str = "") -> Dict:
        """Upload a PDF document for analysis"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(file_path, 'rb') as f:
                    files = {'file': (Path(file_path).name, f, 'application/pdf')}
                    data = {
                        'title': title,
                        'description': description
                    }
                    
                    response = await client.post(
                        f"{self.gateway_url}/documents/upload",
                        files=files,
                        data=data
                    )
                    
                if response.status_code == 200:
                    return {"success": True, "data": response.json()}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_documents(self) -> List[Dict]:
        """Get list of uploaded documents"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.gateway_url}/documents/")
                
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting documents: {e}")
            return []
    
    async def run_analysis(self, analysis_type: str, query: str, title: str = "", doc_id: Optional[int] = None) -> Dict:
        """Run one of the 5 AI analyses"""
        
        analysis_endpoints = {
            "synthese_executive": "/analysis/synthesize",
            "analyse_concurrentielle": "/analysis/analyze-competition", 
            "veille_technologique": "/analysis/tech-watch",
            "analyse_risques": "/analysis/risk-analysis",
            "etude_marche": "/analysis/market-study"
        }
        
        if analysis_type not in analysis_endpoints:
            return {"success": False, "error": f"Unknown analysis type: {analysis_type}"}
        
        try:
            payload = {
                "query": query,
                "title": title or f"Analyse {analysis_type}",
                "top_k": 8
            }
            
            if doc_id:
                payload["doc_id"] = doc_id
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.gateway_url}{analysis_endpoints[analysis_type]}",
                    json=payload
                )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error running analysis {analysis_type}: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_documents(self, query: str, top_k: int = 5) -> Dict:
        """Search documents using semantic search"""
        try:
            payload = {
                "query": query,
                "top_k": top_k
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.gateway_url}/search",
                    json=payload
                )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_report(self, analysis_result: Dict, analysis_type: str) -> Dict:
        """Generate a PDF report from analysis results"""
        try:
            payload = {
                "title": analysis_result.get("title", "Rapport d'Analyse"),
                "content": analysis_result.get("content", ""),
                "analysis_type": analysis_type,
                "metadata": analysis_result.get("metadata", {})
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.gateway_url}/reports/generate",
                    json=payload
                )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {"success": False, "error": str(e)}
    
    async def export_report_pdf(self, report_id: int) -> Dict:
        """Export report as PDF"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.gateway_url}/reports/export/{report_id}"
                )
            
            if response.status_code == 200:
                return {
                    "success": True, 
                    "pdf_content": response.content,
                    "filename": f"rapport_{report_id}.pdf"
                }
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_system_status(self) -> Dict:
        """Get system status from all microservices"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.gateway_url}/status")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"success": False, "error": str(e)}
    
    def run_analysis_sync(self, analysis_type: str, query: str, title: str = "", doc_id: Optional[int] = None) -> Dict:
        """Synchronous wrapper for run_analysis"""
        return asyncio.run(self.run_analysis(analysis_type, query, title, doc_id))
    
    def upload_document_sync(self, file_path: str, title: str, description: str = "") -> Dict:
        """Synchronous wrapper for upload_document"""
        return asyncio.run(self.upload_document(file_path, title, description))
    
    def search_documents_sync(self, query: str, top_k: int = 5) -> Dict:
        """Synchronous wrapper for search_documents"""
        return asyncio.run(self.search_documents(query, top_k))
    
    def generate_report_sync(self, analysis_result: Dict, analysis_type: str) -> Dict:
        """Synchronous wrapper for generate_report"""
        return asyncio.run(self.generate_report(analysis_result, analysis_type))
    
    def get_documents_sync(self) -> List[Dict]:
        """Synchronous wrapper for get_documents"""
        return asyncio.run(self.get_documents())
    
    def get_system_status_sync(self) -> Dict:
        """Synchronous wrapper for get_system_status"""
        return asyncio.run(self.get_system_status())
