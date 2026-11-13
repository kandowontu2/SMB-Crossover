"""Root's serial Mini physical comparison on the strict private DK successor."""
import argparse
from hashlib import sha256
import json

import replay_mini_dkjr_direct_1113 as Replay
from nightly_patch_guard_v1 import check

Base=Replay.Base
LUA='ca91879ddf7745d10d1fb7b9199a6bfd7d1f5bd7ace490070c19fc8afdea3e8d'
PUBLIC='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--max-missed-updates',type=int)
    args=p.parse_args()
    assert check(Base.ROM)['ROM_sha256']==PUBLIC
    rom=Base.OUT/'candidate.nes'
    raw=rom.read_bytes()
    assert sha256(raw).hexdigest()==Replay.T.PIN
    text=Replay.controller(raw)
    assert sha256(text.encode()).hexdigest()==LUA
    summary=dict(ROM_SHA256=Replay.T.PIN,current_Downloads_SHA256=PUBLIC,
        Lua_SHA256=LUA,native_run=not args.metadata,private_only=True,installed=False)
    if not args.metadata:
        script=Base.OUT/'controller.lua'
        script.write_text(text,encoding='utf-8',newline='\n')
        q=Base.run(script,rom,Base.OUT/'capture',Replay.T.PIN,240)
        receipt=q['receipt']
        compact={k:receipt.get(k)for k in('passed','error','physical_frames',
            'completed_Main','source_updates','checks','cadence','full_stage',
            'terminal_native','capture_files','script_RAM_writes')}
        compact['lifts']=receipt.get('phases',{}).get('fullstage',{}).get('lifts',[])
        compact['obstacles']=receipt.get('phases',{}).get('fullstage',{}).get('actual_obstacle_clears',[])
        summary.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],
                       receipt=compact,outputs_written=q['outputs_written'])
    print(json.dumps(summary,separators=(',',':')),flush=True)
    assert check(Base.ROM)['ROM_sha256']==PUBLIC
    if not args.metadata:
        assert q['passed'],'Private Mini full route failed'
        if args.max_missed_updates is not None:
            cadence=receipt['cadence']
            assert cadence['zero_Main_frames']<=args.max_missed_updates,cadence
            assert cadence['zero_source_frames']<=args.max_missed_updates,cadence


if __name__=='__main__':main()
