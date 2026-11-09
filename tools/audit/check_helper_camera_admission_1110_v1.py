"""Source-link camera-entry helpers on exact installed ddd. No ROM output."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import battletoads_current_loader_controls_v1 as L
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at
import profile_mini_busy_1108_v1 as P

R, N = P.R, P.N
SOURCE = R / 'tools/reference/helper_camera_admission_1110_v1.s'
ROM = R / 'build/mini-sweep-seam-native-1110/candidate.nes'
PIN = 'ddd6e71b42aaed99645a54b64b766b4fb3a32aee5c3b55bfe9b7c552000c94b3'
TH_PARENT = R / 'build/thomas-current-lifts-1102-v2'
TH_KERNEL = next((TH_PARENT / 'sideoutputs').glob('*-kernel.bin'))
TH_STATE = next((TH_PARENT / 'sideoutputs').glob('*-state.bin'))
TH_CHR = 1048592 + 426 * 1024
TH_GATE = 0xb2dd
TH_END = 0xb303
TH_TICK = 0xb2b3
TH_LEFTS = (400, 560, 688, 864, 2560, 2816)
DP_LEFTS = (688, 872)
DP_TICK = 0xb198
DP_END = 0xb32a
DP_SPAN_SHA = 'e4221553057e8bc8bd24ad2e43f61825c3c8efac1560a9c3862ff41f649c04ab'
HP_LOAD_AREA = 0xab65
HP_CONFIGURE = 0xab99
HP_CONFIGURE_RELEASE = 0xab9e
STOP = 0x5b00


def bank_at(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def exact(raw, at, size, sha):
    data = raw[at:at + size]
    assert P.sha(data) == sha, (hex(at), P.sha(data))
    return data


def patch(at, old, new, role):
    assert len(old) == len(new)
    return dict(file_offset=at, old_hex=old.hex(), new_hex=new.hex(), role=role)


def compose(raw, out):
    original = P.bundle(raw)
    assert raw[bank_at(26, HP_LOAD_AREA):bank_at(26, HP_LOAD_AREA) + 3] == bytes.fromhex('8d6a01')
    assert raw[bank_at(26, 0xb173):bank_at(26, 0xb176)] == bytes.fromhex('2098b1')
    assert raw[bank_at(26, 0xb134):bank_at(26, 0xb13b)] == bytes.fromhex('ad0260c922f05d')
    old_dp = exact(raw, bank_at(26, DP_TICK), DP_END - DP_TICK, DP_SPAN_SHA)
    old_kernel, state = TH_KERNEL.read_bytes(), TH_STATE.read_bytes()
    assert len(old_kernel) == len(state) == 8192
    assert raw[TH_CHR:TH_CHR + 6144] == old_kernel[:6144]
    assert raw[TH_CHR + 6144:TH_CHR + 8192] == state[4096:6144]
    cookie_at = P.location(original, 'ThCookie')
    old_cookie = raw[cookie_at:cookie_at + 16]
    assert old_cookie == bytes.fromhex('a70a4001') + hashlib.sha256(old_kernel + state).digest()[:12]

    with tempfile.TemporaryDirectory(prefix='camera-link-', dir=out) as folder:
        tmp = Path(folder)
        cfg, obj, binary, labels = (tmp / f'admit.{ext}' for ext in ('cfg', 'o', 'bin', 'lbl'))
        cfg.write_text('MEMORY { TH:start=$b2dd,size=$26,file=%O; '
                       'DP:start=$b198,size=$192,file=%O,fill=yes,fillval=$ea; } '
                       'SEGMENTS { THOMAS:load=TH,type=ro; GOKU_KARNOV:load=DP,type=ro; }\n')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        code = binary.read_bytes()
        symbols = {cols[2][1:]: int(cols[1], 16) for line in labels.read_text().splitlines()
                   if len(cols := line.split()) == 3}
    assert symbols['DpPlatformTick'] == DP_TICK and symbols['DpPlatformEnd'] <= DP_END
    width = TH_END - TH_GATE
    assert len(code) == width + len(old_dp)
    kernel_offset = TH_GATE - 0xa000
    new_kernel = old_kernel[:kernel_offset] + code[:width] + old_kernel[kernel_offset + width:]
    new_cookie = old_cookie[:4] + hashlib.sha256(new_kernel + state).digest()[:12]
    release_at = bank_at(26, HP_CONFIGURE_RELEASE)
    assert raw[release_at:release_at + 3] == bytes.fromhex('20dcac')
    release = bytes((0x20, symbols['DpConfigureRelease'] & 255, symbols['DpConfigureRelease'] >> 8))
    changes = [
        patch(TH_CHR + kernel_offset, old_kernel[kernel_offset:kernel_offset + width], code[:width],
              'Thomas offscreen camera gate inside existing kernel'),
        patch(cookie_at, old_cookie, new_cookie, 'Thomas full code/state loader cookie'),
        patch(bank_at(26, DP_TICK), old_dp, code[width:], 'Goku and Karnov two independent native slots'),
        patch(release_at, raw[release_at:release_at + 3], release, 'Shared configure cleanup for the two owners'),
    ]
    return install(raw, changes), changes, symbols, new_kernel, state, new_cookie


def call(m, pc, *, x=0, y=0):
    c = cpu_at(m, pc, 232, 0x21, x=x, y=y)
    run(c, lambda z: (z.pc, z.sp) == (STOP, 232))
    return c


def position(m, prefix, x):
    N.put(m, **{prefix + '_PageLoc': (x >> 8) & 255, prefix + '_X_Pos': x & 255})


def geometry(m, camera, player):
    position(m, 'ScreenLeft', camera)
    position(m, 'ScreenRight', camera + 255)
    N.put(m, Player_PageLoc=(player >> 8) & 255, Player_X_Position=player & 255)


def lift_slots(m):
    return {i: (N.get(m, 'Enemy_X_Position', i) + 256 * N.get(m, 'Enemy_PageLoc', i),
                N.get(m, 'Enemy_Y_Position', i), N.get(m, 'Enemy_State', i))
            for i in range(6) if N.get(m, 'Enemy_Flag', i) == 1 and N.get(m, 'Enemy_ID', i) == 0x25}


def fill_actors(m, count):
    for slot in range(count):
        for name, val in (('Enemy_Flag', 1), ('Enemy_ID', 6), ('Enemy_X_Position', 30 + slot),
                          ('Enemy_PageLoc', 0), ('Enemy_State', 0)):
            m[P.address(m.bundle, name) + slot] = val


def thomas_seed(b, expected_kernel, expected_state, cookie):
    m = L.make(b, SelectedCharacter=10, FmAlts=64, CurrentPlayer=0, AreaAddrsLOffset=5)
    old_cookie = ROM.read_bytes()[P.location(b, 'ThCookie'):P.location(b, 'ThCookie') + 16]
    for bank in (2, 3):
        m.ram[bank][0x1fe0:0x1ff0] = old_cookie
    c, low = L.call(m, 'ThLoad')
    assert c.p & 1 and m.ppu_reads > 0
    for bank, expected in ((2, expected_state), (3, expected_kernel)):
        assert m.ram[bank][:0x1fe0] == expected[:0x1fe0]
        assert m.ram[bank][0x1fe0:0x1ff0] == cookie
        assert m.ram[bank][0x1ff0:] == expected[0x1ff0:]
    assert m.ram_writes[:2] == [(3, 0x1fe0, 0), (2, 0x1fe0, 0)]
    assert m.ram_writes[-1] == (2, 0x1fe0, 0xa7)
    reads, writes = m.ppu_reads, len(m.ram_writes)
    warm, _ = L.call(m, 'ThLoad')
    assert warm.p & 1 and (m.ppu_reads, len(m.ram_writes)) == (reads, writes)
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    N.put(m, CurrentBank=3, CurrentBankC=2, TimerControl=0, DisableScreenFlag=0, Mirror_PPUMASK=30,
          OperMode_Task=3, GameEngineSubroutine=8)
    return m, dict(cold_cycles=c.processorCycles, warm_cycles=warm.processorCycles, minimum_SP=low,
                   PPU_reads=reads, previous_cookie_rejected=True)


def dp_seed(b, owner, mode):
    m = N.fresh(b)
    m.raw_page(1, 154)
    N.put(m, CurrentBank=154, SelectedCharacter=owner, CrossoverBehaviorVersion=mode,
          AreaPointer=0x25, WorldNumber=0, LevelNumber=0, GameEngineSubroutine=8,
          TimerControl=0, GamePauseStatus=0, ObjectOffset=4, NmiDisable=255)
    call(m, HP_LOAD_AREA)
    assert [N.get(m, n) for n in ('HpValid', 'HpCount', 'HpArea', 'HpKey', 'HpCharacter', 'HpMode')] == [
        1, 0, 0x25, 0, owner, mode]
    return m


def slot_write(m, name, slot, value):
    m[P.address(m.bundle, name) + slot] = value


def platform_carries(m, slot, x):
    geometry(m, x-100, x+8)
    platform_y = N.get(m, 'Enemy_Y_Position', slot)
    N.put(m, ObjectOffset=slot, GameEngineSubroutine=8, TimerControl=0, Player_State=2,
          Player_Y_Position=platform_y-30, Player_Y_HighPos=1, FrameCounter=1,
          Player_Y_Speed=1, Player_BoundBoxCtrl=0)
    slot_write(m, 'PlatformCollisionFlag', slot, 255)
    N.invoke(m, 'GetPlayerOffscreenBits', x=0)
    N.invoke(m, 'RelativePlayerPosition', x=0)
    N.invoke(m, 'BoundingBoxCore', x=0, y=0)
    N.invoke(m, 'RunLargePlatform', x=slot)
    left, y, _ = lift_slots(m)[slot]
    assert left == x and N.get(m, 'PlatformCollisionFlag', slot) == slot, (
        N.get(m,'SelectedCharacter'),slot,x,
        [N.get(m,'BoundingBox_UL_Corner',i) for i in range(4)],
        [N.get(m,'EnemyBoundingBoxCoord',slot*4+i) for i in range(4)])
    assert N.get(m, 'Player_Y_Position') == y - 32 and N.get(m, 'Player_Y_HighPos') == 1


def qualify(b, th):
    counts = dict(thomas_boundaries=0, thomas_sequence=0, shared_boundaries=0,
                  shared_two_slots=0, shared_cleanup=0, foreign_cleanup=0,
                  native_carry=0)
    for i, left in enumerate(TH_LEFTS):
        for relative in (255, 256, 270, 287, 288, 320):
            for occupied in (0, 5, 6):
                m = L.fork(th)
                m.ram[2][0x838] = 0x3f ^ (1 << i)
                fill_actors(m, occupied)
                geometry(m, left - relative, left - 20)
                call(m, TH_TICK)
                expected = 256 <= relative <= 287 and occupied < 6
                assert lift_slots(m) == ({5: (left,192,0)} if expected else {}), (i,relative,occupied,lift_slots(m))
                assert bool(m.ram[2][0x838] & (1 << i)) == (expected or relative < 256)
                counts['thomas_boundaries'] += 1
    m = L.fork(th)
    m.ram[2][0x838] = 0
    for i,left in enumerate(TH_LEFTS):
        geometry(m, left - 287, left - 400)
        call(m, TH_TICK)
        assert {x for x,_,_ in lift_slots(m).values()} == set(TH_LEFTS[:i+1])
        counts['thomas_sequence'] += 1
    for slot, (left, _, _) in lift_slots(m).items():
        platform_carries(m, slot, left)
        counts['native_carry'] += 1

    for owner in (24,34):
        for mode in (0,1):
            seed = dp_seed(b, owner, mode)
            for i,left in enumerate(DP_LEFTS):
                for relative in (255,256,270,287,288,320):
                    for occupied in (0,5,6):
                        m = slim_fork(seed)
                        slot_write(m, 'HpVisible', 1-i, 1)
                        fill_actors(m, occupied)
                        geometry(m, left - relative, left - 12)
                        call(m, DP_TICK)
                        expected = 256 <= relative <= 287 and occupied < 6
                        assert lift_slots(m) == ({5: (left,208,0x40)} if expected else {}), (owner,mode,i,relative,occupied,lift_slots(m))
                        assert N.get(m, 'ObjectOffset') == 4
                        assert N.get(m, 'HpVisible', i) == int(expected or relative < 256)
                        counts['shared_boundaries'] += 1
            m = slim_fork(seed)
            geometry(m, 688-287, 215)
            call(m, DP_TICK)
            platform_carries(m, 5, 688)
            counts['native_carry'] += 1
            old = lift_slots(m)[5]
            geometry(m, 872-287, 700)
            call(m, DP_TICK)
            assert lift_slots(m) == {4: (872,208,0x40), 5: old}
            assert N.get(m, 'PlatformCollisionFlag', 5) == 5
            assert tuple(N.get(m,'HpActorSlot',i) for i in range(2)) == (6,5)
            assert tuple(N.get(m,'HpActorOwner',i) for i in (5,4)) == (0x83,0x84)
            platform_carries(m, 4, 872)
            counts['native_carry'] += 1
            counts['shared_two_slots'] += 1

            for stale in ('none','id','flag','state','left','page','owner','slot'):
                z = slim_fork(m)
                field, value = {
                    'id':('Enemy_ID',6), 'flag':('Enemy_Flag',2), 'state':('Enemy_State',0),
                    'left':('Enemy_X_Position',0), 'page':('Enemy_PageLoc',4),
                    'owner':('HpActorOwner',2), 'slot':('HpActorSlot',7),
                    'none':(None,None),
                }[stale]
                if field:
                    slot_write(z, field, 1 if stale == 'slot' else 4, value)
                second_before = N.get(z, 'Enemy_Flag', 4)
                N.put(z, SelectedCharacter=0)
                call(z, HP_CONFIGURE)
                assert N.get(z,'Enemy_Flag',5) == 0 and N.get(z,'HpSupport') == 0
                assert N.get(z,'Enemy_Flag',4) == (0 if stale == 'none' else second_before), (owner,mode,stale)
                counts['shared_cleanup'] += 1
            # With the old stage cookie still live, a future pipe destination
            # alone changes neither eligibility nor reciprocal ownership.
            N.put(m, AreaPointer=194)
            before = lift_slots(m)
            call(m, DP_TICK)
            assert lift_slots(m) == before
            N.put(m, AreaAddrsLOffset=6)
            call(m, DP_TICK)
            assert not lift_slots(m) and N.get(m,'HpSupport') == 0

    for owner in (0,1,5,10,23,25,33,35,41):
        results = []
        for rom in (P.bundle(ROM.read_bytes()), b):
            m = N.fresh(rom)
            m.raw_page(1,154)
            N.put(m, CurrentBank=154, SelectedCharacter=owner, AreaPointer=0x25,
                  WorldNumber=0, LevelNumber=0)
            call(m, HP_LOAD_AREA)
            results.append(bytes(m[0x7382:0x73dd]))
        assert results[0] == results[1], owner
        counts['foreign_cleanup'] += 1
    return dict(CPU=counts, spawn_relative_range=[256,287], stage='1-1',
                Thomas_lefts=TH_LEFTS, Goku_Karnov_lefts=DP_LEFTS,
                native_route_pending=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True)
    raw = ROM.read_bytes()
    assert P.sha(raw) == PIN
    image, patches, symbols, kernel, state, cookie = compose(raw, args.output)
    b = P.bundle(image)
    m, th_load = thomas_seed(b, kernel, state, cookie)
    print('Thomas cold loader and assembled layout', th_load, symbols, flush=True)
    result = qualify(b, m)
    q = dict(passed=True, ROM_written=False, parent_SHA256=PIN, expected_memory_only_SHA256=P.sha(image),
             patches=patches, symbols=symbols, thomas_loader=th_load, **result,
             bindings={str(p):P.sha(p.read_bytes()) for p in
                       (Path(__file__), SOURCE, ROM, TH_KERNEL, TH_STATE)})
    (args.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ('bindings','patches')}), flush=True)


if __name__ == '__main__':
    main()
