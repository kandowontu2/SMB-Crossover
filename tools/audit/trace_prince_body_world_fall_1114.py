"""Passive actual-control health/fall trace; no gameplay state writes."""
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_body_world_1114 as Game

C,P,N=Game.C,Game.P,Game.N


def run(parent):
    raw,info=C.proposal(parent);model,opening=Game.cold(raw)
    bus=type(model);cpu=N.NesMPU;frame=P.Frames.frame
    context=dict(pc=0,frame=0,cpu=None);health=[];landings=[];previous=None;native_events=[]
    targets={}
    for name in('KillPlayer','InjurePlayer','PlayerEnemyCollision','EnemyToPlayerCollision','MarioSourceKillPlayer'):
        if name in model.bundle['syms']:
            targets[P.W.address(model.bundle,name),((P.W.location(model.bundle,name)-16)//8192)|128]=name
    labels=json.loads((C.R/'build/prince-actor-1101-v1/native-labels-v153.json').read_text())
    for name,pc in labels.items():
        if any(k in name.lower()for k in('kill','hurt','damage','fatal','death'))or name in('PpNativeContact','PpOriginalDefenderContact','PpOriginalIncoming'):
            pc=int(pc,0)if isinstance(pc,str)else pc
            if 0xa000<=pc<0xe000:targets[pc,3 if pc<0xc000 else 2]=name
    def state(m):
        s=m.ram[2]
        actors=[]
        for slot in range(6):
            if N.get(m,'Enemy_Flag',slot):actors.append(dict(slot=slot,id=N.get(m,'Enemy_ID',slot),flag=N.get(m,'Enemy_Flag',slot),state=N.get(m,'Enemy_State',slot),x=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot),y=N.get(m,'Enemy_Y_Position',slot)))
        c=context['cpu'];regs=None if c is None else dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,
            stack=[m[0x100+((c.sp+i)&255)]for i in range(1,17)])
        return dict(frame=context['frame'],PC=hex(context['pc']),maps=m.rawtags[:],
            registers=regs,engine=N.get(m,'GameEngineSubroutine'),ObjectOffset=N.get(m,'ObjectOffset'),
            lives=N.get(m,'NumberofLives'),power=N.get(m,'PlayerStatus'),star=N.get(m,'StarInvincibleTimer'),
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
            sx=int.from_bytes(s[0x60f:0x611],'little'),sy=s[0x611],action=s[0x616],pose=s[0x617],mode=s[0x618],
            foot=int.from_bytes(s[0x84:0x86],'little'),old_foot=int.from_bytes(s[0x86:0x88],'little'),
            delta=s[0x88],origin=int.from_bytes(s[0x89:0x8b],'little'),
            fall_raw=list(s[0x6c0:0x6d0]),query=int.from_bytes(s[0x78:0x7a],'little'),
            surface=int.from_bytes(s[0x7f:0x81],'little'),row=s[0x7c],current_row=s[0x83],
            baseline=int.from_bytes(s[0x9b:0x9d],'little'),health=s[0x6cf],sword=s[0x6ee],
            guard_uid=s[0x61c],guard_hp=s[0x6d0],guard_dead=s[0x6de],actors=actors)
    class Bus(bus):
        def __setitem__(self,at,value):
            if self is model and at==0xc6cf and self.rawtags[2]==2 and value!=self.ram[2][0x6cf]:
                health.append(dict(before=self.ram[2][0x6cf],after=value,state=state(self)))
            return super().__setitem__(at,value)
    class CPU(cpu):
        def step(self):
            context['pc']=self.pc;context['cpu']=self
            if self.memory is model and self.pc>=0x8000:
                name=targets.get((self.pc,model.rawtags[(self.pc-0x8000)//8192]))
                if name:
                    native_events.append(dict(name=name,state=state(model)))
                    if len(native_events)>40:native_events.pop(0)
            return super().step()
    def advance(m,*a,**kw):
        nonlocal previous
        context['frame']+=1;out=frame(m,*a,**kw)
        if m is model:
            s=m.ram[2];x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
            key=(s[0x618],s[0x616],s[0x6cd],s[0x6ce],s[0x6cf])
            if 590<=x<=720 and key!=previous:
                landings.append(state(m));previous=key
                if len(landings)>48:landings.pop(16)
        return out
    model.__class__=Bus
    try:
        with patch.object(N,'NesMPU',CPU),patch.object(P.Frames,'frame',advance):q=Game.route(raw,model,mode='pits-intuitive')
    finally:model.__class__=bus
    return dict(composition=info,opening=opening,result=q,health_writes=health,fall_states=landings,native_damage_events=native_events,
        passive_observer=True,gameplay_seeds=0,outputs=0,Mesen=False)


if __name__=='__main__':
    q=run(Game.Factory.ROM.read_bytes());digest=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    first=q['health_writes'][0];frame=first['state']['frame']
    events=[x for x in q['native_damage_events']if x['state']['frame']==frame and x['name']not in('PpNativePitDeath','PpNativeDeferredKill')]
    result=q['result']
    print(json.dumps(dict(ROM_SHA256=q['composition']['candidate_SHA256'],
        passed=result['passed'],phase=result['phase'],updates=result['logical_updates'],terminal=result['terminal'],
        route_receipt=result['receipt_SHA256'],first_HP_write=first,total_HP_writes=len(q['health_writes']),
        same_Main_native_contact_entries=events,full_trace_SHA256=digest,
        passive_observer=True,gameplay_seeds=0,outputs=0,Mesen=False),separators=(',',':')),flush=True)
