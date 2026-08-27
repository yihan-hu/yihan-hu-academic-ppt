#!/usr/bin/env python3
import base64
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / 'scripts' / 'check-academic-pptx-hybrid.py'
PNG_1PX = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9Zl1sAAAAASUVORK5CYII='
)


class CanvaEditableFigureContractTest(unittest.TestCase):
    def make_case(self, figure_kind):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / 'fig.png').write_bytes(PNG_1PX)
        spec = {
            'meta': {
                'designSource': 'guizang-template',
                'visualStyle': 'guizang-swiss-academic',
                'pptxFidelity': 'native-first',
                'figurePolicy': 'whitelist-enforced',
            },
            'slides': [{
                'kind': 'figure',
                'layout': 'S22',
                'figureKind': figure_kind,
                'editableFigureWorkflow': 'canva-magic-layers',
                'editableFigureSource': 'fig.png',
                'canvaDesignId': 'Dabcdefghij',
                'powerPointEditabilityVerified': False,
                'elements': [{
                    'type': 'image',
                    'role': 'generated-figure',
                    'figureKind': figure_kind,
                    'figureSource': 'deterministic',
                    'path': 'fig.png',
                    'fit': 'contain',
                    'x': 0.8,
                    'y': 1.3,
                    'w': 11.0,
                    'h': 5.0,
                }],
            }],
        }
        (root / 'deck-spec.json').write_text(json.dumps(spec), encoding='utf-8')
        slide_xml = (
            '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">'
            '<p:cSld><p:spTree><p:pic></p:pic></p:spTree></p:cSld></p:sld>'
        )
        with zipfile.ZipFile(root / 'deck.pptx', 'w') as zf:
            zf.writestr('ppt/slides/slide1.xml', slide_xml)
        return temp, root

    def run_checker(self, root):
        return subprocess.run(
            [sys.executable, str(CHECKER), str(root / 'deck-spec.json'), str(root / 'deck.pptx')],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

    def test_explanatory_figure_allows_canva_companion(self):
        temp, root = self.make_case('study-design-diagram')
        self.addCleanup(temp.cleanup)
        proc = self.run_checker(root)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_quantitative_figure_rejects_canva_companion(self):
        temp, root = self.make_case('forest-plot')
        self.addCleanup(temp.cleanup)
        proc = self.run_checker(root)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('Canva Magic Layers is allowed only for non-quantitative explanatory whitelist figures', proc.stderr)


if __name__ == '__main__':
    unittest.main()
