"""Existing authored Samus physical-audio checks on private H, both mappers."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-samus-audio-scan-h';J=H/'native-checks-cw'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not J.exists();J.mkdir()
 assert sha(H/'cpu-review-ct.json')=='70bcf833b77d9a3058b37f990c0f66a75df5203ae8bddc4a474fc26d9a86bcee'
 fixtures=['samus-audio-effects','samus-pickup-sfx','samus-world-sfx']
 deps=[R/f'tests/{n}.lua'for n in fixtures]+[R/'tests/guest-world-sfx.lua',R/'tests/menu-bootstrap.lua',R/'tools/run_mesen.py',R/'tools/audit/run_mesen_isolated.py']
 sys.path.insert(0,str(R/'tools/playthroughs'));from roster_run import workspace_bytes
 total=workspace_bytes(R);owned=sum(p.stat().st_size for p in H.rglob('*')if p.is_file());assert owned+50000000+50000000<300000000 and total+50000000<80000000000
 pre=dict(script_sha256=sha(__file__),cpu_review_sha256=sha(H/'cpu-review-ct.json'),dependencies={str(p.relative_to(R)):sha(p)for p in deps},phase_before=owned,phase_cap=300000000,reserve=50000000,workspace_before=total,global_cap=80000000000,scope='Authored existing beam/pickup/world sound fixtures, with emulated setup writes. Physical APU/MMC5 output assertions; not ordinary acquisition, exact source waveform, final media or complete ISR composition.',main_changed=False)
 (J/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n');groups=[]
 for name in fixtures:
  for mp in ['mmc3','mmc5']:
   rom=H/f'source/build/smb-crossover-{mp}.nes';out=J/(mp+'-'+name)
   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(R/f'tests/{name}.lua'),str(rom),'--timeout','180']
   with(J/(mp+'-'+name+'-host.log')).open('wb')as log:q=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT)
   groups.append(dict(fixture=name,mapper=mp,exit=q.returncode,rom_sha256=sha(rom),files={str(p.relative_to(J)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in out.rglob('*')if p.is_file()}))
   (J/'partial.json').write_text(json.dumps(groups,indent=2)+'\n');print(name,mp,q.returncode,flush=True)
 out=J/'review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_H_EXISTING_NATIVE_AUDIO_FIXTURES'if all(g['exit']==0 for g in groups)else'RETAINED_PRIVATE_H_NATIVE_AUDIO_FAILURES',preparation_sha256=sha(J/'preparation.json'),groups=groups,main_changed=False,ordinary_and_ISR_and_source_fidelity_pending=True,goal_complete=False),indent=2)+'\n');print('REVIEW',sha(out))
if __name__=='__main__':main()
