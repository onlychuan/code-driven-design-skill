"""Cross-format invariants, independently decoded QR symbols and source identity."""
from pathlib import Path
import contextlib
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/'skills/code-driven-design/scripts'
sys.path.insert(0,str(SCRIPTS))
import render_design as design
from test_renderer import RendererTests

try:
    import reportlab
    from pypdf import PdfReader
    from pypdf.generic import ContentStream
    import fontTools
    PDF_AVAILABLE=True
except ImportError:
    PDF_AVAILABLE=False
try:
    import zxingcpp
    from PIL import Image
    QR_AVAILABLE=True
except ImportError:
    QR_AVAILABLE=False

EXAMPLE=ROOT/'skills/code-driven-design/assets/example-card.json'

class QRDecodingTests(unittest.TestCase):
    @unittest.skipUnless(QR_AVAILABLE,'Independent QR decoder/Pillow unavailable')
    def test_decodes_payloads_across_supported_versions(self):
        payloads=['https://a.co','https://example.org/路径']+["https://example.org/"+'x'*n for n in [1,12,28,42,59,73,86,110,130]]
        sizes=set()
        for payload in payloads:
            with self.subTest(payload=payload):
                matrix=design.make_qr(payload); sizes.add(len(matrix))
                pitch=6; side=(len(matrix)+8)*pitch
                pixels=Image.new('L',(side,side),255)
                for row,values in enumerate(matrix):
                    for col,dark in enumerate(values):
                        if dark:
                            pixels.paste(0,((col+4)*pitch,(row+4)*pitch,(col+5)*pitch,(row+5)*pitch))
                result=zxingcpp.read_barcodes(pixels)
                self.assertEqual([x.text for x in result],[payload])
        self.assertGreaterEqual(len(sizes),8)

class PDFExportTests(unittest.TestCase):
    @unittest.skipUnless(PDF_AVAILABLE,'Optional PDF dependencies unavailable')
    def test_real_dimensions_outlines_process_color_and_reproducibility(self):
        scene=json.loads(EXAMPLE.read_text(encoding='utf-8'))
        # Vera ships with ReportLab; use the dependency's licensed font in tests only.
        font=Path(reportlab.__file__).parent/'fonts/Vera.ttf'
        self.assertTrue(font.is_file())
        for entry in scene['fonts'].values(): entry['path']=str(font)
        with tempfile.TemporaryDirectory(prefix='design-pdf-test-') as directory:
            base=Path(directory); source=base/'scene.json'
            source.write_text(json.dumps(scene),encoding='utf-8')
            args=[str(source),'--out',str(base/'output'),'--pdf','--outline-svg']
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(design.main(args),0)
            pdf=(base/'output/artwork.pdf').read_bytes()
            reader=PdfReader(io.BytesIO(pdf))
            self.assertEqual(len(reader.pages),2)
            for page in reader.pages:
                for box,w,h in [(page.trimbox,90,55),(page.bleedbox,96,61),(page.mediabox,106,71)]:
                    self.assertAlmostEqual(float(box.width)/design.MM_PT,w,places=3)
                    self.assertAlmostEqual(float(box.height)/design.MM_PT,h,places=3)
                operations=ContentStream(page.get_contents(),reader).operations
                self.assertFalse(any(op in [b'rg',b'RG',b'Tj',b'TJ',b'Do'] for values,op in operations))
                for values,op in operations:
                    if op in [b'k',b'K']:
                        self.assertTrue(all(0<=float(v)<=1 for v in values))
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(design.main(args+['--overwrite']),0)
            self.assertEqual((base/'output/artwork.pdf').read_bytes(),pdf)
            # Failed required-font validation must preserve an existing output.
            scene['fonts']['body']['path']=str(base/'missing.ttf')
            source.write_text(json.dumps(scene),encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(design.main(args+['--overwrite']),2)
            self.assertEqual((base/'output/artwork.pdf').read_bytes(),pdf)

if __name__=='__main__': unittest.main()
