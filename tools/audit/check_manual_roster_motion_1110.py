"""Real guest GameCore carrying and native112px strokes for all WWF/FF forms."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_manual_roster_input_1110 as I

P,N,W,R=I.P,I.N,I.W,I.R
OUT=I.OUT
PROOF=OUT/'leaf-proof.json'
SHA=lambda path:sha256(Path(path).read_bytes()).hexdigest()


def scene(b,owner,variant):
    m=P.scene(b,owner)
    if variant:
        N.put(m,FfVariant=variant,FmGroups=variant,DisableScreenFlag=1,
              Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
        N.invoke(m,'InitScreen')
        N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,GameEngineSubroutine=8)
    P.frame(m,0)
    return m


def main():
    cli=argparse.ArgumentParser();cli.add_argument('--owner',type=int,choices=(22,29));a=cli.parse_args()
    q=json.loads(PROOF.read_text())
    assert q['passed'] and not q['native_ingress_pending'] and q['interrupt_pending']
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    raw=I.BASE.read_bytes();assert I.SHA(raw)==I.PIN==q['parent_SHA256']
    candidate=P.install(raw,q['patches']);assert I.SHA(candidate)==q['expected_memory_only_SHA256']
    b=I.bundle(candidate,q['labels'])
    result={};W.D.offset=W.right_offset
    for owner,count in ((22,4),(29,6)):
        if a.owner and owner!=a.owner:continue
        for variant in range(count):
            m=scene(b,owner,variant)
            triangle=W.native_triangle(m,q['labels'])
            vertical=W.D.motion(scene(b,owner,variant),owner,0x28)
            horizontal=W.carrying(scene(b,owner,variant),owner)
            result[f'{owner}:{variant}']=dict(triangle=triangle,vertical=vertical,horizontal=horizontal)
            print('Real guest/native carrying',owner,variant,vertical,horizontal,flush=True)
    receipt=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        expected_memory_only_SHA256=q['expected_memory_only_SHA256'],
        leaf_proof_SHA256=SHA(PROOF),forms=result,
        scope='Real GameCore/native platform boarding and60update carrying plus337native dispatcher updates for initial-right112px triangle. No Mesen/full-stage/IRQ claim.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in (Path(__file__),PROOF,Path(I.__file__),W.SOURCE)})
    (OUT/('motion'+(f'-{a.owner}' if a.owner else '')+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':main()
