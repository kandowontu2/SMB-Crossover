"""Finish the genuine native floatey-number score consumer, no full Main."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v3 as T
from check_tmnt_render_oa import address,location
C=T.C;make=T.make;put=T.put;get=T.get;setv=T.setv;actor=T.actor;run=T.run;sha=T.sha
P=R/'build/final-fantasy-host-combat-v2';O=R/'build/final-fantasy-host-combat-controls-v5'

def score(b):
    native=T.qualified(C.E.P/'candidate.nes')
    physical=(location(native,'FloateyNumbersCore')-16)//8192
    rows=[]
    for kind,x,player in itertools.product(['Goomba','HammerBro','PiranhaPlant','Bowser'],range(6),range(2)):
        m=make(b);actor(m,x=x,kind=address(b,kind),px=144,y=160)
        put(m,FfDamage=75,WorldNumber=7,ObjectOffset=5,DuplicateObj_Offset=(x+1)%6,CurrentPlayer=player,VRAM_Buffer1_Offset=0)
        for n,length in [('DigitModifier',6),('Player1ScoreDisplay',6),('Player2ScoreDisplay',6)]:
            for i in range(length):setv(m,n,0,i)
        setv(m,'MmEnemyHealthLo',75,x)
        run(m,'FfHostDamage',x=x)
        # This is the genuine native enemy-loop caller's index contract.
        for step in range(8):
            setv(m,'ObjectOffset',x)
            c,tr=T.direct(m,'FloateyNumbersCore',x=x,bank=physical|128)
            assert c.x==x,('native score restores actual actor X',kind,x,step,c.x)
        want=[0]*6;want[3 if kind in ['HammerBro','Bowser']else 4]=5 if kind=='Bowser'else 2 if kind=='PiranhaPlant'else 1
        actual=[get(m,'Player1ScoreDisplay'if player==0 else'Player2ScoreDisplay',i)for i in range(6)]
        other=[get(m,'Player2ScoreDisplay'if player==0 else'Player1ScoreDisplay',i)for i in range(6)]
        assert actual==want and other==[0]*6,('actual native score digits',kind,x,player,actual,want,other)
        assert all(get(m,'DigitModifier',i)==0 for i in range(6))
        rows.append(dict(kind=kind,slot=x,player=player,native_tens_digits=actual))
    return dict(cases=len(rows),actual_FloateyNumbersCore_AddToScore_DigitsMath_HUD_route=True,
                own_score_once_other_player_unchanged=True,rows=rows)

def lower_guards(b):
    rows=[]
    for name,owner,x,p in itertools.product(['FfHostTarget','FfHostDamage','FfHostContact'],[0,9,21,23,32,255],[0,5,6,255],C.flags()):
        m=make(b);put(m,SelectedCharacter=owner,FfDamage=255,FfAction=1)
        actor(m);m.raw_page(1,3);setv(m,'CurrentBank',3);before=T.state(m)
        c,tr=T.direct(m,name,a=255,x=x,y=167,p=p)
        assert not c.p&1 and T.state(m)==before and c.x==x and c.y==167,(name,owner,x,p)
        rows.append([name,owner,x,p])
    invalid=0
    for x,p in itertools.product([6,7,255],C.flags()):
        m=make(b);m.raw_page(1,3);setv(m,'CurrentBank',3);before=T.state(m)
        c,tr=T.direct(m,'FfHostNewEnemy',a=89,x=x,y=167,p=p)
        assert (c.a,c.x,c.y,c.p)==(89,x,167,p)and T.state(m)==before
        invalid+=1
    return dict(foreign_lower_entry_cases=len(rows),own_invalid_reuse_APXY64_cases=invalid,
                no_application_state_writes=True)

def flash_observation(b):
    m=make(b);actor(m,kind=address(b,'HammerBro'));put(m,FfDamage=25)
    run(m,'FfHostDamage');values=[get(m,'MmEnemyFlash')]
    for _ in range(3):run(m,'FfHostWeapons');values.append(get(m,'MmEnemyFlash'))
    assert values==[2,2,2,2]
    return dict(observed_native_flash=values,
                existing_contract='Surviving damage publishes native flash2. This component does not age it; the eventual public hook must give native feedback aging one actual active owner. Current native renderer has no FF flash owner. No native flash visuals claimed.',
                native_audio='Native SFX queue requests are qualified; APU/music waveform and ISR/audio installation are outside this component.')

def main():
    assert not O.exists();O.mkdir();b=C.bundle(P);d=dict(passed=False,native=False,host_Main=False,checks={},failures={})
    p=json.loads((P/'build-proof.json').read_text())
    for f,h in p['bindings'].items():assert sha(f)==h,f
    for n,fn in [('score',score),('lower_guards',lower_guards),('feedback_ownership',flash_observation)]:
        try:d['checks'][n]=fn(b)
        except Exception as e:d['failures'][n]=dict(error=repr(e),traceback=traceback.format_exc())
    d['passed']=not d['failures']
    d['bindings']={**p['bindings'],str((P/'build-proof.json').resolve()):sha(P/'build-proof.json'),
                   str(Path(__file__).resolve()):sha(__file__),str(Path(T.__file__).resolve()):sha(T.__file__),str(Path(C.__file__).resolve()):sha(C.__file__)}
    (O/'controls.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=d['passed'],checks=list(d['checks']),failures=d['failures'])))
    assert d['passed']
if __name__=='__main__':main()
