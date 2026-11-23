"""Exactffd708 ordinary Battletoads M->second-question Flower investigation.

The retained91dc Mushroom/1-UP/Star/full native passes keep their own scope.
This separate source-only-by-default replay observes actual selection bytes,
loaded private code, native food/contact/credit and original worker returns.
The default second-food scope keeps the real Mushroom reward and requires
a new live-enemy health deficit; selection retains the literal-Flower negative.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
from unittest.mock import patch

import run_grant_stock_1123 as Host
import inspect_rogue_missile_targets_cb95_1116 as Engine
from check_ff_stdout_controller_source_1110 import LuaRuntime
from replay_sonic_hidden_life_f7c9_1116 import value

W,N,H,ROM,R,OUT=Host.W,Host.N,Host.H,Host.ROM,Host.Stock.R,Host.Stock.OUT
PIN='ffd7081036bca9cb165d9f4c5527e909126df70f993b4ebec75b7dd7ac83a6b1'
CACHE,COOKIE=1989648,765863
PINS={
 ('rash','selection'):'eb12d492870aad3e0fff8bf381f5c9308a3c7ff0471ccd3449e2f9a82501bd74',
 ('zitz','selection'):'6e2b26525b43ee56048c20515c90f942c29ce3eb5939bba003d5d605230ab0d9',
 ('rash','second-food'):'f404e1d4bebaaed617c753074822196c9a9777e24436b9f5396c5b9582d7a3ec',
 ('zitz','second-food'):'f993e0b3c487cf8dd3c019eb39155ee1e9b2a268fbb88660dbb3f41b4d092de9',
}
FORMS={'rash':('RASH',0,0),'zitz':('ZITZ',1,32)}
SCOPES=('selection','second-food')
TEMPLATE=R/'tools/playthroughs/battletoads_stock_6a3_1116.lua'
TRAVEL=R/'tools/playthroughs/full_roster_policy_og.lua'
ALIGN=R/'tools/playthroughs/battletoads_food_align_6a3_1116.lua'
INTERCEPT=R/'tools/playthroughs/battletoads_food_intercept_6a3_1116.lua'
RAM_NAMES='''Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State
Player_X_Speed Player_Y_Speed PlayerStatus PlayerSize PlayerFacingDir PreviousA_B_Buttons
WorldNumber LevelNumber AreaPointer AreaType AreaAddrsLOffset GameEngineSubroutine
ScreenLeft_X_Pos ScreenLeft_PageLoc Block_Buffer_1 Enemy_Flag Enemy_ID Enemy_State PowerUpType
Enemy_X_Position Enemy_PageLoc Enemy_Y_Position OperMode OperMode_Task NumberofLives
CurrentPlayer FmGroups SelectedCharacter CrossoverBehaviorVersion CheatInvincible CheatStartLevel
CrossoverTitleDrawn DisableScreenFlag CrossoverMenuState CrossoverMenuIndex TimerControl
ScrollLock StarInvincibleTimer GuestPowerupActive GuestPowerupAge Square2SoundQueue
FloateyNum_Timer FloateyNum_Control Player1ScoreDisplay BoundingBox_UL_Corner EnemyBoundingBoxCoord
BtHostReady BtVariant BtSrc_Objects_Life BtSrc_Objects_death_timer BtSrc_FrameCounter SavedJoypadBits'''.split()


def once(text,a,b):
    assert text.count(a)==1,(a,text.count(a))
    return text.replace(a,b,1)


@lru_cache(maxsize=4)
def bindings(raw,key,scope='selection'):
    assert H(raw)==PIN and key in FORMS and scope in SCOPES
    b=dict(W.Symbols.bundle(),raw=raw);name,cycle,variant=FORMS[key]
    ram={n:W.address(b,n)for n in RAM_NAMES};hooks={}
    if scope=='second-food':
        for n in('ObjectOffset','InjuryTimer'):ram[n]=W.address(b,n)
    def add(name,pc,at,work=False):
        hooks[name]=dict(pc=pc,offset=3*8192+(pc&8191)if work else at-16,bytes=list(raw[at:at+8]),work=work)
    for n in ('GameLoop','UnionPwrUpCore','EraseEnemyObject','SetupFloateyNumber','FloateyNumbersCore'):
        add(n,W.address(b,n),W.location(b,n))
    for n in ('BtCoreStep','BtPickup','BtFoodHeal','BtConstruct'):
        pc=W.address(b,n);add(n,pc,CACHE+(pc&8191),True)
    pc=W.address(b,'BtCacheServices')+3*20;add('BtPrepare20',pc,CACHE+(pc&8191),True)
    if scope=='second-food':
        pc=W.address(b,'BtInjury');add('BtInjury',pc,CACHE+(pc&8191),True)
    pc,at=W.address(b,'IdleLoop'),W.location(b,'IdleLoop');call=b'\x20'+W.address(b,'GameLoop').to_bytes(2,'little')
    returns=[i+3 for i in range(61)if raw[at+i:at+i+3]==call];assert len(returns)==2 and returns[0]==12
    for i,delta in enumerate(returns):add('MainReturn'+str(i),pc+delta,at+delta)
    pc,at=W.address(b,'FloateyNumbersCore'),W.location(b,'FloateyNumbersCore');timer=ram['FloateyNum_Timer']
    needle=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0));hits=[i for i in range(120-len(needle))if raw[at+i:at+i+len(needle)]==needle]
    assert len(hits)==1 and pc+hits[0]==0x897c;add('StockTimerDEC',pc+hits[0],at+hits[0])
    pc,at=W.address(b,'UnionPwrUpCore'),W.location(b,'UnionPwrUpCore');body=raw[at:at+64]
    for name,needles in (
        ('SelectRead',(b'\xad'+ram['PlayerStatus'].to_bytes(2,'little'),b'\xa5'+bytes((ram['PlayerStatus']&255,)))),
        ('SelectStore',(b'\x9d'+ram['PowerUpType'].to_bytes(2,'little'),b'\x95'+bytes((ram['PowerUpType']&255,))))):
        hits=[i for pattern in needles for i in range(len(body)-len(pattern)+1)if body[i:i+len(pattern)]==pattern]
        assert len(hits)==1,(name,hits);add(name,pc+hits[0],at+hits[0])
    return dict(sha=PIN,key=key,kind='second-food'if scope=='second-food'else'flower',name=FORMS[key][0],cycle=cycle,variant=variant,ram=ram,hooks=hooks,
                cookie=raw[COOKIE:COOKIE+16].hex(),cache_hex=raw[CACHE:CACHE+0x1fe0].hex())


@lru_cache(maxsize=4)
def controller(raw,key,scope='selection'):
    cfg=bindings(raw,key,scope)
    assert H(TRAVEL.read_bytes())=='17d3a38d53fe09b930048f081938bf707028f765577207bce41777ea4f5edb7b'
    travel=once(TRAVEL.read_text(),'b.b=c.poll%8<2','b.b=near and e.dx<48 and c.poll%32<2')
    travel=once(travel,"local phase='approach';local clock=0;","local phase='route';local clock=0;")
    text=once(TEMPLATE.read_text()," if food.phase=='mushroom'then buttons=travel(c);return end",ALIGN.read_text())
    first=text.index(" elseif food.phase=='mushroom-collect'then");last=text.index(" if food.phase=='flower-travel'then",first)
    text=text[:first]+INTERCEPT.read_text()+'\n'+text[last:]
    text=once(text,"hook('FloateyNumbersCore',function()","hook('StockTimerDEC',function()")
    text=once(text,' local before=score();pendingScore=returning(function(t)',""" local cpu=emu.getState();assert(cpu['cpu.a']==43 and cpu['cpu.y']==6,'Actual timer43/control6 credit branch')
 q.credit_writer={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],slot=i,timer=r('FloateyNum_Timer',i),control=r('FloateyNum_Control',i),state=state()}
 local before=score();pendingScore=returning(function(t)""")
    text=once(text,'local age=0',"""food.selection={};food.prepare20={}
hook('BtPrepare20',function()
 local cpu=emu.getState();food.prepare20[#food.prepare20+1]={pc=cpu['cpu.pc'],sp=cpu['cpu.sp'],state=state(),actor=actor(cpu['cpu.x'])}
 assert(#food.prepare20<=3,'Bounded actual native preparation callbacks')
end)
hook('SelectRead',function()
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 food.selection[#food.selection+1]={read_pc=cpu['cpu.pc'],state=state(),actor=a,status=r('PlayerStatus')}
 assert(#food.selection<=3,'Bounded real food selector calls')
end)
hook('SelectStore',function()
 local cpu=emu.getState();local q=food.selection[#food.selection];assert(q,'Real status load precedes type store')
 q.store={pc=cpu['cpu.pc'],A=cpu['cpu.a'],P=cpu['cpu.ps'],slot=cpu['cpu.x'],state=state()}
end)
local age=0""")
    if scope=='second-food':
        text=once(text,"  if c.x<1180 then buttons=travel(c);return end", """  if not food.secondInjury then
   if not food.initialInvulnerabilityEnded then
    food.initialInvulnerabilityWait=food.initialInvulnerabilityWait or guestReturns
    assert(guestReturns-food.initialInvulnerabilityWait<1200,'Original injury timer naturally expires on safe floor')
    if r('InjuryTimer')~=0 then buttons={};return end
    food.initialInvulnerabilityEnded=state()
   end
   if not food.woundTarget and c.x>=500 and c.x<1180 and c.grounded and c.y==176 then
    for i=0,5 do local a=actor(i);local dx=a.x-c.x
     if a.flag==1 and(a.id==0 or a.id==3 or a.id==6)and a.state<2 and a.y>=168 and dx>8 and dx<80 then
      local clear=true
      for x=c.x+8,a.x+8,8 do if c.block(x,208)==0 or c.block(x,192)~=0 then clear=false end end
      if clear then food.woundTarget={state=state(),actor=a,at=guestReturns};break end
     end
    end
   end
   if food.woundTarget then
    local a=actor(food.woundTarget.actor.slot)
    food.woundLatest={state=state(),actor=a,injuryTimer=r('InjuryTimer')}
    if a.flag~=1 or a.state>=2 then food.woundTarget=nil;buttons=travel(c);buttons.b=false;return end
    assert(guestReturns-food.woundTarget.at<220,'Live floor enemy reaches the standing original body')
    if not food.woundTarget.jump and c.grounded and not c.lastA and math.abs(a.x-c.x)<40 then
     food.woundTarget.jump=guestReturns
    end
    local dx=a.x-c.x
    buttons={right=dx>16,left=dx< -16,a=food.woundTarget.jump and guestReturns-food.woundTarget.jump<5};return
   end
   assert(c.x<1180,'A genuine floor enemy deficit precedes the second food')
  end
  if c.x<1180 then buttons=travel(c);if not food.secondInjury then buttons.b=false end;return end""")
        text=once(text,"   assert(a.kind==1,'Second authored question produced Mushroom because native PlayerStatus stayed0; Flower not acquired')",
                  "   assert(a.kind==0 and food.secondInjury,'Actual second question produces original healing Mushroom food')")
        first=text.index(" elseif food.phase=='flower-collect'then");last=text.index('\nend\nlocal function endpoint()',first)
        text=text[:first]+""" elseif food.phase=='flower-collect'then
  local a=target();assert(a,'The genuinely revealed second food remains until physical collection')
  assert(guestReturns-food.headAt<500,'Bounded real second-food interception')
  buttons={right=c.x<1302,left=c.x>1306}
  food.secondIntercept=food.secondIntercept or{state=state(),actor=a,target_x=1304}
 end"""+text[last:]
        text=once(text,"  q.after=state();q.return_pc=t.pc;q.return_sp=t.sp", """  q.after=state();q.return_pc=t.pc;q.return_sp=t.sp
  if n==2 then assert(food.secondInjury and q.actor.kind==0 and q.before.HP>0 and q.before.HP<47 and q.after.HP==math.min(47,q.before.HP+8),
   'Actual second authored Mushroom heals a new live-enemy deficit with original8/cap47')end""")
        text=once(text,'food.selection={};food.prepare20={}',"""food.selection={};food.prepare20={}
hook('BtInjury',function()
 if not food.woundTarget or food.secondInjury then return end
 local a=actor(r('ObjectOffset'));local before=state()
 returning(function(t)
  local after=state()
  if after.HP<before.HP then
   assert(before.HP==47 and after.HP==43 and a.flag==1 and a.state<32 and a.slot==food.woundTarget.actor.slot,
    'A naturally spawned active enemy causes the new original4HP deficit')
   food.secondInjury={before=before,after=after,actor=a,pc=t.entryPC,return_pc=t.pc,return_sp=t.sp}
  end
 end)
end)""")
        text=once(text,'full_stage_claim=false','full_stage_claim=false,literal_Flower_claim=false,second_question_food=true')
    program='local C='+value(cfg)+"\nlocal ROSTER_CONFIG={name="+value(key)+"}\nlocal travel=(function()\n"+travel+'\nend)()\n'+text
    assert not any(s in program for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(program)
    return program.encode()


def cold(raw,key,scope='selection'):
    cfg=bindings(raw,key,scope);b=dict(W.Symbols.bundle(),raw=raw)
    expected=bytearray(raw[CACHE:CACHE+8192]);expected[0x1fe0:0x1ff0]=raw[COOKIE:COOKIE+16]
    entry=W.address(b,'BtConstruct');reads=[];base=N.NesMPU
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc==entry and m.rawtags[(entry-0x8000)//8192]==3 and not reads:
                assert bytes(m.ram[3])==expected,'Actual8192-byte loaded current BT cache and full16 cookie before constructor'
                reads.append(dict(pc=self.pc,sp=self.sp,bytes=8192,SHA256=H(bytes(m.ram[3]))))
            return super().step()
    with patch.object(N,'Bus',W.ControllerBus),patch.object(N,'NesMPU',CPU):
        m=W.UI.seed(b,0)
        for pad in [2,4,4]+[32]*cfg['cycle']:W.UI.key(m,pad)
        assert W.UI.menu_name(m)[0]==FORMS[key][0]and N.get(m,'SelectedCharacter')==33
        start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Host.Family.Layout.NEW_PAUSE))))
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
                assert reads and m.ram[3][cfg['ram']['BtHostReady']&8191]==1
                assert m.ram[3][cfg['ram']['BtVariant']&8191]==cfg['variant']
                assert m.ram[3][cfg['ram']['BtSrc_Objects_Life']&8191]==47
                assert N.get(m,'NumberofLives')==2 and N.get(m,'CrossoverBehaviorVersion')==0
                assert N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
                return m
            m.controller_pad=0;Engine.Frames.frame(m,cold=True)
    raise AssertionError('Genuine Battletoads linked menu/Start/constructor bound')


def source(raw,key,limit,scope='selection'):
    program=controller(raw,key,scope);assert H(program)==PINS[(key,scope)]
    with patch.object(Engine.J,'cold',lambda image:cold(image,key,scope)),patch.object(Engine.J,'PIN',PIN):return Engine.run(raw,limit,text=program.decode())


def native(raw,key,scope):
    program=controller(raw,key,scope);assert H(program)==PINS[(key,scope)]
    candidate,script=OUT/'candidate.nes',OUT/'controller.lua';before=script.read_bytes();guard=Host.Stock.check(ROM)
    assert guard['ROM_sha256']==PIN and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script}and candidate.read_bytes()==raw
    try:
        with Host.Stock.preserve_script(script,candidate,raw)as stage:stage(program);q=Host.Stock.run(script,ROM,OUT/'capture',PIN,240)
        assert q['script_SHA256']==PINS[(key,scope)]and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and Host.Stock.check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=FORMS,default='rash')
    p.add_argument('--scope',choices=SCOPES,default='second-food')
    mode=p.add_mutually_exclusive_group();mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=2600);a=p.parse_args();assert 1000<=a.limit<=4000
    raw=ROM.read_bytes();assert H(raw)==PIN
    if a.run:q=native(raw,a.form,a.scope)
    else:
        def deny(*a,**k):raise AssertionError('Battletoads source attempted outputs/emulator')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.form,a.limit,a.scope)
            else:
                program=controller(raw,a.form,a.scope);assert H(program)==PINS[(a.form,a.scope)]
                q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program),route_executed=False,outputs=0)
    print('BATTLETOADS_FLOWER '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
