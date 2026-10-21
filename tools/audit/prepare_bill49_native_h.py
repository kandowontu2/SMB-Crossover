"""Bind solid-roof observations to the real native ceiling-stop instruction."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
G = R/'build/verification/root49-bill-native-g'
H = R/'build/verification/root49-bill-native-h'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
info = lambda p: dict(bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
    assert not H.exists()
    freeze=json.loads((G/'freeze.json').read_text())
    assert all(info(G/n)==h for n,h in freeze['files'].items())
    review=G/'positive-m3-a-review.json'
    data=json.loads(review.read_text())
    assert data['status']=='FAIL_UNADMITTED_NATIVE_COVERAGE' and not data['source_projection_mismatches']
    assert len(data['missing_actual_paths'])==6
    binding=json.loads((G/'bindings/positive-m3-a/binding.json').read_text())
    assert binding['hooks']['Head']['label']=='PlayerHeadCollision'
    code=(G/'bind_native.py').read_text()
    old="h=dict(src['hooks']);h['BlockSize']=im.hook('CrossoverBlockSize')"
    assert code.count(old)==1
    code=code.replace(old,old+"\n # Roofs are solidC4: native goes through NYSpd, not block-effects entry.\n h['Head']=im.hook('NYSpd')")
    assert "spec.roof,0xc4" in (G/'native.lua').read_text()
    H.mkdir()
    for n in freeze['files']:
        text=code if n=='bind_native.py' else (G/n).read_text()
        if n.endswith('.py'):compile(text,str(H/n),'exec')
        (H/n).write_text(text)
    files={n:info(H/n)for n in freeze['files']}
    (H/'freeze.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')
    report=dict(status='PREPARED_SOLID_ROOF_HOOK_BINDING_NOT_EXECUTED',script_sha256=sha(__file__),
        prior_negative=dict(path=str(review.relative_to(R)),**info(review)),
        prior_freeze=dict(path=str((G/'freeze.json').relative_to(R)),**info(G/'freeze.json')),
        new_freeze=info(H/'freeze.json'),files=files,
        change='Only the Head observer is rebound from PlayerHeadCollision (interactive-block effects) to NYSpd (the actual solidC4 ceiling stop). Actual physical bank/eight-byte guard remains required.',
        preserved=['All46 arenas, corrected genuine launch/injury placements and readonly corpse telemetry.',
            'All native source/integer/ABI assertions and missing death-publication requirements.',
            'No gameplay edits or new emulated writes.'],
        runtime_changes=False,main_changes=False,route_proof=False)
    (H/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],sha(H/'preparation.json'),flush=True)


if __name__=='__main__':main()
