"""Current ordinary earned Bub/Bob M/F route with actual pickup witnesses."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import inspect,json
import explore_bub_flower_forward_7a80_1115 as Previous

ROM,PIN,Base=Previous.ROM,Previous.PIN,Previous.Base
B=Base.B

@lru_cache(maxsize=2)
def bindings(raw,identity=0):
    old=Base.reference(raw);b=dict(B.W.Symbols.bundle(),raw=raw)
    parent=Base.Previous.U.combined_reverse(old);labels=B.bindings(parent)[0]['labels']
    fields={n:B.W.address(b,n)for n in('PowerUpType','BoundingBox_UL_Corner','EnemyBoundingBoxCoord',
        'Player1ScoreDisplay','FloateyNum_Control','FloateyNum_Timer','Square2SoundQueue',
        'GuestPowerupAge','GuestPowerupActive')}
    image=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in B.PAGES)
    hooks={}
    for n in('BbNativePickup','BbNativeUpdate'):
        pc=labels[n];hooks[n]=dict(pc=pc,kind=1,offset=3*8192+(pc&8191),data=image[pc-0xa000:pc-0xa000+8].hex())
    pc=labels['BbNativePickup'];start=pc-0xa000;code=image[start:start+46]
    pattern=bytes.fromhex('1d02c09d02c0');assert code.count(pattern)==1
    pc+=code.index(pattern)+len(pattern)
    hooks['BbGrantAfter']=dict(pc=pc,kind=1,offset=3*8192+(pc&8191),data=image[pc-0xa000:pc-0xa000+8].hex())
    for n in('EraseEnemyObject','SetupFloateyNumber','GuestPowerupUpdate'):
        at=B.W.location(b,n);hooks[n]=dict(pc=B.W.address(b,n),kind=2,offset=at-16,data=raw[at:at+8].hex())
    return dict(ram=fields,hooks=hooks,identity=identity,ROM_SHA256=PIN)

WITNESS=r'''
local actualMoves=0;local currentPickup=nil
local function itemScore()local value=0;for i=0,5 do value=value*10+read(Stock.ram.Player1ScoreDisplay+i)end;return value end
local function itemBox(at)local t={};for i=0,3 do t[#t+1]=read(at+i)end;return t end
local function itemState()local q=state();q.moves=actualMoves;q.score=itemScore();q.flags=work(2,(identity==1 and 0x42 or 0x2e)+2);q.power=r('PlayerStatus');return q end
local function regularItem(slot)
 return slot>=0 and slot<6 and read(L.Enemy_Flag+slot)==1 and read(L.Enemy_ID+slot)==46
  and read(L.Enemy_State+slot)>=128 and read(L.PowerUpType+slot)<2
end
local function pickupRecord(slot)
 local kind=read(L.PowerUpType+slot);flower.pickups=flower.pickups or{}
 local key=kind==0 and'M'or'F';flower.pickups[key]=flower.pickups[key]or{kind=kind,slot=slot,freeze=0}
 return flower.pickups[key]
end
for name,h in pairs(Stock.hooks)do
 emu.addMemoryCallback(guard(function()
  if not game or r('SelectedCharacter')~=39 then return end
  local kind=h.kind==1 and emu.memType.nesWorkRam or emu.memType.nesPrgRom
  if not mapped(h.pc,kind,h.offset)then return end
  for i=1,#h.data,2 do assert(read(h.pc+(i-1)//2)==tonumber(h.data:sub(i,i+1),16),'Exact current mature pickup/move/animation hook '..name)end
  local cpu=emu.getState();local slot=cpu['cpu.x']
  if name=='BbNativeUpdate'then if active()then actualMoves=actualMoves+1 end
  elseif name=='BbNativePickup'and regularItem(slot)then
   local p=pickupRecord(slot);assert(not p.collector,'One physical regular collector per kind')
   p.collector={state=itemState(),slot=slot,x=full_x(slot),y=read(L.Enemy_Y_Position+slot),
    player_box=itemBox(Stock.ram.BoundingBox_UL_Corner),item_box=itemBox(Stock.ram.EnemyBoundingBoxCoord+slot*4)}
   currentPickup=p
  elseif name=='BbGrantAfter'and currentPickup then
   local p=currentPickup;p.grant={state=itemState(),source_actor=slot}
   assert(slot==(identity==1 and 0x42 or 0x2e),'Actual selected original source actor')
   assert(p.grant.state.flags==(p.kind==0 and 1 or 7),'Original item4/item2 masks applied by actual code')
  elseif name=='SetupFloateyNumber'and(regularItem(slot)or(currentPickup and currentPickup.slot==slot))then
   -- Actual MarioSourcePowerupCollision erases the actor before this call.
   -- Keep the authenticated collector/slot token through native bookkeeping.
   local p=currentPickup and currentPickup.slot==slot and currentPickup or pickupRecord(slot)
   p.setup={control=cpu['cpu.a'],state=itemState()}
  elseif name=='EraseEnemyObject'and currentPickup and currentPickup.slot==slot then
   currentPickup.erase=itemState()
  elseif name=='GuestPowerupUpdate'and currentPickup and r('GuestPowerupActive')==1 then
   currentPickup.freeze=currentPickup.freeze+1
   currentPickup.first_age=currentPickup.first_age or read(Stock.ram.GuestPowerupAge)
   currentPickup.last_age=read(Stock.ram.GuestPowerupAge)
  end
 end),emu.callbackType.exec,h.pc)
end
emu.addMemoryCallback(guard(function(at,value)
 if currentPickup and not currentPickup.cue and value==32 then
  currentPickup.cue={value=value,state=itemState(),PC=emu.getState()['cpu.pc']}
 end
end),emu.callbackType.write,Stock.ram.Square2SoundQueue)
local function observePickup()
 if currentPickup then
  local p=currentPickup;local control=read(Stock.ram.FloateyNum_Control+p.slot)
  if control==6 then p.popup=p.popup or{control=control,timer=read(Stock.ram.FloateyNum_Timer+p.slot),state=itemState()}end
 end
end
local function requirePickup(p,post)
 assert(p and p.collector and p.grant and p.erase and p.setup and p.popup and p.cue,'Actual physical collector/grant/erase/popup/cue witnesses')
 assert(p.setup.control==6 and p.popup.control==6 and p.cue.value==32,'Native1000 popup and cue32')
 assert(p.freeze==60,'Exactly60 actual hosted powerup updates')
 assert(actualMoves-p.grant.state.moves>=post,'Actual Bub movement calls after source grant')
 assert(itemScore()==p.collector.state.score+1000,'Actual delayed1000 score')
end
'''


@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    text=Previous.controller(raw,identity,mode);once=Previous.Previous.Previous.once
    cfg=bindings(raw,identity)
    line='local Stock='+Base.Previous.lua(cfg)+'\n'
    at=text.index('\n')+1;text=text[:at]+line+text[at:]
    marker='local Q={launch={bob=identity}}'
    add='\n'.join('L.'+n+'='+str(value)for n,value in cfg['ram'].items())+'\n'
    text=once(text,marker,add+marker)
    text=once(text,'local poweredGeneration,poweredSlot=nil,nil',WITNESS+'\nlocal poweredGeneration,poweredSlot=nil,nil')
    text=once(text," if flower.phase=='mushroom'then", " observePickup()\n if flower.phase=='mushroom'then")
    text=once(text,'flower.M_resume=25;full_part=',"requirePickup(flower.pickups and flower.pickups.M,25)\n   flower.M_resume=25;full_part=")
    text=once(text,"   finish(true,'Genuine earned Mushroom then Flower and25 source movement calls');return", "   requirePickup(flower.pickups and flower.pickups.F,25)\n   flower.actual_post_F_moves=actualMoves-flower.pickups.F.grant.state.moves\n   assert(flower.actual_post_F_moves==25,'Exactly25 actual post-Flower movement entries')\n   finish(true,'Genuine earned Mushroom then Flower and25 actual movement calls');return")
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    assert not any(x in text for x in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text


def source_check(raw,identity=0):
    Base.reference(raw)
    source=inspect.getsource(Base.Previous.source_check)
    def once(old,new):
        nonlocal source
        assert source.count(old)==1,old;source=source.replace(old,new,1)
    once('events, callbacks = {}, defaultdict(list)','events, callbacks = {}, defaultdict(list)\n    write_callbacks=defaultdict(list)')
    once('dict(exec=0)','dict(exec=0,write=1)')
    once('api.addMemoryCallback=lambda fn,kind,pc:callbacks[pc].append(fn)',
        'api.addMemoryCallback=lambda fn,kind,pc:(callbacks if kind==0 else write_callbacks)[pc].append(fn)')
    once('    Base=B.N.NesMPU', '''    old_bus=type(m)
    class WriteObserved(old_bus):
        def __setitem__(self,at,value):
            if isinstance(at,int):
                for fn in tuple(write_callbacks.get(at,())):fn(at,value)
            return super().__setitem__(at,value)
    m.__class__=WriteObserved
    Base=B.N.NesMPU''')
    once('    result=dict(passed=', '    m.__class__=old_bus\n    result=dict(passed=')
    ns=dict(Base.Previous.__dict__,PIN=PIN,controller=controller)
    exec(compile(source,str(Path(__file__))+':read-only-write-observer','exec'),ns)
    return ns['source_check'](raw,identity,'mushroom',4200)
