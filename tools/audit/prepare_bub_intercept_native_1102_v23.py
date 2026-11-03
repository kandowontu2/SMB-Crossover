"""Recover an earned ride setup after a natural enemy intercepts its bubble."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-landing-'+args.identity+'-full11-rearm2/controller.lua');text=source.read_text()
    evidence=O/'native-landing-bub-full11-rearm2/capture/full11.json'
    q=json.loads(evidence.read_text());assert q['why']=='Fullstage source injury/death'and q['part']=='grow'
    assert q['index']==4 and q['current_x']==872 and q['initial_lives']==q['final_lives']==2
    assert q['source']['failures']==0 and len(q['clears'])==3
    events=q['source']['events']
    capture=next(e for e in events if e['kind']=='original-source-trap-commit'and e['Main']==1226)
    release=next(e for e in events if e['kind']=='source-timeout-or-camera-release'and e['Main']==1266)
    assert capture['detail']['slot']==release['detail']['slot']==1 and release['detail']['elapsed_source_updates']==39
    assert q['source']['completed_Main']==1271
    # Capture invalidates this ride setup. Do not follow the trapped circle
    # until it expires in the player's face. Reuse the already-qualified
    # original timeout and close grounded combat; no source state is written.
    anchor=" if full_combat then\n  full_contact_sample('completed-combat-Main',false)"
    addition=""" if full_part=='grow'and q.captures>full_ride_base.captures then
  full_part='clear-route';full_step=0;full_pad={}
  full_event('route-bubble-intercepted-by-natural-enemy')
  full_events[#full_events].actual_enemies=full_enemy_snapshot()
 end
 if full_part=='clear-route'then
  if not full_rearm_has_support(actor)then full_fail('Intercepted route cleanup lost actual floor support')end
  if full_step>240 then full_fail('Bounded intercepted route bubble recovery')end
  local trapped=false
  for slot=0,5 do if full_state(0x320+16*slot)~=0 then trapped=true end end
  if trapped and not full_combat then
   -- Original trap clock39 is allowed to complete. Release both buttons;
   -- retreat only over the native body foot's verified solid terrain.
   local target=full_runup(obstacles[full_index])
   local behind=full_solid(x-2,y+32);local inside=full_solid(x+11,y+32)
   full_pad=x>target+1 and behind and inside and{left=true}or{}
   return
  end
 end
"""
    assert text.count(anchor)==1;text=text.replace(anchor,addition+anchor)
    old="if(full_part=='approach'or full_part=='march')and(grounded or full_rearm_has_support(actor))then"
    new="if(full_part=='approach'or full_part=='march'or full_part=='clear-route')and(grounded or full_rearm_has_support(actor))then"
    assert text.count(old)==1;text=text.replace(old,new)
    anchor=" elseif full_part=='grow'then\n  full_pad={right=true,b=full_step<4}"
    replacement=""" elseif full_part=='clear-route'then
  -- Keep a safe grounded position while a surviving natural enemy approaches
  -- the proven close-shot window. The existing combat code above owns its
  -- vertical alignment, original cooldown, fresh B, capture and actual defeat.
  full_pad={}
  local enemy=full_target()
  if not enemy then
   full_event('natural-enemy-corridor-cleared-rearm-original-ride')
   full_part='approach';full_step=0
  end
 elseif full_part=='grow'then
  full_pad={right=true,b=full_step<4}"""
    assert text.count(anchor)==1;text=text.replace(anchor,replacement)
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    proof=O/'intercepted-route-v23.json'
    if not proof.exists():
        proof.write_text(json.dumps(dict(passed=True,native=False,ROM_changed=False,ROM_sha256=PIN,
            preserved_negative=dict(path=str(evidence.relative_to(R)),sha256=sha(evidence),Main=1271,x=872,y=176,part='grow',injury=True,source_observer_failures=0),
            actual_sequence=dict(ride_launch_Main=1216,capture_Main=1226,slot=1,original_release_Main=1266,original_elapsed_updates=39),
            controller_change='On actual new capture while growing a route bubble, keep real floor support, release A/B, retreat only on verified floor to runup and wait for actual saved trap tokens to retire. Existing close grounded combat then clears natural enemies, and the same cooldown/facing/runup logic rearms a new earned ride.',
            unchanged='Candidate bytes, original donor source/timers/physics, fullstage injury/lives/defeat/all7crossings/active1-2 assertions and physical bridge/art/header guards.',
            native_qualification_pending=True),indent=2)+'\n')
    target=O/('native-landing-'+args.identity+'-full11-intercept');rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,proof,O/'combined-landing.json',O/'landing-v21-proposal.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Controller-only natural route-bubble interception recovery justified by frozen v22 actual capture1226/release1266/original39timer/hurt1271. No ROM changes. Grounded real-floor retreat/button release waits for genuine trap retirement, existing close grounded combat earns actual defeats, then original cooldown/facing logic rearms a fresh bubble ride. All strict no-injury/lives/all4pipes/3authoredpits/active1-2/header/CHR/RGB/lastdraw/NativeIn-Out guards retained.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True,native=False)))


if __name__=='__main__':main()
