"""Rebind the qualified dual native helper rows to the delivered Getsu line."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import check_manual_dual_platform_1110 as D

R=D.R
BASE=R/'build/getsu-fast-head-native-1110/candidate.nes'
PIN='66a7b9325d90efb7751387e0c1c95a756fde57d92f13d6180178ade3e535090c'
OUT=D.OUT


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    assert a.output.resolve()==OUT
    proof_path,irq_path=OUT/'proof.json',OUT/'irq.json'
    proof=json.loads(proof_path.read_text())
    irq=json.loads(irq_path.read_text())
    assert proof['passed'] and irq['passed']
    assert irq['foreground_proof_SHA256']==sha(proof_path)
    assert irq['expected_memory_only_SHA256']==proof['expected_memory_only_SHA256']
    for name,digest in proof['bindings'].items():
        assert sha(R/name)==digest,name
    old=D.BASE.read_bytes()
    current=BASE.read_bytes()
    assert sha256(old).hexdigest()==proof['parent_SHA256']==D.PIN
    assert sha256(current).hexdigest()==PIN
    rows=proof['patches']
    slots=set()
    for row in rows:
        at=row['file_offset'];pre=bytes.fromhex(row['old_hex'])
        assert current[at:at+len(pre)]==old[at:at+len(pre)]==pre
        assert not slots.intersection(range(at,at+len(pre)))
        slots.update(range(at,at+len(pre)))
    upstream=[i for i,(x,y) in enumerate(zip(old,current)) if x!=y]
    assert not slots.intersection(upstream)
    trial=D.P.install(current,rows)
    assert all(a==b for i,(a,b) in enumerate(zip(current,trial)) if i not in slots)
    before,after=D.P.bundles(current,trial)
    regular={owner:D.P.regular_parity([D.P.scene(before,owner),D.P.scene(after,owner)],owner,current,trial)
             for owner in (0,5,25,34,41,42)}
    owner={}
    for raw in (41,34):
        seed=D.P.scene(after,raw)
        owner[raw]={'controls':D.controls(seed,raw,proof['labels']),
                    'horizontal':D.motion(seed,raw,0x24),'vertical':D.motion(seed,raw,0x28)}
    refs={Path(__file__).resolve(),BASE,proof_path,irq_path}
    bindings=proof['bindings']|{p.relative_to(R).as_posix():sha(p) for p in refs}
    result=proof|dict(parent_SHA256=PIN,expected_memory_only_SHA256=sha256(trial).hexdigest(),
        original_source_parent_SHA256=D.PIN,ROM_written=False,Mesen_run=False,
        upstream_changes=len(upstream),upstream_disjoint=True,foreign_and_owner_CPU=regular,
        current_owner_CPU=owner,bindings=bindings,
        interrupt_reuse=dict(source_irq=irq_path.relative_to(R).as_posix(),source_irq_SHA256=sha(irq_path),
            reason='All changed helper/Mini/Karnov instruction bytes and loaded Mini/Karnov payloads identical to qualified095c pair; Getsu-only991/992/cookie/head paths are disjoint. Native actual current-lineage replays remain required.'))
    (OUT/'rebase-proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,expected_memory_only_SHA256=result['expected_memory_only_SHA256'],
                         patch_count=len(rows),upstream_changes=len(upstream),regular=regular)),flush=True)


if __name__=='__main__':main()
