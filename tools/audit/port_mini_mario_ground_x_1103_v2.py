"""Port Mini Mario's original ground acceleration; isolated CPU fixture only."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import struct
import subprocess
import sys

from py65.devices.mpu6502 import MPU

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / 'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1/reference.zip'
OUT = ROOT / 'build/mini-mario-motion-1103-v2'
CC65 = ROOT / 'tools/Windows/cc65/bin'

ASM = r'''
.setcpu "6502"
.segment "CODE"
; Fixture addresses only: no game RAM allocation or native hook is implied.
vel = $0200
delta = $0202
buttons = $0204
attack = $0205
anim = $0206
stage = $0207
dir = $0208
.export ground_x
ground_x:
    lda #0
    sta dir
    lda buttons
    and #3
    bne moving
    lda #0
    sta stage
    lda vel+1
    bmi coast_negative
    ora vel
    bne coast_positive
    jmp integrate
coast_positive:
    lda vel+1
    sec
    sbc #1
    sta vel+1
    bmi zero_velocity
    jmp integrate
zero_velocity:
    lda #0
    sta vel
    sta vel+1
    jmp integrate
coast_negative:
    inc vel+1
    bpl coast_negative_crossed
    jmp integrate
coast_negative_crossed:
    lda vel+1
    ora vel
    bne zero_velocity
    jmp integrate
moving:
    lda buttons
    and #1
    beq normalized
    inc dir
    jsr negate
normalized:
    lda vel+1
    bpl accelerate
    clc
    lda vel
    adc #<$02C8
    sta vel
    lda vel+1
    adc #>$02C8
    sta vel+1
    lda #$FF
    sta stage
    jmp restore_sign
accelerate:
    lda buttons
    and #4
    beq walk
    inc vel+1
    lda vel+1
    cmp #>$15E2
    bcc run_below_cap
    bne cap_run
    lda vel
    cmp #<$15E2
    bcc run_below_cap
cap_run:
    lda #<$15E2
    sta vel
    lda #>$15E2
    sta vel+1
run_below_cap:
    lda #2
    sta stage
    lda attack
    beq run_anim
    lda #7
    bne set_anim
run_anim:
    lda #3
    bne set_anim
walk:
    clc
    lda vel
    adc #$80
    sta vel
    lda vel+1
    adc #0
    sta vel+1
    bne walk_minimum_ok
    lda #0
    sta vel
    lda #1
    sta vel+1
walk_minimum_ok:
    lda vel+1
    cmp #>$0E51
    bcc walk_below_cap
    bne cap_walk
    lda vel
    cmp #<$0E51
    bcc walk_below_cap
cap_walk:
    lda #<$0E51
    sta vel
    lda #>$0E51
    sta vel+1
walk_below_cap:
    lda #0
    sta stage
    lda #7
set_anim:
    sta anim
restore_sign:
    lda dir
    beq integrate
    jsr negate
integrate:
    ; Arithmetic >>8: the signed high byte is the exact integer delta.
    ldx #0
    lda vel+1
    bpl positive_delta
    dex
positive_delta:
    clc
    adc delta
    sta delta
    txa
    adc delta+1
    sta delta+1
    bmi clamp_negative
    bne clamp_positive
    lda delta
    cmp #128
    bcc done
clamp_positive:
    lda #127
    sta delta
    lda #0
    sta delta+1
    rts
clamp_negative:
    cmp #$FF
    bne clamp_low
    lda delta
    cmp #129
    bcs done
clamp_low:
    lda #129
    sta delta
    lda #$FF
    sta delta+1
done:
    rts
negate:
    sec
    lda #0
    sbc vel
    sta vel
    lda #0
    sbc vel+1
    sta vel+1
    rts
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(PACKET) as z:
        raw_source = z.read('plugins/PlatformerPlus/engine/src/states/playerstates.c')
        source = raw_source.decode()
        a = source.index('    //FUNCTION ACCELERATION', source.index('void ground_state('))
        b = source.index('    //FUNCTION X COLLISION', a)
        snippet = source[a:b] + '\n deltaX = CLAMP(deltaX, -127, 127);\n'
        defaults = {f['key']: f.get('defaultValue') for f in json.loads(z.read(
            'plugins/PlatformerPlus/engine/engine.json'))['fields']}
        overrides = {f['id']: f['value'] for f in json.loads(z.read(
            'project/engine_field_values.gbsres'))['engineFieldValues']}
    settings = defaults | overrides
    constants = {k: settings[k] for k in ('plat_turn_acc', 'plat_run_acc', 'plat_run_vel',
        'plat_walk_acc', 'plat_min_vel', 'plat_walk_vel', 'plat_dec')}
    assert constants == dict(plat_turn_acc=712, plat_run_acc=256, plat_run_vel=5602,
        plat_walk_acc=128, plat_min_vel=256, plat_walk_vel=3665, plat_dec=256)
    c = r'''
#include <stdint.h>
#include <stdio.h>
#include <fcntl.h>
#include <io.h>
typedef int8_t BYTE;
typedef int16_t WORD;
#define MIN(a,b) ((a)<(b)?(a):(b))
#define CLAMP(a,b,c) ((a)<(b)?(b):((a)>(c)?(c):(a)))
_Static_assert((-1 >> 8) == -1, "Need arithmetic signed right shift");
struct { uint8_t anim_tick; } PLAYER;
WORD pl_vel_x, deltaX;
BYTE run_stage;
uint8_t buttons, que_attacking;
#define INPUT_LEFT (buttons&1)
#define INPUT_RIGHT (buttons&2)
#define INPUT_PLATFORM_RUN (buttons&4)
''' + ''.join(f'const WORD {k} = {v};\n' for k, v in constants.items()) + \
        'void original_ground_x(void) {\n' + snippet + r'''
}
static void putword(unsigned char *p, int16_t v) { p[0]=(uint16_t)v; p[1]=(uint16_t)v>>8; }
int main(void) {
    unsigned char in[8], out[6];
    _setmode(_fileno(stdin), _O_BINARY); _setmode(_fileno(stdout), _O_BINARY);
    while (fread(in,1,8,stdin)==8) {
        pl_vel_x=(int16_t)(in[0]|in[1]<<8); deltaX=(int16_t)(in[2]|in[3]<<8);
        buttons=in[4]; que_attacking=in[5]; PLAYER.anim_tick=in[6]; run_stage=(int8_t)in[7];
        original_ground_x();
        putword(out, pl_vel_x); putword(out+2, deltaX); out[4]=PLAYER.anim_tick; out[5]=(uint8_t)run_stage;
        if(fwrite(out,1,6,stdout)!=6) return 2;
    }
    return ferror(stdin)?3:0;
}
'''
    (OUT / 'original-ground-x.c').write_text(c)
    (OUT / 'ground-x.s').write_text(ASM)
    (OUT / 'ground-x.cfg').write_text('MEMORY { ROM: start=$8000, size=$4000, file=%O; }\nSEGMENTS { CODE: load=ROM, type=ro; }\n')
    subprocess.run(['C:/Strawberry/c/bin/gcc.exe', '-std=c11', '-O2', '-Wall', '-Wextra',
        str(OUT/'original-ground-x.c'), '-o', str(OUT/'original-ground-x.exe')], check=True)
    subprocess.run([str(CC65/'ca65.exe'), str(OUT/'ground-x.s'), '-o', str(OUT/'ground-x.o')], check=True)
    subprocess.run([str(CC65/'ld65.exe'), '-C', str(OUT/'ground-x.cfg'), str(OUT/'ground-x.o'),
        '-o', str(OUT/'ground-x.bin')], check=True)
    code = (OUT/'ground-x.bin').read_bytes()
    cases = bytearray()
    # Entire supported velocity domain, all L/R/run combinations and three platform deltas.
    for velocity in range(-5602, 5603):
        for buttons in range(8):
            for delta in (-128, 0, 128):
                cases += struct.pack('<hhBBBB', velocity, delta, buttons,
                    (velocity + buttons) & 1, (velocity ^ buttons) & 255, 0x55)
    # Exhaust the animation/attack preservation inputs at every branch boundary.
    for velocity in (-5602, -3665, -713, -712, -711, -257, -256, -255, -1, 0, 1, 127,
                     128, 255, 256, 257, 3537, 3665, 5346, 5602):
        for buttons in range(8):
            for attack in (0, 1, 128, 255):
                for anim in range(256):
                    cases += struct.pack('<hhBBBB', velocity, 0, buttons, attack, anim, 0xAA)
    reference = subprocess.run([str(OUT/'original-ground-x.exe')], input=cases, capture_output=True, check=True).stdout
    count = len(cases)//8
    assert len(reference) == count*6
    cpu = MPU()
    cpu.memory[0x8000:0x8000+len(code)] = code
    min_cycles, max_cycles = 10**9, 0
    digest = hashlib.sha256()
    for i in range(count):
        seed = cases[i*8:i*8+8]
        cpu.memory[0x200:0x208] = seed
        cpu.pc, cpu.sp, cpu.p = 0x8000, 0xFD, 0x20 | ((i & 1) * 0xC1)
        cpu.memory[0x1FE:0x200] = [0xFF, 0x5A]
        cycle_start = cpu.processorCycles
        steps = 0
        while cpu.pc != 0x5B00:
            cpu.step()
            steps += 1
            assert steps < 180, (i, hex(cpu.pc))
        actual = bytes(cpu.memory[0x200:0x204] + cpu.memory[0x206:0x208])
        expected = reference[i*6:i*6+6]
        assert actual == expected, (i, seed.hex(), actual.hex(), expected.hex())
        assert cpu.sp == 0xFF
        cycles = cpu.processorCycles - cycle_start
        min_cycles, max_cycles = min(min_cycles, cycles), max(max_cycles, cycles)
        digest.update(actual)
    receipt = dict(passed=True, component='Mini Mario ground horizontal acceleration and X delta clamp',
        reference_packet_sha256=sha(PACKET.read_bytes()), original_source_sha256=sha(raw_source),
        literal_snippet_sha256=sha(snippet.encode()), compiled_C_sha256=sha(c.encode()),
        code_sha256=sha(code), code_bytes=len(code), settings=constants, cases=count,
        result_sha256=digest.hexdigest(), cycles=[min_cycles, max_cycles],
        scope='Literal preserved upstream C snippet compiled with host GCC compared with assembled 6502; arithmetic signed shift checked. Entire legal ground velocity domain, all simultaneous L/R/run inputs, signed platform deltas, animation/attack branch boundaries. In-memory fixtures only.',
        remaining='Original GB machine-code comparison, complete state/Main and collision integration, Y/jump/swim, native RAM/code allocation, graphics, audio, innate wall-grab if needed, menu admission and 1-1 remain unimplemented. No ROM produced or nightly changed.')
    (OUT/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
