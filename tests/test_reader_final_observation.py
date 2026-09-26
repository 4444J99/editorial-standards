"""Regressions for the final identity observation and literal HTML text."""

import sys
import unittest
from pathlib import Path

import test_reader_upstreams as fixtures

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from raw_html_contracts import raw_html_anchor_contract_lines


class FinalObservationTests(unittest.TestCase):
    def test_identity_change_during_final_commit_read_is_rejected(self):
        for field, replacement in (
            ("default_branch", "replacement"),
            ("full_name", "replacement/repository"),
            ("id", 999),
            ("id", True),
        ):
            with self.subTest(field=field, replacement=replacement):
                reads = {}
                changed = set()

                def get(path):
                    value = fixtures.UpstreamTests().fake(path)
                    if "/commits/" in path:
                        reads[path] = reads.get(path, 0) + 1
                        if reads[path] == 3:
                            name = path.split("repos/", 1)[1].split("/commits/", 1)[0]
                            changed.add(name)
                    if path.startswith("repositories/") and value["full_name"] in changed:
                        value[field] = replacement
                    return value

                report = fixtures.module.inspect(get)
                self.assertEqual(report["status"], "unmeasured")
                self.assertTrue(all(row["status"] == "unmeasured" for row in report["inputs"]))
                self.assertTrue(all("default_head" not in row for row in report["inputs"]))

    def test_plaintext_closing_tag_does_not_restore_anchor_parsing(self):
        for start in ("<plaintext>", "<PLAINTEXT>", "<plaintext/>"):
            with self.subTest(start=start):
                content = start + '</plaintext><a href="../../README.md">not a link</a>'
                self.assertEqual(raw_html_anchor_contract_lines(content), [])

    def test_anchor_before_plaintext_is_retained(self):
        before = '<a href="before">real link</a>'
        content = before + '<plaintext></plaintext><a href="after">literal</a>'
        self.assertEqual(raw_html_anchor_contract_lines(content),
                         raw_html_anchor_contract_lines(before))

    def test_other_raw_text_elements_still_close(self):
        anchor = '<a href="../../README.md">real link</a>'
        for tag in ("script", "style", "textarea", "title", "xmp", "iframe",
                    "noembed", "noframes"):
            with self.subTest(tag=tag):
                content = f"<{tag}>literal</{tag}>" + anchor
                self.assertEqual(raw_html_anchor_contract_lines(content),
                                 raw_html_anchor_contract_lines(anchor))
