"""Exact Mini five-row cold source and memory-only component composition."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_existing_owners_1103_v17 as Q
import measure_mini_private_owner_1103_v15 as M
import build_storage_guard_v1 as G
O=M.O
BOOT='''.setcpu "6502"
.segment "MINI_COLD"
.export MiniColdBoot,MiniColdEnd,MiniCodePages
R0=$03
R1=$04
R2=$05
; Resident CoCold has saved AXYP/R0..7/fiveSMC/maps, forcedblank/SEI,
; retired every previous owner and invalidated bothheaders. Commonworker
; copied the single immutable967 row intoC2:D000 and zeroedC000..C8FF.
; TypedFarCall entersC2:D25E with A3 mapped; R5/R6 cookie pointer survives.
; This cold-only leaf does not run MiniInit or publish validity.
MiniColdBoot:
 lda #0
 sta R0
 sta R2
 lda #$a0
 sta R1
NextRow:
 jsr MapRow
 ldx #4
Copy:
 lda $2007
 sta (R0),y
 iny
 bne Copy
 inc R1
 dex
 bne Copy
 lda R1
 sec
 sbc #4
 sta R1
 jsr MapRow
 ldx #4
Verify:
 lda $2007
 cmp (R0),y
 bne Failed
 iny
 bne Verify
 inc R1
 dex
 bne Verify
 inc R2
 lda R2
 cmp #5
 bne NextRow
 sec
 rts
Failed:
 clc
 rts
MapRow:
 lda R2
 asl
 tax
 lda MiniCodePages+1,x
 sta $5130
 lda MiniCodePages,x
 sta $5123
 ldy #0
 sty $5130
 bit $2002
 lda #$0c
 sta $2006
 sty $2006
 lda $2007
 rts
MiniCodePages:
 .word 962,963,964,965,966
MiniColdEnd:
'''


def metadata(index,frames,attributes):
    assert len(index)==352 and len(frames)==217 and len(attributes)==256
    boot=(O/'cold-v19.bin').read_bytes();assert len(boot)<=0x300-0x25e
    image=bytearray([255])*1024
    image[:352]=index;image[0x160:0x160+217]=frames
    image[0x25e:0x25e+len(boot)]=boot;image[0x300:0x400]=attributes
    return bytes(image)


def component(kernel,meta,art,expected_kernel_SHA256):
    """Accept exact compiler outputs, return immutable padded source images."""
    assert hashlib.sha256(kernel).hexdigest()==expected_kernel_SHA256
    assert len(kernel)<=5120 and len(meta)==len(art)==1024
    boot=(O/'cold-v19.bin').read_bytes()
    assert meta[0x25e:0x25e+len(boot)]==boot
    # This is explicit source-declared FF padding of a granted code image,
    # never a claim that any preexisting physical FF byte was available.
    code=kernel+bytes([255])*(5120-len(kernel))
    cookie=bytes([0xa7,41,1])+hashlib.sha256(code+meta+art).digest()[:13]
    return dict(code=code,metadata=meta,art=art,cookie=cookie,kernel_bytes=len(kernel),declared_FF_pad=5120-len(kernel))


def compose(kernel,meta,art,expected_kernel_SHA256):
    """Return exact parent+shared+seven carriers in memory; never emit ROM."""
    images=component(kernel,meta,art,expected_kernel_SHA256)
    base,fit,rows=Q.image();raw=bytearray(base['raw'])
    at=16+65*8192+fit['Mini_cookie_CPU']-0xa000
    assert raw[at:at+16]==bytes.fromhex(fit['Mini_cookie_placeholder'])
    raw[at:at+16]=images['cookie']
    # Final cookie is inside the one already-reassembled manager extent;
    # retain a disjoint manifest instead of adding an overlapping patch.
    owner=next(r for r in rows if r['role']=='owner-v15')
    start=owner['file_offset'];owner['new_hex']=bytes(raw[start:start+owner['bytes']]).hex()
    carriers=[*(images['code'][i:i+1024]for i in range(0,5120,1024)),meta,art]
    parent=M.BASE.read_bytes()
    for page,data in zip(M.CODE+[M.META,M.ART],carriers):
        at=1048592+page*1024;assert raw[at:at+1024]==parent[at:at+1024]
        raw[at:at+1024]=data
        rows.append(dict(physical_CHR=page,file_offset=at,bytes=1024,old_hex=parent[at:at+1024].hex(),new_hex=data.hex(),role='Granted Mini code/immutable/art'))
    spans=sorted((r['file_offset'],r['file_offset']+r['bytes'])for r in rows)
    assert all(a[1]<=z[0]for a,z in zip(spans,spans[1:]))
    check=bytearray(parent)
    for row in rows:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert check[at:at+len(old)]==old
        check[at:at+len(new)]=new
    assert check==raw
    return dict(base,raw=bytes(raw)),dict(parent_SHA256=M.PIN,memory_SHA256=M.sha(raw),Mini_cookie=images['cookie'].hex(),kernel_SHA256=expected_kernel_SHA256,kernel_bytes=len(kernel),code_bytes=5120,metadata_bytes=1024,art_bytes=1024,source_declared_FF_padding=images['declared_FF_pad'],patches=rows)


def main():
    G.preflight(private_root=O,reserved_bytes=200000,reserved_files=10,fresh=True)
    boot,L=M.assemble('cold-v19',BOOT,'MEMORY{C:start=$d25e,size=$a2,file=%O;}SEGMENTS{MINI_COLD:load=C,type=ro;}')
    assert L['MiniColdBoot']==0xd25e and L['MiniColdEnd']<=0xd300
    host=R/'build/mini-mario-host-1103-v22';proof=json.loads((host/'mini-host-v22.json').read_text())
    kernel=(host/'mini-host-v22.bin').read_bytes();assert M.sha(kernel)==proof['SHA256']
    artroot=R/'build/mini-mario-art-1103-v12';attrs=R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin'
    index=(artroot/'engine-animation-index.bin').read_bytes();frames=(artroot/'engine-animation-frames.bin').read_bytes();art=(artroot/'body.chr').read_bytes()
    meta=metadata(index,frames,attrs.read_bytes());base,q=compose(kernel,meta,art,proof['SHA256'])
    (O/'metadata-v19.bin').write_bytes(meta)
    padding='.setcpu "6502"\n.segment "MINI_CODE_IMAGE"\nMiniCodeStart:\n .incbin "'+(host/'mini-host-v22.bin').as_posix()+'"\n .res $1400-(*-MiniCodeStart),$ff\n'
    (O/'code-padding-v19.s').write_text(padding)
    source=(O/'owner-v15.s').read_text();old=bytes.fromhex(json.loads((O/'owner-fit-v15.json').read_text())['Mini_cookie_placeholder']);cookie=bytes.fromhex(q['Mini_cookie'])
    oldtext='MiniCookie:\n .byte '+','.join('$%02x'%v for v in old)
    newtext='MiniCookie:\n .byte '+','.join('$%02x'%v for v in cookie)
    assert source.count(oldtext)==1
    (O/'owner-final-v19.s').write_text(source.replace(oldtext,newtext))
    q.update(passed=True,source_images_only=True,CPU_qualified=False,ROM_written=False,labels=L,
        cold_boot_bytes=len(boot),all83_owners_preserved=True,frontend_or_scene_changed=False,
        kernel_receipt=host.relative_to(R).as_posix()+'/mini-host-v22.json',
        metadata_layout=dict(animation_index=['D000','D160'],animation_frames=['D160','D239'],cold_boot=['D25E',f'{L["MiniColdEnd"]:04X}'],native_attributes=['D300','D400']),
        private_parser='A0vector37rows+reset19; strict tagbounds remain selector114byte. New41 is selected-owner authenticated, not any-bank fallback.',
        bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),Path(Q.__file__),O/'owner-fit-v15.json',O/'owner-final-v19.s',O/'cold-v19.s',O/'cold-v19.bin',O/'metadata-v19.bin',O/'code-padding-v19.s',host/'mini-host-v22.bin',host/'mini-host-v22.s',host/'mini-host-v22.json',artroot/'engine-animation-index.bin',artroot/'engine-animation-frames.bin',artroot/'body.chr',attrs,R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']})
    (O/'payload-manifest-v19.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))


if __name__=='__main__':main()
