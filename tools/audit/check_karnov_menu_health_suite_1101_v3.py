"""One bounded exact-candidate health/rebound/scene regression suite."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    expected=sha(O/'candidate.nes')
    jobs=[('check_karnov_health_1101_v2.py',['--integrated','--output',str(O/'health-CPU-controls.json')],'health-CPU-controls.json'),
        ('check_karnov_rebound_1101_v2.py',[],'rebound-CPU-controls.json'),
        ('check_karnov_life_restart_1101_v3.py',[],'life-restart-CPU-controls.json'),
        ('check_karnov_terrain_host_1101_v1.py',[],'terrain-CPU-controls.json'),
        ('check_karnov_terrain_vectors_1101_v1.py',[],'terrain-vectors.json'),
        ('check_karnov_scene_1101_v1.py',[],'scene-CPU-controls.json')]
    receipts={}
    for name,args,receipt in jobs:
        subprocess.run([sys.executable,str(R/'tools/audit'/name),*args],check=True,cwd=R)
        path=O/receipt;q=json.loads(path.read_text());assert q['passed']and q['ROM_sha256']==expected
        for p,h in q['bindings'].items():assert sha(p)==h,p
        receipts[receipt]=sha(path)
    assert sha(O/'candidate.nes')==expected
    result=dict(passed=True,ROM_sha256=expected,source_CPU=True,native_emulator=False,installed=False,receipts=receipts,bindings={str(Path(__file__).resolve()):sha(__file__)})
    (O/'menu-health-suite.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
