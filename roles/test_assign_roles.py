"""Small integration checks for the trained role model."""

import copy
import json
import unittest
from pathlib import Path

from common.format import check_format
from roles.assign_roles import DEFAULT_MODEL, _pairwise_probabilities, assign_roles


ROOT = Path(__file__).resolve().parents[1]


class AssignRolesTest(unittest.TestCase):
    def test_pairwise_probabilities_are_complementary(self):
        probabilities = _pairwise_probabilities([0.8, 0.3])
        self.assertAlmostEqual(sum(probabilities), 1.0)
        self.assertGreater(probabilities[0], 0.5)

    @unittest.skipUnless(DEFAULT_MODEL.exists(), "Eğitilmiş yerel model bulunamadı")
    def test_example_dialogue(self):
        source = json.loads(
            (ROOT / "common" / "ornek_diyalog.json").read_text(encoding="utf-8")
        )
        result = assign_roles(copy.deepcopy(source))
        self.assertTrue(check_format(result))
        roles_by_speaker = {}
        for segment in result["segments"]:
            roles_by_speaker.setdefault(segment["speaker"], segment["role"])
            self.assertEqual(roles_by_speaker[segment["speaker"]], segment["role"])
        self.assertEqual(roles_by_speaker, {"A": "Doctor", "B": "Patient"})

    @unittest.skipUnless(DEFAULT_MODEL.exists(), "Eğitilmiş yerel model bulunamadı")
    def test_person1_asr_example(self):
        source = json.loads(
            (ROOT / "asr" / "asr_001.json").read_text(encoding="utf-8")
        )
        result = assign_roles(copy.deepcopy(source))
        self.assertTrue(check_format(result))
        roles_by_speaker = {
            segment["speaker"]: segment["role"] for segment in result["segments"]
        }
        # Person 1's README identifies SPEAKER_00 as the clinician.
        self.assertEqual(
            roles_by_speaker,
            {"SPEAKER_00": "Doctor", "SPEAKER_01": "Patient"},
        )


if __name__ == "__main__":
    unittest.main()
