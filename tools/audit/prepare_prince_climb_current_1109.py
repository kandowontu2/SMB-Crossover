"""Replay the controller-only first pipe with the funded Prince ledge worker."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from observe_chip_committed_write import lua
from prepare_prince_climb_trace_1108 import ALIGN_TRACE
from prepare_prince_resume_1108 import BODY, FIRST_PIPE, LEGACY, NIGHTLY
from prepare_selected_native_packet_v1 import R, prepare, sha

BASE = R/'build/mini-parser-lift-1109/candidate.nes'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--jump-gap',type=int,default=86)
    args=parser.parse_args()
    proof=json.loads(args.proof.read_text())
    assert proof['passed'] and proof['parent_SHA256']==sha(BASE)==sha(NIGHTLY)
    assert proof['full_Mini_payload_and_all_nonpatch_bytes_exact']
    assert proof['climb']['projected_native_climb_exit_center']==452
    for path,digest in proof['bindings'].items():
        assert sha(R/path)==digest,path
    original=BASE.read_bytes()
    raw=bytearray(original)
    written=set()
    for row in proof['patches']:
        at=row['offset']
        before,after=(bytes.fromhex(row[key]) for key in ('preimage','replacement'))
        claimed=range(at,at+len(before))
        assert len(before)==len(after) and raw[at:at+len(before)]==before,hex(at)
        assert written.isdisjoint(claimed),hex(at)
        raw[at:at+len(before)]=after
        written.update(claimed)
    mini=slice(1048592+962*1024,1048592+969*1024)
    assert raw[mini]==original[mini]
    args.output.mkdir()
    rom=args.output/'prince-private.nes'
    rom.write_bytes(raw)
    assert sha(rom)==proof['expected_memory_only_SHA256']
    labels=Path(json.loads((BODY/'candidate.json').read_text())['candidate'])
    assert sha(labels)==LEGACY
    for suffix in ('.dbg','.lbl'):
        shutil.copyfile(labels.with_suffix(suffix),rom.with_suffix(suffix))
    body=FIRST_PIPE.read_text()
    assert body.count(LEGACY)==body.count('enemy.gap<=96')==1
    body=body.replace(LEGACY,sha(rom)).replace('enemy.gap<=96',f'enemy.gap<={args.jump_gap}')
    body,n=re.subn(r'^Q\.cookie=\{[\d,]+\}$','Q.cookie='+lua(list(bytes.fromhex(proof['Prince_cookie']))),body,flags=re.M)
    assert n==1 and 'emu.write(' not in body
    anchor='local function controls_tick(finish)'
    assert body.count(anchor)==1
    body=body.replace(anchor,ALIGN_TRACE+'\n'+anchor)
    packet=args.output/'native'
    prepare(packet,rom,body,[Path(__file__),BASE,NIGHTLY,FIRST_PIPE,args.proof],expected=sha(rom),
            timeout=150,allow_interactive=True,
            scope='Private Prince cold launch and controller-only first pipe, with source ledge and landing observations.')
    return subprocess.call([sys.executable,'-B',packet/'run.py'])


if __name__=='__main__':
    raise SystemExit(main())
