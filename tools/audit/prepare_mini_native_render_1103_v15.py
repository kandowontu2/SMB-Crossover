"""Compile direct native Mini sprite leaf from the exact source pose packet."""
from pathlib import Path
import hashlib
import json
import subprocess
from py65.devices.mpu6502 import MPU
import build_storage_guard_v1 as G

R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-native-render-1103-v15'
ART=R/'build/mini-mario-art-1103-v12'
sha=lambda b:hashlib.sha256(b).hexdigest()

SOURCE='''; Proposed Mini-only conditional overlay. No native allocation yet.
.setcpu "6502"
.segment "MINI_RENDER"
.export MiniNativeDraw,MiniNativeDrawEnd
MiniPose=$c310
MiniRenderX=$c311
MiniRenderY=$c313
MiniRendered=$c315
; Input integer screenpart origin, independently projected by future host.
; Source records prove every pose has zero or one part at relative0,0.
; AXYP restored except handled C=1, even when invisible/clipped/OAM-full.
MiniNativeDraw:
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 sta MiniRendered
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 lda MiniRenderX+1
 ora MiniRenderY+1
 bne Done
 lda MiniRenderY
 beq Done
 cmp #240
 bcs Done
 ldx CurrentOAMOffset
 cpx #252
 bcs Done
 txa
 and #3
 bne Done
 ldy MiniPose
 cpy #78
 bcs Done
 lda MiniPoseTile,y
 beq Done
 sta Sprite_Data+1,x
 lda MiniPoseAttribute,y
 sta Sprite_Data+2,x
 lda MiniRenderX
 sta Sprite_Data+3,x
 lda MiniRenderY
 sec
 sbc #1
 sta Sprite_Data,x
 txa
 clc
 adc #4
 sta CurrentOAMOffset
 lda #1
 sta MiniRendered
Done:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
MiniPoseTile:
 .byte TILE_VALUES
MiniPoseAttribute:
 .byte ATTRIBUTE_VALUES
MiniNativeDrawEnd:
'''


def main():
    G.preflight(private_root=O,reserved_bytes=40000,reserved_files=6,fresh=True)
    O.mkdir(exist_ok=False)
    art=json.loads((ART/'receipt.json').read_text());assert art['passed'] and not art['ROM_written']
    layout=json.loads((ART/'layout.json').read_text());poses=layout['pose_records']
    assert len(poses)==78 and all(len(p['parts'])<=1 for p in poses)
    assert all(part['x']==part['y']==0 for p in poses for part in p['parts'])
    assert all(0<part['tile']<64 and part['tile']&1 for p in poses for part in p['parts'])
    native=json.loads((R/'build/dkjr-native-source-1102-v2/native-body-v10-layout.json').read_text())
    # The bound source rendering packet supplies current native RAM symbols.
    # No legacy source constant or guessed address enters the assembled leaf.
    native=native.get('native_bindings',{})
    import sys
    sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
    from link_pit_rygar_sophia_audit_cpu import scoped_load
    from check_tmnt_render_oa import address
    base=R/'build/excitebike-pose-1101-v3/current4.nes'
    b=scoped_load(base)
    symbols={n:address(b,n) for n in ['ObjectMetasprite','SmPosePtr','CurrentOAMOffset','Sprite_Data']}
    assert symbols['ObjectMetasprite']==0x6e1 and symbols['SmPosePtr']==0x6b06
    tiles=[p['parts'][0]['tile'] if p['parts'] else 0 for p in poses]
    attributes=[p['parts'][0]['attributes'] if p['parts'] else 0 for p in poses]
    text='\n'.join(n+'=$%04x'%pc for n,pc in symbols.items())+'\n'+SOURCE
    text=text.replace('TILE_VALUES',','.join(map(str,tiles))).replace('ATTRIBUTE_VALUES',','.join(map(str,attributes)))
    (O/'native-render.s').write_text(text)
    (O/'native-render.cfg').write_text('MEMORY{C:start=$a000,size=$1000,file=%O;}SEGMENTS{MINI_RENDER:load=C,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for args in [[cc/'ca65.exe',O/'native-render.s','-o',O/'native-render.o'],
                 [cc/'ld65.exe','-C',O/'native-render.cfg',O/'native-render.o','-o',O/'native-render.bin','-Ln',O/'native-render.lbl']]:
        result=subprocess.run(list(map(str,args)),capture_output=True,text=True);assert result.returncode==0,result.stderr
    (O/'native-render.o').unlink()
    code=(O/'native-render.bin').read_bytes();assert len(code)<512
    memory=[0]*65536;memory[0xa000:0xa000+len(code)]=code
    cpu=MPU(memory=memory,pc=0xa000);cases=0;maxcycles=0
    scenarios=[(40,192,0),(248,208,248),(255,239,64),(-1,192,0),(256,192,0),
               (40,0,0),(40,-1,0),(40,240,0),(40,192,252),(40,192,2)]
    for pose in range(80):
        for x,y,offset in scenarios:
            for flags in [0x20,0x61,0xe0,0xa1]:
                memory[0x200:0x300]=[0xf8]*256
                memory[0xc310:0xc315]=[pose,x&255,(x>>8)&255,y&255,(y>>8)&255]
                memory[symbols['CurrentOAMOffset']]=offset
                memory[symbols['ObjectMetasprite']]=145
                cpu.pc=0xa000;cpu.sp=224;cpu.a=83;cpu.x=71;cpu.y=109;cpu.p=flags
                cpu.stPushWord(0x5aff);start=cpu.processorCycles
                for _ in range(90):
                    if cpu.pc==0x5b00:break
                    cpu.step()
                else:raise AssertionError(('finite draw',pose,x,y,offset))
                assert cpu.sp==224 and(cpu.a,cpu.x,cpu.y)==(83,71,109)
                assert cpu.p==(flags|0x31) #6502 PHP/PLP B+unused bits, handled C.
                drawn=pose<78 and bool(tiles[pose]) and 0<=x<=255 and 1<=y<=239 and offset<252 and offset%4==0
                expected=[0xf8]*256
                if drawn:expected[offset:offset+4]=[y-1,tiles[pose],attributes[pose],x]
                assert memory[0x200:0x300]==expected
                assert memory[0xc315]==int(drawn)
                assert memory[symbols['CurrentOAMOffset']]==offset+4*drawn
                assert memory[symbols['ObjectMetasprite']]==0
                assert memory[symbols['SmPosePtr']]+256*memory[symbols['SmPosePtr']+1]==symbols['ObjectMetasprite']
                cases+=1;maxcycles=max(maxcycles,cpu.processorCycles-start)
    receipt=dict(passed=True,CPU_only=True,ROM_written=False,allocation_granted=False,
        source_poses=78,cases=cases,code_and_table_bytes=len(code),max_cycles=maxcycles,
        parts_per_pose_maximum=1,extra_outline_sprites=0,stable_unbanked_zero_descriptor=True,
        input_fields_half_open=[0xc310,0xc316],native_symbols=symbols,
        scope='Actual assembled one-part native OAM leaf, all original source poses/attributes and genuine empty poses; clipping, OAM alignment/capacity and fullAXYPexceptC tested. No source part resampling or invented animation. Keeps ObjectMetasprite absent and SmPosePtr on its stable native zero header, avoiding the observed Prince legacy CHR overwrite path.',
        limits='Caller must supply correct original-derived screenpart origin and compiled source animation. Physical art page publication, hardware DMA/rendering, native Main/collision/owner/menu and Mini nightly remain unqualified. Omit origins outside screen rather than wrap them; topY0 is omitted because NES OAM cannot address visible scanline0.',
        bindings={str(p.relative_to(R)):sha(p.read_bytes()) for p in [Path(__file__),ART/'receipt.json',
            ART/'layout.json',ART/'body.chr',O/'native-render.s',O/'native-render.bin',base.with_suffix('.lbl')]})
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items()if k!='bindings'}))


if __name__=='__main__':main()
