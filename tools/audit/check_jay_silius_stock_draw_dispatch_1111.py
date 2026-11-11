"""Qualify the live Jay stock sprite dispatch on exact 3d32 in memory."""
from collections import Counter
from itertools import product
import json
from types import SimpleNamespace
from unittest.mock import patch

from py65.devices.mpu6502 import MPU

import check_jay_silius_stock_hit_draw_1111 as Hit

F,J,C,H,N,W = Hit.F,Hit.J,Hit.C,Hit.H,Hit.N,Hit.W
SOURCE = H.ROOT/'tools/reference/jay_silius_stock_draw_dispatch_1111.s'
START, END, HOT = 0xa91f,0xaab1,0xb27f
LEGACY_RECORD, LEGACY_HUD = 0xa9c2,0xaab1
RELAX = (0xa983,0xa98d,0xa997,0xa99f,0xa9ae,0xa9de,0xa9f7,0xa9fe,0xaa05,0xaa16,0xaa56,0xaa5d)
SCOPE, MUX = 0xb2c1,0xb303
DRAW_PARENT = '20bd447db2cb77d0724ec5ae329de422341833bc288cd9453e480926b63d62fa'
PIN = '3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8'
DESCRIPTOR = bytes.fromhex('030101da004b014c01')
MODE_LENGTHS = dict(imp=1,acc=1,imm=2,zpg=2,zpx=2,zpy=2,inx=2,iny=2,rel=2,
                    abs=3,abx=3,aby=3,ind=3)


def at(bank,pc):
    return C.offset(bank,pc)


def instructions(raw,bank,lo,hi):
    while lo<hi:
        op,mode = MPU.disassemble[raw[at(bank,lo)]]
        n = MODE_LENGTHS[mode]
        yield lo,op,mode,raw[at(bank,lo):at(bank,lo)+n]
        lo += n
    assert lo==hi


def relative(pc,target):
    diff = target-pc-2
    assert -128<=diff<=127,(hex(pc),hex(target),diff)
    return diff&255


def render_patch(raw,insert):
    assert C.digest(raw[at(98,START):at(98,END)])=='bd2bbbd57a798d36a83f8a1e7cd74f0485016f98c36dc1d850228f330b4170a7'
    assert C.digest(raw[at(98,0xac42):at(98,0xac91)])=='afb60ba9b14c853b54f2014487117dbbb1883e014adadcc43f37ec8c1e3a09f0'
    assert raw[at(126,0x80c2):at(126,0x80c9)]==bytes.fromhex('8da17d8d165160')
    rows = dict((pc,(op,mode,data)) for pc,op,mode,data in instructions(raw,98,START,END))
    assert raw[at(98,START):at(98,START)+10]==bytes.fromhex('a9e18da17da9e18d1651')
    assert raw[at(98,0xa9b8):at(98,0xa9c2)]==bytes.fromhex('4c42ac')+b'\xea'*7
    assert raw[at(98,0xaa92):at(98,0xaa96)]==bytes.fromhex('20b1aa60')
    retarget = {}
    fragments = []
    pc = START
    while pc<END:
        dst = START+sum(len(row[1]) for row in fragments)
        retarget[pc] = dst
        if pc==START:
            fragments.append((pc,bytes.fromhex('a9e120c280'),None))
            pc += 10
            continue
        if pc==0xa9bb:
            pc += 7
            continue
        op,mode,data = rows[pc]
        if pc==0xaa92:
            fragments.append((pc,insert,None))
        if pc in RELAX:
            following = rows[pc+2][2]
            assert mode=='rel' and data[1]==3 and following[0]==0x4c
            fragments.append((pc,bytes((data[0]^0x20,0)),int.from_bytes(following[1:],'little')))
            pc += 5
            continue
        target = None
        if mode=='rel':
            disp = data[1]
            target = pc+2+(disp if disp<128 else disp-256)
        elif op in ('JSR','JMP'):
            assert mode=='abs'
            target = int.from_bytes(data[1:],'little')
        fragments.append((pc,data,target))
        pc += len(data)
    out = bytearray()
    for old,data,target in fragments:
        if target is not None:
            if START<=target<END:
                target = retarget[target]
            operand = bytes((relative(START+len(out),target),)) if len(data)==2 else J.u16(target)
            data = data[:1]+operand
        out.extend(data)
    assert len(out)==(END-START)-48+len(insert)<=END-START,(len(out),len(insert))
    bank = raw[at(98,START)-((START)&8191):at(98,START)-((START)&8191)+8192]
    branch = b'\x4c'+J.u16(LEGACY_RECORD)
    hit_offsets = [i for i in range(len(bank)-2) if bank[i:i+3]==branch]
    refs = [0xa000+i for i in hit_offsets]
    decoded = [p for p,op,_,v in instructions(raw,98,0xac42,0xac91) if op=='JMP' and v==branch]
    assert refs==decoded and len(refs)==2,(refs,decoded)
    return bytes(out).ljust(END-START,b'\xea'),retarget,refs,dict(relaxed=len(RELAX),
        previous_Nops=7,mapper_compaction=5,bytes_inserted=len(insert),padding=END-START-len(out))


def assemble_live(trial,work,cookie):
    known = dict(PrivateUpdate=0xa785,OamOffset=0x06de,BodyBytes=0xc0bc,DrawLimit=0xc0bd,
                 FrameCounter=W.address(trial,'FrameCounter'),OperMode=W.address(trial,'OperMode'),
                 OperModeTask=W.address(trial,'OperMode_Task'))
    for name in ('GamePauseStatus','NmiDisable','FamilyMainCommit','SwimmingFlag','WorldNumber',
                 'LevelNumber','ScreenLeft_PageLoc','ScreenLeft_X_Pos','Player_PageLoc'):
        known[name] = W.address(trial,name)
    text = SOURCE.read_text().replace('CookieBytes',','.join(map(str,cookie)))
    old = work['source']
    constants = old.split('.setcpu',1)[0]
    drawer = old[old.index('DrawStock:'):]
    needle = ' stx ShotIndex\n lda ShotRecords+9,x'
    assert drawer.count(needle)==1
    drawer = drawer.replace(needle,' stx ShotIndex\n lda OamOffset\n cmp DrawLimit\n bcs DrawAdvance\n lda ShotRecords+9,x')
    definitions = ''.join(f'{k}=${v:04x}\n' for k,v in known.items())
    layout = {'HOT94':(HOT,129),'DRAW_CALL':(0x4000,48),'SCOPE':(SCOPE,MUX-SCOPE),
              'MUX':(MUX,0xb3c0-MUX)}
    result = H.assemble(definitions+constants+text+'\n'+drawer,layout)
    assert result['symbols']['PrivateMux']==MUX and result['symbols']['DrawPrivate']==SCOPE
    return result


def flight_on_3d32(donor):
    import deliver_dkjr_second_gap_1111 as Dk
    import deliver_sonic_rings_1110 as Sonic

    assemble_parent = F.compose_parent
    assert Dk.PIN==PIN

    def exact_parent(resident):
        source = resident['b031_source']
        built = Sonic.Build.proposal(source)
        previous = Dk.merge(source,built[0])
        assert C.digest(previous)==PIN
        with patch.object(H,'ROM',SimpleNamespace(read_bytes=lambda:previous)), \
                patch.object(Sonic.Build,'proposal',return_value=built):
            return assemble_parent(resident)

    with patch.object(F,'compose_parent',exact_parent):
        return F.proposal(donor)


def proposal(donor):
    flight = flight_on_3d32(donor)
    hit,work,old_payload,old_cookie,_ = Hit.proposal(flight)
    raw = hit['raw']
    assert C.digest(raw)==DRAW_PARENT
    preliminary = assemble_live(hit,work,bytes(16))
    assert work['symbols']['DrawStock']==SCOPE
    private = old_payload[:SCOPE-0xb000]
    private += preliminary['images']['SCOPE'].ljust(MUX-SCOPE,b'\xea')
    private += preliminary['images']['MUX']
    assert len(private)<=960 and len(private)%256
    prefix = flight[6]['source']
    for old,new in ((' lda #$60\n sta $03',' lda #$40\n sta $03'),
                    (f'CopyPages={len(flight[7])//256}\n',f'CopyPages={len(private)//256}\n'),
                    (f'CopyTailBytes={len(flight[7])%256}\n',f'CopyTailBytes={len(private)%256}\n')):
        assert prefix.count(old)==1,old
        prefix = prefix.replace(old,new)
    shim = H.assemble(prefix,{'PREFIX':(0xa000,64),'FLIGHT':(F.FLIGHT,512)})['images']['PREFIX']
    packet = (shim.ljust(64,b'\xea')+private).ljust(1024,b'\xea')
    stage = raw[C.CHR+331*1024:C.CHR+333*1024]
    cookie = bytes((0xa7,16,32,7))+C.sha256(stage+flight[3]+DESCRIPTOR+packet).digest()[:12]
    program = assemble_live(hit,work,cookie)
    draw,relocated,refs,funding = render_patch(raw,program['images']['DRAW_CALL'])
    out = bytearray(raw)
    edits = []

    def put(offset,value):
        assert all(offset+len(value)<=i or j<=offset for i,j in edits)
        out[offset:offset+len(value)] = value
        edits.append((offset,offset+len(value)))

    put(at(98,START),draw)
    for pc in refs:
        put(at(98,pc)+1,J.u16(relocated[LEGACY_RECORD]))
    original_hot = raw[at(94,HOT):at(94,HOT)+129]
    assert original_hot[108:124]==old_cookie and original_hot[124:]==b'\xff'*5
    put(at(94,HOT),program['images']['HOT94'].ljust(129,b'\xff'))
    cold_addr = flight[4]['symbols']['Cookie']
    assert raw[at(65,cold_addr):at(65,cold_addr)+16]==old_cookie
    put(at(65,cold_addr),cookie)
    put(C.CHR+F.PAGE*1024,packet)
    report = dict(parent=flight[-1]['parent'],image=C.digest(out),cookie=cookie.hex(),
        private_bytes=len(private),packet_sha=C.digest(packet),old_draw_redirects=[hex(x) for x in refs],
        segments=program['used'],funding=funding,patches=edits,
        draw_hook=hex(relocated[0xaa92]),legacy_record=hex(relocated[LEGACY_RECORD]))
    return dict(hit,raw=bytes(out)),hit,flight,program,private,cookie,report


class DmaBus(W.ControllerBus):
    def __setitem__(self,address,value):
        if address==0x4014 and value==2:
            self.dma = bytes(self[0x200:0x300])
        super().__setitem__(address,value)


def cells(oam):
    return [bytes(oam[i:i+4]) for i in range(0,256,4) if oam[i]<240 and oam[i+1]==40]


def live_draw(trial,program,private,cookie,report):
    m = C.menu(trial,1,{'images':{}})
    m.__class__ = DmaBus
    m.dma = None
    active_updates = 0
    visible = []
    dma_frames = 0
    calls = Counter()
    cuts = Counter()
    seen = set()
    seed = None
    prior = None
    hot_pcs = {i['pc'] for i in program['instructions'] if i['segment']=='HOT94'}
    private_pcs = {i['pc'] for i in program['instructions'] if i['segment'] in ('SCOPE','MUX')}
    hook = int(report['draw_hook'],16)
    for _ in range(680):
        active = tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)
        if active and active_updates==60:
            break
        m.controller_pad = 64 if active and 4<=active_updates<20 else 0
        m.dma = None

        def watch(memory,cpu):
            nonlocal seed
            pc, bank = cpu.pc,m.rawtags[1]
            if bank==222 and pc==HOT:
                kind = m[0x103+cpu.sp]
                assert kind in (224,226),kind
                if active:
                    calls['draw_hot' if kind==226 else 'movement_hot'] += 1
            if bank==3 and pc==MUX and active:
                assert cpu.y in (224,226)
                assert C.Common.headers(m)==(cookie,)*2 and m.ram[3][0x1000:0x1000+len(private)]==private
                calls['draw_private' if cpu.y==226 else 'movement_private'] += 1
            if bank==226 and pc==START and active and seed is None and F.slot(m,0xf0)[9]:
                seed = C.Vector.clone(m)
            during_new = (bank==3 and pc in private_pcs) or (bank==222 and pc in hot_pcs)
            during_new |= bank==226 and hook<=pc<hook+47
            during_new |= bank in (222,226) and pc in (0x80c2,0x80c5,0x80c8)
            token = bank,pc,cpu.p&4
            if active and during_new and token not in seen:
                seen.add(token)
                for vector in ('NMI','IRQ'):
                    q,d = C.Vector.clone(m,cpu)
                    before = (tuple(map(bytes,q.ram)),bytes(q[3:11]),bytes(q[0x15a:0x17b]),
                              bytes(q[0x200:0x300]),bytes(q[0x101+cpu.sp:0x200]),tuple(q.rawtags))
                    outcome = C.Vector.isr(q,d,vector)
                    after = (tuple(map(bytes,q.ram)),bytes(q[3:11]),bytes(q[0x15a:0x17b]),
                             bytes(q[0x200:0x300]),bytes(q[0x101+cpu.sp:0x200]),tuple(q.rawtags))
                    assert before[:-1]==after[:-1],(vector,hex(pc),bank)
                    if before[-1]!=after[-1]:
                        assert q[pc:pc+3]==list(bytes.fromhex('8d1651'))
                        assert before[-1][:2]==after[-1][:2] and before[-1][3]==after[-1][3]
                        assert q.rawtags[2]==q[0x7da1]
                        cuts['C_mapper_split'] += 1
                    cuts[vector+'_'+outcome] += 1

        C.Game.frame(m,watch)
        if not active:
            continue
        assert N.get(m,'NumberofLives')==2 and not any(N.get(m,'JnShotKind',i) for i in range(6))
        if prior is not None:
            assert m.dma is not None and cells(m.dma)==[prior],(active_updates,prior,m.dma)
            assert m.chr_latches[0]==216 and m.ppuctrl&0x20,(m.chr_latches,m.ppuctrl)
            dma_frames += 1
        shot = F.slot(m,0xf0)
        frame_cells = cells(m[0x200:0x300])
        if shot[9]:
            prior = bytes((shot[7]-8,40,0,shot[6]-4))
            assert frame_cells==[prior],(active_updates,shot.hex(),frame_cells)
            visible.append((active_updates,shot[6],shot[7],prior.hex()))
        else:
            assert not frame_cells,(active_updates,frame_cells)
            prior = None
        active_updates += 1
    assert active_updates==60 and seed is not None and len(visible)==dma_frames==50
    assert visible[0][:3]==(4,56,191) and visible[-1][:3]==(53,252,191)
    assert calls=={'draw_hot':60,'draw_private':60,'movement_hot':60,'movement_private':60},calls
    return seed,dict(updates=active_updates,first=visible[0],last=visible[-1],real_NMI_DMA=dma_frames,
                     calls=dict(calls),vectors=dict(cuts),lives=N.get(m,'NumberofLives'))


def rejection_capacity(seed,program):
    counts = Counter()
    draw = program['symbols']['DrawStock']

    def test(m):
        path = []
        def watch(memory,cpu):
            if m.rawtags[1]==3 and cpu.pc in (MUX,draw):
                path.append(cpu.pc)
            assert not (cpu.pc==0xa2cb and m.rawtags[1]==224),'Draw reached legacy movement'
        C.Vector.call(m,'JnDraw',observe=watch)
        return path

    for bank,index in product((2,3),range(16)):
        m = C.Vector.clone(seed)
        m.ram[bank][0x1fe0+index] ^= 1
        assert test(m)==[] and not cells(m[0x200:0x300]),(bank,index)
        counts['header_byte_failures'] += 1

    for offset,body,flip,rotation in product((0,228,232,236,240,248,252,253), (0,16,24), (0,2),(0,28)):
        m = C.Vector.clone(seed)
        # The native reservation consumes the first byte behind SmPosePtr.
        # This directed descriptor tests both null and allocated bodies.
        ptr = 0x6400 if body else 0
        N.put(m,CurrentOAMOffset=offset,GuestOamRotationActive=int(bool(rotation)),RgOamRotation=rotation)
        m[0x6b06],m[0x6b07] = ptr&255,ptr>>8
        if ptr:
            m[ptr] = body
        original = bytes(F.slot(m,0xf0))
        for j in range(3):
            record = bytearray(original)
            record[6] += j*12
            record[9] = 1|flip
            m.ram[2][0x80+j*16:0x90+j*16] = record
        m[0x200:0x300] = bytes((248,0,0,0))*64
        path = test(m)
        max_shots = min(3,max(0,(252-body-offset)//4)) if offset&3==0 else 0
        oam = m[0x200:0x300]
        expected = {((offset+rotation+4*j)&255):bytes((183,40,32*flip,52+12*j)) for j in range(max_shots)}
        actual = {j:bytes(oam[j:j+4]) for j in range(0,256,4) if oam[j]<240 and oam[j+1]==40}
        assert actual==expected,(offset,body,flip,rotation,path,actual,expected)
        assert N.get(m,'CurrentOAMOffset')==offset+4*max_shots
        counts['body_capacity_cases'] += 1

    for name,value in (('OperMode',0),('OperMode_Task',2),('GamePauseStatus',1),
                       ('NmiDisable',0),('FamilyMainCommit',0),('ScreenLeft_X_Pos',1)):
        m = C.Vector.clone(seed)
        N.put(m,**{name:value})
        assert test(m)==[MUX] and not cells(m[0x200:0x300]),name
        counts['scene_declines'] += 1
    for offset in (0x33,0x34):
        m = C.Vector.clone(seed)
        m.ram[2][offset] = 0 if offset==0x33 else (m.ram[2][offset]+1)&255
        assert test(m)==[MUX] and not cells(m[0x200:0x300])
        counts['stale_frame_declines'] += 1
    return dict(counts)


def legacy_draw(hit,trial,flight,donor):
    compare = {'images':{},'symbols':{'JaySceneOrRetire':0,'PublishPosition':0},'instructions':[]}
    family = C.family_parity(hit,trial,compare,flight[1],donor)
    exact = 0
    for variant,kind,face,vx,age in product((0,64),range(1,14),(1,2),(3,253),(0,4,10)):
        states = []
        for image in (hit,trial):
            m = C.Common.blank(image)
            C.Common.scene(m,16)
            m[0x730b] = variant
            N.put(m,PlayerFacingDir=face,JnShotKind=kind,JnShotVX=vx,JnShotAge=age,
                  JnShotX=128,JnShotY=176,JnShotPage=0,CurrentOAMOffset=24)
            c = C.Vector.call(m,'JnDraw')
            states.append((C.Vector.regs(c),C.Vector.app(m),m.vram,m.chr_latches))
        assert states[0]==states[1],(variant,kind,face,vx,age,states[0][0],states[1][0])
        exact += 1
    return dict(natural_family=family,legacy_weapon_render_pairs=exact)


if __name__=='__main__':
    donor = C.actual_donor()
    trial,hit,flight,program,private,cookie,report = proposal(donor)
    print('Jay production draw layout',report,flush=True)
    seed, live = live_draw(trial,program,private,cookie,report)
    print('Jay production draw Main',live,flush=True)
    negatives = rejection_capacity(seed,program)
    print(json.dumps(dict(passed=True,layout=report,live=live,rejections=negatives,
        legacy=legacy_draw(hit,trial,flight,donor),ROM_written=False,Mesen=False,generated_files=0),sort_keys=True),flush=True)
