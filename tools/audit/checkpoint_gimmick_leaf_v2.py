"""Save the frozen original Gimmick component, excluding ongoing admission work."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from checkpoint_roster_packets_v1 import ROOT,verify


def bind(path):
    path=Path(path).resolve();data=path.read_bytes()
    return dict(path=str(path),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def main():
    hp=ROOT/'build/gimmick-component-v2/handoff.json';h=json.loads(hp.read_text());seen={};verify(h,seen)
    assert bind(hp)['sha256']=='43f8639a7cddb9625cd8e8b6fe9fe65a4f8ad2ecad7080adcfa76b4f50838fae'
    public=[ROOT/name for name in h['owned_publication']]
    assert len(public)==18
    assert not any('admission' in p.name for p in public)
    root=dict(h,original_handoff=bind(hp),owned_files=[bind(p)for p in public+[Path(__file__).resolve()]],
        report=bind(ROOT/'docs/qa/gimmick-component-source-2026-10-29.txt'),
        limits='Source CPU/IRQ/render/component only. Private raw26/menu25 admission is ongoing in a separate successor; no native clear or shared build promotion.')
    target=hp.parent/'root-checkpoint.json';assert not target.exists()
    target.write_text(json.dumps(root,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(target),'--name','gimmick-original-kernel-and-render-component'],cwd=ROOT,check=True)
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(progress.read_text())
    state['Gimmick_compiled_component']=dict(status=root['limits'],handoff=bind(hp),measured_sizes=h['measured_sizes'],
        checkpoint='checkpoints/2026-10-28/gimmick-original-kernel-and-render-component')
    progress.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(public_files=len(public),bindings=len(seen),candidate=h['candidate']['sha256'])))


if __name__=='__main__':main()
