"""Native Toad uses ordinary fresh jump when the real mount has a Goomba."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_smb1_toad_flower_emerge_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='c83cdd3018a37014bdabb51ebd4a22ab2ecf710e7a07d8eab467e5d26a96c33d'


@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old="  if q.phase=='back'then\n";assert text.count(old)==1
    text=text.replace(old,old+"""   local e=c.enemy()
   if e and math.abs(e.dx)<48 and c.x+13<q.edge and c.grounded and c.y>=160 and not lastA then
    q.phase='rise';q.takeoff=guestReturns;q.stand=state();q.evasion={state=state(),actor=e}
    return{a=true}
   end
""",1)
    Previous.Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text


def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),evasion_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_live_Goomba_damage_negative='98c72193b17777e17023655f64861bfe669ffa045035e4e19922e0cd771e31ca',
        ordinary_change='Actual hostile proximity and real left-row head clearance admit fresh standingA before settling; no game/ability grants')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
