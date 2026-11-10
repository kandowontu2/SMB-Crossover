"""Observe existing stomp/contact protection after actual Prince landing.

Executes c3fb GameLoop plus normal NMI on authored native fourth-pipe data.
The translated CPU setup is explicit; no enemy, inventory, damage, timer or
protection outcome is seeded. Writes no artifact and patches no source code.
"""
import json
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q

C,N,I,F=Q.C,Q.N,Q.I,Q.Foot.F


def main():
    _,bundle,_,layout,_,_,_=Q.proposal()
    env,seed,labels=C.fixture(bundle);N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
    F.REAL_NMI=True;_,model=F.authored(seed)
    fields=['StompTimer','StompChainCounter','InjuryTimer','StarInvincibleTimer',
        'GuestHurtKind','GuestHurtTicks','GuestInvulTicks','GuestBodyPrev','GuestBodyNow',
        'Enemy_CollisionBits','Player_CollisionBits','TimerControl','IntervalTimerControl']
    address={name:I.address(bundle,name) for name in fields}
    watched=['StompTimer','InjuryTimer','StarInvincibleTimer','GuestHurtKind','GuestHurtTicks','GuestInvulTicks']
    watch={(3,0xbd22):'PrinceNativeContact',(2,0xd47d):'PrinceLandingContact',
        (2,0xdadd):'OriginalDefender'}
    for name in ['PlayerEnemyCollision','GuestBodyContactBridge','MarioSourceBodyImmunity',
        'EnemyStomped','ChkForPlayerInjury','ChkETmrs','InjurePlayer','X5StompDispatch']:
        if name in bundle['syms']:
            watch[((I.location(bundle,name)-16)//8192)|128,I.address(bundle,name)]=name
    tick=0;phase='Main';pending=[];calls=[];writes=[];snapshots=[];hp=[];native=N.NesMPU
    def protection():
        out={name:model[at] for name,at in address.items()}
        out['Enemy_CollisionBits']=list(model[address['Enemy_CollisionBits']:address['Enemy_CollisionBits']+6])
        return out
    def row():
        r=F.sample(model,tick)
        return dict(x=r['x'],y=r['y'],foot=r['foot'],action=r['action'],mode=r['mode'],
            source_HP=r['hp'],native_DY=N.get(model,'Player_Y_Speed'),sword=model.ram[2][0x6ee],
            ObjectOffset=N.get(model,'ObjectOffset'),actors=r['actors'],protection=protection())
    def stamp():return dict(tick=tick,phase=phase,**row())
    class Trace(native):
        def step(self):
            if self.memory is not model or tick<89:return super().step()
            pc=self.pc;tag=model.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            for item in pending[:]:
                if (pc,self.sp)==item['return']:
                    item['out']=dict(regs=[self.a,self.x,self.y,self.p,self.sp],**stamp())
                    calls.append(item);pending.remove(item)
            name=watch.get((tag,pc))
            if name and (name!='PlayerEnemyCollision' or model[I.address(bundle,'Enemy_ID')+self.x]<7):
                back=((model[0x101+self.sp]|model[0x102+self.sp]<<8)+1)&65535
                item=dict(name=name,PC=pc,bank=tag,regs=[self.a,self.x,self.y,self.p,self.sp],
                    **{'return':(back,self.sp+2)},**stamp())
                # Collision entry is frequent even without body overlap. Save
                # only its real admission side effects or actual source calls.
                pending.append(item)
            before=tuple(model[address[n]] for n in watched);old_hp=model.ram[2][0x6cf]
            result=super().step()
            after=tuple(model[address[n]] for n in watched)
            if before!=after:
                writes.append(dict(tick=tick,phase=phase,bank=tag,PC=pc,
                    changes={n:[a,b] for n,a,b in zip(watched,before,after) if a!=b},**row()))
            if old_hp!=model.ram[2][0x6cf]:
                hp.append(dict(tick=tick,phase=phase,bank=tag,PC=pc,before=old_hp,
                    after=model.ram[2][0x6cf],protection=protection()))
            return result
    stage='run';landed=None
    with patch.object(N,'NesMPU',Trace):
        for tick in range(145):
            r=F.sample(model,tick);x,y=r['x'],r['y']
            if not r['hp'] or r['engine']!=8 or r['lives']!=2:break
            if stage=='run' and 745<=x<=752 and abs(y-112)<=2 and C.Recovery.running(model,r):stage='takeoff'
            if stage=='takeoff' and r['action']==4:stage='flight'
            if landed is None and N.get(model,'Enemy_State',1)==4:landed=tick
            pad=129 if stage=='takeoff' else 1
            if landed is not None:pad=128 if (tick-landed)%16<8 else 0
            phase='Main';C.Route.controls(env,model,labels,pad)
            if tick in (89,90,91,92,141,142):snapshots.append(stamp())
            phase='normalNMI';N.consume(model)
            if tick in (89,90,91,92,141,142):snapshots.append(stamp())
    admitted=[]
    for item in calls:
        name=item['name']
        if name=='PlayerEnemyCollision':
            # Keep only actual overlap tick90/142, where the source callback
            # is independently observed below, plus next update91.
            if item['tick'] not in (90,91,142):continue
        if name=='MarioSourceBodyImmunity' and item['tick'] not in (90,142):continue
        admitted.append({k:v for k,v in item.items() if k!='return'})
    assert landed==91 and hp[0]['before']==5 and hp[0]['after']==4 and hp[0]['tick']==91
    assert [(p['tick'],p['before'],p['after']) for p in hp[1:]]==[(142,4,3),(142,3,2),(142,2,1),(142,1,0)]
    assert any(q['name']=='EnemyStomped' and q['tick']==90 and q['regs'][1]==1 for q in calls)
    assert any(q['name']=='OriginalDefender' and q['tick']==142 and q['protection']['StompTimer']==0 for q in calls)
    print('STOMP_GRACE '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],
        native_symbols={name:dict(bank=bank,PC=pc) for (bank,pc),name in watch.items()},
        native_fields=address,landing=landed,protection_writes=writes,HP_writes=hp,
        snapshots=snapshots,calls=admitted,terminal=stamp(),
        translated_CPU_scene=True,source_or_native_outcomes_seeded=False,ROM_written=False,outputs_written=0),
        separators=(',',':')),flush=True)


if __name__=='__main__':main()
