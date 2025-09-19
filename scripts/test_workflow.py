#!/usr/bin/env python3
"""
Complete Workflow Test Script
Tests the full end-to-end workflow of the Insight MVP system
"""

import asyncio
import httpx
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 60.0

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class WorkflowTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.client = None
        self.test_results = []
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def log_success(self, message: str):
        print(f"{Colors.GREEN}✓ {message}{Colors.NC}")
        self.test_results.append(("PASS", message))
    
    def log_error(self, message: str):
        print(f"{Colors.RED}✗ {message}{Colors.NC}")
        self.test_results.append(("FAIL", message))
    
    def log_info(self, message: str):
        print(f"{Colors.BLUE}ℹ {message}{Colors.NC}")
    
    def log_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")
    
    async def test_system_health(self):
        """Test overall system health"""
        print(f"\n{Colors.YELLOW}🏥 Testing System Health{Colors.NC}")
        print("=" * 50)
        
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_success("Gateway is healthy")
            else:
                self.log_error(f"Gateway health check failed: {response.status_code}")
                return False
                
            # Check all services
            response = await self.client.get(f"{self.base_url}/health/services")
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get("overall_status") == "healthy":
                    self.log_success("All microservices are healthy")
                else:
                    self.log_warning("Some services may be degraded")
                    for service, status in health_data.get("services", {}).items():
                        if status.get("status") != "healthy":
                            self.log_error(f"Service {service} is unhealthy: {status.get('error', 'Unknown error')}")
            else:
                self.log_error("Failed to check service health")
                return False
                
            return True
            
        except Exception as e:
            self.log_error(f"Health check failed: {str(e)}")
            return False
    
    async def test_document_ingestion(self):
        """Test document ingestion workflow"""
        print(f"\n{Colors.YELLOW}📄 Testing Document Ingestion{Colors.NC}")
        print("=" * 50)
        
        try:
            # Check if there are existing documents
            response = await self.client.get(f"{self.base_url}/documents")
            if response.status_code == 200:
                documents = response.json()
                self.log_success(f"Retrieved documents list: {len(documents)} documents found")
                
                if len(documents) > 0:
                    # Test getting a specific document
                    doc_id = documents[0]["id"]
                    response = await self.client.get(f"{self.base_url}/documents/{doc_id}")
                    if response.status_code == 200:
                        self.log_success(f"Retrieved document details for ID {doc_id}")
                    else:
                        self.log_error(f"Failed to retrieve document {doc_id}")
                else:
                    self.log_warning("No documents found - you may want to ingest some PDFs first")
                    
                # Test document statistics
                response = await self.client.get(f"{self.base_url}/documents/stats")
                if response.status_code == 200:
                    stats = response.json()
                    self.log_success(f"Document stats: {stats.get('total_documents', 0)} docs, {stats.get('total_pages', 0)} pages")
                else:
                    self.log_error("Failed to retrieve document statistics")
                    
                return len(documents) > 0
            else:
                self.log_error("Failed to retrieve documents list")
                return False
                
        except Exception as e:
            self.log_error(f"Document ingestion test failed: {str(e)}")
            return False
    
    async def test_vector_search(self):
        """Test vector search functionality"""
        print(f"\n{Colors.YELLOW}🔍 Testing Vector Search{Colors.NC}")
        print("=" * 50)
        
        try:
            # Test vector collections
            response = await self.client.get(f"{self.base_url}/search/collections")
            if response.status_code == 200:
                collections = response.json()
                self.log_success("Retrieved vector collections")
            else:
                self.log_error("Failed to retrieve vector collections")
                return False
            
            # Test semantic search
            search_queries = [
                "strategic opportunities and market analysis",
                "risk assessment and mitigation strategies", 
                "competitive landscape and industry trends",
                "technology innovation and digital transformation"
            ]
            
            for query in search_queries:
                payload = {"query": query, "top_k": 3}
                response = await self.client.post(f"{self.base_url}/search", json=payload)
                
                if response.status_code == 200:
                    results = response.json()
                    self.log_success(f"Search '{query[:30]}...': {len(results)} results")
                    
                    # Check result quality
                    if results and len(results) > 0:
                        top_result = results[0]
                        score = top_result.get("score", 0)
                        if score > 0.5:
                            self.log_info(f"  High relevance score: {score:.3f}")
                        else:
                            self.log_warning(f"  Low relevance score: {score:.3f}")
                else:
                    self.log_error(f"Search failed for query: {query}")
                    
            return True
            
        except Exception as e:
            self.log_error(f"Vector search test failed: {str(e)}")
            return False
    
    async def test_analysis_types(self):
        """Test all 5 strategic analysis types"""
        print(f"\n{Colors.YELLOW}📊 Testing Strategic Analysis Types{Colors.NC}")
        print("=" * 50)
        
        # Test scenarios for each analysis type
        analysis_tests = [
            {
                "endpoint": "/analysis/synthesize",
                "name": "Synthèse Exécutive",
                "query": "Quelles sont les principales opportunités stratégiques identifiées dans nos documents?",
                "title": "Synthèse Stratégique Test"
            },
            {
                "endpoint": "/analysis/competition", 
                "name": "Analyse Concurrentielle",
                "query": "Qui sont nos principaux concurrents et comment se positionnent-ils sur le marché?",
                "title": "Analyse Concurrentielle Test"
            },
            {
                "endpoint": "/analysis/tech-watch",
                "name": "Veille Technologique", 
                "query": "Quelles sont les technologies émergentes qui pourraient impacter notre secteur?",
                "title": "Veille Technologique Test"
            },
            {
                "endpoint": "/analysis/risk-analysis",
                "name": "Analyse de Risques",
                "query": "Quels sont les principaux risques identifiés et comment les mitiger?",
                "title": "Analyse de Risques Test"
            },
            {
                "endpoint": "/analysis/market-study",
                "name": "Étude de Marché",
                "query": "Quelle est la taille du marché et les perspectives de croissance?",
                "title": "Étude de Marché Test"
            }
        ]
        
        successful_analyses = 0
        
        try:
            for test in analysis_tests:
                payload = {
                    "query": test["query"],
                    "title": test["title"],
                    "top_k": 5
                }
                
                response = await self.client.post(f"{self.base_url}{test['endpoint']}", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_success(f"{test['name']}: Analysis completed")
                    
                    # Validate response structure
                    required_fields = ["analysis_type", "title", "content", "sources", "metadata"]
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if not missing_fields:
                        self.log_info(f"  Response structure is valid")
                        content_length = len(result.get("content", ""))
                        sources_count = len(result.get("sources", []))
                        self.log_info(f"  Content length: {content_length} chars, Sources: {sources_count}")
                        successful_analyses += 1
                    else:
                        self.log_warning(f"  Missing fields: {missing_fields}")
                        
                else:
                    self.log_error(f"{test['name']}: Analysis failed (HTTP {response.status_code})")
                    
                # Small delay between requests
                await asyncio.sleep(1)
                
            return successful_analyses == len(analysis_tests)
            
        except Exception as e:
            self.log_error(f"Analysis types test failed: {str(e)}")
            return False
    
    async def test_report_generation(self):
        """Test report generation and management"""
        print(f"\n{Colors.YELLOW}📑 Testing Report Generation{Colors.NC}")
        print("=" * 50)
        
        try:
            # Test listing existing reports
            response = await self.client.get(f"{self.base_url}/reports")
            if response.status_code == 200:
                reports = response.json()
                self.log_success(f"Retrieved reports list: {len(reports)} reports found")
                
                if len(reports) > 0:
                    # Test getting a specific report
                    report_id = reports[0]["id"]
                    response = await self.client.get(f"{self.base_url}/reports/{report_id}")
                    if response.status_code == 200:
                        report_detail = response.json()
                        self.log_success(f"Retrieved report details for ID {report_id}")
                        
                        # Test PDF export
                        response = await self.client.get(f"{self.base_url}/reports/{report_id}/export")
                        if response.status_code == 200:
                            self.log_success(f"Successfully exported report {report_id} as PDF")
                        else:
                            self.log_error(f"Failed to export report {report_id} as PDF")
                    else:
                        self.log_error(f"Failed to retrieve report {report_id}")
                        
                # Test report statistics
                response = await self.client.get(f"{self.base_url}/reports/stats")
                if response.status_code == 200:
                    stats = response.json()
                    self.log_success(f"Report stats: {stats.get('total_reports', 0)} total reports")
                    by_type = stats.get('by_analysis_type', {})
                    if by_type:
                        for analysis_type, count in by_type.items():
                            self.log_info(f"  {analysis_type}: {count} reports")
                else:
                    self.log_error("Failed to retrieve report statistics")
                    
                return True
            else:
                self.log_error("Failed to retrieve reports list")
                return False
                
        except Exception as e:
            self.log_error(f"Report generation test failed: {str(e)}")
            return False
    
    async def test_complete_workflow(self):
        """Test complete end-to-end workflow"""
        print(f"\n{Colors.YELLOW}🔄 Testing Complete Workflow{Colors.NC}")
        print("=" * 50)
        
        try:
            # Test the integrated workflow endpoint
            workflow_payload = {
                "analysis_type": "synthesize",
                "query": "Effectuer une synthèse complète des opportunités stratégiques",
                "title": "Test Workflow Complet",
                "auto_export": True
            }
            
            self.log_info("Starting complete workflow: analysis + report generation")
            response = await self.client.post(f"{self.base_url}/workflows/analyze-and-report", params=workflow_payload)
            
            if response.status_code == 200:
                result = response.json()
                self.log_success("Complete workflow executed successfully")
                
                # Validate workflow result
                if "analysis" in result and "report" in result:
                    self.log_success("Workflow includes both analysis and report")
                    
                    analysis = result["analysis"]
                    report = result["report"]
                    
                    self.log_info(f"Analysis title: {analysis.get('title', 'N/A')}")
                    self.log_info(f"Report ID: {report.get('id', 'N/A')}")
                    
                    if "export_url" in result:
                        self.log_success("Auto-export URL provided")
                    
                    return True
                else:
                    self.log_error("Workflow result missing analysis or report")
                    return False
            else:
                self.log_error(f"Complete workflow failed (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            self.log_error(f"Complete workflow test failed: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all workflow tests"""
        print(f"{Colors.BLUE}🧪 Starting Complete Workflow Tests{Colors.NC}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run tests in sequence
        tests = [
            ("System Health", self.test_system_health),
            ("Document Ingestion", self.test_document_ingestion),
            ("Vector Search", self.test_vector_search),
            ("Analysis Types", self.test_analysis_types),
            ("Report Generation", self.test_report_generation),
            ("Complete Workflow", self.test_complete_workflow)
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
                else:
                    failed_tests += 1
            except Exception as e:
                self.log_error(f"{test_name} test crashed: {str(e)}")
                failed_tests += 1
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{Colors.BLUE}📊 TEST SUMMARY{Colors.NC}")
        print("=" * 60)
        print(f"Total Tests: {passed_tests + failed_tests}")
        print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.NC}")
        print(f"{Colors.RED}Failed: {failed_tests}{Colors.NC}")
        print(f"Duration: {duration:.2f} seconds")
        
        if failed_tests == 0:
            print(f"\n{Colors.GREEN}🎉 ALL WORKFLOW TESTS PASSED!{Colors.NC}")
            print("The Insight MVP system is fully functional.")
            return True
        else:
            print(f"\n{Colors.RED}❌ Some workflow tests failed.{Colors.NC}")
            print("Check the details above and service logs for more information.")
            return False

async def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        global BASE_URL
        BASE_URL = sys.argv[1]
    
    print(f"Testing Insight MVP at: {BASE_URL}")
    
    async with WorkflowTester() as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
