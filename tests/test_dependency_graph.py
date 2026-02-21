"""Tests for dependency graph construction and validation."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'demo'))
from run_demo import build_dependency_graph


class TestDependencyGraph:
    """Test suite for 39-document dependency graph."""

    def test_graph_has_39_documents(self):
        graph = build_dependency_graph()
        assert len(graph) == 39, f"Expected 39 documents, got {len(graph)}"

    def test_all_documents_canonical(self):
        graph = build_dependency_graph()
        for doc_id, info in graph.items():
            assert info["status"] == "CANONICAL", f"{doc_id} is not CANONICAL"

    def test_layer_distribution(self):
        """Layer 0: DOC-001 to DOC-006, Layer 1: DOC-007 to DOC-009,
        Layer 2: DOC-010 to DOC-023, Layer 3: DOC-024 to DOC-039."""
        graph = build_dependency_graph()
        layers = {0: 0, 1: 0, 2: 0, 3: 0}
        for info in graph.values():
            layers[info["layer"]] += 1
        assert layers[0] == 6, f"Layer 0 should have 6 docs, got {layers[0]}"
        assert layers[1] == 3, f"Layer 1 should have 3 docs, got {layers[1]}"
        assert layers[2] == 14, f"Layer 2 should have 14 docs, got {layers[2]}"
        assert layers[3] == 16, f"Layer 3 should have 16 docs, got {layers[3]}"

    def test_doc_ids_sequential(self):
        graph = build_dependency_graph()
        for i in range(1, 40):
            assert f"DOC-{i:03d}" in graph, f"DOC-{i:03d} missing from graph"

    def test_no_self_dependencies(self):
        graph = build_dependency_graph()
        for doc_id, info in graph.items():
            assert doc_id not in info["depends_on"], f"{doc_id} depends on itself"

    def test_dependencies_exist(self):
        """Every dependency reference must point to an existing document."""
        graph = build_dependency_graph()
        for doc_id, info in graph.items():
            for dep in info["depends_on"]:
                assert dep in graph, f"{doc_id} depends on {dep} which doesn't exist"

    def test_doc_001_has_no_dependencies(self):
        """Root document should have no dependencies."""
        graph = build_dependency_graph()
        assert len(graph["DOC-001"]["depends_on"]) == 0, "DOC-001 should have no dependencies"

    def test_layer_values_valid(self):
        graph = build_dependency_graph()
        for doc_id, info in graph.items():
            assert info["layer"] in (0, 1, 2, 3), f"{doc_id} has invalid layer {info['layer']}"
