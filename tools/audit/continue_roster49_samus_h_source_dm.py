"""Use completed DJ native producer capture; retain its host label mismatch."""
from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-samus-h-source-dj'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert J.exists()and not(J/'H-command.json').exists()
 original=R/'tools/audit/run_roster49_samus_h_source_dj.py';prep=json.loads((J/'preparation.json').read_text());assert sha(original)==prep['script_sha256']
 negative=dict(original_script_sha256=sha(original),actual_G_manifest_sha256=sha(R/'build/roster-through-2-2/root49-g-samus-producers-dj-2-v0-mmc3/manifest.json'),reason='Host expected frame-limit, native result literally frame limit. G process terminal1 at intended24145, no native failure or H launch. Resume completed evidence without rerun or changing original receipt.')
 (J/'host-negative-dm.json').write_text(json.dumps(negative,indent=2)+'\n')
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json';assert sha(cp)==prep['checkpoint_H_sha256']
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('samus_dm_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);hi=im.Image(cp.parent/'smb-crossover-mmc3.nes')
 d=R/'build/roster-through-2-2/root49-g-samus-producers-dj-2-v0-mmc3';prior=R/'build/roster-through-2-2/root49-g-samus-boss-g-2-v0-mmc3';m=json.loads((d/'manifest.json').read_text());assert m['result']['failure']=='frame limit'and m['result']['frames']==24145
 rr=lambda p:list(csv.DictReader(p.open(newline='')))
 assert rr(d/'inputs.csv')==rr(prior/'inputs.csv')[:24144]and rr(d/'trace.csv')==rr(prior/'trace.csv')[:24145]
 producers=rr(d/'samus-producers.csv');returns=rr(d/'samus-producer-returns.csv');assert len(producers)==len(returns)
 fields=['index','frame','poll','world','level','area','areaType','engine','x','y','yHigh','state','power','held','ab','previousAB','ball','crouch','flip','jumped','vx0','vx1','vx2','vy0','vy1','vy2','xf0','xf1','yf0','yf1','released','timer','injury']
 ref=J/'G-producers.lua';ref.write_text('return{\n'+',\n'.join('{'+','.join(z[n]for n in fields)+'}'for z in producers)+'\n}\n')
 original_clock=V/'root49-current-g-samus-a/clock-c-ck/policy.lua';body=original_clock.read_text();config=body[:body.index('\ndofile(')];body=body[body.index('local C=SOURCE_CLOCK'):]
 oldref='C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/root49-current-g-samus-a/clock-c-ck/source-F-reference.lua';assert body.count(oldref)==1;body=body.replace(oldref,ref.as_posix())
 fallback='C:/Users/kando/Documents/ChatGPT/SMB Crossover/build/verification/root49-current-g-samus-a/clock-c-ck/fallback-D-pose.lua';ground=V/'root49-samus-h-ground-dh/policy.lua';assert body.count(fallback)==1;body=body.replace(fallback,ground.as_posix())
 a=body.index(' if not q then');b=body.index('\n pacing:write',a);body=body[:a]+' if not q then return fallback(c)end\n'+body[b:]
 observer=V/'root49-current-g-samus-a/observer-g.lua';hp=J/'H-policy.lua';hp.write_text(config+'\n'+'dofile('+im.lua(observer.as_posix())+')\n'+body)
 binding=json.loads((V/'root49-current-g-samus-a/clock-c-ck/preparation.json').read_text())
 # Guard bytes are additionally checked by the native observer on every call.
 assert not any(z in hp.read_text()for z in['emu.write(','emu.setState(','emu.loadSavestate'])
 receipt=dict(script_sha256=sha(__file__),host_negative_sha256=sha(J/'host-negative-dm.json'),G_manifest_sha256=sha(d/'manifest.json'),G_rows=len(producers),G_literal_input_and21trace=True,G_reference_sha256=sha(ref),H_policy_sha256=sha(hp),fallback_sha256=sha(ground),clock_template_sha256=sha(original_clock),checkpoint_H_sha256=sha(cp))
 (J/'producer-review-dm.json').write_text(json.dumps(receipt,indent=2)+'\n');print('G_ACTUAL_PRODUCERS',len(producers),flush=True)
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 assert workspace_bytes(R)+200000000<80000000000
 args=[sys.executable,str(R/'tools/playthroughs/roster_run.py'),'--character','2','--mapper','mmc3','--rom',str(hi.path),'--tag','root49-h-samus-source-dj','--policy',str(hp),'--frames','45000','--timeout','900','--workspace-cap-gb','80']
 (J/'H-command.json').write_text(json.dumps(args,indent=2)+'\n')
 with(J/'H-native.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 out=R/'build/roster-through-2-2/root49-h-samus-source-dj-2-v0-mmc3';m=json.loads((out/'manifest.json').read_text());z=dict(exit=q.returncode,manifest_sha256=sha(out/'manifest.json'),result=m.get('result'),analysis_pending=True,goal_complete=False)
 (J/'result-dm.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z),flush=True)
if __name__=='__main__':main()
