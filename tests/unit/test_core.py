#!/usr/bin/env python3
"""
Tests unitaires pour Sharingan OS
Couverture: modules critiques
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCapabilityAssessment:
    """Tests pour sharingan_capability_assessment"""

    def test_assessment_returns_dict(self):
        """Vérifier que l'évaluation retourne un dict"""
        from sharingan_capability_assessment import assess_sharingan_capabilities
        result = assess_sharingan_capabilities()
        assert isinstance(result, dict)

    def test_assessment_has_required_keys(self):
        """Vérifier les clés requises"""
        from sharingan_capability_assessment import assess_sharingan_capabilities
        result = assess_sharingan_capabilities()
        required_keys = ["autonomy_score", "capabilities_status", "improvements_needed"]
        assert all(k in result for k in required_keys)

    def test_autonomy_score_range(self):
        """Score entre 0 et 1"""
        from sharingan_capability_assessment import assess_sharingan_capabilities
        result = assess_sharingan_capabilities()
        assert 0 <= result["autonomy_score"] <= 1

    def test_capabilities_status_structure(self):
        """Vérifier structure des statuts"""
        from sharingan_capability_assessment import assess_sharingan_capabilities
        result = assess_sharingan_capabilities()
        required_keys = ["FONCTIONNEL", "PARTIEL", "LIMITE", "MANQUANT"]
        assert all(k in result["capabilities_status"] for k in required_keys)

    def test_run_assessment_returns_dict(self):
        """Tester le point d'entrée principal"""
        from sharingan_capability_assessment import run_assessment
        result = run_assessment()
        assert isinstance(result, dict)


class TestFakeDetector:
    """Tests pour fake_detector"""

    def test_detect_fakes_placeholder(self):
        """Détection de placeholder"""
        from fake_detector import detect_fakes
        result = detect_fakes("AI Response to: [TODO] implement", context="ai_response")
        assert result.is_fake is True
        assert result.fake_type == "placeholder"

    def test_detect_fakes_valid(self):
        """Contenu valide accepté"""
        from fake_detector import detect_fakes
        result = detect_fakes("def calculate_sum(a, b): return a + b", context="code")
        assert result.is_fake is False

    def test_validate_readiness(self):
        """Validation du système"""
        from fake_detector import validate_readiness
        result = validate_readiness()
        assert "ready" in result
        assert "components" in result


class TestCheckObligations:
    """Tests pour check_obligations"""

    def test_check_obligations_returns_dict(self):
        """Vérifier retour de check_obligations"""
        from check_obligations import check_obligations
        result = check_obligations()
        assert isinstance(result, dict)
        assert "file" in result
        assert "passed" in result

    def test_check_obligations_on_example_file(self):
        """Tester sur un fichier existant"""
        from check_obligations import check_obligations
        from pathlib import Path
        result = check_obligations(str(Path(__file__).parent.parent / "AGENTS.md"))
        assert result["passed"] is True or "issues" in result


class TestGenomeProposer:
    """Tests pour genome_proposer"""

    def test_proposer_creation(self):
        """Création du proposeur"""
        from genome_proposer import GenomeProposer
        proposer = GenomeProposer()
        assert proposer is not None
        assert isinstance(proposer.proposals, list)

    def test_get_evolution_stats(self):
        """Stats d'évolution"""
        from genome_proposer import GenomeProposer
        proposer = GenomeProposer()
        stats = proposer.get_evolution_stats()
        assert "total_evolutions" in stats
        assert "by_type" in stats


class TestCheckDependencies:
    """Tests pour check_dependencies"""

    def test_check_returns_structure(self):
        """Vérifier structure de retour"""
        from check_dependencies import check_dependencies
        result = check_dependencies()
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
