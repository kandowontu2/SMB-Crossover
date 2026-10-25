"""Extract/retarget the original Famicom Parodius player and weapon program.

This produces a component for integration, not a selectable character. Calls
that depend on SMB terrain, enemies, audio or scene exits remain explicit
adapter symbols. Original instruction addresses are retained for differential
tests. The caller supplies the original button encoding (B=fire, A=upgrade).
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

sys.path.append('C:/Users/kando/AppData/Local/Programs/Python/Python314/Lib/site-packages')
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path('C:/NES/Parodius Da! (Japan).nes')
SHA = 'ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a'
FIELDS = ['Type', 'Contact', 'X', 'XF', 'Y', 'YF', 'VX', 'VXF', 'VY', 'VYF',
          'DrawFlags', 'Frame', 'Palette', 'Angle', 'Phase', 'Aux', 'Active',
          'AnimDelay', 'AnimCursor', 'Animation']
ORIGINAL_FIELDS = [0x6200, 0x6230, 0x6260, 0x6290, 0x62c0, 0x62f0,
                   0x6320, 0x6350, 0x6380, 0x63b0, 0x63e0, 0x6410,
                   0x6440, 0x6470, 0x64a0, 0x64d0, 0x6500, 0x6710,
                   0x6740, 0x6770]
RANGES = [(0x8191, 0x83b2), (0x83b2, 0x8493), (0x8493, 0x8785),
          (0x878f, 0x8db1), (0x8db5, 0x90e6), (0x9130, 0x914f),
          (0x9bba, 0x9bd5), (0xc8d7, 0xc8e2), (0xc977, 0xca03)]
EXTERNALS = {0xed8d: 'PnPublishSkin', 0xfe20: 'PnSoundEvent',
             0x9371: 'PnSourceExit', 0x97fc: 'PnBellSpecials',
             0x90e6: 'PnTerrainImpact', 0xc905: 'PnTerrainQuery'}
BRANCH = {'BCC': 'jcc', 'BCS': 'jcs', 'BEQ': 'jeq', 'BNE': 'jne',
          'BMI': 'jmi', 'BPL': 'jpl', 'BVC': 'jvc', 'BVS': 'jvs'}
ENTRY = {0x8191: 'PnNativeBigMotion', 0x824c: 'PnNativeMotion',
         0x83b2: 'PnNativeGear', 0x8493: 'PnNativeWeapons',
         0x8b4b: 'PnNativeVelocity', 0x8c03: 'PnNativeClear',
         0x8c19: 'PnNativeBodyPose', 0x8db8: 'PnNativeSpawn',
         0x9bba: 'PnNativeKill', 0xc977: 'PnNativeSetAnimation',
         0xc98a: 'PnNativeAnimate'}


def source_cpu():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    prg = raw[16:16+128*1024]
    cpu = MPU()
    cpu.memory[0x8000:0xa000] = prg[10*8192:11*8192]
    cpu.memory[0xc000:0xe000] = prg[14*8192:15*8192]
    return raw, cpu


def mappings():
    """Exclusive ship overlay; it never uses additional cartridge WRAM.

    $5D is the existing Vic adapter page. Only its unused actor/history storage
    is reused: player X/Y, capsule storage, frame/entry/death flags and control
    registers are retained. No menu variant or shared inventory is overwritten.
    """
    aliases = {}
    ram = {}
    for index, (native, field) in enumerate(zip(ORIGINAL_FIELDS, FIELDS)):
        if index < 9:
            address, m3 = 0x5c00+index*28, f'RgAudioRam+{index*28}'
        elif index < 18:
            address, m3 = 0x5e00+(index-9)*28, f'MmAudioRamStart+{128+(index-9)*28}'
        else:
            address, m3 = 0x5f00+(index-18)*28, f'MmAudioRamStart+{(index-18)*28}'
        name = 'Pn'+field
        aliases[name] = (address, m3)
        ram[native] = name
    special = {
        0x0640: ('PnHistory', 0x5f40, 'MmAudioRamStart+384'),
        0x0641: ('PnHistory+1', None, None),
        0x6620: ('PnPunch', 0x5d80, None),
        0x66b0: ('PnEnemyIndex', 0x5d41, None),
        0x6530: ('PnEnemyType', 0x5dec, None),
        0x6590: ('PnBigStage', 0x5da9, None),
        0x65c0: ('PnBigTimerHi', 0x5daa, None),
        0x65f0: ('PnBigTimerLo', 0x5dab, None),
        0x76: ('VvGun', None, None), 0x77: ('VvRingCursor', None, None),
        0x78: ('VvMeter', None, None), 0x79: ('VvFlags', None, None),
        0x7a: ('VvSpeed', None, None), 0x7b: ('PnBellFlags', 0x5da8, None),
        0x87: ('PnSkin', 0x5dac, None), 0x8f: ('VvVariant', 0x5fea, None),
        0x40: ('VvFresh', None, None), 0x42: ('VvHeld', None, None),
        0x23: ('VvClock', None, None),
        0x97: ('PnAutoMode', 0x5dad, None),
        0x98: ('PnAutoIndex', 0x5dae, None),
        0x81: ('PnNativeStage', 0x5daf, None),
        0x8b: ('PnNativeStageFlags', 0x5db0, None),
        0x6c: ('PnNativeWindHi', 0x5db1, None),
        0x6d: ('PnNativeWindLo', 0x5db2, None),
        0x65: ('PnNativeScroll', 0x5db3, None),
        0x9d: ('PnNativeRocketWait', 0x5db4, None),
        0x5c: ('PnNativeObjectStart', 0x5db5, None),
        0x60: ('PnNativeStage60', 0x5db6, None),
        0x63: ('PnNativeStage63', 0x5db7, None),
        0x64: ('PnNativeStage64', 0x5db8, None),
    }
    for native, (name, address, m3) in special.items():
        ram[native] = name
        if address is not None:
            aliases[name] = (address, m3)
    for offset, native in enumerate([*range(4,16), 0x15, 0x17, 0x18]):
        name = f'PnScratch{native:02x}'
        ram[native] = name
        aliases[name] = (0x5d68+offset, None)
    ram.update({0: 'M0', 1: 'M1', 2: 'R0', 3: 'R1',
                0x10: 'R4', 0x11: 'R5', 0x12: 'R6', 0x13: 'R7',
                0x6506: 'PnActive+6', 0x650b: 'PnActive+11'})
    aliases['PnHitMask'] = (0x5fc0, 'MmAudioRamStart+64')
    return aliases, ram


def native_animations(cpu):
    word = lambda address: cpu.memory[address]+256*cpu.memory[address+1]
    assert word(0xca03) == 0xce59
    records = []
    for index in range(92):
        pointer = word(0xce59+index*2)
        cursor = pointer
        data = []
        uniform = cpu.memory[pointer] == 0xfd
        if uniform:
            data.extend(cpu.memory[cursor:cursor+2]); cursor += 2
        while True:
            value = cpu.memory[cursor]
            data.append(value); cursor += 1
            if value >= 0xfe:
                break
            if not uniform:
                data.append(cpu.memory[cursor]); cursor += 1
            assert cursor-pointer < 128, (index, hex(pointer))
        records.append(dict(index=index, address=pointer, data=data))
    return records


def generate(output):
    raw, cpu = source_cpu()
    dis = Disassembler(cpu)
    aliases, ram = mappings()
    output.mkdir(parents=True, exist_ok=True)
    lines = ['; Generated original Famicom Parodius player/weapon component.',
             '; Integration callbacks are mandatory; this file alone is not playable.']
    for name, (address, m3) in aliases.items():
        if m3:
            lines += ['.if ::MAPPER_MMC5', f'{name}=${address:04x}', '.else',
                      f'{name}={m3}', '.endif']
        else:
            lines.append(f'{name}=${address:04x}')
    lines += ['.export '+','.join(aliases), '.pushseg', '.segment "VIC_CORE"']
    instructions = []
    starts = set()
    for lo, hi in RANGES:
        pc = lo
        while pc < hi:
            starts.add(pc)
            length, _ = dis.instruction_at(pc)
            assert pc+length <= hi
            pc += length
    for lo, hi in RANGES:
        pc = lo
        while pc < hi:
            length, text = dis.instruction_at(pc)
            mnemonic, _, operand = text.partition(' ')
            assert mnemonic != '???', (hex(pc), text)
            if mnemonic in BRANCH or mnemonic in ('JMP', 'JSR'):
                target = int(operand[1:], 16)
                if target == 0x83b2 and pc < 0x83b2:
                    symbol = 'PnMotionEnd'
                elif target == 0x8493 and pc < 0x8493:
                    symbol = 'PnGearEnd'
                else:
                    symbol = EXTERNALS.get(target, f'Pn{target:04x}')
                    assert target in EXTERNALS or target in starts, (hex(pc), text)
                assembly = BRANCH.get(mnemonic, mnemonic.lower())+' '+symbol
            elif pc == 0xc97b:
                # Group zero is the player/weapon spriteset for every call
                # in these source ranges. The original TYA before this store
                # remains, preserving A/P, without allocating 28 zero bytes.
                assembly = 'nop ; animation group is always zero'
            elif pc == 0xc993:
                assembly = 'lda #0 ; native player/weapon animation group'
            elif operand and not operand.startswith('#') and '$' in operand:
                match = re.search(r'\$([a-fA-F0-9]+)', operand)
                address = int(match[1], 16)
                if address >= 0x8000:
                    assert (0x9153 <= address < 0x9371 or 0x8784 <= address < 0x878f
                            or 0x8db1 <= address < 0x8db5
                            or address in (0xcbd6,0xca03,0xca04)), (hex(pc), text)
                    symbol = f'Pn{address:04x}'
                else:
                    assert address in ram, (hex(pc), text)
                    symbol = ram[address]
                assembly = mnemonic.lower()+' '+operand[:match.start()]+symbol+operand[match.end():]
            else:
                assembly = text.lower()
            lines.append(f'Pn{pc:04x}: {assembly} ; original ${pc:04x}')
            instructions.append(dict(address=pc, source=bytes(cpu.memory[pc:pc+length]).hex(),
                                     source_assembly=text, assembly=assembly))
            pc += length
        if hi == 0x83b2:
            lines.append('PnMotionEnd:rts')
        elif hi == 0x8493:
            lines.append('PnGearEnd:rts')
    for address, name in ENTRY.items():
        lines.extend([f'{name}=Pn{address:04x}', f'.export {name}'])
    lines.append('.popseg')
    (output/'parodius_native.s').write_text('\n'.join(lines)+'\n')
    data = ['; Native velocity, equipment, pose and animation data.',
            '.pushseg', '.segment "VIC_GFX"']
    # All addresses receive labels, so operands may address the second byte
    # of a pointer or a table. The five velocity pointers must relocate.
    pointer_bytes = {0x9163+index*2: cpu.memory[0x9163+index*2]+256*cpu.memory[0x9164+index*2]
                     for index in range(5)}
    for address in [*range(0x8784,0x878f), *range(0x8db1,0x8db5), *range(0x9153, 0x9371)]:
        if address in pointer_bytes:
            value = '<Pn'+format(pointer_bytes[address], '04x')
        elif address-1 in pointer_bytes:
            value = '>Pn'+format(pointer_bytes[address-1], '04x')
        else:
            value = '$'+format(cpu.memory[address], '02x')
        data.append(f'Pn{address:04x}: .byte {value}')
    data.append('Pncbd6: .byte '+','.join(str(v) for v in cpu.memory[0xcbd6:0xccd6]))
    data.extend(['Pnca03: .byte <PnAnimationTable', 'Pnca04: .byte >PnAnimationTable',
                 'PnAnimationTable:'])
    animations = native_animations(cpu)
    data.extend(' .word PnAnimation'+str(row['index']) for row in animations)
    for row in animations:
        data.append('PnAnimation'+str(row['index'])+': .byte '+','.join(str(v) for v in row['data']))
    data.extend(['.export PnAnimationTable', '.popseg'])
    (output/'parodius_data.inc').write_text('\n'.join(data)+'\n')
    manifest = dict(source=str(SOURCE), source_sha256=SHA, playable=False,
                    integration_callbacks=EXTERNALS, entry_points=ENTRY,
                    scope=__doc__, original_ranges=RANGES,
                    ram_symbols=ram, aliases={name:dict(mmc5=addr,mmc3=m3) for name,(addr,m3) in aliases.items()},
                    instructions=instructions, animations=animations,
                    adaptations=['Entry separation: motion/gear/weapons are called independently.',
                                 'Native animation group is constant zero for this component.'],
                    output_sha256={name:hashlib.sha256((output/name).read_bytes()).hexdigest()
                                   for name in ('parodius_native.s','parodius_data.inc')})
    (output/'native-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build/verification/parodius-native-ni/component')
    args = parser.parse_args()
    result = generate(args.output)
    print(json.dumps(dict(instructions=len(result['instructions']), animations=len(result['animations']),
                          output=str(args.output), playable=False)))
