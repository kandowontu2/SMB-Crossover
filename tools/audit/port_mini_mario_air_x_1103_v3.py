"""Compose original ground and airborne horizontal motion in one NES component."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import struct
import subprocess

from py65.devices.mpu6502 import MPU
import port_mini_mario_ground_x_1103_v2 as G

OUT = G.ROOT / 'build/mini-mario-motion-1103-v3'


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(G.PACKET) as z:
        player = z.read('plugins/PlatformerPlus/engine/src/states/playerstates.c').decode()
        platform = z.read('plugins/PlatformerPlus/engine/src/states/platform.c').decode()
    a = player.index('    //FUNCTION ACCELERATION', player.index('void jump_state('))
    b = player.index('    //FUNCTION X COLLISION', a)
    air = player[a:b]
    a = platform.index('    //C. ACCELERATION', platform.index('void fall_state('))
    b = platform.index('    //D. COLLISIONS', a)
    falling = platform[a:b]
    norm = lambda s: re.sub(r'\s+', '', re.sub(r'//[^\n]*', '', s))
    assert norm(air) == norm(falling), 'Jump/fall original horizontal code must agree'
    air += '\n deltaX = CLAMP(deltaX, -127, 127);\n'
    original_c = (G.OUT/'original-ground-x.c').read_text()
    assert G.sha(original_c.encode()) == '5b2b99f1994cda8282d041ae0b74060152d199baf5ebe572a7c87cdc81c852ea'
    c = replace_once(original_c, 'void original_ground_x(void)',
        'const WORD plat_air_dec = 208;\nuint8_t mode;\nvoid original_ground_x(void)')
    c = replace_once(c, 'static void putword(', 'void original_air_x(void) {\n'+air+'}\nstatic void putword(')
    c = replace_once(c, 'unsigned char in[8], out[6];', 'unsigned char in[9], out[6];')
    c = replace_once(c, 'while (fread(in,1,8,stdin)==8)', 'while (fread(in,1,9,stdin)==9)')
    c = replace_once(c, '        original_ground_x();',
        '        mode=in[8]; if(mode) original_air_x(); else original_ground_x();')
    asm = replace_once(G.ASM, '.export ground_x\nground_x:', '''.export ground_x, air_x
mode = $0209
ground_x:
    lda #0
    sta mode
    jmp start
air_x:
    lda #1
    sta mode
start:''')
    asm = replace_once(asm, '    sta stage\n    lda vel+1\n    bmi coast_negative', '''    sta stage
    lda mode
    beq ground_coast
    jmp air_coast
ground_coast:
    lda vel+1
    bmi coast_negative''')
    asm = replace_once(asm, 'normalized:\n    lda vel+1', '''normalized:
    lda mode
    beq ground_normalized
    lda buttons
    and #4
    beq ground_normalized
    jmp air_run
ground_normalized:
    lda vel+1''')
    asm = replace_once(asm, 'walk_below_cap:\n    lda #0\n    sta stage\n    lda #7', '''walk_below_cap:
    lda #0
    sta stage
    lda mode
    bne restore_sign
    lda #7''')
    asm += r'''
air_run:
    ; Original airborne run immediately clamps the normalized direction.
    ; This intentionally differs from ground's gradual reversal.
    inc vel+1
    lda vel+1
    bmi air_minimum
    beq air_minimum
    cmp #>$15E2
    bcc air_run_ready
    bne air_maximum
    lda vel
    cmp #<$15E2
    bcc air_run_ready
air_maximum:
    lda #<$15E2
    sta vel
    lda #>$15E2
    sta vel+1
    jmp air_run_ready
air_minimum:
    lda #0
    sta vel
    lda #1
    sta vel+1
air_run_ready:
    lda #1
    sta stage
    jmp restore_sign
air_coast:
    lda vel+1
    bmi air_coast_negative
    ora vel
    bne air_coast_positive
    jmp integrate
air_coast_positive:
    sec
    lda vel
    sbc #208
    sta vel
    lda vel+1
    sbc #0
    sta vel+1
    bpl air_coast_done
    jmp zero_velocity
air_coast_negative:
    clc
    lda vel
    adc #208
    sta vel
    lda vel+1
    adc #0
    sta vel+1
    bmi air_coast_done
    jmp zero_velocity
air_coast_done:
    jmp integrate
'''
    (OUT/'original-motion-x.c').write_text(c)
    (OUT/'motion-x.s').write_text(asm)
    (OUT/'motion-x.cfg').write_text((G.OUT/'ground-x.cfg').read_text())
    subprocess.run(['C:/Strawberry/c/bin/gcc.exe', '-std=c11', '-O2', '-Wall', '-Wextra',
        str(OUT/'original-motion-x.c'), '-o', str(OUT/'original-motion-x.exe')], check=True)
    subprocess.run([str(G.CC65/'ca65.exe'), str(OUT/'motion-x.s'), '-o', str(OUT/'motion-x.o')], check=True)
    subprocess.run([str(G.CC65/'ld65.exe'), '-C', str(OUT/'motion-x.cfg'), str(OUT/'motion-x.o'),
        '-o', str(OUT/'motion-x.bin'), '-Ln', str(OUT/'motion-x.lbl')], check=True)
    labels = {line.split()[2].lstrip('.'): int(line.split()[1], 16)
        for line in (OUT/'motion-x.lbl').read_text().splitlines()}
    code = (OUT/'motion-x.bin').read_bytes()
    cases = bytearray()
    modes = []
    for mode in range(2):
        start = len(cases)//9
        for velocity in range(-5602, 5603):
            for buttons in range(8):
                for delta in (-128, 0, 128):
                    cases += struct.pack('<hhBBBBB', velocity, delta, buttons,
                        (velocity + buttons) & 1, (velocity ^ buttons) & 255, 0x55, mode)
        for velocity in (-5602, -3665, -713, -712, -711, -257, -256, -255, -209, -208, -207,
                         -1, 0, 1, 127, 128, 207, 208, 209, 255, 256, 257, 3537, 3665, 5346, 5602):
            for buttons in range(8):
                for attack in (0, 1, 128, 255):
                    for anim in range(256):
                        cases += struct.pack('<hhBBBBB', velocity, 0, buttons, attack, anim, 0xAA, mode)
        modes.append(dict(mode='ground' if mode == 0 else 'jump/fall', cases=len(cases)//9-start))
    reference = subprocess.run([str(OUT/'original-motion-x.exe')], input=cases,
        capture_output=True, check=True).stdout
    count = len(cases)//9
    assert len(reference) == count*6
    cpu = MPU()
    cpu.memory[0x8000:0x8000+len(code)] = code
    digests = [hashlib.sha256(), hashlib.sha256()]
    bounds = [[10**9, 0], [10**9, 0]]
    for i in range(count):
        seed = cases[i*9:i*9+9]
        mode = seed[8]
        cpu.memory[0x200:0x208] = seed[:8]
        cpu.memory[0x209] = 255 - mode  # Entry sets mode itself.
        cpu.pc, cpu.sp, cpu.p = labels['air_x' if mode else 'ground_x'], 0xFD, 0x20|((i&1)*0xC1)
        cpu.memory[0x1FE:0x200] = [0xFF, 0x5A]
        cycle_start = cpu.processorCycles
        steps = 0
        while cpu.pc != 0x5B00:
            cpu.step()
            steps += 1
            assert steps < 200, (i, hex(cpu.pc))
        actual = bytes(cpu.memory[0x200:0x204]+cpu.memory[0x206:0x208])
        expected = reference[i*6:i*6+6]
        assert actual == expected, (i, seed.hex(), actual.hex(), expected.hex())
        assert cpu.sp == 0xFF and cpu.memory[0x209] == mode
        cycles = cpu.processorCycles-cycle_start
        bounds[mode][0] = min(bounds[mode][0], cycles)
        bounds[mode][1] = max(bounds[mode][1], cycles)
        digests[mode].update(actual)
    for i in range(2):
        modes[i] |= dict(cycles=bounds[i], result_sha256=digests[i].hexdigest())
    receipt = dict(passed=True, component='Mini Mario combined ground/jump/fall horizontal motion',
        reference_packet_sha256=G.sha(G.PACKET.read_bytes()), code_sha256=G.sha(code),
        code_bytes=len(code), original_air_snippet_sha256=G.sha(air.encode()),
        source_jump_fall_tokens_identical=True, cases=count, modes=modes,
        scope='Literal upstream C acceleration blocks compiled with host GCC versus assembled 6502. Ground and airborne behaviors remain distinct, including direction reversal, run stage, air deceleration, animation preservation and arithmetic signed delta. In-memory fixtures only.',
        remaining='GB machine-code oracle, complete Main/Y/jump/swim/world collision/native integration/graphics/audio/wall-grab/menu/1-1. No ROM or nightly change.')
    (OUT/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
