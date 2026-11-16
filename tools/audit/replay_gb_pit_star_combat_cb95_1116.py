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
   stock.combat=stock.combat or{first={state=state(),enemy=e},samples={}}
   local q=stock.combat;q.last={state=state(),enemy=e}
   if #q.samples<8 and(not q.sampleAt or guestReturns-q.sampleAt>=8)then q.samples[#q.samples+1]=q.last;q.sampleAt=guestReturns end
   return travel(c)
  end
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
    assert text.replace(INSERT,'',1)==old,'Only ordinary align combat controls and passive samples change'
    Previous.Prefix.M.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'))
    return text

def metadata(raw,kind='star'):
    q=dict(Previous.metadata(raw,'star'))
    q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,kind).encode()),
        previous_factory_SHA256=PREVIOUS_SHA,
        retained_alignment_injury_negative='32832749b3485e9044fdb9a7ff569da0f1dab4512be43938e71ec5d743859a0a',
        ordinary_control_delta='During actual nearby enemy contact risk at Star alignment, call unchanged Pit travel/bow policy; otherwise whole frozen controller exact.',
        restoration_proof='Removing one inserted combat-input/passive-sample fragment reconstructs the entire frozen Star controller byte-for-byte.')
    return q

def family(kind='star'):
    assert kind=='star'
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
