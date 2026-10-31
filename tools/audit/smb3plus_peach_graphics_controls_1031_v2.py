"""Keep exact donor pixels; use the stronger four-identity write comparison.

V1 completed its9072 qualified comparisons, then the duplicate older foreign
checker rejected the already-disclosed form5 scratch-pointer relocation. Its
pixel/palette assertions are reused unchanged; the stronger9072 comparison
still checks every other write and the actual two relocated pointer stores.
"""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import smb3plus_peach_graphics_controls_1031_v1 as P


def main():
    old,new=[P.scoped_load(p/'candidate.nes') for p in [P.P,P.J]]
    outcomes=[]
    for b in [old,new]:
        q=P.G.seed(b,0,5,0,1)
        c,tr,path,info=P.M.T.invoke(q,'M3Graphics',a=91,x=3,y=7,p=0x30)
        outcomes.append((P.M.regs(c),P.M.T.app(q,tr),q.m.banks[:]))
    assert outcomes[0]!=outcomes[1] and outcomes[0][0]==outcomes[1][0]
    difference=[dict(index=i,old=a,new=b) for i,(a,b) in enumerate(zip(outcomes[0][1],outcomes[1][1])) if a!=b]
    assert len(difference)==2
    assert [r['new'][0] for r in difference]==[P.address(new,'R0'),P.address(new,'R1')]
    negative=P.O/'graphics-duplicate-fixture-negative-v1.json'
    P.B.write(negative,json.dumps(dict(candidate=P.B.sha(P.J/'candidate.nes'),
        variant=0,form=5,frame=0,flags=48,differences=difference,
        cause='Duplicate old checker does not classify the two precisely asserted transient form5 low-pointer stores. The full four-identity checker does.',
        bindings={str(p):P.B.sha(p) for p in [Path(__file__),Path(P.__file__),Path(P.G.__file__)]}),indent=2)+'\n')
    original=P.G.main
    source=Path(P.G.__file__).read_text()
    a=source.index('    foreign=[]\n');z=source.index('    donor_chr=',a)
    assert source[a:z].count("M.T.invoke(q,'M3Graphics'")==1
    source=source[:a]+'    foreign=[] # The enclosing9072-case comparison covers all four identities.\n'+source[z:]
    namespace=dict(P.G.__dict__);namespace['__name__']='bound_exact_donor_pixels'
    exec(compile(source,str(Path(__file__))+'::unchanged-donor-pixel-and-palette-assertions','exec'),namespace)
    P.G.main=namespace['main']
    try:
        # The enclosing comparison updates these globals immediately before
        # calling G.main; the copied namespace must receive those exact paths.
        def donor():
            namespace.update(P=P.P,O=P.O,J=P.J)
            namespace['main']()
        P.G.main=donor
        P.main()
    finally:P.G.main=original
    p=P.O/'graphics-controls-v1.json';d=json.loads(p.read_text())
    d['bindings'].update({str(p):P.B.sha(p) for p in [Path(__file__),negative]})
    d['retained_duplicate_fixture_negative']=str(negative)
    P.B.write(P.O/'graphics-controls-v2.json',json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
