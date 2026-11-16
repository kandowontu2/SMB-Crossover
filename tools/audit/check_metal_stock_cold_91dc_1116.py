"""Actual Metal cold readback and returned worker component, no item seeds."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_metal_stock_91dc_1116 as C

if __name__=='__main__':
    raw=C.ROM.read_bytes();assert C.digest(raw)==C.PIN
    def deny(*args,**kw):raise AssertionError('Metal source component attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        m,opening=C.cold(raw,report=True);lab=C.labels();base=C.N.NesMPU
        points={(2,lab['Ms12Movement']):'Ms12Movement',(3,lab['MsHostStep']):'MsHostStep',(3,lab['MsNativeConstruct']):'MsNativeConstruct'}
        hits=Counter();returns=Counter();accepted=Counter();first={};pending=[]
        class CPU(base):
            def step(self):
                for q in tuple(pending):
                    if(self.pc,self.sp)==(q['returnPC'],q['returnSP']):
                        returns[q['name']]+=1;accepted[q['name']]+=self.p&1;pending.remove(q)
                        if q['name']not in first:first[q['name']]=dict(q,C=self.p&1)
                if self.pc>=0x8000:
                    tag=self.memory.rawtags[(self.pc-0x8000)//8192];name=points.get((tag,self.pc))
                    if name:
                        hits[name]+=1;sp=self.sp;ret=(self.memory[256+((sp+1)&255)]+256*self.memory[256+((sp+2)&255)]+1)&65535
                        pending.append(dict(name=name,PC=self.pc,SP=sp,bank=tag,returnPC=ret,returnSP=(sp+2)&255))
                return super().step()
        with patch.object(C.N,'NesMPU',CPU):
            for pad,n in((0,12),(128,24),(0,8)):
                for _ in range(n):m.controller_pad=pad;C.Frames.frame(m,whole_pass=True)
        assert not pending and hits['Ms12Movement']>0 and hits['MsHostStep']>0
        assert hits==returns and accepted['Ms12Movement']>0 and accepted['MsHostStep']>0
        q=dict(passed=True,actual_cold=opening,entries=dict(hits),returns=dict(returns),accepted=dict(accepted),first=first,
            terminal={n:C.N.get(m,n)for n in('SelectedCharacter','PlayerStatus','NumberofLives','Player_X_Position','Player_PageLoc','Player_Y_Position','GameEngineSubroutine')},
            source=dict(ready=m.ram[2][0x800],epoch=m.ram[2][0x801],armor=m.ram[2][0x5d0],weapon=m.ram[2][0x718]),
            source_scope='Real compiled cold/headers then44 ordinary completedMain components; no natural item/full-stage claim',outputs=0,Mesen=False,gameplay_seeds=0)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
