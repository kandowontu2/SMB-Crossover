"""Finite actual helper/caller and compiled-IRQ proof of three-byte NOP repair."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json

from check_tmnt_render_oa import load, address, location
from verify_native_relocation import NesMPU
from z2_platform_late_check import Machine

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
FLAGS = [0x20 | (i & 15) | ((i & 16) << 2) | ((i & 32) << 2) for i in range(64)]


def setup(b, entry, shape, flag, character=18, parity=0):
    q = Machine(b)
    q.setup(ident={'empty':6, 'firebar':0x1b, 'lift':0x2b, 'edge':0x2c}[shape],
            active=0 if shape == 'empty' else 1,
            rel=255 if shape == 'edge' else 100, offset=240 if shape == 'edge' else 16,
            rotation=252 if shape == 'edge' else 4)
    for n,v in dict(SelectedCharacter=character, VvVariant=1, OperMode=1,
                    GameEngineSubroutine=8, Player_Y_HighPos=1, Player_Y_Position=176,
                    Player_X_Position=128, PlayerFacingDir=1, PlayerStatus=1,
                    FrameCounter=parity, Mirror_PPUMASK=30, Mirror_PPUCTRL=0xa8,
                    Sprite0HitDetectFlag=1, NmiDisable=255).items():
        q.put(n,v)
    if shape == 'firebar':
        q.put('FirebarPartCount',2)
        for i in range(2):
            q.put('FirebarPartX',100+i*8,i)
            q.put('FirebarPartY',112,i)
    pc = address(b,entry)
    window = (pc-0x8000)//8192
    q.m.page(window,(location(b,entry)-16)//8192)
    if window in [1,2]:
        q.put('CurrentBank' if window == 1 else 'CurrentBankC',q.m.banks[window]|128)
    q.m[0x5204]=128
    c=NesMPU(memory=q.m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=0x55,3,7,flag,0xfd
    c.stPushWord(0x7eff)
    q.m.writes=[]
    return q,c


def regs(c):
    return c.pc,c.a,c.x,c.y,c.p&0xcf,c.sp


def ordinary(m):
    return bytes(m[:0x100])+bytes(m[0x200:0x2000])+bytes(m[0x5c00:0x8000])


def outcome(q,c):
    return regs(c),ordinary(q.m),tuple(q.m.banks),tuple((a,v) for a,v in q.m.writes if not 0x100<=a<0x200)


def run(b,entry,shape,flag,character=18,parity=0,inject=None):
    q,c=setup(b,entry,shape,flag,character,parity)
    trace=[]; done_calls=0; irq=None
    for index in range(100000):
        if c.pc==0x7f00:
            break
        bank=q.m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        trace.append((index,c.pc,bank))
        if bank==4 and c.pc==address(b,'WorldFirebarAdmissionDone'):
            done_calls+=1
        if inject==index:
            before=regs(c),ordinary(q.m),tuple(q.m.banks)
            first=len(q.m.writes)
            assert not c.p&4
            c.irq()
            assert c.pc==0x8000
            minimum=c.sp
            for _ in range(300):
                if c.pc==before[0][0] and c.sp==before[0][-1]:
                    break
                c.step();minimum=min(minimum,c.sp)
            else:
                raise AssertionError(('IRQ return timeout',hex(before[0][0])))
            assert (regs(c),ordinary(q.m),tuple(q.m.banks))==before
            writes=q.m.writes[first:]
            hardware=[(a,v) for a,v in writes if 0x2000<=a<0x6000]
            assert hardware and all(a in [0x2005,0x2006,0x5128,0x5130] for a,v in hardware)
            irq=dict(PC=before[0][0],bank=bank,min_SP=minimum,hardware=hardware)
            # Only the independently checked actual IRQ event log is removed.
            # No RAM, register, SMC, mapper or hardware value is restored.
            del q.m.writes[first:]
        c.step()
    else:
        raise AssertionError(('Caller timeout',entry,shape,hex(c.pc)))
    assert c.sp==0xfd
    return q,c,trace,done_calls,irq


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();out=a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    old,new=load(a.parent),load(a.candidate)
    assert sha(a.parent)=='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
    rows=[]
    for flag,shape in itertools.product(FLAGS,['empty','firebar','lift','edge']):
        left,c,_,dc,_=run(old,'WorldFirebarDrawAdmission',shape,flag)
        right,d,_,dd,_=run(new,'WorldFirebarDrawAdmission',shape,flag)
        assert outcome(left,c)==outcome(right,d),(flag,shape)
        assert dc==dd==1 and d.processorCycles-c.processorCycles==-37
        rows.append(dict(entry='WorldFirebarDrawAdmission',shape=shape,flags=flag,delta=-37))
    for char,parity,shape in itertools.product([0,5,18],[0,1],['empty','firebar','lift']):
        left,c,_,dc,_=run(old,'DrawAllMetasprites',shape,0x69,char,parity)
        right,d,_,dd,_=run(new,'DrawAllMetasprites',shape,0x69,char,parity)
        assert outcome(left,c)==outcome(right,d),(char,parity,shape)
        assert dc==dd==1 and d.processorCycles-c.processorCycles==-37
        rows.append(dict(entry='DrawAllMetasprites',shape=shape,character=char,parity=parity,delta=-37))
    irqs=[]
    for label,b in [('parent',old),('candidate',new)]:
        lo=address(b,'WorldFirebarDrawAdmission');hi=lo+39
        for shape in ['empty','firebar','lift']:
            q,c,trace,dc,_=run(b,'WorldFirebarDrawAdmission',shape,0x20)
            expected=outcome(q,c)
            targets=[(i,pc,bank) for i,pc,bank in trace if bank==4 and lo<=pc<hi]
            for i,pc,bank in targets:
                r,d,_,dd,irq=run(b,'WorldFirebarDrawAdmission',shape,0x20,inject=i)
                assert outcome(r,d)==expected,(label,shape,hex(pc))
                assert dd==dc and irq is not None
                irqs.append(dict(ROM=label,shape=shape,**irq))
    (out/'cases.json').write_text(json.dumps(dict(differentials=rows,IRQ=irqs),indent=2)+'\n',encoding='utf-8')
    proof=dict(passed=True,source_only=True,native_run=False,adopted=False,
               parent_ROM_sha256=sha(a.parent),candidate_ROM_sha256=sha(a.candidate),
               actual_helper_cases=256,actual_DrawAll_callers=18,
               all_physical_flags=64,actual_compiled_IRQ_injections=len(irqs),
               exact_AXYP_SP_ordinary_RAM_SMC_OAM_ordered_writes_and_PRG_banks=True,
               genuine_old_Done_RTS_callback_once_per_call=True,complete_call_cycle_delta=-37,
               cases_sha256=sha(out/'cases.json'),tool_sha256=sha(Path(__file__)),
               limits='Finite arranged CPU helper/complete caller states. Exact ordinary RAM/SMC; only discarded stack omitted. Actual compiled IRQ/vector/RTI is checked at every wrapper instruction boundary, including old NOPs, new JMP, genuine Done and farcall SMC/return instructions. Physical P flags exclude only emulator B/U representation. No PPU, DMA/DMC clocks, native cadence or recovered-draw claim.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(proof,indent=2))


if __name__=='__main__':main()
