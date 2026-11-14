"""Separate bounded ordinary-B acknowledgement and enemy-range controller."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_smb2_flower_control_followup_1113 as Parent
import replay_smb2_flower_hit_followup_1113 as Aim

PIN=Parent.PIN
PARENT_SHA='f78b68e72ea531df1e0adae1f6e749e31c7fbe2db6d77fbe7434d2a872654153'
AIM_SHA='f6a6b42c825328be662acd7016ac095959315aca82a2d8077ebb8df7d2c69957'
SCOPES=('throw','hit')
OLD=" elseif natural.phase=='vegetable-throw'then\n  pad=0\n"
NEW=r''' elseif natural.phase=='vegetable-throw'then
  pad=0
  if own.S2Holding~=0 then
   assert(updates-natural.since<12,'Bounded source throw input acknowledgement')
   if own.S2Held&64==0 then pad=64
   else natural.throw_input_ack={s=s,source=own};pad=0 end
  end
'''
FRESH_OBSERVER=r'''emu.addMemoryCallback(guard(function()
 if not game or not currentHook('S2N8E05')or natural.phase~='vegetable-throw'or r('S2Holding')==0 then return end
 if r('S2Fresh')&64~=0 then natural.throw_fresh={s=state(),source=sourceState()}end
end),emu.callbackType.exec,F.S2N8E05)
'''


def controller(raw,variant=0,scope='throw'):
    assert sha256(raw).hexdigest()==PIN and scope in SCOPES and 0<=variant<8
    assert sha256(Path(Parent.__file__).read_bytes()).hexdigest()==PARENT_SHA
    assert sha256(Path(Aim.__file__).read_bytes()).hexdigest()==AIM_SHA
    before=Aim.controller(raw,variant)if scope=='hit'else Parent.controller(raw,variant,'throw')
    W=Parent.Frozen.Flower.Parent.Root.Base.W;b=dict(W.Symbols.bundle(),raw=raw)
    at=W.location(b,'S2N8E05');pc=W.address(b,'S2N8E05')
    assert raw[at:at+3]==b'\x2c'+W.address(b,'S2Fresh').to_bytes(2,'little')
    field='S2N8E05='+str(pc)+','
    hook='S2N8E05={offset='+str(at-16)+',hex="'+raw[at:at+12].hex()+'"},'
    assert before.count(OLD)==before.count('local F={')==before.count('local itemHooks={')==1
    marker='local function drive()';assert before.count(marker)==1
    text=before.replace(OLD,NEW).replace('local F={','local F={'+field)
    text=text.replace('local itemHooks={','local itemHooks={'+hook).replace(marker,FRESH_OBSERVER+marker)
    old_range="elseif own.S2VX<8 and r('S2Face')==1"
    new_range="elseif a.x-s.x<=40 and own.S2VX<8 and r('S2Face')==1"
    if scope=='hit':
        assert text.count(old_range)==1;text=text.replace(old_range,new_range)
    reversed_text=text.replace(NEW,OLD).replace('local F={'+field,'local F={')
    reversed_text=reversed_text.replace('local itemHooks={'+hook,'local itemHooks={').replace(FRESH_OBSERVER,'')
    if scope=='hit':reversed_text=reversed_text.replace(new_range,old_range)
    assert reversed_text==before
    Parent.Frozen.Flower.Parent.Root.Base.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_run(raw,variant=0,scope='throw',limit=1500):
    Base=Parent.Frozen.Flower.Parent.Root.Base
    runtime=Base.LuaRuntime
    def bounded_runtime(*args,**kwargs):
        lua=runtime(*args,**kwargs);lua.globals().CPU_FLOWER_MAIN_LIMIT=limit-2;return lua
    with patch.object(Parent.OldReplay,'controller',lambda image,v,mode:controller(image,v,scope)),\
        patch.object(Parent.Runner,'PIN',PIN),patch.object(Base,'LuaRuntime',bounded_runtime):
        q=Parent.Runner.run_controller(raw,variant,'ack-followup-'+scope,limit)
    result=Parent.Frozen.Flower.compact(q)
    natural=(q['receipt']or{}).get('natural',{})
    result['throw_fresh']=natural.get('throw_fresh');result['throw_input_ack']=natural.get('throw_input_ack')
    if result['passed']:
        assert result['throw_fresh']and result['throw_fresh']['source']['S2Fresh']&64
        assert result['throw_fresh']['source']['S2Holding']!=0
    return result


def metadata(raw,variant=0,scope='throw'):
    text=controller(raw,variant,scope)
    return dict(ROM_SHA256=PIN,variant=variant,scope=scope,controller_SHA256=sha256(text.encode()).hexdigest(),
        B_hold_until_source_ack_max_updates=12,release_on_ack=True,
        original_assertions_bounds_exact=True,new_readonly_freshB_observer=True,
        extra_hit_control=None if scope=='throw'else'Wait for forward gap<=40 before low-arc throw; existing odd-family range',
        game_changes=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--scope',choices=SCOPES,default='throw')
    p.add_argument('--cpu',action='store_true');p.add_argument('--limit',type=int,default=1500)
    args=p.parse_args();raw=Parent.Frozen.C.Owner.NIGHTLY.read_bytes()
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant,args.scope,args.limit)if args.cpu else metadata(raw,variant,args.scope)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Acknowledged controls must retain original scope assertions'
