"""Install the pinned Game Boy Color Mini fireball art into a private candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from prepare_mini_mario_art_1103_v12 import GB, GBPIN
from prepare_mini_mario_native_power_1103_v56 import N, address, bundle
from prepare_mini_motion_fast_1108 import once
from prepare_mini_no_wall_1108 import CODE, COOKIE, LINKER
from prepare_mini_owner_payload_1103_v19 import BOOT
from prepare_selected_native_packet_v1 import R, sha

REFERENCE = R/'tools/reference/mini_fireball_art_1108.s'
WEAPONS = R/'tools/reference/mini_mario_fireball_1103.s'
BASE_ART = R/'build/mini-two-fireballs-1103'
FRAME_OFFSETS = {'A':0x10ff30,'B':0x10ff50,'C':0x10ff70,'D':0x10ff90}
ART_OFFSETS = {'A':0x2e0,'B':0x3e0,'C':0x3a0,'D':0x3c0}
TILES = {'A':0x6f,'B':0x7f,'C':0x7b,'D':0x7d}
CC = R/'tools/Windows/cc65/bin'


def donor_tiles():
    raw = GB.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == GBPIN
    expected = ('0038367e5e4c20000000380c0c000000', '00384e1e3a3c1c00000004041c180000',
                '00002418182400000000000000000000', '24bd7ee7e77ebd240000183c3c180000')
    frames = {}
    for (name,offset), hex_bytes in zip(FRAME_OFFSETS.items(),expected,strict=True):
        data = raw[offset:offset+16]
        assert raw.find(data) == raw.rfind(data) == offset
        low, high = bytearray(),bytearray()
        for y in range(8):
            pixels = []
            for bit in reversed(range(8)):
                source = ((data[2*y]>>bit)&1) | (((data[2*y+1]>>bit)&1)<<1)
                pixels.append([0,2,3,1][source])
            low.append(sum((p&1)<<(7-x) for x,p in enumerate(pixels)))
            high.append(sum((p>>1)<<(7-x) for x,p in enumerate(pixels)))
        assert (low+high).hex() == hex_bytes
        frames[name] = bytes(low+high)+bytes(16)
    return frames


def assemble(source, config, output):
    cfg = output.with_suffix('.cfg')
    cfg.write_text(config,encoding='utf-8')
    obj, labels = output.with_suffix('.o'), output.with_suffix('.lbl')
    subprocess.run([CC/'ca65.exe',source,'-o',obj],check=True)
    subprocess.run([CC/'ld65.exe','-C',cfg,obj,'-o',output,'-Ln',labels],check=True)
    return {name:int(pc,16) for pc,name in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',labels.read_text(),re.M)}


def patch(raw,offset,before,after):
    assert len(before) == len(after) and raw[offset:offset+len(before)] == before,hex(offset)
    raw[offset:offset+len(after)] = after


def adjust_weapons(source):
    source = once(source,'PlayerStatus=$075b','FrameCounter=$0e\nMiniFireballPhase=$c324\nPlayerStatus=$075b')
    source = once(source,''' cmp #1
 beq HideShot
 cmp #$80                  ; native collision still calls DrawFireball once.
 bne SlotDone              ; states81+ retain genuine native explosion art.
HideShot:''',''' bmi HideShot               ; Native collision/timing, donor visual.
 cmp #1
 bne SlotDone
 lda FrameCounter
 and #3
 bne HideShot
 inc MiniFireballPhase,x     ; Every fourth active update; independent slot phase.
HideShot:''')
    source = once(source,''' cmp #1
 bne NextDraw
 lda Fireball_X_Position,y''',''' cmp #1
 beq VisibleState
 cmp #$80
 bcc NextDraw
 cmp #$86
 bcs NextDraw               ; Blank at the end of the native impact lifetime.
VisibleState:
 lda Fireball_X_Position,y''')
    source = once(source,''' lda Fireball_Y_Position,y
 cmp #236''',''' lda Fireball_Y_Position,y
 cmp #8
 bcc NextDraw
 cmp #236''')
    return once(source,''' lda Fireball_Y_Position,y
 clc
 adc #3                    ; OAM Y+1 then visible row0 =>base+4.
 sta Sprite_Data,x
 lda #$6f                  ; slot5 + metadata offset$2E0, 8x16 lowbit1.
 sta Sprite_Data+1,x
 lda #2
 sta Sprite_Data+2,x
 lda $03
 clc
 adc #6''',''' jsr $d400                 ; Donor frame, palette, flip and exact Y offset.
 lda $03
 clc
 adc #4''')


def verify_cold(raw, attributes, phase):
    image = bundle(raw)
    memory = N.fresh(image)
    N.put(memory,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,
          DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
    N.invoke(memory,'MiniScene')
    assert memory.ram[2][0x1300:0x1400] == attributes
    assert memory.ram[2][0x1400:0x1400+len(phase)] == phase
    assert memory.ram[3][:5120] == raw[CODE:CODE+5120]
    assert memory.ram[2][0x1fe0:0x1ff0] == memory.ram[3][0x1fe0:0x1ff0] == raw[COOKIE:COOKIE+16]
    assert N.get(memory,'SelectedCharacter') == 41


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    base, output = args.base.resolve(),args.output.resolve()
    parent = json.loads((base/'candidate.json').read_text())
    rom = base/'candidate.nes'
    assert parent['candidate_SHA256'] == sha(rom) and parent['platform_spawn']
    raw = bytearray(rom.read_bytes())
    meta = CODE+5120
    attributes = bytes(raw[meta+0x300:meta+0x400])
    assert hashlib.sha256(attributes).hexdigest() == 'aec04d8e6465b5ba04b09af9c49beb7b49e9471f84127e6845de15f0c331f73a'
    output.mkdir()
    # The already owned 1 KB is shared between physical sprite patterns and
    # the loaded metadata. Reconstruct the table only once during cold boot.
    stage = output/'art-stage.bin'
    labels = assemble(REFERENCE,'''MEMORY {
 IMAGE:start=$d300,size=$a0,file=%O;
 A3:start=$b400,size=$80,file="";
 C2:start=$d400,size=$80,file="";
}
SEGMENTS {
 ART_BOOT:load=IMAGE,type=ro;
 RESTORE:load=IMAGE,run=A3,type=ro,define=yes;
 PHASE:load=IMAGE,run=C2,type=ro,define=yes;
}
''',stage)
    phase_load = labels['__PHASE_LOAD__']-0xd300
    phase = stage.read_bytes()[phase_load:phase_load+labels['__PHASE_SIZE__']]
    assert labels['MiniFireballArtBoot'] == 0xd300 and labels['MiniFireballPose'] == 0xd400
    stage_data = stage.read_bytes()
    assert len(stage_data) <= 0xa0
    raw[meta+0x300:meta+0x300+len(stage_data)] = stage_data

    cold = output/'art-cold.s'
    cold.write_text(once(BOOT,' bne NextRow\n sec\n rts',' bne NextRow\n jmp $d300'),encoding='utf-8')
    cold_bin = cold.with_suffix('.bin')
    assemble(cold,'MEMORY{C:start=$d25e,size=$72,file=%O;}SEGMENTS{MINI_COLD:load=C,type=ro;}',cold_bin)
    expected = (R/'build/mini-mario-owner-1103-v15/cold-v19.bin').read_bytes()+b'\xff'
    patch(raw,meta+0x25e,expected,cold_bin.read_bytes())

    frames = donor_tiles()
    for name,offset in ART_OFFSETS.items():
        raw[meta+offset:meta+offset+32] = frames[name]
    weapons = output/'art-weapons.s'
    weapons.write_text(adjust_weapons(WEAPONS.read_text()),encoding='utf-8')
    spans = [('MINI_FB_ATTACK',0xbcc0,160),('MINI_FB_HELPERS',0xbd72,178),('MINI_FB_ART',0xd2e0,32)]
    cfg = 'MEMORY {\n'+''.join(f'{n}:start=${pc:04x},size={cap},file="{(output/(n+".bin")).as_posix()}";\n'
                                   for n,pc,cap in spans)+'}\nSEGMENTS {\n'+''.join(
                                   f'{n}:load={n},type=ro;\n' for n,_,_ in spans)+'}\n'
    fire = assemble(weapons,cfg,output/'mini-fireball.bin')
    for name,pc,capacity in spans[:2]:
        old = (BASE_ART/(name+'.bin')).read_bytes().ljust(capacity,b'\xea')
        new = (output/(name+'.bin')).read_bytes().ljust(capacity,b'\xea')
        patch(raw,16+89*8192+(pc&8191),old,new)
    # D239's existing wrapper contains the far-call target as two immediates.
    assert raw[meta+0x239:meta+0x247] == bytes.fromhex('088d6a01a9a98d6c01a9bd8d6d01')
    raw[meta+0x23e] = fire['MiniFireballDrawReturn']&255
    raw[meta+0x243] = fire['MiniFireballDrawReturn']>>8

    asm = output/'mini-lift.s'
    asm.write_text(once((base/'mini-lift.s').read_text(),' ldx #$23\n@clear:',' ldx #$25\n@clear:'),encoding='utf-8')
    component = asm.with_suffix('.bin')
    assemble(asm,LINKER.read_text(),component)
    data = component.read_bytes()
    before = (base/'mini-lift.bin').read_bytes()
    differences = [(a,b) for a,b in zip(before,data,strict=True) if a!=b]
    assert differences == [(0x23,0x25)]
    raw[CODE:CODE+5120] = data.ljust(5120,b'\xff')
    raw[COOKIE+3:COOKIE+16] = hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    verify_cold(raw,attributes,phase)

    candidate = output/'candidate.nes'
    candidate.write_bytes(raw)
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(rom.with_suffix(ext),candidate.with_suffix(ext))
    report = dict(passed=True,candidate_SHA256=sha(candidate),parent_SHA256=sha(rom),
                  platform_spawn=True,donor_SHA256=GBPIN,
                  frames={name:dict(donor_offset=FRAME_OFFSETS[name],CHR_offset=ART_OFFSETS[name],
                                    tile=TILES[name],bytes=frame.hex()) for name,frame in frames.items()},
                  render_labels=fire,cold_loader_exact_attribute_table=True,
                  phase_RAM=[0xc324,0xc325],phase_every_updates=4,palette=[0x16,0x30,0x27],
                  live_art_extent=[6,6],native_collision_extent=[4,4],
                  scope='Donor moving and impact artwork, existing native projectile physics and impact lifetime.',
                  bindings={str(p):sha(p) for p in (Path(__file__),rom,REFERENCE,WEAPONS,GB)})
    (output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
