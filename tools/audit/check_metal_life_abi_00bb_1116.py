"""Exact equal-life public ABI/whole-state comparison and four-cycle cost."""
from pathlib import Path
from unittest.mock import patch
import json
import current_metal_life_00bb_1116 as C


def run():
    parent=C.ROM.read_bytes();raw,_=C.Compose.proposal(parent);m,_=C.cold(raw,report=True);N=C.N;base=N.NesMPU;rows=[]
    def reference(t):
        t.bundle=dict(t.bundle,raw=parent);t.ram[2][0x14ad:0x14af]=bytes.fromhex('f039')
        for b in(2,3):t.ram[b][0x1fe0:0x1ff0]=C.Compose.OLD_COOKIE
        for slot,tag in enumerate(t.rawtags):
            if tag&128:t.raw_page(slot,tag)
        return t
    for flags in(0x30,0x31,0x70,0x71,0xb0,0xb1,0x34,0xf5):
        seed=N.fork(m);seed.ram[2][0x5d0]=128;seed.ram[2][0x718]=128
        N.put(seed,FrameCounter=(N.get(seed,'FrameCounter')+1)&255)
        old=reference(N.fork(seed));new=N.fork(seed);results=[];original=[]
        for t in(old,new):
            hits=[]
            class CPU(base):
                def step(self):
                    if self.pc==0xb461 and self.memory.rawtags[1]==3:hits.append(self.sp)
                    return super().step()
            with patch.object(N,'NesMPU',CPU):result=N.invoke(t,'HuMovement',a=85,x=7,y=91,p=flags)
            assert len(hits)==1;results.append(result);original.append(hits)
        for field in('A','X','Y','P','minimum_SP'):assert results[0][field]==results[1][field],(flags,field,results)
        assert results[1]['P']&1 and results[1]['CPU']-results[0]['CPU']==4,(flags,results)
        assert bytes(old[:0x800])==bytes(new[:0x800])and bytes(old[0x5c00:0x8000])==bytes(new[0x5c00:0x8000])
        for bank in range(4):
            excluded=set(range(0x1fe0,0x1ff0))if bank in(2,3)else set()
            if bank==2:excluded|={0x14ad,0x14ae}
            assert all(a==b for i,(a,b)in enumerate(zip(old.ram[bank],new.ram[bank],strict=True))if i not in excluded)
        assert old.rawtags==new.rawtags and old.chr_latches==new.chr_latches
        rows.append(dict(P=flags,parent=results[0],candidate=results[1],actual_original_frame_entries=original,extra_cycles=4))
    return dict(passed=True,ROM_SHA256=C.PIN,actual_HuMovement_equal_life_pairs=rows,
        native_RAM_all_SMC_live_stack_private_and_maps_exact=True,only_declared_code_and_cookies_excluded=True,
        scope='Eight meaningful flag inputs on public HuMovement, original downstream frame executes once in each; component inventory seeds, no natural-item claim',outputs=0,Mesen=False)


if __name__=='__main__':
    def deny(*args,**kw):raise AssertionError('Metal ABI attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run()
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
