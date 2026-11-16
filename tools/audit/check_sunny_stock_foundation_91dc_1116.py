"""Actual compiled Sunny cold and first returned movement owner, zero outputs."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_sunny_stock_91dc_1116 as C

if __name__=='__main__':
    raw=C.ROM.read_bytes();assert C.digest(raw)==C.PIN;config=C.bindings(raw);N=C.N
    tracked=('PlayerMovementSubs','PlayerPhysicsSub','CrossoverVanillaMovement','BmNativeMovement','MarioSourceMovement','SunnyNativeMovement')
    points={(config['hooks'][n]['bank']|128,config['hooks'][n]['pc']):n for n in tracked}
    hits=Counter();first={};returned=[];pending=[];base=N.NesMPU
    def deny(*args,**kw):raise AssertionError('Sunny foundation attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        metadata=C.foundation(raw);m,opening=C.cold(raw,report=True)
        class CPU(base):
            def step(self):
                for q in tuple(pending):
                    if(self.pc,self.sp)==(q['returnPC'],q['returnSP']):returned.append(dict(q,returned=True));pending.remove(q)
                if self.pc>=0x8000:
                    tag=self.memory.rawtags[(self.pc-0x8000)//8192];name=points.get((tag,self.pc))
                    if name:
                        hits[name]+=1
                        if name not in first:
                            h=config['hooks'][name];at=16+h['offset'];assert bytes(self.memory[self.pc:self.pc+64])==raw[at:at+64]
                            sp=self.sp;ret=(self.memory[256+((sp+1)&255)]+256*self.memory[256+((sp+2)&255)]+1)&65535
                            q=dict(name=name,PC=self.pc,SP=sp,PRGbank=tag&127,readback_bytes=64,returnPC=ret,returnSP=(sp+2)&255)
                            first[name]=q;pending.append(q)
                return super().step()
        with patch.object(N,'NesMPU',CPU):
            for pad,n in((0,12),(128,24),(0,8)):
                for _ in range(n):m.controller_pad=pad;C.Frames.frame(m,whole_pass=True)
        assert hits['SunnyNativeMovement']==44 and hits['CrossoverVanillaMovement']==44 and hits['MarioSourceMovement']==0
        assert any(q['name']=='SunnyNativeMovement'for q in returned)
        q=dict(passed=True,metadata=metadata,actual_cold=opening,hits=dict(hits),first=first,returned=returned,
            terminal={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','PlayerStatus','PlayerSize','X5ChrMode','SunnyReady','SunnyForm','SunnyLife','NumberofLives')},
            scope='Current compiled Sunny/actual returned owner component; no item or full-stage claim',outputs=0,Mesen=False,gameplay_seeds=0)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
