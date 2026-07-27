"""Disposable integration contract for the track-local AGENTS review helpers."""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


TRACK = Path(__file__).resolve().parent.parent
SCRIPTS = TRACK / "scripts"
sys.path.insert(0, str(SCRIPTS))

import backup_agents
import bootstrap_review_toolchain as bootstrap
import dispatch_stage7
import inventory_agents
import sync_execution


class ReviewToolchainContract(unittest.TestCase):
    def test_disposable_integration_contract(self) -> None:
        negative_cases = 0

        def rejected(condition: bool, label: str) -> None:
            nonlocal negative_cases
            self.assertTrue(condition, label)
            negative_cases += 1

        inventory_result = inventory_agents.self_test()
        self.assertEqual(inventory_result["status"], "PASS")
        self.assertEqual(inventory_result["live_targets_touched"], 0)

        backup_result = backup_agents.self_test()
        self.assertEqual(backup_result["status"], "PASS")
        self.assertEqual(backup_result["live_targets_touched"], 0)
        self.assertGreaterEqual(backup_result["negative_case_count"], 5)

        rubric = bootstrap.load_rubric(TRACK)
        self.assertEqual(bootstrap.validate_rubric(rubric), [])

        with tempfile.TemporaryDirectory(
            prefix="review-toolchain-integration-"
        ) as temporary:
            fixture = Path(temporary)
            target = fixture / "repo" / "AGENTS.md"
            target.parent.mkdir(parents=True)
            target.write_text("Fixture-only instructions.\n", encoding="utf-8")
            packet = bootstrap.complete_packet(
                target=target,
                client="codex",
                evidence={"source": "disposable fixture"},
            )
            self.assertEqual(bootstrap.validate_packet(packet), [])
            self.assertEqual(len(packet["rubric"]), 24)

            rejected(bool(bootstrap.validate_rubric({})), "empty rubric accepted")

            duplicate_rubric = copy.deepcopy(rubric)
            duplicate_rubric["rubric_ids"][-1] = duplicate_rubric[
                "rubric_ids"
            ][-2]
            rejected(
                bool(bootstrap.validate_rubric(duplicate_rubric)),
                "duplicate rubric ID accepted",
            )

            rejected(
                bool(bootstrap.validate_packet({})),
                "empty packet accepted",
            )

            bad_client = copy.deepcopy(packet)
            bad_client["client"] = "unknown"
            rejected(
                bool(bootstrap.validate_packet(bad_client)),
                "unknown client accepted",
            )

            missing_semantics = copy.deepcopy(packet)
            missing_semantics["client_semantics"] = {}
            rejected(
                bool(bootstrap.validate_packet(missing_semantics)),
                "missing client semantics accepted",
            )

            wrong_ids = copy.deepcopy(packet)
            wrong_ids["rubric"][-1]["id"] = "UNKNOWN-99"
            rejected(
                bool(bootstrap.validate_packet(wrong_ids)),
                "unknown rubric ID accepted",
            )

            bad_result = copy.deepcopy(packet)
            bad_result["rubric"][0]["result"] = "Maybe"
            rejected(
                bool(bootstrap.validate_packet(bad_result)),
                "invalid result accepted",
            )

            bad_confidence = copy.deepcopy(packet)
            bad_confidence["rubric"][0]["confidence"] = 2
            rejected(
                bool(bootstrap.validate_packet(bad_confidence)),
                "out-of-range confidence accepted",
            )

            missing_evidence = copy.deepcopy(packet)
            missing_evidence["rubric"][0]["evidence"] = {}
            rejected(
                bool(bootstrap.validate_packet(missing_evidence)),
                "empty evidence accepted",
            )

            bad_disposition = copy.deepcopy(packet)
            bad_disposition["rubric"][0]["disposition"] = "guess"
            rejected(
                bool(bootstrap.validate_packet(bad_disposition)),
                "invalid disposition accepted",
            )

            with self.assertRaises(bootstrap.ToolchainError):
                bootstrap.client_semantics("unknown")
            negative_cases += 1

            with self.assertRaises(bootstrap.ToolchainError):
                bootstrap.assert_within(
                    fixture / "outside.txt",
                    fixture / "inside",
                    label="fixture",
                )
            negative_cases += 1

            with self.assertRaises(bootstrap.ToolchainError):
                inventory_agents.parse_cutoff("2026-03-28T00:00:00")
            negative_cases += 1

            excluded = (
                fixture
                / "development"
                / "repo"
                / "node_modules"
                / "AGENTS.md"
            )
            rejected(
                inventory_agents.is_excluded(
                    excluded, fixture / "development" / "repo"
                ),
                "excluded dependency target accepted",
            )

            with self.assertRaises(bootstrap.ToolchainError):
                sync_execution.require_exact_counts(
                    {
                        "task_count": 16,
                        "readiness_count": 8,
                        "checkbox_count": 24,
                    }
                )
            negative_cases += 1

            alternation = fixture / "validator-alternation.json"
            alternation.write_text(
                json.dumps({"last_used": "unknown"}), encoding="utf-8"
            )
            with self.assertRaises(bootstrap.ToolchainError):
                dispatch_stage7.select_validator(alternation)
            negative_cases += 1

            failed = bootstrap.run_owned_process(
                [sys.executable, "-c", "raise SystemExit(7)"], 10
            )
            rejected(
                failed["status"] == "Fail" and failed["returncode"] == 7,
                "nonzero owned process did not fail closed",
            )

            timed_out = bootstrap.run_owned_process(
                [
                    sys.executable,
                    "-c",
                    "import time; time.sleep(2)",
                ],
                1,
            )
            rejected(
                timed_out["status"] == "Unverified"
                and timed_out["cleanup"] == "owned-process-terminated",
                "timed-out owned process was not terminated",
            )

            missing_state = fixture / "missing-alternation.json"
            selected, state = dispatch_stage7.select_validator(missing_state)
            self.assertEqual((selected, state), ("luna", None))

        self.assertGreaterEqual(negative_cases, 15)
        proof_path = os.environ.get("REVIEW_TOOLCHAIN_TEST_RESULT")
        self.assertTrue(proof_path, "bootstrap proof output was not configured")
        Path(proof_path).write_text(
            json.dumps(
                {
                    "negative_cases_passed": True,
                    "negative_case_count": negative_cases,
                    "live_targets_touched": 0,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
