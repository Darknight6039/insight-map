#!/usr/bin/env python3
"""
Final Validation Script for Insight MVP
Validates the complete system is ready for production use
"""

import asyncio
import httpx
import sys
import os
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    BOLD = '\033[1m'
    NC = '\033[0m'

class FinalValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.client = None
        self.validation_results = []
        
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    def log_success(self, message: str):
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
        self.validation_results.append(("PASS", message))
    
    def log_error(self, message: str):
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        self.validation_results.append(("FAIL", message))
    
    def log_warning(self, message: str):
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")
        self.validation_results.append(("WARN", message))
    
    def log_info(self, message: str):
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}")
    
    def log_section(self, title: str):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.NC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.NC}")
    
    async def validate_project_structure(self):
        """Validate project structure and required files"""
        self.log_section("🏗️  PROJECT STRUCTURE VALIDATION")
        
        # Check required directories
        required_dirs = [
            "data/pdfs",
            "data/reports", 
            "data/logo",
            "gateway-api/app",
            "document-service/app",
            "vector-service/app", 
            "rag-service/app",
            "rag-service/prompts",
            "report-service/app",
            "status-service/app",
            "scripts"
        ]
        
        for directory in required_dirs:
            if Path(directory).exists():
                self.log_success(f"Directory exists: {directory}")
            else:
                self.log_error(f"Missing directory: {directory}")
        
        # Check required files
        required_files = [
            "docker-compose.yml",
            "env.example", 
            "README.md",
            "scripts/test_all_services.sh",
            "scripts/test_workflow.py",
            "scripts/example_calls.sh",
            "rag-service/prompts/templates.py"
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                self.log_success(f"File exists: {file_path}")
            else:
                self.log_error(f"Missing file: {file_path}")
        
        # Check service requirements.txt files
        services = ["gateway-api", "document-service", "vector-service", "rag-service", "report-service"]
        for service in services:
            req_file = f"{service}/requirements.txt"
            if Path(req_file).exists():
                self.log_success(f"Requirements file exists: {req_file}")
            else:
                self.log_error(f"Missing requirements file: {req_file}")
        
        return True
    
    async def validate_environment_config(self):
        """Validate environment configuration"""
        self.log_section("⚙️  ENVIRONMENT CONFIGURATION")
        
        # Check if .env file exists
        if Path(".env").exists():
            self.log_success(".env file exists")
            
            # Check for critical environment variables
            with open(".env", "r") as f:
                env_content = f.read()
                
            critical_vars = [
                "POSTGRES_USER",
                "POSTGRES_PASSWORD", 
                "POSTGRES_DB",
                "OPENAI_API_KEY"
            ]
            
            for var in critical_vars:
                if var in env_content and f"{var}=" in env_content:
                    line = [l for l in env_content.split('\n') if l.startswith(f"{var}=")]
                    if line and not line[0].endswith("your_openai_api_key_here"):
                        self.log_success(f"Environment variable configured: {var}")
                    else:
                        self.log_warning(f"Environment variable needs configuration: {var}")
                else:
                    self.log_error(f"Missing environment variable: {var}")
        else:
            self.log_warning(".env file not found - using env.example as reference")
            if Path("env.example").exists():
                self.log_info("Copy env.example to .env and configure values")
            else:
                self.log_error("env.example template missing")
        
        return True
    
    async def validate_services_health(self):
        """Validate all microservices are healthy"""
        self.log_section("🏥 SERVICES HEALTH VALIDATION")
        
        try:
            # Test gateway health
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                self.log_success("Gateway API is healthy")
            else:
                self.log_error(f"Gateway API unhealthy: HTTP {response.status_code}")
                return False
            
            # Test all services health
            response = await self.client.get(f"{self.base_url}/health/services")
            if response.status_code == 200:
                health_data = response.json()
                overall_status = health_data.get("overall_status", "unknown")
                
                if overall_status == "healthy":
                    self.log_success("All microservices are healthy")
                else:
                    self.log_warning(f"System status: {overall_status}")
                
                # Check individual services
                services = health_data.get("services", {})
                for service_name, service_info in services.items():
                    status = service_info.get("status", "unknown")
                    if status == "healthy":
                        self.log_success(f"Service {service_name}: healthy")
                    else:
                        error = service_info.get("error", "Unknown error")
                        self.log_error(f"Service {service_name}: {status} - {error}")
                
                return overall_status == "healthy"
            else:
                self.log_error("Failed to get services health status")
                return False
                
        except Exception as e:
            self.log_error(f"Health check failed: {str(e)}")
            self.log_info("Make sure all services are running: docker-compose up -d")
            return False
    
    async def validate_api_endpoints(self):
        """Validate critical API endpoints"""
        self.log_section("🌐 API ENDPOINTS VALIDATION")
        
        endpoints_to_test = [
            ("/health", "Gateway health"),
            ("/analysis/types", "Analysis types"),
            ("/documents", "Documents list"),
            ("/reports", "Reports list"),
            ("/search/collections", "Vector collections"),
            ("/docs", "Swagger documentation")
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints_to_test:
            try:
                response = await self.client.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    self.log_success(f"{description}: HTTP {response.status_code}")
                else:
                    self.log_error(f"{description}: HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_error(f"{description}: Failed - {str(e)}")
                all_passed = False
        
        return all_passed
    
    async def validate_analysis_capabilities(self):
        """Validate the 5 analysis types"""
        self.log_section("🧠 ANALYSIS CAPABILITIES VALIDATION")
        
        analysis_types = [
            ("synthesize", "Synthèse Exécutive"),
            ("competition", "Analyse Concurrentielle"), 
            ("tech-watch", "Veille Technologique"),
            ("risk-analysis", "Analyse de Risques"),
            ("market-study", "Étude de Marché")
        ]
        
        # First check if analysis types endpoint works
        try:
            response = await self.client.get(f"{self.base_url}/analysis/types")
            if response.status_code == 200:
                types_data = response.json()
                available_types = types_data.get("available_types", [])
                self.log_success(f"Analysis types endpoint working: {len(available_types)} types available")
            else:
                self.log_error("Analysis types endpoint failed")
                return False
        except Exception as e:
            self.log_error(f"Analysis types check failed: {str(e)}")
            return False
        
        # Test each analysis type with a simple query
        test_payload = {
            "query": "Test validation query for system check",
            "title": "Validation Test",
            "top_k": 3
        }
        
        all_passed = True
        
        for analysis_type, description in analysis_types:
            try:
                response = await self.client.post(
                    f"{self.base_url}/analysis/{analysis_type.replace('_', '-')}", 
                    json=test_payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "analysis_type" in result and "content" in result:
                        self.log_success(f"{description}: Analysis endpoint working")
                    else:
                        self.log_warning(f"{description}: Response structure incomplete")
                else:
                    self.log_error(f"{description}: HTTP {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_error(f"{description}: Failed - {str(e)}")
                all_passed = False
        
        return all_passed
    
    async def validate_documentation(self):
        """Validate documentation and examples"""
        self.log_section("📚 DOCUMENTATION VALIDATION")
        
        # Check Swagger docs
        try:
            response = await self.client.get(f"{self.base_url}/docs")
            if response.status_code == 200:
                self.log_success("Swagger documentation accessible")
            else:
                self.log_error("Swagger documentation not accessible")
        except Exception as e:
            self.log_error(f"Swagger documentation check failed: {str(e)}")
        
        # Check OpenAPI schema
        try:
            response = await self.client.get(f"{self.base_url}/openapi.json")
            if response.status_code == 200:
                schema = response.json()
                if "info" in schema and "paths" in schema:
                    self.log_success("OpenAPI schema valid")
                    paths_count = len(schema.get("paths", {}))
                    self.log_info(f"API has {paths_count} documented endpoints")
                else:
                    self.log_error("OpenAPI schema incomplete")
            else:
                self.log_error("OpenAPI schema not accessible")
        except Exception as e:
            self.log_error(f"OpenAPI schema check failed: {str(e)}")
        
        # Check if scripts are executable
        scripts = ["test_all_services.sh", "test_workflow.py", "example_calls.sh"]
        for script in scripts:
            script_path = Path(f"scripts/{script}")
            if script_path.exists():
                if os.access(script_path, os.X_OK):
                    self.log_success(f"Script executable: {script}")
                else:
                    self.log_warning(f"Script not executable: {script} (run: chmod +x scripts/{script})")
            else:
                self.log_error(f"Missing script: {script}")
        
        return True
    
    async def run_final_validation(self):
        """Run complete validation suite"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("🔍 INSIGHT MVP - FINAL VALIDATION")
        print("=" * 60)
        print("Validating complete system for production readiness")
        print(f"{Colors.NC}")
        
        validation_steps = [
            ("Project Structure", self.validate_project_structure),
            ("Environment Config", self.validate_environment_config),
            ("Services Health", self.validate_services_health),
            ("API Endpoints", self.validate_api_endpoints),
            ("Analysis Capabilities", self.validate_analysis_capabilities),
            ("Documentation", self.validate_documentation)
        ]
        
        passed_validations = 0
        total_validations = len(validation_steps)
        
        for step_name, validation_func in validation_steps:
            try:
                result = await validation_func()
                if result:
                    passed_validations += 1
            except Exception as e:
                self.log_error(f"{step_name} validation crashed: {str(e)}")
        
        # Final summary
        self.log_section("📊 VALIDATION SUMMARY")
        
        passed_count = len([r for r in self.validation_results if r[0] == "PASS"])
        failed_count = len([r for r in self.validation_results if r[0] == "FAIL"])
        warning_count = len([r for r in self.validation_results if r[0] == "WARN"])
        
        print(f"Total Validations: {passed_count + failed_count + warning_count}")
        print(f"{Colors.GREEN}✅ Passed: {passed_count}{Colors.NC}")
        print(f"{Colors.RED}❌ Failed: {failed_count}{Colors.NC}") 
        print(f"{Colors.YELLOW}⚠️  Warnings: {warning_count}{Colors.NC}")
        
        if failed_count == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 SYSTEM VALIDATION SUCCESSFUL!{Colors.NC}")
            print(f"{Colors.GREEN}The Insight MVP is ready for production use.{Colors.NC}")
            print(f"\n{Colors.BLUE}🚀 Next Steps:{Colors.NC}")
            print("1. Access Swagger docs: http://localhost:8000/docs")
            print("2. Run example API calls: ./scripts/example_calls.sh")
            print("3. Test complete workflow: python3 scripts/test_workflow.py")
            print("4. Upload PDFs and start analyzing!")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ SYSTEM VALIDATION FAILED{Colors.NC}")
            print(f"{Colors.RED}Please fix the issues above before using in production.{Colors.NC}")
            print(f"\n{Colors.YELLOW}💡 Troubleshooting:{Colors.NC}")
            print("1. Check docker-compose logs for service errors")
            print("2. Verify .env configuration")
            print("3. Ensure OpenAI API key is valid")
            print("4. Run: docker-compose up -d --build")
            return False

async def main():
    """Main validation runner"""
    async with FinalValidator() as validator:
        success = await validator.run_final_validation()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
