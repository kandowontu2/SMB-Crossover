"""Separate normal-fire/terrain-aware ordinary controller after earned Bomb."""
import argparse
from hashlib import sha256
import json
from multiprocessing.connection import Listener
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
    prefix+='local FIRE_TERRAIN_BASE='+str(Frozen.Late.Native.W.address(b,'MmSolidTerrain'))+'\n'
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


def development(raw):
    """One genuine prefix, then ordinary-input forks; never a full proof."""
    with patch.object(Frozen.Late,'controller',controller):
        prefix,seed=Frozen.Late.run(raw,limit=7000,stop_at_pickups=4,return_model=True)
    assert len(prefix['pickups'])==4 and prefix['source']['health']==0,prefix
    models={'seed':seed}
    def probe(model,limit):
        with patch.object(Frozen.Late,'controller',controller):
            return Frozen.Late.run(raw,input_model=Frozen.Late.Native.N.fork(model),history=prefix['pickups'],
                limit=limit,return_model=True)
    q,model=probe(seed,3000);models['first']=model
    print('KARNOV_FIRE_SUFFIX_DEVELOPMENT '+json.dumps(dict(prefix_Main=prefix['actual_Main_NMI_updates'],
        genuine_prefix_derived_fork=True,final_unbroken_claim=False,result=q),separators=(',',':')),flush=True)
    if q['passed']:return
    with Listener(('127.0.0.1',0),authkey=b'karnov-fire-suffix-1113')as listener:
        print('KARNOV_FIRE_SUFFIX_MEMORY_READY '+json.dumps(dict(port=listener.address[1],models=list(models))),flush=True)
        while True:
            with listener.accept()as connection:
                command=connection.recv()
                if command['op']=='close':connection.send(dict(closed=True));break
                assert command['op']=='suffix'and command.get('from','seed')in models
                assert len(models)<6
                q,m=probe(models[command.get('from','seed')],min(command.get('limit',1800),3000))
                models[command['name']]=m;connection.send(q)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cpu',action='store_true')
    p.add_argument('--limit',type=int,default=12000);p.add_argument('--develop',action='store_true');args=p.parse_args()
    raw=Frozen.Late.Feature.Owner.NIGHTLY.read_bytes()
    if args.develop:development(raw)
    elif args.cpu:
        q=cpu(raw,args.limit);print(json.dumps(q,separators=(',',':')),flush=True);assert q['passed']
    else:
        text=controller(raw);print(json.dumps(dict(ROM_SHA256=PIN,base_SHA256=BASE,
            controller_SHA256=sha256(text.encode()).hexdigest(),bytes=len(text),Lua_compile=True,
            ROM_or_runtime_writes=0,outputs=0,Mesen_run=False)),flush=True)
