"""Port the literal original jump/fall Y calculations, with hold gravity explicit."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import struct
import subprocess

from py65.devices.mpu6502 import MPU
import port_mini_mario_ground_x_1103_v2 as G

OUT = G.ROOT/'build/mini-mario-motion-1103-v5'
CHECKPOINT = G.ROOT/'docs/qa/checkpoints/2026-11-03/mini-mario-motion-v4/inputs.zip'

Y_ASM = r'''
.export air_y
yvel = $0220
ydelta = $0222
hold = $0224
ybuttons = $0225
bounce = $0226
nocollide = $0227
queued = $0228
attached = $0229
holdgrav = $022A
boost = $022C
threshold = $022E
ymode = $0230
air_y:
    lda ymode
    bne jumping
    lda nocollide
    beq fall_gravity
    lda #<$1B58
    sta yvel
    lda #>$1B58
    sta yvel+1
    jmp y_integrate
fall_gravity:
    lda ybuttons
    and #1
    beq fall_normal
    lda yvel+1
    bpl fall_normal
    jsr add_hold_gravity
    jmp fall_cap
fall_normal:
    clc
    lda yvel+1
    adc #8
    sta yvel+1
fall_cap:
    lda yvel+1
    bmi fall_done
    cmp #$20
    bcc fall_done
    bne cap_fall
    lda yvel
    beq fall_done
cap_fall:
    lda #0
    sta yvel
    lda #$20
    sta yvel+1
fall_done:
    jmp y_integrate
jumping:
    lda hold
    beq after_pulse
    lda ybuttons
    and #1
    ora bounce
    beq after_pulse
    jmp pulse
after_pulse:
    lda ybuttons
    and #1
    beq jump_not_held
    lda yvel+1
    bpl jump_not_held
    jsr add_hold_gravity
    jmp y_integrate
jump_not_held:
    lda yvel+1
    bmi jump_gravity
    lda #0
    sta queued
    sta attached
jump_gravity:
    clc
    lda yvel+1
    adc #8
    sta yvel+1
    jmp y_integrate
pulse:
    sec
    lda yvel+1
    sbc #$30
    sta yvel+1
    ; The shipped settings normalize jump force to12288 and reduction to0.
    lda vel+1
    bpl boost_abs
    eor #$FF
    clc
    adc #1
boost_abs:
    sta boost
    lda #0
    sta boost+1
    lda bounce
    beq scale_boost
    asl boost
    rol boost+1
scale_boost:
    ldx #5
boost_loop:
    asl boost
    rol boost+1
    dex
    bne boost_loop
    ; Original signed threshold test also saturates the -32768 boundary.
    lda yvel+1
    cmp #$80
    bne boost_threshold
    lda yvel
    beq saturate_jump
boost_threshold:
    clc
    lda yvel
    adc #$FF
    sta threshold
    lda yvel+1
    adc #$7F
    sta threshold+1
    lda boost+1
    cmp threshold+1
    bcc subtract_boost
    bne saturate_jump
    lda boost
    cmp threshold
    bcc subtract_boost
    beq subtract_boost
saturate_jump:
    lda #1
    sta yvel
    lda #$80
    sta yvel+1
    jmp pulse_done
subtract_boost:
    sec
    lda yvel
    sbc boost
    sta yvel
    lda yvel+1
    sbc boost+1
    sta yvel+1
pulse_done:
    dec hold
y_integrate:
    ldx #0
    lda yvel+1
    bpl y_positive_delta
    dex
y_positive_delta:
    clc
    adc ydelta
    sta ydelta
    txa
    adc ydelta+1
    sta ydelta+1
    bmi y_clamp_negative
    bne y_clamp_positive
    lda ydelta
    cmp #128
    bcc y_done
y_clamp_positive:
    lda #127
    sta ydelta
    lda #0
    sta ydelta+1
    rts
y_clamp_negative:
    cmp #$FF
    bne y_clamp_low
    lda ydelta
    cmp #129
    bcs y_done
y_clamp_low:
    lda #129
    sta ydelta
    lda #$FF
    sta ydelta+1
y_done:
    rts
add_hold_gravity:
    clc
    lda yvel
    adc holdgrav
    sta yvel
    lda yvel+1
    adc holdgrav+1
    sta yvel+1
    rts
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ZipFile(G.PACKET) as z:
        player = z.read('plugins/PlatformerPlus/engine/src/states/playerstates.c').decode()
        platform = z.read('plugins/PlatformerPlus/engine/src/states/platform.c').decode()
    a = player.index('    //Add jump force during each jump frame', player.index('void jump_state('))
    b = player.index('    temp_y = PLAYER.pos.y;', a)
    jump = player[a:b]
    a = platform.index('    //FLOAT INPUT', platform.index('void fall_state('))
    b = platform.index('    //Collision ', a)
    fall = platform[a:b]
    integration = '    deltaY += pl_vel_y >> 8;\n'
    assert integration in player and integration in platform
    jump += integration
    fall += integration
    with ZipFile(CHECKPOINT) as z:
        previous = z.read('build/mini-mario-motion-1103-v3/motion-x.bin')
        asm = z.read('build/mini-mario-motion-1103-v3/motion-x.s').decode()+Y_ASM
        cfg = z.read('build/mini-mario-motion-1103-v3/motion-x.cfg').decode()
    assert G.sha(previous) == 'd65ee8cf327646fdee069561a18278b1afa361d105322624d34aa8c19bf2ba17'
    prefix = r'''
#include <stdint.h>
#include <stdio.h>
#include <fcntl.h>
#include <io.h>
typedef int16_t WORD;
typedef uint8_t UBYTE;
#define FALSE 0
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define CLAMP(a,b,c) ((a)<(b)?(b):((a)>(c)?(c):(a)))
#define INPUT_PLATFORM_JUMP (buttons&1)
#define INPUT_UP (buttons&2)
#define FALL_INIT 0
const WORD plat_jump_vel=12288, jump_per_frame=12288, boost_val=32;
const WORD jump_reduction_val=0, plat_grav=2048, plat_max_fall_vel=8192, plat_float_grav=912;
const UBYTE plat_float_input=0;
WORD pl_vel_x, pl_vel_y, deltaY, plat_hold_grav;
UBYTE hold_jump_val, buttons, enemy_bounce, nocollide, que_state, actor_attached;
_Static_assert((-1>>8)==-1, "arithmetic signed shift required");
'''
    c = prefix+'void original_jump_y(void) {\n'+jump+'}\nvoid original_fall_y(void) {\n'+fall+r'''
}
static void word(unsigned char *p,int16_t v) { p[0]=(uint16_t)v; p[1]=(uint16_t)v>>8; }
int main(void) {
    unsigned char in[15], out[7];
    _setmode(_fileno(stdin),_O_BINARY); _setmode(_fileno(stdout),_O_BINARY);
    while(fread(in,1,15,stdin)==15) {
        pl_vel_x=(int16_t)(in[0]|in[1]<<8); pl_vel_y=(int16_t)(in[2]|in[3]<<8);
        deltaY=(int16_t)(in[4]|in[5]<<8); hold_jump_val=in[6]; buttons=in[7];
        enemy_bounce=in[8]; nocollide=in[9]; que_state=in[10]; actor_attached=in[11];
        plat_hold_grav=(int16_t)(in[12]|in[13]<<8);
        if(in[14]) original_jump_y(); else original_fall_y();
        deltaY=CLAMP(deltaY,-127,127);
        word(out,pl_vel_y); word(out+2,deltaY); out[4]=hold_jump_val; out[5]=que_state; out[6]=actor_attached;
        if(fwrite(out,1,7,stdout)!=7) return 2;
    }
    return ferror(stdin)?3:0;
}
'''
    (OUT/'original-air-y.c').write_text(c)
    (OUT/'motion-xy.s').write_text(asm)
    (OUT/'motion-xy.cfg').write_text(cfg)
    subprocess.run(['C:/Strawberry/c/bin/gcc.exe','-std=c11','-O2','-Wall','-Wextra',
        str(OUT/'original-air-y.c'),'-o',str(OUT/'original-air-y.exe')],check=True)
    subprocess.run([str(G.CC65/'ca65.exe'),str(OUT/'motion-xy.s'),'-o',str(OUT/'motion-xy.o')],check=True)
    subprocess.run([str(G.CC65/'ld65.exe'),'-C',str(OUT/'motion-xy.cfg'),str(OUT/'motion-xy.o'),
        '-o',str(OUT/'motion-xy.bin'),'-Ln',str(OUT/'motion-xy.lbl')],check=True)
    code = (OUT/'motion-xy.bin').read_bytes()
    assert code[:len(previous)] == previous, 'All already-qualified X bytes must remain identical'
    labels = {line.split()[2].lstrip('.'):int(line.split()[1],16)
        for line in (OUT/'motion-xy.lbl').read_text().splitlines()}
    cases = bytearray()
    def add(x,y,dy,held,buttons,bounce,nocollide,gravity,mode):
        cases.extend(struct.pack('<hhhBBBBBBhB',x,y,dy,held,buttons,bounce,nocollide,13,1,gravity,mode))
    for mode in range(2):
        for y in range(-16384,8193):
            for buttons in range(2):
                for gravity in (0,2048):
                    for held in (range(2) if mode else (0,)):
                        add(5602 if y&1 else -5602,y,(-128,0,128)[y%3],held,buttons,y&1,0,gravity,mode)
    for y in (-20480,-20479,-20478,-20000,-19359,-19358,-19357,-1,0,1,8191,8192):
        for x in (-5602,-3665,-257,-256,-255,-1,0,1,255,256,257,3665,5602):
            for bounce in range(2):
                for held in (0,1,2,255):
                    for buttons in range(4):
                        for gravity in (0,512,1024,2048):
                            add(x,y,0,held,buttons,bounce,0,gravity,1)
    for mode in range(2):
        for y in (-20480,-16384,-1,0,1,8192):
            for nc in (1,2,255):
                for buttons in range(4):
                    add(-5602,y,128,1,buttons,0,nc,2048,mode)
    reference = subprocess.run([str(OUT/'original-air-y.exe')],input=cases,capture_output=True,check=True).stdout
    count = len(cases)//15
    assert len(reference)==count*7
    cpu = MPU()
    cpu.memory[0x8000:0x8000+len(code)] = code
    digest = hashlib.sha256()
    bounds = [10**9,0]
    saturations = 0
    for i in range(count):
        seed = cases[i*15:i*15+15]
        cpu.memory[0x200:0x202] = seed[:2]
        cpu.memory[0x220:0x22C] = seed[2:14]
        cpu.memory[0x230] = seed[14]
        cpu.pc,cpu.sp,cpu.p = labels['air_y'],0xFD,0x20|((i&1)*0xC1)
        cpu.memory[0x1FE:0x200] = [0xFF,0x5A]
        cycle_start = cpu.processorCycles
        steps = 0
        while cpu.pc!=0x5B00:
            cpu.step()
            steps += 1
            assert steps<220, (i,hex(cpu.pc))
        actual = bytes(cpu.memory[0x220:0x225]+cpu.memory[0x228:0x22A])
        expected = reference[i*7:i*7+7]
        assert actual==expected, (i,seed.hex(),actual.hex(),expected.hex())
        assert cpu.sp==0xFF and bytes(cpu.memory[0x200:0x202])==seed[:2]
        digest.update(actual)
        cycles = cpu.processorCycles-cycle_start
        bounds[0],bounds[1] = min(bounds[0],cycles),max(bounds[1],cycles)
        saturations += actual[:2]==b'\x01\x80'
    receipt = dict(passed=True,component='Mini Mario combined X and jump/fall Y arithmetic',
        original_packet_sha256=G.sha(G.PACKET.read_bytes()), code_bytes=len(code),
        Y_added_bytes=len(code)-len(previous),code_sha256=G.sha(code),X_prefix_unchanged=True,
        literal_jump_snippet_sha256=G.sha(jump.encode()),literal_fall_snippet_sha256=G.sha(fall.encode()),
        cases=count,cycles=bounds,saturation_cases=saturations,result_sha256=digest.hexdigest(),
        retained_fixture_negative=dict(case=0,seed='1eea00c08000000000000d01000000',
            actual='00c84800000d01',old_oracle='00c87f00000d01',
            cause='Initial C slice stopped before the original delta integration line. The successor includes that literal line in both original functions; no6502change.'),
        parameters=dict(jump_per_frame=12288,boost=32,reduction=0,gravity=2048,max_fall=8192,
            float_input=0,hold_gravity='Explicit fixture input0/512/1024/2048; actual GB Studio core default not established yet'),
        scope='Literal upstream C jump/fall Y blocks compiled with host GCC against assembled6502. Both jump-held paths, horizontal-speed enemy-bounce boost, signed saturation, fall cap, drop-through and queued fall transition. Supported pulse inputY>=-20480 avoids pre-boost signed overflow. Pure CPU fixtures; unknown hold-gravity default remains explicit.',
        remaining='Bind actual GB default/compiled reference and complete Main/state/collision/lifecycle/CHR/audio/menu/native playthrough. No original-ROM instruction equivalence, playable admission, helper or nightly update.')
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
