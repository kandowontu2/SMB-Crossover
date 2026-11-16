"""Actual public header/lifecycle components and paired compiled family cold."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import argparse,json
import current_sonic_hidden_heads_f7c9_1116 as F
from check_sonic_hidden_reached_irq_f7c9_1116 import slim


def private(m,candidate):
    rows=[bytearray(v)for v in m.ram]
    if candidate:
        assert rows[3][0x1b26:0x1b39]==F.C.NEW and rows[2][0x1344:0x1371]==F.C.HELPER
        rows[3][0x1b26:0x1b39]=F.C.OLD;rows[2][0x1344:0x1371]=b'\xff'*45
        for k in(2,3):
            for i,(a,b)in enumerate(zip(F.C.OLD_COOKIE,F.COOKIE,strict=True)):rows[k][0x1fe0+i]^=a^b
    return list(map(bytes,rows))


def parentize(seed,parent):
    m=slim(seed);m.bundle=dict(m.bundle,raw=parent)
    m.ram[3][0x1b26:0x1b39]=F.C.OLD;m.ram[2][0x1344:0x1371]=b'\xff'*45
    for k in(2,3):m.ram[k][0x1fe0:0x1ff0]=F.C.OLD_COOKIE
    for win,t in enumerate(m.rawtags):
        if t&128:m.raw_page(win,t)
    return m


def same(a,b,own=False):
    assert private(a,False)==private(b,True)if own else[bytes(v)for v in a.ram]==[bytes(v)for v in b.ram]
    assert bytes(a[:0x800])==bytes(b[:0x800])and bytes(a[0x6000:0x8000])==bytes(b[0x6000:0x8000])
    assert a.rawtags==b.rawtags and a.chr_latches==b.chr_latches and a.protection==b.protection and a.vram==b.vram


def guards(raw):
    q=F.bindings(raw);N=F.N;parent=F.C.inverse(raw);seed,cold=F.cold(raw,'sonic')
    for _ in range(4):seed.controller_pad=0;F.Frames.frame(seed,whole_pass=True)
    counts=Counter();row=[];active=[None];base=N.NesMPU
    class CPU(base):
        def step(self):
            m=self.memory;t=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(t,self.pc)==(2,0xd344)and m.bundle['raw']is raw:
                assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(F.COOKIE,)*2,'Full public headers dominate helper'
                counts[active[0]]+=1
            return super().step()
    cases=[('positive',None,None)]
    cases += [('header%d_%d'%(k,i),('header',k,i),None)for k in(2,3)for i in range(16)]
    cases += [('Ready0',None,dict(ready=0)),('epoch255',None,dict(frame=255)),('paused',None,dict(pause=1)),
              ('death_engine_component',None,dict(engine=11)),('area_reentry_component',None,dict(ready=0,level=1))]
    for name,fault,change in cases:
        a=parentize(seed,parent);b=slim(seed);active[0]=name
        for m in(a,b):
            if fault is not None:_,k,i=fault;m.ram[k][0x1fe0+i]^=1
            if change:
                if 'ready'in change:m.ram[2][0x119]=change['ready']
                for key,native in(('frame','FrameCounter'),('pause','GamePauseStatus'),('engine','GameEngineSubroutine'),('level','LevelNumber')):
                    if key in change:N.put(m,**{native:change[key]})
        with patch.object(N,'NesMPU',CPU):
            for _ in range(2):
                for m in(a,b):m.controller_pad=0;F.Frames.frame(m,whole_pass=True)
        same(a,b,True)
        row.append(dict(name=name,helper_entries=counts[name],ready=b.ram[2][0x119],pause=N.get(b,'GamePauseStatus'),engine=N.get(b,'GameEngineSubroutine')))
    assert counts['positive']>0 and all(counts[n]==0 for n,_,_ in cases if n.startswith('header'))
    out=dict(passed=True,ROM_SHA256=F.PIN,cold=cold,cases=row,exact_owned_runtime_normalization='Only declared selector19/helper45 and the exact old/new16-cookie XOR in two resident header views; every other private/native/SMC/live byte, maps/CHR/VRAM compared.',
        source_SHA256=F.H(Path(__file__).read_bytes()),scope='Actual complete public Main; explicit header/Ready/epoch/pause/death/area components, not seeded natural events or actual fullstage.',outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


def foreign(raw):
    q=F.bindings(raw);N,W=F.N,F.W;parent=F.C.inverse(raw);rows=[];entries=Counter();base=N.NesMPU
    def cold(image,select):
        b=dict(q['bundle'],raw=image)
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        for v in(4,4,4,1):W.UI.key(m,v)
        for _ in range(select):W.UI.key(m,32)
        label=W.UI.menu_name(m)[0];assert label==('MR GIMMICK','BUB','BOB')[select]
        start=W.UI.key(m,16);N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P']);N.invoke(m,'PauseRoutine',a=0)
        for epoch in range(700):
            if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;F.Frames.frame(m,cold=True,whole_pass=True)
        else:raise AssertionError('Genuine shared-family cold bound')
        return m,dict(name=label,Select=select,raw=N.get(m,'SelectedCharacter'),FmAlts=m[0x5ffe],cold_steps=epoch)
    class CPU(base):
        def step(self):
            m=self.memory;t=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(t,self.pc)==(2,0xd344)and bytes(m[self.pc:self.pc+45])==F.C.HELPER:entries['new_helper']+=1
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        for select in range(3):
            a,old=cold(parent,select);b,new=cold(raw,select);assert old==new;same(a,b)
            for _ in range(16):
                for m in(a,b):m.controller_pad=0;F.Frames.frame(m,whole_pass=True)
            same(a,b);rows.append(dict(identity=new,neutral_public_Main=16,all_native_private_SMC_maps_CHR_VRAM_exact=True))
    assert not entries['new_helper']
    out=dict(passed=True,ROM_SHA256=F.PIN,source_SHA256=F.H(Path(__file__).read_bytes()),compiled_family_pairs=rows,
        new_helper_entries=0,no_foreign_state_mask=True,natural_cold_and16neutral_only=True,outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--foreign',action='store_true');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Source guard/foreign test attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=(foreign if a.foreign else guards)(F.load_current_image())
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
