"""Controller-only earned Rogue Screw continuation on installed Sonic59."""

import argparse
from contextlib import contextmanager
from functools import lru_cache
import inspect
import json
from pathlib import Path
from unittest.mock import patch

import current_sonic_parent_rom_1122 as Parent
import audit_rogue_stock_foundation_1327_1116 as Foundation
import check_contra_force_combined_palette_1122 as Combined
import repair_contra_force_beans_ground_1122 as Beans
import run_rogue_bomb_block_native_1122 as Base
import run_rogue_missile_enemy_native_1122 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R, ROM, H = Base.R, Base.ROM, Base.H
PIN = Parent.CANDIDATE
POLICY = R/'tools/playthroughs/rogue_screw_native_1122.lua'
PINNED_CONTROLLER_SHA256 = '389e057b44093d802e47a5a6cdf2de48843854a51097fbbca243f4953ef0e5e9'
HISTORICAL_CONTROLLER_SHA256 = '08c7ad7fe505a05e8d3969cd992c1604c273db972d25f2411e96d66b747eb311'
EXTERIOR_ONLY_CONTROLLER_SHA256 = '1fbdc00a8930286826d660b0f5c2089e8cfeaf2310e5eb999d0ddfd0e5ffe86e'
HISTORICAL_EXTERIOR_FINISH_SHA256 = '3fc3d6f46f13ce64fba496128698543973a0bf5ebed2ca130e34670eda6fd216'
BASE_CONTROLLER_SHA256 = '1f8406cf1693e2dac5e7e2108b72090b4bc0ff5d76c266dfb9d1fefc133baa7a'
EXTERIOR_POLICY = """  if c.areaType==1 then
   assert(r('AreaAddrsLOffset')==5 and f.exit and f.exit.landing,
          'Native side pipe loads the stock exterior ending after the real lower approach')
   if not f.exterior then
    f.exterior={player=state(),area=c.area,areaType=c.areaType,areaOffset=r('AreaAddrsLOffset'),
                undergroundOffset=gear.high.areaOffset,
                entered=screwCounts('_entered'),returned=screwCounts('_returned')}
    screwPhase('exterior')
   end
   local e=f.exterior
   assert(r('RdHealthLo')==e.player.health_raw[1]and r('RdHealthHi')==e.player.health_raw[2],
          'Native exterior proof preserves its captured health')
   if not e.complete then
    local er,rr=screwCounts('_entered'),screwCounts('_returned');local enough=true
    e.post_returned={};e.post_entered={}
    for n,v in pairs(er)do
     e.post_entered[n]=v-e.entered[n];e.post_returned[n]=rr[n]-e.returned[n]
     if e.post_entered[n]<25 or e.post_returned[n]<25 then enough=false end
    end
    if enough then
     assert(#pending==0,'Exterior checkpoint has no pending gameplay return')
     e.complete={passed=true,player=state(),entered=e.post_entered,returned=e.post_returned,
                 scope='native-side-pipe-and25-exterior-play-updates'}
    end
   end
   if C.exterior_only and e.complete then finish('natural-side-pipe-exterior-and25');return{}end
   return gearTravel(c)
  end
  assert(c.areaType==2 and r('AreaAddrsLOffset')==gear.high.areaOffset,
         'Underground approach applies only to its actual loaded terrain')
"""


@lru_cache(maxsize=1)
def symbols():
    return Base.W.Symbols.bundle()


def comparison_reference(image):
    """Exact retained preimages; historical forward CPU checks stay frozen."""
    if H(image)==Combined.BASE_SHA:return image
    assert H(image)==Combined.COMBINED_SHA
    parent=bytearray(image)
    for at,old in Combined.BASE_PREIMAGES+Combined.Palette.preimages():
        parent[at:at+len(old)]=old
    parent=bytes(parent)
    assert H(parent)==Combined.BASE_SHA
    return parent


def rogue_metadata(image):
    assert H(image)==Foundation.PIN
    return dict(bundle=dict(symbols(),raw=image))


@contextmanager
def compilation_bindings():
    # The exact original Base Lua hash below covers the entire retained
    # controller and binding table. Skip unrelated Jay ancestry rebuilds.
    with patch.object(Base,'comparison_base',comparison_reference), \
         patch.object(Foundation.Current,'bindings',rogue_metadata):
        yield


@lru_cache(maxsize=1)
def bundle(raw):
    raw32=Parent.inverse(raw)
    baseline=Beans.inverse(raw32)
    parent=comparison_reference(baseline)
    with compilation_bindings():
        return baseline,parent,dict(Base.J.bindings(parent)['bundle'],raw=raw)


def controller(raw, *, historical=False, exterior_only=False, legacy_exterior_finish=False):
    assert not(historical and exterior_only)
    assert not legacy_exterior_finish or exterior_only
    baseline,parent,b=bundle(raw)
    with compilation_bindings():
        original=Base.controller(baseline,wall_jump=True,wall_left=True)
    assert H(original.encode())==BASE_CONTROLLER_SHA256,'Exact retained controller and metadata'
    text=original;changes=[]
    def edit(old,new):
        nonlocal text
        assert text.count(old)==1,(old,text.count(old))
        text=text.replace(old,new,1);changes.append((old,new))
    edit(H(baseline),PIN)
    lua=Base.J.Previous.Previous.Frozen.lua
    additions=[]
    if exterior_only:
        additions.append('C.exterior_only=true')
    for name in ('RdControlScrew','RdWxActorContact'):
        at=Base.W.location(b,name);code=raw[at:at+8]
        assert code==baseline[at:at+8]==parent[at:at+8],name
        additions.append('C.hooks.'+name+'='+lua(dict(PC=Base.W.address(b,name),offset=at-16,bytes=list(code))))
    names=('MmEnemyHealthLo','MmEnemyHealthHi','RdAnimReset','RdAnimIndex')
    additions.append('for n,at in pairs('+lua({n:Base.W.address(b,n)for n in names})+')do C.ram[n]=at end')
    line=text.split('\n',1)[0];edit(line,line+'\n'+'\n'.join(additions))
    policy=POLICY.read_text(encoding='utf-8')
    assert policy.count(EXTERIOR_POLICY)==1
    if historical:
        policy=policy.replace(EXTERIOR_POLICY,'',1)
    edit('local function bombDrive()',policy+'\nlocal function bombDrive()')
    edit('local function wallJumpTravel(c, wall, grounded)',
         'local screwPairedGap\nlocal function wallJumpTravel(c, wall, grounded)')
    wall_source=Base.WALL_JUMP_ROUTE.read_text(encoding='utf-8')
    start=wall_source.index('local function wallJumpLift(c,wall,grounded)')
    end=wall_source.index('local function wallJumpTravel(c, wall, grounded)',start)
    edit(wall_source[start:end],'local screwLift\n\n')
    edit('local input=wallJumpLift(c,wall,grounded)','local input=screwLift(c,wall,grounded)')
    start=wall_source.index(' if c.x>=1890 and not wall.pairedGaps then')
    end=wall_source.index(' if c.x>=2184 and not wall.crossedLiftGap then',start)
    edit(wall_source[start:end],""" if c.x>=1840 and not wall.pairedGaps then
  return screwPairedGap(c,wall,grounded)
 end
""")
    edit('and a.y>=128 and a.y<=156 then','and a.y>=64 and a.y<=80 then')
    edit("if grounded and c.y >= 175 and c.y <= 177 and not b.left and not b.right and releasedA() then",
         "if grounded and c.y >= 175 and c.y <= 177 and not b.left and not b.right and releasedA() and r('RdAction')==0 then")
    edit(' local c=context();assert(identity()',' local c=context();if gear.screw then return screwDrive(c)end\n assert(identity()')
    edit("finish('natural-wall-jump-and-landing')","""gear.screw={phase='leave-underground',started=updates,steps={},tail={}}
  stock='screw';born=nil;mature=nil;collector=nil;credit=nil""")
    success="reason=='natural-Screw-body-defeat-and-landing'and gear.complete and gear.high.complete and gear.wall.acquisition and gear.wall.acquisition.credit and gear.screw.complete"
    if not historical:
        success="(("+success+" and gear.screw.exterior and gear.screw.exterior.complete)or(reason=='natural-side-pipe-exterior-and25'and gear.complete and gear.high.complete and gear.wall.acquisition and gear.wall.acquisition.credit and gear.screw.exterior.complete))"
    edit("reason=='natural-wall-jump-and-landing'and gear.complete and gear.high.complete and gear.wall.complete",success)
    if exterior_only and not legacy_exterior_finish:
        edit('and collector and gear.acquisition and gear.acquisition.credit and born and mature and not reset',
             'and gear.wall.acquisition.collector and gear.acquisition and gear.acquisition.credit and gear.wall.acquisition.birth and gear.wall.acquisition.mature and not reset')
    edit("(r('LevelNumber')==0 or(gear.started and r('LevelNumber')==1))",
         "(r('LevelNumber')==0 or(gear.started and r('LevelNumber')==1)or(gear.screw and r('LevelNumber')==2))")
    edit("(a.private==(gear.wall and 210 or(gear.high and 209 or 208)) and a.owner==2)",
         "(a.private==(gear.screw and 211 or(gear.wall and 210 or(gear.high and 209 or 208))) and a.owner==2)")
    edit("(tank and 216 or(gear.wall and 210 or(gear.high and 209 or(gear.started and 208 or 217))))",
         "(tank and 216 or(gear.screw and 211 or(gear.wall and 210 or(gear.high and 209 or(gear.started and 208 or 217)))))")
    edit("a.x==(gear.wall and 2400 or 1104) and a.state<128 and a.saved_raw==1, 'Correct authored upgrade actor'",
         "a.x==(gear.screw and 944 or(gear.wall and 2400 or 1104)) and a.state<128 and a.saved_raw==1, 'Correct authored upgrade actor'")
    edit("p.actor.private==(gear.wall and 210 or 209) and p.actor.state",
         "p.actor.private==(gear.screw and 211 or(gear.wall and 210 or 209)) and p.actor.state")
    edit("stock=='wall-jump-credit'and 7 or(stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0))",
         "stock=='screw-credit'and 15 or(stock=='wall-jump-credit'and 7 or(stock=='high-jump-credit'and 3 or(stock=='bomb-credit'and 1 or 0)))")
    edit("   elseif stock=='wall-jump-credit'then","""   elseif stock=='screw-credit'then
    gear.screw.acquisition={birth=born,mature=mature,collector=collector,credit=credit}
    stock='screw-earned';credit=nil;screwPhase('use')
   elseif stock=='wall-jump-credit'then""")
    edit("wallJumpPhase('prepare');stock='wall-jump-earned';credit=nil","""gear.screw={phase='leave-underground',started=updates,steps={},tail={}}
    stock='screw';born=nil;mature=nil;collector=nil;credit=nil""")
    edit("stock=='wall-jump'and 2 or(stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9))",
         "stock=='screw'and 3 or(stock=='wall-jump'and 2 or(stock=='high-jump'and 1 or(stock=='bomb'and 0 or 9)))")
    edit("stock=='wall-jump'and 7 or(stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0))",
         "stock=='screw'and 15 or(stock=='wall-jump'and 7 or(stock=='high-jump'and 3 or(stock=='bomb'and 1 or 0)))")
    edit('a.private==208 or a.private==209 or a.private==210)',
         'a.private==208 or a.private==209 or a.private==210 or a.private==211)')
    edit("local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}","""local p={name=n,pc=ret,sp=(sp+2)&255,kind=kind,at=at,A=c['cpu.a']}
 if n=='RdControlScrew'then p.before=state();p.animation={r('RdAnimReset'),r('RdAnimIndex')}
 elseif n=='RdWxActorContact'then p.enemy=actor(c['cpu.x']);p.health=r('MmEnemyHealthLo',p.enemy.slot);p.before=state()end""")
    edit("  elseif n=='RdHsCollectActor'then","""  elseif n=='RdControlScrew'then
   local f=gear.screw
   if f and f.acquisition then
    local carry=cpu()['cpu.ps']&1
    if carry==0 then
     assert(p.before.gear&8~=0 and p.before.action==1,'Original earned spin pose admission')
     f.admitted=f.admitted or{Main=updates,player=p.before,animation=p.animation,C=carry}
    elseif p.before.native_state==0 then f.groundRejected=f.groundRejected or{player=p.before,C=carry}end
   end
  elseif n=='RdWxActorContact'then
   local f=gear.screw;local a=actor(p.enemy.slot)
   assert(p.A==0x81 and p.health>0 and r('MmEnemyHealthLo',p.enemy.slot)==0 and r('MmEnemyHealthHi',p.enemy.slot)==0,
          'Actual original Screw81 terminal contact zeros native HP')
   assert(a.state&32~=0 or a.flag==0,'Real native ShellOrBlockDefeat state')
   assert(not f.hit and p.before.health_raw[1]==r('RdHealthLo')and p.before.health_raw[2]==r('RdHealthHi'),
          'Body hit protects the captured actual source health')
   f.hit={Main=updates,before_enemy=p.enemy,after_enemy=a,before_HP=p.health,after_HP=0,player=state()}
  elseif n=='RdHsCollectActor'then""")
    edit('local age=0',"""hook('RdControlScrew',function()
 if gear.screw and active()and identity()then enter('RdControlScrew')end
end)
hook('RdWxActorContact',function()
 local f=gear.screw;if not f or not f.acquisition or not active()or not identity()or cpu()['cpu.a']~=0x81 then return end
 local a=actor(cpu()['cpu.x'])
 if a.flag==1 and (a.id==6 or a.id==0 or a.id==3)and a.state&32==0 then enter('RdWxActorContact')end
end)
local age=0""")
    edit('updates<11800','updates<16000')
    edit('if frame>=22000 then','if frame>=28000 then')
    restored=text
    for old,new in reversed(changes):
        assert restored.count(new)==1,old
        restored=restored.replace(new,old,1)
    assert restored==original
    LuaRuntime().compile(text)
    assert not any(t in text for t in ('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def cold(raw):
    q=bundle(raw)
    with patch.object(Previous,'bundle',lambda image:q if image is raw else (_ for _ in ()).throw(AssertionError('Wrong cold image'))):
        return Previous.cold(raw)


def source(raw,limit):
    import inspect_rogue_missile_targets_cb95_1116 as Engine
    program=controller(raw)
    print('SCREW_BOUND '+json.dumps(dict(ROM_SHA256=PIN,controller_SHA256=H(program.encode()))),flush=True)
    frame=Engine.Frames.frame;consume=Engine.N.consume;cpu=Engine.N.NesMPU;milestones=set()
    # The retained scheduler checks every opcode twice. Fold its BRK guard
    # into the ordinary CPU fetch; instruction order/cycles remain identical.
    class CheckedCPU(cpu):
        def step(self):
            opcode=self.memory[self.pc]
            assert opcode,('Actual linked BRK',hex(self.pc))
            self.pc=(self.pc+1)&self.addrMask
            self.excycles=0;self.addcycles=self.extracycles[opcode]
            self.instruct[opcode](self)
            self.pc&=self.addrMask
            self.processorCycles+=self.cycletime[opcode]+self.excycles
            return self
    body=inspect.getsource(frame)
    guard="        assert m[c.pc], ('BRK', hex(c.pc), m.rawtags)\n"
    assert body.count(guard)==1;body=body.replace(guard,'')
    loop="    for _ in range(4_000_000 if cold else 500_000):\n        stop=(idle,253) if whole_pass else (idle+12,252)"
    assert body.count(loop)==1
    body=body.replace(loop,"    stop=(idle,253) if whole_pass else (idle+12,252)\n    step=c.step\n    for _ in range(4_000_000 if cold else 500_000):")
    assert body.count('        c.step()')==1;body=body.replace('        c.step()','        step()')
    scope=dict(Engine.Frames.__dict__);exec(compile(body,'<checked source frame>','exec'),scope)
    fast=scope['frame']
    body=inspect.getsource(consume)
    guard="        assert m[c.pc]!=0,('Actual NMI BRK',hex(c.pc));c.step()"
    assert body.count(guard)==1;body=body.replace(guard,'        c.step()')
    body=body.replace('c=NesMPU(memory=m,pc=0x5b00)','c=_N.NesMPU(memory=m,pc=0x5b00)')
    scope=dict(Engine.N.__dict__,_N=Engine.N);exec(compile(body,'<checked source NMI>','exec'),scope)
    fast_consume=scope['consume']
    paired=[]
    def paired_cold(image):
        m=cold(image)
        a,b=Engine.N.fork(m),Engine.N.fork(m)
        for bits in (0,1,1,0):
            a.controller_pad=b.controller_pad=bits
            with patch.object(Engine.N,'NesMPU',cpu),patch.object(Engine.N,'consume',consume):left=frame(a,whole_pass=True)
            right=fast(b,whole_pass=True)
            assert left==right and list.__eq__(a,b)
            assert {k:v for k,v in a.__dict__.items()if k!='bundle'}=={k:v for k,v in b.__dict__.items()if k!='bundle'}
            paired.append(dict(pad=bits,cycles=left,all_bus_state_exact=True))
        print('SCREW_SOURCE_SCHEDULER '+json.dumps(dict(passed=True,paired=paired)),flush=True)
        return m
    def observe(m,*args,**kwargs):
        result=fast(m,*args,**kwargs)
        level=Engine.N.get(m,'LevelNumber')
        if level==2 and level not in milestones and tuple(Engine.N.get(m,n)for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
            milestones.add(level)
            print('SCREW_STAGE13 '+json.dumps(dict(x=Engine.N.get(m,'Player_X_Position')+256*Engine.N.get(m,'Player_PageLoc'),
                  y=Engine.N.get(m,'Player_Y_Position'),gear=Engine.N.get(m,'RdGear'),lives=Engine.N.get(m,'NumberofLives'))),flush=True)
        return result
    with patch.object(Engine.J,'cold',paired_cold),patch.object(Engine.J,'PIN',PIN),patch.object(Engine.Frames,'frame',observe), \
         patch.object(Engine.N,'NesMPU',CheckedCPU),patch.object(Engine.N,'consume',fast_consume):
        q=Engine.run(raw,limit,text=program)
    q['source_scheduler_pairs']=paired
    q.pop('receipt_SHA256')
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    return q


def side_pipe_candidate(installed):
    import compose_sonic_current_auth_epoch_1122 as Sonic
    import repair_rogue_side_pipe_1123 as Pipe

    owner = Sonic.inverse(installed) if H(installed) == Sonic.CANDIDATE else installed
    repaired = Pipe.compose(owner)
    assert H(owner) == PIN and Pipe.inverse(repaired) == owner
    image = bytearray(installed)
    for at, old, new in Pipe.spans(owner):
        assert image[at:at+len(old)] == old and repaired[at:at+len(new)] == new
        image[at:at+len(old)] = new
    return owner, bytes(image)


def native_program(raw, image, *, historical=False, exterior_only=False, legacy_exterior_finish=False):
    program = controller(raw,historical=historical,exterior_only=exterior_only,legacy_exterior_finish=legacy_exterior_finish)
    expected=HISTORICAL_CONTROLLER_SHA256 if historical else(HISTORICAL_EXTERIOR_FINISH_SHA256 if legacy_exterior_finish else(EXTERIOR_ONLY_CONTROLLER_SHA256 if exterior_only else PINNED_CONTROLLER_SHA256))
    assert H(program.encode()) == expected,'Exact frozen native diagnostic controller'
    if H(image) != PIN:
        assert program.count(PIN) == 1
        program = program.replace(PIN, H(image), 1)
        LuaRuntime().compile(program)
    return program.encode()


def native(raw, installed=None, *, private=None, historical=False, exterior_only=False, legacy_exterior_finish=False):
    import build_storage_guard_v1 as Storage
    from capture_budget import preflight
    from mesen_session_guard_v1 import require_free_workspace
    from nightly_patch_guard_v1 import check
    from run_mario_luigi_stock_native_1122 import preserve_script
    from run_stdout_mesen_1110 import run
    installed = raw if installed is None else installed
    image = installed if private is None else private
    program = native_program(raw, image,historical=historical,exterior_only=exterior_only,legacy_exterior_finish=legacy_exterior_finish)
    guard=check(ROM);assert guard['ROM_sha256']==H(installed) and not guard['matching_patch_files']
    target,script=Base.OUT/'candidate.nes',Base.OUT/'controller.lua'
    assert {p.name for p in Base.OUT.iterdir()}=={'candidate.nes','controller.lua'}
    assert target.read_bytes()==installed
    Storage.preflight(private_root=Base.OUT,reserved_bytes=0,reserved_files=0,fresh=True)
    preflight(Base.OUT/'capture',reserved_files=0);require_free_workspace(R,ROM,allow_interactive=True)
    previous=H(script.read_bytes())
    try:
        with preserve_script(script,target,installed)as stage:
            stage(program)
            try:
                launch = ROM
                if private is not None:
                    assert not check(target)['matching_patch_files']
                    target.write_bytes(private)
                    launch = target
                    assert check(launch)['ROM_sha256'] == H(image)
                q=run(script,launch,Base.OUT/'capture',H(image),240)
            finally:
                if private is not None:
                    target.write_bytes(installed)
        assert q['script_SHA256']==H(program)and q['ROM_SHA256']==H(image)
        assert q['native_Mesen']and q['shared_Mesen_queue']and q['capture_watchdog']
        assert not q['images']and q['outputs_written']==0
        assert q['receipt_SHA256']==H(json.dumps(q['receipt'],sort_keys=True).encode())
    finally:
        assert H(script.read_bytes())==previous and target.read_bytes()==installed and ROM.read_bytes()==installed and check(ROM)==guard
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__);mode=p.add_mutually_exclusive_group()
    mode.add_argument('--source',action='store_true');mode.add_argument('--run',action='store_true')
    mode.add_argument('--validate',action='store_true');p.add_argument('--limit',type=int,default=13000)
    p.add_argument('--side-pipe-candidate',action='store_true')
    p.add_argument('--historical-exterior-diagnostic',action='store_true',
                   help='Exact08c7/e7adf historical controller that stops at the exterior stairs')
    p.add_argument('--exterior-only',action='store_true',help='Pass after real exterior entry and25 completed play updates')
    p.add_argument('--historical-exterior-finish-diagnostic',action='store_true',
                   help='Exact359bc historical exterior checkpoint with rejected legacy live-field finish')
    a=p.parse_args();assert 8000<=a.limit<=15000
    if a.historical_exterior_finish_diagnostic:a.exterior_only=True
    installed=ROM.read_bytes();raw=installed;private=None
    if a.side_pipe_candidate:
        assert not a.source
        raw,private=side_pipe_candidate(installed)
    assert H(raw)==PIN
    assert not(a.source and(a.historical_exterior_diagnostic or a.exterior_only))
    assert not(a.historical_exterior_diagnostic and a.exterior_only)
    if a.run:q=native(raw,installed,private=private,historical=a.historical_exterior_diagnostic,exterior_only=a.exterior_only,legacy_exterior_finish=a.historical_exterior_finish_diagnostic)
    else:
        def deny(*args,**kwargs):raise AssertionError('Source Screw test attempted files or process launch')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
            if a.source:q=source(raw,a.limit)
            else:
                image=installed if private is None else private
                program=native_program(raw,image,historical=a.historical_exterior_diagnostic,exterior_only=a.exterior_only,legacy_exterior_finish=a.historical_exterior_finish_diagnostic)
                q=dict(passed=True,route_executed=False,controller_SHA256=H(program),ROM_SHA256=H(image),outputs=0,native=False)
    assert ROM.read_bytes()==installed
    receipt=q.get('receipt',{});gear=receipt.get('natural_Bomb',{})
    print('ROGUE_SCREW_SUMMARY '+json.dumps(dict(passed=q['passed'],reason=receipt.get('reason'),
          controller_SHA256=q.get('script_SHA256',q.get('controller_SHA256')),receipt_SHA256=q.get('receipt_SHA256'),
          terminal=receipt.get('terminal'),high_jump=gear.get('high',{}).get('phase'),
          wall_jump=Base.compact_wall_receipt(gear.get('wall')),
          exterior=gear.get('screw',{}).get('exterior'),screw=gear.get('screw')),separators=(',',':')),flush=True)
    print('ROGUE_SCREW '+json.dumps(q,separators=(',',':')),flush=True)
    return 0 if q['passed']else 1


if __name__=='__main__':raise SystemExit(main())
