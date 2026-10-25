"""Adopt only the independently verified Rygar graphics repair."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=R/'build/verification/rygar-walk-k4';S=O/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    out=O/'adoption-ka.json';assert not out.exists()
    manifest=json.loads((O/'manifest.json').read_text());receipt=json.loads((O/'pixel-check-k7/summary.json').read_text())
    assert receipt['status']=='PASS_ORIGINAL_NATIVE_WALK_PIXELS_BOTH_FACINGS_ALL_POWERS'
    names=tuple(manifest['outputs'])
    for n in names:
        assert sha(S/n)==manifest['outputs'][n]
        assert sha(R/n)==manifest['source_before'][n],('Main changed since private candidate',n)
    for mapper in ('mmc3','mmc5'):
        for name in ('walk','rygar-controls','rygar-attacks','bill-flare-limit-202'):
            folder=O/(f'repaired-k8-walk-{mapper}'if name=='walk'else f'repaired-k9-{name}-{mapper}')
            logs=list(folder.glob('*.log'));assert len(logs)==1
            log=logs[0].read_text();assert'PASS 'in log and'FAIL 'not in log
    for n in names:shutil.copyfile(S/n,R/n)
    meta=R/'docs/reference/expanded-assets.json';data=json.loads(meta.read_text())
    data['RYGAR']['maximum_sprites']=6
    data['RYGAR']['native_walk_oam_slots']=[2,3,4,5,6,7]
    data['RYGAR']['native_walk_frames_right']=[302,309,316]
    data['RYGAR']['native_walk_frames_left']=[432,440,447]
    meta.write_text(json.dumps(data,indent=2)+'\n')
    out.write_text(json.dumps(dict(adopted=True,source_hashes={n:sha(R/n)for n in names},proof_sha256=sha(O/'pixel-check-k7/summary.json'),pending_main_rebuild=True,scope='Rygar complete native walk artwork only; no levels or expanded roster enabled.'),indent=2)+'\n')
    print('Adopted4 verified Rygar art inputs; rebuild pending')
if __name__=='__main__':main()
