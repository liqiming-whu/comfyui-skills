import importlib.util
import argparse
import unittest
from unittest import mock
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "monitor_comfyui.py"
SPEC = importlib.util.spec_from_file_location("monitor_comfyui", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class MonitorTests(unittest.TestCase):
    def test_request_json_accepts_empty_success_response(self):
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b""
        with mock.patch.object(MODULE.urllib.request, "urlopen", return_value=response):
            self.assertIsNone(MODULE.request_json("http://localhost", "/free", {}))

    def test_command_output_decoder_accepts_utf8_on_windows(self):
        text = "机械革命 RTX 5070 Ti"
        self.assertEqual(MODULE.decode_command_output(text.encode("utf-8")), text)

    def test_history_timing_and_cache(self):
        record = {
            "status": {
                "status_str": "success",
                "completed": True,
                "messages": [
                    ["execution_start", {"timestamp": 1000}],
                    ["execution_cached", {"timestamp": 1100, "nodes": ["1", "2"]}],
                    ["execution_success", {"timestamp": 3500}],
                ],
            }
        }
        result = MODULE.summarize_record("prompt", record)
        self.assertEqual(result["execution_seconds"], 2.5)
        self.assertEqual(result["cached_nodes"], ["1", "2"])

    def test_prompt_summary_records_models(self):
        prompt = {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "model.safetensors"},
            }
        }
        result = MODULE.prompt_summary(prompt)
        self.assertEqual(result["node_count"], 1)
        self.assertEqual(result["class_types"], ["UNETLoader"])
        self.assertEqual(result["model_references"], ["model.safetensors"])

    def test_vary_seed_inputs_changes_literals_but_not_links(self):
        prompt = {
            "1": {"class_type": "Seed", "inputs": {"seed": 1}},
            "2": {"class_type": "Sampler", "inputs": {"noise_seed": ["1", 0]}},
        }
        changed = MODULE.vary_seed_inputs(prompt)
        self.assertNotEqual(prompt["1"]["inputs"]["seed"], 1)
        self.assertLessEqual(prompt["1"]["inputs"]["seed"], 2**50)
        self.assertEqual(prompt["2"]["inputs"]["noise_seed"], ["1", 0])
        self.assertEqual(set(changed), {"1.seed"})

    def test_strict_benchmark_enables_real_run_guards(self):
        args = argparse.Namespace(
            strict_benchmark=True,
            clear_cache="never",
            vary_seed=False,
            require_output=False,
            require_uncached=False,
        )
        MODULE.apply_strict_benchmark(args)
        self.assertEqual(args.clear_cache, "before-each")
        self.assertTrue(args.vary_seed)
        self.assertTrue(args.require_output)
        self.assertTrue(args.require_uncached)


if __name__ == "__main__":
    unittest.main()
