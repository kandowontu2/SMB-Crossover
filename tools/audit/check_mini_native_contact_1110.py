"""Check Mini's ordinary contact through the existing native bridge."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import check_mini_direct_frame_stack_1110 as Link
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_lift_admission_async_1108_v1 import tags


A,L,M,N,R = Link.A,Link.L,Link.M,Link.N,Link.R
BASE,PIN = Link.BASE,Link.PIN
SOURCE = R/'tools/reference/mini_native_contact_1110.s'
FUNDING = R/'src/smb2_roster_audio.s'
GATE,HELPER,BRIDGE = 0xbf03,0xb157,0xedb1
HOT = HELPER+10
ENEMY = 0x9659
OLD = bytes.fromhex('08ad0260c919f00bc927f016ad6a01284cdcab28a9158d6c01a9bb8d6d01a9f6d0db'
                    '28a9298d6c01a9b08d6d01a9c1d0cc')
offset = Link.Q.offset


def build(out):
    raw = BASE.read_bytes()
    assert M.sha(raw)==PIN
    b = M.bundle(raw)
    at = lambda bank,pc,n:raw[offset(bank,pc):offset(bank,pc)+n]
    for name,pc in (('S2BoundaryBody',GATE),('S2AudioNativeEntry',0xb180),('GuestBodyContactBridge',BRIDGE),
                    ('PlayerEnemyCollision',ENEMY),('GuestBodyContact',0xb5a1),
                    ('GuestBodyNoStomp',0x6f18),('GuestBodyStompAllowed',0x7fe3)):
        assert M.address(b,name)==pc,name
    assert '.res $29,$ff' in FUNDING.read_text() and at(74,HELPER,41)==b'\xff'*41
    assert at(74,0xb151,6)==bytes((1,2,4,8,16,32))
    meta = (R/'src/meta_knight.s').read_text()
    assert meta.count('lda BitMask,x')==2 and 'ldx #5\nLoop:' in meta
    assert 'ldx KbPullSlot\n  dex\n  jpl Loop' in meta
    assert at(74,0xbf00,52)==bytes.fromhex('4c5a01')+OLD
    assert at(127,BRIDGE,19)==bytes.fromhex('8d6a01a9038d6c01a9bf8d6d01a9ca205a0160')
    assert at(126,0x96ae,17)==bytes.fromhex('ad9c07f0064cf59a0a060420b1ed900160')
    assert at(10,0xb719,9)==bytes.fromhex('68850d68a868aa1860')
    bank = at(74,0xa000,8192)
    indexes = [i+0xa000 for i in range(len(bank)) if bank[i:i+3]==bytes.fromhex('bd51b1')]
    assert len(indexes)==2 and all(0xb000<=pc<0xb151 for pc in indexes),indexes
    assert bank.count(bytes.fromhex('b951b1'))==0
    for pc in (*range(GATE+1,0xbf34),*range(HELPER,0xb180)):
        assert all(bytes((op,pc&255,pc>>8)) not in bank for op in (0x20,0x4c,0x6c)),hex(pc)
    cfg,obj,binary,lbl = (out/f'contact.{ext}' for ext in ('cfg','o','bin','lbl'))
    cfg.write_text('MEMORY{G:start=$BF03,size=$31,file=%O; M:start=$B157,size=$29,file=%O;}\n'
                   'SEGMENTS{GATE:load=G,type=ro; CONTACT:load=M,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary,'-Ln',lbl],check=True)
    obj.unlink()
    code = binary.read_bytes()
    labels = {line.split()[2][1:]:int(line.split()[1],16) for line in lbl.read_text().splitlines()}
    assert len(code)==90 and labels==dict(ContactGate=GATE,MiniContact=HELPER,MiniContactEnd=0xb17f)
    assert code[49+HOT-HELPER:49+HOT-HELPER+3]==bytes.fromhex('ad5307')
    rows = [dict(file_offset=offset(74,pc),physical_PRG=74,CPU_half_open=[pc,pc+len(old)],
                 old_hex=old.hex(),new_hex=new.hex(),role=role)
            for pc,old,new,role in ((GATE,OLD,code[:49],'existing exact body boundary'),
                                   (HELPER,b'\xff'*41,code[49:],'source-declared B157..B180 alignment'))]
    return raw,install(raw,rows),rows,labels,indexes


def setup(seed,owner,enemy,engine,version,flags,pc=BRIDGE,*,slot=0,star=0,injury=0,area=1,vertical=4,overlap=True):
    m = slim_fork(seed)
    N.put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,CrossoverBehaviorVersion=version,
          ObjectOffset=slot,AreaType=area,Player_State=2,Player_Y_Speed=vertical,Player_Y_Position=169,
          Player_Y_HighPos=1,Player_Rel_XPos=112,Player_Rel_YPos=169,Enemy_Rel_XPos=115,
          Player_X_Position=199,Player_PageLoc=2,StarInvincibleTimer=star,InjuryTimer=injury)
    for name,value in (('Enemy_Flag',1),('Enemy_ID',enemy),('Enemy_State',0),('Enemy_OffscreenBits',0),
                       ('EnemyOffscrBitsMasked',0),('Enemy_Y_Position',184),('Enemy_Y_HighPos',1),
                       ('Enemy_X_Position',202),('Enemy_PageLoc',2),('Enemy_MovingDir',2),('Enemy_BoundBoxCtrl',9)):
        if name in m.bundle['syms']:
            m[M.address(m.bundle,name)+slot] = value
    box = M.address(m.bundle,'BoundingBox_UL_Corner')
    m[box:box+4] = bytes((113,193,119,201))
    ebox = box+4*(slot+1)
    m[ebox:ebox+4] = bytes((115 if overlap else 145,198,125 if overlap else 155,204))
    m.writes.clear()
    m.ram_writes.clear()
    c = N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp = 0x91,slot,enemy,flags,236
    c.stPushWord(0x5aff)
    return c


def execute(c):
    hits,stores = Counter(),{}
    def observe(z):
        tag,pc = tags(z),z.pc
        if pc in (GATE,HELPER,HOT,0xb5a1,0xb71a,0x9806,0x976c,0x9af5,0x98b5,0xb029,0xbb15):
            hits[tag,pc] += 1
        if (tag,pc)==(138,0xb71a):
            stores[len(z.memory.writes)] = (0x0d,z.a)
    run(c,lambda z:(z.pc,z.sp)==(0x5b00,236),observe)
    return hits,stores


def compare(a,b,traces):
    m,n = a.memory,b.memory
    assert registers(a,0xef)==registers(b,0xef) and live_stack(a)==live_stack(b)
    A.P.compare_memory(m,n)
    assert Link.Q.memory(m)==Link.Q.memory(n) and m.ram_writes==n.ram_writes
    old,old_stores = traces[0]
    new,_ = traces[1]
    hot = bool(new[202,HOT])
    transport = {0x145,0x162,0x16a,0x16c,0x16d,0x179,0x5115} if hot else set()
    if hot:
        assert old[138,0xb5a1]==1 and len(old_stores)==1
        for index,expected in old_stores.items():
            assert m.writes[index]==expected
        old_maps,new_maps = [[v for k,v in q.writes if k==0x5115] for q in (m,n)]
        indexes = [i for i in range(len(old_maps)-1) if old_maps[i:i+2]==[0x8a,0xca]]
        at, = indexes
        assert old_maps[:at]+old_maps[at+2:]==new_maps
    def writes(bus,omitted):
        return [(k,v) for i,(k,v) in enumerate(bus.writes)
                if i not in omitted and k not in transport and not 0x17b<=k<=0x100+a.sp]
    assert writes(m,old_stores if hot else {})==writes(n,{})
    return hot


def foreground(before,after):
    images = L.bundles(before,after)
    cold = [N.fresh(b) for b in images]
    mini = [L.fixture(b,0,False,False) for b in images]
    counts = Counter()

    def check(seeds,*args,**kwargs):
        pair = [setup(seed,*args,**kwargs) for seed in seeds]
        traces = [execute(c) for c in pair]
        try:
            hot = compare(*pair,traces)
        except AssertionError as error:
            raise AssertionError((args,kwargs,[registers(c,0xef) for c in pair],traces)) from error
        result = pair[0].processorCycles-pair[1].processorCycles
        if kwargs.get('pc',BRIDGE)==BRIDGE and args[0]==41:
            assert hot
            m = pair[1].memory
            assert (m[0x7fe3],m[0x6f18])==(kwargs.get('area',1),1)
            assert [m[at] for at in (0x162,0x16a,0x16c,0x16d,0x179)]==[0x8a,0x91,0xa1,0xb5,kwargs.get('slot',0)]
        return hot,result,traces[0][0]

    for owner,version,flags in product(range(256),(0,1),(0x21,0x60,0x65)):
        hot,cycles,_ = check(mini if owner==41 else cold,owner,6,8,version,flags)
        assert hot==(owner==41)
        counts['Mini bridge' if hot else 'foreign bridge',cycles] += 1
    outcomes = Counter()
    for enemy,version,star,injury,vertical,area,overlap in product((0,6,7,12,13,18,20,21,45,51),
            (0,1),(0,2),(0,16),(4,0xfc),(0,1),(False,True)):
        hot,cycles,hits = check(mini,41,enemy,8,version,0x21,pc=ENEMY,star=star,injury=injury,
                                area=area,vertical=vertical,overlap=overlap)
        counts['whole native enemy',cycles] += 1
        for kind,pc in (('star',0x9af5),('injury',0x976c),('stomp',0x9806),('score',0x98b5)):
            outcomes[kind] += hits[254,pc]
        assert hot==(overlap and star==0),(enemy,star,overlap,hot)
    assert all(outcomes[k] for k in ('star','injury','stomp','score')),outcomes
    return dict(cycles=[[role,delta,n] for (role,delta),n in sorted(counts.items())],outcomes=dict(outcomes))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',required=True,type=Path)
    out = cli.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    before,after,patches,labels,indexes = build(out)
    print('Linked native contact',M.sha(after),labels,flush=True)
    result = foreground(before,after)
    refs = (Path(__file__),SOURCE,FUNDING,BASE,R/'src/meta_knight.s',R/'src/kirby_weapons.s',
            R/'src/guest_body_contact.s',R/'src/guest_source_stomp.s',R/'src/collision.s',out/'contact.bin')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after),
                 patches=patches,labels=labels,BitMask_actor_index_readers=indexes,foreground=result,
                 bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
