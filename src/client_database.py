"""
Client Database Module.
Manages client data and performs fuzzy matching for business names.

This module handles loading client data from the CSV file and matching
business names extracted from PDFs to client records using fuzzy string matching.
"""

import csv
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from rapidfuzz import fuzz, process
from .logger import get_logger

logger = get_logger('ClientDatabase')


class ClientDatabase:
    """Manages client information and matching."""

    def __init__(self, csv_path: str, fuzzy_threshold: int = 85):
        """
        Initialize client database.

        Args:
            csv_path: Path to clients CSV file
            fuzzy_threshold: Minimum similarity score for fuzzy matching (0-100)
        """
        self.csv_path = Path(csv_path)
        self.fuzzy_threshold = fuzzy_threshold
        self.clients = []
        self.business_names = []
        self.logger = logger

        self.load_clients()

    def load_clients(self):
        """Load clients from CSV file."""
        if not self.csv_path.exists():
            self.logger.error(f"Client database not found: {self.csv_path}")
            raise FileNotFoundError(f"Client database not found: {self.csv_path}")

        self.clients = []
        self.business_names = []

        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Log the headers we found
                self.logger.debug(f"CSV Headers: {reader.fieldnames}")

                for row_num, row in enumerate(reader, start=2):
                    # Skip empty rows
                    client_name = row.get('Client-Name', '').strip()
                    if not client_name:
                        self.logger.debug(f"Skipping empty row {row_num}")
                        continue

                    # Validate required fields
                    contact_email = row.get('Contact-Email', '').strip()
                    contact_name = row.get('Contact-Name', '').strip()

                    if not contact_email:
                        self.logger.warning(f"Row {row_num}: Missing email for {client_name}")

                    if not contact_name:
                        self.logger.warning(f"Row {row_num}: Missing contact name for {client_name}")

                    # Store the client (we keep all clients, not filtering by Active status
                    # since the actual CSV doesn't have an Active column)
                    self.clients.append(row)
                    self.business_names.append(client_name)
                    self.logger.debug(f"Loaded client: {client_name}")

            self.logger.info(f"Loaded {len(self.clients)} clients from database")

        except KeyError as e:
            self.logger.error(f"Missing expected column in CSV: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to load client database: {str(e)}")
            raise

    def find_client(self, business_name: str) -> Optional[Dict]:
        """
        Find a client by business name using fuzzy matching.

        Args:
            business_name: Business name to search for

        Returns:
            Client dictionary if found, None otherwise
        """
        if not business_name:
            return None

        business_name = business_name.strip()

        # Try exact match first (case-insensitive)
        for client in self.clients:
            client_name = client.get('Client-Name', '').strip()
            if client_name.lower() == business_name.lower():
                self.logger.info(
                    f"Exact match found: '{business_name}' -> {client_name}"
                )
                return client

        # Try fuzzy matching with token_sort_ratio (better for word order variations)
        result = process.extractOne(
            business_name,
            self.business_names,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=self.fuzzy_threshold
        )

        if result:
            matched_name, score, _ = result
            # Find the client with this business name
            for client in self.clients:
                if client.get('Client-Name', '').strip() == matched_name:
                    self.logger.info(
                        f"Fuzzy match found: '{business_name}' -> "
                        f"'{matched_name}' (score: {score:.1f})"
                    )
                    return client

        self.logger.warning(f"No match found for business name: '{business_name}'")
        return None

    def find_all_matches(
        self,
        business_name: str,
        min_score: Optional[int] = None
    ) -> List[Tuple[Dict, int]]:
        """
        Find all possible matches for a business name above the threshold.

        Useful for detecting multiple potential matches (ambiguous cases).

        Args:
            business_name: Business name to match
            min_score: Minimum score threshold (defaults to fuzzy_threshold)

        Returns:
            List of (client_dict, score) tuples, sorted by score descending
        """
        if not business_name or not business_name.strip():
            return []

        business_name = business_name.strip()
        min_score = min_score or self.fuzzy_threshold

        if not self.clients:
            self.logger.warning("No clients loaded in database")
            return []

        # Get all matches above threshold
        results = process.extract(
            business_name,
            self.business_names,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=min_score,
            limit=None  # Get all matches above threshold
        )

        # Convert to client dicts with scores
        matches = []
        for matched_name, score, _ in results:
            for client in self.clients:
                if client.get('Client-Name', '').strip() == matched_name:
                    matches.append((client, int(score)))
                    break

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)

        self.logger.info(f"Found {len(matches)} matches for '{business_name}'")
        return matches

    def get_service_type(self, client: Dict, report_type: str) -> str:
        """
        Determine service type from report type.

        Args:
            client: Client dictionary
            report_type: 'seo' or 'google_ads'

        Returns:
            'SEO' or 'SEM'
        """
        if report_type.lower() == 'google_ads':
            return 'SEM'
        else:
            return 'SEO'

    def get_personalized_intro(self, client: Dict, report_type: str) -> str:
        """
        Get the personalized introduction text for the client based on report type.

        Args:
            client: Client dictionary
            report_type: 'seo' or 'google_ads'

        Returns:
            Personalized introduction HTML text
        """
        if report_type.lower() == 'google_ads':
            intro = client.get('Google-Ads-Introduction', '').strip()
        else:
            intro = client.get('SEO-Introduction', '').strip()

        return intro

    def validate_database(self) -> Dict[str, any]:
        """
        Validate the database for common issues.

        Returns:
            Dictionary with validation results
        """
        issues = {
            'duplicate_names': [],
            'missing_emails': [],
            'missing_contact_names': [],
            'missing_seo_intro': [],
            'missing_google_ads_intro': [],
            'total_clients': len(self.clients)
        }

        # Check for duplicate client names
        name_counts = {}
        for client in self.clients:
            name_lower = client.get('Client-Name', '').strip().lower()
            if name_lower:
                name_counts[name_lower] = name_counts.get(name_lower, 0) + 1

        issues['duplicate_names'] = [
            name for name, count in name_counts.items() if count > 1
        ]

        # Check for missing data
        for client in self.clients:
            client_name = client.get('Client-Name', '').strip()

            if not client.get('Contact-Email', '').strip():
                issues['missing_emails'].append(client_name)

            if not client.get('Contact-Name', '').strip():
                issues['missing_contact_names'].append(client_name)

            if not client.get('SEO-Introduction', '').strip():
                issues['missing_seo_intro'].append(client_name)

            if not client.get('Google-Ads-Introduction', '').strip():
                issues['missing_google_ads_intro'].append(client_name)

        # Log validation results
        if any([
            issues['duplicate_names'],
            issues['missing_emails'],
            issues['missing_contact_names']
        ]):
            self.logger.warning("Database validation found issues:")
            if issues['duplicate_names']:
                self.logger.warning(f"  Duplicate names: {issues['duplicate_names']}")
            if issues['missing_emails']:
                self.logger.warning(f"  Missing emails: {len(issues['missing_emails'])} clients")
            if issues['missing_contact_names']:
                self.logger.warning(f"  Missing contact names: {len(issues['missing_contact_names'])} clients")
        else:
            self.logger.info("Database validation passed: No critical issues found")

        return issues

    def get_all_clients(self) -> List[Dict]:
        """
        Get all clients.

        Returns:
            List of client dictionaries
        """
        return self.clients.copy()
