"""Publish the focused-tested WIP and prepare an actual Downloads smoke run."""
from pathlib import Path
import hashlib,json,re
from prepare_selected_native_packet_v1 import prepare
from nightly_patch_guard_v1 import check
R=Path(__file__).resolve().parents[2]
O=R/'build/mario-tank-visible-host-1101-v5'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='7ec9cd5c4a462d0f4638c00ed35bc53a94c05cb80f4699f443245c0f754e3a1f'
BASE='58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rom=O/'candidate.nes'
    assert sha(rom)==PIN and sha(DEST) in (BASE,PIN)
    for n in ['candidate-CPU-controls.json','menu-CPU-controls.json','Main-vector-controls.json','visible-CPU-controls.json','CPU-controls.json']:
        q=json.loads((O/n).read_text());assert q['passed'],n
    g=json.loads((O/'graft-assembly.json').read_text())
    assert len(g['source_owner_intervals'])==18
    assert all(x['formal_grant'] for x in g['source_owner_intervals'])
    for n in ['native-final-smoke','native-powered-final']:
        p=O/n
        q=json.loads((p/'capture/result.json').read_text())
        b=json.loads((p/'capture/binding.json').read_text())
        assert q['passed'] and b['ROM_sha256']==PIN and b['exit_code']==0
        ready=json.loads((p/'ready.json').read_text())
        for f,h in ready['bindings'].items():assert sha(Path(f))==h,f
    check(DEST)
    DEST.write_bytes(rom.read_bytes())
    assert sha(DEST)==PIN
    check(DEST)
    controller=(O/'native-final-smoke/controller.lua').read_text()
    names=set(re.findall(r"\br\('([^']+)'\)",controller))
    labels={m[2]:int(m[1],16) for line in rom.with_suffix('.lbl').read_text().splitlines()
            if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line)) and m[2] in names}
    assert labels.keys()==names
    controller='\n'.join(f'L[{json.dumps(n)}]={v}' for n,v in labels.items())+'\n'+controller
    out=O/'downloads-smoke'
    prepare(out,rom,controller,[Path(__file__),DEST],expected=PIN,timeout=90,
            scope='Actual Downloads launch: cold menu, Select seven times on Mario, Start, 36 walking frames. No RAM writes; no full-stage claim.')
    p=out/'ready.json';q=json.loads(p.read_text());q['ROM']=str(DEST);p.write_text(json.dumps(q,indent=2)+'\n')
    print('Nightly replaced without backup; actual Downloads test prepared.')
if __name__=='__main__':main()

