"""Strict root-native ordinary Sonic/Super1UP observer; no game-memory writes."""
from functools import lru_cache
from pathlib import Path
import json,re
import current_sonic_hidden_heads_f7c9_1116 as F
import sonic_natural_life_braked_policy_1327_1116 as Policy

J=F
F_SHA='7bc61c4e600ef6b9264b8c8b8ff308b7d806b3b0e558567b4cc6ebd7f4f93796'
POLICY_SHA='3226b589d1b7c0baa090bf4b60a49e8db1d76687938211c773eb75dfd6b9c845'


@lru_cache(maxsize=2)
def bindings(raw,form='sonic'):
    assert form in F.FORMS and F.H(Path(F.__file__).read_bytes())==F_SHA and F.H(Path(Policy.__file__).read_bytes())==POLICY_SHA
    q=F.bindings(raw);b=q['bundle'];ram=dict(q['fields'])
    names=set(re.findall(r"r\('([A-Za-z0-9_]+)'",Policy.text()))
    names.update(('Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','SavedJoypadBits','ScreenLeft_X_Pos','ScreenLeft_PageLoc','CheatStartLevel','CheatInvincible',
        'ColumnSets','AreaParserTaskNum','CurrentPageLoc','CurrentColumnPos','BlockBufferColumnPos','MTileAttribute',
        'BoundingBox_UL_Corner','Player_State','CrossoverTitleDrawn','DisableScreenFlag','CrossoverMenuState','CrossoverMenuIndex'))
    for n in names:ram[n]=F.W.address(b,n)
    hooks={}
    for n in('GameLoop','SonicHostMain','HandlePowerUpCollision','PlayerHeadCollision'):
        h=q['hooks'][n];hooks[n]=dict(pc=h['PC'],tag=h['tag'],hex=h['first32'])
    for n,pc,tag in(('OriginalFrame',0xbbb0,3),('Selector',0xbb26,3),('Helper',0xd344,2)):
        hooks[n]=dict(pc=pc,tag=tag,hex=q['loaded'](pc)[:32].hex())
    at=F.W.location(b,'FloateyNumbersCore');data=raw[at:at+256];needle=b'\xee'+ram['NumberofLives'].to_bytes(2,'little');assert data.count(needle)==1
    at+=data.index(needle);pc=(F.W.address(b,'FloateyNumbersCore')&0xe000)+((at-16)&8191)
    hooks['LifeINC']=dict(pc=pc,tag=((at-16)//8192)|128,hex=raw[at:at+16].hex())
    for h in hooks.values():
        t,pc=h['tag'],h['pc'];h['offset']=(t&127)*8192+(pc&8191)
        if t>=128:h['bank_SHA256']=F.H(raw[16+8192*(t&127):16+8192*((t&127)+1)])
    return dict(sha=F.PIN,form=form,select=F.FORMS[form][0],name=F.FORMS[form][1],CHR=F.FORMS[form][2],
        ram=ram,hooks=hooks,cookie=F.COOKIE.hex(),source_policy_SHA256=F.H(Policy.text().encode()),
        facade_SHA256=F_SHA,packet_pages=q['packet_pages'],actual_f7_CPU=True)


BODY=r'''
local C=SONIC_CONFIG;local F,H=C.ram,C.hooks
assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact owningf7c9')
local function r(n,i)return emu.read(assert(F[n],n)+(i or 0),emu.memType.nesDebug)end
local function w(at,bank)return emu.read((bank or 2)*8192+(at&8191),emu.memType.nesWorkRam)end
local SONIC_READ=r;local SONIC_MEMORY=function(at)return emu.read(at,emu.memType.nesDebug)end
local P=(function()
POLICY_TEXT
end)();local policy=P.new('life')
local frame,polls,main,updates,motor,pad=0,0,0,0,0,0
local game,done=false,false;local pending,registered,counts={},{},{}
local heads,births,collections,changes,tail,sounds={},{},{},{},{},{}
local target,credit,lifePending=nil,nil,nil;local lastphase=nil
local function mapped(pc)
 local a=emu.convertAddress(pc);if not a then return -1 end
 if a.memType==emu.memType.nesPrgRom then return(a.address//8192)|128 end
 if a.memType==emu.memType.nesWorkRam then return a.address//8192 end
 return -1
end
local function signed(at)local x=w(at)+256*w(at+1)+65536*w(at+2);return x>=8388608 and x-16777216 or x end
local function state()
 return{x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),state=r('Player_State'),
  source_flags=w(0xc030),vx=signed(0xc020),vy=signed(0xc060),frame_status=w(0xc116),source_tick=w(0xc092),
  ready=w(0xc119),have_epoch=w(0xc11a),rings=w(0xc340),ringLives=w(0xc341),hurt=w(0xc34f),sourceStar=w(0xc350),
  status=r('PlayerStatus'),lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),
  saved=r('SavedJoypadBits'),source_input=w(0xc0a8),native_yhigh=r('Player_Y_HighPos'),
  Main=updates,motor=motor,frame=frame,camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')}
end
local function actor(i)return{slot=i,flag=r('Enemy_Flag',i),id=r('Enemy_ID',i),kind=r('PowerUpType',i),state=r('Enemy_State',i),
 x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),yhigh=r('Enemy_Y_HighPos',i)}end
local function json(v)
 if v==nil then return'null'end;local t=type(v);if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return'"'..v:gsub('[%z\1-\31\\"]',function(c)return string.format('\\u%04x',c:byte())end)..'"'end
 assert(t=='table');local q={};if #v>0 then for _,x in ipairs(v)do q[#q+1]=json(x)end;return'['..table.concat(q,',')..']'end
 for k,x in pairs(v)do q[#q+1]=json(tostring(k))..':'..json(x)end;table.sort(q);return'{'..table.concat(q,',')..'}'
end
local function finish(ok,reason)
 if done then return end;done=true;pad=0
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=C.sha,form=C.form,character=C.name,
  physical_frames=frame,input_polls=polls,Main=main,route_Main=updates,motor=motor,counts=counts,pending=#pending,
  head=heads,births=births,collected=collections,credit=credit,sounds=sounds,phase_changes=changes,tail=tail,terminal=state(),
  controller_only=true,original_emergence_state6_allowed=true,no_fully_mature128_claim=true,
  no_game_actor_inventory_health_seeds=true,no_fullstage_or_fidelity_or_cadence_claim=true,files=0,images=0}))
 emu.stop(ok and 0 or 1)
end
local function guard(name,fn)return function(...)if done then return end;local ok,why=pcall(fn,...);if not ok then finish(false,name..' '..tostring(why))end end end
local function count(n)counts[n]=(counts[n]or 0)+1 end
local function bounded(t,v,n)if #t==n then table.remove(t,1)end;t[#t+1]=v end
local function identity()return r('SelectedCharacter')==43 and emu.read(0x5ffe,emu.memType.nesDebug)==C.select end
local function headers()
 for bank=2,3 do local t={};for at=0x1fe0,0x1fef do t[#t+1]=string.format('%02x',w(at,bank))end;assert(table.concat(t)==C.cookie,'Full owning header')end
end
local function auth(name)
 local h=H[name];for i=1,#h.hex,2 do assert(emu.read(h.offset+(i-1)//2,h.tag>=128 and emu.memType.nesPrgRom or emu.memType.nesWorkRam)==tonumber(h.hex:sub(i,i+1),16),'Hook readback '..name)end
end
local function afterMain()
 if not game then return end;updates=updates+1;local s=state();local aa={}
 assert(identity()and s.engine~=11 and r('WorldNumber')==0 and r('LevelNumber')==0,'Living actual owning1-1')
 assert(r('CheatStartLevel')==0 and r('CheatInvincible')==0 and(s.lives==2 or(credit and s.lives==3)),'No cheats or unearnedlife');headers()
 assert(updates<1200,'Finite natural1UP bound')
 for i=0,5 do local a=actor(i);if a.flag~=0 then aa[#aa+1]=a
  if a.id==46 and a.kind==3 and #births==0 then assert(#heads==1 and a.x==1024,'Authored head before birth');births[1]={actor=a,player=s}end
 end end
 if credit and motor>=credit.state.motor+25 then
  assert(target and s.rings==target.before.rings and s.rings==5 and s.ringLives==0 and s.hurt==0 and s.sourceStar==0 and s.status==0 and s.lives==3,'Rings and source resources retained')
  assert((sounds[64]or 0)>credit.cue64_before and counts.OriginalFrame_entries==counts.OriginalFrame_returns,'Actual delayedlife/cue64 plus25balancedworkers')
  finish(true,'Actual ceiling/head, early-emergence physical1UP, delayedINC and25 returned original workers');return
 end
 pad=policy:decide(s,aa);assert(type(pad)=='number'and pad>=0 and pad<=255)
 if policy.phase~=lastphase then bounded(changes,{phase=policy.phase,state=s,pad=pad},8);lastphase=policy.phase end
 bounded(tail,{state=s,phase=policy.phase,pad=pad},8)
end
local function returned(p,c)
 count(p.name..'_returns')
 if p.name=='GameLoop'then main=main+1;afterMain()
 elseif p.name=='OriginalFrame'then if c['cpu.ps']&1~=0 then motor=motor+1 else count('OriginalFrame_C0')end
 elseif p.name=='HandlePowerUpCollision'and p.actor and r('Enemy_Flag',p.actor.slot)==0 then
  local a=p.actor;assert(not target and a.id==46 and a.kind==3 and a.state>=6 and #heads==1 and #births==1,'Original admissible physical1UP')
  assert((sounds[32]or 0)>p.cue32 and r('FloateyNum_Control',a.slot)==11 and r('NumberofLives')==2,'Actual erase/popup11/cue32 beforecredit')
  target={item=a,before=p.before,after=state(),popup=11,boxes=p.boxes};collections[1]=target
 end
end
local function settle()
 local c=emu.getState();local pc,sp=c['cpu.pc'],c['cpu.sp']
 if lifePending and pc==lifePending.pc and sp==lifePending.sp and mapped(pc)==lifePending.tag then
  assert(r('NumberofLives')==3,'Actual lifeINC result3');credit={PC=H.LifeINC.pc,before=lifePending.before,state=state(),cue64_before=lifePending.cue64_before};lifePending=nil
 end
 while #pending>0 do local p=pending[#pending];if p.pc~=pc or p.sp~=sp or p.tag~=mapped(pc)then return end;table.remove(pending);returned(p,c)end
end
local function register(pc)if registered[pc]then return end;registered[pc]=true;emu.addMemoryCallback(guard('Matched actual return',settle),emu.callbackType.exec,pc)end
local function enter(name)
 local h=H[name];if mapped(h.pc)~=h.tag or(name~='GameLoop'and not game)then return end;local c=emu.getState()
 if name=='Selector'or name=='Helper'then count(name);return end
 if name=='PlayerHeadCollision'then if c['cpu.a']==96 then
  local s=state();assert(#heads==0 and s.vy==0 and w(0xc0b6)==4 and w(0xc0b7)==1 and w(0xc0b8)==1,'Real original ceiling clip before hiddenhead')
  heads[1]={tile=96,player=s,PC=h.pc,SP=c['cpu.sp']}
 end;return end
 if name=='LifeINC'then
  if target and not credit then assert(r('NumberofLives')==2,'DelayedINC starts2');lifePending={pc=h.pc+3,tag=h.tag,sp=c['cpu.sp'],before=state(),cue64_before=sounds[64]or 0};register(h.pc+3)end;return
 end
 count(name..'_entries');local sp=c['cpu.sp'];local pc=(emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1)&65535
 local p={name=name,pc=pc,sp=(sp+2)&255,tag=mapped(pc)}
 if name=='HandlePowerUpCollision'then local a=actor(c['cpu.x']);if a.flag~=0 and a.id==46 and a.kind==3 then
  p.actor=a;p.before=state();p.cue32=sounds[32]or 0;local at=F.BoundingBox_UL_Corner;local off=(a.slot+1)*4
  local pbox,abox={},{};for i=0,3 do pbox[#pbox+1]=emu.read(at+i,emu.memType.nesDebug);abox[#abox+1]=emu.read(at+off+i,emu.memType.nesDebug)end
  assert(math.max(pbox[1],abox[1])<=math.min(pbox[3],abox[3])and math.max(pbox[2],abox[2])<=math.min(pbox[4],abox[4]),'Actual positive native overlap')
  p.boxes={player=pbox,item=abox}
 end end
 pending[#pending+1]=p;register(pc)
end
for name,h in pairs(H)do emu.addMemoryCallback(guard(name,function()enter(name)end),emu.callbackType.exec,h.pc)end
emu.addMemoryCallback(guard('Actual pickupcue',function(_,v)if game and(v==32 or v==64)then sounds[v]=(sounds[v]or 0)+1 end end),emu.callbackType.write,F.Square2SoundQueue)
local function pause(n)for _=1,n do coroutine.yield()end end
local function press(v)pad=v;pause(4);pad=0;pause(8)end
local function wait(fn)for _=1,1200 do if fn()then return end;coroutine.yield()end;error('Compiled menu bound')end
local boot=coroutine.create(function()
 wait(function()return frame>=70 and r('CrossoverTitleDrawn')==1 and r('DisableScreenFlag')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 and r('DisableScreenFlag')==0 end)
 for _,v in ipairs({4,4,4,1})do press(v)end;assert(r('CrossoverMenuIndex')==25,'Actual compiledslot25')
 for _=1,C.select do press(32)end;assert(identity(),'Actual Sonic form')
 press(16);wait(function()return r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 end)
 for name in pairs(H)do auth(name)end;headers();game=true;pad=0;while not done do coroutine.yield()end
end)
emu.addEventCallback(guard('Physical input poll',function()polls=polls+1;emu.setInput({right=pad&1~=0,left=pad&2~=0,down=pad&4~=0,up=pad&8~=0,start=pad&16~=0,select=pad&32~=0,b=pad&64~=0,a=pad&128~=0},0)end),emu.eventType.inputPolled)
emu.addEventCallback(guard('Physical frame',function()frame=frame+1;assert(frame<8000,'Bounded physical frames');local ok,why=coroutine.resume(boot);assert(ok,why)end),emu.eventType.endFrame)
'''


def value(v):
    if isinstance(v,dict):return'{'+','.join('['+json.dumps(k)+']='+value(x)for k,x in sorted(v.items()))+'}'
    if isinstance(v,list):return'{'+','.join(value(x)for x in v)+'}'
    if isinstance(v,bool):return'true'if v else'false'
    if v is None:return'nil'
    return json.dumps(v,separators=(',',':'))


@lru_cache(maxsize=2)
def controller(raw,form='sonic'):
    q=bindings(raw,form);body=BODY.replace('POLICY_TEXT',Policy.text());assert 'POLICY_TEXT'not in body
    return'local SONIC_CONFIG='+value(q)+'\n'+body
