import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "ui_graph.py"
SPEC = importlib.util.spec_from_file_location("ui_graph", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class UiGraphTests(unittest.TestCase):
    def graph(self):
        return {
            "last_node_id": 2,
            "last_link_id": 0,
            "nodes": [
                {"id": 1, "inputs": [], "outputs": [{"type": "MODEL", "links": None}]},
                {"id": 2, "inputs": [{"name": "model", "type": "MODEL", "link": None}, {"name": "steps", "widget": {"name": "steps"}, "link": None}], "outputs": [], "widgets_values": [5], "widgets_values_named": {"steps": 5}},
            ],
            "links": [],
        }

    def test_connect_updates_all_link_references(self):
        graph = self.graph()
        link_id = MODULE.connect(graph, 1, 0, 2, 0, None)
        self.assertEqual(graph["links"], [[link_id, 1, 0, 2, 0, "MODEL"]])
        self.assertEqual(graph["nodes"][0]["outputs"][0]["links"], [link_id])
        self.assertEqual(graph["nodes"][1]["inputs"][0]["link"], link_id)

    def test_set_widget_synchronizes_both_representations(self):
        graph = self.graph()
        MODULE.set_widget(graph, 2, "steps", 8)
        self.assertEqual(graph["nodes"][1]["widgets_values"], [8])
        self.assertEqual(graph["nodes"][1]["widgets_values_named"]["steps"], 8)

    def test_remove_node_cleans_links(self):
        graph = self.graph()
        MODULE.connect(graph, 1, 0, 2, 0, None)
        MODULE.remove_node(graph, 1)
        self.assertEqual(graph["links"], [])
        self.assertIsNone(graph["nodes"][0]["inputs"][0]["link"])


if __name__ == "__main__":
    unittest.main()
