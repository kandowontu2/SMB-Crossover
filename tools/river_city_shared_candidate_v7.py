"""Preserve Ryan hurt/ceiling negative; cap wall separation to the real step."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 original=R/'build/river_city_shared_v5_build.py';proof=R/'build/river-city-shared-v5-overlay/build-proof.json';d=json.loads(proof.read_text())
 assert next(r['sha256']for r in d['bindings']if Path(r['path'])==original)==sha(original)
 src=original.read_text().replace('river-city-shared-v5','river-city-shared-v7').replace('river_city_wall_prepass.s','river_city_wall_prepass_v2.inc')
 generated=R/'build/river_city_shared_v7_build.py';assert not generated.exists();generated.write_text(src,newline='\n')
 subprocess.run([sys.executable,'-B',str(generated)],cwd=R,check=True)
 p=R/'build/river-city-shared-v7-overlay/build-proof.json';out=json.loads(p.read_text());out['bindings'].append(dict(path=str(Path(__file__).resolve()),sha256=sha(__file__)))
 out['retained_negative']='build/verification/roster-expansion-ryan-hard-shared-v1: source hurt under brick; X2706->2719. Real-step-bound response must reject deep vertical overlap, not weaken world-step assertion.'
 p.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
