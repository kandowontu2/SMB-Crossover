"""Current Gimmick ordinary live-Goomba/natural-Mushroom observations only."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256

import replay_mr_gimmick_full11_current_1114 as Stage
import replay_shared_world_chr_reset_1114 as World

R,ROM,PIN,W,N=Stage.R,Stage.ROM,Stage.PIN,Stage.W,Stage.N
IDENTITIES={'mr_gimmick':Stage.IDENTITIES['mr_gimmick']}


class Frozen:
    LuaRuntime=Stage.Frozen.LuaRuntime
    normalize=staticmethod(Stage.normalize)


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    assert key=='mr_gimmick'and sha256(raw).hexdigest()==PIN
    q=deepcopy(World.bindings(Stage.Current.owning82(raw),'hogan'))
    actual=Stage.bindings(raw,key)
    q.update(actual);q['role']=-1;q['prince_cookie']=[];q['prince_packet']={}
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('EnemyMetasprite','Enemy_SprAttrib','Enemy_Y_HighPos','Mirror_PPUCTRL','FmGroups','X5WideChrActive'):
        q['ram'][name]=W.address(b,name)
    q['maximum_images']=2;q['maximum_PNG_bytes']=65536
    return q


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    q=bindings(raw,key)
    assert sha256(World.Previous.TEMPLATE.read_bytes()).hexdigest()==World.Previous.TEMPLATE_SHA
    text=World.Previous.TEMPLATE.read_text()
    begin=text.index(' else\n  if birth then setPad(0)')
    end=text.index('\n end\nend\nlocal function hook',begin)
    replacement=r''' else
  local status=r('GmRam0091')
  local starB=(#shots==0)or status==0 or(status>=128 and status<169)
  local bits=starB and 64 or 0
  if birth then setPad(0)
  elseif phase=='settle'then if age>=4 then switch('approach',65)end
  elseif phase=='approach'then
   if s.x>=306 then switch('align',bits)else setPad(bits|1)end
  elseif phase=='align'then
   local v=r('GmRam00CC');if v>=128 then v=v-256 end
   local stopping=s.x+v*math.abs(v)/32
   if stopping<330 then bits=bits|1 elseif stopping>334 then bits=bits|2 end
   setPad(bits)
   if s.native_state==0 and s.x>=329 and s.x<=334 and math.abs(v)<=2 then switch('jump',128)end
  elseif phase=='jump'then setPad(age<25 and 128 or 0)
  end'''
    text=text[:begin]+replacement+text[end:]
    text=text.replace('Two ordinary current421 world-sprite observations','Two ordinary current Gimmick world-sprite observations')
    text='local C='+Stage.Frozen.lua(q)+'\n'+text
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:q[k]for k in('name','slot','owner','cycle')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),maximum_images=2,maximum_PNG_bytes=65536,
        scope='Observe existing graphics only; no gfxfix, native visual acceptance or fullstage claim',
        ordinary_inputs_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
