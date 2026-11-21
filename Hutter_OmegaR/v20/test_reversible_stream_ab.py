from pathlib import Path
import hashlib
import random
import tempfile
import unittest
from reversible_stream_ab import MODES, transform, inverse, archive, restore, choose_mode, evaluate

class TestRealPipelineReshapes(unittest.TestCase):
    def test_exhaustive_two_byte_pairs(self):
        for n in range(0,60):
            data=bytes(((j*73+11)&255) for j in range(n))
            for i, _ in enumerate(MODES):
                self.assertEqual(inverse(transform(data,i),i),data,(i,n))

    def test_random_and_all_byte_values(self):
        rnd=random.Random(44)
        for length in (1,2,3,5,16,255,256,257,8191,65539):
            data=bytes(rnd.randrange(256) for _ in range(length))
            for i in range(len(MODES)):
                tx=transform(data,i)
                self.assertEqual(len(tx),len(data))
                self.assertEqual(inverse(tx,i),data)

    def test_roundtrip_real_container_each_mode(self):
        data=b'abacab'*900 + bytes(range(256))*4
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);inp=t/'src';inp.write_bytes(data)
            for mode in range(len(MODES)):
                output=t/f'{mode}.omr20'; recovered=t/f'{mode}.back'
                saved=archive(inp,output,283,mode)
                actual=restore(output,recovered,max_bytes=len(data))
                self.assertEqual(actual['sha256'],hashlib.sha256(data).hexdigest())
                self.assertEqual(recovered.read_bytes(),data)
                self.assertEqual(saved['archive_bytes'],output.stat().st_size)

    def test_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);p=t/'source';p.write_bytes(b'abracadabra'*53)
            z=t/'z';archive(p,z,31,2)
            bad=t/'corrupt';raw=bytearray(z.read_bytes());raw[0]^=0x20;bad.write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'BAD_MAGIC'):
                restore(bad,t/'rec',max_bytes=10_000)
            bad2=t/'truncated';bad2.write_bytes(z.read_bytes()[:-2])
            with self.assertRaises(ValueError):restore(bad2,t/'rec2',max_bytes=10_000)

    def test_training_mode_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/'fake';src.write_bytes(bytes(range(63))*39)
            x=choose_mode(src,63)
            self.assertEqual(x['train_indices'],[0,5,10,15,20,25,30,35])
            self.assertIn(x['chosen_mode'],MODES)

    def test_fail_closed_noncanonical(self):
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);p=t/'fake';p.write_bytes(b'foo bar')
            with self.assertRaisesRegex(ValueError,'REAL_STREAM_SHA_OR_SIZE_MISMATCH'):
                evaluate(p,t/'work',t/'results')

    def test_end_to_end_synthetic(self):
        data=(b'aaaaabbbcccdd'*150)+bytes(range(256))*10
        with tempfile.TemporaryDirectory() as td:
            t=Path(td);src=t/'fake';src.write_bytes(data)
            output=t/'metrics.json'
            record=evaluate(src,t/'scratch',output,chunk=183,
                expected_sha=hashlib.sha256(data).hexdigest(),expected_size=len(data))
            self.assertEqual(record['status'],'REAL_PRECODER_STREAM_DOUBLE_ROUNDTRIP')
            self.assertTrue(record['no_claim_of_hutter_admissibility'])
            self.assertIsNone(record['competition_score'])
            self.assertFalse((t/'scratch').exists())
            self.assertTrue(output.exists())
            self.assertEqual(len(record['per_block_baseline_bytes']),len(record['per_block_candidate_bytes']))

if __name__ == '__main__':unittest.main(verbosity=2)
