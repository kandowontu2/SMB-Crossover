"""Qualify donor ammo selection and a detached authenticated Jay defeat hook."""
from itertools import product
import json
from pathlib import Path

import check_jay_silius_shotgun_1111 as Shot
import check_jay_silius_stock_hit_draw_1111 as Hit

C, H, N, W, J = Shot.C, Shot.H, Shot.N, Shot.W, Shot.J
D = C.Donor
SOURCE = H.ROOT / 'tools/reference/jay_silius_enemy_ammo_1111.s'
HOST_SOURCE = H.ROOT / 'tools/reference/jay_silius_ammo_host_1111.s'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383'
ORIGIN = 0xb700
FIELDS = {name: 0xc0d0+i for i, name in enumerate((
    'DropRandom', 'DropSourceClock', 'DropSourceRoom', 'DropSourceMode',
    'DropSourceXLo', 'DropCameraXLo', 'DropScreenX', 'DropStage', 'DropTimer',
    'DropVelocityY', 'DropPlayerFlags',
))}
ORIGINAL_INPUTS = (0x16a, 0x167, 0xd3, 0x153, 0x11, 0x31, 0x16)
CONTROL = (0, 0, 0, 0x30)
AMMO = 0xc0be
HOST_ORIGIN, DRAW_ORIGIN = 0xba90, 0xbc80
HOST_LAYOUT = {'AMMOHOST':(HOST_ORIGIN,512),'AMMODRAW':(DRAW_ORIGIN,128)}
ART_PAGE, ART_OFFSET = 216, 672
HOST_FIELDS = {name: 0xc0e0+i for i, name in enumerate((
    'DropWorldXLo','DropWorldXHi','DropWorldYLo','DropWorldYHi','DropNextYLo','DropNextYHi',
    'DropVisibleX','DropVisibleY','DropFlags','DropProbeX','DropProbeYHi',
    'DropCandidateX','DropCandidatePage',
))}


def assemble():
    linked = C.Jay.build()
    assert set(FIELDS.values()).isdisjoint(linked['ram'].values())
    constants = dict(FIELDS, NativeDefeat=0x9af5, WeaponAmmo=AMMO,
                     OriginalSoundRequest=linked['symbols']['OriginalSoundRequest'])
    source = ''.join(f'{k}=${v:04x}\n' for k,v in constants.items()) + SOURCE.read_text()
    program = H.assemble(source, {'AMMODROP': (ORIGIN, 192)})
    return program, linked


def assemble_host(program, linked, *, origin=HOST_ORIGIN, draw_origin=DRAW_ORIGIN):
    bundle = W.Symbols.bundle()
    native = ('FrameCounter','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position')
    constants = {name: W.address(bundle,name) for name in native}
    constants.update(HOST_FIELDS)
    constants.update(FIELDS)
    constants.update({name:program['symbols'][name] for name in (
        'RollAmmoDrop','AdvanceAmmoDrop','AmmoGravity','TouchAmmoDrop')})
    constants.update(CameraPixel=W.address(bundle,'ScreenLeft_X_Pos'),
        CameraPage=W.address(bundle,'ScreenLeft_PageLoc'),CameraXLo=linked['ram'][0x31],
        CameraYHi=linked['ram'][0x32],
        PlayerCenterX=linked['ram'][0x16],PlayerCenterY=linked['ram'][0x17],PlayerFlags=linked['ram'][0x19],
        NativeDefeat=0x9af5,StepStock=0xb154,DrawStock=0xb337,ShotMetasprite=0xc0b7,
        OamOffset=W.address(bundle,'CurrentOAMOffset'),DrawLimit=0xc0bd,
        NativeRender=W.address(bundle,'MetaspriteRenderLoop'),
        QueryY=linked['ram'][2],QueryX=linked['ram'][3],QueryDirection=linked['ram'][2]+2,
        JayHostTile=linked['symbols']['JayHostTile'])
    source = ''.join(f'{k}=${v:04x}\n' for k,v in constants.items()) + HOST_SOURCE.read_text()
    work = H.assemble(source, {'AMMOHOST': (origin,512), 'AMMODRAW': (draw_origin,128)})
    return work, constants


def ammo_art(raw):
    assert C.digest(raw) == D.PIN
    start = 16+8*16384+8*4096+0xfc*16
    pixels = raw[start:start+64]
    assert len(pixels) == 64 and pixels[:32] != pixels[32:]
    return pixels


def stock_donor(raw):
    cpu, _ = C.Motion.Motion.opening(raw)
    m = cpu.memory
    seen = {}
    hits = []
    arc = []
    cells = []
    touch_seed = None
    for epoch in range(125):
        def observe():
            nonlocal touch_seed
            bank, pc = m.code_key(cpu.pc)
            if (bank,pc) == (7,0xe780) and m[0x18] == 9:
                hits.append((epoch,m[0x1f]))
            if (bank,pc) == (6,0x881d):
                seen['kill'] = (epoch,m[0x18],m[0x19],m[0x1e])
                seen['inputs'] = [m[a] for a in ORIGINAL_INPUTS]
            if (bank,pc) == (6,0x882b):
                seen['random'] = cpu.a
            if (bank,pc) == (6,0xa606):
                seen['birth'] = (epoch,m[0x18],m[0x1a],m[0x14],m[0x15])
            if (bank,pc) == (7,0xe7d2) and m[0x18] == 0x22:
                seen.setdefault('first_overlap_test', (epoch,m[0x16],m[0x17]))
                touch_seed = D.fork(cpu) if epoch == 124 else None
            if (bank,pc) == (7,0xc4d2) and m[0x18] == 0x22:
                arc.append((epoch,m[0x12]*256+m[0x13],m[0x15],m[0x16],m[0x17],m[0x1a]))
            if (bank,pc) == (7,0xe56f) and m[0x18] == 0x22:
                assert m.ppu_ctrl & 0x20 and m.chr_pages[0] == 8
                cells.append((epoch,bytes(m.ram[0x200+cpu.x-4:0x200+cpu.x]).hex()))
            if (bank,pc) == (7,0xe82c):
                seen['touch'] = (epoch,m[0x16],m[0x17],m[0xb1])
            if (bank,pc) == (7,0xe845):
                seen['retirement'] = (m[0x19],m[0xb1],m[0xd1])
            cpu.step()
        D.frame(cpu,m,128 + (2 if epoch % 8 == 0 else 0),observe)
    assert hits == [(44,3),(50,2),(55,1),(69,0),(100,3),(105,2),(110,1)], (hits,seen)
    assert seen == dict(kill=(69,0x23,0x1d,48),inputs=[0,242,8,0,152,182,190],
                        random=0x68,birth=(93,0x22,128,0,192),
                        first_overlap_test=(94,152,156),touch=(124,107,160,63),
                        retirement=(0,63,0x18)),seen
    assert touch_seed is not None
    assert len(arc) == 32 and len(cells) == 31
    for age, (epoch, y, velocity, screen_x, screen_y, timer) in enumerate(arc):
        assert (epoch,y,velocity,timer) == (
            93+age,2564-64*age+2*age*(age+1),(192+4*age)&255,128-age//2)
        assert screen_y == y//16
        if age:
            cell = bytes.fromhex(cells[age-1][1])
            assert cells[age-1][0] == epoch
            assert (cell[0],cell[3]) == (screen_y-8,screen_x)
            assert cell[1] in (0xfc,0xfe) and cell[2] in (0x40,0xc0)
    seen['arc'] = dict(samples=len(arc),birth_y_Q4=arc[0][1],apex_y_Q4=min(row[1] for row in arc),
                       collected_y_Q4=arc[-1][1],OAM_cells=len(cells),tiles=[0xfc,0xfe],
                       trace_sha256=C.digest(json.dumps((arc,cells),separators=(',',':')).encode()))
    return seen, touch_seed


def direct(cpu, pc, a=0, x=0):
    return Shot.Stock.direct(cpu,pc,(a,x,CONTROL[2],CONTROL[3]))


def qualify(raw, program, linked, donor):
    src = D.DonorBus(raw)
    src.low_bank = 6
    original = D.NesMPU(memory=src)
    src.cpu = original
    memory = [0]*65536
    memory[ORIGIN:ORIGIN+len(program['images']['AMMODROP'])] = program['images']['AMMODROP']
    worker = N.NesMPU(memory=memory)
    for name, data in linked['images'].items():
        assert name == 'PRIVATE'
        memory[0xa000:0xa000+len(data)] = data
    symbols = program['symbols']
    first = FIELDS['DropRandom']
    stage = FIELDS['DropStage']
    timer = FIELDS['DropTimer']
    velocity = FIELDS['DropVelocityY']
    flags = FIELDS['DropPlayerFlags']
    roll_count = 0
    for seed, axes, guard, busy in product(range(256),range(4),range(3),range(2)):
        params = (seed, (0,242,255,63)[axes], (8,12,8)[guard], guard == 2,
                  (0,152,32,16)[axes], (0,24,255,128)[axes], (0,190,255,99)[axes])
        for address,value in zip(ORIGINAL_INPUTS,params,strict=True):
            src[address] = value
        src[0x19] = 0x1d
        memory[first:first+7] = params
        memory[stage],memory[timer] = (0x22,77) if busy else (0,0)
        direct(original,0x881d)
        direct(worker,symbols['RollAmmoDrop'])
        assert memory[first] == src[0x16a],(params,busy)
        expected = (0x22,77) if busy else (0x23,24) if src[0x19]&0x40 else (0,0)
        assert (memory[stage],memory[timer]) == expected,(params,busy,src[0x19])
        roll_count += 1

    memory[stage],memory[timer],memory[velocity] = 0x23,24,0
    for age in range(1,25):
        direct(worker,symbols['AdvanceAmmoDrop'])
        assert (memory[stage],memory[timer],memory[velocity]) == (
            (0x23,24-age,0) if age < 24 else (0x22,128,0xc0))
    for age in range(1,257):
        memory[FIELDS['DropSourceClock']] = age&1
        direct(worker,symbols['AdvanceAmmoDrop'])
        assert (memory[stage],memory[timer]) == (0x22 if age < 256 else 0,128-age//2)

    for v in range(256):
        memory[velocity] = src[0x15] = v
        direct(original,0xe20e)
        direct(worker,symbols['AmmoGravity'])
        assert memory[velocity] == src[0x0b]

    touch_count = 0
    for tier, dx, dy, count in product((0,8), (0,11,12,17,18,255), (0,11,12,17,18,255), (0,17,46,47,62,63)):
        old = D.fork(donor)
        src = old.memory
        # Keep a visible same-screen center and compare unsigned host magnitudes.
        src[0x16] = src[0x17] = 20
        src[0x506],src[0x507] = (20+dx if dx < 255 else 240,20+dy if dy < 255 else 240)
        src[0x509],src[0xb1],src[0xd1] = tier,count,0
        src[0],src[1] = 18,18
        memory[stage],memory[flags],memory[AMMO] = 0x22,tier,count
        direct(old,0xe7d2)
        result = direct(worker,symbols['TouchAmmoDrop'],dx,dy)
        claimed = dx < 18 and dy < (12 if tier else 18)
        assert (bool(result[3]&1),bool(src[0x17c]),not src[0x19]) == (claimed,)*3
        assert (memory[AMMO],memory[stage]) == (src[0xb1],0 if claimed else 0x22)
        touch_count += 1
    return dict(roll_pairs=roll_count,actor_ticks=280,gravity_pairs=256,touch_pairs=touch_count)


def host_defeat(raw, program, source_inputs):
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    m = C.menu(bundle,1,{'images':{}})
    for _ in range(650):
        if tuple(N.get(m,k) for k in ('OperMode','OperMode_Task','GameEngineSubroutine')) == (1,3,8):
            break
        m.controller_pad = 0
        C.Game.frame(m)
    else:
        raise AssertionError('Jay never reached the active engine')
    for epoch in range(5):
        m.controller_pad = 64 if epoch == 4 else 0
        C.Game.frame(m)
    assert C.Common.headers(m) == (Shot.COOKIE,)*2
    assert Hit.F.slot(m,0xf0)[9]
    birth = Hit.native_goomba(m)
    baseline = m
    m = C.Vector.clone(baseline)
    mapped = m.ram[3]
    start,end = 0x1200,0x1400
    original_jsr = bytes.fromhex('20f59a')
    found = [at for at in range(start,end) if mapped[at:at+3] == original_jsr]
    assert len(found) == 1,found
    at, = found
    hook = program['symbols']['RecordAmmoDefeat']
    data = program['images']['AMMODROP']
    origin = ORIGIN-0xa000
    assert bytes(mapped[origin:origin+len(data)]) == bytes(len(data))
    mapped[origin:origin+len(data)] = data
    mapped[at+1:at+3] = hook.to_bytes(2,'little')
    first = FIELDS['DropRandom']-0xc000
    assert m.ram[2][first:first+16] == bytes(16)
    m.ram[2][first:first+7] = bytes(source_inputs)
    hits = []
    for epoch in range(5,29):
        calls = []
        def observe(mem,cpu):
            if mem.rawtags[1] == 3 and cpu.pc == 0x9af5:
                calls.append((cpu.a,cpu.x,cpu.y,cpu.p))
        for machine in (baseline,m):
            machine.controller_pad = 0
            C.Game.frame(machine,observe)
        assert tuple(m.rawtags) == tuple(baseline.rawtags)
        assert C.Common.headers(m) == C.Common.headers(baseline) == (Shot.COOKIE,)*2
        assert bytes(m[:0x800]) == bytes(baseline[:0x800])
        for bank, (actual, expected) in enumerate(zip(m.ram, baseline.ram, strict=True)):
            if bank not in (2,3):
                assert actual == expected, bank
        assert m.ram[2][:first] == baseline.ram[2][:first]
        assert m.ram[2][first+len(FIELDS):] == baseline.ram[2][first+len(FIELDS):]
        normalized_code = bytearray(m.ram[3])
        normalized_code[origin:origin+len(data)] = baseline.ram[3][origin:origin+len(data)]
        normalized_code[at+1:at+3] = baseline.ram[3][at+1:at+3]
        assert normalized_code == baseline.ram[3]
        if calls:
            assert len(calls) == 2 and calls[0] == calls[1],calls
            assert m.ram[2][first] == 0x68
            assert list(m.ram[2][first+7:first+9]) == [0x23,24]
            hits.append(epoch)
            break
        assert m.ram[2][first] == source_inputs[0] and not m.ram[2][first+7]
    assert len(hits) == 1 and N.get(m,'NumberofLives') == 2
    assert N.get(m,'Enemy_State',birth['slot'])&0x20
    assert N.get(m,'FloateyNum_Control',birth['slot']) == 1
    return dict(epoch=hits[0],parser=birth,hook_jsr=f'{at+0xa000:04X}',
                identical_native_defeat_regs=list(calls[0]),pending_ticks=24)


def host_pickup(raw, donor, program, linked):
    import check_jay_silius_shotgun_transport_1111 as Transport
    work, aliases = assemble_host(program,linked)
    art = ammo_art(donor)
    at = C.CHR+ART_PAGE*1024+ART_OFFSET
    assert raw[at:at+len(art)] == bytes(len(art))
    with_art = raw[:at]+art+raw[at+len(art):]
    m = Shot.stage_seed(dict(W.Symbols.bundle(),raw=with_art))
    motion, runtime, _, _ = Transport.Motion.assemble(m,m.bundle,origin=0xb800,
                                                    control_tail=True,native_sync=True)
    assert 0xb800+len(motion['images']['HANDOFF']) <= HOST_ORIGIN
    m = Transport.Motion.fixture(m,motion,runtime)
    scope = slice(Shot.Draw.SCOPE-0xa000,Shot.Draw.MUX-0xa000)
    m.ram[3][scope] = Transport.draw_scope(m.bundle,bytes(m.ram[3][scope]))
    m.__class__ = Shot.Draw.DmaBus
    m.dma = None
    drop = program['images']['AMMODROP']
    assert not any(m.ram[3][ORIGIN-0xa000:ORIGIN-0xa000+len(drop)])
    m.ram[3][ORIGIN-0xa000:ORIGIN-0xa000+len(drop)] = drop
    for section, (origin, _) in HOST_LAYOUT.items():
        data = work['images'][section]
        assert not any(m.ram[3][origin-0xa000:origin-0xa000+len(data)])
        m.ram[3][origin-0xa000:origin-0xa000+len(data)] = data
    for address, before, target in (
        (0xb2af,0x9af5,'CaptureAmmoDefeat'),(0xb14e,0xb154,'StepAmmoAndStock'),
        (0xb332,0xb337,'DrawAmmoAndStock'),
    ):
        pos = address-0xa000
        assert m.ram[3][pos:pos+3] == b'\x20'+J.u16(before)
        m.ram[3][pos+1:pos+3] = J.u16(work['symbols'][target])
    snapshots = []
    killed = []
    drawn = []
    defeat_registers = []
    prior_cell = None
    dma_matches = 0
    collected = None

    def read(name):
        return m.ram[2][aliases[name]-0xc000]

    def oam_cells(data):
        return {bytes(data[i:i+4]) for i in range(0,256,4)}

    for epoch in range(160):
        m.controller_pad = 64 if epoch == 4 else 1 if epoch >= 68 else 0
        m.dma = None
        def observe(mem,cpu):
            if mem.rawtags[1] == 3 and cpu.pc == work['symbols']['CaptureAmmoDefeat']:
                killed.append(epoch)
                defeat_registers.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp))
            if mem.rawtags[1] == 3 and cpu.pc == aliases['NativeDefeat']:
                assert defeat_registers == [(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)]
            if mem.rawtags[1] == 132 and cpu.pc == aliases['NativeRender']:
                meta = bytes(m.ram[2][0xb7:0xbc])
                if meta[1] in (0x2a,0x2c) and m[3]+256*m[4] == 0xc0b7:
                    assert meta[0] == 4 and meta[2] in (0x40,0xc0) and meta[3:] == bytes((0xf8,0))
                    drawn.append((epoch,bytes(((m[9]-8)&255,meta[1],meta[2],m[7]))))
        C.Game.frame(m,observe)
        if epoch == 4:
            birth = Hit.native_goomba(m)
        if prior_cell is not None:
            assert m.dma is not None and prior_cell in oam_cells(m.dma)
            assert m.chr_latches[0] == ART_PAGE
            dma_matches += 1
        prior_cell = None
        if drawn and drawn[-1][0] == epoch:
            prior_cell = drawn[-1][1]
            assert prior_cell in oam_cells(m[0x200:0x300])
            frame = (read('DropTimer')>>2)&3
            assert prior_cell == bytes((read('DropVisibleY')-8,
                (0x2a,0x2c,0x2a,0x2c)[frame],(0xc0,0xc0,0x40,0x40)[frame],read('DropVisibleX')))
        snapshots.append((epoch,read('DropStage'),read('DropTimer'),
            read('DropWorldYHi')*256+read('DropWorldYLo'),read('DropVelocityY'),read('DropVisibleX'),
            read('DropVisibleY'),m.ram[2][AMMO-0xc000]))
        if killed and not read('DropStage') and m.ram[2][AMMO-0xc000]:
            collected = epoch
            break
    assert killed == [11] and collected == 100,(killed,collected,snapshots[-4:])
    assert [(row[1],row[2]) for row in snapshots[11:35]] == [(0x23,24-i) for i in range(24)]
    assert snapshots[35][1:5] == (0x22,128,3072,0xc0)
    for i, row in enumerate(snapshots[35:67]):
        assert row[3:5] == (3072-64*i+2*i*(i+1),(192+4*i)&255)
    grounded = next(row for row in snapshots[67:] if row[3:5] == (3200,0))
    assert snapshots[-1][1] == 0 and snapshots[-1][-1] == 16
    assert m.ram[2][linked['ram'][0xd1]-0xc000] == 0x18
    assert N.get(m,'NumberofLives') == 2 and len(drawn) == dma_matches == 64
    assert C.Common.headers(m) == (Shot.COOKIE,)*2
    return dict(code=work['used'],defeat=killed[0],defeat_registers=defeat_registers[0],parser=birth,
        birth=35,world_x=read('DropWorldXLo')+256*read('DropWorldXHi'),
        Y_Q4=[3072,2592,3200],grounded=grounded[0],collected=collected,ammo=16,sound=0x18,
        native_OAM=len(drawn),next_DMA=dma_matches,CHR_page=ART_PAGE,art_sha256=C.digest(art),
        code_sha256={name:C.digest(data) for name,data in work['images'].items()})


def physics_pairs(raw, program, linked):
    work, aliases = assemble_host(program,linked)
    seed = Shot.stage_seed(dict(W.Symbols.bundle(),raw=NIGHTLY.read_bytes()))
    for section, image in program['images'].items():
        seed.ram[3][ORIGIN-0xa000:ORIGIN-0xa000+len(image)] = image
    for section, (origin, _) in HOST_LAYOUT.items():
        image = work['images'][section]
        seed.ram[3][origin-0xa000:origin-0xa000+len(image)] = image
    count = queries_count = blocking = 0
    for y, v, airborne in product((0x880,0xa00,0xafe,0xb00,0xcf0,0xcfe,0xd01,0xeff,0xf00),
                                  (0xc0,0xfc,0,4,0x38,0x3c),(0,4)):
        m = C.Vector.clone(seed)
        initial = dict(DropWorldXLo=104,DropWorldXHi=0,DropWorldYLo=y&255,DropWorldYHi=y>>8,
            DropVelocityY=v,DropStage=0x22,DropTimer=128,DropFlags=airborne|1,
            PlayerCenterX=240,PlayerCenterY=0)
        for key,value in initial.items():
            m.ram[2][aliases[key]-0xc000] = value
        queries = []
        ret = None
        def native(c):
            nonlocal ret
            if c.pc == aliases['JayHostTile']:
                xq,yq,direction = (m[aliases[k]] for k in ('QueryX','QueryY','QueryDirection'))
                lo,hi = (m[0x100+((c.sp+n)&255)] for n in (1,2))
                ret = ((lo+256*hi+1)&0xffff,(c.sp+2)&255,(xq,yq,direction))
            elif ret is not None and (c.pc,c.sp) == ret[:2]:
                queries.append((ret[2],c.a))
                ret = None
        Shot.Stock.direct(N.NesMPU(memory=m),work['symbols']['StepAmmo'],CONTROL,native)
        original_bus = D.DonorBus(raw)
        original_bus.low_bank = 6
        old = D.NesMPU(memory=original_bus)
        original_bus.cpu = old
        for key,value in {0x10:6,0x11:0x80,0x12:y>>8,0x13:y&255,0x14:0,0x15:v,
                          0x19:airborne|1,0x1c:0,0x32:0}.items():
            original_bus[key] = value
        index = 0
        def donor(c):
            nonlocal index,blocking
            if c.pc != 0xd002:
                return False
            expected,value = queries[index]
            index += 1
            assert (original_bus[3],original_bus[2]) == expected[:2],(y,v,airborne,expected,
                original_bus[3],original_bus[2])
            c.a = value
            c.FlagsNZ(value)
            c.pc = c.stPopWord()+1
            blocking += bool(value)
            return True
        Shot.Stock.direct(old,0xe1a4,(0,6,0,0x30),donor)
        assert index == len(queries)
        def read(name):
            return m.ram[2][aliases[name]-0xc000]
        assert (read('DropWorldYHi'),read('DropWorldYLo'),read('DropVelocityY'),read('DropFlags')&4) == (
            original_bus[0x12],original_bus[0x13],original_bus[0x15],original_bus[0x19]&4),(
                y,v,airborne,queries)
        count += 1
        queries_count += len(queries)
    return dict(original_integrations=count,ordered_native_queries=queries_count,blocking_queries=blocking)


def main():
    donor = D.DONOR.read_bytes()
    assert C.digest(donor) == D.PIN
    raw = NIGHTLY.read_bytes()
    assert C.digest(raw) == PIN
    program, linked = assemble()
    trace, touch = stock_donor(donor)
    print('Verified original controller defeat, ammo birth and collection',trace,flush=True)
    result = qualify(donor,program,linked,touch)
    print('Verified detached source pairs',result,flush=True)
    host = host_defeat(raw,program,trace['inputs'])
    terrain = physics_pairs(donor,program,linked)
    pickup = host_pickup(raw,donor,program,linked)
    print(json.dumps(dict(passed=True,parent=PIN,donor=trace,pairs=result,host=host,terrain=terrain,pickup=pickup,
        worker_bytes=len(program['images']['AMMODROP']),code_sha256=C.digest(program['images']['AMMODROP']),
        source_sha256=C.digest(SOURCE.read_bytes()),checker_sha256=C.digest(Path(__file__).read_bytes()),
        host_source_sha256=C.digest(HOST_SOURCE.read_bytes()),
        detached=True,ROM_written=False,Mesen=False,generated_files=0),sort_keys=True))


if __name__ == '__main__':
    main()
