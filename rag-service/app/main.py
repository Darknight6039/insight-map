import os
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from loguru import logger
from openai import OpenAI

# Import our prompt templates
import sys
sys.path.append("/app")
from prompts.templates import (
    ANALYSIS_PROMPTS, 
    get_prompt_template, 
    format_context, 
    format_sources
)

VECTOR_URL = os.environ.get("VECTOR_URL", "http://vector-service:8002")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BRAND_LOGO_PATH = os.environ.get("BRAND_LOGO_PATH", "/app/data/logo/logo.svg")

app = FastAPI(title="RAG Service - Strategic Intelligence", version="0.1.0")


# Updated Pydantic models for the 5 analysis types
class AskPayload(BaseModel):
    query: str
    top_k: Optional[int] = 5

class ReportPayload(BaseModel):
    title: str
    query: str
    brand: Optional[dict] = None

class AnalysisPayload(BaseModel):
    query: str
    title: Optional[str] = None
    top_k: Optional[int] = 8
    context_override: Optional[str] = None  # Allow manual context

class SyntheseExecutivePayload(AnalysisPayload):
    pass

class AnalyseConcurrentiellePayload(AnalysisPayload):
    pass

class VeilleTechnologiquePayload(AnalysisPayload):
    pass

class AnalyseRisquesPayload(AnalysisPayload):
    pass

class EtudeMarchePayload(AnalysisPayload):
    pass

class AnalysisResponse(BaseModel):
    analysis_type: str
    title: str
    content: str
    sources: List[Dict]
    metadata: Dict
    timestamp: datetime


def build_analysis_prompt(analysis_type: str, query: str, passages: List[Dict]) -> str:
    """Build a specialized prompt for the given analysis type"""
    template = get_prompt_template(analysis_type)
    context = format_context(passages)
    sources = format_sources(passages)
    
    # Format the template with context and sources
    formatted_prompt = template.format(
        context=context,
        sources=sources,
        query=query
    )
    
    return formatted_prompt

def build_prompt(query: str, passages: List[Dict]) -> str:
    """Legacy function for backward compatibility"""
    return build_analysis_prompt("synthese_executive", query, passages)


async def get_passages(query: str, top_k: int):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{VECTOR_URL}/search", json={"query": query, "top_k": top_k})
        r.raise_for_status()
        return r.json()


def call_openai(prompt: str, analysis_type: str = "general") -> str:
    """Call OpenAI with specialized system prompts based on analysis type"""
    if not OPENAI_API_KEY:
        return f"[OpenAI API key not configured]\n\nAnalysis Type: {analysis_type}\n\n" + prompt[:500]
    
    # Specialized system prompts based on analysis type
    system_prompts = {
        "synthese_executive": "Tu es un consultant senior en stratégie d'entreprise. Produis des synthèses exécutives claires et actionnables.",
        "analyse_concurrentielle": "Tu es un expert en intelligence concurrentielle. Analyse les dynamiques de marché et identifie les positionnements stratégiques.",
        "veille_technologique": "Tu es un expert en innovation technologique. Identifie les tendances tech émergentes et leurs implications business.",
        "analyse_risques": "Tu es un expert en risk management. Effectue des analyses de risques méthodiques et propose des mesures de mitigation.",
        "etude_marche": "Tu es un analyste marché senior. Réalise des études de marché approfondies avec projections et scénarios.",
        "general": "Tu es un consultant senior en stratégie d'entreprise."
    }
    
    system_prompt = system_prompts.get(analysis_type, system_prompts["general"])
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,  # Increased for more detailed analysis
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return f"[Erreur API OpenAI: {str(e)}]\n\nType d'analyse: {analysis_type}\n\nPrompt de fallback:\n{prompt[:500]}..."


async def perform_analysis(analysis_type: str, payload: AnalysisPayload) -> AnalysisResponse:
    """Core analysis function used by all 5 analysis endpoints"""
    try:
        # Get relevant passages from vector search
        if payload.context_override:
            passages = []  # Use provided context instead
            context = payload.context_override
        else:
            passages = await get_passages(payload.query, payload.top_k or 8)
        
        # Build specialized prompt
        prompt = build_analysis_prompt(analysis_type, payload.query, passages)
        
        # Get AI analysis
        analysis_content = call_openai(prompt, analysis_type)
        
        # Build response
        response = AnalysisResponse(
            analysis_type=analysis_type,
            title=payload.title or f"Analyse {analysis_type.replace('_', ' ').title()}",
            content=analysis_content,
            sources=passages,
            metadata={
                "query": payload.query,
                "passages_count": len(passages),
                "top_k": payload.top_k or 8,
                "used_context_override": bool(payload.context_override)
            },
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Generated {analysis_type} analysis for query: {payload.query[:50]}...")
        return response
        
    except Exception as e:
        logger.error(f"Error in {analysis_type} analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/health")
def health():
    return {"status": "ok", "service": "rag-service", "available_analyses": list(ANALYSIS_PROMPTS.keys())}

@app.get("/analysis_types")
def get_analysis_types():
    """Get list of available analysis types"""
    return {
        "available_types": list(ANALYSIS_PROMPTS.keys()),
        "descriptions": {
            "synthese_executive": "Synthèse exécutive avec recommandations stratégiques",
            "analyse_concurrentielle": "Analyse de la concurrence et positionnement marché",
            "veille_technologique": "Veille des innovations et tendances technologiques",
            "analyse_risques": "Analyse des risques et mesures de mitigation",
            "etude_marche": "Étude de marché complète avec projections"
        }
    }

# THE 5 MAIN ANALYSIS ENDPOINTS

@app.post("/synthesize", response_model=AnalysisResponse)
async def synthesize(payload: SyntheseExecutivePayload):
    """PROMPT 1: Génère une synthèse exécutive stratégique"""
    return await perform_analysis("synthese_executive", payload)

@app.post("/analyze_competition", response_model=AnalysisResponse)
async def analyze_competition(payload: AnalyseConcurrentiellePayload):
    """PROMPT 2: Analyse concurrentielle et mapping du marché"""
    return await perform_analysis("analyse_concurrentielle", payload)

@app.post("/tech_watch", response_model=AnalysisResponse)
async def tech_watch(payload: VeilleTechnologiquePayload):
    """PROMPT 3: Veille technologique et innovation"""
    return await perform_analysis("veille_technologique", payload)

@app.post("/risk_analysis", response_model=AnalysisResponse)
async def risk_analysis(payload: AnalyseRisquesPayload):
    """PROMPT 4: Analyse des risques méthodique"""
    return await perform_analysis("analyse_risques", payload)

@app.post("/market_study", response_model=AnalysisResponse)
async def market_study(payload: EtudeMarchePayload):
    """PROMPT 5: Étude de marché complète"""
    return await perform_analysis("etude_marche", payload)

# LEGACY ENDPOINTS FOR BACKWARD COMPATIBILITY

@app.post("/ask_question")
async def ask_question(payload: AskPayload):
    """Legacy endpoint - basic Q&A"""
    passages = await get_passages(payload.query, payload.top_k or 5)
    prompt = build_prompt(payload.query, passages)
    answer = call_openai(prompt)
    return {"answer": answer, "citations": passages}

@app.post("/generate_report")
async def generate_report(payload: ReportPayload):
    """Legacy endpoint - generate basic report"""
    passages = await get_passages(payload.query, 8)
    prompt = build_prompt(payload.query, passages)
    answer = call_openai(prompt)
    report = {
        "title": payload.title,
        "executive_summary": answer,
        "citations": passages,
        "brand": payload.brand or {"logo_path": BRAND_LOGO_PATH},
    }
    return report


