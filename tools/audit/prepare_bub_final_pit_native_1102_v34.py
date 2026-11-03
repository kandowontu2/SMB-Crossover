"""Controller-only final-pit ingress on current9cf, with bounded decisions."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
OLD='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-landing-'+args.identity+'-full11-stepback/controller.lua');text=source.read_text()
    proof=O/'final-pit-ingress-v33-CPU.json';q=json.loads(proof.read_text());assert q['passed']and q['ROM_sha256']==PIN
    assert {(c['identity'],c['initial_source_selector'])for c in q['cases']}=={(i,s)for i in[0,1]for s in[0,2,3]}
    assert all(c['final_x']==2502 and c['final_y']==128 and c['lives']==2 for c in q['cases'])
    def once(a,b):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b)
    once(OLD,PIN)
    once('local full_normal_actual={}\n','local full_normal_actual={}\nlocal full_edge_decisions,full_edge_dropped,full_edge_row={},0,nil\n')
    anchor='\n\ndo\n local h=BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B'
    helper='''

local function full_normal_jump_ready(actor)
 -- NativeState0/DY0 and a real native foot are mandatory. The approved
 -- landing adapter clears healthy source2/3 by original D41C before the
 -- PlayerStep that consumes this fresh A. Injury/ascent remain excluded.
 local selector=full_state(actor+3)
 if selector~=0 and selector~=2 and selector~=3 then return false end
 if r('Player_State')~=0 or ram(142)~=0
  or ram(BUB_NATIVE_OBSERVER_CONFIG.ram.Player_Y_HighPos)~=1 then return false end
 local s=full_support_probe()
 return s.foot[2].solid or s.foot[4].solid
end

do
 local h=BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B'''
    once(anchor,helper)
    once('  actual_normal_pit_jump_entries=full_normal_actual,','  actual_normal_pit_jump_entries=full_normal_actual,\n  actual_final_edge_decisions=full_edge_decisions,actual_final_edge_dropped=full_edge_dropped,')
    once(" if full_state(actor+3)&128~=0 or full_state(0x307)~=0 then full_fail('Fullstage source injury/death')end",''' if full_state(actor+3)&128~=0 or full_state(0x307)~=0 then full_fail('Fullstage source injury/death')end
 full_edge_row=nil
 if full_index==7 and x>=2436 and x<=2448 then
  if#full_edge_decisions<48 then
   local side,side_tile=full_solid(x+20,y+31)
   local forward,edge_tile=full_solid(x+4,y+32)
   full_edge_row={Main=q.completed_Main,part=full_part,support=full_support_probe(),
    side=side,side_tile=side_tile,edge_missing=not forward,edge_tile=edge_tile,
    jump_ready=full_normal_jump_ready(actor),previous_source_held=full_state(0x301),
    source_held=full_state(actor+1),source_cooldown=full_state(actor+8),
    prior_pad=r('SavedJoypadBits'),combat=full_combat}
   full_edge_decisions[#full_edge_decisions+1]=full_edge_row
  else full_edge_dropped=full_edge_dropped+1 end
 end''')
    once('elseif edge and x>=2432 and x<2448 and(full_state(actor+3)==0 or full_state(actor+3)==3)then',
         'elseif edge and x>=2432 and x<2448 and full_normal_jump_ready(actor)then')
    # Only final-pit pulses change. Stair retreats and every earlier ability,
    # combat, route, death and cadence guard remain exact frozen v31 text.
    start=text.index(" elseif full_part=='normal-pit'then");end=text.index(" elseif full_part=='march'then",start)
    piece=text[start:end];old='if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then'
    assert piece.count(old)==1;piece=piece.replace(old,'if need and full_normal_jump_ready(actor)then');text=text[:start]+piece+text[end:]
    once('  local ok,why=pcall(full_tick,finish)\n','''  local ok,why=pcall(full_tick,finish)
  if full_edge_row then
   full_edge_row.next_part=full_part
   full_edge_row.requested_pad=(full_pad.right and 1 or 0)|(full_pad.left and 2 or 0)
    |(full_pad.b and 64 or 0)|(full_pad.a and 128 or 0)
  end
''')
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    for guard in["q.native_state==0 and(q.foot[2].solid or q.foot[4].solid)",
                  "full_state(actor+9)==0 and full_state(actor+1)&128~=0",
                  "if#full_clears~=7",'if full_stationary>500',"full_stair_target=x-6"]:assert guard in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    target=O/('native-current-landing-'+args.identity+'-full11-final-pit');rom=O/'combined-current-landing.nes'
    assert not target.exists()
    prepare(target,rom,text,[Path(__file__),source,proof,O/'combined-current-landing.json',O/'actual-stair-route-v30-CPU.json',O/'landing-v21-CPU.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Current9cf Sunny-preserving private landing candidate; controller-only final-pit ingress accepts healthy source0/2/3 only with actual native0/DY0/Yhigh1/realfoot. ExactoriginalD41C+D36B CPU qualifies bothidentities at captured plateau; actualv31 edgepredicate is unrecorded so thispacket logs bounded48acceptededge decisions. Frozen6px supportedstair retreat/directionaljump/air/landing retained. AllphysicalD36Bnative0/realfoot/A/noBubbleMarker guards, max2normalpitjumps, sixearnedbubblecrossings, naturalcombat, noinjury/lives/all7crossings/active1-2/sourcehardware observers remain. No ROM/sourcephysics/ability changes; no emulator run or installation byproducer.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,immutable=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True)))


if __name__=='__main__':main()
