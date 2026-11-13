"""Unmodified-ROM native regressions for the exact private Steve update."""
import argparse
from hashlib import sha256
import json

import steve_armor_idle_1113 as Idle
import replay_quick_flag_jump_1113 as Quick
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Idle.Native.Packet.Entry.ROOT/'build/metal-flower-native-1112'
PINS={
    'steve_stage':'3c477bf925743d320a3e51e008f582708297a2b78f0ad19be5112bde6ba8144d',
    'jay_pickup':'b198a94852e46c85922cc065ce39a0349298aaccd42f34f8da272d7363d8e11c',
    'jay_stage':'9189a9408ea6f52778a2dc53f6206e632ec4534b9d9e4057d91b08fb3ec34e29',
    'quick_stage':'20595adf32d5b12c9e6498f8ca0ef2542a849ffcda871c919c6c5b0e3075dc12',
    'steve_pickups':'82ace2fe3ead540390e5a0eb3dd5c9003461238fba925a686fdd5aa7d9a465a6',
}


def proposal():
    raw=Idle.Native.Live.Art.D.HOST.read_bytes()
    parent=Idle.reverse(raw) if sha256(raw).hexdigest()==Idle.Native.IDLE_CANDIDATE else raw
    assert sha256(parent).hexdigest()==Idle.PARENT
    image,info=Idle.proposal(parent)
    assert sha256(image).hexdigest()==Idle.Native.IDLE_CANDIDATE
    assert Idle.reverse(image)==parent
    return image,info,parent


def controller(name,image,info,parent):
    if name=='steve_stage':text=Idle.Native.controller(image,info,mode='full_stage')
    elif name=='jay_pickup':text=Idle.Native.jay_controller(image,info,mode='pickup')
    elif name=='jay_stage':text=Idle.Native.jay_controller(image,info,mode='stage')
    elif name=='steve_pickups':
        import replay_steve_natural_pickups_1113 as Natural
        text=Natural.controller(image,info)
    else:
        assert name=='quick_stage'
        text=Quick.controller(image)
    assert sha256(text.encode()).hexdigest()==PINS[name],name
    return text


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',choices=tuple(PINS),action='append')
    parser.add_argument('--downloads',action='store_true')
    parser.add_argument('--metadata',action='store_true')
    args=parser.parse_args()
    image,info,parent=proposal()
    rom=Idle.Native.Live.Art.D.HOST if args.downloads else OUT/'candidate.nes'
    assert rom.read_bytes()==image
    if args.downloads:assert check(rom)['ROM_sha256']==Idle.Native.IDLE_CANDIDATE
    cases=args.case or list(PINS)
    for name in cases:
        text=controller(name,image,info,parent)
        if args.metadata:
            print(json.dumps(dict(case=name,script_SHA256=PINS[name],native_run=False,outputs=0)),flush=True)
            continue
        script=OUT/'controller.lua'
        script.write_text(text,encoding='utf-8',newline='\n')
        result=run(script,rom,OUT/'capture',Idle.Native.IDLE_CANDIDATE,180)
        q=result['receipt']
        print(json.dumps(dict(case=name,passed=result['passed'],ROM_SHA256=result['ROM_SHA256'],
            script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
            receipt=q,seconds=result['seconds']),sort_keys=True),flush=True)
        assert result['passed'],(name,q)
    assert rom.read_bytes()==image
    if args.downloads:assert check(rom)['ROM_sha256']==Idle.Native.IDLE_CANDIDATE


if __name__=='__main__':main()
