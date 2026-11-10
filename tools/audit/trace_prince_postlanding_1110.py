"""Trace Prince's first post-stomp debit in memory; no artifact or ROM writes."""
import json
from unittest.mock import patch

import check_prince_landing_exit_1110 as Exit
import prince_original_cpu_1101_v1 as Original

C,N,I=Exit.C,Exit.C.N,Exit.C.I


def main():
    assert C.digest(Exit.ROM.read_bytes())==Exit.PIN
    bundle=C.Start.W.bundle(Exit.ROM.read_bytes())
    env,model,labels=C.fixture(bundle)
    N.put(model,CrossoverBehaviorVersion=0)
    stage='run';tick=0;history=[];changes=[];entries=[];fall_counts=[];snapshots=[]
    native=N.NesMPU
    watch={(2,0xddbe):'ProxyIn',(2,0xde99):'ProxyOut',(2,0xdadd):'DonorDefenderContact',
           (3,0xbd22):'NativeContact',(3,0xb36e):'HostUpdate',
           (254,I.address(bundle,'EnemyStomped')):'EnemyStomped'}
    class Trace(native):
        def step(self):
            if self.memory is not model:return super().step()
            pc=self.pc
            bank=model.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            before=model.ram[2][0x6cf]
            old_count=model.ram[2][0x6c6]
            if (bank,pc)==(3,0xa297) and tick==91:
                snapshots.append((bytes(model.ram[2][:0x800]),[self.a,self.x,self.y,self.p]))
            if (bank,pc) in watch:
                entries.append(dict(tick=tick,pc=pc,bank=bank,name=watch[bank,pc],
                                    guard_UID=model.ram[2][0x61c],guard_live=model.ram[2][0x6e0]))
            if tick>=90 and pc>=0x8000:
                history.append([bank,pc,self.a,self.x,self.y,self.p,self.sp])
                if len(history)>28:history.pop(0)
            result=super().step()
            if model.ram[2][0x6c6]!=old_count:
                fall_counts.append(dict(tick=tick,pc=pc,bank=bank,before=old_count,
                    after=model.ram[2][0x6c6],source_y=model.ram[2][0x611],
                    foot=int.from_bytes(model.ram[2][0x84:0x86],'little'),action=model.ram[2][0x616]))
            if model.ram[2][0x6cf]!=before:
                row=dict(tick=tick,PC=pc,bank=bank,HP_before=before,HP_after=model.ram[2][0x6cf],
                    regs=[self.a,self.x,self.y,self.p,self.sp],
                    source_actor=bytes(model.ram[2][0x60e:0x61c]).hex(),
                    source_guard=bytes(model.ram[2][0x61c:0x62a]).hex(),
                    source_6c0_6ef=bytes(model.ram[2][0x6c0:0x6f0]).hex(),
                    native_actors=C.Route.actors(model),entries=entries[-12:],trace=history[:])
                changes.append(row);print(json.dumps(row,separators=(',',':')),flush=True)
            return result
    with patch.object(N,'NesMPU',Trace):
        for tick in range(100):
            row=C.Recovery.sample(model,tick)
            if tick>=89:print('Frame '+json.dumps(row,separators=(',',':')),flush=True)
            if row['hp']<5:break
            if stage=='run' and 745<=row['x']<=752 and abs(row['y']-112)<=2 and C.Recovery.running(model,row):stage='takeoff'
            if stage=='takeoff' and row['action']==4:stage='flight'
            C.Route.controls(env,model,labels,129 if stage=='takeoff' else 1)
    assert changes and changes[0]['tick']==91
    state,regs=snapshots[0]
    donor=Original.machine();donor.memory.switch(5)
    list.__setitem__(donor.memory,slice(0,0x800),state)
    outcome=Original.call(donor,0x858a,a=regs[0],x=regs[1],y=regs[2],p=regs[3],limit=20000)
    assert state[0x6cf]==5 and state[0x6c6]==3 and donor.memory[0x6cf]==4
    writes=[(at,value) for at,value in donor.memory.writes if at==0x6cf]
    assert writes==[(0x6cf,4)],writes
    print('ORIGINAL_DONOR '+json.dumps(dict(donor_SHA256=Original.SHA,
        translated_entry=0xa297,original_entry=[5,0x858a],
        translated_store=0xa28e,original_store=[5,0x8581],
        source_fall_counter_before=state[0x6c6],HP_before=state[0x6cf],
        original_HP_after=donor.memory[0x6cf],original_HP_writes=writes,
        original_returns=list(outcome),fall_counter_trace=fall_counts),separators=(',',':')),flush=True)


if __name__=='__main__':main()
