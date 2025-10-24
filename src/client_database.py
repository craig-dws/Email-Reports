"""
Client Database Module.
Manages client data and performs fuzzy matching for business names.
"""

import csv
from pathlib import Path
from typing import Dict, Optional, List
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
                for row in reader:
                    # Only load active clients
                    if row.get('Active', 'TRUE').upper() == 'TRUE':
                        self.clients.append(row)
                        self.business_names.append(row['BusinessName'])

            self.logger.info(f"Loaded {len(self.clients)} active clients from database")

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

        # Try exact match first (case-insensitive)
        for client in self.clients:
            if client['BusinessName'].lower() == business_name.lower():
                self.logger.info(
                    f"Exact match found: '{business_name}' -> {client['BusinessName']}"
                )
                return client

        # Try fuzzy matching
        result = process.extractOne(
            business_name,
            self.business_names,
            scorer=fuzz.ratio,
            score_cutoff=self.fuzzy_threshold
        )

        if result:
            matched_name, score, _ = result
            # Find the client with this business name
            for client in self.clients:
                if client['BusinessName'] == matched_name:
                    self.logger.info(
                        f"Fuzzy match found: '{business_name}' -> "
                        f"'{matched_name}' (score: {score})"
                    )
                    return client

        self.logger.warning(f"No match found for business name: '{business_name}'")
        return None

    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """
        Get client by ID.

        Args:
            client_id: Client ID to search for

        Returns:
            Client dictionary if found, None otherwise
        """
        for client in self.clients:
            if client['ClientID'] == str(client_id):
                return client
        return None

    def get_all_clients(self) -> List[Dict]:
        """
        Get all active clients.

        Returns:
            List of client dictionaries
        """
        return self.clients.copy()

    def add_client(self, client_data: Dict) -> bool:
        """
        Add a new client to the database.

        Args:
            client_data: Dictionary containing client information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate new ID
            max_id = max([int(c['ClientID']) for c in self.clients], default=0)
            client_data['ClientID'] = str(max_id + 1)

            # Add timestamps
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            client_data.setdefault('CreatedDate', today)
            client_data.setdefault('LastModifiedDate', today)
            client_data.setdefault('Active', 'TRUE')

            # Append to CSV
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'ClientID', 'FirstName', 'BusinessName', 'Email',
                    'ServiceType', 'PersonalizedText', 'Active',
                    'CreatedDate', 'LastModifiedDate'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(client_data)

            # Reload database
            self.load_clients()
            self.logger.info(f"Added new client: {client_data['BusinessName']}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to add client: {str(e)}")
            return False

    def update_client(self, client_id: str, updates: Dict) -> bool:
        """
        Update client information.

        Args:
            client_id: Client ID to update
            updates: Dictionary of fields to update

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read all clients
            all_clients = []
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                all_clients = list(reader)

            # Update the client
            from datetime import datetime
            updated = False
            for client in all_clients:
                if client['ClientID'] == str(client_id):
                    client.update(updates)
                    client['LastModifiedDate'] = datetime.now().strftime('%Y-%m-%d')
                    updated = True
                    break

            if not updated:
                self.logger.warning(f"Client ID {client_id} not found for update")
                return False

            # Write back to CSV
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_clients)

            # Reload database
            self.load_clients()
            self.logger.info(f"Updated client ID {client_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update client: {str(e)}")
            return False

    def deactivate_client(self, client_id: str) -> bool:
        """
        Deactivate a client (soft delete).

        Args:
            client_id: Client ID to deactivate

        Returns:
            True if successful, False otherwise
        """
        return self.update_client(client_id, {'Active': 'FALSE'})
