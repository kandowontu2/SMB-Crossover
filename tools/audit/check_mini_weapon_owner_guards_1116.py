"""Declared component header/Fresh/Ready/menu guards on owning e32f code."""
from pathlib import Path
from unittest.mock import patch
import json
import current_mini_weapon_owner_1116 as Current
import check_mini_weapon_owner_public_1116 as Public

C,N,W=Current.Compose,Current.N,Current.W

def run(parent):
    raw,_=C.proposal(parent);seed,opening=Current.cold(raw,True);base=N.NesMPU;entries=[];faults=[]
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc in(0xa000,0xa006,0xa066)and m.rawtags[1]==3:entries.append(dict(PC=self.pc,SP=self.sp))
            return super().step()
    for bank in(2,3):
        for index in range(16):
            for slot in(0,2,34):
                t=N.fork(seed);t.ram[bank][0x1fe0+index]^=1
                N.put(t,PlayerStatus=2,A_B_Buttons=64,PreviousA_B_Buttons=0,SavedJoypadBits=64,FrameCounter=(N.get(t,'FrameCounter')+1)&255)
                entries.clear()
                with patch.object(N,'NesMPU',CPU):out=Public.public(t,slot)
                assert not entries and not out['hits'].get('Mini_native_weapon',0),(bank,index,slot,entries,out)
                assert N.get(t,'Fireball_State')==N.get(t,'Fireball_State',1)==0
                faults.append(dict(bank=bank,byte=index,slot=slot,C=out['P']&1,CPU=out['CPU']))
    ready=[]
    for value in(0,1,2):
        a=Public.parent_clone(seed,parent);b=N.fork(seed)
        for t in(a,b):t.ram[2][0x300]=value;N.put(t,FrameCounter=(N.get(t,'FrameCounter')+1)&255)
        left=Public.public(a,0);right=Public.public(b,0)
        assert Public.state(a)==Public.state(b)
        assert all(left[k]==right[k]for k in('A','X','Y','P','SP','minimum_SP'))
        assert right['CPU']-left['CPU']==4*right['hits'].get('Foreign',0)
        ready.append(dict(before=value,after=b.ram[2][0x300],public=right))
    fresh=N.fork(seed);N.put(fresh,Fireball_State=1);fresh[W.address(fresh.bundle,'Fireball_State')+1]=1
    out=Public.public(fresh,15)
    assert N.get(fresh,'Fireball_State')==N.get(fresh,'Fireball_State',1)==0
    assert all(bytes(fresh.ram[b][0x1fe0:0x1ff0])==Current.COOKIE for b in(2,3))
    a=Public.parent_clone(seed,parent);b=N.fork(seed)
    assert 'FmNativePrepare'in b.bundle['syms']
    old=N.invoke(a,'FmNativePrepare');new=N.invoke(b,'FmNativePrepare')
    assert Public.state(a)==Public.state(b)and all(old[k]==new[k]for k in('A','X','Y','P'))
    retired=[bytes(b.ram[k][0x1fe0:0x1ff0]).hex()for k in(2,3)]
    entries.clear();N.put(b,PlayerStatus=2,A_B_Buttons=64,PreviousA_B_Buttons=0,SavedJoypadBits=64)
    with patch.object(N,'NesMPU',CPU):after=Public.public(b,34)
    assert not entries and not after['hits'].get('Mini_native_weapon',0)
    q=dict(passed=True,ROM_SHA256=C.CANDIDATE,actual_cold=opening,header_fault_cases=len(faults),
        header_fault_scope='Every byte of both16B loaded headers; actual compiled movement0/draw2/weapon34, no source vector/native weapon entry',
        faults=faults,Ready_cases=ready,actual_public_Fresh=out,Fresh_clears_both_real_native_states=True,
        actual_FmNativePrepare=dict(parent=old,candidate=new,retired_headers=retired,after_weapon=after),
        primitive_component_seeds=True,natural_stock_claim=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Mini guards attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
