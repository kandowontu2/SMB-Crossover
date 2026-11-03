"""Compile Mini's private native tile sampler; no allocation or ROM emission."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from py65.devices.mpu6502 import MPU
import build_storage_guard_v1 as G

R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-native-tile-1103-v13'
ROM=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
sha=lambda b:hashlib.sha256(b).hexdigest()

SOURCE='''; Proposed mutually exclusive Mini overlay only; not host allocations.
.setcpu "6502"
.segment "MINI_NATIVE"
.export MiniNativeTile,MiniNativeTileEnd
MiniQueryX=$c2e0
MiniQueryY=$c2e2
MiniQueryTile=$c2e4
MiniQueryAddress=$c2e5
MiniQueryKind=$c2e7
MiniQueryFlags=$c2e8
MiniQueryColumn=$c2e9
MiniTileAttributes=$d000
; Input: integer worldpixel X/Y, each unsigned16. Caller extends tile8 X.
; Output: raw native metatile, native buffer address and directional flags.
; X/Y preserved; A=flags, C=ordinary solid. No host ZP/native buffer writes.
; Flags0F for all-sided native solid,10 for native vine. ExactGBS flag
; numeric binding remains a required caller-level proof before integration.
MiniNativeTile:
 txa
 pha
 tya
 pha
 lda #0
 sta MiniQueryTile
 sta MiniQueryFlags
 sta MiniQueryKind
 sta MiniQueryAddress
 sta MiniQueryAddress+1
 lda MiniQueryY+1
 bne Done
 lda MiniQueryY
 cmp #32
 bcc Done
 cmp #240
 bcs Done
 lda MiniQueryX
 lsr
 lsr
 lsr
 lsr
 sta MiniQueryColumn
 lda MiniQueryY
 and #$f0
 sec
 sbc #32
 ora MiniQueryColumn
 tay
 lda MiniQueryX+1
 and #1
 bne Buffer2
 tya
 sta MiniQueryAddress
 lda #>Block_Buffer_1
 sta MiniQueryAddress+1
 lda Block_Buffer_1,y
 jmp Classify
Buffer2:
 tya
 clc
 adc #<Block_Buffer_2
 sta MiniQueryAddress
 lda #>Block_Buffer_2
 adc #0
 sta MiniQueryAddress+1
 lda Block_Buffer_2,y
Classify:
 sta MiniQueryTile
 tax
 lda MiniTileAttributes,x
 and #3
 cmp #1
 bne Vine
 lda #15
 bne Store
Vine:
 cpx #$26
 bne Done
 lda #151
 sta MiniQueryKind
 lda #16
Store:
 sta MiniQueryFlags
Done:
 pla
 tay
 pla
 tax
 lda MiniQueryFlags
 cmp #15
 beq Solid
 clc
 rts
Solid:
 sec
 rts
MiniNativeTileEnd:
'''


def main():
    G.preflight(private_root=O,reserved_bytes=50000,reserved_files=7,fresh=True)
    O.mkdir(exist_ok=True)
    raw=ROM.read_bytes();assert sha(raw)==PIN
    p=R/'build/dkjr-native-source-1102-v2/native-world-v3-layout.json'
    old=json.loads(p.read_text()); at=old['native_MTileAttribute_file_offset']
    attrs=raw[at:at+256];assert sha(attrs)==old['native_MTileAttribute_SHA256']
    native=old['native_bindings'];assert native['Block_Buffer_1']==0x300 and native['Block_Buffer_2']==0x3d0
    source='\n'.join(n+'=$%04x'%native[n] for n in ['Block_Buffer_1','Block_Buffer_2'])+'\n'+SOURCE
    (O/'native-tile.s').write_text(source)
    (O/'native-tile.cfg').write_text('MEMORY{C:start=$a000,size=$1000,file=%O;}SEGMENTS{MINI_NATIVE:load=C,type=ro;}')
    cc=R/'tools/Windows/cc65/bin'
    for args in [[cc/'ca65.exe',O/'native-tile.s','-o',O/'native-tile.o'],
                 [cc/'ld65.exe','-C',O/'native-tile.cfg',O/'native-tile.o','-o',O/'native-tile.bin','-Ln',O/'native-tile.lbl']]:
        result=subprocess.run(list(map(str,args)),capture_output=True,text=True)
        assert result.returncode==0,result.stderr
    (O/'native-tile.o').unlink()
    code=(O/'native-tile.bin').read_bytes();assert len(code)<256
    memory=[0]*65536;memory[0xa000:0xa000+len(code)]=code;memory[0xd000:0xd100]=attrs
    buffer1=native['Block_Buffer_1'];buffer2=native['Block_Buffer_2']
    for i in range(416):memory[buffer1+i]=(i*73+19)&255
    cpu=MPU(memory=memory,pc=0xa000);cases=0;maxcycles=0
    def sample(x,y):
        nonlocal cases,maxcycles
        memory[0xc2e0:0xc2e4]=[x&255,x>>8,y&255,y>>8]
        cpu.pc=0xa000;cpu.sp=224;cpu.x=71;cpu.y=109;cpu.p=0x61;cpu.stPushWord(0x5aff)
        start=cpu.processorCycles
        for _ in range(110):
            if cpu.pc==0x5b00:break
            cpu.step()
        else:raise AssertionError(('finite bound',x,y,hex(cpu.pc)))
        assert cpu.sp==224 and(cpu.x,cpu.y)==(71,109)
        addr=0 if not 32<=y<240 else buffer1+208*((x>>8)&1)+((y-32)//16)*16+((x>>4)&15)
        tile=memory[addr]if addr else 0
        flags=15 if addr and attrs[tile]&3==1 else 16 if addr and tile==0x26 else 0
        kind=151 if addr and tile==0x26 and flags==16 else 0
        assert memory[0xc2e4:0xc2e9]==[tile,addr&255,addr>>8,kind,flags],(x,y,addr)
        assert cpu.a==flags and bool(cpu.p&1)==(flags==15)
        cases+=1;maxcycles=max(maxcycles,cpu.processorCycles-start)
    before=memory[buffer1:buffer1+416]
    # Every8px subcell through4095px, everyrow including HUD/bottom; cover
    # fractional-cell side samples and the2048px source tileX extension.
    for x in range(0,4096,8):
        for y in range(0,256,8):sample(x,y)
    for tile in range(256):
        memory[buffer1]=tile;sample(0,32);sample(7,39);sample(15,47)
    memory[buffer1]=before[0]
    for x in [0,255,256,511,512,2047,2048,3407,4095,65535]:
        for y in [0,31,32,239,240,255,256,65535]:sample(x,y)
    assert memory[buffer1:buffer1+416]==before
    (O/'native-attributes.bin').write_bytes(attrs)
    receipt=dict(passed=True,CPU_only=True,native_playable=False,ROM_written=False,
        allocation_granted=False,code_bytes=len(code),cases=cases,max_cycles=maxcycles,
        proposed_query_half_open=[0xc2e0,0xc2ea],proposed_attribute_half_open=[0xd000,0xd100],
        native_ROM_SHA256=PIN,native_buffers_unchanged=True,extended_worldpixel_X=True,
        contract='Integer worldpixel inputs16bits; native buffer topY32,row13,col16,pageparity. Replicate each metatile tofour8px cells. Raw metatile and native buffer address retained for deferred native head transactions; no SMB collision function runs from the private sampler.',
        limits='Independent sampler only. ExactGBS directional flag numeric binding, caller/state/collision semantics, moving actors and native powerup transaction remain pending. No allocated shared RAM/code/CHR, native owner/menu/nightly or Mini1-1 claim.',
        bindings={str(p.relative_to(R)):sha(p.read_bytes()) for p in [Path(__file__),ROM,
            R/'build/dkjr-native-source-1102-v2/native-world-v3-layout.json',
            O/'native-tile.s',O/'native-tile.cfg',O/'native-tile.bin',O/'native-attributes.bin']})
    (O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items()if k!='bindings'}))


if __name__=='__main__':main()
