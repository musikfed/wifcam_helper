"""Hardware-free tests for the T23N minimal IMG tool."""
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lenya-image.py"

def fixture(extra=0, second_type=0x83):
    img = bytearray(40 * 512 + extra)
    img[510:512] = b"\x55\xaa"
    for index,(typ,start,sectors) in enumerate(((0x0e,1,6),(second_type,7,33))):
        offset=446+index*16
        struct.pack_into("<B",img,offset+4,typ)
        struct.pack_into("<II",img,offset+8,start,sectors)
    img[512+54:512+59] = b"FAT16"
    img[512+510:512+512] = b"\x55\xaa"
    ext=7*512+1024+56
    img[ext:ext+2] = b"\x53\xef"
    return bytes(img)

class TestLenyaImage(unittest.TestCase):
    def invoke(self,*args):
        return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],
                              text=True,capture_output=True)
    def test_valid_img(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ok.img";p.write_bytes(fixture())
            r=self.invoke(p)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue(json.loads(r.stdout)["already_compact"])
    def test_safe_compaction(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"full.img";q=Path(d)/"small.img"
            raw=fixture(4096);p.write_bytes(raw)
            r=self.invoke(p,"--compact-to",q)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(q.read_bytes(),raw[:40*512])
            self.assertEqual(p.read_bytes(),raw)
            self.assertNotEqual(self.invoke(p,"--compact-to",q).returncode,0)
    def test_zip_input(self):
        with tempfile.TemporaryDirectory() as d:
            z=Path(d)/"camera.zip"
            with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as a:
                a.writestr("camera/sd.img",fixture())
            self.assertEqual(self.invoke(z).returncode,0)
    def test_reject_gpt(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.img";p.write_bytes(fixture(second_type=0xee))
            self.assertNotEqual(self.invoke(p).returncode,0)

if __name__=="__main__":
    unittest.main()
