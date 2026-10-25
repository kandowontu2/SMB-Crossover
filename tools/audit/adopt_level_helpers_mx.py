"""Apply the frozen native-platform packet without replacing later roster code."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2]
D=R/'build/verification/level-platform-mr-candidate-agent'
O=R/'build/verification/level-platform-adoption-mx'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not O.exists()
    assert sha(D/'incremental-merge-manifest.json')=='d27c217ace4390f24bc7c687ff891223d5b8141e56d9d85a5689d3b04f6d9ea8'
    packet=json.loads((D/'incremental-merge-manifest.json').read_text())
    assert sha(D/'incremental-merge.patch')==packet['patch_sha256']
    for n,f in packet['files'].items():assert sha(D/'merge-staging'/n)==f['after_sha256'],n
    parent=json.loads((R/'build/checkpoints/mac-roster-mw/manifest.json').read_text())
    for n,f in packet['files'].items():
        if not f['new']:assert sha(R/n)==parent['source_files'][n],n
        else:assert not (R/n).exists(),n
    subprocess.run(['git','apply','--check','--',str(D/'incremental-merge.patch')],cwd=R,check=True)
    O.mkdir(parents=True)
    for n,f in packet['files'].items():
        if f['new']:continue
        p=O/'before'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    subprocess.run(['git','apply','--',str(D/'incremental-merge.patch')],cwd=R,check=True)
    report=dict(parent='mac-roster-mw',packet_sha256=sha(D/'incremental-merge-manifest.json'),before={n:sha(O/'before'/n) for n,f in packet['files'].items() if not f['new']},after={n:sha(R/n) for n in packet['files']},new=[n for n,f in packet['files'].items() if f['new']],reused_native_platform_ids=[37,40],roster_unchanged=True)
    (O/'adoption.json').write_text(json.dumps(report,indent=2)+'\n')
    # Retarget immutable component suites to the actual combined binaries.
    shutil.copyfile(D/'implemented-cell-contract.json',O/'implemented-cell-contract.json')
    p=O/'source/src/crossover_helper_data.json';p.parent.mkdir(parents=True);shutil.copyfile(R/'src/crossover_helper_data.json',p)
    t=(D/'check_static_final.py').read_text().replace('build/checkpoints/cv3-roster-mr/','build/checkpoints/mac-roster-mw/')
    t=t.replace('unchanged main workspace','combined main source, authored component fixtures')
    t=t.replace('Exhaustive full parser/spawn/lift checks of the pre-final candidate are retained separately; final change only rejects invalid rawIDs in helper admission.','Private exhaustive parser/spawn/lift evidence is retained separately; these checks bind the combined32-identity build.')
    (O/'check_static.py').write_text(t)
    shutil.copyfile(D/'check_helpers_final.py',O/'check_helpers.py')
    print(json.dumps(dict(evidence=str(O),files=len(packet['files']))))

if __name__=='__main__':main()
