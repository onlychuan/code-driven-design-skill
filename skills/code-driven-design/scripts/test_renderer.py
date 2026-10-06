#!/usr/bin/env python3
"""Behavior checks; no third-party dependencies or writes into the repository."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

import render_design as design
import preserve_artifact as preserve


EXAMPLE = Path(__file__).resolve().parent.parent / "assets" / "example-card.json"


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.scene = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_portable_scene_and_xml_text_escaping(self):
        self.assertEqual(design.validate_scene(self.scene), [])
        self.scene["faces"][0]["elements"][1]["text"] = '<script>alert("x")</script> & example'
        svg = design.svg_face(self.scene,self.scene["faces"][0])
        node = ET.fromstring(svg)
        self.assertEqual(node.tag,"{http://www.w3.org/2000/svg}svg")
        self.assertNotIn("<script>",svg)
        self.assertIn("&lt;script&gt;",svg)
        preview = design.html_preview(self.scene,[svg])
        self.assertIn("default-src 'none'",preview)
        self.assertNotIn("<script>",preview)

    def test_rejects_active_links_unknown_fields_and_bad_colors(self):
        for change in ("url","unknown","color","nan"):
            scene = copy.deepcopy(self.scene)
            if change == "url":
                scene["faces"][1]["elements"][4]["url"]="javascript:alert(1)"
            elif change == "unknown":
                scene["faces"][0]["elements"][0]["onclick"]="run()"
            elif change == "color":
                scene["colors"]["accent"]["cmyk"][0] = 120
            else:
                scene["size_mm"][0] = float("nan")
            with self.subTest(change=change), self.assertRaises(design.DesignError):
                design.validate_scene(scene)

    def test_qr_structure_version_growth_and_capacity(self):
        small = design.make_qr("https://example.org/")
        large = design.make_qr("https://example.org/" + "x"*120)
        self.assertGreater(len(large),len(small))
        self.assertTrue(all(isinstance(value,bool) for row in small for value in row))
        self.assertTrue(all(small[0][col] for col in range(7)))
        self.assertFalse(small[7][7])
        self.assertTrue(small[len(small)-8][8])
        with self.assertRaises(design.DesignError):
            design.make_qr("https://example.org/" + "x"*300)

    def test_reed_solomon_parity_annuls_generator_roots(self):
        # A valid systematic RS codeword evaluates to zero at every generator
        # root. This checks the algebra independently of the encoder's matrix.
        payload = list("https://example.org/模型".encode("utf-8"))
        codeword = payload + design.parity(payload,18)
        root = 1
        for _ in range(18):
            evaluated = 0
            for byte in codeword:
                evaluated = design.gf_mul(evaluated,root) ^ byte
            self.assertEqual(evaluated,0)
            root = design.gf_mul(root,2)

    def test_determinism_overwrite_and_source_preservation(self):
        with tempfile.TemporaryDirectory(prefix="design-render-") as folder:
            out = Path(folder)/"render"
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(design.main([str(EXAMPLE),"--out",str(out)]),0)
                before = (out/"preview.html").read_bytes()
                self.assertEqual(design.main([str(EXAMPLE),"--out",str(out)]),2)
                self.assertEqual(design.main([str(EXAMPLE),"--out",str(out),"--overwrite"]),0)
                self.assertEqual((out/"preview.html").read_bytes(),before)
                original = Path(folder)/"supplied.html"
                original.write_bytes(b'<!doctype html>\r\n<meta http-equiv="Content-Security-Policy" content="default-src none"><iframe sandbox="allow-scripts" srcdoc="&lt;p&gt;test"></iframe>\xff')
                staged = Path(folder)/"publish"
                self.assertEqual(preserve.main([str(original),"--out",str(staged)]),0)
                self.assertEqual(original.read_bytes(),(staged/"index.html").read_bytes())
                self.assertEqual(preserve.main([str(original),"--out",str(staged),"--verify"]),0)
                (staged/"index.html").write_bytes(b"changed")
                self.assertEqual(preserve.main([str(original),"--out",str(staged),"--verify"]),2)


if __name__ == "__main__":
    unittest.main()
