"""Measure actual H Mega Man underground CPU work, excluding native interruptions."""
from pathlib import Path
import collections,csv,hashlib,importlib.util,json,statistics,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-megaman-h-profile-ds'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('mm_h_ds',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 names=['GameLoop','GameCoreRoutine','EnemiesAndLoopsCore','PlayerGfxHandler','DrawAllMetasprites','DrawMetasprite','AreaParserTaskHandler','BlockObjectsCore','MiscObjectsCore','GuestPostEnemyCollision','InventoryUiTick','PlayerCtrlRoutine','MegaManMovement','MegaManWeapons','MegaManDrawShots','MegaManGraphics','RemainingWeapons','AudioUpdate','MegaManAudioUpdate','MegaManAudioNativeUpdate']
 hooks={n:image.hook(n)for n in names};hooks.update(NMI=image.hook('NonMaskableInterrupt'),IRQ=image.hook('IrqScrollSplit'),NMI_END=image.hook('NonMaskableInterrupt',delta='last'),IRQ_END=image.hook('IrqScrollSplit',delta='last'))
 pc=image.ram['FarcallJmpTarget_SMC']+3;ret=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon'])
 scoped=V/'root49-current-f-samus-exclusive-profile-bj/profile-actual-ram-return.lua';assert sha(scoped)=='69876d2888b8461512b4129537fa4f30919dc09d2a9bdab0437be9a1a24c47b5'
 source=R/'build/roster-through-2-2/root49-h-megaman-dg-1-v0-mmc3';m=json.loads((source/'manifest.json').read_text());assert m['verified_through_2_2']and m['rom_sha256']==sha(image.path)
 policy=J/'policy.lua';policy.write_text('ORDINARY_PROFILE='+im.lua(dict(hooks=hooks,ram=image.ram,ram_return=ret,start_frame=6600,stop_frame=8800,base_policy=(source/'policy.lua').as_posix()))+'\nreturn dofile('+im.lua(scoped.as_posix())+')\n')
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+150000000<80000000000
 prep=dict(script_sha256=sha(__file__),checkpoint_H_sha256=sha(cp),policy_sha256=sha(policy),profile_helper_sha256=sha(scoped),source_manifest_sha256=sha(source/'manifest.json'),source_inputs_sha256=sha(source/'inputs.csv'),hooks=hooks,ram_return=ret,phase_cap=150000000,reserve=50000000,global_cap=80000000000,workspace_before=used,scope='Cold complete ordinary H prefix; actual6600..8800 underground function calls/actual ROM or compiled farcall RAM returns/SP/8byte guards. Subtract completed nested IRQ/NMI costs; parent scopes still contain child functions and must not be added as independent shares. No runtime/state/controller changes or all-weapon/whole-game optimization claim.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','1','--mapper','mmc3','--rom',str(image.path),'--tag','root49-h-megaman-profile-ds','--policy',str(policy),'--replay',str(source/'inputs.csv'),'--frames','8850','--timeout','900','--workspace-cap-gb','80']
 (J/'command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 d=R/'build/roster-through-2-2/root49-h-megaman-profile-ds-1-v0-mmc3';a=json.loads((d/'manifest.json').read_text());assert q.returncode==1 and a['result']['failure']=='frame limit'and a['result']['frames']==8850
 rr=lambda p:list(csv.DictReader(p.open(newline='')))
 literal={}
 for n in['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']:
  x,y=rr(d/n),rr(source/n);literal[n]=x==y[:len(x)];assert literal[n],n
 groups=collections.defaultdict(list)
 for line in(d/'ordinary-profile.jsonl').open():
  z=json.loads(line);assert z['exclusive_cycles']>=0 and z['entry_ISR_depth']==0;groups[z['name']].append(z)
 result={}
 for name,z in groups.items():
  cycles=sorted(x['exclusive_cycles']for x in z);result[name]=dict(calls=len(z),median=statistics.median(cycles),p95=cycles[int((len(cycles)-1)*.95)],maximum=max(cycles),total=sum(cycles),interrupt_cycles_excluded=sum(x['interrupted_cycles']for x in z))
 out=J/'review.json';out.write_text(json.dumps(dict(status='PASS_ACTUAL_H_MEGAMAN_UNDERGROUND_PROFILE',script_sha256=sha(__file__),preparation_sha256=sha(J/'preparation.json'),manifest_sha256=sha(d/'manifest.json'),source_input_trace_hardware_prefix_literal=literal,scopes=result,limits=prep['scope'],goal_complete=False),indent=2)+'\n');print(json.dumps(dict(review_sha256=sha(out),scopes=result)),flush=True)
if __name__=='__main__':main()
