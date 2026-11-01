"""Qualify the actual options owning link, loader, Main and resource deltas.

No executable overlay or ROM patch. Equipment stocks are explicit state
fixtures; separate controller-only native routes qualify earned pickup/combat.
"""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_karnov_options_host_component_1101_v8 as Q
import check_karnov_combat_main_1101_v6 as T
import check_karnov_loader_funding_1101_v6 as F
from check_tmnt_render_oa import address,location
J=T.BASE;O=R/'build/karnov-options-native-1101-v8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def owners(b):
    grant=R/'build/karnov-carrier-extension-1101-v7/carrier-grant.json'
    assert sha(grant)=='0d43f5788bc22a1bcee80a91a123e4a1d29f7da22c4fabac116517ba322507aa'
    g=json.loads(grant.read_text());assert g['passed']and g['carrier_granted']
    old=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(old)==g['base_ROM_sha256']==Q.A.PIN
    a=old.read_bytes();raw=b['raw'];assert len(a)==len(raw)
    lo,hi=[location(b,n)for n in ['KrResidentBegin','KrResidentLimit']]
    allowed=[(lo,hi),(1048592+399*1024,1048592+407*1024),
             (1048592+1019*1024,1048592+1023*1024)]
    v=location(b,'KrServiceVeneers');previous=a[v+1]|a[v+2]<<8
    for row in range(37):
        at=v+3*row
        assert a[at]==raw[at]==76 and a[at+1]|a[at+2]<<8==previous
        assert raw[at+1]|raw[at+2]<<8==address(b,'KrDispatch')
        allowed.append((at+1,at+3))
    for name,offset in [('InitScreen',12),('FmResolve::Native',4),('FmStartFlags',4)]:
        at=location(b,name)+offset-1
        assert raw[at]==a[at]==169 and a[at+2:at+15]==raw[at+2:at+15]
        allowed.append((at+1,at+2))
    changed=[i for i,(x,y)in enumerate(zip(a,raw))if x!=y]
    outside=[i for i in changed if not any(l<=i<h for l,h in allowed)]
    assert not outside,('Other owner changed',outside[:20])
    return dict(passed=True,grant_sha256=sha(grant),parent_ROM_sha256=sha(old),
                changed_bytes=len(changed),unchanged_other_owners=True,allowed_intervals=allowed)


def loader(b):
    payload=(J/'kr-options.bin').read_bytes();assert len(payload)==2048
    rows=[]
    for fault in [None,8,9,10,11]:
        m=F.L.make(b,SelectedCharacter=34,FmAlts=1);seen=[]
        def observe(mem,c,i):
            if c.pc==address(b,'KrCopyRow')and mem.rawtags[1]==157:
                row=mem[address(b,'R2')];seen.append(row)
                if row==fault:mem.corrupt_at=(2,{8:0x900,9:0xd00,10:0x1600,11:0x1a00}[row])
        c,low=F.call(m,'KrLoad',observer=observe)
        if fault is None:
            assert c.p&1 and seen==list(range(12))and m.ppu_reads==23064
            assert bytes(m.ram[2][0x1600:0x1e00])==payload
            assert bytes(m.ram[2][0x900:0xe00])==(J/'kr-combat.bin').read_bytes()
            assert bytes(m.ram[3])==(J/'kr-kernel.bin').read_bytes()
            assert m.ram_writes[-2:]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            reads=m.ppu_reads;writes=len(m.ram_writes);warm,_=F.call(m,'KrLoad')
            assert warm.p&1 and reads==m.ppu_reads and writes==len(m.ram_writes)
        else:assert not c.p&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        rows.append(dict(fault_row=fault,rows=seen,success=bool(c.p&1),minimum_SP=low,PPU_reads=m.ppu_reads))
    return dict(passed=True,carrier_cases=rows,cookies=F.header_checks(b,b),
                cold_Main=F.cold_Main_ISR(b,carrier_rows=(0,8,9,10,11)))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--expected',required=True);args=ap.parse_args()
    O.mkdir(exist_ok=True);assert not(O/'binding.json').exists()
    assert sha(J/'candidate.nes')==args.expected
    stage=json.loads((J/'terrain-assembly.json').read_text());assert stage['passed']and stage['options']
    for p,h in stage['bindings'].items():assert sha(p)==h,p
    T.INTEGRATED=True;T.EXPECTED=args.expected;b=T.bundle()
    assert (J/'kr-cookie.bin').read_bytes()[3]==15
    q=dict(passed=False,ROM_sha256=args.expected,no_executable_overlay=True,native_emulator=False,installed=False)
    try:
        q['owners']=owners(b);q['loader']=loader(b)
        Q.model=lambda:(b,dict(actual_owning_link=True,ROM_sha256=args.expected))
        q['equipment_Main']=Q.checks();q['combat_Main']=T.main_checks()
        q['passed']=q['equipment_Main']['passed']and q['combat_Main']['passed']
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['scope']='Actual12-row cold loader, both16-byte cache headers, complete owning link and native Main with IRQ/NMI cuts. Explicit earned-stock fixtures test source Select/Down+B activation,88px boots jump/expiry, boomerang return and flight controls/expiry. Separate native controller routes qualify visible rendering, earned pickups and combat.'
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(Q.__file__),Path(T.__file__),Path(F.__file__),J/'terrain-assembly.json',J/'candidate.nes',J/'candidate.dbg',J/'kr-kernel.bin',J/'kr-options.bin',J/'kr-combat.bin']}
    (O/'options-integrated.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],ROM_sha256=args.expected,error=q.get('error'),equipment_minimum_ISR=q.get('equipment_Main',{}).get('minimum_Main_ISR_SP'),combat_minimum_ISR=q.get('combat_Main',{}).get('minimum_Main_ISR_SP'))))
    assert q['passed'],q.get('error','Options/combat Main')


if __name__=='__main__':main()
