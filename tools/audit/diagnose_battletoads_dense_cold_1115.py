"""Truthful actual CPU/mapping trace of failed5b28 cold, no opcode changes."""
from collections import deque
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import compose_battletoads_dense_current_1115 as C
import battletoads_dense_current_model_1115 as Model

W,N,Old=Model.W,Model.N,Model.Previous


def trace(raw,kind):
    base=N.NesMPU;ring=deque(maxlen=32);far=deque(maxlen=24);queries=[];pads=[];ctx=dict(cpu=None,m=None,pad=0)
    key=W.UI.key;lookups=[]
    class CPU(base):
        def step(self):
            m=self.memory
            if m.bundle['raw']is raw:
                ctx.update(cpu=self,m=m)
                pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                row=dict(PC=pc,tag=tag,A=self.a,X=self.x,Y=self.y,P=self.p,SP=self.sp,
                    opcode=bytes(m[pc+i]for i in range(3)).hex(),stack_next8=bytes(m[0x101+self.sp: min(0x200,0x109+self.sp)]).hex())
                ring.append(row)
                if(tag,pc)==(215,0xb0c2)and bytes(m[pc:pc+3])==bytes.fromhex('b9d8b7'):
                    address=0xb7d8+self.y;pos=16+87*8192+(address&8191);expected=16+96*8192+(address&8191)
                    lookups.append(dict(PC=pc,SP=self.sp,Y=self.y,selected=N.get(m,'SelectedCharacter'),
                        actual_mapped_raw=tag,CPU_address=address,actual_physical_file=pos,actual_byte=m[address],
                        intended_PRG96_file=expected,intended_byte=raw[expected]))
                if pc in(0x15a,0x15d,0x16b):
                    far.append(dict(**row,selected=N.get(m,'SelectedCharacter'),group=N.get(m,'FmGroups'),
                        target=m[0x16c]+256*m[0x16d],safeA=m[0x16a],nextBank=m[0x162],maps=list(m.rawtags)))
                if(tag,pc)==(215,0xb08e):
                    queries.append(dict(**row,selected=N.get(m,'SelectedCharacter'),group=N.get(m,'FmGroups'),
                        target=m[0x16c]+256*m[0x16d],safeA=m[0x16a],nextBank=m[0x162]))
                    assert len(queries)<=128,'Bounded actual public query trace'
            return super().step()
    def observed_key(m,pad,*a,**kw):
        owned=m.bundle['raw']is raw
        if owned:ctx['pad']=pad
        result=key(m,pad,*a,**kw)
        if owned:pads.append(dict(pad=pad,menu=N.get(m,'CrossoverMenuIndex'),selected=N.get(m,'SelectedCharacter'),name=W.UI.menu_name(m)[0]))
        return result
    error=None;passed=False
    with patch.object(N,'NesMPU',CPU),patch.object(W.UI.F,'NesMPU',CPU),patch.object(W.UI,'key',observed_key):
        try:
            m=Old.cold(raw)if kind=='prior-a90'else Model.cold(raw)
            passed=True
        except AssertionError as e:error=str(e)
    m=ctx['m'];c=ctx['cpu'];assert m is not None and c is not None
    return dict(input=kind,ROM_SHA256=C.digest(raw),cold_passed=passed,error=error,last_pad=ctx['pad'],pads=pads,
        public_query_count=len(queries),last_public_queries=queries[-4:],actual_entry_low_lookups=lookups,
        last_farcall_steps=list(far)[-6:],last_actual_instructions=list(ring)[-14:],
        actual_terminal=dict(PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,maps=m.rawtags,
            selected=N.get(m,'SelectedCharacter'),group=N.get(m,'FmGroups'),menu=N.get(m,'CrossoverMenuIndex'),
            target=m[0x16c]+256*m[0x16d],safeA=m[0x16a],nextBank=m[0x162]),
        raw_actual_ROM_CPU_executed=True,no_observer_skip_or_retarget=True)


if __name__=='__main__':
    parent=C.load_current_image();assert C.digest(parent)==C.PIN
    image,_=C.proposal(parent);reference=C.reference(parent)
    def deny(*a,**kw):raise AssertionError('Cold diagnostic attempted output/native')
    rows=[]
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        for kind,raw in(('current40a',parent),('prior-a90',reference),('failed5b28',image)):
            row=trace(raw,kind);rows.append(row)
            print('CASE '+json.dumps(row,separators=(',',':')),flush=True)
    q=dict(rows=rows,outputs=0,Mesen_run=False,no_image_or_opcode_changes=True)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
