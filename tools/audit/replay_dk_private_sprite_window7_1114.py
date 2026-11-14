"""Explicit exact DK-window7 ordinary images; frozen common defaults preserved."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import compose_dk_private_sprite_window7_1114 as Compose
import replay_shared_world_chr_reset_1114 as Previous

R,ROM,PIN,W,N=Previous.R,Previous.ROM,Compose.CANDIDATE,Previous.W,Previous.N
IDENTITIES={'donkey_kong':Previous.IDENTITIES['donkey_kong']}


class Frozen:
    LuaRuntime=Previous.Frozen.LuaRuntime
    @staticmethod
    def normalize(raw):return Previous.Frozen.normalize(Compose.inverse(raw))


@lru_cache(maxsize=1)
def bindings(raw,key='donkey_kong'):
    assert key=='donkey_kong'
    parent=Compose.inverse(raw);c=deepcopy(Previous.bindings(parent,key));c['sha']=PIN
    for h in c['hooks'].values():
        if'bank'in h:
            lo=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[lo:lo+8192]).hexdigest()
    c['ram'].update({n:W.address(dict(W.Symbols.bundle(),raw=raw),n)for n in('DkShots','DkRenderPage','DkAttack','DkAge')})
    c['maximum_images']=3
    return c


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    c=bindings(raw,key);parent=Compose.inverse(raw)
    text=Previous.controller(parent,key)
    prefix='local C='+Previous.Previous.Frozen.lua(Previous.bindings(parent,key))+'\n'
    assert text.startswith(prefix)
    text='local C='+Previous.Previous.Frozen.lua(c)+'\n'+text[len(prefix):]
    marker=" else\n  if birth then setPad(0)"
    replacement=" else\n  if #shots>=2 then setPad(age<4 and 0 or age<8 and 64 or 0);return end\n  if birth then setPad(0)"
    assert text.count(marker)==1;text=text.replace(marker,replacement,1)
    marker="target=a;capture('first-natural-mature-Mushroom',a);break"
    replacement="target=a;capture('first-natural-mature-Mushroom',a);switch('barrel-show',0);break"
    assert text.count(marker)==1;text=text.replace(marker,replacement,1)
    old="  if#shots==2 then finish(true,'Two ordinary private82ec world-sprite observations')end"
    new="""  if#shots==2 then
   for i=0,2 do local at=C.ram.DkShots+12*i
    if read(at)==1 and read(at+1)<6 then
     local shot={slot=i,kind=read(at),pose=read(at+1),x=read(at+4)+256*read(at+5),y=read(at+6),direction=read(at+7)}
     local onScreen=false
     for slot=0,63 do local at=slot*4;local tile=emu.read(at+1,emu.memType.nesSpriteRam)
      if emu.read(at,emu.memType.nesSpriteRam)<240 and(tile&1)*4+(tile>>6)==7 then onScreen=true end
     end
     if onScreen and spriteBanks[7]==823 then capture('ordinary-emitted-barrel',shot);break end
    end
   end
  end
  if#shots==3 then finish(true,'Three ordinary DK-window7 Goomba Mushroom barrel observations')end"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text


def metadata(raw,key='donkey_kong'):
    c=bindings(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,compiled_menu={k:c[k]for k in('name','slot','cycle','owner','role')},
        controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),maximum_images=3,
        changed_ROM_bytes=3,ordinary_inputs_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False)
