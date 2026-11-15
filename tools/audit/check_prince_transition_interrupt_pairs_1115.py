"""Paired current NMIs at genuine219 cuts, restoring only old219 on baseline."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_transition_model_1115 as Model

N,W=Model.N,Model.W


def run(raw):
    current=Model.Current.normalize(raw,kind='prince-graphics-590')
    recipe=Model.Research.importer_plan(current.referenceAE);old,new=recipe['old'],recipe['new']
    start,end=Model.Research.START,Model.Research.END;base=N.NesMPU
    counts=Counter();seen=set();cuts=[];minimum=255;native_effects=Counter();entry_routes=Counter();trace_hash=sha256()
    cookie=raw[Model.Current.Graphics.Packet.COOKIE:Model.Current.Graphics.Packet.COOKIE+16]
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_probe_active',False)and start<=at<end and self.rawtags[2]==2:
                self._owned_code_reads.append(at)
            return super().__getitem__(at)
    def critical(m):
        names=('SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine','NumberofLives',
            'WorldNumber','LevelNumber','PlayerStatus','StarInvincibleTimer','FrameCounter',
            'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos')
        return tuple(N.get(m,name)for name in names)+tuple(N.get(m,name,i)for name in
            ('Enemy_Flag','Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position')for i in range(6))
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
    def pair(cpu,kind):
        nonlocal minimum
        machines=[];before=[];regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc)
        for parent in(False,True):
            m=N.fork(cpu.memory);m.__class__=Bus;m._owned_code_reads=[];m._probe_active=False
            if parent:m.ram[2][start&8191:end&8191]=old
            assert bytes(m.ram[2][start&8191:end&8191])==(old if parent else new)
            c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            before.append(dict(private=[bytes(b)for b in m.ram],transport=transport(m),critical=critical(m),
                native=bytes(m[:0x800]),upper=bytes(m[0x101+c.sp:0x200]),skip=N.get(m,'NmiSkipped')))
            m._probe_active=True;c.irq()if kind=='IRQ'else c.nmi();machines.append((c,m))
        entry_routes[kind+':'+hex(machines[0][0].pc)]+=1
        assert(machines[0][0].pc,machines[0][0].sp)==(machines[1][0].pc,machines[1][0].sp)
        for steps in range(100000):
            a,ma=machines[0];b,mb=machines[1]
            ra=(a.a,a.x,a.y,a.p&239,a.sp,a.pc);rb=(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            assert ra==rb,'Restoring only219 altered ISR CPU path'
            minimum=min(minimum,a.sp,b.sp)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and b.sp<=regs[4]
            tag=ma.rawtags[(a.pc-0x8000)//8192]if a.pc>=0x8000 else-1
            assert not(start<=a.pc<end and tag==2),'ISR must not execute changed219'
            instruction=bytes(ma[a.pc:a.pc+3]);assert instruction==bytes(mb[b.pc:b.pc+3])and ma.rawtags==mb.rawtags
            trace_hash.update(bytes((a.pc&255,a.pc>>8,a.sp,a.p&239,tag&255))+instruction)
            assert ma[a.pc]and mb[b.pc];a.step();b.step()
        else:raise AssertionError('Paired ISR return bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        effects=[]
        for which,(c,m)in enumerate(machines):
            m._probe_active=False;prior=before[which]
            assert not m._owned_code_reads,'NMI/IRQ routing or data must not depend on restored219'
            assert [bytes(row)for row in m.ram]==prior['private'],'ISR private-game write'
            assert transport(m)==prior['transport']and critical(m)==prior['critical']
            assert bytes(m[0x101+regs[4]:0x200])==prior['upper'],'ISR above-entry caller stack write'
            assert N.get(m,'NmiSkipped')==(prior['skip']+(kind=='busyNMI'))&255
            effects.append(bytes(m[:0x800]))
        assert effects[0]==effects[1],'Candidate/baseline native RAM, audio or stack effects differ'
        for i,(left,right)in enumerate(zip(before[0]['native'],effects[0])):
            if left!=right and not 0x100<=i<0x200:native_effects[(kind,i,left,right)]+=1
        counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if hasattr(m,'rawtags')and start<=self.pc<end and m.rawtags[2]==2 and not self.p&4:
                if hasattr(m,'bundle')and m.bundle.get('raw')==raw and N.get(m,'SelectedCharacter')==38:
                    if all(bytes(m.ram[b][0x1fe0:0x1ff0])==cookie for b in(2,3)):
                        assert bytes(m.ram[2][start&8191:end&8191])==new
                        key=(self.pc,self.sp,self.p&193)
                        if key not in seen:
                            seen.add(key);assert len(seen)<=512
                            pair(self,'IRQ')
                            if N.get(m,'NmiDisable')==255:pair(self,'busyNMI')
                            cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p))
            return super().step()
    def stop(m,tick):
        s=Model.state(m);return tick>4507 and s['x']>=1880 and s['guard']==1 and s['hp']>0
    with patch.object(N,'NesMPU',CPU):q=Model.run(raw,full=True,limit=5100,frame_observer=stop)
    assert q['checkpoint_reached']and counts['IRQ']and counts['busyNMI']
    q.update(paired_interrupt_counts=dict(counts),reached_unique_contexts=len(cuts),minimum_ISR_SP=minimum,
        reached_instruction_PCs=sorted({row['PC']for row in cuts}),entry_routes=dict(entry_routes),
        identical_ISR_path_trace_SHA256=trace_hash.hexdigest(),
        baseline_restores_only_original219=True,no_ISR_read_or_execution_of219=True,
        exact_same_native_RAM_audio_stack_effects=True,no_private_game_writes=True,
        all_live_transport_and_above_entry_stack_preserved=True,critical_gameplay_fields_constant=True,
        observed_native_effects=[dict(kind=key[0],address=key[1],before=key[2],after=key[3],cases=count)for key,count in sorted(native_effects.items())],
        scope='Counterfactual same-context old219 versus proposed219 ISR fidelity; no native-RAM/audio allowlist')
    q['paired_interrupt_receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Paired IRQ source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
