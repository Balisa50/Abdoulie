import logging
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)


class AuditEngine:
    """
    Validates freight invoices against contract rules and detects anomalies.
    Implements business logic for automated freight auditing.
    """

    def __init__(self, contract_rules: dict[str, Any]) -> None:
        """
        Initialize the audit engine with contract rules.

        Args:
            contract_rules: Dictionary containing contract terms, e.g.:
                {
                    'carrier_name': 'ROADWAY EXPRESS',
                    'max_rate_per_mile': 3.50,
                    'allowed_accessorials': ['FUEL SURCHARGE'],
                    'min_string_similarity': 0.8
                }
        """
        self.contract_rules = contract_rules
        self.min_similarity = contract_rules.get("min_string_similarity", 0.8)

    def audit(
        self, invoice_data: dict[str, Any], shipment_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Perform comprehensive audit of invoice against contract rules.

        Args:
            invoice_data: Extracted invoice data containing:
                - carrier_name: str
                - total_charge: float
                - invoice_number: str
                etc.
            shipment_data: Reference shipment data containing:
                - mileage: float
                - expected_rate: float (optional)
                etc.

        Returns:
            List of anomaly dictionaries, each containing:
                - type: str (anomaly type identifier)
                - severity: str (HIGH, MEDIUM, LOW)
                - detail: str (human-readable description)
                - field: str (affected field name)
                - expected: Any (expected value)
                - actual: Any (actual value)
        """
        anomalies: list[dict[str, Any]] = []

        # Validation: Check required fields
        required_invoice_fields = ["carrier_name", "total_charge"]
        required_shipment_fields = ["mileage"]

        for field in required_invoice_fields:
            if not invoice_data.get(field):
                anomalies.append(
                    {
                        "type": "MISSING_FIELD",
                        "severity": "HIGH",
                        "detail": f"Required invoice field '{field}' is missing or empty",
                        "field": field,
                        "expected": "non-empty value",
                        "actual": None,
                    }
                )

        for field in required_shipment_fields:
            if not shipment_data.get(field):
                anomalies.append(
                    {
                        "type": "MISSING_FIELD",
                        "severity": "HIGH",
                        "detail": f"Required shipment field '{field}' is missing or empty",
                        "field": field,
                        "expected": "non-empty value",
                        "actual": None,
                    }
                )

        # If critical fields are missing, return early
        if anomalies:
            return anomalies

        # Check 1: Rate Overage
        rate_anomalies = self._check_rate_overage(invoice_data, shipment_data)
        anomalies.extend(rate_anomalies)

        # Check 2: Carrier Mismatch
        carrier_anomalies = self._check_carrier_match(invoice_data)
        anomalies.extend(carrier_anomalies)

        # Check 3: Additional validations
        additional_anomalies = self._check_additional_rules(invoice_data, shipment_data)
        anomalies.extend(additional_anomalies)

        logger.info(f"Audit complete: found {len(anomalies)} anomalies")
        return anomalies

    def _check_rate_overage(
        self, invoice_data: dict[str, Any], shipment_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Check if the rate per mile exceeds the contracted maximum.
        """
        anomalies = []

        total_charge = invoice_data.get("total_charge")
        mileage = shipment_data.get("mileage")
        max_rate = self.contract_rules.get("max_rate_per_mile")

        if not all([total_charge, mileage, max_rate]):
            return anomalies

        # Ensure numeric types
        try:
            total_charge = float(total_charge)
            mileage = float(mileage)
            max_rate = float(max_rate)
        except (ValueError, TypeError):
            logger.error("Invalid numeric values for rate calculation")
            return anomalies

        if mileage <= 0:
            anomalies.append(
                {
                    "type": "INVALID_DATA",
                    "severity": "HIGH",
                    "detail": "Mileage must be greater than zero",
                    "field": "mileage",
                    "expected": "> 0",
                    "actual": mileage,
                }
            )
            return anomalies

        # Calculate actual rate per mile
        actual_rate = total_charge / mileage

        if actual_rate > max_rate:
            overage_amount = total_charge - (max_rate * mileage)
            overage_percent = ((actual_rate - max_rate) / max_rate) * 100

            anomalies.append(
                {
                    "type": "RATE_OVERAGE",
                    "severity": "HIGH" if overage_percent > 10 else "MEDIUM",
                    "detail": (
                        f"Calculated rate ${actual_rate:.2f}/mi exceeds "
                        f"contracted ${max_rate:.2f}/mi by ${overage_amount:.2f} "
                        f"({overage_percent:.1f}% over)"
                    ),
                    "field": "total_charge",
                    "expected": max_rate * mileage,
                    "actual": total_charge,
                }
            )

        return anomalies

    def _check_carrier_match(self, invoice_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Check if the carrier name on the invoice matches the contracted carrier.
        Uses string similarity to handle minor variations.
        """
        anomalies = []

        invoice_carrier = invoice_data.get("carrier_name")
        contract_carrier = self.contract_rules.get("carrier_name")

        if not invoice_carrier or not contract_carrier:
            return anomalies

        # Normalize for comparison
        invoice_carrier_norm = str(invoice_carrier).upper().strip()
        contract_carrier_norm = str(contract_carrier).upper().strip()

        # Calculate similarity
        similarity = SequenceMatcher(None, invoice_carrier_norm, contract_carrier_norm).ratio()

        if similarity < self.min_similarity:
            anomalies.append(
                {
                    "type": "CARRIER_MISMATCH",
                    "severity": "HIGH",
                    "detail": (
                        f"Invoice carrier '{invoice_carrier}' does not match "
                        f"contracted carrier '{contract_carrier}' "
                        f"(similarity: {similarity:.2%})"
                    ),
                    "field": "carrier_name",
                    "expected": contract_carrier,
                    "actual": invoice_carrier,
                }
            )

        return anomalies

    def _check_additional_rules(
        self, invoice_data: dict[str, Any], shipment_data: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Perform additional business rule validations.
        """
        anomalies = []

        # Check for negative or zero charges
        total_charge = invoice_data.get("total_charge")
        if total_charge is not None:
            try:
                if float(total_charge) <= 0:
                    anomalies.append(
                        {
                            "type": "INVALID_CHARGE",
                            "severity": "HIGH",
                            "detail": f"Total charge ${total_charge} must be positive",
                            "field": "total_charge",
                            "expected": "> 0",
                            "actual": total_charge,
                        }
                    )
            except (ValueError, TypeError):
                pass

        # Check for unreasonably high charges (10x the expected rate)
        if total_charge and shipment_data.get("mileage"):
            try:
                max_rate = self.contract_rules.get("max_rate_per_mile", 10.0)
                threshold = float(max_rate) * float(shipment_data["mileage"]) * 10

                if float(total_charge) > threshold:
                    anomalies.append(
                        {
                            "type": "SUSPICIOUS_CHARGE",
                            "severity": "MEDIUM",
                            "detail": (
                                f"Total charge ${total_charge} is unusually high "
                                f"(exceeds 10x expected rate)"
                            ),
                            "field": "total_charge",
                            "expected": f"< ${threshold:.2f}",
                            "actual": total_charge,
                        }
                    )
            except (ValueError, TypeError):
                pass

        return anomalies
