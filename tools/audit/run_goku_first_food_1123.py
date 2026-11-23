"""Current27e01 Goku ordinary Easy first authored Mushroom and source reward.

True menu31 Arthur->Select Goku, normal input, authored X336 actor, immediate
native +20HP/cap150 and Pole/tier1, actual popup1000 writer and25 completed
Main/Dragon Power movement returns. Source declares linked real menu entry.
Root alone owns --run and the existing two-file native slot.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_quick_second_food_1123 as Shared

Base,Stock,W,N,H,ROM,Engine=Shared.Base,Shared.Stock,Shared.W,Shared.N,Shared.H,Shared.ROM,Shared.Engine
PIN='27e01af3ad9e581ac1b77227bc4ba491af76eaf9c7995c3a6eea10d891087866'
LUA='68dc1dd9b0704e66597c752085906d10998ccefb4470a2804a47fec485acbdb7'
SOURCE_PROOF={
    'receipt_SHA256':'d59b6fddd209b690fc4ff563c1a7021cddb434547c199899bd26761eb9d6f693',
    'receipt_inner_SHA256':'2c9c8a5728642f8c837c36efe6153acdb2c2311104265f4155c4d3e72f6ee068',
    'linked_source_passes':430,'Main_returns':430,'Dp_returns':430,
    'authored_birth':[336,136,0],'collector_player':[399,176],
    'health_before_after':[94,114],'Pole_before_after':[0,1],'tier_before_after':[0,1],
    'score_before_after':[20,1020],'post_credit_returns':25,'terminal':[399,176,113,1,2],
    'scope':'Declared linked real menu entry; actual owning CPU; no native cadence claim',
}

DRIVE=r'''
local function released()return r('DpPrevious')&128==0 end
local function change(p)
 if food.phase==p then return end
 food.phase=p;food.at=guestReturns;food.events=food.events or{}
 assert(#food.events<35,'Bounded ordinary Goku phases')
 food.events[#food.events+1]=state()
end
local function drive()
 if not menuDone or not active()then buttons={};return end;identity();observe()
 if pendingCollect or pendingScore or food.pickups[1]then buttons={};return end
 local c=context();local a=target()
 if a then
  change('collect');food.intercept={state=state(),actor=a}
  local x=a.state>=128 and math.min(419,math.max(385,a.x-8))or 388
  buttons={right=c.x<x-2,left=c.x>x+2};return
 end
 if food.phase=='collect'then buttons={};return end
 if food.phase=='press'then
  if r('DpAction')==2 or r('DpAction')==3 and r('DpJumping')~=0 then
   food.launch=food.launch or state();change('airborne')
  elseif not released()then change('release');buttons={};return end
  buttons={a=true};return
 end
 if food.phase=='airborne'then
  if c.grounded and r('DpAction')==1 and guestReturns-food.at>5 then change('release')
  else buttons={a=guestReturns-food.at<32};return end
 end
 if c.x<310 then
  local e=c.enemy();buttons={right=true}
  if food.approachJump and not c.grounded then buttons.a=true
  elseif c.grounded and r('DpAction')==1 and released()and e and e.dx>8 and e.dx<65 and math.abs(e.y-c.y)<40 then
   food.approachJump=state();buttons.a=true
  end
  return
 end
 food.approachJump=nil
 if not c.grounded or r('DpAction')~=1 then buttons={};return end
 if math.abs(c.x-330)>2 then change('align');buttons={right=c.x<328,left=c.x>332};return end
 if c.vx~=0 or not released()then change('release');buttons={};return end
 food.attempts=(food.attempts or 0)+1;assert(food.attempts<=6,'Bounded genuinely released original jump requests')
 change('press');buttons={a=true}
end
'''


def once(text,a,b):return Shared.once(text,a,b)


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(raw)==PIN;b=dict(W.Symbols.bundle(),raw=raw)
    names='''Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State
Player_X_Speed Player_Y_Speed PlayerStatus PlayerFacingDir PreviousA_B_Buttons A_B_Buttons
WorldNumber LevelNumber AreaPointer AreaType GameEngineSubroutine ScreenLeft_X_Pos ScreenLeft_PageLoc
Block_Buffer_1 Enemy_Flag Enemy_ID Enemy_State PowerUpType Enemy_X_Position Enemy_PageLoc Enemy_Y_Position
OperMode OperMode_Task NumberofLives CurrentPlayer FmAlts SelectedCharacter CrossoverBehaviorVersion
CheatInvincible CheatStartLevel CrossoverTitleDrawn DisableScreenFlag CrossoverMenuState CrossoverMenuIndex
TimerControl ScrollLock StarInvincibleTimer GuestPowerupActive Square2SoundQueue FloateyNum_Timer
FloateyNum_Control Player1ScoreDisplay BoundingBox_UL_Corner EnemyBoundingBoxCoord SavedJoypadBits
ObjectOffset DpReady DpHP DpPole DpWaves DpPower DpHunger DpProtection DpSecondPhase DpAction
DpPrevious DpJumping DpClock'''.split()
    ram={n:W.address(b,n)for n in names};hooks={}
    def add(name,pc,at):hooks[name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+12]),work=False)
    for n in('GameLoop','UnionPwrUpCore','EraseEnemyObject','SetupFloateyNumber','HandlePowerUpCollision','DpMovement','DpPickup'):
        add(n,W.address(b,n),W.location(b,n))
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):add('MainReturn'+str(i),pc+delta,at+delta)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=ram['FloateyNum_Timer']
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle]
    assert len(hits)==1;add('StockTimerDEC',pc+hits[0],at+hits[0])
    # The exact owner's real input latch used by the retained f205 retry.
    at=16+86*8192+(0xb33b&8191)
    assert raw[at:at+19].hex()=='a5dc4dd95f25dcaabd07b58d165ca5dc8dd95f'
    assert ram['DpPrevious']==0x5fd9 and ram['DpAction']==0x5c00 and ram['DpJumping']==0x5c0b
    pickup=hooks['DpPickup'];assert raw[pickup['offset']+16:pickup['offset']+17]==b'\x48'
    return dict(sha=PIN,key='goku',kind='mushroom',cycle=1,ram=ram,hooks=hooks)


@lru_cache(maxsize=1)
def controller(raw):
    cfg=bindings(raw);text=Shared.TEMPLATE.read_text()
    text=once(text,"return n:sub(1,2)=='Bt'and work(at)or read(at)",'return read(at)')
    text=text.replace("'BtSrc_Objects_Life',r('CurrentPlayer')","'DpHP'")
    text=once(text,"HP=r('DpHP'),lives=", "HP=r('DpHP'),pole=r('DpPole'),waves=r('DpWaves'),tier=r('DpPower'),hunger=r('DpHunger'),protection=r('DpProtection'),action=r('DpAction'),previous=r('DpPrevious'),second=r('DpSecondPhase'),lives=")
    text=once(text,'Bt_entries=guestEntries,Bt_returns=guestReturns','Dp_entries=guestEntries,Dp_returns=guestReturns')
    text=once(text,'local function returning(fn)',"""local function mapping(pc)
 local m=emu.convertAddress(pc);return m and tostring(m.memType)..':'..tostring(m.address)or'cpu:'..tostring(pc)
end
local function returning(fn)""")
    text=once(text,"entryPC=emu.getState()['cpu.pc']}","entryPC=emu.getState()['cpu.pc'],mapping=mapping(pc)}")
    text=once(text,'if t.sp==sp then table.remove(list,i);t.fn(t)end','if t.sp==sp and t.mapping==mapping(pc)then table.remove(list,i);t.fn(t)end')
    text=once(text," assert(r('SelectedCharacter')==33 and r('FmGroups')==64+C.variant and r('BtVariant')==C.variant,'Actual Battletoads identity')", " assert(r('SelectedCharacter')==24 and r('FmAlts')&128~=0,'Actual menu-selected Goku identity')")
    text=once(text," assert(r('BtHostReady')==1 and r('DpHP')<128,'Living original source')", " assert(r('DpReady')==68 and r('DpHP')>0 and r('DpHP')<=150 and r('DpWaves')==0,'Living original Dragon Power owner')")
    text=once(text,'poll=guestReturns,char=33,variant=C.variant','poll=guestReturns,char=24,variant=128')
    text=once(text,' if not food.births[n]then',""" if not food.births[n]then
  local h=food.heads[n];assert(n==1 and h and h.after and h.after.flag==1 and h.after.kind==0 and h.after.x==a.x,
   'Actual authored head returns the original first Mushroom actor')""")
    a=text.index('local function drive()');z=text.index('local function endpoint()',a);text=text[:a]+DRIVE+'\n'+text[z:]
    text=once(text,"  assert(r('PlayerStatus')==q.before.power and r('GuestPowerupActive')==0,'Original food preserves native tier, no invented upgrade')", "  assert(r('PlayerStatus')==1 and r('DpPower')==1 and r('DpPole')==1 and r('DpWaves')==0 and r('GuestPowerupActive')==0,'Actual earned Pole/tier survives25 original movements')")
    text=once(text,"  assert(r('DpHP')==q.after.HP,'Food HP retained through25 workers')", "  assert(r('DpHP')>0,'Ordinary original hunger/damage continues without death after pickup')")
    text=once(text,"   assert(guestEntries==guestReturns and mainEntries==mainReturns,'Balanced actual returns')", """   assert(guestEntries==guestReturns and mainEntries==mainReturns,'Balanced actual returns')
   assert(not pendingCollect and not pendingScore,'All native food/score transactions returned')
   for _,list in pairs(dynamic)do assert(#list==0,'Every observed worker returned through the exact mapped caller')end""")
    text=once(text,"'Natural Battletoads '..C.kind..' food and25 actual returned original workers at returned Main'", "'Natural Goku Mushroom, actual health/Pole reward and25 completed original workers'")
    a=text.index("hook('BtConstruct',function()");z=text.index("hook('BtPickup',function()",a)
    text=text[:a]+r'''
hook('DpMovement',function()
 food.first_worker=food.first_worker or{pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp']}
 assert(not pendingGuest,'Previous Dragon Power movement returned');guestEntries=guestEntries+1
 pendingGuest=returning(function(t)pendingGuest=nil;guestReturns=guestReturns+1 end)
end)
hook('DpPickup',function()
 if not pendingCollect then return end
 local q=pendingCollect;local before=state();assert(emu.getState()['cpu.a']==0 and q.actor.kind==0,'Actual first Mushroom kind at source collector')
 local pc=emu.getState()['cpu.pc']
 returning(function(t)
  local after=state();assert(after.HP==math.min(150,before.HP+20)and before.HP<150 and after.HP>before.HP,
   'Immediate original food20/cap150 produces a real health increase')
  assert(before.pole==0 and before.tier==0 and after.pole==1 and after.tier==1 and after.waves==before.waves and after.hunger==0,
   'Actual native Pole/tier1 and original hunger reset, not Mario growth')
  q.source_reward={before=before,after=after,pc=pc,return_pc=t.pc,return_sp=t.sp}
 end)
end)
''' +text[z:]
    text=once(text,"hook('BtPickup'", "hook('HandlePowerUpCollision'")
    text=once(text," observe();local n=#food.pickups+1;", " assert(a.kind==0,'Only the real first Mushroom is accepted')\n observe();local n=#food.pickups+1;")
    text=once(text,"  assert(q.after.HP==math.min(47,q.before.HP+8),'Actual source food8 cap47')", "  assert(q.source_reward and q.after.HP==q.source_reward.after.HP and q.after.pole==1 and q.after.tier==1,'Source award returned before actual native erase and popup')")
    text=once(text,"  assert(q.after.power==q.before.power and r('GuestPowerupActive')==0 and q.after.engine==8,'Actual food semantics, no Mario upgrade')", "  assert(r('GuestPowerupActive')==0 and q.after.engine==8,'Immediate original reward without hosted Mario growth')")
    text=once(text,"hook('FloateyNumbersCore',function()", "hook('StockTimerDEC',function()")
    text=once(text,' local before=score();pendingScore=returning(function(t)',""" local cpu=emu.getState();assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual timer43/control6 score branch')
 q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],timer=r('FloateyNum_Timer',i),control=r('FloateyNum_Control',i)}
 local before=score();pendingScore=returning(function(t)""")
    text=once(text," press('left');press('down');press('down');for i=1,C.cycle do press('select')end", " press('up');press('left');press('select')")
    text=once(text," assert(r('CrossoverMenuIndex')==23 and r('SelectedCharacter')==33 and r('FmGroups')==64+C.variant,'Actual compiled Battletoads selection')", " assert(r('CrossoverMenuIndex')==31 and r('SelectedCharacter')==24 and r('FmAlts')&128~=0,'Actual compiled Arthur Select alternate Goku')")
    text=once(text,'Exact owning6a3 environment','Exact owning27e01 environment')
    text=once(text,'Bounded natural Battletoads food policy','Bounded natural Goku first-food policy')
    program='local C='+Stock.value(cfg)+'\n'+text
    assert 'Bt'not in program and not any(s in program for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    Stock.LuaRuntime().compile(program);return program.encode()


def cold(raw):
    bindings(raw);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(8,2,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='GOKU'and N.get(m,'SelectedCharacter')==24 and N.get(m,'FmAlts')&128
    start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Base.Host.Family.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'DpReady')==68 and N.get(m,'DpHP')==100 and N.get(m,'DpPole')==N.get(m,'DpWaves')==N.get(m,'DpPower')==0
            assert N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Bounded genuine Goku linked-menu/Select/Start entry')


def source(raw,limit):
    program=controller(raw);assert H(program)==LUA
    with patch.object(Engine.J,'cold',cold),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit,text=program.decode())


def native(raw):
    program=controller(raw);assert H(program)==LUA
    out=Stock.OUT;candidate,script=out/'candidate.nes',out/'controller.lua';before=script.read_bytes();guard=Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(out.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Stock.run(script,ROM,out/'capture',PIN,230)
        assert q['script_SHA256']==LUA and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--source',action='store_true');g.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=1800);a=p.parse_args();assert 400<=a.limit<=2500
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*a,**k):raise AssertionError('Goku source attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                program=controller(raw);assert H(program)==LUA;q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0)
    print('GOKU_FIRST_FOOD '+json.dumps(q,separators=(',',':')),flush=True);return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
