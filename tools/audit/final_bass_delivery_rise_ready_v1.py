"""A narrow observation-only successor to the preserved first physical failure."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,sys
from final_item_abilities_static_prepare_v2 import ROOT,D
from final_item_abilities_run import lua
from final_item_abilities_remaining731_run_v1 import verify_manifest
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location
from parodius_visibility_hud_static_startup_v1 import MOCK
from final_bass_delivery_run_v1 import SHA
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--negative',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--lua-root',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 verify_manifest(a.ready/'manifest.json');verify_manifest(a.negative/'manifest.json');np=json.loads((a.negative/'proof.json').read_text());assert np['negative_preserved']and np['native_aggregate_remains_FALSE']
 old=Path(json.loads((a.ready/'proof.json').read_text())['output']);cfg=json.loads((old/'config.json').read_text());cfg['pickup_art']={int(k):v for k,v in cfg['pickup_art'].items()};script=(old/'run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert script.startswith(prefix);body=script[len(prefix):]
 original="""hook('InventoryRisePickup',function()
 if not entered or phase~='collect'or not current or current.item==nil then return end
 if emu.getState()['cpu.x']==5 and current.item>0 and r('TimerControl')==0 then
  current.riseCalls=current.riseCalls+1
 end
end)
"""
 replacement=(ROOT/'tools/audit/final_bass_delivery_rise_observer_v1.lua').read_text()+'\n';assert body.count(original)==1;new=body.replace(original,replacement)
 before="if current.item>0 then assert(current.riseCalls==48 and current.revealY-r('Enemy_Y_Position',5)==16,'Exact private48-active-update/16pixel rise')end"
 after="""if current.item>0 then
      event('actual-rise-endpoint',{entryCount=current.riseEntryCount or 0,acceptedReturns=current.riseCalls,phaseWrites=current.risePhaseWrites or 0,yWrites=current.riseYWrites or 0,startY=current.riseStartY,revealY=current.revealY,terminal=riseSnapshot()})
      assert(current.riseCalls==48 and current.risePhaseWrites==48 and current.riseYWrites==16 and current.riseStartY-r('Enemy_Y_Position',5)==16 and current.revealY-r('Enemy_Y_Position',5)==16,'Exact private48-accepted-updates/16-source-decrements/full-rise')
     end"""
 assert new.count(before)==1;new=new.replace(before,after)
 restored=new.replace(after,before).replace(replacement,original);assert restored==body
 b=scoped_load(old/'candidate.nes');assert sha(old/'candidate.nes')==SHA;start=location(b,'InventoryRisePickup');n=int(b['syms']['InventoryRisePickup']['size'],0);raw=b['raw'][start:start+n]
 cfg['rise_writers']={}
 for name in ['InvRisePhase','InvPickupOwner','InvPickup','Enemy_State','Enemy_Y_Position']:cfg['ram'][name]=address(b,name)
 for kind,name,opcode,zpopcode in [('phase','InvRisePhase',0xfe,0xf6),('y','Enemy_Y_Position',0xde,0xd6)]:
  addr=address(b,name);pattern=bytes([zpopcode,addr])if addr<256 else bytes([opcode,addr&255,addr>>8]);assert raw.count(pattern)==1;delta=raw.index(pattern);cfg['rise_writers'][kind]=dict(address=address(b,'InventoryRisePickup')+delta,bank=(start-16)//8192,bytes=list(pattern))
 out=a.output/'native';out.mkdir()
 for ext in['.nes','.dbg','.lbl','.map']:shutil.copy2(old/('candidate'+ext),out/('candidate'+ext))
 put(out/'config.json',cfg);(out/'run.lua').write_text('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+new,encoding='utf-8');shutil.copy2(old/'inherited-NMI-stack-APU-guards.lua',out/'inherited-NMI-stack-APU-guards.lua')
 sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 tests="""
local testCount=0
local function rejected(f)local ok=pcall(f);assert(not ok);testCount=testCount+1 end
for _,state in ipairs({1,2,8,16})do for phase=0,2 do
 local b={accepted=true,phase=phase,state=state,y=152};local move=phase==2;local state2=state+(move and 1 or 0);if state2>=17 then state2=128 end
 local a={phase=(phase+1)%3,state=state2,y=152-(move and 1 or 0)}
 assert(riseExpected(b,a));testCount=testCount+1
 rejected(function()riseExpected(b,{phase=a.phase,state=a.state,y=a.y+1})end)
 rejected(function()riseExpected(b,{phase=(a.phase+1)%3,state=a.state,y=a.y})end)
 rejected(function()riseExpected(b,{phase=a.phase,state=(a.state+1)%256,y=a.y})end)
 b.accepted=false;assert(not riseExpected(b,{phase=phase,state=state,y=152}));testCount=testCount+1
 rejected(function()riseExpected(b,{phase=phase,state=state,y=151})end)
end end
RISE_OBSERVER_MODELS=testCount
"""
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Startup mutation")end;emu.getScreenBuffer=function()local t={};for i=1,256*240 do t[i]=0xff000000 end;return t end');rt.execute((out/'run.lua').read_text()+tests)
 count=rt.eval('#callbacks');assert count==73 and rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')and rt.eval('#events[emu.eventType.endFrame]')==3;assert rt.eval('RISE_OBSERVER_MODELS')==72
 rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
 q=Arena(b,9);q.set('InvPickupOwner',9,5);q.set('InvPickup',2,5);q.set('Enemy_State',1,5);q.set('Enemy_Y_Position',152,5);phaseWrites=yWrites=0;chronology=[]
 for call in range(48):
  beforeRow={n:q.get(n,5)for n in ['InvRisePhase','Enemy_State','Enemy_Y_Position']};_,trace=q.invoke('InventoryRisePickup',x=5)
  for t in trace:
   for kind,name in [('phase','InvRisePhase'),('y','Enemy_Y_Position')]:
    if t['pc']==cfg['rise_writers'][kind]['address']and t['address']==address(b,name)+5:
     if kind=='phase':phaseWrites+=1
     else:yWrites+=1
  chronology.append(dict(call=call+1,before=beforeRow,after={n:q.get(n,5)for n in beforeRow}))
 assert phaseWrites==48 and yWrites==16 and q.get('Enemy_State',5)==128 and q.get('Enemy_Y_Position',5)==136
 controls=dict(passed=True,native_run=False,ROM_sha256=SHA,read_only_observation_delta=True,only_two_replacements_reverse_exact=True,all_controller_seed_caps_other_mechanics_default_no_result_writes_and_shared_guards_literal=True,original_entry_predicate_retained_as_diagnostic=True,actual_return_models=72,actual_source_INC_phase_writes=48,actual_source_DEC_y_writes=16,actual_CPU_chronology=chronology,source_writers=cfg['rise_writers'],native_original_operands_not_recoverable=True,static_callbacks=count,dispatcher_last=True,endFrame_callbacks=3,original_strict_module_sha256=sha(out/'inherited-NMI-stack-APU-guards.lua'),scope='This does not retag the original entry-only failure. Actual native count/endpoint remain pending. Strong48accepted-returns+48sourceincrements+16decrements+16pixels+maturestate contract replaces entry-as-clock assumption.')
 put(a.output/'source-controls.json',controls);put(a.output/'exact-replacements.json',[dict(before=original,after=replacement),dict(before=before,after=after)])
 review=dict(passed=True,agent_visual_review=True,ROM_sha256=SHA,native_aggregate_remains_FALSE=True,actual_complete_wholeframes=18,selection_path=str(a.negative/'selection.json'),selection_sha256=sha(a.negative/'selection.json'),sheet_path=str(a.negative/'whole-PPU-negative-contact.png'),sheet_sha256=sha(a.negative/'whole-PPU-negative-contact.png'),partial_failure_snapshot_scope='Viewed separately; current partial buffer at assertion, never labeled completedPPU885.',observations=['Mushroom rises above used block, explicitly aligned downward aftermaturity, native60update transform andfreebuster use/cleanup visible.','METAL icon emerges progressively above block through884. No unexpected terrain/background shift apparent in these selected sparse scenes.','Review does not close original compound rise assertion or certify full source-art/allpixels/allitems/BALANCE/Hard/lag/audio.'])
 put(a.output/'negative-agent-visual-review.json',review)
 report=ROOT/'docs/qa/final-bass-delivery-negative-observer-2026-10-26.txt';report.write_text('Bass first four-reward native negative and SOURCE-only rise observer successor\n\nExact3b/Easy0. ONE run exited1; worker released, no retry. Original7ba7853e... remainsFALSE. UntouchedPRNG delivered mushroom0 (sample1) thenMETAL2(sample36); only first reward completed. Mushroom reveal371/mature437/contactalignment468/commit528,60committedtransform updates, buster594/cleanup810/completion819. METAL reveal833, failed compound48count/16pixel assertion885:205:173/update548. Four-reward/BALANCE outcomes remain incomplete.\n\nOriginal failure omitted terminal record/count/Y operands. Exact native entry count and which conjunction term failed cannot be recovered honestly. Source initializes state1/phase0 and requires16decrements to17→128. Saved actualsource/hardware DMA METAL OAM firstY160at836→lastY145at884 implies actorY152→137; mature assertion occurredlater. This is bounded publication evidence, not invented terminalRAM. 884completePPU/771complete256DMA/459scoped safeenables pass mechanically, no FPS/globalNMI claim.\n\nNew observer preserves oldentrypredicate as diagnostic, logs eachsource entry/fullrealSP+bank return, and counts real phaseINC/YDEC statechanging writes at linkedPCs (RMWdummy retained but notclocked). Strong48acceptedreturns+48INC+16DEC+16pixels+maturestate replaces unqualifiedentryclock; terminaloperandsdump precedesguard. Seventy-two finite returnmodelcontrols and actual48-callCPUchronology pass; all othermechanics/controller/seeds/caps/guardbytes unchanged. Native successor UNGRANTED/unrun.\n\nAgent viewed18actualwholeframes plus separatelyclassified partialassertionsnapshot. Source/capture hashes in '+str(a.negative)+'; selectedvisualscope only. Post-rise downward contactalignment stays disclosed. No ROMpatch or gamebug conclusion.\n',encoding='utf-8')
 env=json.loads((a.ready/'environment.json').read_text());put(a.output/'environment.json',env)
 files={Path(q['path'])for q in json.loads((a.ready/'manifest.json').read_text())['bindings']};files.update([Path(__file__),ROOT/'tools/audit/final_bass_delivery_rise_observer_v1.lua',a.ready/'proof.json',a.ready/'manifest.json',a.negative/'proof.json',a.negative/'manifest.json',report]);files.update(q for q in a.output.rglob('*')if q.is_file())
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),bytes=f.stat().st_size,sha256=sha(f))for f in sorted(files,key=str)]))
 command='python -B tools/audit/final_bass_delivery_run_v1.py --ready "'+a.output.as_posix()+'" --native-grant';put(a.output/'proof.json',dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,profile='bass-easy-four-rewards',mode_value=0,maximum_rewards=4,maximum_launches=1,maximum_owned_workers=1,retry=False,source_controls_sha256=sha(a.output/'source-controls.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),output=str(out),script_sha256=sha(out/'run.lua'),source_freeze_sha256=json.loads((a.ready/'proof.json').read_text())['source_freeze_sha256'],stable_command=command,environment=env,original_native_FALSE_proof_sha256=sha(old/'proof.json'),negative_freeze_sha256=sha(a.negative/'proof.json'),observer_only=True))
 verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(files),script_sha256=sha(out/'run.lua'),source_controls_sha256=sha(a.output/'source-controls.json'),stable_command=command),indent=2))

if __name__=='__main__':main()
