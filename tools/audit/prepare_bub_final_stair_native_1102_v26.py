"""Bind both source-proven supported normal jumps, with actual entry snapshots."""
import argparse,json,re,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/'native-landing-bub-full11-final-stair/controller.lua';text=source.read_text()
    proof=O/'final-stair-gap-v25-CPU.json';p=json.loads(proof.read_text())
    assert p['passed']and p['ROM_sha256']==PIN
    cases=[c for c in p['cases']if c['foot_probe_dx']==4];contracts=[]
    assert len(cases)==2
    for c in cases:
        es=[e for e in c['original_D36B_events']if 2432<=e['x']<2480]
        assert[(e['x'],e['y'])for e in es]==[(2444,112),(2473,112)]
        assert all(e['native_state']==0 and e['prior_support']==0 and e['source_keys']&128 for e in es)
        def solid(x,y):return any(a<=x<b and top<=y<208 for a,b,top in p['geometry'])
        support=[dict(x=e['x'],y=e['y'],native_state=e['native_state'],
            left=solid(e['x']+1,e['y']+32),right=solid(e['x']+14,e['y']+32))for e in es]
        assert support[0]['left']and not support[0]['right']and support[1]['right']and not support[1]['left']
        assert c['crossing']['x']==2501 and c['crossing']['y']==128 and c['lives']==2 and not c['source_injury']
        contracts.append(dict(identity=c['identity'],actual_original_jump_support=support,far_landing=c['crossing']))
    # Rebind only the two literal identity/menu plans for Bob. All physical
    # entry metadata and the copied source are identical between identities.
    refs=[]
    if args.identity=='bob':
        bob=O/'native-landing-bob-full11-rearm2/controller.lua';bt=bob.read_text();refs.append(bob)
        for prefix in['local BUB_NATIVE_OBSERVER_CONFIG=','local Q=']:
            old=next(x for x in text.splitlines()if x.startswith(prefix));new=next(x for x in bt.splitlines()if x.startswith(prefix))
            assert text.count(old)==1;text=text.replace(old,new)
    anchor='local full_normal_takeoff=nil'
    assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\nlocal full_normal_actual={} ')
    # Capture the actual original D36B instruction entry, rather than only
    # the requested input. This is a physically qualified source callback.
    anchor='local function full_rearm_has_support(actor)'
    hook="""do
 local h=BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B
 emu.addMemoryCallback(function()
  if phase~='fullstage'or full_part~='normal-pit'then return end
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=emu.memType.nesWorkRam or a.address~=h.physical then return end
  for i,v in ipairs(h.bytes)do assert(ram(h.pc+i-1)==v,'Actual original normal jump entry')end
  assert(#full_normal_actual<2,'At most two measured original final-pit jumps')
  local q=full_support_probe();local actor=Q.launch.bob==1 and 0x42 or 0x2e
  assert(q.native_state==0 and(q.foot[2].solid or q.foot[4].solid),'Actual original final-pit jump has native left or right foot support')
  assert(full_state(actor+9)==0 and full_state(actor+1)&128~=0,'Original normal jump has genuine A and no bubble support marker')
  q.original_PC=h.pc;q.Main_pending=BUB_OBSERVER.summary().completed_Main+1
  q.source_held=full_state(actor+1);q.support_marker=full_state(actor+9)
  full_normal_actual[#full_normal_actual+1]=q
 end,emu.callbackType.exec,h.pc)
end

"""
    assert text.count(anchor)==1;text=text.replace(anchor,hook+anchor)
    anchor='  actual_enemy_states=full_enemy_snapshot(),'
    assert text.count(anchor)==1;text=text.replace(anchor,anchor+'\n  actual_normal_pit_jump_entries=full_normal_actual,')
    start=text.index(" elseif full_part=='normal-pit'then")
    end=text.index(" elseif full_part=='march'then",start)
    new=""" elseif full_part=='normal-pit'then
  full_pad={right=true};full_min_y=math.min(full_min_y,y)
  if grounded then
   local need=full_solid(x+20,y+31)or not full_solid(x+4,y+32)
   if need and(full_state(actor+3)==0 or full_state(actor+3)==3)then
    full_ground_pulse=full_ground_pulse+1;full_pad.a=full_ground_pulse<=3
   else full_ground_pulse=0 end
  else full_ground_pulse=0 end
  if full_step>=5 and q.source_total_jump_starts<=full_ride_base.source_total_jump_starts then full_fail('Final pit missed genuine original normal jump')end
  if q.source_bubble_ride_restarts~=full_ride_base.source_bubble_ride_restarts or q.launches~=full_ride_base.launches then full_fail('Final pit normal jumps were unexpectedly bubble-assisted')end
  local starts=q.source_total_jump_starts-full_ride_base.source_total_jump_starts
  if starts>2 then full_fail('Final pit exceeded measured two original supported jumps')end
  if x>=obstacle.right+8 and grounded then
   if starts<1 or starts~=#full_normal_actual then full_fail('Final pit lacks actual source jump/support records')end
   full_clears[#full_clears+1]={kind=obstacle.kind,left=obstacle.left,right_exclusive=obstacle.right,
    Main=q.completed_Main,x=x,y=y,minimum_anchor_y=full_min_y,
    ability='original-normal43px-supported-jumps',actual_takeoffs=full_normal_actual,
    original_jump_starts=starts,original_support_restarts=0}
   full_event('actual-supported-final-pit-normal-jump-crossing')
   full_index=full_index+1;full_part='march';full_step=0;full_pad={right=true}
  elseif full_step>500 then full_fail('Original normal jumps failed final authored pit')end
"""
    text=text[:start]+new+text[end:]
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    assert 'if#full_clears~=7' in text and 'if full_stationary>500' in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    contract=O/'final-stair-gap-v26-contract.json'
    if not contract.exists():
        contract.write_text(json.dumps(dict(passed=True,native=False,ROM_sha256=PIN,source_physics_changed=False,
            cases=contracts,CPU_receipt=dict(path=str(proof.relative_to(R)),sha256=sha(proof)),
            root_approval='Two genuinely supported jumps are acceptable for1-1 when native right-foot overlaps authored farbank and original landing/reset occurred; retain actual takeoff/support/farlanding records.',
            scope='v25 CPU control performs two authentic original jumps at2444 and2473; second has native right-foot support on farbank2480, not an air jump. Packet reproduces same4pxfoot control and independently records physicallyqualified D36B entries, realfoot support/A/no bubblemarker, actual supported farlanding. Nativepending.'),indent=2)+'\n')
    target=O/('native-landing-'+args.identity+'-full11-supported-stair');rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,proof,contract,O/'combined-landing.json',O/'landing-v21-proposal.json',*refs],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Controller-only source-proven finalstair traversal, bothidentityCPU original43pxjumps at2444 leftfoot and2473 rightfoot-supported farbank. ActualphysicalD36B callbacks must independently record nativeground/solidfoot/A/nobubblesupport for each accepted jump, max2, then genuine supportedfarlanding. Sixearlierbubblecrossings/naturalcombat/interception unchanged. All7authoredcrossings/active1-2/noinjury/lives/source/physicalheadersart guards strict. ROM/helpers unchanged.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True,native=False)))


if __name__=='__main__':main()
