"""Compose RCR with current Celeste/Mac sources in a private review overlay.

Real menu thumbnail, bounded HP row, actual CHR segmentation; no padding patch
or canonical/shared-source adoption. Frozen prior candidates remain untouched.
"""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
from PIL import Image
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/reference')]
from build_roster_expansion_menu import navigation,position,encode,tile_pixel
from prepare_river_city_reference import native_pixels,NATIVE
from prepare_river_city_assets import POSES
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def once(s,a,b):assert s.count(a)==1,a;return s.replace(a,b)
def main():
    base=R/'build/roster-union-celeste-mac-v1.nes'
    assert sha(base)=='00597cddbff069acbd6fad1571b7b734c5c5f72bc67da49e672565e6c2c4e94d'
    out=R/'build/river-city-shared-v3-overlay';assert not out.exists();(out/'src').mkdir(parents=True)
    inputs=[]
    def edit(name,fn):
        p=R/name;inputs.append(dict(path=str(p),sha256=sha(p)))
        d=out/name;d.parent.mkdir(parents=True,exist_ok=True);d.write_text(fn(p.read_text()),newline='\n')
    edit('src/river_city_core.s',lambda s:once(s,' jsr RcIntegrate\n',' lda Player_Y_Position\n sta RcTerrainOldY\n jsr RcIntegrate\n jsr RcTerrainWallPrepass\n'))
    def wrapper(s):
        s=once(s,'.include "river_city_core.s"','.include "river_city_core.s"\n.include "river_city_wall_prepass.s"')
        s=once(s,'.include "river_city_render.s"','.include "river_city_shared_palette_render.inc"')
        s=once(s,'.include "river_city_art.inc"','.include "river_city_shared_palette_art.inc"')
        return once(s,'.incbin "chr/characters/river-city.chr"','.incbin "chr/characters/river-city-shared-palette.chr",0,8192\n.segment "RIVER_CITY_EXTRA_CHR"\n.incbin "chr/characters/river-city-shared-palette.chr",8192,3072')
    edit('src/river_city.s',wrapper)
    # Keep the frozen shared-palette packet unchanged. This sparse successor
    # moves HP48 from clipped row0 to visible row1, aligned to the native name.
    def hud(s):
        start=s.index('.proc RcUi\n');end=s.index('.endproc',start)
        body=once(s[start:end],' lda #4\n sta VRAM_Buffer1+1,x\n sta VRAM_Buffer1+2,x',
                  ' lda #$23\n sta VRAM_Buffer1+1,x\n lda #4\n sta VRAM_Buffer1+2,x')
        return s[:start]+body+s[end:]
    edit('src/river_city_shared_palette_render.inc',hud)
    def cfg(s):
        s=once(s,'    LM_CHR_MEM: start=$a7000,size=$a000,type=ro,fill=yes,file=%O,fillval=$00;',
            '    LM_CHR_MEM: start=$a7000,size=$2400,type=ro,fill=yes,file=%O,fillval=$00;\n'
            '    RIVER_CITY_EXTRA_CHR_MEM: start=$a9400,size=$c00,type=ro,fill=yes,file=%O,fillval=$00;\n'
            '    ROGUE_DAWN_CHR_MEM: start=$aa000,size=$4000,type=ro,fill=yes,file=%O,fillval=$00;\n'
            '    LM_UNUSED_CHR_MEM: start=$ae000,size=$2000,type=ro,fill=yes,file=%O,fillval=$00;\n'
            '    LM_TAIL_CHR_MEM: start=$b0000,size=$1000,type=ro,fill=yes,file=%O,fillval=$00;')
        return once(s,'    MAC_ROSTER_CHR: load=LM_CHR_MEM,type=ro,optional=yes;',
            '    MAC_ROSTER_CHR: load=LM_CHR_MEM,type=ro,optional=yes;\n'
            '    MAC_ROSTER_CHR_TAIL: load=LM_TAIL_CHR_MEM,type=ro,optional=yes;\n'
            '    RIVER_CITY_EXTRA_CHR: load=RIVER_CITY_EXTRA_CHR_MEM,type=ro,optional=yes;\n'
            '    ROGUE_DAWN_CHR: load=ROGUE_DAWN_CHR_MEM,type=ro,optional=yes;')
    edit('smb1base-mmc5-expanded.cfg',cfg)
    mac=(R/'chr/characters/mac-roster.chr').read_bytes()
    assert len(mac)==40960 and mac[9216:36864]==bytes(27648),'Reused Mac pages must be genuine unused zeroes'
    edit('src/mac_roster.s',lambda s:once(s,'.incbin "chr/characters/mac-roster.chr"',
        '.incbin "chr/characters/mac-roster.chr",0,9216\n.segment "MAC_ROSTER_CHR_TAIL"\n.incbin "chr/characters/mac-roster.chr",36864,4096'))
    menu=(R/'src/roster_expansion_menu.inc').read_text();inputs.append(dict(path=str(R/'src/roster_expansion_menu.inc'),sha256=sha(R/'src/roster_expansion_menu.inc')))
    def get(n):return list(map(int,re.search(n+r':\n \.byte ([^\n]+)',menu)[1].split(',')))
    present=get('X5MenuPresent');chars=get('X5MenuCharacters');assert present[20]==0 and chars[20]==0
    present[20]=1;chars[20]=21;edges=navigation([i for i,v in enumerate(present)if v])
    tables={'X5MenuPresent':present,'X5MenuCharacters':chars}
    for d in ('left','right','up','down'):tables['X5Menu'+d.title()]=[edges[i][d]if i in edges else 0 for i in range(28)]
    for label,values in tables.items():menu,n=re.subn(label+r':\n \.byte [^\n]+',label+':\n .byte '+','.join(map(str,values)),menu);assert n==1
    (out/'src/roster_expansion_menu.inc').write_text(menu,newline='\n')
    # Decode the actual authentic standing body, then use the existing menu's
    # 16x24 nearest-neighbor silhouette convention. All other cells stay exact.
    native,_,_=native_pixels(NATIVE.read_bytes(),POSES[0][1],0,1)
    minx=min(x for x,y in native);miny=min(y for x,y in native)
    pic=Image.new('RGBA',(max(x for x,y in native)-minx+1,max(y for x,y in native)-miny+1))
    colors={1:(0,0,0,255),2:(248,248,248,255),3:(248,176,104,255),4:(40,96,192,255)}
    for(x,y),v in native.items():pic.putpixel((x-minx,y-miny),colors[v])
    factor=min(1,16/pic.width,24/pic.height)
    pic=pic.resize((max(1,round(pic.width*factor)),max(1,round(pic.height*factor))),Image.Resampling.NEAREST)
    canvas=Image.new('RGBA',(16,24));canvas.alpha_composite(pic,((16-pic.width)//2,24-pic.height))
    packed=bytearray((R/'chr/characters/packed-mmc5-roster-expanded.chr').read_bytes())
    nt=bytearray((R/'chr/raw/roster-expansion-menu.bin').read_bytes());data=bytearray(packed[4096:8192])
    used=set(nt[:960]);pool={bytes(data[i*16:(i+1)*16]):i for i in used};free=[i for i in range(64,252)if i not in used]
    top,col=position(20);changed=[]
    for ty,tx in [(y,x)for y in range(3)for x in range(2)]:
        values=[]
        for y in range(8):
            line=[]
            for x in range(8):
                r,g,b,a=canvas.getpixel((tx*8+x,ty*8+y));v=.299*r+.587*g+.114*b
                line.append(0 if a<128 else 1 if v<95 else 2 if v<200 else 3)
            values.append(line)
        pattern=encode(values)
        if pattern not in pool:
            assert free,'No menu CHR capacity';t=free.pop(0);pool[pattern]=t;data[t*16:(t+1)*16]=pattern;changed.append(t)
        nt[(top+ty)*32+col+tx]=pool[pattern]
    packed[4096:8192]=data
    for name,raw in [('chr/characters/packed-mmc5-roster-expanded.chr',packed),('chr/raw/roster-expansion-menu.bin',nt)]:
        inputs.append(dict(path=str(R/name),sha256=sha(R/name)));p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    canvas.resize((128,192),Image.Resampling.NEAREST).save(out/'thumbnail-review.png')
    output=R/'build/river-city-shared-v3.nes';assert not output.exists()
    command=['python','-B','tools/build_mmc5_expanded.py','--source-overlay',str(out),'--output',str(output)]
    r=subprocess.run(command,cwd=R,capture_output=True,text=True);(out/'build.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
    # Real layout, no postlink mutation; original Mac used patterns unchanged.
    actual=output.read_bytes();cb=16+1048576
    assert actual[cb+668*1024:cb+677*1024]==mac[:9216]
    assert actual[cb+704*1024:cb+708*1024]==mac[36864:]
    assert actual[cb+677*1024:cb+680*1024]==(R/'chr/characters/river-city-shared-palette.chr').read_bytes()[8192:]
    assert actual[cb+680*1024:cb+704*1024]==bytes(24576)
    files=[Path(__file__),output,output.with_suffix('.dbg'),output.with_suffix('.lbl'),R/'src/river_city_wall_prepass.s']+[p for p in out.rglob('*')if p.is_file()]
    proof=dict(status='Private composed candidate; no native/shared-source/canonical adoption',ROM_sha256=sha(output),parent_sha256=sha(base),native_run=False,
        source_preimages=inputs,menu_new_tiles=changed,free_menu_tiles=len(free),command=command,
        limits=['Native composed route/PPU/ABI pending','Rogue CHR reserved, not yet populated or playable'],bindings=[dict(path=str(p),sha256=sha(p))for p in files])
    (out/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(ROM_sha256=sha(output),new_thumbnail_tiles=changed,remaining_tiles=len(free))))
if __name__=='__main__':main()
