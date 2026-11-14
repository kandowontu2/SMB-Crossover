"""Natural stock hidden1UP controller and actual CPU route; no game grants."""
import argparse
from functools import lru_cache
from hashlib import sha256
import json
from unittest.mock import patch

import compose_smb2_postbg_mirror_1113 as Post
import compose_smb2_foreground_current_1113 as Current
import bub_native_noops_1113 as Bub
import replay_smb2_variants_stage_1113 as Terrain
import replay_smb2_flower_control_followup_1113 as Settle
import check_smb2_natural_powerups_1113 as Runner
import replay_smb2_natural_powerups_1113 as OldReplay
import check_thomas_star_route_1113 as Streams

PIN=Post.CANDIDATE
W=Post.W


@lru_cache(maxsize=1)
def inputs(raw):
    assert sha256(raw).hexdigest()==PIN
    current=Post.inverse(raw);public=Current.inverse(current);base=Bub.combined_reverse(public)
    assert sha256(base).hexdigest()==Terrain.Flag.PIN
    flagged=Current.Flag.proposal(base)[0]
    mirrored=Current.Mirror.all_mirrors_proposal(flagged)[0]
    private=Current.Priority.proposal(mirrored)[0]
    assert sha256(private).hexdigest()==Terrain.FULL_PIN
    geometry=Streams.availability(raw)
    ground=geometry['areas'][0]
    hidden=next(q for q in ground['items']if q['kind']==3 and q['left']==1024 and q['top']==128)
    assert hidden['bytes']=='0683'
    b=dict(W.Symbols.bundle(),raw=raw)
    return private,b,dict(stream_SHA256=ground['stream_SHA256'],ROM_offset=ground['ROM_offset'],hidden=hidden)


LUA=r'''
local function oneupSource()
 local q={};for _,name in ipairs({'S2Health','S2MaxHealth','S2Vegetables','S2Size','S2Air','S2VX','S2VY','S2Held','S2Fresh','S2Charge','S2Life'})do q[name]=r(name)end;return q
end
local function oneupActor(slot)
 return{slot=slot,flag=read(F.Enemy_Flag+slot),id=read(F.Enemy_ID+slot),kind=read(F.PowerUpType+slot),state=read(F.Enemy_State+slot),x=read(F.Enemy_X_Position+slot)+256*read(F.Enemy_PageLoc+slot),y=read(F.Enemy_Y_Position+slot)}
end
local function oneupHook(name)
 local q=emu.convertAddress(F[name]);return q and q.memType==emu.memType.nesPrgRom and q.address==oneupHooks[name].offset
end
local function oneupPhase(name)oneup.phase=name;oneup.since=updates end
for _,h in pairs(oneupHooks)do for i=1,#h.hex,2 do assert(emu.read(h.offset+(i-1)//2,emu.memType.nesPrgRom)==tonumber(h.hex:sub(i,i+1),16),'Exact current hidden1UP hook')end end
emu.addMemoryCallback(guard(function()
 if not game or not oneupHook('S2N8CCD')then return end
 local own=oneupSource()
 if own.S2Fresh&128~=0 and own.S2VY>=128 then oneup.last_jump={s=state(),source=own}end
end),emu.callbackType.exec,F.S2N8CCD)
emu.addMemoryCallback(guard(function()
 if not game or not oneupHook('NativeRarePlayerHeadCollisionCore')then return end
 local c=emu.getState();if c['cpu.a']~=96 then return end
 local s=state();assert(s.x>=1000 and s.x<=1048,'Real authored hidden-block head location')
 assert(oneup.last_jump and updates-oneup.last_jump.s.updates<120,'Actual original fresh-A rising jump precedes head')
 assert(not oneup.head,'One genuine hidden1UP head writer')
 oneup.head={s=s,source=oneupSource(),tile=c['cpu.a'],launch=oneup.last_jump}
end),emu.callbackType.exec,F.NativeRarePlayerHeadCollisionCore)
emu.addMemoryCallback(guard(function()
 if not game or not oneupHook('S2MainPrepare')then return end
 local a=oneupActor(emu.getState()['cpu.x']);if a.kind~=3 then return end
 assert(oneup.head and a.x==1024,'Head writer precedes authored kind3 preparation')
 oneup.prepare={s=state(),source=oneupSource(),item=a}
end),emu.callbackType.exec,F.S2MainPrepare)
local pendingOneup=nil
emu.addMemoryCallback(guard(function()
 if not game or not oneupHook('S2MainPickup')then return end
 local c=emu.getState();local a=oneupActor(c['cpu.x']);if a.kind~=3 then return end
 assert(oneup.head and oneup.birth and a.state>=128 and a.flag==1 and a.id==46,'Real mature natural1UP collector')
 assert(not pendingOneup and not oneup.pickup,'Single hidden1UP collector')
 local sp=c['cpu.sp'];local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local q={s=state(),before=oneupSource(),item=a,return_pc=pc,return_sp=(sp+2)&255};pendingOneup=q
 emu.addMemoryCallback(guard(function()
  if pendingOneup~=q or emu.getState()['cpu.sp']~=q.return_sp then return end
  q.after=oneupSource();q.erased=read(F.Enemy_Flag+a.slot)==0;q.popup=read(F.FloateyNum_Control+a.slot);q.sound=r('Square2SoundQueue')
  q.lives=r('NumberofLives');q.timer=read(F.FloateyNum_Timer+a.slot)
  for _,name in ipairs({'S2Health','S2MaxHealth','S2Vegetables'})do assert(q.before[name]==q.after[name],'Native1UP preserves source HP/max/reserve')end
  assert(q.erased and q.popup==11 and q.sound==32 and q.lives==2,'Native1UP erase/SFX/popup precede delayed award')
  oneup.pickup=q;pendingOneup=nil
 end),emu.callbackType.exec,pc)
end),emu.callbackType.exec,F.S2MainPickup)
local function drive()
 local s=state();local own=oneupSource()
 assert(r('SelectedCharacter')==25 and r('S2Variant')==identity and s.ready==178,'Actual SMB2/Doki owner')
 assert(own.S2Health>0 and s.engine~=6 and s.engine~=11,'Natural1UP route remains alive')
 assert(s.lives==(oneup.award and 3 or 2)or(oneup.pickup and s.lives==3),'Only actual delayed1UP life gain')
 assert(updates<2600,'Finite natural hidden1UP route')
 if not active()then pad=0;return end
 assert(s.world==0 and s.level==0,'Unmodified authored1-1')
 if updates%60==0 then
  oneup.recent[#oneup.recent+1]={s=s,source=own,phase=oneup.phase,pad=pad,hidden=tile(1024,128)}
  if #oneup.recent>8 then table.remove(oneup.recent,1)end
 end
 if oneup.pickup then
  pad=0
  for _,name in ipairs({'S2Health','S2MaxHealth','S2Vegetables'})do assert(own[name]==oneup.pickup.before[name],'1UP keeps source stats through normal play')end
  if s.lives==3 and not oneup.award then oneup.award={s=s,source=own};oneupPhase('resume')end
  if oneup.award then
   pad=updates-oneup.award.s.updates<8 and 1 or 0
   if updates-oneup.award.s.updates>=30 then
    assert(own.S2Life==3 and s.lives==3 and oneup.head and oneup.prepare and oneup.birth,'Life gain retained without source reset')
    finish(true,'Natural hidden1UP: real head/birth/mature collector/popup0B/delayed life2to3 and30normal updates');return
   end
  end
  return
 end
 local item=nil
 for slot=0,5 do local a=oneupActor(slot)
  if a.flag==1 and a.id==46 and a.kind==3 then
   item=a
   if not oneup.birth then assert(oneup.head and oneup.prepare,'Real hidden head and preparation before birth');oneup.birth={s=s,item=a};oneupPhase('chase')end
  end
 end
 if item then pad=s.x<item.x-5 and 1 or s.x>item.x+4 and 2 or 0;return end
 if oneup.head then pad=0;return end
 if oneup.phase=='travel'then
  if s.x<976 then traversalDrive();return end
  oneupPhase('align')
 end
 if oneup.phase=='align'then
  pad=oneupSettle(1018)
  if own.S2Air==0 and s.y>=160 and math.abs(s.x-1018)<=1 and own.S2VX==0 and own.S2Held&128==0 then oneupPhase('charge');pad=4 end
 elseif oneup.phase=='charge'then
  assert(own.S2Air==0,'Real supported original Down charge');pad=4
  if own.S2Charge>=60 and own.S2Held&128==0 then
   oneup.attempts=oneup.attempts+1;oneup.request={s=s,source=own};oneupPhase('jump');pad=128
  end
 elseif oneup.phase=='jump'then
  oneup.minY=math.min(oneup.minY,s.y);pad=updates-oneup.since<60 and 128 or 0
  if updates-oneup.since>4 and own.S2Air==0 then oneup.landings=oneup.landings+1;oneupPhase('release');pad=0 end
 elseif oneup.phase=='release'then
  pad=0
  if own.S2Held&128==0 then
   assert(oneup.attempts<6,'Six original supported jumps found no native hidden head');oneupPhase('charge');pad=4
  end
 else error('Unknown hidden1UP control phase')end
end
'''


def controller(raw,variant=0):
    private,b,geometry=inputs(raw)
    text=Terrain.profile_controller(private,variant,full=True)
    assert text.count(Terrain.FULL_PIN)==1;text=text.replace(Terrain.FULL_PIN,PIN)
    once=Terrain.Frozen.Flag.Root.once
    names=('S2Variant','S2Health','S2MaxHealth','S2Vegetables','S2Size','S2Air','S2VX','S2VY',
        'S2Held','S2Fresh','S2Charge','S2Life','PowerUpType','Enemy_Y_Position','Square2SoundQueue',
        'FloateyNum_Control','FloateyNum_Timer','NativeRarePlayerHeadCollisionCore','S2MainPrepare','S2MainPickup','S2N8CCD')
    fields=','.join(n+'='+str(W.address(b,n))for n in names)+','
    text=once(text,'local F={','local F={'+fields)
    hooks=('NativeRarePlayerHeadCollisionCore','S2MainPrepare','S2MainPickup','S2N8CCD')
    literal='local oneupHooks={'+','.join(n+'={offset='+str(W.location(b,n)-16)+',hex="'+raw[W.location(b,n):W.location(b,n)+12].hex()+'"}'for n in hooks)+'}\n'
    text=literal+text
    text=once(text,'local frames,updates,pad=0,0,0',"local oneup={phase='travel',since=0,attempts=0,landings=0,minY=255,recent={}}\nlocal frames,updates,pad=0,0,0")
    text=once(text,'return_counts=returns,pipes=pipes,recent=records','return_counts=returns,pipes=pipes,recent=records,oneup=oneup')
    text=once(text,'partial_endpoint=false,full_stage=ok','partial_endpoint=true,full_stage=false,natural_oneup_only=true')
    if "string.format('%q',k)"in text:text=once(text,"string.format('%q',k)","string.format('%q',tostring(k))")
    text=once(text,'local function drive()','local function traversalDrive()')
    helper=Settle.HELPER.replace('flowerRetreatSettle','oneupSettle')
    marker='-- Observe every actual GameLoop return, including the native catch-up caller.'
    text=once(text,marker,helper+LUA+'\n'+marker)
    Settle.bindings(raw);Terrain.charge_source(raw)
    Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_run(raw,variant=0,limit=2800):
    assert sha256(raw).hexdigest()==PIN
    with patch.object(OldReplay,'controller',lambda image,v,mode:controller(image,v)),patch.object(Runner,'PIN',PIN):
        q=Runner.run_controller(raw,variant,'natural-hidden-oneup',limit)
    receipt=q.pop('receipt')or{};q['reason']=receipt.get('reason');q['all_returned_Main']=receipt.get('all_returned_Main')
    q['oneup']=receipt.get('oneup');q['physical_native_claim']=False
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--cpu',action='store_true');p.add_argument('--limit',type=int,default=2800)
    args=p.parse_args();raw=Post.Owner.NIGHTLY.read_bytes()
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant,args.limit)if args.cpu else dict(ROM_SHA256=PIN,variant=variant,controller_SHA256=sha256(controller(raw,variant).encode()).hexdigest(),geometry=inputs(raw)[2],outputs=0,Mesen_run=False)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Natural hidden1UP scope remains unqualified'
