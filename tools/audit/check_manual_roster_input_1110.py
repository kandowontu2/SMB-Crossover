"""Source-funded WWF/FF manual input through the native gameplay bridge."""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import tempfile

import check_manual_wide_horizontal_1110 as W

P,N,R=W.P,W.N,W.R
OUT=R/'build/manual-roster-platform-1110'
BASE=R/'build/manual-wide-floor-native-1110/candidate.nes'
PIN='74fde1dba64b17f7f9028c3da1d5948c041e9af11fb37fca4d241d834724318e'
SOURCE=R/'tools/reference/manual_roster_input_1110.s'
INGRESS=R/'tools/reference/manual_roster_ingress_1110.s'
SHA=lambda raw:sha256(raw).hexdigest()


def build(out):
    raw=BASE.read_bytes(); assert SHA(raw)==PIN
    values,hpc,hreader,hthresholds=W.table(W.BASE.read_bytes())
    data=W.DATA.read_text().split('HpSineVertical:\n',1)[1]
    vertical=bytes(int(v) for line in data.splitlines() if '.byte' in line
                   for v in line.split('.byte',1)[1].strip().split(','))
    assert len(vertical)==256 and max(vertical)==75 and vertical==bytes(sorted(vertical))
    vpc=hpc+256
    assert raw[P.at(26,vpc):P.at(26,vpc)+256]==vertical
    vopcode=b'\xb9'+vpc.to_bytes(2,'little')
    bank=raw[P.at(26,0xa000):P.at(26,0xa000)+8192]
    assert bank.count(vopcode)==1
    vreader=0xa000+bank.index(vopcode)
    vthresholds=bytes([0]+[vertical.index(i)-1 for i in range(1,76)])
    b=P.L.M.bundle(raw)
    defs='NativeMotionResume=$ae6e\n'+''.join(f'{n}=${P.L.M.address(b,n):04x}\n' for n in ('HpTemp2','HpSineIndex'))
    original=W.SOURCE.read_text()
    roster=P.replace_one(original,'    cmp #34\n    beq ManualWideHorizontal',
        '    cmp #34\n    beq ManualWideHorizontal\n    cmp #22\n    beq ManualWideHorizontal\n    cmp #29\n    beq ManualWideHorizontal')
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        work=Path(tmp)
        (work/'thresholds.bin').write_bytes(hthresholds)
        (work/'vertical-thresholds.bin').write_bytes(vthresholds)
        def paths(s):
            for name in ('thresholds.bin','vertical-thresholds.bin'):
                s=s.replace('"'+name+'"','"'+(work/name).as_posix()+'"')
            return s
        oldsrc=work/'old.s'; oldsrc.write_text(defs+paths(original))
        old,ol=P.link(work,oldsrc,(('HORIZONTAL',hpc,256),))
        assert len(old)==167 and raw[P.at(26,hpc):P.at(26,hpc)+256]==old.ljust(256,b'\xea')
        oldgate=work/'old-ingress.s';oldgate.write_text('ROSTER_INGRESS=0\n'+INGRESS.read_text())
        old_ingress,oi=P.link(work,oldgate,(('ROSTER_FIXED_BRIDGE',0x837b,31),('ROSTER_DISPATCH',0xb134,12)))
        assert len(old_ingress)==43 and oi['RosterFireballBridgeEnd']==0x839a and oi['RosterDispatcherEnd']==0xb140
        assert raw[P.at(126,0x837b):P.at(126,0x837b)+31]==old_ingress[:31]
        assert raw[P.at(26,0xb134):P.at(26,0xb134)+12]==old_ingress[31:]
        src=work/'roster.s'; src.write_text('ROSTER_INGRESS=1\n'+defs+paths(roster)+'\n'+paths(SOURCE.read_text())+'\n'+INGRESS.read_text())
        code,labels=P.link(work,src,(('HORIZONTAL',hpc,175),
            ('ROSTER_INPUT_HEAD',hpc+175,81),('ROSTER_VERTICAL',vpc,256),
            ('ROSTER_FIXED_BRIDGE',0x837b,31),('ROSTER_DISPATCH',0xb134,12)))
        sizes=(labels['ManualHorizontalEnd']-hpc,
               labels['ManualRosterInputHeadEnd']-(hpc+175),
               labels['ManualRosterInputEnd']-vpc)
        assert sizes[0]==175 and sizes[1]<=81 and sizes[2]<=256
        assert len(code)==sum(sizes)+43
    patches=[]; at=0
    for pc,size,capacity in zip((hpc,hpc+175,vpc),sizes,(175,81,256)):
        patches.append(P.L.patch(raw,P.at(26,pc),code[at:at+size].ljust(capacity,b'\xea'),
            'Exact native sine table factoring funds raw22/29 manual input'))
        at+=size
    patches.extend((P.L.patch(raw,P.at(126,0x837b),code[at:at+31],
        'Same31B native bridge admits selected22+; old low raw fast path retained'),
        P.L.patch(raw,P.at(26,0xb134),code[at+31:at+43],
        'Manual input before retained Karnov/native helper dispatcher; no empty helper scratch update')))
    old_reader=raw[P.at(26,hreader):P.at(26,hreader)+3]
    assert old_reader==b'\x20'+ol['ManualSineDecode'].to_bytes(2,'little')
    patches.append(P.L.patch(raw,P.at(26,hreader),b'\x20'+labels['ManualSineDecode'].to_bytes(2,'little'),'Relocated exact horizontal decoder'))
    patches.append(P.L.patch(raw,P.at(26,vreader),b'\x20'+labels['RosterVerticalDecode'].to_bytes(2,'little'),'Exact vertical decoder'))
    new=P.install(raw,patches)
    return raw,new,patches,labels,dict(horizontal=hpc,vertical=vpc,
        horizontal_reader=hreader,vertical_reader=vreader,sizes=sizes,
        vertical_decoder=labels['RosterVerticalDecodeEnd']-vpc),vertical


def bundle(raw,labels):
    b=P.L.M.bundle(raw)
    b['segs']['roster_manual']=dict(start=str(0xa000),ooffs=str(P.at(26,0xa000)))
    b['segs']['manual_ctor']=dict(start=str(0xa000),ooffs=str(P.at(64,0xa000)))
    b['segs']['roster_fixed']=dict(start=str(0x8000),ooffs=str(P.at(126,0x8000)))
    for n,v in labels.items():
        b['syms'][n]=dict(val=str(v),seg='roster_fixed' if n.startswith('RosterFireballBridge') else 'roster_manual')
    b['syms']['ManualPlatform']=dict(val=str(0xb378),seg='manual_ctor')
    b['syms']['HpNativePlatformDispatch']=dict(val=str(0xae40),seg='roster_manual')
    assert raw[P.at(26,0xab99):P.at(26,0xab99)+5]==bytes.fromhex('a2028ed473')
    b['syms']['HpConfigure']=dict(val=str(0xab99),seg='roster_manual')
    return b


def decoder(b,vertical):
    seed=N.fresh(b); count=0; worst=0
    for index,p in product(range(256),(0x20,0x21,0x6d,0xa5)):
        m=P.slim_fork(seed)
        m[P.L.M.address(b,'HpSineIndex')]=index
        z=N.invoke(m,'RosterVerticalDecode',a=91,x=2,y=173,p=p)
        assert z['A']==vertical[index] and z['Y']==173
        assert z['P']&0x4d==p&0x4d,(index,p,z)
        count+=1
        worst=max(worst,z['CPU'])
    return dict(cases=count,maximum_cycles_if_reported=worst)


def ram_audit(raw):
    names=('HpAxisFlags','HpAxis','HpDeferred')
    b=P.L.M.bundle(raw)
    uses={n:[] for n in names}
    for path in [*sorted((R/'src').glob('*.s')),*sorted((R/'src').glob('*.inc')),
                 *sorted((R/'tools/reference').glob('*.s')),*sorted((R/'tools/reference').glob('*.inc'))]:
        if path==SOURCE: continue
        for i,line in enumerate(path.read_text(errors='replace').splitlines(),1):
            for n in names:
                if __import__('re').search(r'\b'+n+r'\b',line):
                    uses[n].append([str(path.relative_to(R)),i,line.strip()])
    for n in names:
        assert len(uses[n])==1 and uses[n][0][0]=='src\\crossover_helper_ram.s',uses[n]
        assert 'ref' not in b['syms'][n]
    opcodes={0xad,0xbd,0xb9,0xae,0xbe,0xac,0xbc,0x8d,0x9d,0x99,0x8e,0x8c,
             0xcd,0xdd,0xd9,0xee,0xfe,0xce,0xde,0x2c,0x2d,0x0d,0x4d}
    direct={}
    for target in range(0x73d1,0x73d4):
        needle=target.to_bytes(2,'little')
        hits=[i for i in range(16,len(raw)-2) if raw[i] in opcodes and raw[i+1:i+3]==needle]
        assert not hits,(target,hits)
        direct[hex(target)]=0
    return dict(named_fields=uses,whole_ROM_absolute_operand_candidates=direct,
        declared_slab=[0x7382,0x73dd],reset='Existing HpConfigure clears full91bytes.',
        adjacent_indexed_owners='Descriptor73C8+X<=8, seven pointers73BA/73C1+X<=6, sound-test73C5+X<=11 all stop73D0. Apparent VIC73CE indexed read is an unaligned hit across LDY5D74; DEC5D73.',
        scope='Conditional raw22/29 lease of retired helper bytes; no RAM growth/repacking; source tests elsewhere proposing old Celeste scratch are historical and not emitted here.')


def input_cases(b):
    seed=N.fresh(b)
    N.put(seed,SelectedCharacter=22,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
          GamePauseStatus=0,TimerControl=0,MmDeathFlag=0,DisableScreenFlag=0,
          Player_X_Position=100,Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1,
          PlayerFacingDir=2,CurrentPlayer=0)
    results={}
    for owner,variant,player in [(o,v,p) for o,count in ((22,4),(29,6)) for v in range(count) for p in (0,1)]:
        m=P.slim_fork(seed)
        N.put(m,SelectedCharacter=owner,CurrentPlayer=player,FfVariant=variant,FmGroups=variant)
        pad=P.L.M.address(b,'SavedJoypadBits')+player
        births=[]
        def tick(held):
            m[pad]=held
            m[pad^1]=0 if pad in (0xdc,0xdd) else m[pad^1]
            before=P.actors(m)
            scratch=bytes(m[i] for i in range(3,11)); maps=tuple(m.rawtags)
            z=N.invoke(m,'ManualRosterInput',a=83,x=17,y=91,p=0x65)
            assert (z['A'],z['X'],z['Y'],z['P']&0xcf)==(83,17,91,0x65&0xcf)
            assert scratch==bytes(m[i] for i in range(3,11)) and maps==tuple(m.rawtags)
            changed=[i for i,(a,c) in enumerate(zip(before,P.actors(m))) if a!=c]
            if changed: births.extend(changed)
        tick(0);tick(0x28)
        assert len(W.D.owned(m,0x25))==1 and len(W.D.owned(m))==1
        vertical_slot=W.D.owned(m,0x25)[0][0]
        vrow=P.actors(m)[vertical_slot]
        assert vrow[:8]==(1,0x25,0x41,92,1,208,1,5),vrow
        for _ in range(30):tick(0x28)
        assert len(births)==1
        tick(0x24)
        assert len(W.D.owned(m))==2
        hslot=W.D.owned(m,0x28)[0][0]
        hrow=P.actors(m)[hslot]
        assert hrow[:8]==(1,0x28,0x42,124,1,208,1,5),hrow
        assert P.actors(m)[vertical_slot]==vrow
        for _ in range(30):tick(0x24)
        assert len(births)==2
        # Replacing at a new player X changes only the matching axis slot.
        N.put(m,Player_X_Position=132)
        tick(0);tick(0x24)
        assert P.actors(m)[vertical_slot]==vrow and W.D.owned(m,0x28)[0][0]==hslot
        assert P.actors(m)[hslot][3:5]==(156,1)
        hrow=P.actors(m)[hslot]
        tick(0);tick(0x28)
        assert W.D.owned(m,0x25)[0][0]==vertical_slot and P.actors(m)[hslot]==hrow
        results[f'{owner}:{variant}:P{player+1}']=dict(input_updates=68,
            vertical_slot=vertical_slot,horizontal_slot=hslot,held_no_repeat=True,independent_replacement=True)
    return results


def pressure_guards(b):
    seed=N.fresh(b)
    N.put(seed,SelectedCharacter=22,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
          GamePauseStatus=0,TimerControl=0,MmDeathFlag=0,Player_X_Position=100,
          Player_PageLoc=1,Player_Y_Position=176,Player_Y_HighPos=1,CurrentPlayer=0)
    def tick(m,held):
        N.put(m,SavedJoypadBits=held)
        return N.invoke(m,'ManualRosterInput',a=83,x=17,y=91,p=0x65)
    pressure={}
    for owner in (22,29):
        m=P.slim_fork(seed);N.put(m,SelectedCharacter=owner)
        for slot in range(6):P.set_slot(m,slot,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0)
        tick(m,0);tick(m,0x28);tick(m,0x24)
        assert tuple(m[i] for i in (0x73d2,0x73d3))==(128,128) and not W.D.owned(m)
        N.invoke(m,'EraseEnemyObject',x=2);tick(m,0)
        assert m[0x73d2]==3 and m[0x73d3]==128 and len(W.D.owned(m,0x25))==1
        before=P.actors(m)[2]
        N.invoke(m,'EraseEnemyObject',x=3);tick(m,0)
        assert m[0x73d2]==3 and m[0x73d3]==4 and len(W.D.owned(m))==2
        assert P.actors(m)[2]==before
        N.invoke(m,'HpConfigure')
        assert bytes(m[i] for i in range(0x73d1,0x73d4))==bytes(3)
        pressure[owner]=dict(independent_pending_queues=True,existing_configure_reset=True)
    guards=0
    for owner,field,value in product((22,29),
            ('OperMode','OperMode_Task','GameEngineSubroutine','GamePauseStatus','TimerControl','MmDeathFlag'),(1,2)):
        m=P.slim_fork(seed);N.put(m,SelectedCharacter=owner)
        invalid={'OperMode':0,'OperMode_Task':2,'GameEngineSubroutine':9,
                 'GamePauseStatus':1,'TimerControl':value,'MmDeathFlag':value}
        N.put(m,**{field:invalid[field]})
        m[0x73d1]=128;m[0x73d2]=m[0x73d3]=128
        tick(m,0x28)
        assert not W.D.owned(m) and (m[0x73d2],m[0x73d3])==(0,0)
        guards+=1
    foreign=0
    for owner in tuple(range(43)):
        if owner in (22,29):continue
        m=P.slim_fork(seed);N.put(m,SelectedCharacter=owner)
        m[0x73d1]=43;m[0x73d2]=91;m[0x73d3]=128
        before=P.actors(m);tick(m,0x28)
        assert P.actors(m)==before and tuple(m[i] for i in range(0x73d1,0x73d4))==(43,91,128)
        foreign+=1
    return dict(pressure=pressure,inactive_cases=guards,foreign_cases=foreign)


def regular(base,new,labels):
    before,after=bundle(base,labels),bundle(new,labels)
    original=P.memory
    def canonical(m):
        result=list(original(m))
        if N.get(m,'SelectedCharacter') in (22,29):
            slab=bytearray(result[2]);slab[0x13d1:0x13d4]=bytes(3);result[2]=bytes(slab)
            banks=list(result[5]);slab=bytearray(banks[0]);slab[0x13d1:0x13d4]=bytes(3)
            banks[0]=bytes(slab);result[5]=tuple(banks)
        return result
    P.memory=canonical
    try:
        result={}
        for owner in (0,5,22,23,25,29,34,41,42):
            seeds=[P.scene(b,owner) for b in (before,after)]
            result[owner]=P.regular_parity(seeds,owner,base,new)
            print('regular',owner,result[owner],flush=True)
        return result
    finally:P.memory=original


def actual_frames(b,raw):
    tail=raw[P.at(64,0xbfdd):P.at(64,0xbfdd)+35]
    assert tail.count(bytes.fromhex('e88a60'))==1
    birthpc=0xbfdd+tail.index(bytes.fromhex('e88a60'))
    original=N.NesMPU;births=[]
    class Trace(original):
        def step(self):
            m=self.memory
            if self.pc==birthpc and m.rawtags[1]==0xc0:
                row=P.actors(m)[self.x]
                px=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                py=N.get(m,'Player_Y_Position')
                horizontal=row[1]==0x28
                assert P.world(row,3,4)==max(0,px+(24 if horizontal else -8))
                assert row[5]==py+32 and row[7]==5
                births.append(dict(slot=self.x,kind=row[1],left=P.world(row,3,4),top=row[5],player_x=px,player_y=py))
            return original.step(self)
    N.NesMPU=Trace
    try:
        results={}
        for owner,count in ((22,4),(29,6)):
            for variant in range(count):
                m=P.scene(b,owner)
                if variant:
                    N.put(m,FfVariant=variant,FmGroups=variant,DisableScreenFlag=1,
                          Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
                    N.invoke(m,'InitScreen')
                    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,GameEngineSubroutine=8)
                start=len(births)
                for held in (0,0x28)+(0x28,)*8+(0,0x24)+(0x24,)*8:
                    P.frame(m,held)
                got=births[start:]
                assert len(got)==2 and got[0]['kind']==0x25 and got[1]['kind']==0x28,(owner,variant,got)
                assert len(W.D.owned(m))==2,(owner,variant,P.actors(m))
                results[f'{owner}:{variant}']=dict(updates=20,births=got)
                print('actual GameCore input',owner,variant,got,flush=True)
        return results
    finally:N.NesMPU=original


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fit',action='store_true');a=ap.parse_args()
    OUT.mkdir(exist_ok=True)
    raw,new,rows,labels,layout,vertical=build(OUT)
    print('source fit',layout,'memory image',SHA(new),flush=True)
    if a.fit:return
    audit=ram_audit(raw)
    b=bundle(new,labels)
    dec=decoder(b,vertical);print('vertical decoder',dec,flush=True)
    inputs=input_cases(b);print('input variants/players',len(inputs),flush=True)
    guards=pressure_guards(b);print('queues/guards',guards,flush=True)
    parity=regular(raw,new,labels)
    frames=actual_frames(b,new)
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,native_ingress_pending=False,interrupt_pending=True,
        parent_SHA256=PIN,expected_memory_only_SHA256=SHA(new),patches=rows,labels=labels,
        layout=layout,RAM=audit,vertical_decoder=dec,inputs=inputs,guards=guards,regular=parity,actual_GameCore=frames,
        scope='Actual CPU GameCore input/native constructor and exact table replacement. No Mesen/carry/IRQ/whole-stage or installation claim.',
        bindings={str(p.relative_to(R)).replace('\\','/'):SHA(p.read_bytes()) for p in
            (Path(__file__),SOURCE,INGRESS,W.SOURCE,W.DATA,BASE)})
    (OUT/'leaf-proof.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
