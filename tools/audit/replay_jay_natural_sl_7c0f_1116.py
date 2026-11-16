"""Strict root-native packaging for ordinary current7c0f Jay Star/1UP."""
from functools import lru_cache
from pathlib import Path
import json
import jay_natural_fsl_controls_v3_1116 as V3
import check_jay_natural_sl_current_1116 as Source

J=V3.J
V3_SHA='6746cbe6239e67c08ee6d5cdd9207902bd3b83f86c4d4e1c3fd1be5ef2e58704'


@lru_cache(maxsize=2)
def bindings(raw,kind):
    assert kind in('star','life')and J.H(raw)==J.PIN
    assert J.H(Path(V3.__file__).read_bytes())==V3_SHA
    q=J.bindings(raw);b=q['bundle'];ram=dict(q['fields']);hooks={}
    for name in('Enemy_Y_HighPos','FloateyNum_Control','NmiDisable','Player1ScoreDisplay'):
        ram[name]=J.W.address(b,name)
    for name in('GameLoop','JayIntegrate','HandlePowerUpCollision','PlayerHeadCollision','SetupFloateyNumber'):
        h=q['hooks'][name];hooks[name]=dict(pc=h['PC'],tag=h['tag'],hex=h['first16_hex'])
    name='JnCollectPickup';at=J.W.location(b,name)
    hooks[name]=dict(pc=J.W.address(b,name),tag=((at-16)//8192)|128,hex=raw[at:at+16].hex())
    at=J.W.location(b,'FloateyNumbersCore');data=raw[at:at+256]
    needle=b'\xee'+ram['NumberofLives'].to_bytes(2,'little')
    assert data.count(needle)==1
    at+=data.index(needle)
    original=J.W.address(b,'FloateyNumbersCore')
    pc=(original&0xe000)+((at-16)&8191)
    hooks['LifeINC']=dict(pc=pc,tag=((at-16)//8192)|128,hex=raw[at:at+16].hex())
    for name,h in hooks.items():
        if h['tag']>=128:
            bank=h['tag']&127;h['bank_SHA256']=J.H(raw[16+8192*bank:16+8192*(bank+1)])
            h['offset']=bank*8192+(h['pc']&8191)
        else:h['offset']=h['tag']*8192+(h['pc']&8191)
    return dict(sha=J.PIN,kind=kind,ram=ram,hooks=hooks,cookie=J.COOKIE.hex(),
        source=q['source'],geometry=Source.geometry(raw),source_policy_SHA256=J.H(V3.text().encode()),
        facade_SHA256=J.H(Path(J.__file__).read_bytes()))


BODY=r'''
-- Ordinary inputs and passive witnesses only. No game-memory writes.
local C=JAY_CONFIG;local F,H=C.ram,C.hooks
local expected=assert(os.getenv('SMB_STDOUT_ROM_SHA'));assert(expected==C.sha,'Exact owning current7c0f')
local P=(function()
POLICY_TEXT
end)();local policy=P.new(C.kind)
local frame,polls,main,updates,motor,pad=0,0,0,0,0,0
local game,done=false,false
local counts,pending,registered,heads,births,collects,popups,sounds={},{},{},{},{},{},{},{}
local seen,changes,tail={}, {}, {}
local music64=0
local target,credit,award,lifePending=nil,nil,nil,nil
local lastphase=nil
local function r(n,i)return emu.read(F[n]+(i or 0),emu.memType.nesDebug)end
local function w(bank,at)return emu.read(bank*8192+at,emu.memType.nesWorkRam)end
local function source(at)return w(2,at&8191)end
local function mapped(pc)
 local q=emu.convertAddress(pc);if not q then return -1 end
 if q.memType==emu.memType.nesPrgRom then return(q.address//8192)|128 end
 if q.memType==emu.memType.nesWorkRam then return q.address//8192 end
 return -1
end
local function state()
 local score=0;for i=0,5 do score=score*10+r('Player1ScoreDisplay',i)end
 return{x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),
  native_state=r('Player_State'),native_vy=r('Player_Y_Speed'),native_yhigh=r('Player_Y_HighPos'),
  source_flags=source(C.source.flags),source_control=source(C.source.control),grounded=source(C.source.flags)&4==0,
  hp=r('JnHealth'),maximum=r('JnMaxHearts'),tier=r('JnOwnedTier'),lives=r('NumberofLives'),status=r('PlayerStatus'),
  star=r('StarInvincibleTimer'),engine=r('GameEngineSubroutine'),camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'),
  score=score,weapon=source(0xc020),ammo=source(0xc0be),Main=updates,motor=motor,frame=frame}
end
local function actor(i)
 return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),
  x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),yhigh=r('Enemy_Y_HighPos',i),
  private=r('InvPickup',i),owner=r('InvPickupOwner',i),contact=r('PlatformCollisionFlag',i)}
end
local function json(v)
 if v==nil then return'null'end
 local t=type(v);if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return'"'..v:gsub('[%z\1-\31\\"]',function(c)return string.format('\\u%04x',c:byte())end)..'"'end
 assert(t=='table');local q={}
 if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end
 for k,x in pairs(v)do q[#q+1]=json(tostring(k))..':'..json(x)end;table.sort(q);return'{'..table.concat(q,',')..'}'
end
local function finish(ok,reason)
 if done then return end;done=true;pad=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=C.sha,kind=C.kind,controller_only=true,
  physical_frames=frame,input_polls=polls,Main=main,route_Main=updates,motor=motor,counts=counts,pending=#pending,
  head=heads,births=births,collected=collects,target=target,credit=credit,award=award,popups=popups,sound=sounds,
  phase_changes=changes,tail=tail,terminal=state(),source_policy_SHA256=C.source_policy_SHA256,geometry=C.geometry,
  no_gameplay_or_actor_or_health_seeds=true,no_fullstage_or_cadence_claim=true,files=0,images=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(name,fn)return function(...)
 if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,name..' '..tostring(why))end
end end
local function count(name)counts[name]=(counts[name]or 0)+1 end
local function bounded(q,row,n)if #q==n then table.remove(q,1)end;q[#q+1]=row end
local function auth(name)
 local h=H[name];for i=1,#h.hex,2 do
  local actual=emu.read(h.offset+(i-1)//2,h.tag>=128 and emu.memType.nesPrgRom or emu.memType.nesWorkRam)
  assert(actual==tonumber(h.hex:sub(i,i+1),16),'Actual hook readback '..name)
 end
end
local function identity()return r('SelectedCharacter')==16 and emu.read(0x730b,emu.memType.nesDebug)&96==32 end
local function afterMain()
 if not game then return end
 updates=updates+1;local s=state();local aa={}
 assert(identity()and s.hp>0 and s.engine~=11,'Actual living Jay identity')
 assert(s.lives==2 or(target and C.kind=='life'and s.lives==3),'Only actual natural life credit')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0,'1-1 no cheats')
 assert(updates<2400,'Finite ordinary natural route')
 for bank=2,3 do
  local h={};for i=0x1fe0,0x1fef do h[#h+1]=string.format('%02x',w(bank,i))end
  assert(table.concat(h)==C.cookie,'Complete owning Jay header')
 end
 for i=0,5 do local a=actor(i);if a.flag~=0 then
  aa[#aa+1]=a
  if a.id==46 then
   local key=a.slot..'/'..a.kind
   if not seen[key]then
    if a.kind==(C.kind=='star'and 2 or 3)then
     assert(#heads==1 and a.x==C.geometry.targets[C.kind].left,'Actual authored head before target birth')
    end
    assert(#births<8);births[#births+1]={actor=a,player=s};seen[key]=true
   end
  end
 end end
 if target and not credit then
  if C.kind=='star'or(s.lives==3 and award and(sounds[64]or 0)>award.cue64_before)then credit={state=s,Main=updates,motor=motor}end
 end
 if credit and motor>=credit.motor+25 then
  assert(s.hp==target.before.hp and s.maximum==target.before.maximum and s.tier==target.before.tier,'Native item retains inherited health/tier')
  if C.kind=='star'then assert(s.score>=target.before.score+1000,'Natural Star1000score')
  else assert(s.lives==3 and award and sounds[64],'Real delayed INC/cue64')end
  assert((counts.JayIntegrate_entries or 0)==(counts.JayIntegrate_returns or 0),'Balanced original donor returns')
  finish(true,'Natural '..C.kind..' physical collector and25 resumed original returns');return
 end
 local bits=policy:decide(s,aa);assert(type(bits)=='number'and bits>=0 and bits<=255);pad=bits
 if policy.phase~=lastphase then bounded(changes,{Main=updates,motor=motor,phase=policy.phase,x=s.x,y=s.y},8);lastphase=policy.phase end
 bounded(tail,{state=s,phase=policy.phase,pad=pad},8)
end
local function returned(p,c)
 count(p.name..'_returns')
 if p.name=='GameLoop'then main=main+1;afterMain()
 elseif p.name=='JayIntegrate'then motor=motor+1
 elseif p.name=='JnCollectPickup'then p.C=c['cpu.ps']&1;counts.last_private_C=p.C
 elseif p.name=='HandlePowerUpCollision'and p.actor.flag~=0 and p.actor.id==46 and r('Enemy_Flag',p.actor.slot)==0 then
  local a=p.actor;local s=state()
  assert(not target and a.kind==(C.kind=='star'and 2 or 3)and a.private==252 and a.owner==16,'Actual owning target type')
  assert(#heads>0 and #births>0 and counts.last_private_C==0,'Natural head/birth and native C0 collector')
  assert((sounds[32]or 0)>p.cue32_before,'Actual native pickup cue32 write')
  assert(s.hp==p.before.hp and s.maximum==p.before.maximum and s.tier==p.before.tier,'Native stats preserved')
  target={item=a,before=p.before,after=s,Main=updates,motor=motor,popup=r('FloateyNum_Control',a.slot),sound_queue=r('Square2SoundQueue'),cue32_writes=(sounds[32]or 0)-p.cue32_before,music64_writes=music64-p.music64_before}
  if C.kind=='star'then assert(s.star==35 and target.music64_writes>0 and target.popup==6,'Native Star35/music64/popup6')
  else assert(s.lives==2 and target.popup==11,'Native1UP popup11 before delayed credit')end
  collects[#collects+1]=target;policy:collect(C.kind)
 end
end
local function settle()
 local c=emu.getState();local pc,sp=c['cpu.pc'],c['cpu.sp']
 while #pending>0 do local p=pending[#pending]
  if p.pc~=pc or p.sp~=sp or p.tag~=mapped(pc)then return end
  table.remove(pending);returned(p,c)
 end
end
local function register(pc)
 if registered[pc]then return end;registered[pc]=true
 emu.addMemoryCallback(guard('Actual return',settle),emu.callbackType.exec,pc)
end
local function enter(name)
 local h=H[name];if mapped(h.pc)~=h.tag then return end
 if name~='GameLoop'and not game then return end
 local c=emu.getState()
 if name=='PlayerHeadCollision'then
  local s=state();local left=C.geometry.targets[C.kind].left
  if c['cpu.a']==(C.kind=='star'and 87 or 96)and math.abs(s.x-left)<25 then
   assert(#heads==0,'Single authored target head');heads[1]={tile=c['cpu.a'],player=s}
  end
  return
 end
 if name=='SetupFloateyNumber'then bounded(popups,c['cpu.a'],16);return end
 if name=='LifeINC'then
  if not target or C.kind~='life'then return end
  assert(r('NumberofLives')==2 and target.popup==11,'Delayed source INC begins from2')
  lifePending={pc=h.pc+3,sp=c['cpu.sp'],tag=h.tag,before=state(),cue64_before=sounds[64]or 0}
  if not registered['life']then registered.life=true;emu.addMemoryCallback(guard('Actual life INC result',function()
   local p=lifePending;if not p or mapped(p.pc)~=p.tag or emu.getState()['cpu.sp']~=p.sp then return end
   assert(r('NumberofLives')==3,'Actual EE life result3');award={before=p.before,after=state(),PC=h.pc,cue64_before=p.cue64_before};lifePending=nil
  end),emu.callbackType.exec,h.pc+3)end
  return
 end
 count(name..'_entries')
 local sp=c['cpu.sp'];local pc=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}
 if name=='HandlePowerUpCollision'then p.actor=actor(c['cpu.x']);p.before=state();p.cue32_before=sounds[32]or 0;p.music64_before=music64 end
 pending[#pending+1]=p;register(pc)
end
for name,h in pairs(H)do emu.addMemoryCallback(guard(name,function()enter(name)end),emu.callbackType.exec,h.pc)end
emu.addMemoryCallback(guard('Actual cue',function(_,v)if game and(v==32 or v==64)then sounds[v]=(sounds[v]or 0)+1 end end),emu.callbackType.write,F.Square2SoundQueue)
emu.addMemoryCallback(guard('Actual Star music',function(_,v)if game and v==64 then music64=music64+1 end end),emu.callbackType.write,F.AreaMusicQueue)
local function pause(n)for _=1,n do coroutine.yield()end end
local function press(v)pad=v;pause(4);pad=0;pause(8)end
local function wait(fn)for _=1,1200 do if fn()then return end;coroutine.yield()end;error('Compiled menu bound')end
local boot=coroutine.create(function()
 wait(function()return frame>=70 and emu.read(0x6004,emu.memType.nesDebug)==1 and emu.read(0x775,emu.memType.nesDebug)==0 end)
 press(16);wait(function()return emu.read(0x7307,emu.memType.nesDebug)==2 and emu.read(0x775,emu.memType.nesDebug)==0 end)
 press(4);for _=1,7 do press(1)end;press(32)
 assert(emu.read(0x7309,emu.memType.nesDebug)==15 and identity(),'Actual compiled Jay name/Select variant')
 press(16);wait(function()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end)
 for name in pairs(H)do auth(name)end
 game=true;pad=0;while not done do coroutine.yield()end
end)
emu.addEventCallback(guard('Physical controller poll',function()
 polls=polls+1;emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)
end),emu.eventType.inputPolled)
emu.addEventCallback(guard('Physical frame',function()
 frame=frame+1;assert(frame<10000,'Physical route bound');local ok,why=coroutine.resume(boot);assert(ok,why)
end),emu.eventType.endFrame)
'''


@lru_cache(maxsize=2)
def controller(raw,kind):
    q=bindings(raw,kind)
    body=BODY.replace('POLICY_TEXT',V3.text());assert 'POLICY_TEXT'not in body
    def value(v):
        if isinstance(v,dict):return'{'+','.join('['+json.dumps(k)+']='+value(x)for k,x in sorted(v.items()))+'}'
        if isinstance(v,list):return'{'+','.join(value(x)for x in v)+'}'
        if isinstance(v,bool):return'true'if v else'false'
        if v is None:return'nil'
        return json.dumps(v,separators=(',',':'))
    return 'local JAY_CONFIG='+value(q)+'\n'+body
