"""Separate normal-fire/terrain-aware ordinary controller after earned Bomb."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import replay_karnov_ladder_early_1113 as Frozen

PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
BASE='7d1ea719a760ac0dedb17fedde3705d5ccfdc67d1af34018efc017f859c79091'
SOURCE=Frozen.SOURCE.with_name('karnov_ladder_fire_suffix_1113.lua')


def controller(raw):
    assert sha256(raw).hexdigest()==PIN
    text=Frozen.current_controller(raw);assert sha256(text.encode()).hexdigest()==BASE
    b=dict(Frozen.Late.Native.W.Symbols.bundle(),raw=raw)
    prefix='local FIRE_CONTACT_OFFSET='+str(Frozen.Late.Native.W.location(b,'HandleEnemyFBallCol')-16)+'\n'
    point='local function mapped(pc,physical)';assert text.count(point)==1
    text=text.replace(point,SOURCE.read_text()+'\n'+point)
    point='native_blast_contacts=blastCalls,fifth=stockFifth';assert text.count(point)==1
    text=text.replace(point,point+',normal_fire=stockFifth.normal_fire')
    text=prefix+text
    assert all(word not in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    Frozen.Late.LuaRuntime().compile(text)
    return text


def cpu(raw,limit=12000):
    with patch.object(Frozen.Late,'controller',controller):q=Frozen.Late.run(raw,limit=limit)
    q['ROM_SHA256']=PIN
    q['normal_fire']=q['fifth'].get('normal_fire')
    q['receipt']={key:q['receipt'].get(key)for key in('passed','reason')}if q['receipt']else None
    q.pop('geometry',None);q.pop('actors',None)
    q['fifth']={key:q['fifth'].get(key)for key in('stage','site','art','grown','climbed','complete','restored_cells','restored_attributes')}
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cpu',action='store_true')
    p.add_argument('--limit',type=int,default=12000);args=p.parse_args()
    raw=Frozen.Late.Feature.Owner.NIGHTLY.read_bytes()
    if args.cpu:
        q=cpu(raw,args.limit);print(json.dumps(q,separators=(',',':')),flush=True);assert q['passed']
    else:
        text=controller(raw);print(json.dumps(dict(ROM_SHA256=PIN,base_SHA256=BASE,
            controller_SHA256=sha256(text.encode()).hexdigest(),bytes=len(text),Lua_compile=True,
            ROM_or_runtime_writes=0,outputs=0,Mesen_run=False)),flush=True)
