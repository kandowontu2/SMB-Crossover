"""Paired parent/candidate retirement-entry failure diagnosis; no game fix."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_body_transition_lifecycle_1115 as Life

C,N,W=Life.C,Life.N,Life.W


def run(parent):
    candidate,_=C.proposal(parent);cases=[]
    for label,raw in(('parent590',parent),('candidate16a',candidate)):
        with patch.object(Life.Candidate.Game,'proof_parent',lambda image:raw if image==raw else (_ for _ in()).throw(AssertionError('Wrong paired cold image'))):
            m,opening=Life.Candidate.Game.cold(raw)
        Life.idle(m,8);N.put(m,SelectedCharacter=0)
        target=0xae0b;b=m.bundle;m[W.address(b,'SafecallA_SMC')+1]=83
        at=W.address(b,'FarcallJmpTarget_SMC');m[at+1]=target&255;m[at+2]=target>>8
        c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=193,71,109,0x21,224;c.stPushWord(0x5aff)
        trace=[];status=None
        for steps in range(4000000):
            if c.pc==0x5b00:status='returned';break
            opcode=bytes(m[c.pc:c.pc+3]);tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            if not opcode[0]:status='BRK';break
            trace.append(dict(PC=c.pc,tag=tag,bytes=opcode.hex(),A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp))
            if len(trace)>24:trace.pop(0)
            c.step()
        else:raise AssertionError('Paired retirement diagnostic bound')
        head,parts,_=C.Packet.extract(raw);meta=parts[1]
        physical=lambda pc:16+65*8192+(pc&8191)
        lows=raw[physical(0xabcb):physical(0xabcb)+4];highs=raw[physical(0xabcf):physical(0xabcf)+4]
        targets=[a+256*b for a,b in zip(lows,highs)]
        cases.append(dict(label=label,ROM_SHA256=C.digest(raw),opening=opening,status=status,steps=steps,
            PC=c.pc,SP=c.sp,maps=m.rawtags[:],actual_opcode=bytes(m[c.pc:c.pc+8]).hex(),last24=trace,
            current_retire_targets=targets,expected_meta_D733=meta[0xd733-0xc800:0xd733-0xc800+8].hex(),
            actual_live_RAM2_D733=bytes(m.ram[2][0xd733&8191:(0xd733&8191)+8]).hex(),
            both_headers=[bytes(m.ram[bank][0x1fe0:0x1ff0]).hex()for bank in(2,3)]))
    q=dict(passed=True,diagnostic_only=True,paired_cases=cases,
        both_same_terminal=(cases[0]['status'],cases[0]['PC'],cases[0]['actual_opcode'])==(cases[1]['status'],cases[1]['PC'],cases[1]['actual_opcode']),
        explicit_selector_component=True,natural_retirement_qualified=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Retirement diagnostic attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
