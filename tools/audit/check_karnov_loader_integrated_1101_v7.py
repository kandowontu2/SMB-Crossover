"""Final owning-link cold-loader faults, cookie gates and actual Main ISR."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_karnov_loader_funding_1101_v6 as F
import check_karnov_combat_integrated_1101_v7 as I
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    I.T.INTEGRATED=True;I.T.EXPECTED=I.EXPECTED;b=I.T.bundle()
    rows=[];payload=(I.T.BASE/'kr-combat.bin').read_bytes();assert len(payload)==1280
    for fault in [None,8,9]:
        m=F.L.make(b,SelectedCharacter=34,FmAlts=1);seen=[]
        def observe(mem,c,i):
            if c.pc==F.address(b,'KrCopyRow')and mem.rawtags[1]==157:
                row=mem[F.address(b,'R2')];seen.append(row)
                if row==fault:mem.corrupt_at=(2,0x900 if row==8 else 0xd00)
        c,low=F.call(m,'KrLoad',observer=observe)
        if fault is None:
            assert c.p&1 and seen==list(range(10))and m.ppu_reads==18964
            assert bytes(m.ram[2][0x900:0xe00])==payload
            assert bytes(m.ram[3])==(I.T.BASE/'kr-kernel.bin').read_bytes()
            assert m.ram_writes[-2:]==[(3,0x1fe0,167),(2,0x1fe0,167)]
            nr=m.ppu_reads;nw=len(m.ram_writes);warm,_=F.call(m,'KrLoad')
            assert warm.p&1 and nr==m.ppu_reads and nw==len(m.ram_writes)
        else:assert not c.p&1 and m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
        rows.append(dict(fault_row=fault,rows=seen,success=bool(c.p&1),minimum_SP=low,PPU_reads=m.ppu_reads))
    q=dict(passed=True,ROM_sha256=I.EXPECTED,no_executable_overlay=True,
           carrier_cases=rows,cookies=F.header_checks(b,b),cold_Main=F.cold_Main_ISR(b),
           bindings={str(p.resolve()):sha(p)for p in [Path(__file__),Path(F.__file__),I.T.BASE/'candidate.nes',I.T.BASE/'candidate.dbg',I.T.BASE/'kr-combat.bin']})
    (I.O/'loader-final.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ROM_sha256=I.EXPECTED,carrier_cases=rows,cookie_cases=q['cookies'],cold_Main={k:v for k,v in q['cold_Main'].items()if k!='interrupts'})))


if __name__=='__main__':main()
