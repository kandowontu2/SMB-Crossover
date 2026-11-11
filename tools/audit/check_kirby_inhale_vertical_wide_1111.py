"""Qualify Kirby's existing inhale contact with full native world Y."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
from unittest.mock import patch

import check_kirby_owner_main_1101_v2 as Main
import check_kirby_red_return_1111 as Bind
import check_sonic_native_effects_vectors_1110 as Vectors


A, N = Bind.Authority, Bind.N
PIN = 'b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576'
CANDIDATE = 'a1305ec9ca6cdb637214a76f6cea0931c422e7b5699081ef497cc95cad9e6efc'
SOURCE = Bind.R / 'tools/reference/kirby_inhale_vertical_wide_1111.s'
BANK = 74
OLD_VERTICAL, OLD_TARGET = 0xaafc, 0xaaf6
VERTICAL, TARGET = OLD_TARGET, 0xa220
STOP = (0x5b00,224)
sys.path.insert(0,str(SOURCE.parent))
from sonic_sms_compact_cold_worker_1110 import assemble


def offset(pc):
    return 16+BANK*8192+(pc&8191)


def jsr(pc):
    return b'\x20'+pc.to_bytes(2,'little')


def proposal(raw, bundle):
    assert sha256(raw).hexdigest()==PIN
    prior = A.AUTHORITY.read_bytes()
    assert sha256(prior).hexdigest()==A.AUTHORITY_ROM
    for name,start,size in (('KbInhaleTargetY',OLD_TARGET,6),('KbInhaleVertical',OLD_VERTICAL,29)):
        assert A.address(bundle,name)==start and A.location(bundle,name)==offset(start)
        assert int(bundle['syms'][name]['size'],0)==size
    assert A.address(bundle,'KbShellEnemyContact')==0xab19==VERTICAL+35
    assert A.address(bundle,'KbWeapons::StopInhale')==TARGET+8
    assert raw[offset(TARGET-6):offset(TARGET+8)]==bytes.fromhex('2055a24c37a2')+b'\xea'*8
    assert raw[offset(VERTICAL):offset(VERTICAL+35)]==prior[offset(VERTICAL):offset(VERTICAL+35)]
    bank = raw[offset(0xa000):offset(0xa000)+8192]
    for old,expected in ((OLD_VERTICAL,[0xa2a6,0xaa54]),(OLD_TARGET,[0xa2e6,OLD_VERTICAL])):
        got=[0xa000+i for i in range(len(bank)-2) if bank[i:i+3]==jsr(old)]
        assert got==expected
        assert b'\x4c'+old.to_bytes(2,'little') not in bank
        far=bytes((0xa9,old&255,0x8d,0x6c,1,0xa9,old>>8,0x8d,0x6d,1))
        assert far not in raw[16:1048592]
    inputs=('Enemy_Y_HighPos','Enemy_Y_Position','Player_Y_Position','Player_Y_HighPos')
    declarations=''.join(f'{n}=${A.address(bundle,n):04x}\n' for n in inputs)
    p=assemble(declarations+SOURCE.read_text(encoding='ascii'),{'TARGET':(TARGET,6),'VERTICAL':(VERTICAL,35)})
    assert p['used']=={'TARGET':6,'VERTICAL':35}
    assert p['images']['TARGET']==raw[offset(OLD_TARGET):offset(OLD_TARGET+6)]
    image=bytearray(raw)
    edits=((TARGET,p['images']['TARGET']),(VERTICAL,p['images']['VERTICAL']),
           (0xa2a6,jsr(VERTICAL)),(0xaa54,jsr(VERTICAL)),(0xa2e6,jsr(TARGET)))
    allowed=set()
    for at,body in edits:
        start=offset(at);image[start:start+len(body)]=body
        allowed.update(range(start,start+len(body)))
    changed={i for i,(a,b) in enumerate(zip(raw,image,strict=True)) if a!=b}
    assert changed<=allowed and all(i<offset(0xab19) for i in changed)
    assert len(changed)==38 and sha256(image).hexdigest()==CANDIDATE
    receipt=dict(parent_SHA256=PIN,image_SHA256=sha256(image).hexdigest(),changed_bytes=len(changed),
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),spans=[(at,len(body))for at,body in edits])
    return bytes(image),p,receipt


def wide_pairs(image,bundle):
    data=[0]*65536
    data[0xa000:0xc000]=image[offset(0xa000):offset(0xa000)+8192]
    c=N.NesMPU(memory=data,pc=VERTICAL)
    slot=3
    px,ph,ey,eh=(A.address(bundle,n) for n in ('Player_Y_Position','Player_Y_HighPos',
                                               'Enemy_Y_Position','Enemy_Y_HighPos'))

    def call(py,pyh,y,yh):
        data[px],data[ph],data[ey+slot],data[eh+slot]=py,pyh,y,yh
        c.pc,c.sp,c.x,c.y,c.p,c.a=VERTICAL,224,slot,91,0x31,85
        c.stPushWord(STOP[0]-1)
        for _ in range(30):
            if (c.pc,c.sp)==STOP:break
            c.step()
        else:raise AssertionError((hex(c.pc),c.sp))
        assert (c.x,c.y,c.sp)==(slot,91,224)
        return bool(c.p&1)

    cases=Counter()
    for pyh,py,y in product((0,1,2),range(256),range(256)):
        d=256+y-(256*pyh+py)
        want=-4<=d<=20
        assert call(py,pyh,y,1)==want,(pyh,py,y,d)
        cases[f'player_page_{pyh}']+=1
        if want:cases[f'near_page_{pyh}']+=1
    for high,py,y in product(range(3,256),(0,4,236,255),(0,4,236,255)):
        assert not call(py,high,y,1)
        cases['distant_player_high']+=1
    for high in range(256):
        if high==1:continue
        assert not call(176,1,184,high)
        cases['nonvisible_enemy_high']+=1
    return dict(cases)


def spawn_seed(bundle):
    m=N.fresh(bundle)
    N.put(m,CrossoverMenuIndex=12)
    for name in ('MenuResolveCharacter','QueueSelection'):N.invoke(m,name)
    assert N.get(m,'SelectedCharacter')==13
    N.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
    N.invoke(m,'GameMenuRoutine')
    N.invoke(m,'PauseRoutine',a=0)
    for count in range(300):
        if tuple(N.get(m,n)for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        Main.main_step(m);N.consume(m)
    else:raise AssertionError('native menu/parser bound')
    for _ in range(40):Main.main_step(m);N.consume(m)
    assert all(N.get(m,n)==v for n,v in dict(KbHealth=6,KbCopy=0,KbMouth=0,KbPrevious=0,NumberofLives=2).items())
    return m,count


def replay(seed, mode, face, phase, gap, pad, *, edge=False):
    m=N.fork(seed)
    Main.scene(m,face)
    N.put(m,CrossoverBehaviorVersion=mode)
    if phase in ('rise','fall'):
        speed=1 if phase=='fall' else 255
        py=236 if edge else 170 if phase=='fall' else 176
        N.put(m,Player_Y_Position=py,Player_State=2 if phase=='fall' else 1,Player_Y_Speed=speed)
        m[A.address(m.bundle,'MmVY')+2]=speed
    Main.actor(m,6,112+gap*(1 if face==1 else -1),y=0 if edge else 184)
    names=('KbWeapons::Capture','KbWeapons::Suction','KbBodyContact','KbInjuryStart','EnemyStomped')
    points={(A.address(m.bundle,n),((A.location(m.bundle,n)-16)//8192)|128):n for n in names}
    snapshots=[]; events=[]
    for buttons in pad:
        Main.keys(m,buttons)
        m.writes.clear();m.ram_writes.clear();m.ppu_log.clear();m.blocked.clear()
        seen=[]

        def watch(q,c,_):
            if c.pc<0x8000:return
            name=points.get((c.pc,q.rawtags[(c.pc-0x8000)//8192]))
            if name:
                seen.append((name,*(N.get(q,n)for n in ('KbActionAge','KbFresh','Player_Y_Position','Enemy_Y_Position'))))

        Main.call(m,'GameLoop',watch)
        assert not m.blocked and N.get(m,'NumberofLives')==2
        events.append(seen)
        stable=('KbAction','KbActionAge','KbFresh','KbMouth','KbMouthCopy','KbHealth','KbHurt','KbFloat',
                'Enemy_Flag','Enemy_ID','Enemy_State','Enemy_Y_Position','Enemy_X_Position','Enemy_PageLoc',
                'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
                'Player_Y_Speed','PlayerFacingDir','GameEngineSubroutine')
        snapshots.append(tuple(N.get(m,n) for n in stable))
        N.consume(m)
    return snapshots,events


def main_pairs(old,new):
    counts=Counter(); witnesses=[]
    for mode,face,phase,gap,pad in product((0,1),(1,2),('ground','rise','fall'),(6,12,14,16,-6),((0,),(64,))):
        a,b=(replay(seed,mode,face,phase,gap,pad)for seed in (old,new))
        assert a==b,(mode,face,phase,gap,pad,a,b)
        if pad==(64,) and gap>=0:
            assert b[0][0][5]==6 and not any(q[0]=='KbInjuryStart' for q in b[1][0])
        counts['first_Main_pairs']+=1
    for mode,face,pad in product((0,1),(1,2),((64,64,64),(64,0))):
        a,b=(replay(seed,mode,face,'ground',14,pad)for seed in (old,new))
        assert a==b,(mode,face,pad,a,b)
        counts['held_or_release_pairs']+=1
    for mode,face in product((0,1),(1,2)):
        for gap,pad in ((6,64+face),(-6,64+(3-face))):
            a,b=(replay(seed,mode,face,'ground',gap,(pad,)) for seed in (old,new))
            assert a==b,(mode,face,gap,pad,a,b)
            counts['directional_edge_pairs']+=1
    for mode,face in product((0,1),(1,2)):
        a,b=(replay(seed,mode,face,'fall',6,(64,),edge=True) for seed in (old,new))
        assert [e for e in a[1][0] if e[0]=='KbWeapons::Capture']==[('KbWeapons::Capture',8,64,237,0)]
        assert not [e for e in b[1][0] if e[0]=='KbWeapons::Capture'] and b[0][0][3]==0
        assert b[0][0][16:18]==(237,1)
        witnesses.append(dict(mode=mode,face=face,old_capture_age=8,player_y=237,target_y=0,new_mouth=0))
    return dict(counts),witnesses


def interrupt_cuts(seed):
    irq=Vectors.ISR
    irq.DEEPEST=None
    irq.PATHS.clear()
    reached=set();counts=Counter()

    def live(m,c):
        return (irq.regs(c),bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
            bytes(m[0x200:0x800]),bytes(m[0x5c00:0x5d00]),tuple(bytes(b)for b in m.ram),tuple(m.rawtags))

    def observe(m,c):
        pc=c.pc
        if m.rawtags[1]!=202 or pc in reached or not (TARGET<=pc<TARGET+6 or VERTICAL<=pc<VERTICAL+35):
            return
        reached.add(pc)
        a,b=Vectors.clone(m,c)
        irq.finish(a,b,STOP)
        for kind in ('NMI','IRQ'):
            q,d=Vectors.clone(m,c)
            before=live(q,d)
            assert irq.isr(q,d,kind,STOP)=='returned' and live(q,d)==before,(kind,hex(pc))
            irq.finish(q,d,STOP)
            assert live(q,d)==live(a,b),(kind,hex(pc),'continuation')
            counts[kind]+=1

    syms=dict(seed.bundle['syms'])
    for name,at in (('KbInhaleVertical',VERTICAL),('KbInhaleTargetY',TARGET)):
        syms[name]=dict(syms[name],val=hex(at))
    cases=((176,1,184,1),(176,1,205,1),(176,1,172,1),(237,1,0,1),(176,1,184,0))
    with patch.object(irq,'regs',side_effect=lambda c:(c.pc,c.a,c.x,c.y,c.p&0xef,c.sp)), \
            patch.object(irq,'clone',side_effect=Vectors.clone):
        for py,pyh,ey,eyh in cases:
            m=N.fork(seed);m.bundle=dict(seed.bundle,syms=syms)
            N.put(m,Player_Y_Position=py,Player_Y_HighPos=pyh,Enemy_Y_Position=ey,Enemy_Y_HighPos=eyh,
                  DisableScreenFlag=0,Mirror_PPUMASK=30,NmiDisable=255)
            Bind.call(m,'KbInhaleVertical',observe=observe)
            Bind.call(m,'KbInhaleTargetY',observe=observe)
        assert irq.DEEPEST is not None
        m,c,entry,stop=irq.DEEPEST
        a,b=Vectors.clone(m,c)
        q,d=Vectors.clone(m,c)
        before=live(q,d)
        assert irq.isr(q,d,'IRQ')=='returned' and live(q,d)==before
        for target in ((entry[0],entry[-1]),stop):
            irq.finish(a,b,target)
            irq.finish(q,d,target)
            assert live(q,d)==live(a,b)
    assert counts['NMI']==counts['IRQ']>=25
    return dict(cuts=dict(counts),nested_IRQ=1,deepest_parent_SP=c.sp)


def main():
    raw=Bind.NIGHTLY.read_bytes()
    bundle=A.scoped_load(A.AUTHORITY);bundle['raw']=raw
    image,p,receipt=proposal(raw,bundle)
    print(json.dumps(dict(event='proposal',**receipt),sort_keys=True),flush=True)
    print(json.dumps(dict(event='wide',**wide_pairs(image,bundle)),sort_keys=True),flush=True)
    old,origin=spawn_seed(bundle)
    new=N.fork(old);new.bundle=dict(bundle,raw=image)
    for window,tag in enumerate(new.rawtags):
        if tag&128:new.raw_page(window,tag)
    parity,witness=main_pairs(old,new)
    print(json.dumps(dict(event='Main',parser_updates=origin,parity=parity,wrap_fixes=witness),sort_keys=True),flush=True)
    print(json.dumps(dict(event='vectors',**interrupt_cuts(new)),sort_keys=True),flush=True)
    print(json.dumps(dict(passed=True,source_only=True,output_files=0)),flush=True)


if __name__=='__main__':
    main()
