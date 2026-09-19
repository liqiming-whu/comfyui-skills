import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "workflow_tool.py"
SPEC = importlib.util.spec_from_file_location("workflow_tool", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class WorkflowToolTests(unittest.TestCase):
    def test_valid_ui_graph(self):
        workflow = {
            "last_node_id": 2,
            "last_link_id": 1,
            "nodes": [
                {"id": 1, "type": "Source", "inputs": [], "outputs": [{"links": [1]}]},
                {"id": 2, "type": "Target", "inputs": [{"link": 1}], "outputs": []},
            ],
            "links": [[1, 1, 0, 2, 0, "IMAGE"]],
            "version": 0.4,
        }
        self.assertEqual(MODULE.detect_format(workflow), "ui")
        self.assertEqual(MODULE.validate_ui(workflow), [])

    def test_broken_back_reference_is_reported(self):
        workflow = {
            "last_node_id": 2,
            "last_link_id": 1,
            "nodes": [
                {"id": 1, "type": "Source", "inputs": [], "outputs": [{"links": []}]},
                {"id": 2, "type": "Target", "inputs": [{"link": 1}], "outputs": []},
            ],
            "links": [[1, 1, 0, 2, 0, "IMAGE"]],
            "version": 0.4,
        }
        self.assertIn("link 1: missing source output back-reference", MODULE.validate_ui(workflow))

    def test_api_missing_source_is_reported(self):
        prompt = {"2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}}}
        self.assertEqual(MODULE.detect_format(prompt), "api")
        self.assertIn("node 2 input images: missing source node 1", MODULE.validate_api(prompt))



if __name__ == "__main__":
    unittest.main()
