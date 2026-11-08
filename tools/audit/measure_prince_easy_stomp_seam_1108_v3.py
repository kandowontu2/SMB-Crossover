"""Verify the actual native Easy continuation, without proposing contact bytes."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import rebase_prince_deep_foot_1108_v1 as Q
A,N,I,O=Q.A,Q.N,Q.I,Q.O


def main():
    Q.M.STORAGE.preflight(private_root=O,reserved_bytes=12000,reserved_files=1,fresh=True)
    _,base,_,_=Q.image();_,seed,labels=A.first8(base)
    entry=labels['PpNativeContact'];assert entry==0xbd22
    addr=lambda name:I.address(base,name)
    policy=addr('GuestBodyStompAllowed');area=addr('AreaType')
    assert area==0x753
    native=N.NesMPU;calls=[]
    points={(3,entry):'source_contact',(254,addr('EnemyStomped')):'native_stomp',
            (254,addr('InjurePlayer')):'native_injury',(254,addr('HandlePECollisions')):'native_body',
            (2,labels['PpNativeRoute']):'source_route'}
    class Trace(native):
        def step(self):
            m=self.memory;bank=m.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else None
            if (bank,self.pc) in points:
                calls.append(dict(name=points[bank,self.pc],PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,
                                  P=self.p,tag=m[0x179],native_DY=N.get(m,'Player_Y_Speed'),
                                  engine=N.get(m,'GameEngineSubroutine'),HP=m.ram[2][0x6cf]))
            return super().step()
    rows=[]
    for key,easy,dy,enemy,stomp in [
        ('hard-source',False,9,6,False),('easy-descending',True,9,6,True),
        ('easy-rising',True,252,6,False),('easy-stationary',True,0,6,False),
        ('easy-descending-koopa',True,9,0,True),('easy-descending-spiny',True,9,18,False),
        ('easy-descending-plant',True,9,13,False)]:
        m=N.fork(seed);slot=0
        N.put(m,CrossoverBehaviorVersion=0 if easy else 1,ObjectOffset=slot,TimerControl=0,FrameCounter=0,
            Player_X_Position=48,Player_Rel_XPos=48,Player_Y_Position=176,Player_Rel_YPos=176,
            Player_Y_HighPos=1,Player_Y_Speed=dy,Player_State=2,AreaType=1,GuestBodyStompAllowed=0)
        for n,val in dict(Enemy_Flag=1,Enemy_ID=enemy,Enemy_State=0,Enemy_X_Position=48,Enemy_PageLoc=0,
            Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=2).items():m[addr(n)+slot]=val
        m.ram[2][0x6ee]=0;m.ram[2][0x6cf]=5;m.ram[2][0x616]=4;m.ram[2][0x617]=43
        assert N.get(m,'GameEngineSubroutine')==8
        N.invoke(m,'HuFullBox',a=83,x=0,y=0,p=0x21)
        for name in ['RelativeEnemyPosition','GetEnemyOffscreenBits','GetEnemyBoundBox']:N.invoke(m,name,a=83,x=slot,y=0,p=0x21)
        calls.clear();N.NesMPU=Trace
        try:out=N.invoke(m,'PlayerEnemyCollision',a=83,x=slot,y=0,p=0x21)
        finally:N.NesMPU=native
        events=list(calls);names=[c['name'] for c in events]
        assert names.count('native_body')==1,(key,events)
        if stomp:
            assert 'native_stomp' in names and m.ram[2][0x6cf]==5,(key,names,m.ram[2][0x6cf],out)
            assert N.get(m,'Player_Y_Speed')>=0x80 and N.get(m,'Enemy_State',slot)!=0
        else:
            assert m.ram[2][0x6cf]==0,(key,events,m.ram[2][0x6cf])
        rows.append(dict(case=key,explicit_CPU_only_enemy_overlap_fixture=True,events=events,
            HP=m.ram[2][0x6cf],source_action=m.ram[2][0x616],native_Y_speed=N.get(m,'Player_Y_Speed'),
            enemy_state=N.get(m,'Enemy_State',slot),CPU=out['CPU']))
    q=dict(passed=True,measurement_only=True,ROM_written=False,Mesen_run=False,
        input_memory_SHA256=Q.sha(base['raw']),cases=rows,
        conclusion='Actual current native Easy already accepts positive native DY for the tested ordinary overlaps, while Hard and Easy non-descending/hazard cases call original unarmed contact. No body bypass is needed to enable that resolver. Existing X5BounceProfile excludes raw38; native-only velocity does not constitute a source bounce contract.',
        required_integration=['Inspect actual failing native contact behavior, speed and source tag before changing anything.',
            'Preserve Hard, original weapon/body/side/hazard behavior. If an actually descending source frame lost its native DY before enemy contact, use a narrowly proven source-foot crossing guard, not unconditional CLC.',
            'No injected code or ROM output in this fixture.'],
        bindings={p.relative_to(R).as_posix():Q.M.sha(p) for p in [Path(__file__),O/'landing-contract.json',R/'src/collision.s',R/'src/x5_bounce.s',R/'src/little_mac_core.s']})
    (O/'easy-contact-seam.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))


if __name__=='__main__':main()
