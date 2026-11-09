"""Enumerate the exact current MMC5 menu through its compiled input owner."""

import argparse
import json
from pathlib import Path

from inventory_playable_menu_1101_v3 import M, R, menu_name, sha
from prepare_mini_mario_native_power_1103_v56 import bundle


ROM=R/'build/mini-box-terrain-visible-1110/candidate.nes'
PIN='6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'
MISSING={'sonic':('SONIC',),'donkey_kong_jr':('DK JR','DONKEY KONG JR'),
         'getsu_fuma':('GETSU FUMA','GETSU FUUMA'),'mega_giant_mario':('GIANT MARIO',),
         'jay_mccray':('JAY MCCRAY',),'steve_hermann':('STEVE HERMANN',)}


def press(m,key):
    M.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
    M.invoke(m,'CrossoverMenuInput')


def inventory(raw):
    b=bundle(raw)
    seed=M.fresh(b)
    M.put(seed,CrossoverMenuState=2)
    pending=[0]
    slots={}
    while pending:
        slot=pending.pop()
        if slot in slots:
            continue
        assert 0<=slot<64
        start=M.fork(seed)
        M.put(start,CrossoverMenuIndex=slot)
        M.invoke(start,'MenuResolveCharacter')
        M.invoke(start,'QueueSelection')
        for key in (1,2,4,8):
            trial=M.fork(start)
            press(trial,key)
            pending.append(M.get(trial,'CrossoverMenuIndex'))
        rows={}
        for cycle in range(32):
            name,tiles=menu_name(start)
            assert name,(slot,cycle)
            raw_id=M.get(start,'SelectedCharacter')
            signature=raw_id,tuple(tiles)
            if signature in rows:
                break
            starts=[]
            for key in (16,128):
                trial=M.fork(start)
                press(trial,key)
                starts.append(M.get(trial,'CrossoverMenuState')==0)
            assert starts[0]==starts[1],(slot,cycle,name,starts)
            rows[signature]=dict(slot=slot,cycle=cycle,raw=raw_id,name=name,confirm=starts[0])
            press(start,32)
        else:
            raise AssertionError(('Named Select cycle exceeded bound',slot))
        slots[slot]=list(rows.values())
    assert set(slots)==set(range(32))
    entries=[row for slot in sorted(slots) for row in slots[slot]]
    names={r['name'] for r in entries}
    absent=[key for key,aliases in MISSING.items() if not any(alias in name for alias in aliases for name in names)]
    locked=[r for r in entries if not r['confirm']]
    assert len(entries)==94 and len(locked)==1 and 'PRINCE' in locked[0]['name'],(len(entries),locked)
    assert set(absent)==set(MISSING)
    return dict(slots=len(slots),displayed=len(entries),confirmable=len(entries)-len(locked),
                requested_absent=absent,displayed_locked=locked,rows=entries)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert sha(ROM)==PIN
    q=dict(passed=True,ROM_sha256=PIN,**inventory(ROM.read_bytes()),
           scope='Actual 32-slot direction graph, emitted display names, Select cycles and A/Start. CPU only.')
    args.output.mkdir(exist_ok=True)
    (args.output/'exact-roster.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k!='rows'}))


if __name__=='__main__':
    main()
