"""One strict current ordinary Mushroom-access policy; no private lift/bridge."""
from hashlib import sha256
from pathlib import Path
import json

import check_dkjr_powerups_current_1113 as Metadata

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
PACKET='bbdb7d84eb2485d69d23df750ce08a3ed703b2b4de495aa08aa8c6806b7cb3e1'
COOKIE='a72801bbdb7d84eb2485d69d23df750c'
GRANT=R/'docs/qa/allocations/dkjr-natural-m-access-source-root-1116.json'
GRANT_SHA='47339382eae1f2c7c322370cb8dffd421d8771da571c0644a0150cf343b08ce0'
H=lambda b:sha256(b).hexdigest()
PAGES=(817,833,847,856,867,881,882,883,959,960,961)


def bindings(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    assert H(GRANT.read_bytes())==GRANT_SHA
    grant=json.loads(GRANT.read_text());assert grant['source_in_memory_gameplay_authorized']
    body=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in PAGES)
    assert H(body)==PACKET and raw[534485:534501].hex()==COOKIE
    assert bytes.fromhex(COOKIE)==b'\xa7\x28\x01'+sha256(body).digest()[:13]
    b=Metadata.W.Symbols.bundle();b['raw']=raw
    names=('SelectedCharacter','GameEngineSubroutine','NumberofLives','PlayerStatus','PlayerSize',
        'GuestPowerupActive','GuestPowerupAge','Player_X_Position','Player_PageLoc','Player_Y_Position',
        'Player_Y_HighPos','Player_State','Player_Y_Speed','ScreenLeft_X_Pos','ScreenLeft_PageLoc',
        'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position',
        'PowerUpType','InvPickupOwner','InvPickup','FloateyNum_Control','FloateyNum_Timer',
        'Square2SoundQueue','Player1ScoreDisplay','R2','R4','R6','R7','CrossoverMenuState',
        'CrossoverMenuIndex','GamePauseStatus','CheatInvincible','CheatStartLevel','WorldNumber','LevelNumber')
    fields={n:Metadata.W.address(b,n)for n in names}
    expected={'HuHead':(0xb6a0,652976,'8d6a01089848a00a4c40b8'),
        'NrPrepare':(0xa6f4,1017604,'0848ad0260d007'),
        'HandlePowerUpCollision':(0x9b28,1039160,'8d6a01a9e98d6c01a9a78d6d01a9fc'),
        'AddToScore':(0xb815,30757,'ae5807bc3bb8'),
        'GuestPowerupUpdate':(0xb299,86697,'adfd6bf069'),
        'NativeRarePlayerHeadCollisionCore':None}
    hooks={}
    for name,row in expected.items():
        pc,at=Metadata.W.address(b,name),Metadata.W.location(b,name)
        if row is not None:
            assert (pc,at)==row[:2]and raw[at:at+len(bytes.fromhex(row[2]))].hex()==row[2]
        hooks[name]=dict(pc=pc,offset=at-16,preimage16=raw[at:at+16].hex())
    private={'phase':0xb8f0,'move':0xa2e8,'clock':0xaf2d,'prepare':0xbf6b,'pickup':0xbf89}
    for pc,prefix in((private['phase'],'ad68c0d032'),(private['move'],'2091a2'),
            (private['clock'],'a203ce34c0'),(private['prepare'],'0848e006b015a928'),
            (private['pickup'],'adfec8c902f0023860')):
        assert body[pc-0xa000:pc-0xa000+len(bytes.fromhex(prefix))].hex()==prefix
    return dict(fields=fields,hooks=hooks,private=private)


def controller(raw):
    q=bindings(raw)
    prefix='local L={'+','.join(n+'='+str(v)for n,v in q['fields'].items())+'}\n'
    prefix+='local Hooks={'+','.join(n+'={pc='+str(v['pc'])+',offset='+str(v['offset'])+'}'for n,v in q['hooks'].items())+'}\n'
    prefix+='local Private={'+','.join(n+'='+str(v)for n,v in q['private'].items())+'}\n'
    prefix+='local ROM_SHA="'+PIN+'"\n'
    return prefix+POLICY


POLICY=r'''local frame,epoch,bits,game,done=0,0,0,false,false
local attempts,hold,rearm,phase=0,0,0,'approach'
local workEntries,workReturns,moveCalls,clockCalls=0,0,0,0
local workPending,mainPending,pickupPending,creditPending
local follows,headPending={},nil
local heads,solidHeads,effects,prepares,collectors=0,0,0,0,0
local firstRiseHead,firstSolidHead,bestHead,birth,mature,collected,credit
local growthCalls,growthAges=0,{}
local function read(at)return emu.read(at,emu.memType.nesDebug)end
local function r(n,i)return read(L[n]+(i or 0))end
local function ram(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
local function x()return r('Player_X_Position')+256*r('Player_PageLoc')end
local function score()local v=0;for i=0,5 do v=v*10+r('Player1ScoreDisplay',i)end;return v end
local function active()return r('SelectedCharacter')==40 and r('GameEngineSubroutine')==8 and ram(0x8fe)==2 end
local function ground()return active()and r('Player_State')==0 and ram(0x6b)==1 end
local function mapped(pc,offset)local m=emu.convertAddress(pc);return m and m.memType==emu.memType.nesPrgRom and m.address==offset end
local function private(pc,bank)local m=emu.convertAddress(pc);return m and m.memType==emu.memType.nesWorkRam and m.address==bank*8192+(pc&8191)end
local function snapshot()return {frame=frame,epoch=epoch,x=x(),y=r('Player_Y_Position'),native=r('Player_State'),vy=r('Player_Y_Speed'),source=ram(0x6b),prior=ram(0x6c),source_x=ram(0x213),source_y=ram(0x210),facing=ram(0x6d),held=ram(0x14),sample=ram(0x15),engine=r('GameEngineSubroutine'),lives=r('NumberofLives'),status=r('PlayerStatus'),ready=ram(0x8fe),phase=phase}end
local function encode(v)
 if type(v)=='table'then local a,n=true,0;for k in pairs(v)do if type(k)~='number'then a=false end;n=n+1 end;local out={}
  if a then for i=1,n do out[#out+1]=encode(v[i])end;return '['..table.concat(out,',')..']'end
  for k,w in pairs(v)do out[#out+1]=string.format('%q',k)..':'..encode(w)end;return '{'..table.concat(out,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif type(v)=='nil'then return 'null'else return tostring(v)end
end
local function finish(ok,why)
 if done then return end;done=true;bits=0
 if ok then assert(collected and credit and growthCalls==60 and workReturns-credit.returns>=25 and workEntries-credit.entries>=25 and not workPending and not mainPending,'Actual collection/growth/score/postcredit returned-work proof')end
 print('SMB_NATIVE_RECEIPT '..encode({passed=ok,reason=why,ROM_SHA256=ROM_SHA,controller_only=true,terminal=snapshot(),attempts=attempts,
  heads=heads,solid_heads=solidHeads,first_rising_head=firstRiseHead,first_solid_head=firstSolidHead,best_head=bestHead,head_effects=effects,
  prepares=prepares,birth=birth,mature=mature,collectors=collectors,collected=collected,credit=credit,growth_calls=growthCalls,
  original_entries=workEntries,original_returns=workReturns,move_calls=moveCalls,clock_calls=clockCalls,
  postcredit_entries=credit and workEntries-credit.entries or 0,postcredit_returns=credit and workReturns-credit.returns or 0,
  authored_question_cell=read(0x445),no_state_grants=true}))
 emu.stop(ok and 0 or 1)
end
local function token()local c=emu.getState();local sp=c['cpu.sp'];return {pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535,sp=(sp+2)&255}end
local function follow(pc)
 if follows[pc]then return end;follows[pc]=true
 emu.addMemoryCallback(function()
  local c=emu.getState();local function at(p)return p and c['cpu.pc']==p.pc and c['cpu.sp']==p.sp end
  if at(headPending)then
   heads=heads+1;local v=snapshot();v.tile=c['cpu.a'];v.row=r('R2');v.fraction=r('R4');v.base=r('R6')+256*r('R7')
   if ram(0x6b)==3 and not firstRiseHead then firstRiseHead=v end
   if v.tile~=0 then solidHeads=solidHeads+1;if not firstSolidHead then firstSolidHead=v end end
   if not bestHead or v.y<bestHead.y then bestHead=v end;headPending=nil
  end
  if at(pickupPending)then
   local p=pickupPending;assert(r('Enemy_Flag',p.slot)==0,'Actual native erase')
   collected=snapshot();collected.slot=p.slot;collected.kind=p.kind;collected.before_score=p.before_score;collected.erased=true
   collected.control=r('FloateyNum_Control',p.slot);collected.cue=r('Square2SoundQueue');assert(collected.control==6 and collected.cue==32 and collected.engine==9,'Actual mature Mushroom native grant')
   pickupPending=nil
  end
  if at(creditPending)then
   assert(score()==creditPending.before_score+1000,'Actual1000 credit')
   credit=snapshot();credit.before_score=creditPending.before_score;credit.score=score();credit.entries=workEntries;credit.returns=workReturns;creditPending=nil
  end
  if at(workPending)then
   assert(workPending.move and workPending.clock,'Actual original Move+Clock')
   workReturns=workReturns+1;workPending=nil
  end
  if at(mainPending)then mainPending=nil end
 end,emu.callbackType.exec,pc)
end
local function item()
 for i=0,5 do if r('Enemy_Flag',i)~=0 and r('Enemy_ID',i)==46 then
  local v={slot=i,kind=r('PowerUpType',i),state=r('Enemy_State',i),x=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),y=r('Enemy_Y_Position',i),epoch=epoch}
  if not birth then birth=v end
  if v.state&128~=0 and not mature then mature=v end
  return v
 end end
end
local function nearEnemy()
 for i=0,5 do local dx=r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)-x();local id=r('Enemy_ID',i)
  if r('Enemy_Flag',i)==1 and(id==2 or id==6)and r('Enemy_State',i)&32==0 and r('Enemy_Y_Position',i)>=172 and dx>=8 and dx<=30 then return true end
 end;return false
end
local function control()
 if collected then return 0 end
 local it=item()
 if it then phase='mature-and-contact';assert(it.kind==0,'Final prepared natural Mushroom kind')
  if it.state&128==0 or r('Player_Y_Position')<164 then return 0 end
  return x()<it.x-1 and 1 or x()>it.x+1 and 2 or 0
 end
 if x()<328 then
  if ground()and epoch>=rearm and nearEnemy()then hold=epoch+8;rearm=epoch+47 end
  return 1+(epoch<hold and 128 or 0)
 elseif x()>329 then return 2+(epoch<hold and 128 or 0)end
 phase='current-ground-question-jump'
 if ground()and epoch>=rearm then
  if attempts>=4 then finish(false,'current-four-ground-jumps-no-authored-item');return 0 end
  attempts=attempts+1;hold=epoch+8;rearm=epoch+48
 end
 return epoch<hold and 128 or 0
end
for name,h in pairs(Hooks)do
 emu.addMemoryCallback(function()
  if not game or not mapped(h.pc,h.offset)then return end
  local c=emu.getState();local i=c['cpu.x']
  if name=='HuHead'and active()and x()>=320 and x()<=352 then headPending=token();follow(headPending.pc)
  elseif name=='NativeRarePlayerHeadCollisionCore'then effects=effects+1
  elseif name=='NrPrepare'and i<=5 and r('Enemy_ID',i)==46 then prepares=prepares+1
  elseif name=='HandlePowerUpCollision'and i<=5 and r('Enemy_ID',i)==46 and r('Enemy_Flag',i)~=0 then
   assert(birth and mature and i==birth.slot and i==mature.slot and r('PowerUpType',i)==0 and r('Enemy_State',i)&128~=0,'Same real mature natural actor')
   assert(r('InvPickupOwner',i)==40 and r('InvPickup',i)==252,'Current original-owner preparation')
   collectors=collectors+1;pickupPending=token();pickupPending.slot=i;pickupPending.kind=0;pickupPending.before_score=score();follow(pickupPending.pc)
  elseif name=='GuestPowerupUpdate'and collected and r('GuestPowerupActive')~=0 then
   local age=r('GuestPowerupAge');assert(age>=0 and age<60 and not growthAges[age],'Actual60 distinct native growth ages')
   growthAges[age]=true;growthCalls=growthCalls+1
  elseif name=='AddToScore'and collected and not credit then
   local i=collected.slot
   if r('FloateyNum_Control',i)==6 and r('FloateyNum_Timer',i)==42 then
    creditPending=token();creditPending.before_score=collected.before_score;follow(creditPending.pc)
   end
  end
 end,emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(function()
 if not game or not private(0xd65e,2)then return end
 epoch=epoch+1;assert(not mainPending,'No nested D65E');mainPending=token();follow(mainPending.pc)
end,emu.callbackType.exec,0xd65e)
emu.addMemoryCallback(function()
 if not game or not private(Private.phase,3)then return end
 assert(not workPending,'No nested original work');workEntries=workEntries+1;workPending=token();follow(workPending.pc)
end,emu.callbackType.exec,Private.phase)
emu.addMemoryCallback(function()if workPending and private(Private.move,3)then workPending.move=true;moveCalls=moveCalls+1 end end,emu.callbackType.exec,Private.move)
emu.addMemoryCallback(function()if workPending and private(Private.clock,3)then workPending.clock=true;clockCalls=clockCalls+1 end end,emu.callbackType.exec,Private.clock)
local function wait(pred)for _=1,1000 do if pred()then return end;coroutine.yield()end;error('Menu readiness bound')end
local function press(pad)bits=pad;for _=1,4 do coroutine.yield()end;bits=0;for _=1,8 do coroutine.yield()end end
local title=coroutine.create(function()
 wait(function()return frame>=70 and read(0x6004)==1 and r('GamePauseStatus')==0 end)
 press(16);wait(function()return r('CrossoverMenuState')==2 end)
 for _,pad in ipairs({4,4,1,1,1,4})do press(pad)end
 assert(r('CrossoverMenuIndex')==27 and r('SelectedCharacter')==28);press(32);assert(r('SelectedCharacter')==40);press(16);wait(active)
 assert(r('WorldNumber')==0 and r('LevelNumber')==0 and r('CheatInvincible')==0 and r('CheatStartLevel')==0);game=true
end)
if CPU_CONTROLLER_OPENING then frame=541;game=true end
emu.addEventCallback(function()emu.setInput({right=bits&1~=0,left=bits&2~=0,down=false,up=false,start=bits&16~=0,select=bits&32~=0,a=bits&128~=0,b=false},0)end,emu.eventType.inputPolled)
emu.addEventCallback(function()
 if done then return end;frame=frame+1
 if not game then local ok,why=coroutine.resume(title);assert(ok,why);return end
 if r('NumberofLives')~=2 or r('GameEngineSubroutine')==11 or ram(0x6b)==5 then finish(false,'current-natural-access-injury');return end
 if collected and credit and growthCalls==60 and active()and r('PlayerStatus')==1 and r('GuestPowerupActive')==0 and workReturns-credit.returns>=25 and workEntries-credit.entries>=25 and not mainPending and not workPending then
  finish(true,'current-natural-Mushroom-credit-growth-and25-original-returns');return
 end
 bits=active()and control()or 0
 if epoch>=1000 or frame>=5500 then finish(false,'current-natural-access-controller-bound')end
end,emu.eventType.endFrame)
'''
