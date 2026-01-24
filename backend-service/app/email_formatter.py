"""
Email Formatter - Formate les rapports de veille en format email HTML
"""

from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger


def format_watch_email(
    subject: str,
    topic: str,
    articles: List[Dict],
    recipient_name: Optional[str] = None
) -> str:
    """
    Formate un rapport de veille en email HTML responsive
    
    Args:
        subject: Sujet de la veille
        topic: Theme analyse
        articles: Liste des articles avec title, source, date, summary, implications
        recipient_name: Nom du destinataire (optionnel)
    
    Returns:
        HTML formate pour envoi email
    """
    
    greeting = f"Bonjour {recipient_name}," if recipient_name else "Bonjour,"
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    # Articles HTML
    articles_html = ""
    for i, article in enumerate(articles, 1):
        articles_html += f"""
        <tr>
            <td style="padding: 0 0 24px 0;">
                <table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <!-- Article Header -->
                    <tr>
                        <td style="background: #f8fafc; padding: 16px 20px; border-bottom: 1px solid #e2e8f0;">
                            <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #1e293b; font-weight: 600;">
                                {article.get('title', 'Sans titre')}
                            </h3>
                            <p style="margin: 0; font-size: 12px; color: #64748b;">
                                {article.get('source', 'Source inconnue')} | {article.get('date', current_date)}
                            </p>
                        </td>
                    </tr>
                    <!-- Article Summary -->
                    <tr>
                        <td style="padding: 20px;">
                            <p style="margin: 0; font-size: 14px; color: #475569; line-height: 1.6;">
                                {article.get('summary', '')}
                            </p>
                        </td>
                    </tr>
                    <!-- Implications -->
                    <tr>
                        <td style="background: #fef3c7; padding: 16px 20px; border-top: 1px solid #fde68a;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="width: 24px; vertical-align: top; padding-right: 12px;">
                                        <div style="width: 24px; height: 24px; background: #f59e0b; border-radius: 6px; text-align: center; line-height: 24px; color: white; font-size: 12px;">
                                            ↗
                                        </div>
                                    </td>
                                    <td>
                                        <p style="margin: 0 0 4px 0; font-size: 12px; color: #92400e; font-weight: 600;">
                                            Implications marche
                                        </p>
                                        <p style="margin: 0; font-size: 13px; color: #a16207; line-height: 1.5;">
                                            {article.get('implications', 'Non specifie')}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """
    
    html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veille Strategique - {subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="100%" style="max-width: 640px;" cellpadding="0" cellspacing="0">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #0891b2 0%, #3b82f6 100%); border-radius: 16px 16px 0 0; padding: 32px;">
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td>
                                        <p style="margin: 0 0 8px 0; font-size: 12px; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px;">
                                            Veille Strategique
                                        </p>
                                        <h1 style="margin: 0 0 16px 0; font-size: 24px; color: white; font-weight: 700;">
                                            {subject}
                                        </h1>
                                        <p style="margin: 0; font-size: 14px; color: rgba(255,255,255,0.9);">
                                            📅 {current_date}
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="background: #f8fafc; padding: 32px; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0;">
                            <!-- Greeting -->
                            <p style="margin: 0 0 24px 0; font-size: 15px; color: #475569; line-height: 1.6;">
                                {greeting}<br><br>
                                Voici les actualites cles de la semaine concernant <strong style="color: #0891b2;">{topic}</strong>. 
                                Cette veille a ete generee automatiquement par Prometheus.
                            </p>
                            
                            <!-- Articles -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                {articles_html}
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #1e293b; border-radius: 0 0 16px 16px; padding: 24px; text-align: center;">
                            <p style="margin: 0 0 8px 0; font-size: 13px; color: #94a3b8;">
                                Ce rapport a ete genere automatiquement par
                            </p>
                            <p style="margin: 0 0 16px 0; font-size: 16px; color: white; font-weight: 600;">
                                Prometheus - Axial Intelligence
                            </p>
                            <p style="margin: 0; font-size: 11px; color: #64748b;">
                                Pour modifier vos preferences, connectez-vous a votre espace personnel.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    
    return html_template


def parse_report_to_articles(report_content: str) -> List[Dict]:
    """
    Parse un rapport de veille en liste d'articles structures
    
    Args:
        report_content: Contenu brut du rapport genere par l'IA
    
    Returns:
        Liste d'articles avec title, source, date, summary, implications
    """
    articles = []
    
    # Simple parsing logic - can be enhanced based on report structure
    # For now, return mock data structure
    # In production, this would parse the actual AI-generated content
    
    logger.info(f"Parsing report content of length: {len(report_content)}")
    
    # Basic section detection
    sections = report_content.split('##')
    
    for section in sections:
        if section.strip():
            lines = section.strip().split('\n')
            if len(lines) > 1:
                title = lines[0].strip().replace('#', '').strip()
                content = '\n'.join(lines[1:]).strip()
                
                if title and content and len(content) > 50:
                    articles.append({
                        'title': title[:200],
                        'source': 'Prometheus Analysis',
                        'date': datetime.now().strftime("%d/%m/%Y"),
                        'summary': content[:500],
                        'implications': 'Analyse en cours...'
                    })
    
    # Limit to 5 articles
    return articles[:5]
