"""First actual compiled Toad movement and mapped-owner diagnostic only."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_smb1_toad_stock_91dc_1116 as Old

if __name__=='__main__':
    raw=Old.ROM.read_bytes();assert Old.digest(raw)==Old.PIN;b=Old.bundle(raw);N,W=Old.N,Old.W
    names=['PlayerMovementSubs','PlayerPhysicsSub','BmMarioMovement','BmNativeMovement','BmNativeVertical','CrossoverVanillaMovement','MarioSourceMovement',
        'MarioSourceBeginPowerup','MarioSourcePowerupUpdate','MarioSourcePowerupCollision']
    names+=sorted(n for n in b['syms']if n.startswith('Bm')and any(s in n.lower()for s in('power','grow','collect','pickup')))
    names=list(dict.fromkeys(n for n in names if n in b['syms']))
    points={};code={}
    for name in names:
        at,pc=W.location(b,name),W.address(b,name);bank=(at-16)//8192
        points.setdefault((bank|128,pc),[]).append(name)
        code[name]=dict(PC=pc,PRGbank=bank,file=at,bytes96=raw[at:at+96].hex())
    hits=Counter();entries=[];returns=[];pending=[];base=N.NesMPU
    def deny(*args,**kw):raise AssertionError('Toad owner diagnosis attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        m=Old.cold(raw,'toad')
        class CPU(base):
            def step(self):
                for q in tuple(pending):
                    if(self.pc,self.sp)==(q['returnPC'],q['returnSP']):returns.append(dict(q,returned=True));pending.remove(q)
                if self.pc>=0x8000:
                    tag=self.memory.rawtags[(self.pc-0x8000)//8192]
                    for name in points.get((tag,self.pc),()):
                        hits[name]+=1
                        if hits[name]==1:
                            c=code[name];assert bytes(self.memory[self.pc:self.pc+64])==raw[c['file']:c['file']+64]
                            sp=self.sp;pc=(self.memory[256+((sp+1)&255)]+256*self.memory[256+((sp+2)&255)]+1)&65535
                            q=dict(name=name,PC=self.pc,SP=sp,PRGbank=tag&127,readback_bytes=64,returnPC=pc,returnSP=(sp+2)&255)
                            entries.append(q);pending.append(q)
                return super().step()
        with patch.object(N,'NesMPU',CPU):
            for tick in range(12):m.controller_pad=0;Old.Frames.frame(m,whole_pass=True)
        ok=bool(hits['PlayerMovementSubs']==hits['BmMarioMovement']==hits['BmNativeMovement']==12 and hits['MarioSourceMovement']==0
            and any(q['name']=='BmNativeMovement'for q in returns))
        q=dict(passed=ok,scope='First actual cold1-1 neutral movement component, not item or full-stage proof',ROM_SHA256=Old.PIN,
            hits=dict(hits),first_entries=entries,first_returns=returns,code=code,
            matching_Bm_symbols=sorted(n for n in b['syms']if n.startswith('Bm')and'::'not in n),
            terminal={name:N.get(m,name)for name in('SelectedCharacter','MarioVariant','PlayerStatus','PlayerSize','X5ChrMode','GameEngineSubroutine','NumberofLives')},
            gameplay_seeds=0,game_bytes_changed=0,outputs=0,Mesen=False)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
    assert q['passed'],'Actual native Toad movement owner not yet authenticated'
