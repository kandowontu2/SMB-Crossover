"""Exact32bf native Flower observer and Root-only shared-slot replay.

Default: compile/bind in memory. --run uses the existing two-file Mesen slot
and restores both files from memory. Downloads is never modified here.
"""
import argparse
from contextlib import ExitStack,contextmanager
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import probe_dkjr_flower_center176_1123 as Source
from run_mario_luigi_stock_native_1122 import OUT,R,ROM
from nightly_patch_guard_v1 import check
from mesen_session_guard_v1 import require_free_workspace
from run_stdout_mesen_1110 import run

H,Check,Head=Source.H,Source.Check,Source.Head
CANDIDATE=Source.CANDIDATE
SOURCE_SHA='1a4f6f363b34c5d2948fcfc5d07040ff550b44e4fb8cbebc9db1642a474a7118'
POLICY_SHA='11dc69eee1a158df3dbabf8cc19dbebeb6c830672168b098f4ab3caa7be25888'
SOURCE_RECEIPT='fffb3dc9a2e08b2f92b59be98d9c3ede154ac40451c933781db15105ecafc210'
NATIVE_SHA='abfc46a0f32deda1d9c59bb61c8d877f6b3bb44ecda36e0bd1a934dac31d6a51'


@contextmanager
def recipe_cache():
    # These are immutable byte-to-byte authenticators. Cache only this exact
    # invocation's already-checked inputs; no old proof graph or files expand.
    modules=(Source,Source.C,Source.C.Previous,Source.C.Previous.Previous,Source.C.Old)
    with ExitStack() as stack:
        for module in modules:
            for name in ('proposal','inverse'):
                if hasattr(module,name):
                    stack.enter_context(patch.object(module,name,lru_cache(maxsize=4)(getattr(module,name))))
        yield


def parent_image(raw):
    if H(raw)==Source.PIN:return raw,None
    import probe_special_draw_routing_1123 as Draw
    assert H(raw)==Draw.CANDIDATE and Draw.PARENT==Source.PIN
    restored=Draw.inverse(raw)
    assert H(restored)==Source.PIN and Draw.proposal(restored)[0]==raw
    return restored,dict(input_SHA256=H(raw),inverse='probe_special_draw_routing_1123.inverse',
        recovered_SHA256=Source.PIN,proof_rebased=False)


def lua(value):
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in value.items())+'}'
    if isinstance(value,(list,tuple)):return '{'+','.join(lua(v)for v in value)+'}'
    if isinstance(value,str):return json.dumps(value)
    if isinstance(value,bool):return 'true'if value else'false'
    return str(value)


def bindings(raw):
    assert H(Path(Source.__file__).read_bytes())==SOURCE_SHA and H(raw)==CANDIDATE
    bundle=Check.W.Symbols.bundle();bundle=dict(bundle,raw=raw)
    names=('PlayerStatus','GuestPowerupActive','GuestPowerupAge','InvPickupOwner','InvPickup',
        'Player1ScoreDisplay','FloateyNum_Control','Square2SoundQueue','CheatInvincible','CheatStartLevel')
    fields={name:Check.W.address(bundle,name)for name in names}
    hooks={}
    for key,name in (('head','NativeRarePlayerHeadCollisionCore'),('pickup','HandlePowerUpCollision'),
                     ('growth','GuestPowerupUpdate')):
        pc,at=Check.W.address(bundle,name),Check.W.location(bundle,name)
        hooks[key]=dict(pc=pc,offset=at-16,preimage16=raw[at:at+16].hex())
    body=Source.C.Old.Head.payload(raw)
    for pc,expected in ((0xb8f0,'ad68c0d032'),(0xa2e8,'2091a2'),(0xaf2d,'a203ce34c0')):
        expected=bytes.fromhex(expected)
        assert body[pc-0xa000:pc-0xa000+len(expected)]==expected
    return dict(fields=fields,hooks=hooks,ROM_SHA256=CANDIDATE,source_receipt=SOURCE_RECEIPT,
        source_factory_SHA256=SOURCE_SHA,source_policy_SHA256=POLICY_SHA)


DECLARATIONS='''local FF={mushroom={kind=0,target=336,ages={},seen={}},flower={kind=1,target=1248,ages={},seen={}},
 entries=0,returns=0,move_calls=0,clock_calls=0,post_collection_returns=0,grounded_returns=0}
local ffWork,ffHead,ffPickup,ffCurrent
local ffFollows,ffFrozen={},{}
'''

SUCCESS_OLD=""" if ok then assert(originalWorkGrounded>=25 and not originalWorkPending,
  'Twenty-five actual grounded original-source work returns beyond entry guard')end
"""
SUCCESS_NEW=""" if ok then assert(FF.completed and FF.mushroom.complete and FF.flower.complete
  and FF.grounded_returns>=25 and FF.horizontal_birth and gap.birth and gap.initialized
  and births['1264'] and births['1264'].motion_center==176 and not ffWork and not ffPickup,
  'Physical Mushroom and Flower,60 frozen growth clocks each,score and25 grounded original returns')end
"""

OBSERVER=r'''
local function ffR(n,i)return read(FC.fields[n]+(i or 0))end
local function ffReady()return playing and read(0x6002)==40 and ram(2,0x8fe)==2 end
local function ffPrivate(pc,bank)return mapped(pc,'nesWorkRam',bank*8192+(pc&8191))end
local function ffHook(name)local h=FC.hooks[name];return mapped(h.pc,'nesPrgRom',h.offset)end
local function ffScore()local v=0;for i=0,5 do v=v*10+ffR('Player1ScoreDisplay',i)end;return v end
local function ffSnap()
 local s=snapshot();s.power=ffR('PlayerStatus');s.source_y=ram(2,0x210);s.prior=ram(2,0x6c)
 s.held=ram(2,0x14);s.hurt=ram(2,0x68);s.native_state=read(0x1e);s.original_returns=FF.returns
 return s
end
local function ffHealthy()
 return ffReady()and read(0x764)==0 and read(0x761)==0 and read(0x75f)==2
  and ram(2,0x68)==0 and ram(2,0x6b)~=5 and ffR('CheatInvincible')==0 and ffR('CheatStartLevel')==0
end
local function ffItem(k)return k==0 and FF.mushroom or FF.flower end
local function ffActor(i)
 return {slot=i,id=read(0x17+i),flag=read(0x10+i),kind=read(0x34+i),state=read(0x1f+i),
  x=pos(0x76,0x5d,i),y=read(0xbe+i),owner=ffR('InvPickupOwner',i),stamp=ffR('InvPickup',i),Main=updates,frame=frame}
end
local function ffScan()
 for i=0,5 do if read(0x10+i)~=0 and read(0x17+i)==46 and read(0x34+i)<=1 then
  local a=ffActor(i);local p=ffItem(a.kind)
  if not p.birth then
   assert(p.head and a.x==p.target and a.state>0 and a.state&128==0,'Actual revealed rising actor after its authored head hit')
   p.birth=a
  end
  assert(p.birth.slot==i,'Same native item slot from its real birth')
  if a.owner==40 and a.stamp==252 then p.prepared=p.prepared or a end
  if a.state&128~=0 and not p.mature then
   assert(p.prepared and a.owner==40 and a.stamp==252,'Actual mature DK-owned pickup')
   p.mature=a
  end
 end end
end
local function ffToken()
 local c=emu.getState();local sp=c['cpu.sp']
 local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local m=emu.convertAddress(pc);return {pc=pc,sp=(sp+2)&255,kind=m and m.memType,address=m and m.address}
end
local function ffMatches(p,c)
 if not p or c['cpu.pc']~=p.pc or c['cpu.sp']~=p.sp then return false end
 if p.kind then local m=emu.convertAddress(p.pc)
  assert(m and m.memType==p.kind and m.address==p.address,'Actual mapped native/source return')end
 return true
end
local function ffReward(p)
 if not p.collected or p.complete or #p.ages~=60 or ffR('GuestPowerupActive')~=0 then return end
 assert(ffR('PlayerStatus')==p.kind+1 and ffScore()==p.collected.before_score+1000,'Actual completed growth tier and1000-point reward')
 p.credit=ffSnap();p.credit.before_score=p.collected.before_score;p.credit.score=ffScore();p.complete=true
 if ffCurrent==p then ffCurrent=nil end
end
local function ffFollow(pc)
 if ffFollows[pc]then return end;ffFollows[pc]=true
 emu.addMemoryCallback(guarded('Flower actual return',function()
  local c=emu.getState()
  if ffMatches(ffHead,c)then ffHead=nil;ffScan()end
  if ffMatches(ffPickup,c)then
   local t=ffPickup;ffPickup=nil;local p=t.item
   assert(read(0x10+t.slot)==0,'Actual native item erasure')
   p.collected={before=t.before,after=ffSnap(),slot=t.slot,kind=p.kind,erased=true,before_score=t.score,
    control=ffR('FloateyNum_Control',t.slot),cue=ffR('Square2SoundQueue')}
   assert(p.collected.after.engine==9 and p.collected.control==6 and p.collected.cue==32,'Physical native growth transition,float number and cue')
   ffCurrent=p
  end
  if ffMatches(ffWork,c)then
   local p=ffWork;ffWork=nil;assert(p.move and p.clock,'Actual original Move and Clock both returned')
   FF.returns=FF.returns+1;assert(ffHealthy(),'Healthy ordinary Easy1-1 original work')
   ffScan();ffReward(FF.mushroom);ffReward(FF.flower)
   if FF.flower.collected then FF.post_collection_returns=FF.post_collection_returns+1 end
   local grounded=FF.flower.complete and ffR('GuestPowerupActive')==0 and ffR('PlayerStatus')==2
    and read(0x0f)==8 and read(0xbd)==112 and x()>=1248 and x()<=1279 and read(0x1e)==0
    and ram(2,0x6b)==1 and ram(2,0x6c)==1 and ram(2,0x210)==127
   FF.grounded_returns=grounded and FF.grounded_returns+1 or 0
   if grounded and FF.grounded_returns==1 then FF.first_grounded=ffSnap()end
   if grounded then FF.last_grounded=ffSnap()end
   if FF.grounded_returns>=25 then
    assert(FF.mushroom.complete and FF.flower.credit and not ffCurrent and not ffPickup,'Both real growth/credit chains finished')
    assert(FF.horizontal_birth and FF.horizontal_birth.left==1408 and FF.horizontal_birth.top==208
     and gap.birth and gap.initialized and gap.birth.left==1408 and gap.initialized.box==6,'Original X1408 native admission retained')
    FF.completed=true;finish(true,'Natural Mushroom and Flower with25 grounded original movement returns')
   end
  end
 end),emu.callbackType.exec,pc)
end
emu.addMemoryCallback(guarded('Flower source entry',function()
 if not ffReady()or not active()or not ffPrivate(0xb8f0,3)then return end
 assert(not ffWork,'No nested original work');FF.entries=FF.entries+1;ffWork=ffToken();ffFollow(ffWork.pc)
end),emu.callbackType.exec,0xb8f0)
emu.addMemoryCallback(guarded('Flower original Move',function()
 if ffWork and ffPrivate(0xa2e8,3)then ffWork.move=true;FF.move_calls=FF.move_calls+1 end
end),emu.callbackType.exec,0xa2e8)
emu.addMemoryCallback(guarded('Flower original Clock',function()
 if ffWork and ffPrivate(0xaf2d,3)then ffWork.clock=true;FF.clock_calls=FF.clock_calls+1 end
end),emu.callbackType.exec,0xaf2d)
emu.addMemoryCallback(guarded('Flower authored head',function()
 if not ffReady()or not ffHook('head')then return end
 local c=emu.getState();if c['cpu.a']~=193 then return end
 local left=ram(2,0x42)+camera();if left~=336 and left~=1248 then return end
 local k=left==336 and 0 or 1;local p=ffItem(k)
 assert(not p.head and ffR('PlayerStatus')==k and ram(2,0x43)==144 and ram(2,0x45)==159
  and ram(2,0x6b)==4,'Original accepted underside and actual authored question core')
 if k==1 then assert(FF.mushroom.complete,'Naturally earned Mushroom precedes Flower')end
 p.head=ffSnap();p.head.tile=c['cpu.a'];p.head.cell={left,144,left+15,159}
 assert(not ffHead,'No nested native head');ffHead=ffToken();ffFollow(ffHead.pc)
end),emu.callbackType.exec,FC.hooks.head.pc)
emu.addMemoryCallback(guarded('Flower real pickup',function()
 if not ffReady()or not ffHook('pickup')then return end
 local c=emu.getState();local i=c['cpu.x'];if i>5 or read(0x10+i)==0 or read(0x17+i)~=46 or read(0x34+i)>1 then return end
 ffScan();local a=ffActor(i);local p=ffItem(a.kind)
 assert(p.head and p.birth and p.mature and p.prepared and p.birth.slot==i and p.mature.slot==i
  and a.state&128~=0 and a.owner==40 and a.stamp==252 and not p.collected,'Physical same-slot mature prepared collector')
 assert(not ffPickup and not ffCurrent,'No nested pickup/growth')
 ffPickup=ffToken();ffPickup.item=p;ffPickup.slot=i;ffPickup.before=ffSnap();ffPickup.score=ffScore();ffFollow(ffPickup.pc)
end),emu.callbackType.exec,FC.hooks.pickup.pc)
emu.addMemoryCallback(guarded('Flower original freeze',function()
 if not ffReady()or not ffHook('growth')or not ffCurrent or ffR('GuestPowerupActive')==0 then return end
 local p=ffCurrent;local age=ffR('GuestPowerupAge');local key=tostring(age)
 assert(age>=0 and age<60 and not p.seen[key],'Each actual growth age exactly once')
 p.seen[key]=true;p.ages[#p.ages+1]=age
 local b={};for at=0,2047 do b[#b+1]=string.char(ram(2,at))end;local value=table.concat(b)
 if not ffFrozen[p.kind]then ffFrozen[p.kind]=value end
 assert(ffFrozen[p.kind]==value,'Complete original2KB state frozen during real native growth')
end),emu.callbackType.exec,FC.hooks.growth.pc)
emu.addMemoryCallback(guarded('Flower original horizontal admission',function()
 if not ffReady()or not active()or not ffPrivate(0xd1f0,2)or ram(2,0x8fd)~=10 then return end
 local i=emu.getState()['cpu.x'];if i>5 or read(0x17+i)~=40 then return end
 local left,top=pos(0x76,0x5d,i),read(0xbe+i)
 assert(not FF.horizontal_birth and left==1408 and top==208 and read(0x10+i)==1 and read(0x646+i)==6
  and left-camera()>=256 and left-camera()<=287,'Actual original horizontal constructor and box')
 FF.horizontal_birth={slot=i,left=left,center=1432,top=top,box=6,camera=camera(),Main=updates,frame=frame,ordinal=10}
end),emu.callbackType.exec,0xd1f0)
'''


def controller(raw):
    q=bindings(raw);base=Source.controller(raw);assert H(base.encode())==POLICY_SHA
    text=Check.Replay.one(base,SUCCESS_OLD,SUCCESS_NEW)
    receipt_marker='events=events,flag_recovery='
    text=Check.Replay.one(text,receipt_marker,'events=events,flower=FF,flag_recovery=')
    marker="emu.addMemoryCallback(guarded('main',function()"
    text=Check.Replay.one(text,marker,OBSERVER+marker)
    restored=Check.Replay.one(text,OBSERVER+marker,marker)
    restored=Check.Replay.one(restored,'events=events,flower=FF,flag_recovery=',receipt_marker)
    restored=Check.Replay.one(restored,SUCCESS_NEW,SUCCESS_OLD)
    assert restored==base and H(restored.encode())==POLICY_SHA
    result='local FC='+lua(q)+'\n'+DECLARATIONS+text
    Check.LuaRuntime().compile(result)
    assert not any(s in result for s in ('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    if NATIVE_SHA is not None:assert H(result.encode())==NATIVE_SHA
    return result


def main():
    ap=argparse.ArgumentParser();mode=ap.add_mutually_exclusive_group()
    mode.add_argument('--run',action='store_true');mode.add_argument('--model',action='store_true');args=ap.parse_args()
    installed=ROM.read_bytes();guard=check(ROM);parent,recovery=parent_image(installed)
    with recipe_cache():
        image,layout=Source.proposal(parent);program=controller(image).encode()
    metadata=dict(ROM_SHA256=CANDIDATE,controller_SHA256=H(program),source_factory=SOURCE_SHA,
        source_policy=POLICY_SHA,source_receipt=SOURCE_RECEIPT,parent_recovery=recovery,layout=layout,
        no_game_writes=True,source_policy_recovered_exactly=True,native_factory_SHA256=H(Path(__file__).read_bytes()),outputs=0)
    print('DK FLOWER NATIVE BINDING '+json.dumps(metadata,separators=(',',':')),flush=True)
    if args.model:
        m,opening=Head.cold(image)
        with patch.object(Check.Route.Frames,'frame',Check.normal_frame):
            result=Check.Route.route(m,image,6500,controller_text=program.decode())
        print('DK FLOWER NATIVE LUA MODEL '+json.dumps(dict(opening_Main=opening,
            actual_linked_source=True,native_Mesen=False,result=result),separators=(',',':')),flush=True)
        return int(not result['receipt']['passed'])
    if not args.run:return 0
    target,script=OUT/'candidate.nes',OUT/'controller.lua'
    assert set(OUT.iterdir())=={target,script} and not guard['matching_patch_files']
    previous_target,previous_script=target.read_bytes(),script.read_bytes()
    assert H(previous_target)in(guard['ROM_sha256'],Source.PIN)
    require_free_workspace(R,target,allow_interactive=True)
    try:
        target.write_bytes(image);script.write_bytes(program)
        private=check(target);assert private['ROM_sha256']==CANDIDATE and not private['matching_patch_files']
        result=run(script,target,OUT/'capture',CANDIDATE,320,long_no_capture=True)
        assert result['script_SHA256']==H(program) and result['outputs_written']==0 and not result['images']
        assert target.read_bytes()==image and script.read_bytes()==program and check(target)==private
        print('DK FLOWER NATIVE '+json.dumps(result,separators=(',',':')),flush=True)
        return int(not result['passed'])
    finally:
        script.write_bytes(previous_script);target.write_bytes(previous_target)
        assert set(OUT.iterdir())=={target,script} and target.read_bytes()==previous_target and script.read_bytes()==previous_script
        assert ROM.read_bytes()==installed and check(ROM)==guard


if __name__=='__main__':raise SystemExit(main())
