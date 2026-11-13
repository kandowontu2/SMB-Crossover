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
    args=parser.parse_args()
    nightly=P.B.C.ROM
    raw=nightly.read_bytes()
    assert check(nightly)['ROM_sha256']==PARENT==sha256(raw).hexdigest()
    image,info=P.proposal_current(raw)
    assert sha256(image).hexdigest()==CANDIDATE
    assert info['all_unrelated_bytes_retained'] and info['identical_owned_byte_edits']==708
    text=P.controller(image,full=False)
    LuaRuntime().compile(text)
    summary=dict(parent_SHA256=PARENT,ROM_SHA256=CANDIDATE,
        script_SHA256=sha256(text.encode()).hexdigest(),
        actual_native_run=not args.metadata,scope='First natural mushroom; full stage is separate')
    if args.metadata:
        print(json.dumps(summary,separators=(',',':')),flush=True)
        return
    rom,script=ROOT/'candidate.nes',ROOT/'controller.lua'
    rom.write_bytes(image)
    script.write_text(text,encoding='utf-8',newline='\n')
    result=run(script,rom,ROOT/'capture',CANDIDATE,180)
    summary.update(passed=result['passed'],receipt_SHA256=result['receipt_SHA256'],
        receipt=result['receipt'],outputs_written=result['outputs_written'])
    print(json.dumps(summary,separators=(',',':')),flush=True)
    assert check(nightly)['ROM_sha256']==PARENT
    assert result['passed'],'DK Jr. first native mushroom qualification failed'


if __name__=='__main__':
    main()
