"""Capture real G movement inputs, then supply them through ordinary H controls."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-source-dj'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def run(args,log):
 with log.open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 return q.returncode
def main():
 assert not J.exists();J.mkdir()
 g=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';h=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json'
 assert sha(g)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0'and sha(h)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 used=workspace_bytes(R);assert used+400000000<80000000000
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';im=module(helper,'samus_dj_image');image=im.Image(g.parent/'smb-crossover-mmc3.nes')
 pc=image.ram['FarcallJmpTarget_SMC']+3;config=dict(entry=image.hook('SamusMovement'),audio=image.hook('AudioUpdate'),ramReturn=image.hook('FarCallCommon',delta=pc-image.ram['FarCallCommon']))
 prior=R/'build/roster-through-2-2/root49-g-samus-boss-g-2-v0-mmc3';observer=V/'root49-current-g-samus-a/observer-g.lua'
 capture=module(R/'tools/audit/capture_roster49_samus_f_clock_ci.py','samus_dj_capture')
 policy=J/'G-observer.lua';policy.write_text('CLOCK_CAPTURE='+im.lua(config)+'\n'+capture.BODY.replace('dofile(OBSERVER)','dofile('+im.lua(observer.as_posix())+')'))
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(image.path),'--tag','root49-g-samus-producers-dj','--policy',str(policy),'--replay',str(prior/'inputs.csv'),'--frames','24145','--timeout','900','--workspace-cap-gb','80']
 prep=dict(script_sha256=sha(__file__),checkpoint_G_sha256=sha(g),checkpoint_H_sha256=sha(h),producer_policy_sha256=sha(policy),dependencies={str(p.relative_to(R)):sha(p)for p in[helper,observer,prior/'inputs.csv',prior/'trace.csv',prior/'manifest.json',R/'tools/audit/capture_roster49_samus_f_clock_ci.py']},workspace_before=used,phase_cap=400000000,reserve=100000000,global_cap=80000000000,scope='G first four-stage native producer reference only. H consumes ordinary controller buttons on actual compiled movement completion/parsed-input acknowledgment. Neither poses nor savestates are transferred. No identical scheduling or complete route/arsenal assumed.')
 (J/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');(J/'G-command.json').write_text(json.dumps(args,indent=2)+'\n')
 q=run(args,J/'G-native.log');d=R/'build/roster-through-2-2/root49-g-samus-producers-dj-2-v0-mmc3';m=json.loads((d/'manifest.json').read_text())
 assert q==1 and m['result']['failure']=='frame-limit'and m['result']['frames']==24145,m.get('result')
 rr=lambda p:list(csv.DictReader(p.open(newline='')))
 assert rr(d/'inputs.csv')==rr(prior/'inputs.csv')[:24144]
 assert rr(d/'trace.csv')==rr(prior/'trace.csv')[:24145]
 producers=rr(d/'samus-producers.csv');returns=rr(d/'samus-producer-returns.csv');assert len(producers)==len(returns)
 fields=['index','frame','poll','world','level','area','areaType','engine','x','y','yHigh','state','power','held','ab','previousAB','ball','crouch','flip','jumped','vx0','vx1','vx2','vy0','vy1','vy2','xf0','xf1','yf0','yf1','released','timer','injury']
 ref=J/'G-producers.lua';ref.write_text('return{\n'+',\n'.join('{'+','.join(z[n]for n in fields)+'}'for z in producers)+'\n}\n')
 original=V/'root49-current-g-samus-a/clock-c-ck/policy.lua';body=original.read_text();start=body.index('local C=SOURCE_CLOCK');body=body[start:]
 oldref='C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/root49-current-g-samus-a/clock-c-ck/source-F-reference.lua';assert body.count(oldref)==1;body=body.replace(oldref,ref.as_posix())
 fallback='C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/root49-current-g-samus-a/clock-c-ck/fallback-D-pose.lua';assert body.count(fallback)==1
 # Continue the actual G endpoint with the grounded-combat policy; the new
 # controller must validate its own H pose instead of assuming old timing.
 ground=V/'root49-samus-h-ground-dh/policy.lua';body=body.replace(fallback,ground.as_posix())
 a=body.index(' if not q then');b=body.index('\n pacing:write',a)
 body=body[:a]+' if not q then return fallback(c)end\n'+body[b:]
 hp=J/'H-policy.lua';hp.write_text('SOURCE_CLOCK='+im.lua(config)+'\n'+'dofile('+im.lua(observer.as_posix())+')\n'+body)
 hi=im.Image(h.parent/'smb-crossover-mmc3.nes')
 for z in config.values():assert list(hi.raw[z['rom_offset']:z['rom_offset']+8])==z['bytes']
 receipt=dict(G_exit=q,G_manifest_sha256=sha(d/'manifest.json'),G_rows=len(producers),G_literal_input_and21trace=True,G_reference_sha256=sha(ref),H_policy_sha256=sha(hp),fallback_sha256=sha(ground),original_H_clock_template_sha256=sha(original),compiled_G_H_guards_literal=True)
 (J/'producer-review.json').write_text(json.dumps(receipt,indent=2)+'\n');print('G_ACTUAL_PRODUCERS',len(producers),flush=True)
 assert workspace_bytes(R)+200000000<80000000000
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(hi.path),'--tag','root49-h-samus-source-dj','--policy',str(hp),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'H-command.json').write_text(json.dumps(args,indent=2)+'\n');code=run(args,J/'H-native.log')
 out=R/'build/roster-through-2-2/root49-h-samus-source-dj-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text())
 result=dict(exit=code,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False);(J/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
