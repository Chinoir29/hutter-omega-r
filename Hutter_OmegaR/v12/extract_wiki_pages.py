#!/usr/bin/env python3
"""Extract a small XML-well-formed page prefix from authenticated enwik9.

Research canary only: a rearranged/truncated subset is NOT enwik9 and no
compression size produced from it is a Hutter Prize score.
"""
from __future__ import annotations
import argparse, hashlib, json, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET

KNOWN_SIZE = 1_000_000_000
KNOWN_SHA256 = '159b85351e5f76e60cbe32e04c677847a9ecba3adc79addab6f4c6c7aa3744bc'

def checksum(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()

def make_sample(original: Path, output: Path, target: int = 800_000):
    # Only examine the opening 32 MiB; the target must be within that region.
    if not 1000 <= target <= 8 * 1024 * 1024:
        raise ValueError('target outside supported preflight range')
    with original.open('rb') as f:
        head=f.read(32*1024*1024)
    begin=head.find(b'<page>')
    if begin < 0:
        raise ValueError('Opening <page> marker not found')
    end=head.find(b'</page>',max(begin, target))
    if end < 0:
        raise ValueError('Closing </page> marker not found')
    end+=len(b'</page>')
    prefix=head[:begin]
    if b'<mediawiki' not in prefix or b'<siteinfo>' not in prefix:
        raise ValueError('Unexpected enwik9 XML prefix')
    sample=prefix+head[begin:end]+b'\n</mediawiki>\n'
    ET.fromstring(sample) # reject malformed markup and partial wiki pages
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(sample)
    return dict(sample_bytes=len(sample),sha256=hashlib.sha256(sample).hexdigest(),
                pages=sample.count(b'<page>'),requested_target=target,
                scope='XML sample rewrapped from the original; not an official Hutter score')

def self_test():
    with tempfile.TemporaryDirectory() as td:
        base=Path(td);orig=base/'source.xml';res=base/'sample.xml'
        source=b'<?xml version="1.0"?><mediawiki><siteinfo><sitename>x</sitename></siteinfo>\n'
        source+=b''.join(b'<page><title>Test</title><text>' + str(i).encode()+b'</text></page>\n' for i in range(150))
        source+=b'</mediawiki>'
        orig.write_bytes(source)
        info=make_sample(orig,res,2000)
        assert info['pages']>=1
        assert b'</mediawiki>' in res.read_bytes()
        assert checksum(res)==info['sha256']
        assert len(ET.fromstring(res.read_bytes()))>=2
        print('SELF_TEST_PASS',json.dumps(info))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--report',type=Path)
    p.add_argument('--target',type=int,default=800_000)
    p.add_argument('--self-test',action='store_true')
    args=p.parse_args()
    if args.self_test:
        self_test();return
    if not (args.source and args.out and args.report):
        p.error('--source, --out and --report required')
    if args.source.stat().st_size != KNOWN_SIZE or checksum(args.source)!=KNOWN_SHA256:
        raise SystemExit('BLOCKED: not authentic enwik9')
    data=make_sample(args.source,args.out,args.target)
    data.update(source_sha256=KNOWN_SHA256,source_bytes=KNOWN_SIZE,
                source_authenticated=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))
if __name__=='__main__':main()
