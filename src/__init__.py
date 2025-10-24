"""
Email Reports Automation System
Main package initialization
"""

from .logger import get_logger, ReportLogger
from .pdf_extractor import PDFExtractor
from .client_database import ClientDatabase
from .email_generator import EmailGenerator
from .gmail_reader import GmailReader
from .gmail_sender import GmailSender
from .approval_workflow import ApprovalWorkflow
from .orchestrator import ReportOrchestrator

__version__ = '1.0.0'
__all__ = [
    'get_logger',
    'ReportLogger',
    'PDFExtractor',
    'ClientDatabase',
    'EmailGenerator',
    'GmailReader',
    'GmailSender',
    'ApprovalWorkflow',
    'ReportOrchestrator'
]
