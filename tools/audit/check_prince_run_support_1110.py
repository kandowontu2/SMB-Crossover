"""Check typed pipe support through the original standing-to-running transition."""

import argparse
import json
from pathlib import Path
import tempfile

import check_prince_current_support_1110 as Current


R,P,Support = Current.R,Current.P,Current.Support
NEGATIVE = R/'build/prince-current-support-1110/trajectory.json'
BEFORE = ''' lda ActorFrame
 cmp #15
 bne Empty
 lda ActorMode
 cmp #$ff
 bne Empty
'''
AFTER = ''' lda ActorMode
 cmp #1
 beq SupportedMode
 cmp #$ff
 bne Empty
SupportedMode:
'''


def source():
    assert Support.SOURCE.count(BEFORE)==1
    return Support.SOURCE.replace(BEFORE,AFTER)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    result = out/'trajectory.json'
    assert not result.exists()
    negative = Current.read(NEGATIVE)
    assert not negative['passed'] and negative['private_memory_SHA256']==Current.PRINCE_PIN
    baseline = negative['baseline']
    assert baseline['checkpoints']['supported']['x']==179
    records = {r['epoch']:r for r in negative['prototype']['trace']}
    assert (records[239]['action'],records[239]['frame'],records[239]['mode'])==(1,1,1)
    assert (records[239]['x'],records[239]['y'],records[239]['foot'],records[239]['native_state'])==(179,112,145,0)
    assert records[240]['x']==156
    base,cookie,_ = Current.current()
    seed,_ = P.Q.C.C.cold(base,38)
    assert all(bytes(seed.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    with tempfile.TemporaryDirectory(dir=out) as name:
        worker,labels = P.assemble(Path(name),'support',source(),P.one_segment(Support.PROBE,160))
    assert labels['PpD297Support']==Support.PROBE and len(worker)<negative['worker_bytes']
    after = Current.replay(seed,base,worker)
    assert after['checkpoints']['supported']==baseline['checkpoints']['supported']
    assert after['hits'][Support.PROBE]>0
    positive = 'far_ground' in after['checkpoints']
    refs = (Path(__file__),Path(Current.__file__),Path(Support.__file__),NEGATIVE,Current.BASE,Current.SHAFT,Current.NATIVE)
    proof = dict(passed=positive,ROM_written=False,native_run=False,parent_SHA256=Current.BASE_PIN,
                 private_memory_SHA256=Current.PRINCE_PIN,worker_bytes=len(worker),worker_hex=worker.hex(),
                 rejected_v1_at_run_transition=[records[i] for i in (239,240)],
                 replay=after,bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    result.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=positive,bytes=len(worker),checkpoints=after['checkpoints'],last=after['last'])),flush=True)


if __name__=='__main__':
    main()
