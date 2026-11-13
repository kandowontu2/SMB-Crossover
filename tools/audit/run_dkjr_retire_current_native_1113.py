"""Root's bounded physical qualification of the granted DK Jr. successor."""
import argparse
from hashlib import sha256
import json

import compose_dkjr_helper_retire_1113 as P
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PARENT='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
CANDIDATE='e73b66263a8e150d3d21b801e5a55be1817f86d09639fc428ab809b2518842d9'
ROOT=P.B.R/'build/metal-flower-native-1112'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata',action='store_true')
    parser.add_argument('--full-frozen',action='store_true',help='Observe the frozen terrain-positive CPU controller on actual native timing.')
    parser.add_argument('--require-pass',action='store_true')
    args=parser.parse_args()
    nightly=P.B.C.ROM
    raw=nightly.read_bytes()
    assert check(nightly)['ROM_sha256']==PARENT==sha256(raw).hexdigest()
    if args.full_frozen:
        # Reuse the exact candidate already composed and physically qualified
        # for its first mushroom. No repeated source tree or candidate copy.
        image=(ROOT/'candidate.nes').read_bytes()
        assert sha256(image).hexdigest()==CANDIDATE
        text=P.controller(image,full=True,ride_fourth=False,fourth_window=True,
            ledge_wait=True,stationary_wait=True,early_stairs=True,
            riser_retreat=True,landing_prep=False)
        assert sha256(text.encode()).hexdigest()=='bd4bacd76d2584eccc1f745c6abd27c48ab39afe04764d6254438da0f4e11464'
    else:
        image,info=P.proposal_current(raw)
        assert sha256(image).hexdigest()==CANDIDATE
        assert info['all_unrelated_bytes_retained'] and info['identical_owned_byte_edits']==708
        text=P.controller(image,full=False)
    LuaRuntime().compile(text)
    summary=dict(parent_SHA256=PARENT,ROM_SHA256=CANDIDATE,
        script_SHA256=sha256(text.encode()).hexdigest(),
        actual_native_run=not args.metadata,scope='Frozen full-stage controller observation'if args.full_frozen else 'First natural mushroom; full stage is separate')
    if args.metadata:
        print(json.dumps(summary,separators=(',',':')),flush=True)
        return
    rom,script=ROOT/'candidate.nes',ROOT/'controller.lua'
    if not args.full_frozen:
        rom.write_bytes(image)
    script.write_text(text,encoding='utf-8',newline='\n')
    result=run(script,rom,ROOT/'capture',CANDIDATE,240 if args.full_frozen else 180)
    receipt=result['receipt']
    if args.full_frozen:
        receipt={key:value for key,value in receipt.items() if key!='events'}
        receipt['last_events']=result['receipt'].get('events',[])[-12:]
    summary.update(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
        receipt=receipt,outputs_written=result['outputs_written'])
    print(json.dumps(summary,separators=(',',':')),flush=True)
    assert check(nightly)['ROM_sha256']==PARENT
    if not args.full_frozen or args.require_pass:
        assert result['passed'],'DK Jr. native qualification failed'


if __name__=='__main__':
    main()
