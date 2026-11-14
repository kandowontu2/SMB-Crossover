"""Iron's completed-return controls with an earned near-peak stair mount."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_completed_full11_1114 as Previous

PIN,ROM,R,W,N=Previous.PIN,Previous.ROM,Previous.R,Previous.W,Previous.N
Frozen,POLICY=Previous.Frozen,Previous.POLICY
IDENTITIES={'iron':Previous.IDENTITIES['iron']}
normalize=Previous.normalize
PREVIOUS_SOURCE='01b9a2b2960861be35f1d6c8686e8feafbb200bf5f61c5c1c4ef20c22ee1e1e6'
LUA_SHA={'iron':'db850bb8da6277c64fa4079bc1d73664a641f03e1f4eece45957375f7aed495b'}
MARKER='-- Normal controller inputs and readonly native witnesses. No game-state writes.'

MOUNT=r'''
choose=(function(base)
 local data={{begin=2096,peak=2192,far=2240},{begin=2336,peak=2432,far=2480}}
 local phases,heldAt,releaseUntil={},{},{}
 return function(c)
  if c.world~=0 or c.level~=0 then return base(c)end
  local index,s
  for i,v in ipairs(data)do if c.x>=v.begin and c.x<v.far then index,s=i,v;break end end
  if not s then return base(c)end
  if c.grounded and c.y<=112 and c.x>=s.far-15 then
   phases[index]='done';return{right=true},'mount-'..index..'-far-landing'
  end
  local phase=phases[index]or'mount'
  if phase=='done'then return{right=true},'mount-'..index..'-done'end
  local b={right=c.x<s.peak,left=c.x>s.peak+1}
  if phase=='mount'then
   if c.grounded and c.y<=112 then
    phases[index]='release';releaseUntil[index]=c.update+4;heldAt[index]=nil
    return b,'mount-'..index..'-release'
   end
   if c.grounded then
    if c.heldA then heldAt[index]=nil;releaseUntil[index]=c.update+4
    elseif c.update>=(releaseUntil[index]or 0)then heldAt[index]=c.update;b.a=true end
   elseif heldAt[index]then b.a=c.update-heldAt[index]<44 end
   return b,'mount-'..index..'-mount'
  end
  if phase=='release'then
   if c.grounded and c.y>112 then phases[index]='mount';return b,'mount-'..index..'-retry'end
   if c.grounded and c.y<=112 and c.x>=s.peak-1 and c.x<=s.peak+1
      and not c.heldA and c.update>=(releaseUntil[index]or 0)then
    phases[index]='cross';heldAt[index]=c.update
    return{right=true,a=true},'mount-'..index..'-cross'
   end
   return b,'mount-'..index..'-release'
  end
  if phase=='cross'then
   if c.grounded and c.y>112 and c.update-heldAt[index]>4 then
    phases[index]='mount';heldAt[index]=nil;releaseUntil[index]=c.update+4
    return b,'mount-'..index..'-retry'
   end
   return{right=true,a=c.update-heldAt[index]<44},'mount-'..index..'-cross'
  end
  error('Unknown source-controlled mount phase')
 end
end)(choose)
'''


def bindings(raw,key='iron'):
    assert key=='iron'
    return Previous.bindings(raw,key)


@lru_cache(maxsize=1)
def controller(raw,key='iron'):
    assert key=='iron'
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    text=Previous.controller(raw,key)
    assert text.count(MARKER)==1
    text=text.replace(MARKER,MOUNT+'\n'+MARKER,1)
    Frozen.LuaRuntime().compile(text)
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key='iron'):
    assert key=='iron'
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        prior_completed_counter_Lua_SHA256=Previous.LUA_SHA[key],
        ordinary_controls_mount_each_actual_near_peak_before_fresh_gap_jump=True,
        original_jump_physics_and_completed_Main_interleave_fix_unchanged=True,
        other_three_factories_unchanged=True)
    return q
