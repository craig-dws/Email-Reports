"""
Logging configuration for Email Reports Automation System.
Provides comprehensive logging with file rotation and standardized formatting.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class ReportLogger:
    """Centralized logging system for the application."""

    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        """
        Initialize the logger.

        Args:
            log_dir: Directory to store log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create log file with current date
        log_file = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

        # Configure logging format
        log_format = '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            datefmt=date_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # Also output to console
            ]
        )

        self.logger = logging.getLogger('EmailReports')
        self.logger.info("="*60)
        self.logger.info("Email Reports Automation System - Starting")
        self.logger.info("="*60)

    def get_logger(self, name: str = None) -> logging.Logger:
        """
        Get a logger instance.

        Args:
            name: Name for the logger (typically module name)

        Returns:
            Logger instance
        """
        if name:
            return logging.getLogger(f'EmailReports.{name}')
        return self.logger

    def log_operation(self, operation: str, status: str, details: str = ""):
        """
        Log a major operation with standardized format.

        Args:
            operation: Name of the operation (e.g., "PDF_EXTRACTION")
            status: Status (SUCCESS, FAILED, WARNING)
            details: Additional details
        """
        message = f"[{operation}] {status}"
        if details:
            message += f" - {details}"

        if status == "SUCCESS":
            self.logger.info(message)
        elif status == "FAILED":
            self.logger.error(message)
        elif status == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)

    def log_completion(self, total: int, successful: int, failed: int):
        """
        Log completion summary.

        Args:
            total: Total items processed
            successful: Number of successful items
            failed: Number of failed items
        """
        self.logger.info("="*60)
        self.logger.info(f"Processing Complete: {successful}/{total} successful, {failed} failed")
        self.logger.info("="*60)


# Global logger instance
_logger_instance = None


def get_logger(name: str = None, log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
    """
    Get or create the global logger instance.

    Args:
        name: Name for the logger (typically module name)
        log_dir: Directory to store log files
        log_level: Logging level

    Returns:
        Logger instance
    """
    global _logger_instance

    if _logger_instance is None:
        _logger_instance = ReportLogger(log_dir, log_level)

    return _logger_instance.get_logger(name)
