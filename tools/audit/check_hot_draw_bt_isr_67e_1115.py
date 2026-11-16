"""Reached new draw instructions/transport with actual IRQ and NMI oracles."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import compose_hot_draw_bt_67e_1115 as C
import hot_draw_bt_67e_model_1115 as Model
import check_hot_draw_bt_frames_67e_1115 as Families

W,N,Frames=Model.W,Model.N,Model.Frames


def run(parent,image):
    base=N.NesMPU;captures={};phase='cold';minimum=255
    class Capture(base):
        def __init__(self,*a,**kw):
            super().__init__(*a,**kw);self.inside=False
            self.endpoint=(W.address(self.memory.bundle,'IdleLoop'),253)if self.pc==W.address(self.memory.bundle,'IdleLoop')else(0x5b00,224)
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(tag,self.pc)==(194,C.BASE):self.inside=True
            if self.inside and(tag,self.pc)==(132,0xa125):self.inside=False
            new=tag==194 and C.BASE<=self.pc<C.BASE+89
            transport=self.inside and((tag,self.pc)in((215,0xb026),(215,0xb08e),(221,0xadc0),(3,0xa006))or self.pc in(0x15a,0x15d,0x163,0x166,0x16e))
            if m.bundle['raw']is image and(new or transport):
                key=(phase,tag,self.pc,self.p&0xef,self.endpoint)
                if key not in captures or self.sp<captures[key][1]['sp']:
                    captures[key]=(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')},self.endpoint)
            return super().step()
    with patch.object(N,'NesMPU',Capture),patch.object(W.UI.F,'NesMPU',Capture):
        m=Model.cold(image)
        for phase,pad in(('idle',0),('Right',1)):
            m.controller_pad=pad;Frames.frame(m,whole_pass=True)
        # These real compiled constructors reach the remaining low/middle and
        # alternate selector branches, not fabricated instruction PCs.
        for phase,slot,cycles,name in(('hogan',28,0,'HULK HOGAN'),('prince',29,1,'PRINCE PERSIA'),
            ('bub',25,1,'BUB'),('mini',0,8,'MINI MARIO'),('karnov',7,1,'KARNOV')):
            z=Families.family_cold(image,slot,cycles,name);z.controller_pad=0;Frames.frame(z,whole_pass=True)
    assert captures and len(captures)<=1024,len(captures)
    print('PROGRESS '+json.dumps(dict(reached_instruction_transport_contexts=len(captures))),flush=True)
    counts=Counter();arms=Counter();rows=[];early_commits=Counter()
    def finish(seed,regs,endpoint):
        z=Model.reimage(seed,image);c=base(memory=z,pc=regs['pc'])
        for name,value in regs.items():setattr(c,name,value)
        for _ in range(500000):
            if(c.pc,c.sp)==endpoint:break
            assert z[c.pc],('ISR continuation BRK',c.pc,c.sp,regs);c.step()
        else:raise AssertionError(('ISR continuation bound',c.pc,c.sp,endpoint,regs))
        return z,tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
    for key,(arena,regs,endpoint)in sorted(captures.items()):
        busy=bool(N.get(arena,'NmiDisable')&128)
        kinds=('NMI',)if regs['p']&4 else('IRQ','NMI')
        for kind in kinds:
            results=[]
            for raw in(parent,image):
                z=Model.reimage(arena,raw);c=base(memory=z,pc=regs['pc'])
                for name,value in regs.items():setattr(c,name,value)
                original=tuple(regs[n]for n in('pc','sp','a','x','y','p'));skipped=N.get(z,'NmiSkipped')
                c.irq()if kind=='IRQ'else c.nmi();recent=[]
                for _ in range(200000):
                    minimum=min(minimum,c.sp)
                    if(c.pc,c.sp)==original[:2]:break
                    assert z[c.pc],('Actual ISR BRK',key,kind,c.pc)
                    recent.append((z.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1,c.pc,c.sp))
                    if len(recent)>12:recent.pop(0)
                    c.step()
                else:raise AssertionError(('Actual ISR return bound',key,kind))
                actual=tuple(getattr(c,n)for n in('pc','sp','a','x','y','p'))
                assert actual[:5]==original[:5]and actual[5]&0xef==original[5]&0xef,(key,kind,original,actual)
                delta=[dict(address=at,before=arena[at],after=z[at])for at in range(0x15a,0x17b)if arena[at]!=z[at]]
                assert not delta,('ISR SMC restore',key,kind,delta)
                if z.rawtags!=arena.rawtags:
                    # FarCall updates its software shadow immediately before
                    # STA5115. A busy NMI's unchanged audio farcalls may return
                    # with that future bank already mapped. Qualify only this
                    # real pending commit, not arbitrary mapper differences.
                    assert regs['pc']==0x166 and bytes(arena[0x166:0x169])==bytes.fromhex('8d1551')
                    shadow=N.get(arena,'CurrentBank')
                    assert regs['a']==shadow==arena[0x162]
                    expected=list(arena.rawtags);expected[1]=shadow
                    assert z.rawtags==expected,('Unexpected ISR mapper effect',key,kind,arena.rawtags,z.rawtags,shadow)
                    one=Model.reimage(arena,image);commit=base(memory=one,pc=regs['pc'])
                    for name,value in regs.items():setattr(commit,name,value)
                    commit.step()
                    assert commit.pc==0x169 and one.rawtags==z.rawtags
                    assert tuple(getattr(commit,n)for n in('sp','a','x','y','p'))==tuple(regs[n]for n in('sp','a','x','y','p'))
                    assert bytes(one[0x15a:0x17b])==bytes(arena[0x15a:0x17b])
                    early_commits[kind,arena.rawtags[1],shadow]+=1
                assert bytes(z[0x101+regs['sp']:0x200])==bytes(arena[0x101+regs['sp']:0x200])
                if kind=='NMI'and busy:assert(N.get(z,'NmiSkipped')-skipped)&255==1
                results.append((z,{n:getattr(c,n)for n in('pc','sp','a','x','y','p')}))
            Model.compare([z for z,_ in results],min(152,minimum))
            assert results[0][1]==results[1][1]
            ends=[finish(z,r,endpoint)for z,r in results]
            Model.compare([z for z,_ in ends],min(152,minimum));assert ends[0][1]==ends[1][1]
            sp=ends[0][1][1]
            assert bytes(ends[0][0][0x101+sp:0x200])==bytes(ends[1][0][0x101+sp:0x200])
            counts[kind]+=1;arms[kind,'busy'if busy else'regular']+=1
        rows.append(dict(context=key[0],tag=key[1],PC=key[2],P=regs['p'],SP=regs['sp'],
            NmiDisable_busy=busy,endpoint=list(endpoint),arms=list(kinds)))
        if len(rows)%32==0:print('PROGRESS '+json.dumps(dict(contexts=len(rows),arms=dict(counts),minimum_SP=minimum)),flush=True)
    return dict(reached_instruction_transport_contexts=len(rows),minimum_SP=minimum,cuts=dict(counts),
        arms=[dict(kind=k,state=s,cases=n)for(k,s),n in sorted(arms.items())],
        actual_unmodified_parent_ISR_oracle=True,continuations_execute_actual_candidate=True,
        exact_AXYP_SP_SMC_maps_native_private_RAM_PPU_VRAM_and_live_stack=True,
        normalized_status_deepest_reached_stack_contexts_retained=True,
        exact_pending_STA5115_early_publications=[dict(kind=k,previous_bank=a,pending_bank=b,parent_and_candidate_events=n)
            for(k,a,b),n in sorted(early_commits.items())],
        pending_commit_PC=0x166,pending_commit_opcode='8d1551',
        each_early_map_matches_actual_one_instruction_commit=True,no_blanket_mapper_or_SMC_mask=True,
        no_forced_NmiDisable_or_unreachable_ISR_arm=True,
        complete_rows_SHA256=C.H(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),sparse_rows=rows[:32])


if __name__=='__main__':
    raw=C.load_current_image();parent=Model.F.parent(raw);image,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('ISR gate attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Carry.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):q=run(parent,image)
    q.update(parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
