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
ROUTE_PINS={
    ('full11',0):'1c764ce0e76923816e6d0d1a079ab6b8549ebfefd41cda00764fc9fa5c2f059b',
    ('full11',1):'1d60813d2910cd143ea73e2783c578c428fdbcd0354420d03b2ce3b236daac86',
    ('mushroom',0):'f848ad7065ecf9a026eeb98b4cc9d12c88231afcadf53bbe6a6d4fc55194c3eb',
    ('mushroom',1):'e631b0e6c42825f4ba608a3fb6f166213ed3680f8a592e4f975c7ed65163b2a5',
}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=('ui','combined'),required=True)
    p.add_argument('--identity',choices=('0','1','both'),default='both')
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--route',choices=('cadence','full11','mushroom'),default='cadence')
    p.add_argument('--downloads',action='store_true',help='Explicit actual installed-f88 launch; normalize through its exact known inverse for source binding.')
    args=p.parse_args()
    expected_installed=PINS['combined'] if args.downloads else PARENT
    assert check(NIGHTLY)['ROM_sha256']==expected_installed
    raw=NIGHTLY.read_bytes();combined=args.mode=='combined'
    if args.downloads:
        assert combined
        raw=N.combined_reverse(raw)
        assert sha256(raw).hexdigest()==PARENT
    assert args.route=='cadence' or combined,'Route qualification uses the explicit combined candidate'
    image,info=(N.combined_proposal if combined else N.proposal)(raw)
    assert sha256(image).hexdigest()==PINS[args.mode]
    assert (N.combined_reverse if combined else N.reverse)(image)==raw
    identities=(0,1)if args.identity=='both'else(int(args.identity),)
    if not args.metadata and not args.downloads:
        assert OUT.is_dir() and {p.name for p in OUT.iterdir()}=={'candidate.nes','controller.lua'}
        (OUT/'candidate.nes').write_bytes(image)
    for identity in identities:
        text=N.controller(image,identity,combined=combined)
        if args.route!='cadence':
            import replay_bub_combined_route_1113 as Route
            text=Route.controller(image,identity,args.route)
            assert sha256(text.encode()).hexdigest()==ROUTE_PINS[(args.route,identity)]
        result=dict(mode=args.mode,identity=identity,route=args.route,private_only=not args.downloads,installed=args.downloads,
            launch_context='actual Downloads'if args.downloads else'private candidate',
            parent_SHA256=PARENT,ROM_SHA256=PINS[args.mode],
            script_SHA256=sha256(text.encode()).hexdigest(),native_run=not args.metadata)
        if not args.metadata:
            script=OUT/'controller.lua'
            script.write_text(text,encoding='utf-8',newline='\n')
            launch=NIGHTLY if args.downloads else OUT/'candidate.nes'
            assert launch.read_bytes()==image
            q=run(script,launch,OUT/'capture',PINS[args.mode],240 if args.route=='full11' else 180)
            result.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],
                receipt=q['receipt'],outputs_written=q['outputs_written'])
            print(json.dumps(result,separators=(',',':')),flush=True)
            assert q['passed'],'Private budget probe failed its stated ordinary-input windows'
        else:print(json.dumps(result,separators=(',',':')),flush=True)
    assert check(NIGHTLY)['ROM_sha256']==expected_installed


if __name__=='__main__':main()
