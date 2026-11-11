"""Verify Jay's stock bullet impact and native metasprite component in memory."""
from collections import Counter
import json

import check_jay_silius_stock_flight_1110 as F

J,C,H,N,W,Stock = F.J,F.C,F.H,F.N,F.W,F.Stock
SOURCE = H.ROOT/'tools/reference/jay_silius_stock_hit_draw_1111.s'
GOOMBA = 6
PAIR = bytes.fromhex('00000000001824420000000000183c7e')


def art():
    raw = C.Donor.DONOR.read_bytes()
    assert C.digest(raw)==C.Donor.PIN
    at = 16+2*16384+0x3da
    assert raw[at:at+6]==bytes.fromhex('0101fcf8006c')
    at = 16+8*16384+8*4096+0x6c*16
    pixels = raw[at:at+32]
    assert len(pixels)==32 and pixels[:16]==PAIR and any(pixels[16:])
    return pixels


def donor_hit_and_oam():
    raw = C.Donor.DONOR.read_bytes()
    cpu,_ = C.Motion.Motion.opening(raw)
    m = cpu.memory
    hits = []
    sprite = []
    for epoch in range(56):
        def observe():
            if cpu.pc==0xe56f and epoch==0 and m.ram[0x18]==0 and m.ram[0x1f]==1:
                assert m.ppu_ctrl==0xb0 and m.chr_pages==(8,16)
                oam = bytes(m.ram[0x200+cpu.x-4:0x200+cpu.x])
                assert oam==bytes((m.ram[0x17]-8,0x6c,0,m.ram[0x16]-4))
                sprite.append(oam.hex())
            if cpu.pc==0xe780 and m.ram[0x18]==9:
                assert m.ram[:2]==bytes((20,20)) and cpu.x in F.SLOT
                at = 0x300+cpu.x
                assert m.ram[at+8]==0 and m.ram[at+9] and m.ram[at+15]==1
                hits.append((epoch,cpu.x,m.ram[0x1f],m.ram[0x1e]))
                assert (m.ram[0xd0],m.ram[0xd1])==(2,0x1d)
            cpu.step()

        C.Donor.frame(cpu,m,128+(2 if epoch%8==0 else 0),observe)
    assert sprite==['a76c006c'] and hits==[(44,240,3,48),(50,224,2,48),(55,208,1,48)]
    return dict(native_donor_oam=sprite[0],donor_hits=hits)


def proposal(base):
    trial,linked,fields,runtime,cold,stock,flight,payload,old_cookie,report = base
    start = 0xb000+len(payload)
    native_names = ('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_Y_HighPos','Enemy_PageLoc',
                    'Enemy_X_Position','Enemy_Y_Position','ObjectOffset')
    aliases = {k:W.address(trial,k) for k in native_names}
    aliases.update(StockFlight=flight['symbols']['Flight'],ShotRecords=0xbfb0,
        ShotIndex=0xc0b6,ShotMetasprite=0xc0b7,NativeRender=W.address(trial,'MetaspriteRenderLoop'),
        NativeDefeat=W.address(trial,'ShellOrBlockDefeat'),OriginalSoundRequest=linked['symbols']['OriginalSoundRequest'])
    assert set(range(0xc0b6,0xc0bc)).isdisjoint(fields.values())
    assert (aliases['NativeRender'],aliases['NativeDefeat'])==(0xa5ba,0x9af5)
    constants = ''.join(f'{k}=${v:04x}\n' for k,v in aliases.items())
    work = H.assemble(constants+SOURCE.read_text(),{'BULLET':(start,928-len(payload))})
    joined = bytearray(payload+work['images']['BULLET'])
    site, = [i['pc'] for i in flight['instructions'] if i['op']=='JSR' and i['operand']==aliases['StockFlight']]
    pos = site-0xb000
    assert joined[pos:pos+3]==b'\x20'+J.u16(aliases['StockFlight'])
    joined[pos+1:pos+3] = J.u16(work['symbols']['FlightAndHit'])
    assert len(joined)<=928 and len(joined)%256
    text = flight['source']
    for key,div in (('CopyPages',len(joined)//256),('CopyTailBytes',len(joined)%256)):
        before = len(payload)//256 if key=='CopyPages' else len(payload)%256
        needle = f'{key}={before}\n'
        assert text.count(needle)==1
        text = text.replace(needle,f'{key}={div}\n')
    prefix = H.assemble(text,{'PREFIX':(0xa000,96),'FLIGHT':(F.FLIGHT,512)})['images']['PREFIX']
    packet = (prefix.ljust(96,b'\xea')+joined).ljust(1024,b'\xea')
    raw = trial['raw']
    stage = raw[C.CHR+331*1024:C.CHR+333*1024]
    descriptor = bytes.fromhex('030101da004b014c01')
    cookie = bytes((0xa7,16,32,6))+C.sha256(stage+runtime+descriptor+packet).digest()[:12]
    out = bytearray(raw)
    edits = []

    def replace(at,data):
        assert not any(at+n>begin and at<end for begin,end in edits for n in (len(data),))
        edits.append((at,at+len(data)))
        out[at:at+len(data)] = data

    off = C.CHR+F.PAGE*1024
    replace(off,packet)
    for bank,begin,limit in ((65,0xa696,162),(94,0xb27f,124)):
        start = C.offset(bank,begin)
        envelope = raw[start:start+limit]
        assert envelope.count(old_cookie)==1
        replace(start+envelope.index(old_cookie),cookie)
    off = C.CHR+216*1024+640
    assert raw[off:off+32]==bytes(32)
    pixels = art()
    replace(off,pixels)
    return (dict(trial,raw=bytes(out)),work,bytes(joined),cookie,dict(image=C.digest(out),
        code=work['used'],payload_bytes=len(joined),packet_sha=C.digest(packet),art_sha=C.digest(pixels),
        cookie=cookie.hex(),worker_edits=edits))


def native_goomba(m):
    # Directed contact fixture. Use the stock parser and first authored
    # Goomba record, with its right boundary temporarily at the test column.
    # The model receives no direct writes to enemy records.
    pointer = W.address(m.bundle,'E_GroundArea6')
    address = W.location(m.bundle,'E_GroundArea6')
    assert pointer==0xaa3f and m.bundle['raw'][address:address+5]==bytes.fromhex('1ec2006b06')
    fields = dict(EnemyDataOffset=3,EnemyObjectPageLoc=0,EnemyObjectPageSel=0,
                  ScreenRight_X_Pos=0x50,ScreenRight_PageLoc=0,ObjectOffset=4)
    old = {n:N.get(m,n) for n in fields}
    ptr = W.address(m.bundle,'EnemyData')
    old_pointer = bytes(m[ptr:ptr+2])
    assert not N.get(m,'Enemy_Flag',4)
    N.put(m,**fields)
    m[ptr],m[ptr+1] = pointer&255,pointer>>8
    C.Vector.call(m,'ProcessEnemyData',x=4)
    N.put(m,**old)
    m[ptr],m[ptr+1] = old_pointer
    assert N.get(m,'Enemy_ID',4)==GOOMBA and N.get(m,'Enemy_Flag',4)==1
    assert (N.get(m,'Enemy_X_Position',4),N.get(m,'Enemy_PageLoc',4))==(96,0)
    return dict(parser='ProcessEnemyData',source_record='6b06',slot=4,x=96,
                y=N.get(m,'Enemy_Y_Position',4))


def main_hit(trial,work,payload,cookie):
    m = C.menu(trial,1,{'images':{}})
    active_updates = 0
    births, hits, draws = [],[],[]
    draw_snapshot = None
    post_fire = None
    last_flags = [0,0,0]
    for _ in range(650):
        active = tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)
        if active and active_updates==60:
            break
        m.controller_pad = 64 if active and active_updates%16 in (4,5,6) else 0

        def observe(mem,cpu):
            nonlocal draw_snapshot
            if mem.rawtags[1]==3 and cpu.pc==Stock.VECTOR:
                assert C.Common.headers(m)==(cookie,)*2 and m.ram[3][0x1000:0x1000+len(payload)]==payload
            if mem.rawtags[1]==3 and cpu.pc==0x9af5:
                index = cpu.x
                assert not hits and index==N.get(m,'ObjectOffset')
                assert N.get(m,'Enemy_ID',index)==GOOMBA and N.get(m,'Enemy_Flag',index)&0x7f
                assert not N.get(m,'Enemy_State',index)&0x20
                x = m.ram[2][0xb6]
                shot = F.slot(m,x)
                assert not shot[9] and shot[15]==1
                hits.append(dict(epoch=active_updates,slot=index,shot_slot=x,bullet=list(shot[6:8]),
                    enemy=[N.get(m,n,index) for n in ('Enemy_X_Position','Enemy_Y_Position')]))
            if active and draw_snapshot is None and mem.rawtags[1]==226 and cpu.pc==W.address(trial,'JnDraw'):
                if F.slot(m,0xf0)[9]:
                    draw_snapshot = C.Vector.clone(m)
                    draws.append((active_updates,list(F.slot(m,0xf0)[6:8])))

        C.Game.frame(m,observe)
        if active:
            flags = [bool(F.slot(m,x)[9]) for x in F.SLOT]
            births.extend((active_updates,x) for x,a,b in zip(F.SLOT,flags,last_flags,strict=True) if a and not b)
            last_flags = flags
            if active_updates==4:
                assert flags==[False,False,True]
                post_fire = C.Vector.clone(m)
            active_updates += 1
    assert not hits and post_fire is not None and draw_snapshot is not None
    m = post_fire
    enemy = native_goomba(m)
    for active_updates in range(5,29):
        m.controller_pad = 0
        C.Game.frame(m,observe)
        if hits:
            assert len(hits)==1 and hits[0]['slot']==enemy['slot']
            i = hits[0]['slot']
            hits[0]['defeated_state'] = N.get(m,'Enemy_State',i)
            hits[0]['score_control'] = N.get(m,'FloateyNum_Control',i)
            assert hits[0]['defeated_state']&0x20 and hits[0]['score_control']==1,hits
            break
    assert len(hits)==1,(births,hits,draws,active_updates)
    assert N.get(m,'NumberofLives')==2
    return draw_snapshot,dict(unchanged_origin_Main_without_hit=60,births=births,directed_enemy=enemy,hit=hits[0],lives=2,
        native_draw_snapshot=draws[0],body=[N.get(m,n) for n in ('Player_X_Position','Player_Y_Position')])


def draw_checks(seed,work):
    states = Counter()
    for face in (0,2):
        for rotate,start in ((0,0),(1,0),(1,248),(1,252)):
            m = C.Vector.clone(seed)
            m.raw_page(1,3)
            m.raw_page(2,2)
            N.put(m,CurrentBank=3,CurrentBankC=2,GuestOamRotationActive=rotate,
                RgOamRotation=8,CurrentOAMOffset=start)
            bullet = bytes(F.slot(m,0xf0))
            assert bullet[9] and bullet[15]==1
            m.ram[2][0xa9] = 1|face
            prior = bytes(m[0x200:0x300])
            calls = []

            def observe(c):
                if c.pc==0xa5ba and m.rawtags[1]==132:
                    calls.append(bytes(m.ram[2][0xb7:0xbc]))

            Stock.direct(N.NesMPU(memory=m),work['symbols']['DrawStock'],(0,0,0,0x30),observe)
            assert calls==[bytes((4,40,0x40 if face else 0,0xf8,0xfc))]
            actual = bytes(m[0x200:0x300])
            if start==252:
                assert prior==actual and N.get(m,'CurrentOAMOffset')==252
                states['capacity_refusals'] += 1
                continue
            pos = (start+(8 if rotate else 0))&255
            expected = bytes((bullet[7]-8,40,0x40 if face else 0,bullet[6]-4))
            assert actual[pos:pos+4]==expected
            assert prior[:pos]+prior[pos+4:]==actual[:pos]+actual[pos+4:]
            assert N.get(m,'CurrentOAMOffset')==start+4
            states['stock_OAM_pairs'] += 1
    return dict(states)


def main():
    donor = C.actual_donor()
    base = F.proposal(donor)
    trial,work,payload,cookie,report = proposal(base)
    print('Jay impact and draw proposal',report,flush=True)
    seed,hit = main_hit(trial,work,payload,cookie)
    print(json.dumps(dict(passed=True,flight_parent=base[-1]['image'],proposal=report,native_hit=hit,
        isolated_native_draw=draw_checks(seed,work),donor=donor_hit_and_oam(),
        ROM_written=False,Mesen=False,generated_files=0),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
