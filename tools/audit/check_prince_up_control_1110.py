"""Original donor input differential and real fourth-wall action callers.

Uses one fixed Up+Right continuation after the repaired landing, plus the
unchanged successful third-cap fixture. The translated CPU scene is explicit;
the observer seeds no control, terrain, enemy, damage or protection outcome.
"""
import argparse
import json
import re
import sys
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q

sys.path.insert(0,str(Q.R/'tools/reference'))
import prince_original_cpu_1101_v1 as Donor

C,N,I,F=Q.C,Q.N,Q.I,Q.Foot.F


def decode_entry(m):
    data=bytes(m.ram[3][:8159]);found=[]
    for i in range(len(data)-18):
        if data[i:i+3]!=bytes.fromhex('ad18c6'):continue
        if bytes.fromhex('8d16c6ad35c7') in data[i+3:i+14]:found.append(0xa000+i)
    assert len(found)==1,found
    return found[0]


def original_decode(state,regs):
    d=Donor.machine();d.memory.switch(5)
    list.__setitem__(d.memory,slice(0,2048),state)
    out=Donor.call(d,0x839f,a=regs[0],x=regs[1],y=regs[2],p=regs[3])
    return bytes(d.memory[:2048]),out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pad',type=int,choices=(8,9),default=9)
    args=parser.parse_args()
    _,bundle,_,layout,_,_,_=Q.proposal()
    native=N.NesMPU;controls=C.Route.controls
    target=None;tick=-1;part='third';pending=None;points=[];events=[];writes=[];recent=[];aligns=[]
    original_names={int(pc,16):name for pc,name in re.findall(r'^al ([0-9A-Fa-f]+) \.?(PpN_\S+)$',
        (Q.R/'build/prince-actor-1101-v1/contact-core.lbl').read_text(),re.M)}
    checked=0;decoder=None;matrix_seed=None;matrix_regs=None;current_pad=0
    def state(m):
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),source_x=int.from_bytes(m.ram[2][0x60f:0x611],'little'),
            source_y=m.ram[2][0x611],action=m.ram[2][0x616],frame=m.ram[2][0x617],
            mode=m.ram[2][0x618],facing=m.ram[2][0x615],source_phase=m.ram[2][0xa6]&3,
            HP=m.ram[2][0x6cf],native_pad=N.get(m,'SavedJoypad1Bits'),source_pad=m.ram[2][0x40a],
            forward=m.ram[2][0x3a],back=m.ram[2][0x3b],up=m.ram[2][0x3c],
            down=m.ram[2][0x3d],vertical=m.ram[2][0x3e],horizontal=m.ram[2][0x40],
            a_latch=m.ram[2][0x6c0],flag4e4=m.ram[2][0x4e4],flag4f6=m.ram[2][0x4f6])
    class Trace(native):
        def step(self):
            nonlocal pending,checked,matrix_seed,matrix_regs
            if self.memory is not target:return super().step()
            m=target;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            if pending and (pc,self.sp)==pending['return']:
                want,oracle=original_decode(pending['state_bytes'],pending['regs'])
                got=bytes(m.ram[2][:2048]);diff=[i for i,(a,b) in enumerate(zip(got,want)) if a!=b and not 0x100<=i<0x200]
                assert not diff,(part,tick,'donor DecodeInput state mismatch',diff[:12])
                assert [self.a,self.x,self.y,self.p&0xcf]==[oracle[0],oracle[1],oracle[2],oracle[3]&0xcf]
                checked+=1
                if part=='fourth' and 91<=tick<=141:
                    points.append(dict(tick=tick,part=part,input=pending['in'],output=state(m),
                        actual_registers=[self.a,self.x,self.y,self.p],original_registers=list(oracle[:4])))
                pending=None
            if tag==3 and pc==decoder:
                back=((m[0x101+self.sp]|m[0x102+self.sp]<<8)+1)&65535
                pending=dict(state_bytes=bytes(m.ram[2][:2048]),regs=[self.a,self.x,self.y,self.p],
                    **{'return':(back,self.sp+2)},**{'in':state(m)})
                if part=='fourth' and matrix_seed is None:
                    matrix_seed=Q.Sonic.slim_fork(m);matrix_regs=pending['regs']
            if tag==3 and pc==0xa34d and self.y==0:
                events.append(dict(part=part,tick=tick,selected_action=self.a,state=state(m),recent=recent[-14:]))
            if tag==2 and pc==0xc40b:
                aligns.append(dict(part=part,tick=tick,alignment_y=self.y,state=state(m),
                    cell_x=int.from_bytes(m.ram[2][0x7d:0x7f],'little'),
                    material=m.ram[2][0x9f],surface=int.from_bytes(m.ram[2][0x7f:0x81],'little'),
                    original_index=m.ram[2][0x4b1],recent=recent[-5:]))
            if tag in (2,3):
                recent.append(dict(bank=tag,PC=pc,original=original_names.get(pc) if tag==3 else None,
                    op=bytes(m[pc:pc+3]).hex(),regs=[self.a,self.x,self.y,self.p,self.sp]))
                if len(recent)>22:recent.pop(0)
            before=m.ram[2][0x40a]
            result=super().step()
            if m.ram[2][0x40a]!=before:
                writes.append(dict(part=part,tick=tick,bank=tag,PC=pc,before=before,after=m.ram[2][0x40a],
                    native_pad=N.get(m,'SavedJoypad1Bits'),requested_pad=current_pad))
                assert m.ram[2][0x40a]==N.get(m,'SavedJoypad1Bits')==current_pad
            return result
    def controlled(e,m,l,pad):
        nonlocal target,tick,decoder,current_pad
        target=m;tick+=1;current_pad=pad
        if decoder is None:decoder=decode_entry(m)
        return controls(e,m,l,pad)
    with patch.object(N,'NesMPU',Trace),patch.object(C.Route,'controls',controlled):
        env,seed,labels=C.fixture(bundle)
        N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
        F.REAL_NMI=True;_,model=F.authored(seed)
        part='fourth';tick=-1;stage='run';landed=None
        for epoch in range(143):
            r=F.sample(model,epoch);x,y=r['x'],r['y']
            if not r['hp'] or r['engine']!=8 or r['lives']!=2:break
            if stage=='run' and 745<=x<=752 and abs(y-112)<=2 and C.Recovery.running(model,r):stage='takeoff'
            if stage=='takeoff' and r['action']==4:stage='flight'
            if landed is None and N.get(model,'Enemy_State',1)==4:landed=epoch
            pad=129 if stage=='takeoff' else 1
            if landed is not None:pad=args.pad
            C.Route.controls(env,model,labels,pad);N.consume(model)
    assert matrix_seed is not None
    Q.Sonic.O.clear_logs(matrix_seed)
    for pad in range(256):
        m=Q.Sonic.slim_fork(matrix_seed);m.ram[2][0x40a]=pad
        before=bytes(m.ram[2][:2048]);want,oracle=original_decode(before,matrix_regs)
        out=I.invoke(m,3,decoder,tuple(matrix_regs));got=bytes(m.ram[2][:2048])
        assert all(a==b or 0x100<=i<0x200 for i,(a,b) in enumerate(zip(got,want))),(pad,'donor input matrix')
        assert [*out['regs'][:3],out['regs'][3]&0xcf]==[*oracle[:3],oracle[3]&0xcf]
    selected=[]
    for e in events:
        if e['part']!='fourth' and e['selected_action'] not in (13,24,25,10):continue
        selected.append(dict(e,recent=[q for q in e['recent'] if q['bank']==3][-5:]))
    compact_points=[dict(tick=q['tick'],action=q['input']['action'],frame=q['input']['frame'],
        mode=q['input']['mode'],pad=q['output']['source_pad'],
        decoded={k:q['output'][k] for k in ('forward','back','up','down','vertical','horizontal')}) for q in points]
    print('UP_CONTROL '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],
        original_donor_SHA256=Donor.SHA,decoder_PC=decoder,actual_decode_calls_exact=checked,
        original_decode_all256_controller_bytes=True,continuation_pad=args.pad,source_pad_writes=writes,
        fourth_decode_calls=compact_points,original_action_entries=selected,world_align_entries=aligns,
        terminal=state(model),translated_CPU_scene=True,ROM_written=False,outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
