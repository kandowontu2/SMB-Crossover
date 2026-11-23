"""Natural first Mushroom-block replay for Easy Link/Zelda II Link on exact14b.

Only controller inputs are sent. Source mode runs the same Lua hooks against
the linked CPU in RAM; --run is Root's serial, two-file-slot native entry.
Historical staged reward campaigns remain separate from this natural route.
"""
import argparse,json
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch

from check_ff_stdout_controller_source_1110 import LuaRuntime
from current_ice_stock_binding_1122 import RAM_FIELDS
import compose_dkjr_sonic_dispatch_1123 as Current
import profile_sonic_empty_cpu_1110 as Linked
from replay_sonic_hidden_life_f7c9_1116 import value
from run_mario_luigi_stock_native_1122 import H,OUT,R,ROM,preserve_script
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

PIN=Current.CANDIDATE
FORMS={'link':(0,'LINK'),'zelda2':(1,'ZELDA II LINK')}
W,N=Linked.W,Linked.N
OBSERVER=R/'tools/audit/ice_climbers_stock_observer_1122.lua'
OPENING=R/'tools/playthroughs/link_simon_ryu_policy.lua'
PINS={'link':'073c3b9162b67db2d6dcb7b5ec50584070c449089bf018618c8c0018c47b1814',
      'zelda2':'52aedec898ac32db689205e65a8c441194aa1c8decbac2972f75f98617fc928f'}
POLICY=r'''
local hopUntil=0
return function(c)
 if c.status>0 then return{}end
 local b=opening(c)
 -- Keep the first-block route moving with normal inputs. Clear the
 -- original opening Goomba with a held jump rather than a ground attack.
 b.b=false
 local e=c.enemy()
 if c.x<300 and c.grounded and not c.lastA and e and e.dx>0 and e.dx<=68
    and math.abs(e.y-c.y)<40 then hopUntil=c.update+30 end
 if c.update<hopUntil then b.a=true end
 return b
end
'''
PURSUIT_PIN='0d6faf0d25cc669c68ce1a6b39617be5a0a8d6cec3747b51699a7b1ef124efa6'
PURSUIT=r'''
local T={phase='reference',events={}}
Z2_MUSHROOM_PURSUIT=T
local function sample(c,a)
 return{update=c.update,x=c.x,y=c.y,state=c.state,lastA=c.lastA,camera=c.camera,item=a}
end
local function item(c)
 for i=0,5 do
  if c.r('Enemy_Flag',i)>0 and c.r('Enemy_ID',i)==46
     and c.r('InvPickupOwner',i)==4 and c.r('InvPickup',i)==0xc0 then
   return{slot=i,x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i),
          y=c.r('Enemy_Y_Position',i),state=c.r('Enemy_State',i),
          kind=c.r('PowerUpType',i),food=c.r('InvPickupSaveLo',i)}
  end
 end
end
local function phase(c,p,a)
 if T.phase==p then return end
 assert(#T.events<24,'Bounded first-food pursuit phases')
 T.phase=p;T.events[#T.events+1]={phase=p,sample=sample(c,a)}
end
local function steer(c,target)
 return{right=c.x<target-2,left=c.x>target+2}
end
return function(c)
 if c.status>0 then phase(c,'earned');return{}end
 local a=item(c)
 if not a then
  assert(not T.seen,'The authored Jump food disappeared before contact')
  return referenceChoose(c)
 end
 T.seen=T.seen or sample(c,a)
 T.latest=sample(c,a)
 if T.lastX and a.x~=T.lastX then T.direction=a.x>T.lastX and 1 or-1 end
 T.lastX=a.x
 local nextPhase='visible-rise'
 if a.state&128~=0 then
  T.mature=T.mature or sample(c,a)
  assert(c.update-T.mature.update<720,'Bounded mature first-food pursuit')
  nextPhase=a.y<156 and'follow-high-food'or'floor-contact'
 end
 -- Release A from the bump immediately. The uncast Zelda II jump cannot
 -- meet the old policy's Y<=112 mounting threshold; following a food that
 -- walks/falls off the real row avoids an endless vertical-rise loop.
 local target=math.max(c.camera+2,math.min(424,a.x-4))
 if c.grounded and c.y<=144 then
  -- If the bump landed on top, walk off a genuine row edge before pursuit.
  target=(T.direction or 1)<0 and math.max(c.camera+2,300)or 404
  nextPhase='land-off-row'
 end
 phase(c,nextPhase,a)
 local b=steer(c,target)
 b.a=false;b.b=false
 return b
end
'''


@lru_cache(maxsize=2)
def bindings(raw,form):
    assert H(raw)==PIN
    variant,name=FORMS[form];bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(bundle,4)
    for _ in range(variant):W.UI.key(menu,32)
    assert W.UI.menu_name(menu)[0]==name
    assert(N.get(menu,'CrossoverMenuIndex'),N.get(menu,'SelectedCharacter'),N.get(menu,'Z2Variant'))==(4,4,variant)
    names=[n for n in RAM_FIELDS if not n.startswith('Ic')]
    names+=['GamePauseStatus','Z2Variant','Z2PreviousButtons','Z2LearnedSpells','Z2Selection',
            'Z2ActiveSpells','Z2Hp','Z2HpPending','GuestPowerupActive','GuestPowerupTarget',
            'InvPickup','InvPickupOwner','InvPickupSaveLo','InvOwnedLo','InvOwnedHi','RgDoubleJump',
            'PlayerScoreDisplay','GuestLegacyHurt','RgAttack','Enemy_BoundBoxCtrl']
    ram={n:W.address(bundle,n)for n in names}
    hooks={}
    for key,symbol in(('GameLoop','GameLoop'),('Movement','Z2Movement'if variant else'RosterMovement'),
                       ('HandlePowerUpCollision','MarioSourcePowerupCollision'),('PlayerHeadCollision','PlayerHeadCollision')):
        pc,at=W.address(bundle,symbol),W.location(bundle,symbol);bank=(at-16)//8192
        assert at-16==bank*8192+(pc&8191)
        hooks[key]=dict(pc=pc,tag=bank|128,offset=at-16,hex=raw[at:at+12].hex())
    menu_start=16+124*8192
    helpers={0xa000:'088a2907d0058a0907d003ca8ae828090060',
             0xa012:'08e88a2907f0058aca4c0ea0ca8a29184c0ea0',
             0xa080:'2086a0491060',0xa086:'088a186908291f28090060'}
    for pc,hexcode in helpers.items():
        at=menu_start+(pc&8191);assert raw[at:at+len(bytes.fromhex(hexcode))]==bytes.fromhex(hexcode)
    edges={'left':[(i&24)|((i-1)&7)for i in range(32)],'right':[(i&24)|((i+1)&7)for i in range(32)],
           'up':[(i-8)&31 for i in range(32)],'down':[(i+8)&31 for i in range(32)]}
    navigation=[]
    for start in range(32):
        queue,seen=[(start,[])],{start}
        for node,path in queue:
            if node==4:navigation.append(path[0]if path else'');break
            for key,table in edges.items():
                nxt=table[node]
                if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[key]))
        else:raise AssertionError('Compiled menu graph')
    return dict(sha=PIN,form=form,name=name,char=4,slot=4,variant=variant,mode_value=0,
                route='mushroom',expected=[0],ram=ram,hooks=hooks,navigation=navigation)


def controller(raw,form,*,pursuit=False):
    assert not pursuit or form=='zelda2'
    cfg=bindings(raw,form);text=OBSERVER.read_text();edits=[]
    def edit(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b,1);edits.append((a,b))
    edit("assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha","assert(CPU_CONTROLLER_OPENING or os.getenv('SMB_STDOUT_ROM_SHA')==C.sha")
    edit("r('SelectedCharacter')==20 and r('IcVariant')==C.variant","r('SelectedCharacter')==4 and r('Z2Variant')==C.variant")
    edit("r('IcVariant')~=C.variant","r('Z2Variant')~=C.variant")
    edit("local expected=C.route=='life' and {0,3} or {0,1,2}","local expected=C.expected")
    edit("kind=r('PowerUpType',i),","kind=C.variant==1 and 0 or r('PowerUpType',i),nativeKind=r('PowerUpType',i),stamp=r('InvPickup',i),owner=r('InvPickupOwner',i),food=r('InvPickupSaveLo',i),")
    edit("power=r('IcPower')","power=r('PlayerStatus'),growth=r('GuestPowerupActive'),learned=r('Z2LearnedSpells'),selection=r('Z2Selection'),hp=r('Z2Hp'),hpPending=r('Z2HpPending')")
    edit('c.poll=polls;c.char=20;','c.poll=updates;c.char=4;c.update=updates;')
    edit('c.lastA=mask&128~=0',"c.lastA=(C.variant==1 and r('Z2PreviousButtons')or r('PreviousA_B_Buttons'))&128~=0")
    edit('local lifePending','local lifePending\nlocal clockInput={}\nlocal cue=0\nlocal function score()local n=0;for i=0,5 do n=n*10+r("PlayerScoreDisplay",i)end;return n end')
    edit('Living Ice Climber','Living requested Link form')
    edit("assert(updates<5100,'Bounded pickup route')","assert(updates<1600 and s.yHigh<2 and s.lives==2 and(C.variant==0 or s.hp>0),'Bounded living first-block route')")
    edit('q.birth={actor=a,player=s}',"assert(heads['0'],'Actual authored first block bump');q.birth={actor=a,player=s}")
    edit('local a=actor(i);local q=checks[tostring(a.kind)]',"local a=actor(i);local q=checks[tostring(a.kind)]\n  if q and q.birth and a.id==46 and a.slot==q.birth.actor.slot and a.flag>0 and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end")
    edit(' local complete=true',''' local q=checks['0']
 if q.collect and not q.grant and s.status==1 and s.growth==0 and score()>=q.collect.score_before+1000 then
  assert(C.variant==0 or(s.learned&2~=0 and s.selection&7==1),'Original Jump reward persists')
  q.grant=s
 end
 local complete=true''')
    edit("else assert(s.power==q.grant.power and s.status==q.grant.status,'Upgrade persists during movement') end","else assert(s.status==1 and s.growth==0 and(C.variant==0 or s.learned&2~=0),'Earned Link reward persists during movement')end")
    edit('if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope() then','if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()and s.state==0 then')
    edit("if complete then finish(true,'Authored pickups, native credit and 25 further movement updates') end","if complete then finish(true,'Natural first Mushroom block, original reward and25 living movement returns');return end\n clockInput=scope()and choose(context())or{}")
    edit("assert(r('Square2SoundQueue')&32~=0,'Actual pickup cue')","assert(cue>p.cue,'New actual native pickup cue')")
    edit("sound=r('Square2SoundQueue')}","sound=r('Square2SoundQueue'),score_before=p.score}")
    edit("assert(p.before.power==a.kind and s.power==a.kind+1 and s.status==s.power,'Normal Ice power tier transition')",'''if C.variant==0 then
   assert(p.before.status==0 and s.growth~=0 and r('GuestPowerupTarget')==1,'Original Easy Link growth begins')
  else
   assert(a.stamp==0xc0 and a.owner==4 and a.food==0x81,'Authentic first Jump food from Mushroom block')
   assert(p.before.learned&2==0 and s.learned&2~=0 and s.selection&7==1 and s.status==1,
          'Actual contact grants original Jump reward')
   q.collect.adaptation='Existing Z2 first Mushroom block: C0 Jump food, original visible rise, natural walk/fall and contact; Mushroom healing is queued'
  end''')
    edit(' q.grant=s\nend',' -- Grant waits for native score and completed original growth/reward.\nend')
    edit("if p.name=='IcMovement' then motor=motor+1","if p.name=='Movement' then if p.movement and scope()and r('TimerControl')==0 and r('GamePauseStatus')&1==0 then motor=motor+1 end")
    edit(" if name=='HandlePowerUpCollision' then"," if name=='Movement'then p.movement=scope()and r('TimerControl')==0 and r('GamePauseStatus')&1==0 end\n if name=='HandlePowerUpCollision' then")
    edit('  p.actor=a;p.before=state()',"  assert(a.state&128~=0,'Mature real item before native erase');q.mature=q.mature or{actor=a,player=state()}\n  p.actor=a;p.before=state();p.score=score();p.cue=cue")
    edit('phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0','cue_count=cue,pending_returns=#pending,controller_only=true,game_state_writes=false,files=0,images=0')
    edit("local bits={a=128","emu.addMemoryCallback(guarded('Pickup cue',function(_,v)if entered and v==32 then cue=cue+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)\nlocal bits={a=128")
    edit('local b=not entered and menu() or (scope() and choose(context()) or {})','local b=not entered and menu()or(scope()and clockInput or{})')
    edit('  entered=physical','  entered=physical;clockInput=choose(context())')
    restored=text
    for a,b in reversed(edits):assert restored.count(b)==1;restored=restored.replace(b,a,1)
    assert restored==OBSERVER.read_text()
    if pursuit:
        text=text.replace('cue_count=cue,pending_returns=#pending,',
                          'pursuit=Z2_MUSHROOM_PURSUIT,cue_count=cue,pending_returns=#pending,',1)
    choose=('local referenceChoose=(function()\n'+POLICY+'\nend)()\n'
            'local choose=(function()\n'+PURSUIT+'\nend)()')if pursuit else(
            'local choose=(function()\n'+POLICY+'\nend)()')
    program='\n'.join(('local C='+value(cfg),'ROSTER_CONFIG={name="'+form+'"}',
                       'local opening=(function()\n'+OPENING.read_text()+'\nend)()',
                       choose,text))
    assert not any(token in program for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    LuaRuntime().compile(program)
    expected=PURSUIT_PIN if pursuit else PINS[form]
    if expected is not None:assert H(program.encode())==expected,('Frozen Link controller changed',form,pursuit)
    return program


def cold(raw,form):
    cfg=bindings(reference(raw),form);bundle=dict(W.Symbols.bundle(),raw=raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(bundle,4)
    for _ in range(cfg['variant']):W.UI.key(m,32)
    assert W.UI.menu_name(m)[0]==cfg['name']
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    import check_contra_force_fast_ingress_1122 as Fast
    old=m.bundle['syms']['PauseRoutine'];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Fast.Layout.NEW_PAUSE))))
    N.invoke(m,'PauseRoutine',a=0)
    import check_bub_current_budget_1113 as Frames
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            assert N.get(m,'PlayerStatus')==0 and N.get(m,'NumberofLives')==2
            assert N.get(m,'Z2Variant')==cfg['variant'] and N.get(m,'CrossoverBehaviorVersion')==0
            return m
        m.controller_pad=0;Frames.frame(m,cold=True)
    raise AssertionError('Actual Link cold bound')


def source(raw,form,limit,*,pursuit=False):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    program=native_program(raw,form,pursuit=pursuit).decode()
    seed={}
    def enter(image):
        seed['machine']=cold(image,form)
        return seed['machine']
    with patch.object(Engine.J,'cold',enter),patch.object(Engine.J,'PIN',H(raw)):
        result=Engine.run(raw,limit,text=program)
    m=seed['machine']
    result['terminal_diagnostic']={n:N.get(m,n)for n in
        ('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_State',
         'PlayerStatus','GuestPowerupActive','NumberofLives','GameEngineSubroutine',
         'Z2Variant','Z2LearnedSpells','Z2Selection','SavedJoypadBits','PreviousA_B_Buttons')}
    return result


def reference(raw):
    if H(raw)==PIN:return raw
    import compose_dkjr_public_side_forward_1123 as Side
    assert H(raw)==Side.CANDIDATE
    old=Side.inverse(raw)
    assert H(old)==PIN
    return old


def native_program(raw,form,*,pursuit=False):
    """Exact94fa changes only the ROM identity after old hook-byte equality."""
    old=reference(raw);program=controller(old,form,pursuit=pursuit).encode()
    for hook in bindings(old,form)['hooks'].values():
        at=16+hook['offset'];expected=bytes.fromhex(hook['hex'])
        assert old[at:at+len(expected)]==raw[at:at+len(expected)]==expected
    if H(raw)==PIN:return program
    before,after=PIN.encode(),H(raw).encode()
    assert program.count(before)==1
    changed=program.replace(before,after,1)
    assert changed.replace(after,before,1)==program
    LuaRuntime().compile(changed.decode())
    return changed


def native(raw,form,*,pursuit=False):
    program=native_program(raw,form,pursuit=pursuit);expected=H(raw)
    guard=check(ROM);candidate,script=OUT/'candidate.nes',OUT/'controller.lua'
    assert guard['ROM_sha256']==expected and not guard['matching_patch_files']
    assert set(OUT.iterdir())=={candidate,script} and candidate.read_bytes()==raw
    before=script.read_bytes()
    try:
        with preserve_script(script,candidate,raw)as stage:
            stage(program);q=run(script,ROM,OUT/'capture',expected,180)
        print('LINK_FIRST_NATIVE '+json.dumps(q,separators=(',',':')),flush=True)
        assert q['script_SHA256']==H(program)and q['outputs_written']==0 and not q['images']
    finally:
        assert script.read_bytes()==before and candidate.read_bytes()==raw and ROM.read_bytes()==raw and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--form',choices=tuple(FORMS),default='link')
    p.add_argument('--pursuit',action='store_true',help='Separate Zelda II food-following/landing policy; short reference stays pinned')
    group=p.add_mutually_exclusive_group();group.add_argument('--source',action='store_true');group.add_argument('--run',action='store_true')
    p.add_argument('--limit',type=int,default=1500);a=p.parse_args();assert 500<=a.limit<=1600
    raw=ROM.read_bytes()
    assert not a.pursuit or a.form=='zelda2'
    if a.run:
        return int(not native(raw,a.form,pursuit=a.pursuit)['passed'])
    def deny(*args,**kwargs):raise AssertionError('Link source attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        old=reference(raw)
        if a.source:q=source(raw if a.pursuit else old,a.form,a.limit,pursuit=a.pursuit)
        else:
            program=controller(old,a.form,pursuit=a.pursuit);q=dict(passed=True,ROM_SHA256=PIN,controller_SHA256=H(program.encode()),route_executed=False,outputs=0)
        q['installed_ROM_SHA256']=H(raw)
        q['native_binding_controller_SHA256']=H(native_program(raw,a.form,pursuit=a.pursuit))
    print('LINK_FIRST_SOURCE '+json.dumps(q,separators=(',',':')),flush=True)
    return int(not q['passed'])


if __name__=='__main__':raise SystemExit(main())
