"""Declared component states, not seeded natural-item qualification."""
from pathlib import Path
from unittest.mock import patch
import json
import current_metal_life_00bb_1116 as C


def run():
    parent=C.ROM.read_bytes();raw,composition=C.Compose.proposal(parent);assert C.Compose.inverse(raw)==parent
    m,cold=C.cold(raw,report=True);N=C.N;base=N.NesMPU
    def clone():return N.fork(m)
    def state(t):return dict(armor=t.ram[2][0x5d0],weapon=t.ram[2][0x718],saved=t.ram[2][0x83e],ready=t.ram[2][0x800],life=N.get(t,'NumberofLives'),player=N.get(t,'CurrentPlayer'))
    def frame(t):
        seen=[]
        class CPU(base):
            def step(self):
                tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
                if(tag,self.pc)in((2,0xd4ad),(3,0xb90d),(3,0xb461)):
                    seen.append(dict(bank=tag,PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,state=state(self.memory)))
                return super().step()
        t.controller_pad=0
        with patch.object(N,'NesMPU',CPU):C.Frames.frame(t,whole_pass=True)
        return seen
    cases=[]
    for name,old,new,reset in(('equal',2,2,False),('increase',2,3,False),('decrease',2,1,True),('plus_one_wrap',255,0,False),('minus_one_wrap',0,255,True)):
        t=clone();t.ram[2][0x5d0]=128;t.ram[2][0x718]=128;t.ram[2][0x83e]=old;N.put(t,NumberofLives=new)
        before=state(t);trace=frame(t);after=state(t);ctors=[x for x in trace if x['PC']==0xb90d];original=[x for x in trace if x['PC']==0xb461]
        assert len(ctors)==int(reset)and len(original)==1,(name,trace)
        assert after['saved']==new and(after['armor'],after['weapon'])==((0,0)if reset else(128,128)),(name,before,after)
        cases.append(dict(case=name,before=before,after=after,trace=trace,diagnostic_component_seeds=True,natural_item_claim=False))
    t=clone();t.ram[2][0x5d0]=128;t.ram[2][0x718]=128;N.put(t,NumberofLives=3)
    gain=frame(t);assert state(t)['saved']==3 and state(t)['armor']==128
    N.put(t,NumberofLives=2,GameEngineSubroutine=11);death=frame(t)
    assert not any(x['PC']in(0xb90d,0xb461)for x in death)
    N.put(t,GameEngineSubroutine=8);respawn=frame(t)
    assert sum(x['PC']==0xb90d for x in respawn)==1 and state(t)['saved']==2 and state(t)['armor']==0
    cases.append(dict(case='bonus_then_death_respawn_component',gain=gain,death=death,respawn=respawn,after=state(t),natural_death_claim=False))
    return dict(passed=True,ROM_SHA256=C.PIN,composition=composition,cold=cold,cases=cases,outputs=0,Mesen=False,
        scope='Actual compiled cold and public whole-Main components; life/inventory/engine inputs explicitly diagnostic, no natural-item claim')


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Metal component attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run()
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
