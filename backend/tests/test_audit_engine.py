import pytest

from app.audit_engine import AuditEngine


class TestAuditEngine:
    """Test suite for the AuditEngine core logic."""

    def test_rate_overage_detection(self) -> None:
        """
        Test that rate overage anomaly is correctly detected when
        invoice charge per mile exceeds contracted rate.
        """
        # Arrange: Set up contract rules
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
            "allowed_accessorials": ["FUEL SURCHARGE"],
            "min_string_similarity": 0.8,
        }

        engine = AuditEngine(contract_rules)

        # Invoice with rate of $4.12/mile (1857.50 / 450)
        invoice_data = {
            "carrier_name": "ROADWAY EXPRESS",
            "invoice_number": "INV-2024-001",
            "invoice_date": "2024-01-15",
            "total_charge": 1857.50,  # $4.12/mile
            "shipment_reference": "PRO-12345",
        }

        shipment_data = {
            "mileage": 450,
            "origin": "Chicago, IL",
            "destination": "Denver, CO",
        }

        # Act: Perform audit
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Rate overage should be detected
        rate_anomalies = [a for a in anomalies if a["type"] == "RATE_OVERAGE"]

        assert len(rate_anomalies) == 1, "Expected one rate overage anomaly"

        anomaly = rate_anomalies[0]
        assert anomaly["type"] == "RATE_OVERAGE"
        assert anomaly["severity"] in ["HIGH", "MEDIUM"]
        assert "4.12" in anomaly["detail"] or "4.13" in anomaly["detail"]  # Allow rounding
        assert "3.50" in anomaly["detail"]
        assert anomaly["field"] == "total_charge"

        # Verify calculated values
        expected_charge = 3.50 * 450  # $1,575
        assert anomaly["expected"] == expected_charge
        assert anomaly["actual"] == 1857.50

    def test_no_anomalies_when_within_limits(self) -> None:
        """
        Test that no anomalies are detected when invoice is within contract limits.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
            "min_string_similarity": 0.8,
        }

        engine = AuditEngine(contract_rules)

        # Invoice with rate of $3.00/mile (well within limit)
        invoice_data = {
            "carrier_name": "ROADWAY EXPRESS",
            "total_charge": 1350.00,  # $3.00/mile
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: No anomalies should be detected
        assert len(anomalies) == 0, f"Expected no anomalies, but found: {anomalies}"

    def test_carrier_mismatch_detection(self) -> None:
        """
        Test that carrier mismatch is detected when names don't match.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
            "min_string_similarity": 0.8,
        }

        engine = AuditEngine(contract_rules)

        invoice_data = {
            "carrier_name": "FEDEX FREIGHT",  # Different carrier
            "total_charge": 1500.00,
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Carrier mismatch should be detected
        carrier_anomalies = [a for a in anomalies if a["type"] == "CARRIER_MISMATCH"]

        assert len(carrier_anomalies) == 1, "Expected one carrier mismatch anomaly"

        anomaly = carrier_anomalies[0]
        assert anomaly["type"] == "CARRIER_MISMATCH"
        assert anomaly["severity"] == "HIGH"
        assert anomaly["field"] == "carrier_name"
        assert "FEDEX FREIGHT" in anomaly["detail"]
        assert "ROADWAY EXPRESS" in anomaly["detail"]

    def test_carrier_name_similarity_tolerance(self) -> None:
        """
        Test that minor variations in carrier name are tolerated.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
            "min_string_similarity": 0.8,
        }

        engine = AuditEngine(contract_rules)

        # Minor variation: missing one letter
        invoice_data = {
            "carrier_name": "ROADWAY EXPRES",  # Missing 'S'
            "total_charge": 1500.00,
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Should not flag as mismatch (high similarity)
        carrier_anomalies = [a for a in anomalies if a["type"] == "CARRIER_MISMATCH"]
        assert len(carrier_anomalies) == 0, "Minor variations should be tolerated"

    def test_missing_required_fields(self) -> None:
        """
        Test that missing required fields are flagged.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
        }

        engine = AuditEngine(contract_rules)

        # Missing carrier_name and total_charge
        invoice_data = {"invoice_number": "INV-2024-001"}

        # Missing mileage
        shipment_data = {"origin": "Chicago, IL"}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Should detect missing fields
        missing_anomalies = [a for a in anomalies if a["type"] == "MISSING_FIELD"]

        assert len(missing_anomalies) >= 2, "Should detect multiple missing fields"

        missing_fields = [a["field"] for a in missing_anomalies]
        assert "carrier_name" in missing_fields
        assert "total_charge" in missing_fields
        assert "mileage" in missing_fields

    def test_invalid_charge_detection(self) -> None:
        """
        Test that invalid charges (zero or negative) are flagged.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
        }

        engine = AuditEngine(contract_rules)

        invoice_data = {
            "carrier_name": "ROADWAY EXPRESS",
            "total_charge": 0.0,  # Invalid: zero charge
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Should detect invalid charge
        invalid_anomalies = [a for a in anomalies if a["type"] == "INVALID_CHARGE"]

        assert len(invalid_anomalies) == 1, "Should detect invalid charge"
        assert invalid_anomalies[0]["severity"] == "HIGH"

    def test_multiple_anomalies_detected(self) -> None:
        """
        Test that multiple anomalies can be detected simultaneously.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
            "min_string_similarity": 0.8,
        }

        engine = AuditEngine(contract_rules)

        # Invoice with both rate overage and carrier mismatch
        invoice_data = {
            "carrier_name": "FEDEX FREIGHT",  # Wrong carrier
            "total_charge": 2000.00,  # $4.44/mile (over limit)
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Should detect both anomalies
        assert len(anomalies) >= 2, "Should detect multiple anomalies"

        anomaly_types = [a["type"] for a in anomalies]
        assert "RATE_OVERAGE" in anomaly_types
        assert "CARRIER_MISMATCH" in anomaly_types

    def test_suspicious_charge_detection(self) -> None:
        """
        Test that unreasonably high charges are flagged as suspicious.
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
        }

        engine = AuditEngine(contract_rules)

        # Extremely high charge: $100/mile (way over 10x threshold)
        invoice_data = {
            "carrier_name": "ROADWAY EXPRESS",
            "total_charge": 45000.00,  # $100/mile
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: Should detect suspicious charge
        suspicious_anomalies = [a for a in anomalies if a["type"] == "SUSPICIOUS_CHARGE"]

        assert len(suspicious_anomalies) == 1, "Should detect suspicious charge"
        assert suspicious_anomalies[0]["severity"] == "MEDIUM"

    def test_edge_case_exact_rate_limit(self) -> None:
        """
        Test behavior when rate exactly matches the limit (should pass).
        """
        # Arrange
        contract_rules = {
            "carrier_name": "ROADWAY EXPRESS",
            "max_rate_per_mile": 3.50,
        }

        engine = AuditEngine(contract_rules)

        # Exactly at limit: $3.50/mile
        invoice_data = {
            "carrier_name": "ROADWAY EXPRESS",
            "total_charge": 1575.00,  # Exactly $3.50/mile
        }

        shipment_data = {"mileage": 450}

        # Act
        anomalies = engine.audit(invoice_data, shipment_data)

        # Assert: No rate overage should be detected
        rate_anomalies = [a for a in anomalies if a["type"] == "RATE_OVERAGE"]
        assert len(rate_anomalies) == 0, "Exact rate match should not trigger anomaly"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
