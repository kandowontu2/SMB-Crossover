"""All-flag public transport ABI on the genuinely loaded Bowser image."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import traceback

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import bowser_split_loader_controls_v1 as T
H=T.H
O,J=T.O,T.J
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=O/'public-ABI-controls.json'
    assert not out.exists()
    q=dict(passed=False,native=False,no_menu_or_gameplay_ingress=True)
    try:
        b=H.C.qualified(J/'candidate.nes')
        seed=T.make(b)
        c,_=T.call(seed,'BwLoad')
        assert c.p&1
        cases=[]
        for valid,slot,f in itertools.product([0,1],range(37),range(64)):
            m=T.fork(seed)
            if not valid:m.ram[3][0x1fe0]=0
            before=bytes(m[:0x8000]);ram=[bytes(x)for x in m.ram]
            c,low=T.call(m,'BwServiceVeneers',slot=slot,p=T.flags(f))
            assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
            assert c.p&0xcf==T.flags(f)&0x4c
            assert bytes(m[:0x100])==before[:0x100]
            assert bytes(m[0x5c00:0x8000])==before[0x5c00:0x8000]
            assert [bytes(x)for x in m.ram]==ram
            assert m.rawtags==seed.rawtags
            cases.append([valid,slot,f,c.processorCycles,low])
        warm=[];reject=[];retire=[]
        for f in range(64):
            m=T.fork(seed);before=[bytes(x)for x in m.ram];reads=m.ppu_reads
            c,low=T.call(m,'BwLoad',p=T.flags(f))
            assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
            assert c.p&0xcf==(T.flags(f)&0x4c)|1
            assert [bytes(x)for x in m.ram]==before and m.ppu_reads==reads
            warm.append([f,c.processorCycles,low])
            m=T.fork(seed);H.put(m,FamilyMainCommit=0)
            before=[bytes(x)for x in m.ram];reads=m.ppu_reads
            c,low=T.call(m,'BwLoad',p=T.flags(f))
            assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
            assert c.p&0xcf==T.flags(f)&0x4c
            assert [bytes(x)for x in m.ram]==before and m.ppu_reads==reads
            reject.append([f,c.processorCycles,low])
            for family in [0,9,22,27,32,33]:
                m=T.fork(seed);m.ram[3][0x1fe1]=family
                old=[bytes(x)for x in m.ram]
                c,low=T.call(m,'BwRetire',p=T.flags(f))
                assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
                assert c.p&0xcf==T.flags(f)&0x4d
                assert m.ram[3][0x1fe0]==(0 if family==27 else 167)
                expected=bytearray(old[3]);expected[0x1fe0]=0 if family==27 else 167
                assert [bytes(x)for x in m.ram[:3]]==old[:3] and m.ram[3]==expected
                assert m.rawtags==seed.rawtags
                retire.append([f,family,c.processorCycles,low])
        q.update(passed=True,typed_valid_invalid_37rows_all64flags=len(cases),
                 warm_allflags=len(warm),busy_rejection_allflags=len(reject),
                 retirement_allflags_families=len(retire),rows=cases,warm=warm,
                 rejected=reject,retirement=retire,all_R01_R67_ZP_WRAM_maps_exact=True,
                 ABI='Public SFC calls retain A/X/Y/SP/VDI, impose NZ from restored A as genuine SFC does; Check/Load/row result only changes C, Retire preserves C.',
                 limits='All36 loaded services deliberately decline; no world/render/item/enemy/physics or admission claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(T.__file__),
        O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin',J/'bowser/cookie.bin']}
    out.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings','rows','warm','rejected','retirement','traceback']}))
    assert q['passed'],q.get('error')


if __name__=='__main__':main()
