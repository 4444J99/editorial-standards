import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    "upstreams", Path(__file__).parents[1] / "scripts/check_reader_upstreams.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class UpstreamTests(unittest.TestCase):
    def fake(self, path):
        if "/pulls/" in path:
            return {"merged": True, "merge_commit_sha": "a" * 40}
        if "/commits/" in path:
            return {"sha": "b" * 40}
        if "/compare/" in path:
            return {"status": "ahead"}
        return {"default_branch": "main"}

    def test_accepted_inputs_are_immutable_refs(self):
        report = module.inspect(self.fake)
        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(report["inputs"]), 3)
        self.assertTrue(all(r["merge_commit"] == "a" * 40 for r in report["inputs"]))

    def test_unmerged_and_nonboolean_are_not_accepted(self):
        for merged in (False, 1, "true", None):
            def get(path):
                return {"merged": merged} if "/pulls/" in path else self.fake(path)
            self.assertEqual(module.inspect(get)["status"], "unmeasured")

    def test_diverged_default_does_not_accept_closed_pr(self):
        def get(path):
            return {"status": "diverged"} if "/compare/" in path else self.fake(path)
        self.assertEqual(module.inspect(get)["status"], "unmeasured")

    def test_failure_is_redacted_and_other_inputs_still_inspected(self):
        seen = []
        def get(path):
            seen.append(path)
            if "schema-definitions" in path:
                raise ValueError("PRIVATE_CREDENTIAL")
            return self.fake(path)
        report = module.inspect(get)
        self.assertNotIn("PRIVATE_CREDENTIAL", str(report))
        self.assertEqual(report["inputs"][-1]["status"], "accepted")

    def test_head_movement_rejects_observation(self):
        calls = {}
        def get(path):
            if "/commits/" in path:
                calls[path] = calls.get(path, 0) + 1
                return {"sha": ("b" if calls[path] == 1 else "c") * 40}
            return self.fake(path)
        self.assertEqual(module.inspect(get)["status"], "unmeasured")
