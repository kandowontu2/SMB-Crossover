"""Authored1-1 Star route on exact421379; original native admission only."""
import argparse
from hashlib import sha256
import json
from unittest.mock import patch

import compose_smb2_hidden_response_1114 as C
import replay_smb2_hidden_oneup_1113 as Frozen


def geometry(raw):
    ground=Frozen.Streams.availability(raw)['areas'][0]
    star=next(q for q in ground['items']if q['kind']==6 and(q['left'],q['top'])==(1616,144))
    assert star['bytes']
    return dict(area='1-1',stream_SHA256=ground['stream_SHA256'],ROM_offset=ground['ROM_offset'],
        authored_stream_kind6=star,runtime_PowerUpType=2,position_units='world pixel left/top')


def controller(raw,variant=0):
    public=C.Cache.public_image(C.inverse(raw));geometry(raw)
    text=Frozen.controller(public,variant);once=Frozen.Terrain.Frozen.Flag.Root.once
    lua=Frozen.LUA
    lua=once(lua,"'S2Charge','S2Life'","'S2Charge','S2Life','S2Star','StarInvincibleTimer','AreaMusicQueue'")
    lua=once(lua,"local c=emu.getState();if c['cpu.a']~=96 then return end",
        "local c=emu.getState();if state().x<1592 or state().x>1640 or r('S2HeadX')+256*r('S2HeadPage')~=1616 or r('S2HeadY')~=144 then return end")
    lua=once(lua,"s.x>=1000 and s.x<=1048","s.x>=1592 and s.x<=1640")
    lua=lua.replace('a.kind~=3','a.kind~=2').replace('a.kind==3','a.kind==2')
    lua=once(lua,"a.x==1024","a.x==1616")
    begin=lua.index('local pendingOneup=nil');end=lua.index('local function drive()',begin)
    lua=lua[:begin]+r'''local pendingOneup=nil
emu.addMemoryCallback(guard(function()
 if not game or not oneupHook('S2MainPickup')then return end
 local c=emu.getState();local a=oneupActor(c['cpu.x']);if a.kind~=2 then return end
 assert(oneup.head and oneup.birth and a.flag==1 and a.id==46,'Real native Star collector admission')
 assert(not pendingOneup and not oneup.pickup,'Single natural Star collector')
 local sp=c['cpu.sp'];local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local q={s=state(),before=oneupSource(),item=a,return_pc=pc,return_sp=(sp+2)&255};pendingOneup=q
 emu.addMemoryCallback(guard(function()
  if pendingOneup~=q or emu.getState()['cpu.sp']~=q.return_sp then return end
  q.after=oneupSource();q.erased=read(F.Enemy_Flag+a.slot)==0;q.popup=read(F.FloateyNum_Control+a.slot);q.sound=r('Square2SoundQueue')
  q.lives=r('NumberofLives');q.star=r('StarInvincibleTimer');q.music=r('AreaMusicQueue')
  for _,name in ipairs({'S2Health','S2MaxHealth','S2Vegetables'})do assert(q.before[name]==q.after[name],'Native Star preserves source HP/max/reserve')end
  assert(q.before.StarInvincibleTimer==0 and q.erased and q.popup==6 and q.sound==32 and q.lives==2,'Natural Star erase/SFX/popup/lives')
  assert(q.star==35 and q.music==64,'Original Star timer and music grant')
  oneup.pickup=q;pendingOneup=nil;oneupPhase('resume')
 end),emu.callbackType.exec,pc)
end),emu.callbackType.exec,F.S2MainPickup)
''' +lua[end:]
    lua=once(lua,"s.lives==(oneup.award and 3 or 2)or(oneup.pickup and s.lives==3)","s.lives==2")
    begin=lua.index(' if oneup.pickup then');end=lua.index(' local item=nil',begin)
    lua=lua[:begin]+r''' if oneup.pickup then
  pad=0
  for _,name in ipairs({'S2Health','S2MaxHealth','S2Vegetables'})do assert(own[name]==oneup.pickup.before[name],'Star retains source stats through normal play')end
  if updates>=oneup.pickup.s.updates+2 then
   assert(own.S2Star>0 and own.StarInvincibleTimer>0,'Actual Star imported by original source movement')
   if not oneup.imported then oneup.imported={s=s,source=own}end
  end
  if updates-oneup.pickup.s.updates>=31 then
   assert(own.S2Life==2 and s.lives==2 and oneup.head and oneup.prepare and oneup.birth,'Natural Star retained after30 normal updates')
   finish(true,'Natural Star: authored head/birth/native collector/popup6/timer35/music64/source import and30normal updates');return
  end
  return
 end
''' +lua[end:]
    lua=once(lua,'if s.x<976 then','if s.x<1568 then')
    lua=once(lua,"if own.S2Charge>=60 and own.S2Held&128==0 then","if own.S2Held&128==0 then")
    lua=once(lua,'if item then pad=s.x<item.x-5 and 1 or s.x>item.x+4 and 2 or 0;return end',r'''if item then
  pad=s.x<item.x-5 and 1 or s.x>item.x+4 and 2 or 0
  if own.S2Air==0 and own.S2Held&128==0 then
   for slot=0,5 do
    local a=oneupActor(slot)
    if a.flag==1 and a.id<21 and a.state<32 and math.abs(a.x-s.x)<48 then oneup.evade=updates;break end
   end
  end
  if oneup.evade and updates-oneup.evade<24 then pad=pad|128 end
  return
 end''')
    lua=lua.replace('1018','1610').replace('tile(1024,128)','tile(1616,144)')
    lua=lua.replace('hidden1UP','Star').replace('kind3','kind2').replace('1UP','Star')
    text=once(text,Frozen.LUA,lua)
    text=once(text,Frozen.PIN,C.CANDIDATE)
    b=dict(C.W.Symbols.bundle(),raw=raw)
    extra=','.join(n+'='+str(C.W.address(b,n))for n in('S2Star','StarInvincibleTimer','AreaMusicQueue','S2HeadX','S2HeadPage','S2HeadY'))
    text=once(text,'local F={','local F={'+extra+',')
    text=text.replace('oneup','star')
    Frozen.Terrain.Frozen.Flag.Root.Base.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text


def source_run(raw,variant=0,limit=3400):
    assert sha256(raw).hexdigest()==C.CANDIDATE
    with patch.object(Frozen.OldReplay,'controller',lambda image,v,mode:controller(image,v)),patch.object(Frozen.Runner,'PIN',C.CANDIDATE):
        q=Frozen.Runner.run_controller(raw,variant,'natural-star',limit)
    receipt=q.pop('receipt')or{}
    q.update(reason=receipt.get('reason'),all_returned_Main=receipt.get('all_returned_Main'),
        star=receipt.get('star'),geometry=geometry(raw),physical_native_claim=False)
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',choices=tuple(map(str,range(8)))+('all',),default='0')
    p.add_argument('--cpu',action='store_true');args=p.parse_args();raw=C.load_current_image()
    for variant in(range(8)if args.variant=='all'else(int(args.variant),)):
        q=source_run(raw,variant)if args.cpu else dict(ROM_SHA256=C.CANDIDATE,variant=variant,
            controller_SHA256=sha256(controller(raw,variant).encode()).hexdigest(),geometry=geometry(raw),outputs=0,Mesen_run=False)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if args.cpu:assert q['passed'],'Natural Star scope remains unqualified'
