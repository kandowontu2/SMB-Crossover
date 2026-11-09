"""Qualify a typed DK Jr callback after genuine native platform positioning."""
from collections import Counter, deque
from itertools import product
from pathlib import Path
import json
import subprocess

import check_dkjr_scroll_publish_1110_v1 as C
from check_mini_visibility_dispatch_1110_v1 import memory

R, V, I, N = C.R, C.V, C.I, C.N
OUT = R.R / 'build/dkjr-native-carry-1110'
BASE = R.R / 'build/dkjr-camera-native-1110/dkjr-private.nes'
SOURCE = R.R / 'tools/reference/dkjr_platform_carry_1110_v1.s'
PROOF = C.OUT / 'camera-proof.json'
NATIVE = C.OUT / 'native/capture/result.json'
START, END = 0xac2a, 0xaca1
SLOT = 2


def link():
    OUT.mkdir(exist_ok=True)
    cfg = OUT/'carry.cfg'
    cfg.write_text('MEMORY{C:start=$AC2A,size=$77,file=%O;}SEGMENTS{CODE:load=C,type=ro;}\n')
    cc = R.R / 'tools/Windows/cc65/bin'
    output = []
    for name in ['old', 'new']:
        obj, data = (OUT / (name + ext) for ext in ['.o', '.bin'])
        command = [cc/'ca65.exe', SOURCE, '-o', obj]
        if name == 'old':
            command.extend(['-D', 'ORIGINAL'])
        subprocess.run(command, check=True)
        subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', data], check=True)
        obj.unlink()
        output.append(data.read_bytes())
    assert all(len(a) == END - START for a in output)
    return output


def proposal():
    raw = BASE.read_bytes()
    camera, native = [json.loads(p.read_text()) for p in [PROOF, NATIVE]]
    assert I.sha(raw) == camera['memory_only_SHA256'] == native['ROM_sha256']
    assert native['first_pipe']['scroll']['qualified'] and native['first_pipe']['source_state'] == 1
    assert native['first_pipe']['reason'] == 'stationary-at-native-pipe-after-source-hop-and-up'
    cookie = bytes.fromhex(camera['cookie'])
    old, new = link()
    prefix = raw[:V.CHR]
    # Exact actual preimages for the sole body-refresh call and B029 writer.
    at = lambda bank, pc: 16 + bank*8192 + (pc & 8191)
    assert prefix.count(bytes.fromhex('202aac')) == 1
    assert prefix[at(71,0xac26):at(71,0xac2a)] == bytes.fromhex('202aac60')
    assert prefix[at(74,0xbf0b):at(74,0xbf0f)] == bytes.fromhex('c927f016')
    assert prefix.count(bytes.fromhex('a9298d6c01a9b08d6d01a9c1')) == 1
    assert prefix[at(65,0xb029):at(65,0xb031)] == bytes.fromhex('a9fb8d6c014cf2a7')
    assert prefix[at(65,0xa772):at(65,0xa776)] == bytes.fromhex('c972b018')
    rows = [dict(physical_PRG=71, file_offset=at(71,START), old_hex=old.hex(), new_hex=new.hex())]
    pages = [817, 833, 847, 856, 867, 881, 882, 883, 959, 960, 961]
    payload = b''.join(raw[V.CHR+p*1024:V.CHR+(p+1)*1024] for p in pages)
    assert cookie == bytes([0xa7, 40, 1]) + bytes.fromhex(I.sha(payload))[:13]
    assert payload[0x6f] == 0x4c
    old_service = payload[0x6f:0x72]
    reject = int.from_bytes(old_service[1:], 'little') - 0xa000
    assert payload[reject:reject+2] == bytes.fromhex('1860')
    data = payload[:0x6f] + bytes.fromhex('4ca5b6') + payload[0x72:]
    new_cookie = cookie[:3] + bytes.fromhex(I.sha(data))[:13]
    rows.extend([dict(physical_CHR=817, file_offset=V.CHR+817*1024+0x6f,
                      old_hex=old_service.hex(), new_hex='4ca5b6'),
                 dict(physical_PRG=65, file_offset=534485, old_hex=cookie.hex(), new_hex=new_cookie.hex())])
    return raw, R.OAM.compose(raw, rows), cookie, new_cookie, rows


def native(m, name, **kwargs):
    cpu = N.NesMPU
    calls = Counter()
    last = deque(maxlen=20)

    class Trace(cpu):
        def step(self):
            pc = self.pc
            tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
            if (tag, pc) in [(199, START), (193, 0xb029), (193,0xaee2), (3,0xb6a5)]:
                calls[f'{tag}:{pc:04x}'] += 1
            last.append([tag, f'{pc:04x}', self.a,self.x,self.y,self.p,self.sp])
            try:
                return super().step()
            except AssertionError as error:
                raise AssertionError((str(error), list(last), dict(calls))) from error

    N.NesMPU = Trace
    try:
        result = N.invoke(m, name, **kwargs)
    finally:
        N.NesMPU = cpu
    return result, calls


def setup(m, owner, variant, engine, top=208, ident=0x25):
    N.put(m, SelectedCharacter=owner, Z2Variant=variant, OperMode=1, OperMode_Task=3,
          GameEngineSubroutine=engine, ObjectOffset=SLOT, TimerControl=0,
          Player_X_Position=40, Player_PageLoc=0, Player_Y_Position=176, Player_Y_HighPos=1,
          ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0, ScreenRight_X_Pos=255, ScreenRight_PageLoc=0)
    for name, value in [('Enemy_Flag',1), ('Enemy_ID',ident), ('Enemy_Y_Position',top),
                        ('Enemy_X_Position',32), ('Enemy_Y_HighPos',1), ('Enemy_PageLoc',0)]:
        m[N.address(m.bundle,name)+SLOT] = value


def registers(row):
    return [row[k] for k in ('A','X','Y','P')]


def foreign(raw, image):
    seeds = []
    for data in [raw, image]:
        b = I.SYMBOLS.bundle()
        b['raw'] = data
        seeds.append(N.fresh(b))
    count = 0
    for owner, variant, engine, p in product([i for i in range(256) if i != 40], [0,1], [8,11], [0x21,0x65]):
        a,b = [V.slim_fork(seed) for seed in seeds]
        for m in [a,b]:
            setup(m, owner, variant, engine, top=192)
            m.writes.clear()
        old = N.invoke(a, 'PositionPlayerOnVPlat', a=83, x=SLOT, y=91, p=p)
        new = N.invoke(b, 'PositionPlayerOnVPlat', a=83, x=SLOT, y=91, p=p)
        assert registers(old) == registers(new) and memory(a) == memory(b), (owner,variant,engine,p)
        count += 1
    return count


def cold(data, cookie):
    original = N.invoke
    seen = []

    def collect(m, name, *args, **kwargs):
        result = original(m, name, *args, **kwargs)
        if name == 'GameCoreRoutine' and not seen:
            seen.append(V.slim_fork(m))
        return result

    N.invoke = collect
    try:
        I.cpu(data, cookie)
    finally:
        N.invoke = original
    assert len(seen) == 1 and seen[0].ram[2][0x8fe] == 2
    return seen[0]


def genuine_event(parent, child):
    cases = Counter()
    for direction, top in product(['vertical', 'horizontal'], [176, 192, 208]):
        entry = 'PositionPlayerOnVPlat' if direction == 'vertical' else 'PositionPlayerOnHPlat'
        pair = [V.slim_fork(m) for m in [parent, child]]
        for m in pair:
            setup(m, 40, 0, 8, top, 0x25 if direction == 'vertical' else 0x28)
            m[3] = 2 if direction == 'horizontal' else 0
        old, _ = native(pair[0], entry, a=83, x=SLOT, y=91, p=0x21)
        new, hits = native(pair[1], entry, a=83, x=SLOT, y=91, p=0x21)
        assert registers(old) == registers(new) and memory(pair[0])[:5] == memory(pair[1])[:5], (direction, top, old, new)
        assert all(hits[k] == 1 for k in ['199:ac2a','193:b029','193:aee2','3:b6a5']), hits
        assert N.get(pair[1],'Player_Y_Position') == top - 32
        assert pair[1].ram[2][0x210] == top - 17 and pair[1].ram[2][0x6b] == 1
        if direction == 'horizontal':
            assert N.get(pair[1],'Player_X_Position') == 42 and pair[1].ram[2][0x213] == 34
        cases[direction] += 1

    for bank, index in product([2,3], range(16)):
        m = V.slim_fork(child)
        setup(m,40,0,8,192)
        m.ram[bank][0x1fe0+index] ^= 0xff
        before = bytes(m.ram[2][:0x900])
        _, hits = native(m, 'PositionPlayerOnVPlat', x=SLOT)
        assert hits['193:b029'] == hits['193:aee2'] == 1 and not hits['3:b6a5']
        assert bytes(m.ram[2][:0x900]) == before
        cases['individual_cookie_reject'] += 1
    return dict(cases)


def active_platform(seed):
    m = V.slim_fork(seed)
    setup(m,40,0,8,208)
    N.invoke(m,'InitEnemyObject',x=SLOT)
    assert N.get(m,'Enemy_ID',SLOT) == 0x25 and N.get(m,'Enemy_Flag',SLOT) > 0
    accumulated = Counter()
    source_heights, native_heights = set(), set()
    for frame in range(1, 49):
        N.put(m, FrameCounter=frame, SavedJoypadBits=0, SavedJoypad1Bits=0,
              VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
        _, hits = native(m,'GameCoreRoutine',x=0,y=0)
        accumulated.update(hits)
        if hits['3:b6a5']:
            y = N.get(m,'Player_Y_Position')
            top = N.get(m,'Enemy_Y_Position',SLOT)
            assert y == top - 32 and m.ram[2][0x210] == top - 17
            source_heights.add(m.ram[2][0x210])
            native_heights.add(y)
        I.C.clear(m)
    return dict(native_updates=48, real_carry_calls=accumulated['3:b6a5'], calls=accumulated,
                source_heights=sorted(source_heights), native_heights=sorted(native_heights))


def main():
    raw, image, cookie, new_cookie, patches = proposal()
    count = foreign(raw, image)
    parent, child = cold(raw, cookie), cold(image, new_cookie)
    cases = genuine_event(parent, child)
    try:
        live = active_platform(child)
    except AssertionError as error:
        live = dict(real_carry_calls=0, terminal=str(error))
    q = dict(passed=live['real_carry_calls'] > 0, ROM_written=False, platform_placement_added=False,
             base_SHA256=I.sha(raw), memory_only_SHA256=I.sha(image), patches=patches, cookie=new_cookie.hex(),
             foreign_full_AXYP_SMC_memory_cases=count, actual_position_cases=cases, active_platform=live,
             vectors_pending=True,
             bindings={p.relative_to(R.R).as_posix(): I.sha(p.read_bytes()) for p in
                       [Path(__file__), SOURCE, BASE, PROOF, NATIVE, R.R/'src/zelda2_link_platform.s']},
             scope='Exact source proposal. Native platform positioning, original DK typed carry and complete owner authentication. No stage placement or native full-route claim.')
    (OUT/'carry-proof.json').write_text(json.dumps(q,indent=2)+'\n')
    print('DK Jr platform',q['passed'],q['memory_only_SHA256'],cases,live,flush=True)


if __name__ == '__main__':
    main()
