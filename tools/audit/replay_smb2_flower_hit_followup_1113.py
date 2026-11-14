"""Separate ordinary early neutral-aim control; frozen Flower routes intact."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_smb2_flower_control_followup_1113 as Parent

PIN=Parent.PIN
PARENT_SHA='f78b68e72ea531df1e0adae1f6e749e31c7fbe2db6d77fbe7434d2a872654153'
FROZEN_CONTROLLER=Parent.controller
OLD="natural.target={item=a,s=s,source=own};newPhase('vegetable-aim');pad=2;break"
NEW=r'''local clear=true
    for xx=s.x+14,a.x,8 do if solid(xx,s.y+16)or solid(xx,s.y+28)then clear=false;break end end
    if clear and r('S2Face')==1 and own.S2VX>=8 and own.S2VX<128 and own.S2Held&64==0 then
     natural.target={item=a,s=s,source=own,source_face=r('S2Face'),requested_pad=0,line_clear=true}
     newPhase('vegetable-safe-aim');pad=0;break
    end'''
SAFE_AIM=r''' elseif natural.phase=='vegetable-safe-aim'then
  pad=0
  local a=actor(natural.target.item.slot)
  if a.flag~=1 or a.id~=6 or a.state>=32 or a.x<=s.x then newPhase('vegetable-travel')
  elseif own.S2VX<8 and r('S2Face')==1 and own.S2Held&64==0 then
   natural.aim={s=s,source=own,source_face=r('S2Face'),requested_pad=64}
   newPhase('vegetable-throw');pad=64
  end
'''


def bindings(raw):
    assert sha256(raw).hexdigest()==PIN
    Parent.bindings(raw)
    W=Parent.Frozen.Flower.Parent.Root.Base.W
    b=dict(W.Symbols.bundle(),raw=raw)
    fields={n:W.address(b,n)for n in('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position',
        'Enemy_PageLoc','Enemy_Y_Position','S2Face','S2VX','S2Held','S2Fresh')}
    def operand(op,name):return bytes([op])+W.address(b,name).to_bytes(2,'little')
    windows=[]
    for name,code in(
        ('S2N8C75',b'\x29\x01'),
        ('S2N8C77',operand(0x8d,'S2Face')),
        ('S2N8E05',operand(0x2c,'S2Fresh')),
        ('S2N8E60',b'\xa9\x36'),
        ('S2N8E62',operand(0xdd,'S2ObjectType')),
        ('S2N8E66',operand(0xad,'S2VX')),
        ('S2N8E6F',b'\xc9\x08'),
        ('S2N8E8B',operand(0xb9,'S2D8DBA')),
        ('S2N8E93',operand(0x0d,'S2Face')),
        ('S2N8E96',operand(0xb9,'S2D8DB2'))):
        at=W.location(b,name);assert raw[at:at+len(code)]==code,(name,raw[at:at+len(code)].hex(),code.hex())
        windows.append(dict(name=name,file=at,hex=code.hex()))
    table=W.location(b,'S2D8DB2');assert raw[table:table+8]==bytes.fromhex('0000d030d030d030')
    ytable=W.location(b,'S2D8DBA');assert raw[ytable:ytable+4]==bytes.fromhex('180018f8')
    return dict(readonly_fields=fields,original_moving_throw_windows=windows,
        projectile_VX_table_file=table,projectile_VX_table=[0,0,208,48,208,48,208,48],
        projectile_VY_table_file=ytable,projectile_VY_table=[24,0,24,248],
        right_source_face=1,original_moving_arc_threshold=8,
        stationary_and_moving_right_vegetable_VX=48,stationary_vegetable_VY=24,moving_vegetable_VY=248,
        existing_enemy_gate='live Goomba, forward24..72, vertical<=16, source grounded',
        added_ordinary_gate='right face, clear native path, neutral deceleration then freshB below original8-unit arc threshold',
        game_changes=0,outputs=0,Mesen_run=False)


def controller(raw,variant=0,scope='hit'):
    assert scope=='hit' and 0<=variant<8
    assert sha256(Path(Parent.__file__).read_bytes()).hexdigest()==PARENT_SHA
    bound=bindings(raw);before=FROZEN_CONTROLLER(raw,variant,'hit')
    for name,at in bound['readonly_fields'].items():
        if name!='S2Face':assert name+'='+str(at)in before
    extra='S2Face='+str(bound['readonly_fields']['S2Face'])+','
    marker=" elseif natural.phase=='vegetable-aim'then"
    assert before.count(OLD)==1 and before.count('local F={')==1 and before.count(marker)==1
    text=before.replace(OLD,NEW).replace('local F={','local F={'+extra).replace(marker,SAFE_AIM+marker)
    assert text.replace('local F={'+extra,'local F={').replace(NEW,OLD).replace(SAFE_AIM,'')==before
    assert text.count("assert(updates<2600,'Finite ordinary Flower/vegetable route')")==1
    Parent.Frozen.Flower.Parent.Root.Base.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_run(raw,variant=0,limit=1500):
    with patch.object(Parent,'controller',controller):q=Parent.source_run(raw,variant,'hit',limit)
    q['parent_followup_controller_SHA256']=sha256(FROZEN_CONTROLLER(raw,variant,'hit').encode()).hexdigest()
    return q


def metadata(raw,variant=0):
    text=controller(raw,variant)
    return dict(ROM_SHA256=PIN,variant=variant,scope='hit',controller_SHA256=sha256(text.encode()).hexdigest(),
        parent_followup_controller_SHA256=sha256(FROZEN_CONTROLLER(raw,variant,'hit').encode()).hexdigest(),
        changed_controls='Early neutral aiming, preserving right face and using the original low-speed arc threshold',
        original_assertions_bounds_and_observers_exact=True,bindings=bindings(raw),outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--cpu',action='store_true');p.add_argument('--limit',type=int,default=1500)
    args=p.parse_args();raw=Parent.Frozen.C.Owner.NIGHTLY.read_bytes()
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant,args.limit)if args.cpu else metadata(raw,variant)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Separate early aim must retain all original scope assertions'
