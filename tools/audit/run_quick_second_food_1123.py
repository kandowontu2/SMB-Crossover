"""Exactffd708 Quick Man natural first and second question-block health food.

Quick's existing no-growth policy selects another Mushroom at X1248; this
does not claim a physical Flower or a new weapon. Source declares linked
native-menu/Select/Start entry. Root alone may run the native shared slot.
No gameplay, actor, health, position or terrain seeds occur after menu entry.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_roll_stock_1123 as Base
from compose_quick_climb_material_1113 import STREAM, COPY_CODE, COOKIE_SITES

Stock,W,N,H,ROM,Engine=Base.Stock,Base.W,Base.N,Base.H,Base.ROM,Base.Engine
PIN=Base.PIN
LUA='04a90fe78655da884340c2a5e2ab3e9bee84f8bf2e9a1c5cde0590bdfafdd2d2'
SOURCE_PROOF={
    'receipt_SHA256':'626ad631d050bcaf6c05c762adb2a823dacb4377f7e3c3c367b7a5269a7c1179',
    'receipt_inner_SHA256':'bb746e0477ca1a2f325c14ed74cfcf05d3999af2f31c551f9ce23fa24be6c0aa',
    'linked_source_passes':1053,'Main_returns':1053,'Quick_returns':1053,
    'second_food_kind':0,'health_before_after':[36,40],'score_before_after':[1200,2200],
    'after_credit_returns':25,'terminal':[1287,176,40,2],
    'scope':'Declared linked menu entry; actual owning CPU; no native cadence claim',
}
TEMPLATE=Stock.R/'tools/playthroughs/battletoads_stock_6a3_1116.lua'

DRIVE=r'''
local jumpLeft,cooldown,wallRelease=0,0,nil
local function jump()
 if #food.pickups>0 and r('QmField_002C')==12 then
  if wallRelease==nil then wallRelease=2;jumpLeft=0 end
  if wallRelease>0 then return false end
  jumpLeft=40;cooldown=48
 else
  wallRelease=nil
  if r('Player_State')==0 and jumpLeft==0 and cooldown==0 then jumpLeft=40;cooldown=48 end
 end
 return jumpLeft>0
end
local function travel(c)
 local b={right=true,b=false,a=jump()}
 if c.x>=950 and c.x<1080 then b.a=false end
 return b
end
local function drive()
 if not menuDone or not active()then buttons={};return end;identity();observe()
 if food.tick~=guestReturns then
  food.tick=guestReturns;jumpLeft=math.max(0,jumpLeft-1);cooldown=math.max(0,cooldown-1)
  if wallRelease then wallRelease=math.max(0,wallRelease-1)end
 end
 if pendingCollect or pendingScore or food.pickups[#food.pickups]and not food.pickups[#food.pickups].resumed then buttons={};return end
 local c=context();local n=#food.pickups+1;local goal=n==1 and 328 or 1240
 local a=target()
 if a then
  food.phase='collect';food.intercept=food.intercept or{}
  food.intercept[n]={state=state(),actor=a}
  local x=a.x-8;buttons={right=c.x<x-1,left=c.x>x+1};return
 end
 if n==2 and not food.secondInjury then
  if not food.initialInvulnerabilityEnded then
   food.waitAt=food.waitAt or guestReturns
   assert(guestReturns-food.waitAt<150,'Original injury protection expires on the first safe floor')
   if r('InjuryTimer')~=0 then buttons={};return end
   food.initialInvulnerabilityEnded=state()
  end
  if c.x>=500 and c.x<1180 and c.grounded and c.y==176 then
   for i=0,5 do local e=actor(i);local dx=e.x-c.x
    if e.flag==1 and(e.id==0 or e.id==3 or e.id==6)and e.state<2 and e.y>=168 and dx>8 and dx<70 then
     local clear=true;for x=c.x+8,e.x+8,8 do if c.block(x,208)==0 or c.block(x,192)~=0 then clear=false end end
     if clear then
      if dx>=16 then buttons={right=true};return end
      if r('A_B_Buttons')&128~=0 or r('PreviousA_B_Buttons')&128~=0 then buttons={};return end
      food.woundRequest={state=state(),actor=e};food.woundUntil=guestReturns+5
      buttons={a=true};return
     end
    end
   end
  end
  assert(c.x<1180,'Real current live enemy causes a health deficit before second food')
 end
 if c.x<goal-8 then
  buttons=travel(c)
  if food.woundUntil and guestReturns<food.woundUntil then buttons.a=true end
  return
 end
 food.phase='head'
 if c.x>goal+2 then buttons={left=true};return end
 if c.x<goal-2 then buttons={right=true};return end
 buttons={a=jump()}
end
'''


def once(text,a,b):
    assert text.count(a)==1,(a,text.count(a));return text.replace(a,b,1)


@lru_cache(maxsize=1)
def bindings(raw):
    assert H(raw)==PIN and COPY_CODE==7168
    b=dict(W.Symbols.bundle(),raw=raw)
    names='''Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State
Player_X_Speed Player_Y_Speed PlayerStatus PlayerFacingDir PreviousA_B_Buttons A_B_Buttons
WorldNumber LevelNumber AreaPointer AreaType GameEngineSubroutine ScreenLeft_X_Pos ScreenLeft_PageLoc
Block_Buffer_1 Enemy_Flag Enemy_ID Enemy_State PowerUpType Enemy_X_Position Enemy_PageLoc Enemy_Y_Position
OperMode OperMode_Task NumberofLives CurrentPlayer FmAlts SelectedCharacter CrossoverBehaviorVersion
CheatInvincible CheatStartLevel CrossoverTitleDrawn DisableScreenFlag CrossoverMenuState CrossoverMenuIndex
TimerControl ScrollLock StarInvincibleTimer GuestPowerupActive Square2SoundQueue FloateyNum_Timer
FloateyNum_Control Player1ScoreDisplay BoundingBox_UL_Corner EnemyBoundingBoxCoord SavedJoypadBits
ObjectOffset InjuryTimer InvPickupOwner InvPickup InvRisePhase QmField_06C0 QmField_0099 QmField_002C
QmField_0023 QmField_0027 QmField_0420'''.split()
    ram={n:W.address(b,n)for n in names};hooks={}
    def add(name,pc,at,work=False):
        hooks[name]=dict(pc=pc,offset=8192+(pc&8191)if work else at-16,bytes=list(raw[at:at+12]),work=work)
    for n in ('GameLoop','UnionPwrUpCore','EraseEnemyObject','SetupFloateyNumber'):
        add(n,W.address(b,n),W.location(b,n))
    for n in ('QhMovement','QhPickup','QhInjury','QhPrepare'):
        pc=W.address(b,n);assert 0xa000<=pc<0xa000+COPY_CODE
        add(n,pc,STREAM+pc-0xa000,True)
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):add('MainReturn'+str(i),pc+delta,at+delta)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=ram['FloateyNum_Timer']
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle]
    assert len(hits)==1;add('StockTimerDEC',pc+hits[0],at+hits[0])
    pc,at=W.address(b,'UnionPwrUpCore'),W.location(b,'UnionPwrUpCore');body=raw[at:at+64]
    for name,patterns in (
        ('SelectRead',(b'\xad'+ram['PlayerStatus'].to_bytes(2,'little'),b'\xa5'+bytes((ram['PlayerStatus']&255,)))),
        ('SelectStore',(b'\x9d'+ram['PowerUpType'].to_bytes(2,'little'),b'\x95'+bytes((ram['PowerUpType']&255,))))):
        found=[i for p in patterns for i in range(len(body)-len(p)+1)if body[i:i+len(p)]==p]
        assert len(found)==1;add(name,pc+found[0],at+found[0])
    cookie=raw[COOKIE_SITES[0]:COOKIE_SITES[0]+16]
    assert all(raw[at:at+16]==cookie for at in COOKIE_SITES)
    assert cookie[:4]==bytes.fromhex('a7092006')
    export=W.address(b,'QhExport');export_code=raw[STREAM+export-0xa000:STREAM+export-0xa000+160]
    zero=b'\xa9\x00\x8d'+W.address(b,'PlayerSize').to_bytes(2,'little')+b'\x8d'+ram['PlayerStatus'].to_bytes(2,'little')
    assert export_code.count(zero)==1,'Actual current QhExport intentionally resets the native growth status'
    pickup=raw[STREAM+W.address(b,'QhPickup')-0xa000:STREAM+W.address(b,'QhPickup')-0xa000+10]
    assert pickup[:4]==bytes((0xb5,ram['PowerUpType'],0xc9,2)),'Current actual Quick kinds0/1 health branch'
    return dict(sha=PIN,key='quick-man',kind='second-food',cycle=2,ram=ram,hooks=hooks,
                cache_hex=raw[STREAM:STREAM+COPY_CODE].hex(),cookie=cookie.hex())


@lru_cache(maxsize=1)
def controller(raw):
    cfg=bindings(raw);text=TEMPLATE.read_text()
    text=once(text,"return n:sub(1,2)=='Bt'and work(at)or read(at)",'return read(at)')
    text=once(text,'3*8192+(at&8191)','8192+(at&8191)')
    text=text.replace("'BtSrc_Objects_Life',r('CurrentPlayer')","'QmField_06C0'")
    text=once(text,"HP=r('QmField_06C0'),lives=", "HP=r('QmField_06C0'),maxHP=r('QmField_0099'),source_state=r('QmField_002C'),lives=")
    text=once(text,"Bt_entries=guestEntries,Bt_returns=guestReturns", "Quick_entries=guestEntries,Quick_returns=guestReturns")
    text=once(text,'full_stage_claim=false','full_stage_claim=false,literal_Flower_claim=false,new_weapon_claim=false,second_question_food=true')
    text=once(text,'local function returning(fn)',"""local function mapping(pc)
 local m=emu.convertAddress(pc);return m and tostring(m.memType)..':'..tostring(m.address)or'cpu:'..tostring(pc)
end
local function returning(fn)""")
    text=once(text,"entryPC=emu.getState()['cpu.pc']}","entryPC=emu.getState()['cpu.pc'],mapping=mapping(pc)}")
    text=once(text,'if t.sp==sp then table.remove(list,i);t.fn(t)end',
              'if t.sp==sp and t.mapping==mapping(pc)then table.remove(list,i);t.fn(t)end')
    text=once(text," assert(r('SelectedCharacter')==33 and r('FmGroups')==64+C.variant and r('BtVariant')==C.variant,'Actual Battletoads identity')", " assert(r('SelectedCharacter')==9 and r('FmAlts')&32~=0,'Actual native Quick Man identity')")
    text=once(text," assert(r('BtHostReady')==1 and r('QmField_06C0')<128,'Living original source')", " assert(r('QmField_0099')==40 and r('QmField_06C0')>0 and r('QmField_06C0')<=40 and r('PlayerStatus')==0,'Living original Quick health/no-growth policy')")
    text=once(text,'poll=guestReturns,char=33,variant=C.variant','poll=guestReturns,char=9,variant=32')
    text=once(text,' if not food.births[n]then',""" if not food.births[n]then
  local h=food.heads[n];assert(h and h.after and h.after.flag==1 and h.after.kind==0 and h.after.x==a.x,
   'The actual native authored head worker returned this exact Mushroom actor')""")
    a=text.index('local function drive()');z=text.index('local function endpoint()',a);text=text[:a]+DRIVE+'\n'+text[z:]
    text=once(text,"r('QmField_06C0')==q.after.HP,'Food HP retained through25 workers'", "r('QmField_06C0')==40 and q.after.HP==40,'Food HP retained through25 actual Quick workers'")
    text=once(text,"'Natural Battletoads '..C.kind..' food and25 actual returned original workers at returned Main'",
              "'Natural Quick Man second-question Mushroom and25 actual returned original workers at returned Main'")
    text=once(text,"   assert(guestEntries==guestReturns and mainEntries==mainReturns,'Balanced actual returns')", """   assert(guestEntries==guestReturns and mainEntries==mainReturns,'Balanced actual returns')
   assert(not pendingCollect and not pendingScore,'All native food/score transactions returned')
   for _,list in pairs(dynamic)do assert(#list==0,'Every observed native worker returned through its exact mapped caller')end""")
    a=text.index("hook('BtConstruct',function()");z=text.index("hook('BtPickup',function()",a)
    text=text[:a]+r'''
hook('QhMovement',function()
 if not food.first_worker then
  for i=1,#C.cache_hex,2 do assert(work(0xa000+(i-1)//2)==tonumber(C.cache_hex:sub(i,i+1),16),'Whole current7168-byte Quick code stream')end
  for i=1,32,2 do assert(emu.read(2*8192+0x1fe0+(i-1)//2,emu.memType.nesWorkRam)==tonumber(C.cookie:sub(i,i+1),16),'Full current16-byte Quick cookie')end
  food.first_worker={pc=emu.getState()['cpu.pc'],sp=emu.getState()['cpu.sp'],bytes=7168,cookie=true}
 end
 assert(not pendingGuest,'Previous original Quick movement returned');guestEntries=guestEntries+1
 pendingGuest=returning(function(t)pendingGuest=nil;guestReturns=guestReturns+1 end)
end)
''' +text[z:]
    text=once(text,"hook('BtPickup'", "hook('QhPickup'")
    text=once(text," observe();local n=#food.pickups+1;", " assert(a.kind==0 and r('InvPickupOwner',i)==9 and r('InvPickup',i)==252,'Genuine authored Quick Mushroom at the native collector')\n observe();local n=#food.pickups+1;")
    text=once(text,"  assert(r('Square2SoundQueue')==32,'Actual grab cue32')", "  assert(r('Square2SoundQueue')==16,'Actual Quick grab cue16')")
    text=once(text,"  assert(q.after.HP==math.min(47,q.before.HP+8),'Actual source food8 cap47')", """  assert(q.after.HP==q.after.maxHP and q.after.HP==40,'Actual native Quick health refill40')
  if n==2 then assert(food.secondInjury and q.before.HP>0 and q.before.HP<40 and q.actor.kind==0,
   'Real second question Mushroom heals a genuinely earned live-enemy deficit')end""")
    text=once(text,"hook('FloateyNumbersCore',function()", "hook('StockTimerDEC',function()")
    text=once(text,' local before=score();pendingScore=returning(function(t)',""" local cpu=emu.getState();assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual timer43/control6 score writer branch')
 q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],timer=r('FloateyNum_Timer',i),control=r('FloateyNum_Control',i)}
 local before=score();pendingScore=returning(function(t)""")
    text=once(text,'local age=0',r'''
food.selection={};food.prepare={}
hook('SelectRead',function()
 local cpu=emu.getState();food.selection[#food.selection+1]={pc=cpu['cpu.pc'],state=state(),slot=cpu['cpu.x'],status=r('PlayerStatus')}
 assert(#food.selection<=2,'Only the two authored normal power blocks')
end)
hook('SelectStore',function()
 local cpu=emu.getState();local q=food.selection[#food.selection];assert(q and q.status==0 and cpu['cpu.a']==0,'Real status0 selects physical Mushroom0')
 q.store={pc=cpu['cpu.pc'],slot=cpu['cpu.x'],A=cpu['cpu.a'],state=state()}
end)
hook('QhPrepare',function()
 local cpu=emu.getState();local i=cpu['cpu.x'];local q={pc=cpu['cpu.pc'],state=state(),before=actor(i)};food.prepare[#food.prepare+1]=q
 returning(function(t)
  q.after=actor(i);q.return_pc=t.pc;q.return_sp=t.sp
  assert(q.after.kind==0 and r('InvPickupOwner',i)==9 and r('InvPickup',i)==252 and r('InvRisePhase',i)==0,'Actual native Quick Mushroom preparation')
 end)
end)
hook('QhInjury',function()
 if #food.pickups~=1 or not food.pickups[1].resumed or food.secondInjury then return end
 local a=actor(r('ObjectOffset'));local before=state()
 returning(function(t)
  local after=state();if after.HP<before.HP then
   assert(before.HP==40 and after.HP==36 and a.flag==1 and a.state<32,'A naturally spawned live enemy causes original4HP injury')
   food.secondInjury={before=before,after=after,actor=a,pc=t.entryPC,return_pc=t.pc,return_sp=t.sp}
  end
 end)
end)
local age=0''')
    text=once(text," press('left');press('down');press('down');for i=1,C.cycle do press('select')end", " press('down');press('right');for i=1,C.cycle do press('select')end")
    text=once(text," assert(r('CrossoverMenuIndex')==23 and r('SelectedCharacter')==33 and r('FmGroups')==64+C.variant,'Actual compiled Battletoads selection')", " assert(r('CrossoverMenuIndex')==9 and r('SelectedCharacter')==9 and r('FmAlts')&32~=0,'Actual compiled Quick Man selection')")
    text=once(text,'Exact owning6a3 environment','Exact owningffd708 environment')
    text=once(text,'Bounded natural Battletoads food policy','Bounded natural Quick health-food policy')
    program='local C='+Stock.value(cfg)+'\n'+text
    assert 'Bt'not in program and not any(s in program for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    Stock.LuaRuntime().compile(program);return program.encode()


def cold(raw):
    cfg=bindings(raw);b=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for pad in(4,1,32,32):W.UI.key(m,pad)
    assert W.UI.menu_name(m)[0]=='QUICK MAN'and N.get(m,'SelectedCharacter')==9 and N.get(m,'FmAlts')&32
    start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Base.Host.Family.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert bytes(m.ram[1][:COPY_CODE])==raw[STREAM:STREAM+COPY_CODE]
            assert bytes(m.ram[2][0x1fe0:0x1ff0]).hex()==cfg['cookie']
            assert N.get(m,'QmField_06C0')==N.get(m,'QmField_0099')==40 and N.get(m,'NumberofLives')==2
            assert N.get(m,'CrossoverBehaviorVersion')==N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
            return m
        m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Bounded genuine Quick linked-menu/Select/Start entry')


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
    p.add_argument('--limit',type=int,default=3000);a=p.parse_args();assert 1200<=a.limit<=4200
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw)
    else:
        def deny(*a,**k):raise AssertionError('Quick source attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                program=controller(raw);assert H(program)==LUA;q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0,literal_Flower_claim=False,new_weapon_claim=False)
    print('QUICK_SECOND_FOOD '+json.dumps(q,separators=(',',':')),flush=True);return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
