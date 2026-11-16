"""Actual ffbb cold/fire cuts: ISR transport and private marker/Turn readers."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import contra_force_p1_work_marker_model_1116 as M

C,N,W,Frames=M.C,M.N,M.W,M.Frames


def run(raw):
    d=C.Plan.descriptor(M.parent(raw));ranges=[tuple(f['CPU_half_open'])for f in d['fragments']]
    base=N.NesMPU;seen=set();coverage=Counter();reads=Counter();cycles=Counter();minimum=255;ordinary=[]
    context={'identity':None,'source':None};kind_count=Counter();stack_min=Counter()
    def check(seed,cpu,kind):
        nonlocal minimum
        # The foreground bus log is instrumentation, not game state. Do not
        # copy a growing log for each ephemeral interrupt fixture.
        W.clear_logs(seed);z=N.fork(seed);c=base(memory=z,pc=cpu.pc)
        for name in('a','x','y','p','sp','processorCycles'):setattr(c,name,getattr(cpu,name))
        before=(c.pc,c.sp,c.a,c.x,c.y,c.p);smc=bytes(z[0x15a:0x17b]);live=bytes(z[0x101+c.sp:0x200])
        private=[bytes(z.ram[i])for i in(1,2,3)];maps=z.rawtags[:];shadow=[N.get(z,n)for n in('CurrentBank','CurrentBankC')]
        scratch=bytes(z[:16]);reader=type(z).__getitem__;atpc={};start=c.processorCycles
        def read(bus,at):
            if isinstance(at,int)and at>=0x8000:
                tag=bus.rawtags[(at-0x8000)//8192]
                if tag==2 and(at&8191)in(0x2df,0x2fb):
                    reads[kind,atpc.get('tag',-1),atpc.get('PC',-1),at&8191]+=1
            return reader(bus,at)
        with patch.object(type(z),'__getitem__',read):
            if kind=='IRQ':
                assert not c.p&4;z[0x5204]=128;c.irq()
            else:
                assert N.get(z,'NmiDisable')&128,'Only genuinely reached busy NMI is injected here'
                c.nmi()
            minimum=min(minimum,c.sp)
            for _ in range(100000):
                if(c.pc,c.sp)==before[:2]:break
                atpc.update(PC=c.pc,tag=z.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1)
                assert z[c.pc]!=0,('Actual ISR BRK',kind,c.pc,z.rawtags)
                minimum=min(minimum,c.sp);c.step()
            else:raise AssertionError(('Actual ISR bound',kind,c.pc))
        assert(c.pc,c.sp,c.a,c.x,c.y,c.p)==before
        assert bytes(z[0x15a:0x17b])==smc and bytes(z[0x101+c.sp:0x200])==live
        assert[bytes(z.ram[i])for i in(1,2,3)]==private
        assert bytes(z[:16])==scratch,'Borrowed original CF render pointers/scratch changed'
        assert z.rawtags==maps and[N.get(z,n)for n in('CurrentBank','CurrentBankC')]==shadow
        cycles[kind,c.processorCycles-start]+=1;kind_count[kind]+=1
    class Observe(base):
        def step(self):
            m=self.memory
            if m.bundle['raw']is raw and self.pc>=0xa000 and m.rawtags[(self.pc-0x8000)//8192]==3 and any(lo<=self.pc<hi for lo,hi in ranges):
                assert N.get(m,'SelectedCharacter')==31
                marker=m.ram[2][0x2df];variant=(N.get(m,'FmGroups')>>3)&3
                # Registers are checked exactly in every interrupt fixture.
                # The compact reached-context key retains all actual status,
                # stack-depth, class and marker-phase variants, not a cap-
                # driven sampling of a per-frame state forest.
                key=(self.pc,self.sp,self.p,variant,marker&192)
                coverage[context['identity'],self.pc]+=1
                if key not in seen:
                    assert len(seen)<8192,'Reached context bound; coverage must not be silently reduced'
                    seen.add(key);stack_min[self.sp]+=1
                    assert N.get(m,'NmiDisable')&128,('New code reached outside admitted busy foreground',self.pc)
                    if not self.p&4:check(m,self,'IRQ')
                    check(m,self,'busyNMI')
            return super().step()
    with patch.object(N,'NesMPU',Observe):
        for key in M.IDENTITIES:
            context['identity']=key;m=M.cold(raw,key);active_shot_updates=loan_entries=0
            for age in range(32):
                # Ordinary crouch settle, then a two-update B pulse per8.
                m.controller_pad=4|(64 if age>=6 and age%8 in(6,7)else 0)
                Frames.frame(m,whole_pass=True)
                assert N.get(m,'NumberofLives')==2 and N.get(m,'PlayerStatus')==0
                assert not any(m[514+i*4]&24 for i in range(64)),('Complete draw left a hidden/visible tag',key,age)
                assert not m.ram[2][0x2df]&128
                active_shot_updates+=int(any(m.ram[2][0x382+i]for i in range(10,22)))
                loan_entries+=int(m.ram[2][0x2fb]==1)
            row=dict(identity=key,ordinary_Main=32,active_shot_updates=active_shot_updates,loan_palette_updates=loan_entries,
                lives=N.get(m,'NumberofLives'),x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                y=N.get(m,'Player_Y_Position'),all_complete_updates_strip_all64_attributes=True)
            assert active_shot_updates>0,(key,'Ordinary source B did not produce a shot')
            ordinary.append(row);print('PROGRESS '+json.dumps(dict(row,distinct_reached_contexts=len(seen),ISR=dict(kind_count))),flush=True)
    assert not reads,('Actual ISR reads changed private marker/Turn',dict(reads))
    return dict(actual_candidate_SHA256=C.H(raw),unique_reached_contexts=len(seen),
        context_key='PC/SP/full hardware status/class/marker phase; AXY are preserved exactly per actual fixture',
        minimum_SP=minimum,ISR_counts=dict(kind_count),ISR_cycles=[dict(kind=k,cycles=cy,cases=n)for(k,cy),n in sorted(cycles.items())],
        actual_ISRs_read_private_marker_or_intermediateTurn=0,AXYP_SP_all33SMC_full_privateRAM123_live_stack_scratch_maps_exact=True,
        ordinary_all4_class_cold_crouch_B_shot_and_completed_tag_cleanup=ordinary,
        regular_NMI_midbusyMain_not_invented=True,interrupt_fixtures_ephemeral_no_persistent_state_dumps=True,
        reached_PC_counts={k:len({pc for(owner,pc)in coverage if owner==k})for k in M.IDENTITIES},
        actor_health_position_or_terrain_seeds=0,native=False,outputs=0)


if __name__=='__main__':
    parent=C.load_current_image();raw,_=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Reached ISR proof attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw)
    q['source_receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
