"""Separate readonly stock route through all three authored 1-1 powerups."""

import argparse
from hashlib import sha256
import json
from multiprocessing.connection import Listener
import re
from unittest.mock import patch

import replay_karnov_ladder_fifth_1113 as Late

PIN=Late.PIN
SOURCE=Late.SOURCE.with_name('karnov_ladder_early_1113.lua')
LATE_CONTROLLER=Late.controller


def controller(raw,*,approach_x=None,carry_y=None):
    text=LATE_CONTROLLER(raw)
    start=text.index('-- Extension after the frozen four-pickup gameplay prefix.')
    end=text.index('local function control()',start)
    body=text[start:end]
    for before,after in((2400,1104),(2320,1024),(2393,1097),(2377,1081),(2464,1248),(2544,1264)):
        body=re.sub(r'\b'+str(before)+r'\b',str(after),body)
    before='  local gap=fifthGapControl(x,y,ground);if gap then return gap end'
    assert body.count(before)==1
    body=body.replace(before,'  -- The early route earns Ladder before the optional late pit.')
    source=SOURCE.read_text()
    if approach_x is not None:
        assert approach_x in(1720,1724,1728)
        source=source.replace('local EARLY_APPROACH_X=1720',f'local EARLY_APPROACH_X={approach_x}')
    if carry_y is not None:
        assert carry_y in(64,80,96,112,128)
        source=source.replace('local EARLY_CARRY_Y=80',f'local EARLY_CARRY_Y={carry_y}')
    text=text[:start]+body+source+'\n'+text[end:]
    before=' if #pickups>=4 then return fifthControl(x,y,ground,item)end'
    assert text.count(before)==1
    text=text.replace(before,' local earlyHandled,earlyPad=earlyControl(x,y,ground,item);if earlyHandled then return earlyPad end\n'+before)
    before='q.after=state()\n   if #pickups==4 then'
    assert text.count(before)==1
    text=text.replace(before,'''q.after=state()
   if #pickups==2 and q.item.x==1744 then
    q.native={sound=r('Square2SoundQueue'),popup=r('FloateyNum_Control',q.item.slot),inventory=r('InvPickup',q.item.slot)}
    assert(q.native.sound&32~=0 and q.native.popup==6 and q.native.inventory==0,'Third 1-1 native sound/popup/erasure')
    assert(q.after.cycle==1 and q.after.boots_stock==1 and q.after.owned&1~=0 and q.after.option==0,'High 1-1 flower earns original Boots')
    local realHead=false;for _,h in ipairs(early.heads)do if h.tile==193 and h.native_pad&128~=0 then realHead=true end end
    assert(realHead,'Authored high question came from real fresh-jump native head')
   end
   if #pickups==4 then''')
    Late.LuaRuntime().compile(text)
    assert all(word not in text for word in('emu.write','io.open','loadState','saveState','takeScreenshot'))
    return text


def run(raw,*,approach_x=None,carry_y=None,**kwargs):
    with patch.object(Late,'controller',lambda image:controller(image,approach_x=approach_x,carry_y=carry_y)):return Late.run(raw,**kwargs)


def sweep_high(raw,*,lower=False):
    prefix,seed=run(raw,limit=3000,checkpoint_x=1680,checkpoint_pickups=2,return_model=True)
    assert len(prefix['pickups'])==2 and prefix['source']['health']==0 and prefix['terminal']['x']==1680,prefix
    rows=[]
    for x in(1720,1724,1728):
        for y in((112,128)if lower else(64,80,96)):
            report,model=run(raw,approach_x=x,carry_y=y,input_model=Late.Native.N.fork(seed),
                history=prefix['pickups'],limit=650,stop_on_native_head=True,return_model=True)
            early=report['fifth']['early'];heads=[h for h in early['heads']if h['tile']==193 and h['native_pad']&128]
            row=dict(approach_x=x,carry_y=y,updates=report['actual_Main_NMI_updates'],
                head=heads[-1]if heads else None,terminal=report['terminal'],source=report['source'],
                controller_error=report['controller_error'],early=early)
            rows.append(row);print('KARNOV_EARLY_SWEEP '+json.dumps(row,separators=(',',':')),flush=True)
            if heads:
                return dict(passed=True,scope='Genuine two-item prefix-derived ordinary-controller head sweep; third collector and final full route pending',
                    prefix_updates=prefix['actual_Main_NMI_updates'],trials=rows,native_claim=False,
                    final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,output_files=0)
    return dict(passed=False,prefix_updates=prefix['actual_Main_NMI_updates'],trials=rows,
        final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,output_files=0)


def serve(raw,limit):
    prefix,seed=run(raw,limit=limit,checkpoint_x=1680,checkpoint_pickups=2,return_model=True)
    assert len(prefix['pickups'])==2 and prefix['source']['health']==0 and prefix['terminal']['x']==1680,prefix
    models={'seed':seed};histories={'seed':prefix['pickups']};rows=[]
    with Listener(('127.0.0.1',0),authkey=b'karnov-fifth-1113')as listener:
        print('KARNOV_EARLY_MEMORY_READY '+json.dumps(dict(port=listener.address[1],prefix_Main=prefix['actual_Main_NMI_updates'],player=prefix['terminal'],actors=prefix['actors'])),flush=True)
        while True:
            with listener.accept()as connection:
                command=connection.recv()
                if command['op']=='close':connection.send(dict(closed=True));break
                assert command['op']=='suffix'and command.get('from','seed')in models
                name=command.get('name','one');assert name in('one','two','three')
                previous=command.get('from','seed')
                report,model=run(raw,limit=min(command.get('frames',2500),3000),
                    input_model=Late.Native.N.fork(models[previous]),history=histories[previous],return_model=True)
                models[name]=model;histories[name]=report['pickups'];rows.append(dict(name=name,passed=report['passed'],updates=report['actual_Main_NMI_updates'],terminal=report['terminal']))
                connection.send(report)
    return dict(genuine_prefix_Main=prefix['actual_Main_NMI_updates'],development_forks=rows,
        final_unbroken_replay_claim=False,runtime_field_grants_or_reseeds=0,output_files=0)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--limit',type=int,default=11000)
    p.add_argument('--serve-suffix',action='store_true');p.add_argument('--require-pass',action='store_true')
    p.add_argument('--sweep-high',action='store_true')
    p.add_argument('--sweep-lower',action='store_true')
    args=p.parse_args();raw=Late.candidate()
    result=sweep_high(raw,lower=args.sweep_lower)if args.sweep_high or args.sweep_lower else serve(raw,args.limit)if args.serve_suffix else run(raw,limit=args.limit)
    print(json.dumps(result,separators=(',',':')),flush=True)
    if args.require_pass:assert result.get('passed')is True,'Complete early stock item/Ladder route did not pass'
