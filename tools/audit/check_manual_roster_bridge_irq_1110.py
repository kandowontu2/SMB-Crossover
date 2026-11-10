"""Paired genuine ISR cuts for the new same3B fixed bridge predicate."""
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_manual_roster_bridge_mask_1110 as M

V,F,I,P,N,R=M.V,M.F,M.I,M.P,M.N,M.R
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()


def main():
    proof=I.OUT/'bridge-mask-proof.json';q=json.loads(proof.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    sourceproof=json.loads(M.PROOF.read_text());labels=sourceproof['labels']
    old=M.CURRENT.read_bytes();new=P.install(old,q['patches'])
    assert I.SHA(old)==q['current_roster_parent_SHA256']
    assert I.SHA(new)==q['current_roster_mask_SHA256']
    V.BASELINE=(R/'build/remaining-roster-native-1110/candidate.nes').read_bytes()
    assert I.SHA(V.BASELINE)=='d1333adf3d9e62354ccfab9c21490f95bc972200c513183a309d90eed09728d8'
    original=V.pair_source
    def predicate_source(source):
        source=original(source)
        start=source.index('                inside = (tag == 154')
        end=source.index('\n                key = tag,pc,q.sp,q.p&4',start)
        source=source[:start]+'                inside = (tag == 254 and 0x837b <= pc < 0x839a)'+source[end:]
        source=P.replace_one(source,"assert bool(owned(m)) == (scenario != 'full')",'assert not owned(m)')
        return source
    V.pair_source=predicate_source
    identities=((0,0),(5,0),(41,0),(22,0),(29,0),(34,0),(2,0),(32,0))
    try:result=V.vectors(F.bundle(new,labels),labels,0,identities,('predicate',))
    finally:V.pair_source=original
    print('Mask genuine paired predicate IRQ',result,flush=True)
    receipt=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        expected_memory_only_SHA256=q['current_roster_mask_SHA256'],vectors=result,
        paired_baseline_callbacks=dict(V.PAIRED),
        audio_capsule_bank1_offsets=sorted(V.AUDIO_OFFSETS),
        native_commit_acknowledgments={str(k):v for k,v in V.COMMIT_TRANSITIONS.items()},
        whole_frozen70_worker_bytes_unchanged=True,
        scope='New fixed31B bridge only, every reached instruction includingAND12/BEQ0F. GenuineIdleLoop/GameLoop/CoreSP, exact paired d133 baseline ISR CPU/RAM/hardware and full foreground resumes. Owners native0/5,Mini41,desired22/29/34,newlyadmitted2,newlyrejected32. Existing70all10V/H/carry IRQ proofs retain identical worker instruction bytes.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in
            (Path(__file__),Path(M.__file__),proof,Path(V.__file__),V.PROOF)})
    (I.OUT/'bridge-mask-irq.json').write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
