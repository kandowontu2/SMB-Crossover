"""Install the bounded legacy outline flag getter within its original span."""
from pathlib import Path
import hashlib,json,shutil,subprocess
R=Path(__file__).resolve().parents[2];D=R/'build/verification/expanded-controls-agent/raw-id-audit';O=R/'build/verification/outline-adoption-my'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    assert sha(D/'manifest.json')=='06a51db4799e2b30690fa3769b0a3d64d4143f582a00a837764fd6a1381a261f'
    packet=json.loads((D/'manifest.json').read_text())
    for f in packet['files']:assert sha(D/f['path'])==f['sha256'],f['path']
    parent=json.loads((R/'build/checkpoints/level-roster-mx/manifest.json').read_text())
    for n in packet['changed_sources']:assert sha(R/n)==parent['source_files'][n],n
    subprocess.run(['git','apply','--check','--',str(D/'outline-fix.patch')],cwd=R,check=True)
    O.mkdir(parents=True)
    for n in packet['changed_sources']:
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    subprocess.run(['git','apply','--',str(D/'outline-fix.patch')],cwd=R,check=True)
    (O/'adoption.json').write_text(json.dumps(dict(parent='level-roster-mx',packet_sha256=sha(D/'manifest.json'),before={n:sha(O/'before'/n) for n in packet['changed_sources']},after={n:sha(R/n) for n in packet['changed_sources']},resident_growth=0,helper_bytes=17),indent=2)+'\n')
    print('Adopted bounded17B outline getter in original26B resident span')

if __name__=='__main__':main()
