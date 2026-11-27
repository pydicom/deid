#!/usr/bin/env python

import os
import shutil
import tempfile
import unittest

from deid.utils import get_installdir


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.pwd = get_installdir()
        self.deid = os.path.abspath("%s/../examples/deid/deid.dicom" % self.pwd)
        self.tmpdir = tempfile.mkdtemp()
        print("\n######################START######################")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        print("\n######################END########################")

    def test_load_deid(self):
        print("Case 1: Test loading deid directly")
        from deid.config import load_deid

        config = load_deid(self.deid)
        self.assertTrue("format" in config)

        print("Case 2: Loading from folder")
        config = load_deid(os.path.dirname(self.deid))
        self.assertTrue("format" in config)

        print("Case 3: Testing error on non-existing load of file")
        with self.assertRaises(SystemExit) as cm:
            config = load_deid(os.path.join(self.tmpdir, "deid.doesnt-exist"))
        self.assertEqual(cm.exception.code, 1)

        print("Case 4: Testing load of default deid.")
        config = load_deid(self.tmpdir)

    def test_find_deid(self):
        print("Testing finding deid file, referencing directly.")
        from deid.config.utils import find_deid

        config_file = find_deid(self.deid)
        self.assertTrue(os.path.exists(config_file))

        print("Testing finding deid file in folder")
        from deid.config.utils import find_deid

        config_file = find_deid(os.path.dirname(self.deid))
        self.assertTrue(os.path.exists(config_file))

    def test_inline_comment_values(self):
        from deid.config import load_deid

        recipe_file = os.path.join(self.tmpdir, "deid.dicom")
        for value, expected in (
            ("func:pseudonym # comment", "func:pseudonym"),
            ("var:patient_name # comment", "var:patient_name"),
            ("SYNTHETIC VALUE # comment", "SYNTHETIC VALUE"),
            ("func:pseudonym", "func:pseudonym"),
            ('"SYNTHETIC VALUE"', '"SYNTHETIC VALUE"'),
        ):
            with self.subTest(value=value):
                with open(recipe_file, "w") as recipe:
                    recipe.write("FORMAT dicom\n%header\n")
                    recipe.write("REPLACE PatientName %s\n" % value)
                    recipe.write('KEEP (0033,"SYNTHETIC PRIVATE CREATOR",1E)\n')
                actions = load_deid(recipe_file)["header"]
                self.assertEqual(actions[0]["value"], expected)
                self.assertEqual(
                    actions[1]["field"], '(0033,"SYNTHETIC PRIVATE CREATOR",1E)'
                )

    def test_hash_inside_quoted_value_is_not_comment(self):
        from deid.config import load_deid

        recipe_file = os.path.join(self.tmpdir, "quoted-hash.dicom")
        for raw, expected in (
            ('"A#B" # trailing comment', '"A#B"'),
            ("'A#B' # trailing comment", "'A#B'"),
            ('"A\\"#B" # trailing comment', '"A\\"#B"'),
            ("A#unquoted-comment", "A"),
        ):
            with self.subTest(raw=raw):
                with open(recipe_file, "w") as recipe:
                    recipe.write("FORMAT dicom\n%header\n")
                    recipe.write("REPLACE PatientName %s\n" % raw)
                self.assertEqual(load_deid(recipe_file)["header"][0]["value"], expected)

    def test_unquoted_apostrophe_does_not_hide_comment(self):
        from deid.config.utils import _remove_comments

        self.assertEqual(_remove_comments(["O'Brien", "#", "trailing"]), "O'Brien")
        self.assertEqual(
            _remove_comments(['(0033,"Name#1",1E)', "#", "trailing"]),
            '(0033,"Name#1",1E)',
        )

    def test_combined_recipes_keep_every_section(self):
        """Sections of the second and later recipes are merged, not dropped (#314)."""
        from deid.config import DeidRecipe

        base = os.path.join(self.tmpdir, "base.dicom")
        site = os.path.join(self.tmpdir, "site.dicom")
        with open(base, "w") as fh:
            fh.write(
                "FORMAT dicom\n\n"
                "%fields base_tags\nFIELD OperatorsName\n\n"
                "%labels\nADD VERSION 1\n\n"
                "%header\n\nREMOVE PatientName\nREMOVE fields:base_tags\n"
            )
        with open(site, "w") as fh:
            fh.write(
                "FORMAT dicom\n\n"
                "%fields facility_tags\nFIELD InstitutionName\nFIELD StationName\n\n"
                "%fields base_tags\nFIELD PerformingPhysicianName\n\n"
                "%values clinician_names\nFIELD ReferringPhysicianName\n\n"
                "%labels\nADD SITE B\n\n"
                "%header\n\nREMOVE fields:facility_tags\n"
                "REMOVE values:clinician_names\n"
            )
        recipe = DeidRecipe([base, site])

        fields = recipe.get_fields_lists()
        self.assertEqual(
            [x["field"] for x in fields["facility_tags"]],
            ["InstitutionName", "StationName"],
        )
        # A named list defined in both recipes gets both sets of members.
        self.assertEqual(
            [x["field"] for x in fields["base_tags"]],
            ["OperatorsName", "PerformingPhysicianName"],
        )
        self.assertEqual(
            [x["field"] for x in recipe.get_values_lists("clinician_names")],
            ["ReferringPhysicianName"],
        )
        self.assertEqual(
            [x["field"] for x in recipe.deid["labels"]], ["VERSION", "SITE"]
        )
        self.assertEqual(
            [x["field"] for x in recipe.get_actions()],
            [
                "PatientName",
                "fields:base_tags",
                "fields:facility_tags",
                "values:clinician_names",
            ],
        )

    def test_standards(self):
        from deid.config import actions, formats, sections

        print("Testing standards: default actions")
        default_actions = [
            "ADD",
            "BLANK",
            "KEEP",
            "REPLACE",
            "REMOVE",
            "JITTER",
            "LABEL",
        ]
        [self.assertTrue(x in actions) for x in default_actions]

        # Should not be any we don't know about
        unknown = [x for x in actions if x not in default_actions]
        self.assertEqual(len(unknown), 0)

        print("Testing standards: allowed sections")
        default_sections = [
            "header",
            "labels",
            "filter",
            "fields",
            "values",
        ]
        [self.assertTrue(x in sections) for x in default_sections]
        unknown = [x for x in sections if x not in default_sections]
        self.assertEqual(len(unknown), 0)

        print("Testing default formats")
        default_formats = ["dicom"]
        [self.assertTrue(x in formats) for x in default_formats]
        unknown = [x for x in formats if x not in default_formats]
        self.assertEqual(len(unknown), 0)


if __name__ == "__main__":
    unittest.main()
