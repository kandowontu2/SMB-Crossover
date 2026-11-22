"""Controller-only a6 SMB3 stock observers, with retained navigation inlined."""

from pathlib import Path

from check_ff_stdout_controller_source_1110 import LuaRuntime
import current_smb3_pickup_binding_1122 as Current
import replay_smb3_alts_full11_1114 as Navigation
from replay_sonic_hidden_life_f7c9_1116 import value

R, ROM, H, PIN = Current.R, Current.ROM, Current.H, Current.PIN
POLICY = R / 'tools/playthroughs/smb3_pickups_1122.lua'
OBSERVER = R / 'tools/audit/ice_climbers_stock_observer_1122.lua'
OBSERVER_SHA = 'c03ec6768f9b4e2b6e3fca0dc36363f2aa6ea4e835900a9d18c42c69444cd83f'
NAVIGATION_SHA = 'ebf11f132514c1e49e8c7945825ae53131d6edaf5be08e0229ac1b5135f41a25'


def once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new, 1)


AFTER_MAIN = r'''
local function score()
 local n=0;for i=0,5 do local d=r('PlayerScoreDisplay',i);assert(d<10,'Native decimal score');n=n*10+d end
 return n
end
local function afterMain()
 if not entered then return end
 updates=updates+1
 local s=state();s.score=score()
 if #tail==12 then table.remove(tail,1)end
 local live={};for i=0,5 do local a=actor(i);if a.flag>0 and a.flag<128 then live[#live+1]=a end end
 tail[#tail+1]={player=s,mask=mask,actors=live}
 assert(identity()and s.world==0 and s.level==0 and s.engine~=11 and r('OperMode')~=3,'Living requested SMB3 identity in ordinary1-1')
 assert(r('M3Ready')==0xb3,'Actual SMB3 constructor remains ready')
 assert(updates<5100,'Bounded authored pickup route')
 local q=checks[tostring(C.stockKind)]
 assert(s.lives==(q.grant and C.stockKind==3 and q.grant.lives or 2),'No unearned life or death')
 for i=0,5 do
  local a=actor(i)
  if a.kind==C.stockKind and a.flag>0 and a.flag<128 and a.id==46 then
   if not q.birth and a.state<128 and math.abs(a.x-C.blockX)<=2 then
    assert(heads[tostring(C.stockKind)],'Real block head contact precedes authored actor birth')
    q.birth={actor=a,player=s}
   end
   if q.birth and q.birth.actor.slot==i and a.state&128~=0 and not q.mature then q.mature={actor=a,player=s}end
  end
 end
 if C.stockKind==2 and q.collect and not q.grant and s.score>=q.collect.score_before+1000 then
  q.grant=s;q.score_credit={before=q.collect.score_before,after=s.score}
 end
 if q.grant and not q.after and s.motor-q.grant.motor>=25 and scope()then
  assert(s.power==q.collect.before.power,'Stock pickup preserves the actual earned SMB3 form')
  if C.stockKind==3 then
   assert(s.lives==q.collect.before.lives+1 and (soundCounts[64]or 0)>q.collect.cue64_before,'Delayed life and actual extra-life cue persist')
  else assert(s.star>0 and s.score>=q.collect.score_before+1000,'Native Star and score credit persist')end
  assert(counts.M3Step_entries==counts.M3Step_returns and counts.M3Movement_entries==counts.M3Movement_returns,'Balanced actual native SMB3 movement and step returns')
  q.after=s;finish(true,'Authored stock pickup, native credit and25 completed original SMB3 steps');return
 end
 clockInput=scope()and choose(context())or{}
end
'''

COLLECTED = r'''
local function collected(p)
 local a=p.actor;local q=checks[tostring(a.kind)]
 assert(q and q.birth and q.mature and not q.collect,'Born and mature actual stock actor before collection')
 assert(r('Enemy_Flag',a.slot)==0,'Actual native actor erase')
 local popup=r('FloateyNum_Control',a.slot)
 assert(popup==(a.kind==3 and 11 or 6),'Native stock popup')
 assert((soundCounts[32]or 0)>p.cue32_before,'Actual new pickup sound write')
 assert((counts.M3CollectPickup_entries or 0)>p.m3_before,'Actual SMB3 stock dispatch reached')
 local s=state()
 assert(s.power==p.before.power,'Collector preserves actual SMB3 form')
 q.collect={actor=a,before=p.before,after=s,popup=popup,boxes=p.boxes,
  score_before=p.score_before,cue64_before=soundCounts[64]or 0,
  native_M3_dispatches=(counts.M3CollectPickup_entries or 0)-p.m3_before}
 if a.kind==2 then
  assert(s.star==35 and r('AreaMusicQueue')==64 and s.lives==p.before.lives,'Native Star timer35/music64 without life mutation')
  q.collect.music=r('AreaMusicQueue')
 else assert(s.lives==p.before.lives,'1-UP awaits the actual delayed INC writer')end
end
'''

COLLECTOR_ENTRY = r'''
  assert(a.state&128~=0,'Native collector receives a fully emerged stock actor')
  q.mature=q.mature or {actor=a,player=state()}
  local off=(a.slot+1)*4;local box=C.ram.BoundingBox_UL_Corner
  local hero,object={},{}
  for i=0,3 do hero[#hero+1]=emu.read(box+i,emu.memType.nesDebug);object[#object+1]=emu.read(box+off+i,emu.memType.nesDebug)end
  local width=math.min(hero[3],object[3])-math.max(hero[1],object[1])+1
  local height=math.min(hero[4],object[4])-math.max(hero[2],object[2])+1
  assert(width>0 and height>0,'Positive actual native collector overlap')
  p.actor=a;p.before=state();p.score_before=score();p.cue32_before=soundCounts[32]or 0
  p.m3_before=counts.M3CollectPickup_entries or 0;p.boxes={player=hero,item=object,width=width,height=height}
'''


def body():
    assert H(OBSERVER.read_bytes()) == OBSERVER_SHA
    s = OBSERVER.read_text(encoding='utf-8')
    s = s.replace("r('SelectedCharacter')==20 and r('IcVariant')", "r('SelectedCharacter')==17 and r('M3Variant')")
    s = s.replace("power=r('IcPower')", "power=r('M3Form'),growth=r('M3Growth'),poof=r('M3Poof')")
    s = once(s, "local expected=C.route=='life' and {0,3} or {0,1,2}", 'local expected={C.stockKind}')
    s = once(s, 'local lifePending', 'local lifePending\nlocal clockInput={}\nlocal counts,soundCounts={},{}')
    s = once(s, 'c.poll=polls;c.char=20;c.variant=C.variant;c.r=r', 'c.frame=updates;c.update=updates;c.poll=updates;c.char=17;c.variant=C.variant;c.r=r')
    s = once(s, 'c.lastA=mask&128~=0', "c.lastA=r('M3Previous')&128~=0")
    s = once(s, 'phase=ICE_STOCK_STATE or {},controller_only=true,files=0,images=0',
             'phase=SMB3_PICKUP_STATE or {},counts=counts,pending_returns=#pending,sound_writes=soundCounts,controller_only=true,no_game_state_seeds=true,files=0,images=0')
    lo, hi = s.index('local function afterMain()'), s.index('local function collected(p)')
    s = s[:lo] + AFTER_MAIN + '\n' + s[hi:]
    lo, hi = s.index('local function collected(p)'), s.index('local function settle()')
    s = s[:lo] + COLLECTED + '\n' + s[hi:]
    s = once(s, "  if p.name=='IcMovement' then motor=motor+1", "  counts[p.name..'_returns']=(counts[p.name..'_returns']or 0)+1\n  if p.name=='M3Step' then motor=motor+1")
    s = once(s, 'pending[#pending+1]=p;register(pc)',
             "if name=='M3Movement'and pc<0x8000 then assert(pc==C.smc_return_pc,'Actual RAM farcall movement return')end\n counts[name..'_entries']=(counts[name..'_entries']or 0)+1\n pending[#pending+1]=p;register(pc)")
    s = once(s, 'p.actor=a;p.before=state()', COLLECTOR_ENTRY)
    s = once(s, "if r('IcVariant')~=C.variant", "if r('M3Variant')~=C.variant")
    s = once(s, 'local b=not entered and menu() or (scope() and choose(context()) or {})', 'local b=not entered and menu()or(scope()and clockInput or{})')
    s = once(s, '  entered=physical', "  entered=physical;clockInput=choose(context())")
    s = once(s, 'local bits={a=128', "emu.addMemoryCallback(guarded('Actual stock cue writes',function(_,v)if entered and(v==32 or v==64)then soundCounts[v]=(soundCounts[v]or 0)+1 end end),emu.callbackType.write,C.ram.Square2SoundQueue)\n\nlocal bits={a=128")
    assert not any(word in s for word in ('IcMovement', 'IcPower', 'IcVariant', 'ICE_STOCK_STATE'))
    return s


def controller(raw, form='toad3', item='1up', *, mode='easy'):
    assert H(Path(Navigation.__file__).read_bytes()) == NAVIGATION_SHA
    config = Current.bindings(raw, form, item, mode=mode)
    names = ['GameLoop', 'M3Movement', 'M3Step', 'M3CollectPickup',
             'HandlePowerUpCollision', 'PlayerHeadCollision']
    if item == '1up':
        names.append('LifeCredit')
    config['hooks'] = {name: config['hooks'][name] for name in names}
    navigation = Navigation.policy()
    policy = POLICY.read_text(encoding='utf-8')
    config.update(base_policy_SHA256=H(navigation.encode()), stock_policy_SHA256=H(policy.encode()),
                  observer_SHA256=H(body().encode()))
    script = '\n'.join((
        'local C=' + value(config), "local ROSTER_CONFIG={name='smb3'}",
        'local SMB3_PICKUP_KIND=C.stockKind',
        'local SMB3_PICKUP_BASE=(function()\n' + navigation + '\nend)()',
        'local choose=(function()\n' + policy + '\nend)()', body(),
    ))
    LuaRuntime().compile(script)
    assert not any(word in script for word in ('emu.write', 'emu.setState', 'io.open', 'dofile', 'saveState', 'loadState', 'takeScreenshot'))
    return script
