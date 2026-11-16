"""Separate actual-cb95 Star controls: retain M and use existing Pit bow travel."""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
import replay_gb_pit_natural_sl_cb95_1116 as Previous

R,ROM,W,N,H,Current=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.H,Previous.Current
PIN=Previous.PIN
PREVIOUS_SHA='98556fad3fe3db8cd0d059a9cc80d365363d1ed28dcdad627dd23d7dc2a3529e'
INSERT=r'''  local e=c.enemy()
  if e and e.dx>0 and e.dx<112 and math.abs(e.y-c.y)<48 then
   local b=travel(c);local arrows={}
   for i=0,3 do if r('MmBulletType',i)>0 then arrows[#arrows+1]={slot=i,kind=r('MmBulletType',i),x=r('MmBulletX',i)+256*r('MmBulletPage',i),y=r('MmBulletY',i)}end end
   stock.combat=stock.combat or{first={state=state(),enemy=e},samples={}}
   local q=stock.combat;q.last={state=state(),enemy=e,buttons=b,arrows=arrows}
   if #q.samples<8 and(not q.sampleAt or guestReturns-q.sampleAt>=8)then q.samples[#q.samples+1]=q.last;q.sampleAt=guestReturns end
   return b
  end
  stock.alignment_last={state=state(),enemy=e,lastA=lastA,phaseStart=stock.phaseStart,camera=c.camera,feet={c.block(c.x+3,c.y+32),c.block(c.x+12,c.y+32)}}
'''

def bindings(raw,kind='star'):
    assert kind=='star'and H(raw)==PIN
    assert H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    return Previous.bindings(raw,'star')

@lru_cache(maxsize=1)
def controller(raw,kind='star'):
    bindings(raw,kind)
    old=Previous.controller(raw,'star')
    needle=" if stock.phase=='align'then\n"
    assert old.count(needle)==1 and INSERT not in old
    text=old.replace(needle,needle+INSERT,1)
    predictor='local stop=c.x+v*math.abs(v)/32;local center=C.target_x-6'
    assert text.count(predictor)==1
    text=text.replace(predictor,'local stop=c.x;local center=C.target_x-6',1)
    restored=text.replace(INSERT,'',1).replace('local stop=c.x;local center=C.target_x-6',predictor,1)
    assert restored==old,'Only ordinary align combat/direct-stop controls and passive samples change'
    Previous.Prefix.M.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text

def metadata(raw,kind='star'):
    q=dict(Previous.metadata(raw,'star'))
    q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,kind).encode()),
        previous_factory_SHA256=PREVIOUS_SHA,
        retained_alignment_injury_negative='32832749b3485e9044fdb9a7ff569da0f1dab4512be43938e71ec5d743859a0a',
        ordinary_control_delta='During actual nearby enemy risk at Star alignment, call unchanged Pit travel/bow policy; steer actual X then neutral-settle because Pit loads constant directional speed, not Mario acceleration.',
        restoration_proof='Removing one combat-input/passive-sample fragment and restoring the old input stop predictor reconstructs the entire frozen Star controller byte-for-byte.',
        retained_predictor_control_negative='697a3d7a414efbeb392a6e83a35c64d72ffd4f5f9cfa47bff15a301cce2e083f')
    return q

def family(kind='star'):
    assert kind=='star'
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
