"""Check Jay projectile contact across scrolling pages in the CPU model."""

from collections import Counter
from itertools import product
import json

import check_jay_silius_enemy_ammo_1111 as Ammo


C, H, N, W, J = Ammo.C, Ammo.H, Ammo.N, Ammo.W, Ammo.J
ORIGIN = 0xbe30
LIMIT = 0xbfe0
HOOK = 0xb24a
OLD_HOOK = bytes.fromhex('bdb9bf')
SOURCE = H.ROOT / 'tools/reference/jay_silius_world_hit_1111.s'
ENEMY_FIELDS = ('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_Y_HighPos',
                'Enemy_PageLoc','Enemy_X_Position','Enemy_Y_Position')


def assemble(trial, *, native_defeat, origin=ORIGIN):
    aliases = {name: W.address(trial,name) for name in (*ENEMY_FIELDS,'ObjectOffset')}
    linked = C.Jay.build()
    scratch = linked['ram'][2]+7
    aliases.update(ShotRecords=0xbfb0,ShotIndex=0xc0b6,CaptureAmmoDefeat=native_defeat,
        OriginalSoundRequest=linked['symbols']['OriginalSoundRequest'],
        ProjectileX=scratch,ProjectilePage=scratch+1,DeltaX=scratch+2,EnemyPage=linked['probe_index'])
    source = ''.join(f'{name}=${value:04x}\n' for name,value in aliases.items()) + SOURCE.read_text()
    return H.assemble(source,{'WORLD_HIT':(origin,LIMIT-origin)}),aliases


def redirect(program):
    return b'\x4c'+J.u16(program['symbols']['WorldHit'])


def check_loaded(m, program):
    bank = m.ram[3]
    hook = HOOK-0xa000
    jump = redirect(program)
    code = program['images']['WORLD_HIT']
    entry = program['symbols']['WorldHit']-0xa000
    assert bank[hook:hook+3] == jump
    assert bank[entry:entry+len(code)] == code


def isolated_pairs(seed, program, aliases):
    m = C.Vector.clone(seed)
    m.raw_page(1,3)
    m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2)
    sound = C.Jay.build()['ram'][0xd1]
    slot = 0xf0
    record = aliases['ShotRecords']+slot
    counts = Counter()

    def compare(world_x, fraction, shot_y, enemies, expected, shot_live=1):
        for i in range(6):
            m[aliases['Enemy_Flag']+i] = 0
        for i, left, top, flag, kind, state, y_page in enemies:
            values = flag,kind,state,y_page,left>>8,left&255,top
            for name,value in zip(ENEMY_FIELDS,values,strict=True):
                m[aliases[name]+i] = value
        q4 = 16*world_x+fraction
        initial = bytes((q4>>8,q4&255,0,0,0,0,(world_x+107)&255,shot_y,0,shot_live,0,0,0,0,0,1))
        m.ram[2][record-0xc000:record-0xc000+16] = initial
        m[aliases['ObjectOffset']] = 2
        m[sound] = 0
        calls = []

        def observe(cpu):
            if cpu.pc == aliases['CaptureAmmoDefeat']:
                calls.append((cpu.x,cpu.y,m[aliases['ObjectOffset']]))
                cpu.pc = (cpu.stPopWord()+1)&0xffff
                return True

        registers = Ammo.Shot.Stock.direct(N.NesMPU(memory=m),HOOK,(0,slot,0,0x30),observe)
        assert calls == ([] if expected is None else [(expected,)*3]), (world_x,fraction,shot_y,enemies,calls)
        expected_shot = bytearray(initial)
        if expected is not None:
            expected_shot[9] = 0
        assert m.ram[2][record-0xc000:record-0xc000+16] == expected_shot
        assert registers[1] == slot and m[aliases['ObjectOffset']] == 2
        assert m[sound] == (0 if expected is None else 0x1d)

    world_positions = (32,80,236,252,255,256,259,276,510,512,767,768,1024,3067,3072,4075)
    deltas = (-276,-256,-237,-20,-19,-1,0,1,19,20,237,256,276)
    for x, dx, dy, fraction in product(world_positions,deltas,(-20,-19,0,19,20),(0,15)):
        left = x+dx-8
        if left < 0:
            continue
        hit = abs(dx)<20 and abs(dy)<20
        compare(x,fraction,192,[(4,left,184+dy,1,6,0,1)],4 if hit else None)
        category = 'crossing_page' if (left+8)>>8 != x>>8 else 'same_page'
        counts[category+('_hit' if hit else '_miss')] += 1
        if hit and (left+8)>>8 != left>>8:
            counts['enemy_center_carry_hits'] += 1

    for flag,kind,state,y_page,top,live in (
        (0,6,0,1,184,1),(0x80,6,0,1,184,1),(1,7,0,1,184,1),(1,6,0x20,1,184,1),
        (1,6,0,0,184,1),(1,6,0,1,252,1),(1,6,0,1,184,0),
    ):
        compare(260,0,192,[(4,252,top,flag,kind,state,y_page)],None,live)
        counts['guard_misses'] += 1
    compare(0,0,192,[(4,65532,184,1,6,0,1)],None)
    counts['guard_misses'] += 1
    compare(260,8,192,[(3,250,184,1,6,0,1),(5,252,184,1,6,0,1)],5)
    counts['descending_slot_priority'] += 1
    return dict(counts)


def select_spread(m, linked, pause):
    def frame(pad):
        m.controller_pad = pad
        C.Game.frame(m)

    def weapon(field):
        return m.ram[2][field-0xc000]

    for _ in range(8):
        if weapon(pause.PRIVATE['WeaponReady']):
            break
        frame(0)
    selection = linked['fields'][0xb8]
    assert weapon(selection) == 0 and weapon(Ammo.AMMO) == 63
    frame(16)
    assert N.get(m,'GamePauseStatus')&1
    frame(0)
    frame(32)
    assert weapon(selection) == 2
    for _ in range(60):
        frame(0)
        if not N.get(m,'GamePauseTimer') and not N.get(m,'GamePauseStatus')&0x80:
            break
    frame(16)
    assert not N.get(m,'GamePauseStatus')&1 and weapon(selection) == 2
    frame(0)


def native_route(m, linked, aliases, motion, *, cross_page=False, jump_for_spread=False, expect=True):
    fields = linked['motion_fields']
    selection = linked['fields'][0xb8]
    defeat = aliases['CaptureAmmoDefeat'] if expect else 0x9af5
    fired = None
    jumped = None
    hits = []
    for update in range(500 if cross_page else 135):
        x, _, camera = motion.position(m,fields)
        if cross_page:
            target = [256*N.get(m,'Enemy_PageLoc',i)+N.get(m,'Enemy_X_Position',i)+8
                      for i in range(6) if N.get(m,'Enemy_Flag',i)==1 and N.get(m,'Enemy_ID',i)==6]
            ready = x >= 215 and target and min(target) <= 272
            if jump_for_spread and ready and jumped is None:
                jumped = update
            jumping = jumped is not None and update-jumped < 12
            fire = fired is None and ready and (not jump_for_spread or update-jumped == 8)
            m.controller_pad = (1 if x < 215 else 0)|(128 if jumping else 0)|(64 if fire else 0)
        else:
            fire = update%12 == 4 and x > 110
            m.controller_pad = 1|(64 if fire else 0)
        if fire and fired is None:
            fired = update

        def observe(memory, cpu):
            if memory.rawtags[1] != 3 or cpu.pc != defeat:
                return
            enemy = cpu.x
            shot_slot = m.ram[2][aliases['ShotIndex']-0xc000]
            shot = Ammo.Hit.F.slot(m,shot_slot)
            enemy_x = 256*N.get(m,'Enemy_PageLoc',enemy)+N.get(m,'Enemy_X_Position',enemy)+8
            enemy_y = N.get(m,'Enemy_Y_Position',enemy)+8
            shot_x = 16*shot[0]+shot[1]//16
            assert not shot[9] and N.get(m,'ObjectOffset') == enemy
            assert abs(enemy_x-shot_x)<20 and abs(enemy_y-shot[7])<20
            assert N.get(m,'Enemy_ID',enemy) == 6 and N.get(m,'Enemy_Flag',enemy) == 1
            hits.append(dict(update=update,slot=enemy,shot_slot=shot_slot,camera=camera,
                enemy_center=[enemy_x,enemy_y],shot=[shot_x,shot[7]],shot_screen=shot[6],
                velocity=list(shot[4:6]),weapon=m.ram[2][selection-0xc000]))

        C.Game.frame(m,observe)
        assert N.get(m,'GameEngineSubroutine') == 8
        if hits:
            assert len(hits) == 1 and expect
            enemy = hits[0]['slot']
            assert N.get(m,'Enemy_State',enemy)&0x20
            assert N.get(m,'FloateyNum_Control',enemy) == 1
            break
    assert N.get(m,'NumberofLives') == 2 and fired is not None
    if expect:
        assert len(hits) == 1,(fired,update,motion.position(m,fields))
        hit = hits[0]
        assert (hit['enemy_center'][0]//256 != hit['shot'][0]//256) == cross_page,hit
        assert hit['camera'] and hit['shot_screen'] == hit['shot'][0]-hit['camera'],hit
        return dict(first_fire=fired,**hit)
    assert not hits
    assert any(N.get(m,'Enemy_Flag',i)==1 and N.get(m,'Enemy_ID',i)==6
               and N.get(m,'Enemy_PageLoc',i)==1 and not N.get(m,'Enemy_State',i)&0x20 for i in range(6))
    return dict(first_fire=fired,updates=update+1)


def main():
    import compose_jay_silius_1111 as Compose

    raw = Ammo.NIGHTLY.read_bytes()
    assert C.digest(raw) == Ammo.PIN
    image, linked = Compose.proposal(raw)
    motion = Compose.T.Motion
    m, trial, _ = motion.parent(raw=image,pin=C.digest(image),cookie=linked['cookie'])
    program, aliases = assemble(trial,native_defeat=linked['ammo']['symbols']['CaptureAmmoDefeat'])
    check_loaded(m,program)
    matrix = isolated_pairs(m,program,aliases)
    print('World contact matrix',matrix,flush=True)
    stock = native_route(C.Vector.clone(m),linked,aliases,motion)
    print('Natural stock Goomba hit',stock,flush=True)
    cross = native_route(C.Vector.clone(m),linked,aliases,motion,cross_page=True)
    print('Natural cross-page Goomba hit',cross,flush=True)
    spread_machine = C.Vector.clone(m)
    select_spread(spread_machine,linked,Compose.Pause)
    spread = native_route(C.Vector.clone(spread_machine),linked,aliases,motion)
    angled = native_route(spread_machine,linked,aliases,motion,cross_page=True,jump_for_spread=True)
    assert stock['weapon'] == 0 and spread['weapon'] == angled['weapon'] == 2
    assert angled['velocity'] == [72,26]
    legacy = C.Vector.clone(m)
    legacy.ram[3][HOOK-0xa000:HOOK-0xa000+3] = OLD_HOOK
    legacy = native_route(legacy,linked,aliases,motion,expect=False)
    print(json.dumps(dict(passed=True,parent=Ammo.PIN,composed=C.digest(image),stock=stock,cross_page=cross,
        matrix=matrix,legacy_page_one_miss=legacy,
        spread=spread,angled_spread_cross_page=angled,code_bytes=len(program['images']['WORLD_HIT']),
        code_sha256=C.digest(program['images']['WORLD_HIT']),output_files=0),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
