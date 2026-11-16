"""Actual compiled Peach and first returned native movement component only."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_smb1_peach_stock_91dc_1116 as C

if __name__=='__main__':
    raw=C.ROM.read_bytes();assert C.digest(raw)==C.PIN;config=C.bindings(raw);N=C.N
    hits=Counter();first={};returns=[];pending=[];base=N.NesMPU
    tracked=('PlayerMovementSubs','PlayerPhysicsSub','BmMarioMovement','BmNativeMovement','BmNativeVertical',
        'BmFloatVerticalCore','BmFloatSupportCore','MarioSourceMovement')
    points={(config['hooks'][name]['bank']|128,config['hooks'][name]['pc']):name for name in tracked}
    def deny(*args,**kw):raise AssertionError('Peach foundation attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        metadata=C.foundation(raw);m,opening=C.cold(raw,report=True)
        class CPU(base):
            def step(self):
                for q in tuple(pending):
                    if(self.pc,self.sp)==(q['returnPC'],q['returnSP']):returns.append(dict(q,returned=True));pending.remove(q)
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
        assert hits['BmNativeMovement']==44 and hits['MarioSourceMovement']==0
        assert any(q['name']=='BmNativeMovement'for q in returns)
        q=dict(passed=True,metadata=metadata,actual_cold=opening,hits=dict(hits),first=first,returns=returns,
            terminal={n:N.get(m,n)for n in('SelectedCharacter','MarioVariant','BmOwner','PlayerStatus','PlayerSize','X5ChrMode','NumberofLives','BmFloatActive','BmFloatTimer')},
            scope='Real menu/cold/ordinary neutral+A first returned native owner; not natural item/full-stage proof',outputs=0,Mesen=False,gameplay_seeds=0)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
