"""New strict bc5 Bowser stock facade; frozen7ef factories stay unchanged."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import inspect
import current_bowser_stock_bc5_1115 as Current
import replay_bowser_natural_powerups_1113 as Old
import replay_smb1_alts_full11_1114 as Text

R,ROM,PIN,W,N=Current.R,Current.ROM,Current.PIN,Current.W,Current.N
SOURCE=R/'tools/playthroughs/bowser_natural_stock_bc5_1115.lua'
PINS={Path(Old.Base.__file__):'c002b6cf7dc88c6b3d7698b52c5921b8fa25c3b7eb9dee8d8a3c386c3956ba73',
 Path(Old.__file__):'28602a2e2b45da4ff7ec4da637a4ebacebb096a5abbee5ffc5dfbd53b1d21d1d',
 Old.SOURCE:'d9f40ee9c043a0c07ef3e780b59eaea043735e6897ca4706afe983c4f34cff50'}

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def current_policy():
    for path,pin in PINS.items():assert sha256(path.read_bytes()).hexdigest()==pin,path
    # A new namespace, not mutation/relaxation of either frozen factory/API.
    namespace=dict(Old.Base.__dict__);namespace['PIN']=PIN
    exec(compile(inspect.getsource(Old.Base.controller),__file__+':current-full-policy','exec'),namespace)
    base=SimpleNamespace(controller=namespace['controller'],W=W,LuaRuntime=Old.Base.LuaRuntime)
    source=inspect.getsource(Old.controller)
    source=once(source,"assert sha256(text.encode()).hexdigest()==BASE[identity],'Frozen original full-stage controller'",
        "assert sha256(raw).hexdigest()==PIN,'Explicit owning bc5 binding'")
    source=once(source,"assert sha256(text.encode()).hexdigest()==SCRIPTS[identity],'Frozen natural item controller'",
        "assert sha256(raw).hexdigest()==PIN,'Explicit owning bc5 binding'")
    namespace=dict(Old.__dict__);namespace.update(PIN=PIN,Base=base)
    exec(compile(source,__file__+':current-natural-policy','exec'),namespace)
    return namespace['controller']

@lru_cache(maxsize=4)
def bindings(raw,identity=0,kind='oneup'):
    assert identity in(0,1) and kind in('oneup','star');proof=Current.preservation(raw);b=Current.bundle(raw)
    hooks={};image=Current.frozen_image()
    for name in('BwMovement','BwWeaponTail','BwCoreFinish','BwPickup'):
        pc=W.address(b,name);assert 0xa000<=pc<0xa000+proof['decoded_executable_end']
        hooks[name]=dict(pc=pc,offset=3*8192+(pc&8191),space='work',bytes=list(image[pc&8191:(pc&8191)+8]))
    def add(name,pc,at):hooks[name]=dict(pc=pc,offset=at-16,space='prg',bytes=list(raw[at:at+8]),bank=(at-16)//8192)
    for name in('EraseEnemyObject','SetupFloateyNumber'):add(name,W.address(b,name),W.location(b,name))
    at,pc=W.location(b,'FloateyNumbersCore'),W.address(b,'FloateyNumbersCore')
    timer=W.address(b,'FloateyNum_Timer');pattern=bytes((0xde,timer&255,timer>>8,0xc9,43,0xd0))
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    add('TimerDEC',pc+hits[0],at+hits[0])
    life,cue=W.address(b,'NumberofLives'),W.address(b,'Square2SoundQueue')
    inc=bytes((0xee,life&255,life>>8))if life>255 else bytes((0xe6,life))
    store=bytes((0x8d,cue&255,cue>>8))if cue>255 else bytes((0x85,cue))
    pattern=inc+b'\xa9\x40'+store
    hits=[i for i in range(120-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    add('LifeBefore',pc+hits[0],at+hits[0]);delta=hits[0]+len(pattern);add('LifeAfter',pc+delta,at+delta)
    names=('Player_X_Speed','Player_Y_Speed','Player_Y_HighPos','BoundingBox_UL_Corner','EnemyBoundingBoxCoord','StarInvincibleTimer',
        'FloateyNum_Timer','Player1ScoreDisplay','AreaMusicQueue','CrossoverBehaviorVersion','CheatInvincible','CheatStartLevel','PreviousA_B_Buttons')
    return dict(sha=PIN,identity=identity,kind=3 if kind=='oneup' else 2,key=kind,hooks=hooks,
        ram={n:W.address(b,n)for n in names},code_hex=image[:proof['decoded_executable_end']].hex(),cookie=Current.COOKIE.hex())

@lru_cache(maxsize=4)
def controller(raw,identity=0,kind='oneup'):
    config=bindings(raw,identity,kind);text=current_policy()(raw,identity)
    text=once(text,'local frames,updates,pad=0,0,0',"local stock={phase='travel',trace={}}\nlocal frames,updates,pad=0,0,0")
    text=once(text,'return_counts=returns,pipes=pipes,recent=records,natural=natural',
        'return_counts=returns,pipes=pipes,recent=records,natural=natural,stock=stock')
    text=text.replace('s.lives==2 and s.health>0',"(s.lives==2 or(stock.life_credit and s.lives==3))and s.health>0")
    text=once(text,"local function phaseTo(name)",SOURCE.read_text()+"\nlocal function phaseTo(name)")
    text=once(text," assert(s.world==0 and s.level==0,'Authored1-1 item route')",
        " assert(s.world==0 and s.level==0,'Authored1-1 item route')\n if stock.active then stockDrive();return end")
    text=once(text," if s.x<1184 then traversalDrive()else", " if BStock.kind==3 and s.x>=992 and s.native_state==0 then stock.active=true;stock.phase='align';stock.since=updates;pad=0\n  elseif s.x<1184 then traversalDrive()else")
    text=once(text," elseif natural.phase=='resumed-play'then\n  pad=1", " elseif natural.phase=='resumed-play'then\n  do stock.active=true;stock.phase='star-travel';stock.since=updates;stockDrive();return end\n  pad=1")
    text='local BStock='+Text.lua(config)+'\n'+text
    assert not any(word in text for word in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    Old.Base.LuaRuntime().compile(text);return text

def metadata(raw,identity=0,kind='oneup'):
    text=controller(raw,identity,kind)
    return dict(ROM_SHA256=PIN,controller_SHA256=sha256(text.encode()).hexdigest(),factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        template_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),identity=identity,kind=kind,preservation=Current.preservation(raw),
        frozen_policy_sources={str(p.relative_to(R)):h for p,h in PINS.items()},
        control_namespace='New strict bc5 namespace; old7ef factories/defaults untouched',
        endpoint='25 actual BwCoreFinish returns and25 outer BwWeaponTail returns, at actual returned Main; no guest pending',
        gameplay_seeds=0,outputs=0,Mesen_run=False)

def family(identity,kind):
    return SimpleNamespace(W=W,N=N,ROM=ROM,controller=lambda raw,key:controller(raw,identity,kind),metadata=lambda raw,key:metadata(raw,identity,kind))
