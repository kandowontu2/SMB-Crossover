"""Keep every live assertion, avoid full JSON disk writes inside each30th frame."""
import argparse,json,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha

O=R/'build/bub-menu-candidate-1102-v2'
PIN='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');args=ap.parse_args()
    source=O/('native-landing-'+args.identity+'-full11-intercept/controller.lua');text=source.read_text()
    negative=O/'native-landing-bub-full11-intercept/capture'
    q=json.loads((negative/'bub-observer.json').read_text())
    assert q['completed_Main']==1127 and q['physical_frames']==3060 and q['failures']==0
    assert q['captures']==2 and q['phases']['cross']['last_x']==768
    log=(negative/'combined-landing-controller.log').read_text()
    assert 'Maximum execution time (1 seconds) exceeded' in log
    # The event-wide watchdog includes observer serialization and file IO
    # before full_tick. Its last successful write is exactly checkpoint3060;
    # none of the new capture-recovery branches have run yet.
    old='  if frames%30==0 then write()end'
    assert text.count(old)==1
    text=text.replace(old,'  -- All checks remain live; the full receipt is written at terminal success/failure.')
    old=" elseif phase=='fullstage'then full_tick(finish)"
    new=""" elseif phase=='fullstage'then
  local started=os.clock()
  local ok,why=pcall(full_tick,finish)
  if not ok then
   -- A bounded observer-only error record also survives a caught host Lua
   -- timeout before a normal fullstage assertion can emit its full receipt.
   local q=BUB_OBSERVER.summary()
   local f=io.open(OUTPUT..'callback-error.json','w')
   if f then
    f:write(BUB_OBSERVER.json({error=tostring(why),Main=q.completed_Main,
     frame=frame,part=full_part,step=full_step,index=full_index,
     x=full_x(),y=r('Player_Y_Position'),cpu_seconds=os.clock()-started,
     source_checks=q.checks,source_failures=q.failures})..'\\n');f:close()
   end
   error(why)
  end"""
    assert text.count(old)==1;text=text.replace(old,new)
    # No live check, accepted input, physical hook, or terminal writer changes.
    assert text.count('check(')==source.read_text().count('check(')
    assert "finish=function()write();return summary()end" in text
    assert "local function full_fail(why)local q=BUB_OBSERVER.finish();full_write(false,why,q);assert(false,why)end" in text
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    proof=O/'callback-watchdog-v24.json'
    if not proof.exists():
        proof.write_text(json.dumps(dict(passed=True,native=False,ROM_changed=False,ROM_sha256=PIN,
            preserved_negative=dict(folder=str(negative.relative_to(R)),observer_sha256=sha(negative/'bub-observer.json'),
                log_sha256=sha(negative/'combined-landing-controller.log'),physical_frame=3060,completed_Main=1127,
                actual_phase='cross3',actual_x=768,source_failures=0,recovery_had_run=False),
            bounded_control_flow='No self-recursive full_tick call. All its loops are finite6native slots or15source pool slots. The new grow/clear-route guards are false throughout the last saved cross3 phase.',
            diagnosis='Wall-clock timeout is consistent with same-endFrame periodic full JSON serialization/file IO before full_tick. IO delay is an inference, not a proven hardware or source defect.',
            upstream_model='https://github.com/SourMesen/Mesen2/blob/master/Core/Debugger/ScriptingContext.cpp#L337-L354',
            unchanged='Every live source/header/coordinate/CHR/RGB/OAM assertion and terminal/failure full observer writer; all v23 controls and candidate bytes.',
            observer_change='Remove redundant fullJSON checkpoint every30physicalframes. Existing compact routeCSV remains; terminal success/gameplay failure writes complete observer. A caught callback error additionally writes one small callback-error.json.',
            native_qualification_pending=True),indent=2)+'\n')
    target=O/('native-landing-'+args.identity+'-full11-intercept2');rom=O/'combined-landing.nes'
    prepare(target,rom,text,[Path(__file__),source,proof,O/'combined-landing.json',O/'landing-v21-proposal.json'],
        expected=PIN,timeout=240,allow_interactive=True,
        scope='Observer-only successor of frozenv23: remove redundant every30frame fullJSON rewrites from endFrame wall-clock budget. All real source/physical transport/art/header assertions still execute at original cadence, and terminal/failure full observer receipt remains. One bounded callback-error diagnostic added. Controller behavior/strict fullstage/lives/injury/7crossings and ROM unchanged; interception recovery still nativepending becausev23hostwatchdogstopped beforecapture.')
    ready=json.loads((target/'ready.json').read_text());assert all(sha(Path(p))==h for p,h in ready['bindings'].items())
    print(json.dumps(dict(READY=True,identity=args.identity,ROM_sha256=PIN,path=str(target),Lua54_syntax=True,all_bindings_verified=True,native=False)))


if __name__=='__main__':main()
