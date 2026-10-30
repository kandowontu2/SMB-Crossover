"""Freeze metadata-only actual shared Main ingress; no epoch adoption."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
O=R/'build/ff-fx-world-marker-proposal-v2'

def main():
    target=O/'handoff.json';assert not target.exists()
    receipts=[O/n for n in['source-closure.json','marker-controls-v2.json','main-and-isr-controls-v3.json']]
    receipts.append(R/'build/ff-fx-world-marker-reference-v1/source-closure.json')
    files={Path(__file__),R/'tools/audit/ff_fx_world_marker_controls_v3.py',R/'tools/audit/prepare_ff_fx_world_marker_reference_v1.py'}
    for p in receipts:
        d=json.loads(p.read_text());assert d['passed'];files.add(p)
        for f,h in d['bindings'].items():assert B.sha(f)==h,('changed positive binding',f);files.add(Path(f))
    negatives=[O/'main-and-isr-negative-v2.json',R/'build/ff-fx-world-marker-proposal-v1/main-and-isr-negative-v1.json']
    for p in negatives:
        d=json.loads(p.read_text());assert not d['passed'];files.add(p)
        for f,h in d['bindings'].items():assert B.sha(f)==h,('changed negative binding',f);files.add(Path(f))
    readme='''Metadata-only FF world marker on frozen palette-lifecycle v8.

Candidate5c225bb9. The only changes from lifecycle4929545e are130B marker
in C93DF76..<DFF8, the existing11B FF native flash probe, and the already
qualified raw22 graphics datum selecting genuine physicalC93 art. Current
shared-source prototype8062 ancestry is explicit; no installed ROM changed.

The referencef7ea5bd4 is independently source-built with the original native
probe, same corrected graphics selector and same unused marker bytes. This
avoids pretending that an invalid old CFF graphics row can serve as a Main
oracle. Both candidates preserve lifecycle223B+prewriter104B, native public
PCs, header, CHR, original FF code/data and whole RAM3 payload/cookie.

864 object pairs,512 flag pairs and384 foreign pairs pass exact native
outputs and ordered writes except declared ignored attribute bit4 metadata.
Complete mixed fireflower/native-flash objects are tagged iff at least one
visible admitted part usesP1. No body/sword/ink scheduling is installed.

64 genuine Main pairs naturally reach native bank4 / C93. An initial
observer matched the same numeric PC in unrelated bank0; its negative is
retained. Corrected observer uses the genuine linked native bank and retains
all Y1..6, full-state, exact-order, complete-object and C93 assertions.
150 real lag-NMI/IRQ cuts span75 actual busy Main instruction states. Five
normal NMIs occur only after completed Main, not inside partial DrawAll.

Source cost: own leaf+143..351 cycles/object, tested Main+0..587 cycles;
foreign leaf-2..0. No native timing/readiness/palette completion is claimed.
Bit4 is still metadata (ignored by NES hardware); a future epoch compositor
must clear it, preserve body0 and choose exact sword/ink/FX/native palettes.
8 bytes remain in the owned C93 tail. No new lease was used.
'''
    B.write(O/'README.md',readme);files.add(O/'README.md')
    p=dict(passed=True,source_qualified=True,native=False,admitted=False,scheduler=False,metadata_only=True,
        candidate_sha256=B.sha(O/'joint/candidate.nes'),parent_sha256=B.sha(R/'build/ff-fx-palette-lifecycle-v8/joint/candidate.nes'),
        reference_sha256=B.sha(R/'build/ff-fx-world-marker-reference-v1/joint/candidate.nes'),
        own_marker_C93_span=[0xdf76,0xdff8],tail_remaining_bytes=8,
        receipts={str(p.resolve()):B.sha(p)for p in receipts},retained_negatives={str(p.resolve()):B.sha(p)for p in negatives},
        limits=['Metadata-only; authentic FX/sword/ink palettes and epochs remain unimplemented.','No shared adoption, installed ROM change, native run or readiness.'],
        bindings={str(f.resolve()):B.sha(f)for f in sorted(files)})
    B.save(target,p);assert all(B.sha(f)==h for f,h in p['bindings'].items())
    print(json.dumps(dict(path=str(target),sha256=B.sha(target),bindings=len(p['bindings']),ROM=p['candidate_sha256'])),flush=True)

if __name__=='__main__':main()
