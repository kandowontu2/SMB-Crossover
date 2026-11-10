"""Same-size bridge mask; frozen70aa workers and physics remain byte-exact."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import tempfile

import check_manual_roster_paired_irq_1110 as V

F,I,P,N,R=V.F,V.I,V.P,V.N,V.R
PROOF=I.OUT/'ff-foot-proof.json'
CURRENT=R/'build/manual-roster-native-1110/candidate.nes'
CURRENT_PIN='27d2cefbe529547e7e9546c78cd0a4b1bde510b9124f6a56afa9c9cc616b751a'
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()


def image(q):
    base=I.BASE.read_bytes();assert I.SHA(base)==I.PIN
    old=P.install(base,q['patches']);assert I.SHA(old)==q['expected_memory_only_SHA256']
    source='ROSTER_INGRESS=1\n'+''.join(f'{name}=${q["labels"][name]:04x}\n'
        for name in ('ManualRosterDispatch','ManualRosterSkipEmpty'))+I.INGRESS.read_text()
    new_source=P.replace_one(source,'    cmp #22\n    bcc BridgeDone',
        '    and #$12\n    beq BridgeDone')
    with tempfile.TemporaryDirectory(dir=I.OUT) as tmp:
        work=Path(tmp);outputs=[]
        for name,text in (('old',source),('mask',new_source)):
            src=work/f'{name}.s';src.write_text(text)
            code,labels=P.link(work,src,(('ROSTER_FIXED_BRIDGE',0x837b,31),('ROSTER_DISPATCH',0xb134,12)))
            assert len(code)==43 and labels['RosterFireballBridgeEnd']==0x839a
            assert old[P.at(26,0xb134):P.at(26,0xb134)+12]==code[31:]
            outputs.append(code[:31])
        a,b=outputs;offset=P.at(126,0x837b)
        assert old[offset:offset+31]==a
        assert [i for i,(x,y) in enumerate(zip(a,b)) if x!=y]==[11,12,13]
        assert a[11:15]==bytes.fromhex('c916900f') and b[11:15]==bytes.fromhex('2912f00f')
        patch=P.L.patch(old,offset+11,b[11:14],
            'Same3B source bridge predicate excludesMini41 while retaining22/29/34; HpCount>0 always enters')
    return base,old,P.install(old,[patch]),patch


def parity(old,new,labels):
    bundles=[F.bundle(raw,labels) for raw in (old,new)]
    result={}
    for owner in (*range(38),41,42):
        seeds=[P.scene(b,owner) for b in bundles];cycles=Counter()
        for held in (0,)*12+(1,)*16+(0,)*12+(0x20,0,8,0):
            a,b=[P.frame(m,held) for m in seeds]
            first,second=[P.memory(m) for m in seeds]
            assert first==second,(owner,held,'publicstate',V.diagnostic(first,second))
            assert all(a[k]==b[k] for k in 'AXYP'),(owner,held,a,b)
            cycles[b['CPU']-a['CPU']]+=1
        result[str(owner)]=dict(updates=sum(cycles.values()),CPU_delta=dict(cycles))
        print('Mask complete GameCore parity',owner,result[str(owner)],flush=True)
    return result


def predicates(old,new,labels):
    bundles=[F.bundle(raw,labels) for raw in (old,new)];result={}
    for b in bundles:b['syms']['RosterPredicateEntry']=dict(val=str(0x8383),seg='roster_fixed')
    for owner in range(45):
        states=[];regs=[]
        for b in bundles:
            m=P.scene(b,34) if owner==34 else N.fresh(b)
            N.put(m,SelectedCharacter=owner,HpCount=0,OperMode=1,OperMode_Task=3,
                GameEngineSubroutine=9,CurrentPlayer=0,SavedJoypadBits=0,TimerControl=0)
            maps=tuple(m.rawtags)
            z=N.invoke(m,'RosterPredicateEntry',a=83,x=17,y=91,p=0x65)
            assert maps==tuple(m.rawtags)
            states.append((tuple(bytes(row) for row in m.ram),P.actors(m),P.fields(m,P.PLAYER_FIELDS)))
            regs.append({k:z[k] for k in 'AXYP'})
        assert states[0]==states[1],(owner,'isolated predicate writes')
        result[str(owner)]=dict(old=regs[0],new=regs[1],full_4bank_RAM_actors_player_exact=True)
    return result


def main():
    q=json.loads(PROOF.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    base,old,new,patch=image(q)
    print('Source mask image',I.SHA(new),patch,flush=True)
    current=CURRENT.read_bytes();assert I.SHA(current)==CURRENT_PIN
    expected=P.install((R/'build/remaining-roster-native-1110/candidate.nes').read_bytes(),q['patches'])
    assert current==expected
    current_new=P.install(current,[patch])
    regular=parity(current,current_new,q['labels'])
    isolated=predicates(current,current_new,q['labels'])
    baseline=I.regular(base,new,q['labels'])
    assert baseline[0]['native_CPU_overhead']=={0:44}
    assert baseline[5]['native_CPU_overhead']=={0:44}
    assert baseline[41]['native_CPU_overhead']=={0:44}
    inputs=I.input_cases(F.bundle(new,q['labels']))
    births=I.actual_frames(F.bundle(new,q['labels']),new)
    result=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        parent_SHA256=I.SHA(old),expected_memory_only_SHA256=I.SHA(new),
        ff_foot_proof_SHA256=SHA(PROOF),patches=[patch],
        current_roster_parent_SHA256=CURRENT_PIN,current_roster_mask_SHA256=I.SHA(current_new),
        all_owner_complete_GameCore_parity=regular,baseline74fde=baseline,
        all45_isolated_predicate=isolated,
        desired_input_cases=inputs,actual_GameCore_births=births,
        predicate=dict(mask=18,HpCount_positive_unconditionally_admitted=True,
            admits=[o for o in range(45) if o&18],rejects=[o for o in range(45) if not o&18]),
        scope='Complete44update GameCore publicstate andAXYP exact for raw0..37/41/42; cold prototype38/40 require their separately verified long native startup, no borrowed-body scene used. Isolated actual predicate allraw0..44 has exact4bankRAM/actors/player and records ABI flag changes. Exact baseline74fde cycles for0/5/41. All10variants/bothpads input and actualbirth checks. Only3fixedROMbytes changed; frozen helper workers/ctor/footgate byte-exact.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in
            (Path(__file__),PROOF,Path(F.__file__),I.INGRESS,Path(I.__file__),R/'src/game.s',CURRENT)})
    (I.OUT/'bridge-mask-proof.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
