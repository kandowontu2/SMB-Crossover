"""Assemble Mini's source-foot contact with an existing native lift actor."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from prepare_mini_motion_fast_1108 import convert, once
from prepare_mini_no_wall_1108 import CODE, COOKIE, LINKER
from prepare_selected_native_packet_v1 import R, sha
from compose_mini_busy_1108 import FIRE, apply_patch

SUPPORT = R/'tools/reference/mini_mario_native_lift_support_1108.inc'
BASE = R/'build/mini-no-wall-1108/candidate.nes'
SOURCE = BASE.with_name('mini-no-wall.s')


def transform(source, admit):
    source = convert(source)
    source = once(source, 'MiniToPixelFast:\n', 'MiniToPixel:\n')
    source = once(source, '    .assert *-MiniToPixelFast=27', '    .assert *-MiniToPixel=27')
    source = once(source, 'MiniToPixel:\n    jmp MiniToPixelFast\n    .res 9,$ff\n','')
    source = once(source, '    lda MiniTemp+1\n    sta MiniCoord+1\nMiniAddBound:',
                  '    lda MiniTemp+1\n    sta MiniCoord+1\n    jmp MiniToPixel\nMiniAddBound:')
    source = once(source, ' jmp MiniHostAnimate\nMiniHostAnimate:\n','')
    source = once(source, '''    ldx #4
@shift:
    asl MiniCoord
    rol MiniCoord+1
    dex
    bne @shift
    lda MiniNegative''','''    jsr MiniHostToSubpixel
    lda MiniNegative''')
    source = once(source, ' lda Player_PageLoc\n sta MiniOldX+1\n','')
    assert source.count('MiniLastWall') == 3  # Definition and two dead writes.
    source = once(source,'    lda #$FF\n    sta MiniLastWall\n','')
    source = once(source,'    lda #1\n    sta MiniLastWall\n','')
    source = once(source,'MiniName: .byte $16,$12,$17,$12,$24,$24,$24,$12,$18',
                  'MiniName: .byte $16,$12,$17,$12,$24,$24,$24')
    source = once(source,' beq MiniHostDrawSource\n jsr MiniHostNativeCanvas',
                  ' beq MiniHostDrawSource\nMiniHostDrawCanvas:\n jsr MiniHostNativeCanvas')
    source = once(source,' sta MiniPose\n jsr MiniHostGraphics\n jsr MiniHostNativeCanvas\n jmp MiniNativeDraw',
                  ' sta MiniPose\n jsr MiniHostGraphics\n jmp MiniHostDrawCanvas')
    source = once(source, ' adc #24\n clc\n adc MiniTop', ' adc #24\n tay\n clc\n adc MiniTop')
    source = once(source, ' lda Player_Y_Position\n clc\n adc #24\n clc\n adc MiniBottom',
                  ' tya\n clc\n adc MiniBottom')
    for axis in ('X','Y'):
        before = f'''    lda Mini{axis}
    sta MiniCoord
    lda Mini{axis}+1
    sta MiniCoord+1
    jsr MiniToPixel
'''
        assert source.count(before) == (3 if axis == 'X' else 2)
        source = source.replace(before,f'    jsr MiniHostPixel{axis}\n')
    source = once(source, '''    sta MiniNegative
    lda #1
    sta MiniMask
    lda MiniBottom''','''    sta MiniNegative
    jsr MiniPlatformFloor
    jcs @floorhit
    lda #1
    sta MiniMask
    lda MiniBottom''')
    source = once(source, '''@up:
    lda #1
    sta MiniNegative''','''@up:
    lda #0
    sta MiniLiftGround
    lda #1
    sta MiniNegative''')
    source = once(source, '''    bne @headhit
    lda #0
    sta attached''','''    bne @headhit
@floorhit:
    lda #0
    sta attached''')
    source = once(source, ' .res 64,$ff ; Former wall grab worker.\n',SUPPORT.read_text())
    if admit:
        start = source.index('MiniHostImportX:\n')
        end = source.index('MiniHostToSubpixel:\n',start)
        source = source[:start]+'''MiniHostImportX:
 lda Player_X_Position
 sta MiniCoord
 lda Player_PageLoc
 sta MiniCoord+1
 tya
 pha
 ldy #0
 beq MiniHostImportAxis
MiniHostImportY:
 clc
 adc Player_Y_Position
 sta MiniCoord
 lda Player_Y_HighPos
 adc #$ff
 sta MiniCoord+1
 tya
 pha
 ldy #2
MiniHostImportAxis:
 lda MiniX,y
 and #15
 pha
 jsr MiniHostToSubpixel
 pla
 ora MiniCoord
 sta MiniX,y
 lda MiniCoord+1
 sta MiniX+1,y
 pla
 tay
 lda MiniCoord+1
 rts
'''+source[end:]
        source = once(source, '@step:\n lda FrameCounter', '''@step:
 ; The three helpers are in world pages 2 and 3. Outside them there is no
 ; bank call or actor scan. The manager verifies the loaded 1-1 scene.
 lda Player_PageLoc
 sec
 sbc #2
 cmp #2
 bcs @epoch
 lda #$cf
 sta MiniNativeTarget+1
 lda #$bb
 sta MiniNativeTarget+2
 lda #$98
 jsr MiniFarCall
@epoch:
 lda FrameCounter''')
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--admission', type=Path)
    parser.add_argument('--busy-optimizations', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    raw = bytearray(BASE.read_bytes())
    assert sha(BASE) == 'aa02beb0ec5fe8679f9920cf488994d9ff9887bfe07d9badec407670ce38e6e8'
    assert raw[CODE:CODE+5120] == SOURCE.with_suffix('.bin').read_bytes()
    output.mkdir(exist_ok=True)
    assert not (output/'candidate.json').exists(), 'A completed candidate is immutable'
    asm = output/'mini-lift.s'
    asm.write_text('.export MiniPlatformFloor, MiniLiftActor, MiniLiftGround\n'+transform(SOURCE.read_text(),args.admission is not None),
                   encoding='utf-8',newline='\n')
    binary, obj, labels = (asm.with_suffix(ext) for ext in ('.bin','.o','.lbl'))
    compiler = R/'tools/Windows/cc65/bin'
    subprocess.run([compiler/'ca65.exe',asm,'-o',obj],check=True)
    subprocess.run([compiler/'ld65.exe','-C',LINKER,obj,'-o',binary,'-Ln',labels],check=True)
    data = binary.read_bytes()
    assert len(data) <= 5120, len(data)
    values = {name:int(pc,16) for pc,name in re.findall(r'^al ([0-9A-F]+) \.(\w+)$',labels.read_text(),re.M)}
    assert values['MiniVectors'] == 0xa000 and values['MiniInit'] == 0xa3bc
    raw[CODE:CODE+5120] = data.ljust(5120,b'\xff')
    raw[COOKIE+3:COOKIE+16] = hashlib.sha256(raw[CODE:CODE+7168]).digest()[:13]
    refs = [Path(__file__),BASE,SOURCE,SUPPORT,LINKER]
    if args.admission:
        proof = json.loads(args.admission.read_text())
        assert proof['passed'] and proof['parent'] == sha(BASE)
        for path,digest in proof['source_hashes'].items():
            assert sha(path) == digest, path
        for patch in proof['patch_spans']:
            offset = 16+patch['bank']*8192+(patch['pc']&8191)
            apply_patch(raw,offset,patch['before'],patch['after'])
        refs.append(args.admission)
    if args.busy_optimizations:
        batch = R/'build/mini-parser-health-1108-v1/health-batch-v2.json'
        async_proof = batch.with_name('health-batch-async-v3.json')
        fire_irq = FIRE.with_name('interrupts.json')
        parser_proof, irq = (json.loads(p.read_text()) for p in (batch,async_proof))
        fire = json.loads(FIRE.read_text())
        assert fire['passed'] and json.loads(fire_irq.read_text())['passed']
        assert parser_proof['passed'] and irq['passed']
        assert parser_proof['expected_memory_only_SHA256'] == irq['memory_image_SHA256']
        for patch in fire['patches']:
            apply_patch(raw,patch['offset'],patch['preimage'],patch['replacement'])
        for patch in parser_proof['patches']:
            apply_patch(raw,patch['file_offset'],patch['old_hex'],patch['new_hex'])
        refs.extend((FIRE,fire_irq,batch,async_proof))
    game = output/'candidate.nes'
    game.write_bytes(raw)
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(BASE.with_suffix(ext),game.with_suffix(ext))
    report = dict(candidate_SHA256=sha(game),parent_SHA256=sha(BASE),kernel_bytes=len(data),
                  kernel_SHA256=sha(binary),labels=values,platform_spawn=bool(args.admission),
                  busy_optimizations=args.busy_optimizations,
                  scope='Private Mini lift candidate, pending native traversal qualification.',
                  bindings={str(p):sha(p) for p in refs})
    (output/'candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
