"""Private native UI budget measurement; never installs a ROM or release."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import bub_native_noops_1113 as N
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Path(__file__).resolve().parents[2]/'build/bub-empty-native-1113'
PARENT='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
PINS=dict(ui='e76d9bc4c30127f834392e9b4de0a356128fd580b64ea399abc75ba062190179',
    combined='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7')
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('ui','combined'),required=True)
    p.add_argument('--identity',choices=('0','1','both'),default='both')
    p.add_argument('--metadata',action='store_true')
    args=p.parse_args()
    assert check(NIGHTLY)['ROM_sha256']==PARENT
    raw=NIGHTLY.read_bytes();combined=args.mode=='combined'
    image,info=(N.combined_proposal if combined else N.proposal)(raw)
    assert sha256(image).hexdigest()==PINS[args.mode]
    assert (N.combined_reverse if combined else N.reverse)(image)==raw
    identities=(0,1)if args.identity=='both'else(int(args.identity),)
    if not args.metadata:
        assert OUT.is_dir() and {p.name for p in OUT.iterdir()}=={'candidate.nes','controller.lua'}
        (OUT/'candidate.nes').write_bytes(image)
    for identity in identities:
        text=N.controller(image,identity,combined=combined)
        result=dict(mode=args.mode,identity=identity,private_only=True,installed=False,
            parent_SHA256=PARENT,ROM_SHA256=PINS[args.mode],
            script_SHA256=sha256(text.encode()).hexdigest(),native_run=not args.metadata)
        if not args.metadata:
            script=OUT/'controller.lua'
            script.write_text(text,encoding='utf-8',newline='\n')
            q=run(script,OUT/'candidate.nes',OUT/'capture',PINS[args.mode],180)
            result.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],
                receipt=q['receipt'],outputs_written=q['outputs_written'])
            print(json.dumps(result,separators=(',',':')),flush=True)
            assert q['passed'],'Private budget probe failed its stated ordinary-input windows'
        else:print(json.dumps(result,separators=(',',':')),flush=True)
    assert check(NIGHTLY)['ROM_sha256']==PARENT


if __name__=='__main__':main()
