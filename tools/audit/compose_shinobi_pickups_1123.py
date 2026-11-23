"""Bind Shinobi's food, weapon upgrade and native stock-item callbacks."""

import argparse
import json
from pathlib import Path
import re
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch

import compose_shinobi_head_effect_1123 as Head


R, H, W, Stock = Head.ROOT, Head.H, Head.W, Head.Stock
OUT = R / 'build/shinobi-pickups-1123'
SOURCE = R / 'tools/reference/shinobi_pickups_1123.s'
SPANS = (
    ('SHINOBI_HEADER_GAP', 0xD12F, 47, 0x8C),
    ('SHINOBI_HEADER_HELP', 0xD163, 12, 0x8C),
    ('SHINOBI_POSE_GAP', 0xD18F, 47, 0xFF),
    ('SHINOBI_POSE_HELP', 0xD1C3, 12, 0xFF),
    ('SHINOBI_CAMERA_ITEMS', 0xD690, 16, None),
)
CAMERA = bytes.fromhex('8d3e05a57538ed1f078d5a0760000000')
HEAD_PIN = 'a6d51fcc3c7e20d0e821f121508287cd4aa2984af462487c6ffd3b1137d519fb'
CANDIDATE = '3ce7788d62e6818bd487f9de49c141d7f7caff28081c80a94388b2aa12371550'
MUSHROOM_RECEIPT = 'f7c4c14bed0167a717b54781d086074ed643a9c75adea7f224c146c30f16d62e'
FULL_REPLAY = R / 'build/shinobi-bbox-candidate-1101-v30/native-full/controller.lua'
FULL_REPLAY_SHA = '18447f60d8f5d33da1aa5846b50bb2473132a98b831d95bdd932696b65e4c545'

# Exact 93f140ba query and box instructions for in-memory parent recovery.
PARENT_QUERY = bytes.fromhex(
    '8a48a506d068a505c9209062c9f0b05e38e9208d09c029f08d04c04a29f08d05c0'
    'a503186d1f078d06c08d0ac0a5046d1d072901f004a9d0d002a9008509a903850a'
    'ad06c04a4a4a4a1865098509ac04c0b1098d04c8aabd36ef2903c901f004a900f00c'
    'a9018d07c08d08c0d002a9ff8d05c868aaad05c860'
)
PARENT_BOX = bytes.fromhex(
    '08488a489848a50348a50448a50548a50648a50748a50848a50948a50a48ad79c3'
    '48ad84c348ad8fc348ad9ac348201db7a200203bb9688d9ac3688d8fc3688d84'
    'c3688d79c3904cad09c0d047ad08c08d5806ad0bc0f004a9ffd003ad0ac08d5a'
    '06ad0cc038e9208d5906ad0dc0e9003004d020f005a9008d5906ad0ec038e920'
    '8d5b06ad0fc0e9003009f015a9ff8d5b06d00ea9ff8d58068d59068d5a068d'
    '5b0668850a68850968850868850768850668850568850468850368a868aa68283860'
)


def link(metadata, out):
    bundle = W.Symbols.bundle()
    names = ('PowerUpType Enemy_State PlayerStatus Square2SoundQueue EraseEnemyObject SetupFloateyNumber '
             'MarioSourcePowerupCollision FarCallCommon FarcallJmpTarget_SMC PlayerFacingDir '
             'Player_X_Position ScreenLeft_X_Pos Player_Pos_ForScroll').split()
    symbols = {name: W.address(bundle, name) for name in names}
    type_at = W.location(bundle, 'MarioSourcePowerupCollision')
    symbols['Bank_MarioSourcePowerupCollision'] = (type_at - 16) // 8192 | 0x80
    assert symbols['MarioSourcePowerupCollision'] == 0xAF71
    assert symbols['Bank_MarioSourcePowerupCollision'] == 0x83
    preamble = '\n'.join(f'{name} = ${value:04x}' for name, value in symbols.items())
    source = SOURCE.read_text()
    source = source.replace('.segment "SHINOBI_HEADER_GAP"', '.segment "SHINOBI_TABLE_WORKERS"')
    start = SPANS[0][1]
    stop = SPANS[3][1] + SPANS[3][2]
    # Keep the helpers in one segment so their branches can cross table runs.
    # The live bytes between those runs remain exactly as on the nightly.
    for i, (name, pc, _, _) in enumerate(SPANS[1:4], 1):
        previous_end = SPANS[i - 1][1] + SPANS[i - 1][2]
        retained = metadata[previous_end - 0xD000:pc - 0xD000]
        gap = ','.join(f'${byte:02x}' for byte in retained)
        marker = f'.res ${previous_end - start:x}-(*-ShPickup),$EA\n.byte {gap}'
        source = Head.Prior.once(source, f'.segment "{name}"', marker)
    source = Head.Prior.once(source, '.segment "SHINOBI_CAMERA_ITEMS"',
                            f'.res ${stop - start:x}-(*-ShPickup),$EA\n.segment "SHINOBI_CAMERA_ITEMS"')
    out.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=out) as tmp:
        work = Path(tmp)
        asm, cfg, obj, output, labels = (work / name for name in ('items.s', 'items.cfg', 'items.o', 'items.bin', 'items.lbl'))
        asm.write_text(preamble + '\n' + source)
        cfg.write_text('''MEMORY {
 TABLES: start=$D12F, size=$A0;
 CAMERA: start=$D690, size=$10;
}
SEGMENTS { SHINOBI_TABLE_WORKERS: load=TABLES, type=ro; SHINOBI_CAMERA_ITEMS: load=CAMERA, type=ro; }
''')
        cc65 = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc65 / 'ca65.exe', asm, '-o', obj], check=True)
        subprocess.run([cc65 / 'ld65.exe', obj, '-C', cfg, '-o', output, '-Ln', labels], check=True)
        compiled = output.read_bytes()
        addresses = {name: int(pc, 16) for pc, name in re.findall(r'^al ([A-Fa-f0-9]+) \.(\S+)$', labels.read_text(), re.M)}
    assert len(compiled) == stop - start + len(CAMERA)
    return compiled, addresses


def chr_page(image, page):
    start = 1048592 + page * 1024
    return image[start:start + 1024]


def recover_parent(image):
    assert H(image) == CANDIDATE
    code = bytearray(Head.carrier(image))
    assert len(PARENT_QUERY) == Head.QUERY_SIZE and len(PARENT_BOX) == 0xc2
    code[0x1501:0x157a] = PARENT_QUERY
    code[0x1af8:0x1bf8] = PARENT_BOX + b'\xea' * 62
    for pc, before in ((0xB301, '2001b5'), (0xB312, '2001b5'), (0xB7B2, '8d10c8'),
                       (0xB809, '20bab3'), (0xB4EC, 'b925d1'), (0xB596, 'b985d1'),
                       (0xB93E, 'b985d1'), (0xB874, 'a901'), (0xA045, '4c6fa04c6fa0')):
        before = bytes.fromhex(before)
        offset = pc - Head.CODE_START
        code[offset:offset + len(before)] = before
    metadata = bytearray(chr_page(image, 516) + chr_page(image, 517))
    for _, pc, size, fill in SPANS:
        offset = pc - 0xD000
        metadata[offset:offset + size] = CAMERA if fill is None else bytes([fill]) * size
    result = bytearray(image)
    for pages, data in ((Head.PAGES, code), ((516, 517), metadata)):
        for i, page in enumerate(pages):
            offset = 1048592 + page * 1024
            result[offset:offset + 1024] = data[i * 1024:(i + 1) * 1024]
    result[Head.COOKIE:Head.COOKIE + 16] = bytes.fromhex('a7240176644bd3a11536a7c7f02d2cd2')
    assert H(result) == Head.CURRENT
    return bytes(result)


def compose(raw, *, out=OUT):
    with patch.object(Head, 'OUT', out):
        head_image, head = Head.compose(raw)
    assert H(head_image) == HEAD_PIN
    code = bytearray(Head.carrier(head_image))
    metadata = bytearray(chr_page(head_image, 516) + chr_page(head_image, 517))
    compiled, addresses = link(metadata, out)
    cursor_start = SPANS[0][1]
    camera_at = SPANS[3][1] + SPANS[3][2] - cursor_start
    for _, pc, size, fill in SPANS:
        at = pc - 0xD000
        assert metadata[at:at + size] == (bytes([fill]) * size if fill is not None else CAMERA)
        cursor = (pc - cursor_start) if fill is not None else camera_at
        metadata[at:at + size] = compiled[cursor:cursor + size]

    def replace(pc, preimage, opcode, target):
        at = pc - Head.CODE_START
        assert code[at:at + len(preimage)] == preimage, hex(pc)
        code[at:at + len(preimage)] = bytes([opcode]) + target.to_bytes(2, 'little')

    table_readers = ((0xD125, (0xB4EC,), 'ShReadHeaderLow'),
                     (0xD185, (0xB596, 0xB93E), 'ShReadPoseOrdinal'))
    for target, pcs, routine in table_readers:
        references = [i + Head.CODE_START for i in range(len(code) - 2)
                      if code[i + 1:i + 3] == target.to_bytes(2, 'little')]
        assert tuple(references) == pcs
        for pc in pcs:
            replace(pc, b'\xb9' + target.to_bytes(2, 'little'), 0x20, addresses[routine])
    for row, routine in ((23, 'ShMature'), (24, 'ShPickup')):
        replace(Head.CODE_START + row * 3, b'\x4c\x6f\xa0', 0x4C, addresses[routine])
    assert code.count(bytes.fromhex('2090d6')) == 1
    assert code[0x1874:0x187A] == bytes.fromhex('a901ae63c38a')
    code[0x1874:0x1876] = bytes.fromhex('38ea')  # Carry for the sole camera caller.

    result = bytearray(head_image)
    for i, page in enumerate(Head.PAGES):
        at = 1048592 + page * 1024
        result[at:at + 1024] = code[i * 1024:(i + 1) * 1024]
    for i, page in enumerate((516, 517)):
        at = 1048592 + page * 1024
        result[at:at + 1024] = metadata[i * 1024:(i + 1) * 1024]
    art = b''.join(chr_page(head_image, page) for page in (503, 504, 505))
    cookie = bytes([167, 36, 1]) + bytes.fromhex(H(code + metadata + art + metadata[1024:]))[:13]
    result[Head.COOKIE:Head.COOKIE + 16] = cookie
    assert H(result) == CANDIDATE and recover_parent(result) == raw
    return bytes(result), dict(labels=addresses, cookie=list(cookie), head=head, ROM_SHA256=CANDIDATE)


def verify_tables(raw, image, binding):
    parent = Head.mapped_memory(raw)
    memory = Head.mapped_memory(image)
    labels = binding['labels']
    cases = 0
    for name, table in (('ShReadPoseOrdinal', 0xD185), ('ShReadHeaderLow', 0xD125)):
        for index in range(96):
            for flags in (0x30, 0x31, 0x70, 0x71):
                result, _ = Head.direct(memory, labels[name], x=4, y=index, p=flags)
                expected = parent[table + index]
                assert result[:3] == (expected, 4, index)
                assert result[3] & 0x7D == flags & 0x7D
                cases += 1
    maturity = 0
    for slot in range(6):
        for state in (0, 1, 6, 17, 127, 128, 192, 255):
            memory[0x1F + slot] = state
            result, _ = Head.direct(memory, labels['ShMature'], x=slot)
            assert result[3] & 1 == int(state >= 128) and memory[0x1F + slot] == state
            maturity += 1
    return dict(pose_and_header_cases=cases, mature_contact_cases=maturity,
                head=Head.verify_controls(raw, image, binding['head']))


def verify_pickup_dispatch(image):
    prior = Head.Prior
    metadata = chr_page(image, 516) + chr_page(image, 517)
    art = b''.join(chr_page(image, page) for page in (503, 504, 505))
    with patch.object(prior, 'PIN', H(image)), patch.object(prior, 'payload',
            lambda candidate: (Head.carrier(candidate), metadata, art)):
        seed = prior.cold(image)
    native = prior.N
    bundle = seed.bundle
    cases = 0
    for slot in range(6):
        for kind in range(4):
            for weapon in ((0, 2, 3, 0x12) if kind == 1 else (0,)):
                machine = native.fork(seed)
                native.put(machine, ObjectOffset=slot, PlayerStatus=1 if kind == 1 else 0,
                           Square2SoundQueue=0, AreaMusicQueue=0, StarInvincibleTimer=0)
                work = machine.ram[2]
                work[0x539], work[0x53A], work[0x42], work[0x752] = 2, 6, weapon, 0
                for name, value in (('Enemy_ID', 46), ('Enemy_Flag', 1), ('Enemy_State', 128),
                                    ('PowerUpType', kind), ('Enemy_Y_HighPos', 1)):
                    machine[W.address(bundle, name) + slot] = value
                native.invoke(machine, 'HandlePowerUpCollision', x=slot)
                assert native.get(machine, 'Enemy_Flag', slot) == 0 and native.get(machine, 'Square2SoundQueue') == 32
                assert native.get(machine, 'FloateyNum_Control', slot) == (11 if kind == 3 else 6)
                if kind == 0:
                    assert (work[0x539], work[0x752], native.get(machine, 'PlayerStatus')) == (6, 1, 1)
                if kind == 1:
                    assert work[0x42] == weapon + int((weapon & 0xF) < 3) and work[0x539] == 2
                if kind == 2:
                    assert native.get(machine, 'StarInvincibleTimer') == 35
                    assert native.get(machine, 'AreaMusicQueue') == 64
                cases += 1
    return dict(native_dispatch_cases=cases, food_refill=True, bounded_source_weapon_tiers=True,
                stock_star_and_life_routed_to_native=True)


def mushroom_program(raw, image, binding):
    once = Head.Prior.once
    text = Head.observer(raw, image, binding)
    text = once(text, 'local function policy()', '''local mushroom, consumed
local function policy()
 if consumed then
  if moves>=consumed.moves+25 and score()>=consumed.score+1000 then
   assert(r('NumberofLives')==2 and r('ShReady')==167 and r('PlayerStatus')==1,
          'Shinobi kept the pickup and both lives through native movement')
   finish(true,'Shinobi collected his authored first Mushroom');return {}end
  return {}
 end''')
    text = once(text, 'elseif p.name==\'SourcePickup\'or p.name==\'NativePickup\'then\n  pickup={entry=p.name,before=p.before,after=s};finish(false,\'Unexpected collector ingress; qualify actual Shinobi reward separately\')',
                '''elseif p.name=='SourcePickup'then
  assert(mature and #heads==1 and #births==1 and heads[1].pointer==0x3d5 and births[1].actor.x==336,
         'Mature Mushroom followed the exact authored block hit')
  assert(s.status==1 and s.health==r('ShMaxHealth') and r('ShFoodUpdate')==1,'Original donor refill and status')
  mushroom={before=p.before,after=s};pickup=mushroom
 elseif p.name=='NativePickup'then
  assert(mushroom and r('Enemy_Flag',p.slot)==0 and r('Square2SoundQueue')==32,
         'Native item erase and grab cue followed the original refill')
  consumed=s''')
    text = once(text, 'local p={name=name,pc=pc,sp=(sp+2)&255,mem=mem,offset=offset,before=state()}',
                "local p={name=name,pc=pc,sp=(sp+2)&255,mem=mem,offset=offset,before=state(),slot=cpu['cpu.x']}")
    text = once(text, 'actual_pickup_passed=false,latest=latest', 'actual_pickup_passed=ok,latest=latest')
    text = once(text, 'C.hooks.QueryReturn=nil', 'C.hooks.QueryReturn=nil\nC.work.ShMaxHealth=0x53a\nC.work.ShFoodUpdate=0x752\nC.ram.Square2SoundQueue=0x104')
    Stock.LuaRuntime().compile(text)
    return text.encode()


def stage_program(image):
    original = FULL_REPLAY.read_bytes()
    assert H(original) == FULL_REPLAY_SHA
    text = original.decode()
    once = Head.Prior.once
    text = once(text, "local function shot(n)local f=assert(io.open(OUTPUT..n..'.png','wb'));f:write(emu.takeScreenshot());f:close()end\n", '')
    text = once(text, "local trace,spawned,matured,got={},false,false,false", "local updates,lastOwner,peakX=0,nil,0")
    text = once(text, "if phase=='play' then\n  pad.right=true;pad.b=false", '''if phase=='play' and r('LevelNumber')==1 and worldx()<144 then pad.right=true end
 if phase=='play' and r('LevelNumber')==0 then
  pad.right=true;pad.b=false''')
    start = text.index('local function finish(reason)')
    end = text.index('emu.addEventCallback(function()', start)
    text = text[:start] + '''local function finish(reason)
 local passed=killed and r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8
   and r('OperMode_Task')==3 and r('NumberofLives')==initialLives and updates>=25 and peakX>=3136
 local fields='{"passed":%s,"reason":"%s","ROM_SHA256":"%s","frames":%d,"world_x":%d,"max_x":%d,'
    ..'"lives":%d,"initial_lives":%d,"updates_in_1_2":%d,"real_enemy_defeat":%s,'
    ..'"level":%d,"engine":%d,"task":%d,"player_state":%d,"y":%d}'
 print('SMB_NATIVE_RECEIPT '..string.format(fields,
    tostring(passed),reason,C.sha,frame,worldx(),peakX,r('NumberofLives'),initialLives,updates,tostring(killed),
    r('LevelNumber'),r('GameEngineSubroutine'),r('OperMode_Task'),r('Player_State'),r('Player_Y_Position')))
 done=true;emu.stop(passed and 0 or 1)
end
''' + text[end:]
    start = text.index('  if age%40==0 then trace')
    end = text.index("  elseif r('NumberofLives')~=initialLives", start)
    text = text[:start] + '''  if r('LevelNumber')==0 then peakX=math.max(peakX,worldx())end
  for slot=0,5 do
   if r('Enemy_Flag',slot)~=0 and r('Enemy_ID',slot)==6 and r('Enemy_State',slot)&32~=0 then killed=true end
  end
  if r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3 then
   local mapped=emu.memType.nesWorkRam
   local owner=emu.read(2*8192+0x800,mapped)
   local tick=emu.read(2*8192+0x553,mapped)
   assert(owner==167,'Live original Shinobi cache in 1-2')
   if lastOwner~=tick then updates=updates+1 end
   lastOwner=tick
   if updates>=25 then finish('Entered 1-2 with 25 active original updates')end
''' + text[end:]
    fields = set(re.findall(r"r\('([A-Za-z0-9_]+)'", text))
    bundle = W.Symbols.bundle()
    header = 'local C=' + Stock.value(dict(sha=H(image))) + '\nlocal L=' + Stock.value({
        name: W.address(bundle, name) for name in sorted(fields)})
    text = header + "\nassert(os.getenv('SMB_STDOUT_ROM_SHA')==C.sha,'Exact Shinobi stage ROM')\n" + text
    assert not any(word in text for word in ('io.open', 'takeScreenshot', 'emu.write', 'emu.setState', 'dofile'))
    Stock.LuaRuntime().compile(text)
    return text.encode()


def downloads_run(raw, image, controller, install=False):
    rom, out = Head.ROM, Stock.OUT
    target, script = out / 'candidate.nes', out / 'controller.lua'
    before = Stock.check(rom)
    parent = raw if install else image
    assert before['ROM_sha256'] == H(parent) and not before['matching_patch_files']
    assert set(out.iterdir()) == {target, script} and target.read_bytes() == parent
    previous = script.read_bytes()
    Head.require_free_workspace(R, rom, allow_interactive=True)
    try:
        assert Stock.check(rom) == before and target.read_bytes() == parent
        if install:
            rom.write_bytes(image)
        installed = Stock.check(rom)
        assert installed['ROM_sha256'] == CANDIDATE and not installed['matching_patch_files']
        script.write_bytes(controller)
        result = Stock.run(script, rom, out / 'capture', CANDIDATE, 220)
        assert result['script_SHA256'] == H(controller) and result['outputs_written'] == 0 and not result['images']
        if install:
            assert result['passed'] and result['receipt_SHA256'] == MUSHROOM_RECEIPT
            target.write_bytes(image)
        assert rom.read_bytes() == target.read_bytes() == image and Stock.check(rom) == installed
        return result
    except BaseException:
        if install:
            if rom.read_bytes() != raw:
                rom.write_bytes(raw)
            if target.read_bytes() != raw:
                target.write_bytes(raw)
            assert Stock.check(rom) == before and target.read_bytes() == raw
        raise
    finally:
        script.write_bytes(previous)
        assert set(out.iterdir()) == {target, script}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--run', action='store_true')
    mode.add_argument('--stage', action='store_true')
    mode.add_argument('--controls', action='store_true')
    mode.add_argument('--install', action='store_true')
    args = parser.parse_args()
    installed = Head.ROM.read_bytes()
    is_current = H(installed) == CANDIDATE
    raw = recover_parent(installed) if is_current else installed
    image, binding = compose(raw, out=Stock.OUT if args.install else OUT)
    binding['checks'] = verify_tables(raw, image, binding)
    if args.controls:
        binding['dispatcher'] = verify_pickup_dispatch(image)
    script = stage_program(image) if args.stage else mushroom_program(raw, image, binding)
    print('SHINOBI PICKUP BINDING ' + json.dumps(dict(binding, script=H(script)), separators=(',', ':')), flush=True)
    if args.run or args.stage or args.install:
        if args.install or is_current:
            result = downloads_run(raw, image, script, install=args.install and not is_current)
        else:
            result = Head.native(raw, image, binding, controller=script)
        print('SHINOBI PICKUP NATIVE ' + json.dumps(result, separators=(',', ':')), flush=True)
        return int(not result['passed'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
