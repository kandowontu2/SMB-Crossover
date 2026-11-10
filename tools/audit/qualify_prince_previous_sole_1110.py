"""Qualify the frozen Prince landing component; one compact receipt, no ROM."""
import argparse
from collections import Counter
import json
from pathlib import Path
from unittest.mock import patch

import check_prince_previous_sole_1110 as C

R,N,I,P=C.R,C.N,C.I,C.P
OUT=C.OUT
PROOF=OUT/'proof.json'


def call(seed,pc=0xbd22):
    model=N.fork(seed);events=Counter();native=N.NesMPU
    class Trace(native):
        def step(self):
            if self.memory is model and self.pc>=0x8000:
                tag=model.rawtags[(self.pc-0x8000)//8192]
                if (tag,self.pc)==(2,0xdadd):events['donor_contact']+=1
                if (tag,self.pc)==(254,I.address(model.bundle,'EnemyStomped')):events['native_stomp']+=1
            return super().step()
    with patch.object(N,'NesMPU',Trace):
        result=I.invoke(model,3,pc,(83,1,109,0x61))
    return model,result,dict(events)


def contacts(seed,entries):
    cases=[]
    variants=[('captured crossing',{},True),('previous equals head',{'prior':198},True),
        ('side contact',{'prior':210},False),('rising contact',{'prior':220},False),
        ('head already crossed',{'prior':200},False),('not at head yet',{'prior':180,'foot':190},False),
        ('Hard',{'CrossoverBehaviorVersion':1},False),('water',{'AreaType':0},False),
        ('current high',{'high':1},False),('previous high',{'prior_high':1},False),
        ('no admitted epoch',{'valid':0},False),('stale epoch',{'stale':1},False)]
    variants += [(f'protected native enemy {enemy}',{'enemy':enemy},False) for enemy in (7,10,12,13,18,21,45)]
    for name,changes,stomp in variants:
        model=N.fork(seed)
        for key,value in changes.items():
            if key in ('CrossoverBehaviorVersion','AreaType'):N.put(model,**{key:value})
            elif key=='prior':model.ram[2][entries['PreviousSole']+1-0xc000]=value
            elif key=='prior_high':model.ram[2][entries['PreviousHigh']+1-0xc000]=value
            elif key=='foot':model.ram[2][0x84]=value
            elif key=='high':model.ram[2][0x85]=value
            elif key=='valid':model.ram[2][0xaa]=value
            elif key=='stale':N.put(model,FrameCounter=N.get(model,'FrameCounter')^1)
            elif key=='enemy':model[I.address(model.bundle,'Enemy_ID')+1]=value
        actual,regs,events=call(model)
        assert events.get('native_stomp',0)==int(stomp),(name,events)
        assert events.get('donor_contact',0)==int(not stomp),(name,events)
        if stomp:
            assert actual.ram[2][0x6cf]==5 and N.get(actual,'Enemy_State',1)==4
        else:
            reference=N.fork(model)
            reference.ram[3][0x1d30:0x1d32]=(0xdadd).to_bytes(2,'little')
            old,oldregs,oldevents=call(reference)
            assert oldregs['regs']==regs['regs'],name
            assert bytes(old[3:11])==bytes(actual[3:11]),name
            assert bytes(old[0x15a:0x17b])==bytes(actual[0x15a:0x17b]),name
            assert bytes(old[0x200:0x800])==bytes(actual[0x200:0x800]),name
            assert bytes(old.ram[2])==bytes(actual.ram[2]),name
            assert old.rawtags==actual.rawtags and old.chr_latches==actual.chr_latches,name
        cases.append(dict(name=name,events=events,HP=actual.ram[2][0x6cf],
                          enemy_state=N.get(actual,'Enemy_State',1),minimum_SP=regs['minSP']))
    return cases


def lifecycle(seed,entries):
    cases=[]
    private=range(entries['PpCapturePreviousSole']-0xc000,entries['LandingLo']-0xc000)
    for name,values in (
        ('pause',{'GamePauseStatus':1}),('same admitted epoch',{}),
        ('powerup engine',{'GameEngineSubroutine':9}),('foreign owner',{'SelectedCharacter':0}),
        ('non gameplay',{'OperMode':0})):
        model=N.fork(seed);N.put(model,**values)
        before=(bytes(model.ram[2]),bytes(model.ram[3]))
        result=N.invoke(model,'HuMovement',a=83,x=71,y=109,p=0x61)
        assert bytes(model.ram[2])==before[0] and bytes(model.ram[3])==before[1],name
        cases.append(dict(name=name,carry=result['P']&1,private_RAM_exact=True))
    model=N.fork(seed)
    I.invoke(model,2,0xd98f,(83,71,109,0x61))
    assert model.ram[2][0xaa]==0 and model.ram[2][0xab]==0
    _,_,events=call(model)
    assert not events.get('native_stomp'),events
    cases.append(dict(name='retired stale sole',events=events))
    model=N.fork(seed)
    I.invoke(model,3,0xb3ef,(83,71,109,0x61))
    assert model.ram[2][0xaa]==0 and model.ram[2][0xab]==167
    _,_,events=call(model)
    assert not events.get('native_stomp'),events
    old_sole=model.ram[2][0x84:0x86]
    N.put(model,FrameCounter=(N.get(model,'FrameCounter')+1)&255)
    N.invoke(model,'HuMovement',a=83,x=0,y=109,p=0x61)
    assert model.ram[2][entries['PreviousSole']+1-0xc000]==old_sole[0]
    assert model.ram[2][entries['PreviousHigh']+1-0xc000]==old_sole[1]
    cases.append(dict(name='fresh life rejects stale sole then refreshes both bytes',events=events,
                      admitted_epoch=model.ram[2][0xa9],captured_sole=list(old_sole)))
    return cases


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args=cli.parse_args();assert args.output.resolve()==OUT
    target=OUT/'qualified-proof.json';assert not target.exists()
    proof=C.read(PROOF);assert proof['passed'] and proof['parent_SHA256']==C.PIN
    for path,expected in proof['bindings'].items():assert C.digest((R/path).read_bytes())==expected,path
    base=C.Start.W.bundle(C.ROM.read_bytes())
    before,_=P.Q.C.C.cold(base,38)
    updated,chunks,cookie,patches,layout=C.compose(base,before)
    assert C.digest(updated['raw'])==proof['expected_memory_only_SHA256']
    after,_=P.Q.C.C.cold(updated,38)
    poses=P.test_pose(before,after);print('Actual poses',poses,flush=True)
    menus=C.Start.Menu.inventory(updated['raw'])
    assert menus['distinct_named_entries']==menus['confirmable_named_entries']==100 and not menus['locked']
    print('All 100 current entries confirmable',flush=True)
    replay,held,(env,labels,seeds)=C.replay(updated)
    assert replay['result']=='landing-repaired' and len(seeds)==1
    contact_seed=seeds[0]
    matrix=contacts(contact_seed,layout['entries']);print('Contact matrix',matrix,flush=True)
    life=lifecycle(contact_seed,layout['entries']);print('Lifecycle',life,flush=True)
    seed=held[90];N.put(seed,NmiDisable=255)
    vectors=C.Camera.Funded.Life.stress('Actual Prince landing preHP-debit',seed,
        lambda m:C.Route.controls(env,m,labels,1)['regs'],
        [(2,layout['capture'][0],layout['entries']['LandingBank']+5),
         (2,C.HOOK,C.HOOK+3),(3,0xbd22,0xbd3e),(2,0xda1b,0xda69)])
    print('Actual IRQ/FF lag NMI',vectors,flush=True)
    result=dict(passed=True,parent_SHA256=C.PIN,
        expected_memory_only_SHA256=proof['expected_memory_only_SHA256'],ROM_written=False,Mesen_run=False,
        native_pending=True,initial_proof_SHA256=C.digest(PROOF.read_bytes()),poses=poses,
        menu=dict(distinct=100,confirmable=100,locked=[]),contacts=matrix,lifecycle=life,
        real_vectors=vectors,Prince_cookie=cookie.hex(),layout=layout,
        scope='Exact current c10b Prince component. Retains native velocity export, typed climb and camera, '
              'donor action and source no-bounce physics. Late Easy actual-sole crossing invokes host stomp '
              'before donor HP debit. Hard/water/hazard/noncrossing callbacks match original. '
              'CPU X891 repair only; later blind-right X897 side contact and full1-1 remain unqualified.',
        bindings={p.relative_to(R).as_posix():C.digest(p.read_bytes()) for p in
                  (Path(__file__),Path(C.__file__),C.SOURCE,C.ROM,PROOF)})
    target.write_text(json.dumps(result,separators=(',',':'))+'\n')


if __name__=='__main__':main()
