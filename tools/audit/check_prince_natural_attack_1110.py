"""One natural A-attack attempt after landing; no inventory/actor seeding."""
from collections import Counter
import json
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q

C,N,I,F=Q.C,Q.N,Q.I,Q.Foot.F


def main():
    _,bundle,_,layout,_,_,_=Q.proposal()
    env,seed,labels=C.fixture(bundle);N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
    F.REAL_NMI=True;_,model=F.authored(seed)
    code=bytes(model.ram[2][0x1dbe:0x1e99]);pattern=bytes.fromhex('bd4606c903d0')
    sites=[0xddbe+i for i in range(len(code)) if code[i:i+len(pattern)]==pattern]
    assert len(sites)==1,sites
    compare=sites[0]+3
    tick=0;stage='run';landed=None;weapons=set();actions=set();proxy=[];damage=[];contact=[]
    counts=Counter();native=N.NesMPU;recent=[]
    def row():
        r=F.sample(model,tick)
        r.update(sword_mode=model.ram[2][0x6ee],guard_UID=model.ram[2][0x61c],
            guard_live=model.ram[2][0x6e0],guard_HP=model.ram[2][0x6d0])
        for actor in r['actors']:
            actor['bbox_control']=model[I.address(bundle,'Enemy_BoundBoxCtrl')+actor['slot']]
        return r
    class Trace(native):
        def step(self):
            if self.memory is not model:return super().step()
            pc=self.pc;tag=model.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            if tag==2 and pc==compare and landed is not None:
                state=N.get(model,'Enemy_State',self.x);control=self.a
                counts['proxy_cmp3_ctrl'+str(control)+'_state'+str(state)]+=1
                if len(proxy)<8:proxy.append(dict(tick=tick,slot=self.x,control=control,state=state,
                    actual_ID=N.get(model,'Enemy_ID',self.x),PC=pc,source_sword=model.ram[2][0x6ee]))
            if tag==3 and pc==0xbd22 and landed is not None:
                contact.append(dict(tick=tick,slot=self.x,source=row(),source_opcode_regs=[self.a,self.x,self.y,self.p,self.sp]))
            hp=model.ram[2][0x6cf];recent.append([tag,pc,self.a,self.x,self.y,self.p,self.sp])
            if len(recent)>12:recent.pop(0)
            result=super().step()
            if hp!=model.ram[2][0x6cf]:damage.append(dict(tick=tick,bank=tag,PC=pc,before=hp,
                after=model.ram[2][0x6cf],source=row(),last_instructions=recent[:]))
            return result
    with patch.object(N,'NesMPU',Trace):
        for tick in range(240):
            r=row();x,y=r['x'],r['y'];weapons.add(r['sword_mode']);actions.add(r['action'])
            if not r['hp'] or r['engine']!=8 or r['lives']!=2:break
            if stage=='run' and 745<=x<=752 and abs(y-112)<=2 and C.Recovery.running(model,r):stage='takeoff'
            if stage=='takeoff' and r['action']==4:stage='flight'
            if landed is None and N.get(model,'Enemy_State',1)==4:landed=tick
            pad=129 if stage=='takeoff' else 1
            if landed is not None:pad=128 if (tick-landed)%16<8 else 0
            C.Route.controls(env,model,labels,pad);N.consume(model)
    print('NATURAL_ATTACK '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],
        attack_button='A ($80), original source attack button;8on/8off after actual landing',
        sword_modes=sorted(weapons),source_actions=sorted(actions),protected_attack_actions_seen=sorted(actions&{62,69,74}),
        landing=landed,terminal=row(),actual_proxy_literal=dict(PC=compare,bytes=pattern.hex()),
        proxy_eligibility_counts=dict(counts),proxy_samples=proxy,damage=damage,contacts=contact,
        source_inventory_or_enemy_outcomes_seeded=False,ROM_written=False,outputs_written=0)),flush=True)


if __name__=='__main__':main()
