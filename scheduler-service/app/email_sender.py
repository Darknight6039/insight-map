"""
Email sender module for sending watch reports via SMTP
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import List, Optional
from loguru import logger
from datetime import datetime


class EmailSender:
    """Handles sending emails with PDF attachments"""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.company_name = os.getenv("COMPANY_NAME", "Axial Intelligence")

    def is_configured(self) -> bool:
        """Check if SMTP is properly configured"""
        return bool(self.smtp_user and self.smtp_password)

    def send_watch_report(
        self,
        recipients: List[str],
        watch_name: str,
        topic: str,
        report_type: str,
        pdf_content: bytes,
        report_text: Optional[str] = None
    ) -> bool:
        """
        Send a watch report email with PDF attachment
        
        Args:
            recipients: List of email addresses
            watch_name: Name of the watch configuration
            topic: Topic of the analysis
            report_type: Type of report generated
            pdf_content: PDF file content as bytes
            report_text: Optional text summary of the report
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.error("SMTP not configured. Cannot send email.")
            return False

        if not recipients:
            logger.error("No recipients specified for email")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.company_name} <{self.smtp_from}>"
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = f"[Veille Auto] {watch_name} - {topic}"

            # Format report type display name
            report_type_names = {
                "synthese_executive": "Synthèse Exécutive",
                "analyse_concurrentielle": "Analyse Concurrentielle",
                "veille_technologique": "Veille Technologique",
                "analyse_risques": "Analyse des Risques",
                "etude_marche": "Étude de Marché",
                "analyse_approfondie": "Analyse Approfondie"
            }
            report_display = report_type_names.get(report_type, report_type)

            # Build HTML email body
            current_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 24px; }}
                    .content {{ background: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; }}
                    .info-box {{ background: white; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0; border-radius: 0 5px 5px 0; }}
                    .label {{ font-weight: 600; color: #64748b; font-size: 12px; text-transform: uppercase; }}
                    .value {{ font-size: 16px; color: #1e293b; margin-top: 5px; }}
                    .footer {{ background: #1e293b; color: #94a3b8; padding: 20px; border-radius: 0 0 10px 10px; text-align: center; font-size: 12px; }}
                    .attachment-note {{ background: #dbeafe; border: 1px solid #3b82f6; border-radius: 5px; padding: 15px; margin-top: 20px; text-align: center; }}
                    .attachment-note strong {{ color: #1e40af; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Veille Automatisée</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">{self.company_name}</p>
                    </div>
                    <div class="content">
                        <p>Bonjour,</p>
                        <p>Votre veille automatisée <strong>"{watch_name}"</strong> a été exécutée avec succès.</p>
                        
                        <div class="info-box">
                            <div class="label">Sujet analysé</div>
                            <div class="value">{topic}</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="label">Type de rapport</div>
                            <div class="value">{report_display}</div>
                        </div>
                        
                        <div class="info-box">
                            <div class="label">Date d'exécution</div>
                            <div class="value">{current_date}</div>
                        </div>
                        
                        <div class="attachment-note">
                            📎 <strong>Le rapport complet est joint en pièce jointe (PDF)</strong>
                        </div>
                    </div>
                    <div class="footer">
                        <p>Ce message a été généré automatiquement par {self.company_name}</p>
                        <p>Pour modifier vos préférences de veille, connectez-vous à votre tableau de bord.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Attach HTML body
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))

            # Attach PDF
            pdf_filename = f"Veille_{watch_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
            pdf_attachment = MIMEApplication(pdf_content, _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
            msg.attach(pdf_attachment)

            # Send email
            logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {len(recipients)} recipients")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


# Singleton instance
email_sender = EmailSender()
