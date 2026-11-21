from pathlib import Path
import hashlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from profile_true_stream import profile

class ProfileTests(unittest.TestCase):
    def test_exact_chunks_and_sha(self):
        data=bytes([0,1,2,7,255])*13
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'actual'; p.write_bytes(data)
            result=profile(p,17)
            self.assertEqual(result['stream_bytes'],len(data))
            self.assertEqual(result['stream_sha256'],hashlib.sha256(data).hexdigest())
            self.assertEqual([x['input_bytes'] for x in result['blocks']],[17,17,17,14])
            self.assertIsNone(result['official_hutter_score'])

    def test_empty_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'empty';p.write_bytes(b'')
            with self.assertRaisesRegex(ValueError,'empty'):
                profile(p)

    def test_zero_chunk_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bytes';p.write_bytes(b'123')
            with self.assertRaisesRegex(ValueError,'positive'):
                profile(p,0)

if __name__=='__main__': unittest.main(verbosity=2)
