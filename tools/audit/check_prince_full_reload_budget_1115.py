"""Current full route with the existing cold budget only after real decode."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_full_fresh_current_1115 as CurrentCheck

B=CurrentCheck.Base
Frames,N,W=B.Candidate.Frames,B.N,B.Candidate.W


def run(raw):
    current=CurrentCheck.Current.normalize(raw,kind='prince-current-gimmick-7a80')
    head,_,_=B.C.Packet.extract(raw)
    expected=head[B.C.Packet.LOADER-254:B.C.Packet.LOADER]
    assert len(expected)==254 and expected[:3]==bytes.fromhex('a20020')
    # Only these original decoder instruction operands self-modify. All
    # bytes before BitsLeft are otherwise required to equal owning ROM.
    mutable={0x6f,0x70,0xaa,0xab,0xc9,0xca}
    stats=dict(Main_calls=0,ordinary_max_instructions=0,cold_mains=[],
        decoder_SHA256=sha256(expected).hexdigest(),immutable_decoder_bytes=0xe6-len(mutable),
        opcode_operand_exceptions=sorted(mutable),normal_budget=500000,existing_cold_budget=4000000)
    def frame(m,observe=None,*,cold=False,whole_pass=False):
        assert not cold,'This successor grants cold time only to authenticated reached decoder entry'
        stats['Main_calls']+=1
        idle=W.address(m.bundle,'IdleLoop');W.clear_logs(m);N.consume(m)
        c=N.NesMPU(memory=m,pc=idle);c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
        entries=[]
        for instruction in range(4000000):
            stop=(idle,253)if whole_pass else(idle+12,252)
            if c.processorCycles and(c.pc,c.sp)==stop:
                assert not m.blocked
                if entries:
                    stats['cold_mains'].append(dict(Main=stats['Main_calls'],instructions=instruction,
                        cycles=c.processorCycles,entries=entries,returned_same_Main=True))
                else:stats['ordinary_max_instructions']=max(stats['ordinary_max_instructions'],instruction)
                return c.processorCycles
            if c.pc==0xc000 and m.rawtags[2]==2:
                assert c.p&4,'Actual Prince cold decoder must retain SEI'
                assert N.get(m,'DisableScreenFlag')and not N.get(m,'Mirror_PPUMASK')&0x18
                assert N.get(m,'NmiDisable')&0x80
                assert m.ram[2][0x1fe0]==0 and m.ram[3][0x1fe0]==0,'Both previous headers retired before actual reload'
                actual=m.ram[2][:0xe6]
                assert all(a==b for i,(a,b)in enumerate(zip(actual,expected))if i not in mutable),'Actual owning immutable decoder code differs'
                entries.append(dict(PC=c.pc,SP=c.sp,P=c.p,instruction=instruction,
                    map=list(m.rawtags),code_exact=True,both_headers_invalid=True,forcedblank=True))
                assert len(entries)<=3,'Exactly three authenticated Prince cold streams per Main maximum'
            if instruction==500000 and not entries:
                raise AssertionError(('Ordinary Main bound, no authenticated cold ingress',hex(c.pc),c.sp,list(m.rawtags)))
            if observe:observe(m,c)
            assert m[c.pc],('BRK',hex(c.pc),m.rawtags)
            c.step()
        raise AssertionError(('Reached cold Main exceeded original4M budget',hex(c.pc),c.sp,entries))
    with patch.object(Frames,'frame',frame):q=CurrentCheck.run(raw,full=True)
    q['actual_reached_cold_budget']=stats
    q['reload_budget_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Current full reload source gate attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not q['passed']:raise SystemExit(1)
