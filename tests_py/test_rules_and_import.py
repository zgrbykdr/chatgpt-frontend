import unittest
from py_app.core.models import Character, Campaign
from py_app.core.modifier_engine import recalc_character
from py_app.services.txt_feat_parser import parse_feat_txt
from py_app.services.feat_mapping import apply_mappings_to_feats


class RulesEngineTests(unittest.TestCase):
    def test_improved_initiative_applies_plus_4(self):
        c = Character()
        c.abilities["DEX"]["base"] = 14
        c.featChoices.append({
            "id": "feat_improved_initiative_srd",
            "name": "Improved Initiative",
            "active": True,
            "modifiers": [{"target": "initiative", "value": 4, "bonusType": "untyped"}],
        })
        out = recalc_character(c)
        self.assertEqual(out.derived["initiative"], 6)

    def test_fatigued_penalty(self):
        c = Character()
        c.abilities["STR"]["base"] = 14
        c.abilities["DEX"]["base"] = 14
        c.effects.append({
            "name": "Fatigued",
            "active": True,
            "modifiers": [
                {"target": "ability.STR", "value": -2, "bonusType": "penalty"},
                {"target": "ability.DEX", "value": -2, "bonusType": "penalty"},
            ],
        })
        out = recalc_character(c)
        self.assertEqual(out.derived["abilities"]["STR"]["score"], 12)
        self.assertEqual(out.derived["abilities"]["DEX"]["score"], 12)

    def test_txt_import_dedup_and_source_preserve(self):
        raw = (
            "Name\tSource\tDescription\n"
            "Improved Initiative\tPHB 2000 p.96\tFast reactions\n"
            "Improved Initiative\tPHB 2000 p.96\tDuplicate\n"
            "Alertness\tMM 2003 p.12\tKeen senses\n"
        )
        parsed = parse_feat_txt(raw, "sample.txt")
        self.assertEqual(len(parsed["rows"]), 2)
        self.assertEqual(parsed["rows"][0]["source"], "PHB 2000 p.96")

    def test_txt_parser_accepts_escaped_content(self):
        raw = "Name\tSource\tDescription\nAbility Focus\tMonster Manual (3.5) (2003), p.303\tChoose one special attack."
        parsed = parse_feat_txt(raw, "inline.txt")
        self.assertEqual(len(parsed["rows"]), 1)
        self.assertEqual(parsed["rows"][0]["name"], "Ability Focus")

    def test_mapping_applies_by_name_and_source(self):
        feats = [
            {"id": "imported_ability_focus_1", "name": "Ability Focus", "source": "Monster Manual (3.5) (2003), p.303", "mappingStatus": "Unmapped"},
            {"id": "imported_ability_focus_2", "name": "Ability Focus", "source": "Monster Manual II (3e) (2002), p.18", "mappingStatus": "Unmapped"},
        ]
        mappings = [
            {
                "featName": "Ability Focus",
                "source": "Monster Manual (3.5) (2003), p.303",
                "modifiers": [{"target": "save.dc.special", "value": 2, "bonusType": "untyped"}],
                "prerequisites": [],
            }
        ]
        applied = apply_mappings_to_feats(feats, mappings)
        self.assertEqual(applied, 1)
        self.assertEqual(feats[0]["mappingStatus"], "Mapped")
        self.assertEqual(feats[1]["mappingStatus"], "Unmapped")


if __name__ == "__main__":
    unittest.main()
