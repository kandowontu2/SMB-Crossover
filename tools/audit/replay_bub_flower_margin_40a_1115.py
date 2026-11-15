"""Strict fixture-bound Flower margin; move the real takeoff ten pixels left."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import inspect
import replay_bub_flower_ride_40a_1115 as Ride
import replay_bub_flower_7a80_1115 as Witness

R,ROM,W,N,B,PIN=Ride.R,Ride.ROM,Ride.W,Ride.N,Ride.B,Ride.PIN
FIXTURE=R/'tools/reference/bub40a_flower_c8e4_1115.lua'
BASE_SHA='c8e483d60fdd050f97568fdd473220b4aa59ba0b6bd93c3a74dded79b31e77ba'
BOB_SHA='1b858e8c06776d17e190a6945ae321d4f1bac0f69f53bde25e3c0d7855e43560'
RIDE_SOURCE='6294d8f783109eacef22d196109874ba9c82c0f189cc2f5fd14d5cfb8517d351'
once=Witness.Previous.Previous.Previous.once

def reference(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Exact current40a only'
    return raw

@lru_cache(maxsize=2)
def baseline(raw,identity=0):
    reference(raw);data=FIXTURE.read_bytes();assert sha256(data).hexdigest()==BASE_SHA
    text=data.decode();assert '\r'not in text
    if identity==1:
        text=once(text,'["identity"]=0','["identity"]=1')
        text=once(text,'local identity,expectedRom,cookie=0,','local identity,expectedRom,cookie=1,')
    assert sha256(text.encode()).hexdigest()==(BASE_SHA if identity==0 else BOB_SHA),'Exact previously source-qualified/native-tested baseline bytes'
    return text

def head_binding(raw):
    reference(raw)
    image=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in B.PAGES)
    y=W.address(dict(W.Symbols.bundle(),raw=raw),'Player_Y_Position')
    store=bytes((0x85,y))if y<256 else bytes((0x8d,y&255,y>>8))
    pattern=bytes.fromhex('adc8c329f0')+store
    positions=[i for i in range(len(image)-len(pattern)+1)if image[i:i+len(pattern)]==pattern]
    assert len(positions)==1
    at=positions[0];return dict(pc=0xa000+at,offset=3*8192+at,data=image[at:at+16].hex())

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert identity in(0,1)and mode=='mushroom'
    assert sha256(Path(Ride.__file__).read_bytes()).hexdigest()==RIDE_SOURCE
    text=baseline(raw,identity);at=text.index('\n')+1
    text=text[:at]+'local RideHead='+Witness.Base.Previous.lua(head_binding(raw))+'\n'+text[at:]
    text=once(text,'local function full_tick(finish)',Ride.OBSERVER+'\nlocal function full_tick(finish)')
    text=once(text,'if s and step>=4 then pad.right=s.dx>34 end',
        "if s and step>=4 then pad.right=s.dx>(flower.phase=='grow'and 44 or 34)end")
    text=once(text,'if s and s.kind==2 and s.dx>=30 and s.dx<=36 and s.dy>=-20 and s.dy<=-16',
        "if s and s.kind==2 and((flower.phase=='grow'and s.dx>=40 and s.dx<=46)or(flower.phase~='grow'and s.dx>=30 and s.dx<=36))and s.dy>=-20 and s.dy<=-16")
    text=once(text," elseif flower.phase=='ride'then\n  local tx=",r''' elseif flower.phase=='ride-release'then
  full_pad={}
  if sourceUpdates-flower.retry_release>=2 and full_state(0x301)&192==0 then flowerPhase('mount')end
 elseif flower.phase=='ride'then
  if flower.age>8 and q.source_bubble_ride_restarts>flower.base.source_bubble_ride_restarts
   and y>=flower.target.y+16 and full_normal_jump_ready(actor)then
   flower.retries=(flower.retries or 0)+1;assert(flower.retries<=1,'One bounded genuine floor rearm/relaunch')
   flower.landings=flower.landings or{};flower.landings[#flower.landings+1]=rideState()
   flower.retry_release=sourceUpdates;flowerPhase('ride-release');full_pad={};return
  end
  local tx=''')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text

def source_check(raw,identity=0):
    # Same frozen actual-CPU/NMI driver and read-only callback extension.
    # Global exact40a and the authenticated LF fixture replace slow historical
    # controller regeneration; there is no normalized-ROM CPU execution.
    base=SimpleNamespace(reference=reference,Previous=Witness.Base.Previous)
    ns=dict(Witness.__dict__,Base=base,PIN=PIN,controller=controller)
    exec(compile(inspect.getsource(Witness.source_check),str(Path(__file__))+':fixture-current-driver','exec'),ns)
    return ns['source_check'](raw,identity)
