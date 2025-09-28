"""
Backend Service Enhanced - Rapports longs style cabinet de conseil
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import requests
from datetime import datetime
from loguru import logger
from app.business_prompts import get_business_prompt, get_available_business_types, get_business_type_display_name

app = FastAPI(title="Enhanced Backend Intelligence", description="Rapports longs style cabinet de conseil")

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VECTOR_SERVICE_URL = "http://vector-service:8002"

# Modèles Pydantic
class BusinessAnalysisRequest(BaseModel):
    business_type: str
    analysis_type: str
    query: str
    title: Optional[str] = None

class AnalysisResponse(BaseModel):
    analysis_type: str
    business_type: str
    title: str
    content: str
    sources: List[Dict]
    metadata: Dict
    timestamp: str

def search_documents(query: str, top_k: int = 12) -> List[Dict]:
    """Recherche vectorielle étendue"""
    try:
        response = requests.post(
            f"{VECTOR_SERVICE_URL}/search",
            json={"query": query, "top_k": top_k},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("results", [])
        else:
            logger.warning(f"Vector search failed: {response.status_code}")
            return []
            
    except Exception as e:
        logger.error(f"Vector search error: {e}")
        return []

def format_context_extended(documents: List[Dict]) -> str:
    """Formate contexte étendu pour rapports longs"""
    if not documents:
        return "Aucun document de référence trouvé."
    
    context = "## CORPUS DOCUMENTAIRE POUR ANALYSE APPROFONDIE\n\n"
    for i, doc in enumerate(documents[:8], 1):  # Plus de documents
        doc_text = doc.get('text', '')[:800]  # Plus de texte par doc
        score = doc.get('score', 0)
        doc_id = doc.get('doc_id', 'N/A')
        context += f"**[Document {i} - ID:{doc_id}]** (Pertinence: {score:.3f}):\n{doc_text}...\n\n"
    
    return context

def create_extended_business_prompt(business_type: str, analysis_type: str, query: str, context: str) -> str:
    """Crée prompts pour rapports très longs style cabinet conseil"""
    
    # Templates optimisés pour rapports longs
    extended_templates = {
        "finance_banque": {
            "synthese_executive": f"""MISSION: {query}

DOCUMENTS DE RÉFÉRENCE:
{context}

STRUCTURE RAPPORT BANCAIRE (15+ pages):

## 🎯 SYNTHÈSE EXÉCUTIVE (3 pages)
- Enjeux transformation sectorielle avec données [Réf. X]
- 3 recommandations prioritaires avec ROI
- Timeline et investissements requis

## 📊 ANALYSE SECTORIELLE (5 pages)  
- Dimensionnement marché et croissance [Réf. X]
- Segmentation clientèle détaillée [Réf. X]
- Performance concurrentielle [Réf. X]
- Innovations technologiques [Réf. X]

## ⚔️ POSITIONNEMENT CONCURRENTIEL (4 pages)
- Leaders traditionnels vs challengers [Réf. X]
- Forces/faiblesses comparatives [Réf. X]
- Stratégies différenciation [Réf. X]

## 💡 RECOMMANDATIONS STRATÉGIQUES (4 pages)
- Plan transformation 18 mois [Réf. X]
- Business case détaillé [Réf. X]
- Gestion risques [Réf. X]

## 📈 PROJECTIONS ET SOURCES (2 pages)
- Scenarios 2025-2030 [Réf. X]
- Sources documentaires [Réf. X]

IMPORTANT: Génère minimum 8000 mots. Utilise [Réf. X] pour chaque donnée factuelle.""",
[Analyse complète des forces de transformation du secteur bancaire avec données quantifiées]
- Révolution digitale et impact sur les modèles traditionnels [Réf. X]
- Pression réglementaire (Bâle III/IV, DSP2, RGPD) et coûts de conformité [Réf. X]  
- Émergence FinTech/NéoBanques et disruption concurrentielle [Réf. X]
- Évolution attentes clients et nouveaux parcours digitaux [Réf. X]

### Recommandations Stratégiques Prioritaires
[3 recommandations majeures avec business case détaillé]
1. **Transformation digitale accélérée**: Migration cloud-native, APIs ouvertes, IA généralisée
2. **Recentrage métier**: Spécialisation sectorielle vs approche généraliste
3. **Écosystème ouvert**: Partnerships FinTech, Banking-as-a-Service, marketplace

### Impact Financier et Timeline
[Estimation ROI, investissements requis, gains de productivité sur 3-5 ans]

## 📊 ANALYSE SECTORIELLE APPROFONDIE (4-5 pages)

### 1. Dimensionnement et Structure du Marché
#### Taille et Croissance
[Évolution PNB sectoriel, total actifs, dépôts clients 2019-2024 avec projections 2025-2030]
- Banques de détail: €XXX Md PNB, croissance XX% [Réf. X]
- Banque corporate: €XXX Md, marge NII XX% [Réf. X]
- Banque privée: €XXX Md AuM, commission XX% [Réf. X]

#### Segmentation Clientèle Détaillée  
[Analyse comportementale par segment avec data granulaire]
- **Particuliers** (XX millions clients): Usage digital XX%, satisfaction XX% [Réf. X]
- **PME/ETI** (XX milliers clients): Besoins financement, cash management [Réf. X]
- **Grandes Entreprises**: Trade finance, hedging, M&A advisory [Réf. X]
- **Institutionnels**: Gestion actifs, custody, prime brokerage [Réf. X]

### 2. Dynamiques Concurrentielles et Parts de Marché
#### Leaders Traditionnels - Analyse Détaillée
**BNP Paribas Groupe**
- Parts de marché: Détail XX%, Corporate XX%, International XX% [Réf. X]
- Performance: ROE XX%, Cost/Income XX%, CET1 XX% [Réf. X]
- Stratégie: Digitalisation, expansion Europe, sustainability [Réf. X]
- Forces: Réseau international, innovation lab, banque d'investissement
- Faiblesses: Coûts legacy IT, perception client retail, exposition risques émergents

**Société Générale**
- Positionnement: Banque universelle, focus marchés de capitaux [Réf. X]
- Transformation: Plan simplification, cessions non-core, digital-first [Réf. X]
- Innovation: IA trading, blockchain trade finance, open banking APIs [Réf. X]

**Crédit Agricole**
- Modèle mutualiste: Gouvernance, collecte épargne, proximité locale [Réf. X]
- Diversification: Assurance (XX% revenus), asset management, crédit conso [Réf. X]
- International: Présence Europe du Sud, stratégie selective [Réf. X]

#### Challengers Digitaux - Disruption Analysis
[Analyse approfondie Boursorama, ING Direct, Hello Bank, Fortuneo]
- Modèles économiques: Pure players vs filiales groupes [Réf. X]
- Stratégies acquisition: CAC, LTV, viral growth [Réf. X]
- Innovation produit: Agrégation, PFM, robo-advisory [Réf. X]

#### Écosystème FinTech - Cartographie Complète
[Mapping détaillé par verticale: payments, lending, wealth, insurtech]
- **Payments**: Lydia, PayFit, Klarna - volumes, croissance, monétisation [Réf. X]
- **Lending**: October, Credit.fr, Younited - scoring, partnership banks [Réf. X]  
- **Wealth**: Yomoni, Nalo, WealthForge - AuM, performance, pricing [Réf. X]

### 3. Analyse Technologique et Innovation
#### Stack Technologique Moderne
[Architecture cloud-native, microservices, APIs, data mesh]
- Migration cloud: Coûts vs benefits, timelines, risks [Réf. X]
- Open Banking: Implémentation PSD2, revenue streams, partnerships [Réf. X]
- Intelligence Artificielle: Use cases, ROI, deployment challenges [Réf. X]

#### Cybersécurité et Résilience
[Investissements cyber, threat landscape, regulatory requirements]
- Budget cyber: XX% IT spend, SOC capabilities, incident response [Réf. X]
- Fraude: Taux de fraude XX%, ML detection, customer friction [Réf. X]
- Résilience opérationnelle: BCP, disaster recovery, third-party risk [Réf. X]

## ⚔️ ANALYSE CONCURRENTIELLE STRATÉGIQUE (3-4 pages)

### 1. Benchmark Performance Financière
[Analyse comparative ROE, Cost/Income, NIM, provisions sur 5 ans]
#### Rentabilité et Efficacité
- ROE moyen secteur: XX% vs best-in-class XX% [Réf. X]
- Cost/Income: Range XX%-XX%, benchmarks européens [Réf. X]
- Productivité: PNB/ETP, Coût du risque, NIM evolution [Réf. X]

#### Solidité Financière
- Ratios prudentiels: CET1, Leverage, NSFR par établissement [Réf. X]
- Qualité actifs: NPL ratios, provisions coverage, secteurs exposés [Réf. X]
- Funding mix: Dépôts/Total bilan, wholesale funding, diversification [Réf. X]

### 2. Positionnement Stratégique et Différenciation
#### Stratégies Business Model
[Analyse détaillée des choix stratégiques par acteur]
- **Spécialisation vs Universalité**: Avantages/inconvénients par modèle [Réf. X]
- **Géographie**: Domestic champions vs international players [Réf. X]
- **Canaux**: Omnicanal vs digital-first vs relationship-based [Réf. X]

#### Innovation et Transformation
[Capacité innovation, investissements R&D, partnerships]
- Labs innovation: Budgets, projets, time-to-market [Réf. X]
- Partnerships FinTech: Modèles (investment, acquisition, partnership) [Réf. X]
- Culture transformation: Change management, talent acquisition [Réf. X]

### 3. Forces et Faiblesses Comparatives
#### Avantages Concurrentiels Durables
[Analyse des sources de différenciation sustainable]
- **Données et Analytics**: Customer 360, predictive analytics, personalization [Réf. X]
- **Écosystème**: Marketplace, open banking, embedded finance [Réf. X]
- **Excellence Opérationnelle**: STP rates, digital adoption, NPS [Réf. X]

#### Vulnérabilités et Gaps
[Points faibles exploitables par la concurrence]
- **Legacy IT**: Debt technique, modernisation costs, time-to-market [Réf. X]
- **Talent**: Skills gap, attraction tech profiles, reskilling [Réf. X]
- **Réglementaire**: Compliance costs, change readiness, sanctions risk [Réf. X]

## 💡 OPPORTUNITÉS STRATÉGIQUES ET RECOMMANDATIONS (4-5 pages)

### 1. Opportunités de Croissance Identifiées
#### Nouveaux Segments et Géographies
[Analyse opportunités croissance organique et externe]
- **Green Finance**: Marché €XXX Md, croissance XX% CAGR, regulatory drivers [Réf. X]
- **PME Digitales**: Underbanked, besoins spécifiques, solutions packagées [Réf. X]
- **Seniors/Patrimoine**: Vieillissement population, transfert intergénérationnel [Réf. X]

#### Innovation Produits et Services
[Nouveaux revenue streams et business models]
- **Banking-as-a-Service**: Plateforme, APIs, revenue sharing [Réf. X]
- **Embedded Finance**: Marketplace, e-commerce, vertical SaaS [Réf. X]
- **Crypto-Assets**: Custody, trading, DeFi gateway [Réf. X]

### 2. Partenariats et Écosystème
#### Stratégies d'Alliance
[Framework partenariats FinTech, BigTech, traditional players]
- **FinTech Partnerships**: Due diligence, integration, governance [Réf. X]
- **BigTech Collaboration**: Data sharing, infrastructure, co-innovation [Réf. X]
- **Cross-Industry**: Telco, retail, automotive, healthcare [Réf. X]

#### Acquisitions et Consolidation
[M&A opportunities, valuation multiples, integration challenges]
- **Targets FinTech**: Screening criteria, synergies, cultural fit [Réf. X]
- **Horizontal Consolidation**: Scale benefits, regulatory approval, cost synergies [Réf. X]
- **Vertical Integration**: Value chain control, customer ownership [Réf. X]

### 3. Recommandations Opérationnelles Détaillées
#### Plan Transformation 18 Mois (Actions Immédiates)
**Phase 1: Stabilisation et Quick Wins (0-6 mois)**
1. **Migration Cloud Prioritaire**
   - Workloads non-critiques: Email, collaboration, analytics [ROI: XX%]
   - Setup hybrid architecture, security framework
   - Training équipes, governance cloud, cost optimization

2. **Optimisation Coûts Opérationnels**  
   - Rationalisation réseau agences: -XX% footprint, +XX% productivité
   - Automatisation back-office: RPA sur XX processus, -XX% FTEs
   - Renégociation contrats fournisseurs: -XX% costs IT

3. **Expérience Client Digital**
   - Refonte mobile app: UX/UI, temps chargement -XX%, NPS +XX points
   - Chatbot IA: XX% résolution auto, -XX% call center volume
   - Onboarding digital: KYC automatisé, time-to-activate -XX%

**Phase 2: Innovation et Différenciation (6-12 mois)**
1. **Intelligence Artificielle Opérationnelle**
   - Scoring crédit ML: Amélioration XX% accuracy, -XX% false positives
   - Détection fraude temps réel: -XX% fraude, +XX% genuine transactions
   - Personnalisation offers: Conversion +XX%, revenue per customer +XX%

2. **Open Banking Monétisation**
   - APIs externes: XX nouveaux partenaires, €XX revenue sharing
   - Agrégation comptes: XX% customer adoption, engagement +XX%
   - Marketplace services: XX% take rate, €XX nouvelle revenues

3. **Excellence Opérationnelle**
   - STP rate: Amélioration à XX% (vs XX% current), cost reduction -XX%
   - Data governance: Single customer view, GDPR compliance, analytics
   - Cyber resilience: Zero trust architecture, SOC 24/7, pen testing

**Phase 3: Transformation Stratégique (12-18 mois)**
1. **Nouveau Business Model**
   - Platform strategy: Banking-as-a-Service, developer portal
   - Embedded finance: XX partnerships, €XX revenue contribution
   - Innovation lab: XX POCs, X scaling, external ventures

2. **Écosystème et Partnerships**
   - FinTech acquisitions: X targets evaluated, X deals closed
   - Strategic alliances: XX MoUs signed, joint go-to-market
   - International expansion: XX markets assessed, X entry strategies

#### ROI et Business Case
[Analyse financière détaillée des investissements]
- **Investissement Total**: €XXX millions sur 18 mois
- **Gains Productivity**: €XXX millions/an (cost reduction)
- **Revenue Growth**: €XXX millions/an (nouveau business)
- **ROI Net**: XX% après 3 ans, payback XX mois

### 4. Gestion des Risques et Mitigation
#### Risques Transformation
[Risk assessment et plans de mitigation]
- **Risque Technologique**: Legacy integration, cyber, vendor lock-in [Réf. X]
- **Risque Opérationnel**: Change management, skills gap, execution [Réf. X]
- **Risque Concurrentiel**: First-mover advantage, time-to-market [Réf. X]
- **Risque Réglementaire**: Compliance new regulations, data privacy [Réf. X]

#### Plans de Contingence
[Scenarios planning et response strategies]
- **Scénario Pessimiste**: Recession, NIM compression, credit losses
- **Scénario Optimiste**: Accelerated digitalization, market consolidation  
- **Scénario Disruption**: BigTech entry, crypto mainstream adoption

## 📈 PROJECTIONS ET SCENARIOS (2-3 pages)

### 1. Modélisation Financière 2025-2030
#### Scenarios Macro-économiques
[Impact des variables macro sur la performance bancaire]
- **Scénario Central**: Croissance PIB XX%, inflation XX%, taux XX% [Réf. X]
- **Scénario Récessif**: Stress test, provisions, capital adequacy [Réf. X]
- **Scénario Inflationniste**: NIM expansion, cost inflation, real estate [Réf. X]

#### Projections Secteur Bancaire
[Evolution PNB, ROE, market share par segment 2025-2030]
- **Retail Banking**: PNB growth XX% CAGR, digital adoption XX% [Réf. X]
- **Corporate Banking**: Fee income growth, lending margins, ESG [Réf. X]
- **Investment Banking**: Volatility, regulation impact, consolidation [Réf. X]

### 2. Disruption Scenarios et Impact
#### Entrée BigTech Accelerée
[Analyse impact Google, Apple, Amazon entry in banking]
- **Timeline**: Licensing, product launch, market penetration [Réf. X]
- **Impact**: Customer acquisition, pricing pressure, innovation pace [Réf. X]
- **Response Strategy**: Differentiation, partnership, niche focus [Réf. X]

#### Adoption Crypto Mainstream
[Impact CBDCs, stablecoins, DeFi on traditional banking]
- **Payment Infrastructure**: Instant settlement, cost reduction [Réf. X]
- **Lending Market**: Decentralized finance, smart contracts [Réf. X]
- **Monetary Policy**: Central bank digital currencies, transmission [Réf. X]

### 3. Monitoring et KPIs Success
#### Dashboard Performance
[Métriques de suivi transformation et performance]
- **Financial KPIs**: ROE, Cost/Income, NIM, provisions, capital ratios
- **Operational KPIs**: Digital adoption, STP rates, time-to-market, NPS
- **Strategic KPIs**: Market share, new business revenue, innovation pipeline

#### Governance et Reporting
[Organisation du pilotage transformation]
- **Comité Transformation**: Sponsor C-level, steering committee, PMO
- **Reporting Rythm**: Monthly dashboards, quarterly business reviews
- **Risk Management**: Risk appetite, early warning indicators, escalation

## 📚 APPENDICES ET SOURCES (1-2 pages)

### Méthodologie d'Analyse
[Framework d'analyse utilisé, sources de données, limitations]
- **Sources Primaires**: Documents fournis, scoring de pertinence [Réf. 1-X]
- **Sources Secondaires**: Market research, regulatory reports, benchmarks
- **Limites**: Data availability, forecast uncertainty, timing assumptions

### Références Documentaires Détaillées
[Liste exhaustive des documents analysés avec scoring]
{format_sources_detailed(documents)}

### Glossaire et Acronymes
[Définitions des termes techniques et acronymes utilisés]

---

**IMPORTANTE**: Utilise EXCLUSIVEMENT les données des documents fournis [Réf. X] pour toutes affirmations chiffrées.
Ce rapport doit faire minimum 15 pages avec un niveau de détail et d'analyse comparable aux deliverables McKinsey/BCG.
Structure rigoureuse, analyses quantifiées, recommandations actionnables, timeline précise.
            """,
            
            "analyse_concurrentielle": f"""Tu es un Partner senior BCG spécialisé en intelligence concurrentielle et stratégie sectorielle.

CONTEXTE DOCUMENTAIRE COMPLET:
{context}

MISSION: {query}

GÉNÈRE UNE ANALYSE CONCURRENTIELLE APPROFONDIE DE 20-25 PAGES:

# ANALYSE CONCURRENTIELLE STRATÉGIQUE - SECTEUR BANCAIRE

## 🎯 EXECUTIVE SUMMARY (2 pages)
### Enjeux Concurrentiels Majeurs
[Synthèse des forces reshaping le paysage concurrentiel]

### Cartographie Competitive Positioning
[Matrice positionnement: innovation vs scale, premium vs volume]

### Recommandations Strategic Moves
[3 recommandations majeures pour competitive advantage]

## 🗺️ CARTOGRAPHIE CONCURRENTIELLE DÉTAILLÉE (6-8 pages)

### 1. Segmentation du Marché et Acteurs
#### Retail Banking - Analyse Granulaire
**Leaders Établis**
- **BNP Paribas**: Part de marché XX%, XXX agences, XX millions clients [Réf. X]
  * Performance: PNB €XX Md, ROE XX%, Cost/Income XX% [Réf. X]
  * Stratégie: Digitalisation réseau, international expansion, sustainability [Réf. X]
  * Avantages: Scale, brand, international footprint, innovation capacity
  * Faiblesses: Legacy costs, bureaucracy, customer satisfaction gaps
  * Prochains Moves: Cloud migration, AI deployment, green finance leader

- **Société Générale**: Repositionnement banque universelle [Réf. X]
  * Transformation: Simplification organisation, digital-first, market focus [Réf. X]
  * Innovation: Trading algorithms, blockchain, robo-advisory [Réf. X]
  * Challenges: Profitabilité retail, risk appetite, execution speed

- **Crédit Agricole**: Modèle mutualiste, proximité territoriale [Réf. X]
  * Differentiation: Gouvernance participative, épargne solidaire, agriculture [Réf. X]
  * Diversification: CA Assurances, Indosuez, Crédit Conso [Réf. X]
  * Opportunities: ESG leadership, rural digital, silver economy

**Challengers Digitaux**
- **Boursorama**: Pure player digital, XX millions clients [Réf. X]
  * Business Model: Low-cost, digital-only, trading focus [Réf. X]
  * Performance: Acquisition cost €XX, LTV €XX, profitabilité par cohorte [Réf. X]
  * Stratégie: Mass affluent, investment solutions, international expansion

- **ING Direct France**: Épargne et crédit, simplicité [Réf. X]
  * Positioning: Direct bank pioneer, rate leadership, customer experience [Réf. X]
  * Innovation: Mobile-first, AI chatbot, sustainable finance [Réf. X]

#### Corporate Banking - Intelligence Détaillée
**Champions Nationaux**
- **BNP Paribas CIB**: Global reach, investment banking, trade finance [Réf. X]
- **SocGen Corporate**: Capital markets, structured finance, commodities [Réf. X]
- **CA CIB**: Syndication, leveraged finance, coverage sectorielle [Réf. X]

**Spécialistes et Niche Players**
- **Crédit Mutuel Arkéa**: PME/ETI focus, innovation bancaire [Réf. X]
- **Banque Palatine**: Mid-market, family office, real estate [Réf. X]
- **International Players**: HSBC, Deutsche Bank, JPMorgan positioning [Réf. X]

#### Wealth Management - Bataille Segments
**Private Banking Traditional**
- **BNP Paribas Wealth**: €XXX Md AuM, international platform [Réf. X]
- **Société Générale Private**: Focus entrepreneurs, family governance [Réf. X]
- **Crédit Agricole Indosuez**: Heritage familial, art & passion [Réf. X]

**Robo-Advisors et Digital Wealth**
- **Yomoni**: €XXX millions AuM, ETF allocation, digital onboarding [Réf. X]
- **Nalo**: Allocation dynamique, ISR focus, mobile experience [Réf. X]
- **Traditional Response**: Digital wealth platforms, hybrid advisory [Réf. X]

### 2. FinTech Ecosystem - Disruption Analysis
#### Payment et Transaction
**Leaders Établis**
- **Lydia**: XX millions users, P2P payments, merchant solutions [Réf. X]
  * Monetisation: Interchange, premium subscriptions, business accounts
  * Partnership Strategy: Open banking, embedded finance, neo-banks
  * Competitive Moat: Network effects, brand, regulatory compliance

**Emerging Players**
- **Sumup**: Merchant acquiring, POS solutions, SME banking [Réf. X]
- **PayFit**: Payroll fintech, embedded banking, SME focus [Réf. X]
- **Klarna**: BNPL leader, shopping integration, merchant network [Réf. X]

#### Lending et Credit
**Alternative Lending**
- **October**: SME lending, marketplace model, institutional funding [Réf. X]
  * Performance: €XXX millions originated, default rate XX%, ROI investors [Réf. X]
  * Technology: Scoring algorithms, automated underwriting, portfolio management
  * Competitive Advantage: Speed, transparency, digital experience

- **Younited Credit**: Consumer lending, instant decision, mobile-first [Réf. X]
- **Credit.fr**: Real estate crowdfunding, SCPI digital, patrimoine [Réf. X]

#### InsurTech Integration
**Embedded Insurance**
- **Luko**: Home insurance digital, IoT integration, prevention [Réf. X]
- **Alan**: Health insurance, employee benefits, HR integration [Réf. X]
- **Bancassurance Response**: Digital transformation, partnerships, innovation [Réf. X]

### 3. Analyse Forces Concurrentielles Porter
#### Menace Nouveaux Entrants
**BigTech Threat Assessment**
- **Google Pay**: Payment infrastructure, data advantage, ecosystem [Réf. X]
- **Apple**: Wallet, card, BNPL potential, premium positioning [Réf. X]
- **Amazon**: AWS financial services, lending, payment processing [Réf. X]

**Barriers to Entry Analysis**
- **Regulatory**: Banking license, capital requirements, compliance costs [Réf. X]
- **Technology**: Legacy integration, security, scale economics [Réf. X]
- **Customer**: Switching costs, trust, relationship dependency [Réf. X]

#### Pouvoir Négociation Fournisseurs
**Technology Vendors**
- **Core Banking**: Temenos, Finastra, vendor lock-in risks [Réf. X]
- **Cloud Providers**: AWS, Microsoft, Google bargaining power [Réf. X]
- **Fintech Partners**: Revenue sharing, dependency, competitive risks [Réf. X]

#### Pouvoir Négociation Clients
**Segment Analysis**
- **Retail**: Price sensitivity, switching propensity, digital expectations [Réf. X]
- **SME**: Relationship importance, service quality, financing needs [Réf. X]
- **Corporate**: Negotiation power, global reach, sophisticated requirements [Réf. X]

## ⚔️ ANALYSE STRATEGIQUE PAR ACTEUR (4-5 pages)

### 1. BNP Paribas Groupe - Strategic Deep Dive
#### Positionnement Concurrentiel
- **Market Leadership**: Retail #1 France, Corporate top 3, International presence [Réf. X]
- **Diversification**: Geography (XX countries), Business lines, Client segments [Réf. X]
- **Innovation**: Investment €XX millions/year, partnerships, labs [Réf. X]

#### Forces Stratégiques
- **Scale Advantage**: Funding cost, regulatory capital, investment capacity
- **International Network**: Cross-border trade, global corporates, wealth management
- **Technology Platform**: Core banking modern, API capabilities, data analytics
- **Brand Strength**: Trust, expertise, premium positioning

#### Vulnérabilités Critiques
- **Complexity**: Matrix organization, decision speed, agility constraints
- **Cost Structure**: Branch network, legacy IT, regulatory overhead
- **Customer Experience**: Digital gaps, satisfaction scores, millennial appeal
- **Regulatory Risk**: International exposure, AML, sanctions compliance

#### Stratégie Future et Contre-Attaques
- **Digital Transformation**: €XX Md investment, cloud migration, AI deployment
- **Ecosystem Strategy**: Open banking, partnerships, platform business
- **Sustainability**: Green finance leader, ESG integration, transition risk
- **Geographic Focus**: Europe consolidation, Asia growth, US selective

### 2. Société Générale - Repositioning Analysis
#### Transformation Strategy
- **Simplification**: Business reduction, cost cutting, focus core strengths [Réf. X]
- **Digital-First**: Mobile banking, trading platforms, robo-advisory [Réf. X]
- **Market Focus**: Investment banking, transaction banking, specialized finance [Réf. X]

#### Competitive Response Scenarios
- **Defensive**: Cost reduction, capital optimization, risk management
- **Offensive**: Innovation acceleration, M&A opportunities, market share gain
- **Partnership**: Fintech collaboration, platform strategy, ecosystem building

### 3. Emerging Competitors - Threat Assessment
#### Neo-Banks International
- **Revolut**: International expansion, super-app strategy, crypto integration [Réf. X]
- **N26**: European consolidation, premium segments, business banking [Réf. X]
- **Monzo/Starling**: UK success, expansion potential, innovation pace [Réf. X]

#### Response Strategies Required
- **Speed to Market**: Faster innovation cycles, agile development, fail-fast
- **Customer Experience**: UX/UI excellence, personalization, omnichannel
- **Pricing Competition**: Value proposition, fee structures, transparency

## 💡 STRATEGIC RECOMMENDATIONS (3-4 pages)

### 1. Competitive Positioning Strategies
#### Differentiation vs Cost Leadership
**Premium Positioning Strategy**
- **Target**: Mass affluent, HNW, sophisticated corporates
- **Value Prop**: Expertise, relationship, bespoke solutions, global reach
- **Execution**: Advisor training, technology platform, service quality
- **Risks**: Market size limitation, price sensitivity, digital disruption

**Volume Leadership Strategy**  
- **Target**: Mass market, digital natives, SME standardized needs
- **Value Prop**: Low cost, convenience, speed, transparency
- **Execution**: Digital channels, automation, self-service, API integration
- **Risks**: Margin pressure, commoditization, scale requirements

#### Hybrid Strategy - Best of Both Worlds
- **Segmented Approach**: Premium relationship + digital efficiency
- **Channel Strategy**: High-touch + self-service + hybrid models
- **Technology**: AI personalization, predictive analytics, automated advice
- **Organization**: Specialized teams, digital skills, cultural change

### 2. Innovation et R&D Strategy
#### Innovation Lab Strategy
**Internal Innovation**
- **Budget**: €XX millions/year, XX% revenue reinvestment [Réf. X]
- **Focus Areas**: AI/ML, blockchain, quantum computing, cybersecurity
- **Metrics**: Patents filed, POCs launched, time-to-market, ROI

**External Innovation**
- **Venture Capital**: €XX millions fund, fintech investments, strategic stakes
- **Partnerships**: Accelerators, universities, research institutes, startups
- **Acquisition**: Target screening, integration playbook, cultural fit

#### Technology Transformation Roadmap
**Phase 1: Foundation (12 months)**
- Cloud migration: XX% workloads, hybrid architecture, security framework
- API Platform: Open banking compliance, partner integration, developer portal
- Data Platform: Single customer view, analytics, ML infrastructure

**Phase 2: Acceleration (24 months)**
- AI Deployment: Customer service, risk management, personalization, trading
- Blockchain: Trade finance, payments, smart contracts, tokenization
- Cyber Enhancement: Zero trust, threat intelligence, incident response

### 3. Market Entry et Expansion
#### Geographic Expansion
**European Consolidation**
- **Target Markets**: Germany, Italy, Spain fintech acquisition opportunities
- **Entry Mode**: Partnership → Acquisition → Organic growth
- **Timeline**: Market analysis 6 months, entry 12-18 months, scale 3-5 years

**Digital-First International**
- **Target**: Digital banking license, neobank model, global platform
- **Segments**: Expats, global nomads, SME international, wealth management
- **Technology**: Cloud-native, multi-currency, regulatory compliance automation

#### Vertical Integration Opportunities
**Fintech Value Chain**
- **Payment Infrastructure**: Acquiring, processing, settlement, FX
- **Lending Origination**: Scoring, underwriting, servicing, collections
- **Wealth Management**: Advisory, execution, custody, reporting

**Adjacent Industries**
- **Real Estate**: Mortgage, investment, property management, tokenization
- **Healthcare**: Insurance, financing, digital health, employee benefits
- **Automotive**: Leasing, insurance, mobility-as-a-service, connected car

## 📊 COMPETITIVE INTELLIGENCE FRAMEWORK (2-3 pages)

### 1. Monitoring et Early Warning
#### Competitive Intelligence System
**Data Sources**
- **Public**: Financial reports, regulatory filings, press releases, conferences
- **Digital**: Website changes, app updates, social media, job postings
- **Industry**: Consultant reports, analyst coverage, industry events, benchmarks

**Analysis Framework**
- **Strategic Moves**: M&A, partnerships, product launches, market entry/exit
- **Performance Metrics**: Financial KPIs, operational metrics, customer satisfaction
- **Innovation Pipeline**: Patent filings, technology investments, talent acquisition

#### Early Warning Indicators
**Competitive Threats**
- **New Entrant Signals**: Licensing applications, talent recruitment, funding rounds
- **Expansion Plans**: Geographic, product, segment expansion announcements
- **Technology Breakthroughs**: Pilot launches, partnership announcements, research papers

**Market Shifts**
- **Regulatory Changes**: New regulations, enforcement actions, policy consultations
- **Customer Behavior**: Survey data, usage patterns, satisfaction scores, churn rates
- **Technology Adoption**: Emerging technologies, adoption curves, platform shifts

### 2. Response Strategy Framework
#### Competitive Response Playbook
**Response Speed**
- **Immediate (0-3 months)**: Pricing, marketing, sales tactics, partnerships
- **Medium-term (3-12 months)**: Product features, channel expansion, technology deployment
- **Long-term (12+ months)**: Strategic initiatives, M&A, business model evolution

**Response Intensity**
- **Match**: Follow competitor moves, maintain parity, protect market share
- **Leapfrog**: Accelerate innovation, superior offering, capture first-mover advantage
- **Ignore**: Focus own strategy, niche positioning, different battleground

#### Scenario Planning
**Competitive Scenarios**
- **Scenario 1**: Aggressive pricing war, margin compression, consolidation
- **Scenario 2**: Innovation arms race, customer experience competition, technology focus
- **Scenario 3**: Regulatory disruption, open banking acceleration, platform economics

**Strategic Options**
- **Defend**: Cost reduction, efficiency, customer retention, niche focus
- **Attack**: Market share gain, competitive pricing, innovation acceleration
- **Collaborate**: Partnerships, ecosystem, industry standards, regulatory advocacy

## 📈 PERFORMANCE BENCHMARKING (1-2 pages)

### 1. Financial Performance Analysis
#### Key Performance Indicators
[Tableau comparatif détaillé sur 5 ans avec projections]

| Métrique | BNP Paribas | SocGen | CA | Boursorama | Industry Avg |
|----------|-------------|---------|----|-----------:|--------------|
| ROE (%) | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] |
| Cost/Income (%) | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] |
| NIM (%) | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] |
| CET1 (%) | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] | [Réf. X] |

#### Operational Excellence Metrics
- **Digital Adoption**: Mobile MAU, digital transactions %, online onboarding rate
- **Customer Experience**: NPS, satisfaction scores, complaint resolution time
- **Innovation**: R&D spend, patents, product launch frequency, time-to-market

### 2. Strategic Positioning Matrix
#### Competitive Position Mapping
[Matrice positionnement: Market Share vs Growth Rate vs Innovation Index]

#### Competitive Advantage Assessment
[Analyse forces/faiblesses relatives par dimension concurrentielle]

## 📚 SOURCES ET MÉTHODOLOGIE

### Documents Analysés
{format_detailed_sources(documents)}

### Framework d'Analyse
- **Porter 5 Forces**: Industry structure, competitive dynamics assessment
- **Strategic Groups**: Mapping competitors by strategy similarity, performance
- **Blue Ocean**: Value innovation opportunities, uncontested market spaces
- **Game Theory**: Competitive moves, counter-moves, Nash equilibrium analysis

---

**CRITIQUE**: Génère minimum 20 pages avec analyses quantifiées, benchmarks détaillés, recommandations actionnables.
Utilise EXCLUSIVEMENT les données documentaires [Réf. X] pour toute affirmation factuelle.
Niveau de détail et sophistication analytique équivalent aux livrables BCG/McKinsey.
            """
        },
        
        # Templates similaires étendus pour tech_digital et retail_commerce...
    }
    
    # Sélection du template approprié
    if business_type not in extended_templates:
        business_type = "finance_banque"
    
    if analysis_type not in extended_templates[business_type]:
        analysis_type = "synthese_executive"
    
    return extended_templates[business_type][analysis_type]

def call_openai_extended(prompt: str, business_type: str) -> str:
    """Appel OpenAI pour rapports très longs - Version sécurisée"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "":
            return "⚠️ Configuration OpenAI requise. Veuillez configurer OPENAI_API_KEY."
        
        # Import OpenAI avec gestion d'erreur
        try:
            import openai
        except ImportError as e:
            logger.error(f"OpenAI import error: {e}")
            return f"❌ Erreur: Module OpenAI non disponible - {str(e)}"
        
        # Système prompts optimisés
        system_prompts = {
            "finance_banque": """Tu es un consultant senior McKinsey spécialisé en stratégie bancaire.
                              Génère un rapport structuré de 15+ pages avec analyses quantifiées et recommandations actionnables.
                              Utilise EXCLUSIVEMENT les données des documents fournis [Réf. X].""",
            
            "tech_digital": """Tu es un consultant BCG expert en transformation digitale.
                             Génère un rapport technique détaillé avec business case et ROI.
                             Base tes analyses sur les documents fournis [Réf. X].""",
            
            "retail_commerce": """Tu es un consultant Bain expert en retail et commerce.
                                Génère une analyse complète avec insights consommateurs.
                                Réfère aux documents fournis [Réf. X]."""
        }
        
        system_prompt = system_prompts.get(business_type, system_prompts["finance_banque"])
        
        # Configuration OpenAI robuste
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Limiter la taille du prompt pour éviter les erreurs
            max_prompt_length = 12000
            if len(prompt) > max_prompt_length:
                logger.warning(f"Prompt trop long ({len(prompt)} chars), truncation à {max_prompt_length}")
                prompt = prompt[:max_prompt_length] + "\n\n[...RAPPORT TRONQUÉ POUR LIMITES TECHNIQUES...]"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=8000  # Limite plus réaliste
            )
            
            return response.choices[0].message.content
            
        except openai.OpenAIError as oe:
            logger.error(f"OpenAI API error: {oe}")
            return f"❌ Erreur OpenAI API: {str(oe)[:200]}"
        except Exception as client_error:
            logger.error(f"OpenAI client error: {client_error}")
            return f"❌ Erreur client OpenAI: {str(client_error)[:200]}"
        
    except Exception as e:
        logger.error(f"Critical OpenAI error: {e}")
        return f"❌ Erreur critique: {str(e)[:200]}"

def format_detailed_sources(documents: List[Dict]) -> str:
    """Formate les sources détaillées pour appendix"""
    if not documents:
        return "Aucune source documentaire analysée."
    
    sources = ""
    for i, doc in enumerate(documents[:8], 1):
        doc_id = doc.get('doc_id', 'N/A')
        score = doc.get('score', 0)
        text_preview = doc.get('text', '')[:200]
        
        sources += f"""
**[Réf. {i}] Document ID: {doc_id}**
- Score de pertinence: {score:.3f}
- Extrait représentatif: "{text_preview}..."
- Contribution à l'analyse: Source primaire pour métriques sectorielles
"""
    
    return sources

async def generate_extended_analysis(business_type: str, analysis_type: str, query: str, title: str = None) -> AnalysisResponse:
    """Génère rapports longs style cabinet conseil"""
    try:
        logger.info(f"Génération rapport long {business_type}/{analysis_type}")
        
        # 1. Recherche vectorielle étendue
        documents = search_documents(query, top_k=12)
        
        # 2. Contexte étendu pour rapports longs
        context = format_context_extended(documents)
        
        # 3. Prompt pour rapport très long
        prompt = create_extended_business_prompt(business_type, analysis_type, query, context)
        
        # 4. Génération rapport long
        content = call_openai_extended(prompt, business_type)
        
        # 5. Ajout sources détaillées
        if documents and content:
            detailed_sources = format_detailed_sources(documents)
            content += f"\n\n{detailed_sources}"
        
        return AnalysisResponse(
            analysis_type=analysis_type,
            business_type=business_type,
            title=title or f"Rapport {get_business_type_display_name(business_type)} - {analysis_type.replace('_', ' ').title()}",
            content=content,
            sources=[{
                "doc_id": d.get("doc_id"),
                "score": d.get("score"),
                "text": d.get("text", "")[:300]
            } for d in documents],
            metadata={
                "query": query,
                "business_type": business_type,
                "documents_found": len(documents),
                "analysis_length": "extended_report",
                "model": "gpt-4o-mini",
                "max_tokens": 16000,
                "report_pages": "15-25"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in extended analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints
@app.get("/health")
def health():
    return {"status": "healthy", "service": "enhanced-backend", "features": ["extended_reports", "16k_tokens"]}

@app.post("/extended-analysis", response_model=AnalysisResponse)
async def extended_analysis(request: BusinessAnalysisRequest):
    """Génère rapports longs style cabinet conseil"""
    return await generate_extended_analysis(
        request.business_type,
        request.analysis_type,
        request.query,
        request.title
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
