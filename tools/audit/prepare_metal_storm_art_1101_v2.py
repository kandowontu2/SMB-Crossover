"""Export original actor-renderer packets/patterns, including gravity flip art."""
from pathlib import Path
import hashlib,json,sys,zipfile
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
import metal_storm_cpu_1101_v2 as M
OUT=ROOT/'build/metal-storm-component-1101-v2'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    OUT.mkdir(exist_ok=True)
    reference=M.boot()
    for tick in range(600):M.frame(reference,0x10 if tick in [120,121,300,301,480,481]else 0)
    initial=bytes(reference.memory[:2048])
    initial_palette=bytes(reference.memory.ppuread(0x3f00+i)for i in range(32))
    palette=(ROOT/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes();patterns=[];lookup={};packets=[]
    def packet(state,frame,facing,gravity):
        c=M.machine();m=c.memory;m[:2048]=initial;m.regs[6:8]=[12,13];m.map()
        for i,v in enumerate(initial_palette):m.ppu[m.pa(0x3f00+i)]=v
        table=m[0x800e]+256*m[0x800f];meta=m[table]+256*m[table+1]
        values={0x24:table&255,0x25:table>>8,0x480:128,0x498:0,0x4b0:112,0x4c8:0,0x4e0:state,0x4f8:frame,0x528:0,0x540:facing|gravity,0x678:0,0x710:0,0x711:0,0x50:0,0x42:0xfc}
        for a,v in values.items():m[a]=v
        m[0x200:0x300]=bytes([0xf0])*256
        M.call(c,0xf282,x=0,y=0)
        m.regs[:6]=m[0x756:0x75c]
        cells=[];rgba=Image.new('RGBA',(40,40));opaque=0
        assert c.y%4==0 and c.y<=32,(state,frame,c.y)
        for slot in range(c.y//4):
            y,tile,attr,x=m[0x200+4*slot:0x204+4*slot]
            at=(tile&1)*4096+(tile&254)*16
            raw=bytes(m.ppuread(at+i)for i in range(32))
            if raw not in lookup:lookup[raw]=len(patterns);patterns.append(raw)
            assert lookup[raw]<512
            dx=x-128;dy=y+1-112;cell=dict(dx=dx,dy=dy,pattern_index=lookup[raw],pattern_byte_offset=lookup[raw]*32,attributes=attr,original_tile=tile,original_chr_bank=m.ca(at)//1024)
            cells.append(cell)
            for yy in range(16):
                py=15-yy if attr&128 else yy
                for xx in range(8):
                    px=7-xx if attr&64 else xx;v=((raw[(py//8)*16+py%8]>>(7-px))&1)|(((raw[(py//8)*16+py%8+8]>>(7-px))&1)<<1)
                    if v:
                        color=m.ppuread(0x3f10+(attr&3)*4+v)&63
                        rgb=tuple(palette[color*3:color*3+3]);rx=dx+xx+4;ry=dy+yy+3
                        assert 0<=rx<40 and 0<=ry<40,(state,frame,cell,rx,ry)
                        rgba.putpixel((rx,ry),rgb+(255,));opaque+=1
        return dict(state=state,frame=frame,facing=facing,gravity=gravity,metadata=meta,cells=cells,opaque_pixels=opaque,animation_mask=m[0x5a0],source_sprite_palette=[m.ppuread(0x3f10+i)for i in range(16)]),rgba
    # Only the original per-state frame-map entries that are not FF sentinels.
    c=M.machine();c.memory.regs[6:8]=[12,13];c.memory.map();t=c.memory[0x800e]+256*c.memory[0x800f];meta=c.memory[t]+256*c.memory[t+1]
    frame_map=[list(c.memory[meta+13+s*8:meta+21+s*8])for s in range(8)]
    sheet=Image.new('RGB',(8*40,8*50),'#202c40');draw=ImageDraw.Draw(sheet)
    for state in range(8):
        for frame in range(8):
            if frame_map[state][frame]==255:continue
            for facing in [0,64]:
                for gravity in [0,128]:
                    q,rgba=packet(state,frame,facing,gravity);packets.append(q)
                    if facing==0 and gravity==0:
                        sheet.paste(rgba,(frame*40,state*50+10),rgba);draw.text((frame*40+2,state*50),f'{state}:{frame}',fill='white')
    body=b''.join(patterns);(OUT/'body.chr').write_bytes(body);sheet.save(OUT/'body-preview.png')
    # Exact archived native reference is read in memory; no history expansion.
    zpath=ROOT/'build/_recovery/legacy-sources-2026-10-31.zip'
    archived='full-menu-source-art-v1/native/metalstorm-discovery-v1/frame-00600.bin'
    with zipfile.ZipFile(zpath)as z:
        index=json.loads(z.read('index.json'));entry=next(x for x in index if x['path']==archived);native=z.read('objects/'+entry['sha256'])
    assert sha(native)==entry['sha256']and len(native)==14638
    assert native[:8]==b'NATIVE01'
    native_oam=native[14:270];native_chr=native[270:8462];native_palette=native[8462:8494];native_ram=native[-2048:]
    # Native original idle raster: every opaque pixel is reconstructed from original cells/patterns/palette.
    native_image=Image.new('RGBA',(256,240));source_slots=[61,62,63,0,1,2];count=0
    for slot in sorted(source_slots,reverse=True):
        y,tile,attr,x=native_oam[4*slot:4*slot+4];at=(tile&1)*4096+(tile&254)*16
        raw=native_chr[at:at+32];assert len(raw)==32
        for yy in range(16):
            py=15-yy if attr&128 else yy
            for xx in range(8):
                px=7-xx if attr&64 else xx;v=((raw[(py//8)*16+py%8]>>(7-px))&1)|(((raw[(py//8)*16+py%8+8]>>(7-px))&1)<<1)
                if v:
                    color=native_palette[16+(attr&3)*4+v]&63
                    native_image.putpixel((x+xx,y+1+yy),tuple(palette[color*3:color*3+3])+(255,));count+=1
    bbox=native_image.getbbox();assert bbox;native_crop=native_image.crop(bbox)
    # Run original renderer on archived source RAM, preserving its actor pose and cameras.
    c=M.machine();m=c.memory;m[:2048]=native_ram;m.regs[6:8]=[12,13];m.map();table=m[0x800e]+256*m[0x800f];m[0x24],m[0x25]=table&255,table>>8
    # The original capture's visible OAM was published from the preceding actor state.
    # Its idle packet, palette and physical patterns must appear among the valid exports;
    # allow OAM rotation/anchor placement only, never fabricated tile/palette pixels.
    q,image=packet(native_ram[0x4e0],native_ram[0x4f8],native_ram[0x540]&64,native_ram[0x540]&128)
    crop=image.crop(image.getbbox());native_crop.save(OUT/'native-reference-idle.png')
    native_equal=crop.size==native_crop.size and crop.tobytes()==native_crop.tobytes()
    assert native_equal,('original archive idle mismatch',crop.size,native_crop.size,native_ram[0x4e0],native_ram[0x4f8],q)
    result=dict(passed=True,donor_sha256=M.EXPECTED,CPU_original_renderer=True,native_host=False,installed=False,renderer_entry=0xf282,metadata_bank_pair=[12,13],metadata_address=meta,valid_frame_map=frame_map,contexts=len(packets),unique8x16_patterns=len(patterns),CHR_bytes=len(body),CHR_sha256=sha(body),packet_origin='Original world top-left X/Y; dy includes NES OAM Y+1. Pattern byte offsets address32 exact original CHR bytes, not allocated host tiles; attributes retain native palette/priority/X/Y flips. Host per-pose CHR allocation remains required.',packets=packets,native_reference=dict(archive=str(zpath),member=archived,member_sha256=entry['sha256'],slots=source_slots,opaque_pixels=count,cropped_idle_matches_original_native_pixels=True),scope='Original F282 renderer executed for every non-FF player frame-map entry, both facings and both gravity directions. One archived original native idle packet reconstructs pixel-exactly. CPU renderer uses untimed PPU readiness; source art packet generation is not host CHR/OAM or native gameplay admission.')
    result['bindings']={str(p.resolve()):sha(p.read_bytes())for p in[Path(__file__),Path(M.__file__),M.ROM,ROOT/'tools/audit/verify_native_relocation.py',ROOT/'tools/Windows/NEXXT 3.0/defaults/nes.pal',OUT/'body.chr',OUT/'body-preview.png',OUT/'native-reference-idle.png']}
    (OUT/'art.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','packets']}))

if __name__=='__main__':main()
