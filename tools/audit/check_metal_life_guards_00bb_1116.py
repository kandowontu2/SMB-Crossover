"""Actual public header/Fresh/player boundaries, explicitly component fixtures."""
from pathlib import Path
from unittest.mock import patch
import json
import current_metal_life_00bb_1116 as C


def run():
    raw,_=C.Compose.proposal(C.ROM.read_bytes());m,cold=C.cold(raw,report=True);N=C.N;base=N.NesMPU
    def frame(t,headers=True):
        seen=[]
        class CPU(base):
            def step(self):
                tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
                if(tag,self.pc)in((2,0xd476),(3,0xb461),(3,0xb90d)):
                    if headers:assert all(bytes(self.memory.ram[b][0x1fe0:0x1ff0])==C.COOKIE for b in(2,3))
                    seen.append([tag,self.pc,self.sp])
                return super().step()
        t.controller_pad=0
        with patch.object(N,'NesMPU',CPU):C.Frames.frame(t,whole_pass=True)
        return seen
    faults=[]
    for bank in(2,3):
        for i in range(16):
            t=N.fork(m);t.ram[bank][0x1fe0+i]^=1;t.ram[2][0x5d0]=128;t.ram[2][0x718]=128
            before=bytes(t.ram[2][:0x800]);trace=frame(t)
            assert not trace and bytes(t.ram[2][:0x800])==before,(bank,i,trace)
            faults.append([bank,i])
    fresh=N.fork(m);fresh.ram[2][0x5d0]=128;fresh.ram[2][0x718]=128
    result=N.invoke(fresh,'HuFresh');assert fresh.ram[2][0x800]==0
    assert all(bytes(fresh.ram[b][0x1fe0:0x1ff0])==C.COOKIE for b in(2,3))
    N.put(fresh,NumberofLives=3);fresh_trace=frame(fresh)
    assert sum(x[1]==0xb90d for x in fresh_trace)==1 and fresh.ram[2][0x5d0]==fresh.ram[2][0x718]==0
    owner=N.fork(m);owner.ram[2][0x5d0]=128;owner.ram[2][0x718]=128;N.put(owner,CurrentPlayer=1,NumberofLives=3)
    owner_trace=frame(owner);assert sum(x[1]==0xb90d for x in owner_trace)==1
    assert owner.ram[2][0x83d]==1 and owner.ram[2][0x83e]==3 and owner.ram[2][0x5d0]==owner.ram[2][0x718]==0
    foreign=N.fork(m);N.put(foreign,SelectedCharacter=0,MarioVariant=0,CrossoverMenuIndex=0)
    before=bytes(foreign.ram[2][:0x800]);foreign_trace=frame(foreign)
    assert not foreign_trace and bytes(foreign.ram[2][:0x800])==before
    return dict(passed=True,ROM_SHA256=C.PIN,cold=cold,all_header_byte_rejections=faults,
        actual_HuFresh_result=result,Fresh_then_gain_still_constructs=fresh_trace,changed_player_still_constructs=owner_trace,
        foreign_Mario_no_Metal_entries=True,scope='Component header/player/life mutations declared; actual public HuFresh and whole-Main paths, not natural item/death/menu play',outputs=0,Mesen=False)


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Metal guards attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run()
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
