"""Build a source-linked, bounded four-by-eight front end on the current MMC5.

Playable owners retain their original dispatch. Unfinished requested profiles
are visible, named and browseable, but cannot enter unsupported gameplay code.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys
from collections import Counter
from itertools import groupby
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'build/menu-fourth-row-fix-v2'
BASE=ROOT/'build/pit-retold-host-v3'
NAMES=['SUPERMAAA','ROGUE DAWN','KARNOV','SHINOBI','METAL STORM',
       'FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF','GOKU',
       'SMB2 MARIO','SMB2 LUIGI','SMB2 TOAD','SMB2 PEACH','GIMMICK',
       'SMB3 BOWSER','SMB1 BOWSER','DONKEY KONG','HULK HOGAN','TED DIBIASE',
       'BAM BAM BIGELOW','HONKY TONK MAN','RANDY SAVAGE','ANDRE THE GIANT',
       'EXCITEBIKE','PRINCE PERSIA','BURNS','SMITH','IRON','BEANS',
       'ARTHUR','QUICK MAN','THOMAS']
KEYS=['supermaaa','rogue-dawn','karnov','shinobi','metal-storm',
      'ff-fighter','ff-white-mage','ff-black-mage','ff-thief','goku',
      'smb2-mario','smb2-luigi','smb2-toad','smb2-peach','gimmick',
      'bowser-smb3','bowser-smb1','donkey-kong','wwf-5','wwf-0','wwf-1',
      'wwf-2','wwf-3','wwf-4','excitebike','persia','contra-force-burns',
      'contra-force-smith','contra-force-iron','contra-force-beans',
      'arthur','quick-man','thomas']
RAW=[0,1,2,3,4,5,6,7,12,9,10,11,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
SLOT_COUNT=32


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,newline='\n')
def tile(data,t,x,y):return (data[t*16+y]>>(7-x)&1)|((data[t*16+y+8]>>(7-x)&1)<<1)
def encode(v):return bytes(sum(((v[y][x]>>p)&1)<<(7-x)for x in range(8))for p in range(2)for y in range(8))
def fit(pic,size):
    pic=pic.convert('RGBA');pic=pic.crop(pic.getbbox())
    scale=min(1,size[0]/pic.width,size[1]/pic.height)
    if scale<1:pic=pic.resize((max(1,round(pic.width*scale)),max(1,round(pic.height*scale))),Image.Resampling.NEAREST)
    out=Image.new('RGBA',size);out.alpha_composite(pic,((size[0]-pic.width)//2,size[1]-pic.height));return out
def position(s):return 4+s//8*4,4+s%8*3


def assets(out):
    sources={};bindings={}
    for path in [ROOT/'build/full-menu-known-art-v1/all-assets-manifest.json',ROOT/'build/full-menu-source-art-v1/menu-assets.json',ROOT/'build/full-menu-final-art-v1/manifest.json',ROOT/'build/full-menu-quickman-art-v1/manifest.json']:
        if not path.exists():continue
        bindings[str(path)]=sha(path);data=json.loads(path.read_text())
        for row in data.get('entries',data.get('profiles',[])):
            key=row.get('key',row.get('name'));key={'metalstorm':'metal-storm'}.get(key,key.replace('contraforce-','contra-force-'));p=Path(row.get('RGBA',row.get('path','')))
            if p.is_file():
                if row.get('output_sha256'):assert sha(p)==row['output_sha256'],key
                sources[key]=p;bindings[str(p)]=sha(p)
    wwf=ROOT/'build/wwf-menu-art-v1/menu-assets.json'
    if wwf.exists():
        bindings[str(wwf)]=sha(wwf)
        for row in json.loads(wwf.read_text())['variants']:
            p=Path(row['colored_idle_preview']);sources['wwf-'+str(row['id'])]=p;bindings[str(p)]=sha(p)
    palette_path=ROOT/'tools/Windows/NEXXT 3.0/defaults/nes.pal'
    b=palette_path.read_bytes();palette=[tuple(b[i:i+3])for i in range(0,192,3)]
    bindings[str(palette_path)]=sha(palette_path)
    # A neutral question marker denotes unavailable source art; never another hero.
    missing=Image.new('RGBA',(16,24));d=ImageDraw.Draw(missing)
    d.rectangle((2,2,13,21),outline=(248,184,0,255));d.text((5,5),'?',fill=(248,248,248,255))
    pictures=[];preview_pairs=[];preview_rows=[];color_rows=[];facts=[]
    for key,name in zip(KEYS,NAMES):
        p=sources.get(key);pic=Image.open(p).convert('RGBA')if p else missing.copy()
        pictures.append(pic.copy());canvas=fit(pic,(16,32))
        counts=Counter(c[:3]for c in canvas.getdata()if c[3]>=128)
        colors=[c for c,n in counts.most_common(3)]
        while len(colors)<3:colors.append(colors[-1])
        indices=[min((i for i in range(64)if i%16<13 or i==15),key=lambda i:sum((palette[i][j]-c[j])**2 for j in range(3)))for c in colors]
        color_rows.append(indices);values=[]
        for y in range(32):
            values.append([0 if canvas.getpixel((x,y))[3]<128 else 1+min(range(3),key=lambda i:sum((canvas.getpixel((x,y))[j]-palette[indices[i]][j])**2 for j in range(3)))for x in range(16)])
        parts=[]
        for top,left in [(0,0),(0,8),(16,0),(16,8)]:
            pair=b''.join(encode([line[left:left+8]for line in values[top+half*8:top+half*8+8]])for half in range(2))
            if pair not in preview_pairs:preview_pairs.append(pair)
            parts.append(preview_pairs.index(pair)*2)
        preview_rows.append(parts)
        facts.append(dict(key=key,name=name,source=str(p)if p else None,placeholder=p is None,palette=indices,preview_tiles=parts))
    assert len(preview_pairs)<=128
    (out/'pending-previews.chr').write_bytes(b''.join(preview_pairs)+bytes(4096-len(preview_pairs)*32))
    text=['.charmap $2a,$3f','FmNames:']
    for name in NAMES:
        label='*'+name;assert len(label)<=16,label
        text.append(' .byte "'+label.center(16)+'"')
    text+=['FmPreviewTiles:']+[' .byte '+','.join(map(str,r))for r in preview_rows]
    text+=['FmPreviewColors:']+[' .byte '+','.join(map(str,r))for r in color_rows]
    save(out/'src/full_roster_menu_art.inc','\n'.join(text)+'\n')
    return pictures,facts,bindings


def pack(out,pictures):
    parent=(PARENT/'candidate.nes').read_bytes();old_chr=parent[1048592+4096:1048592+8192]
    nt=(ROOT/'chr/raw/roster-expansion-menu.bin').read_bytes()
    portraits={}
    for s in list(range(21))+[22]:
        top,col=4+s//7*4,3+s%7*4;im=Image.new('RGBA',(16,24))
        for y in range(24):
            for x in range(16):
                v=tile(old_chr,nt[(top+y//8)*32+col+x//8],x%8,y%8)
                if v:im.putpixel((x,y),[(0,0,0,0),(72,72,72,255),(160,160,160,255),(248,248,248,255)][v])
        portraits[s]=im
    for s,index in {21:5,23:9,24:10,25:14,26:15,27:17,28:18,29:24,30:26,31:30}.items():portraits[s]=pictures[index]
    new=bytearray([0x24]*960+[0]*64);chrdata=bytearray(old_chr)
    def text(row,col,s):
        for i,c in enumerate(s):new[row*32+col+i]=0x24 if c==' 'else 0x3f if c=='*'else int(c)if c.isdigit()else ord(c)-55
    text(1,8,'CHOOSE YOUR HERO');text(27,5,'A OR START PLAY  B BACK');text(28,4,'D PAD MOVE  *COMING SOON')
    for c in range(2,30):new[3*32+c]=252
    for r in range(19,25):new[r*32+12:r*32+20]=bytes([254])*8
    new[960:968]=bytes([0xa5])*8;new[1008:1016]=bytes([0x55])*8;new[1016:]=bytes([0x55])*8
    for ar in [4,5]:
        for ac in [3,4]:new[960+ar*8+ac]=0xf0 if ar==4 else 0xff
    chrdata[64*16:252*16]=bytes(188*16);pool={bytes(16):36};nexttile=64
    for s,pic in portraits.items():
        canvas=fit(pic,(16,24));top,col=position(s)
        for ty in range(3):
            for tx in range(2):
                values=[]
                for y in range(8):
                    line=[]
                    for x in range(8):
                        r,g,b,a=canvas.getpixel((tx*8+x,ty*8+y));l=.299*r+.587*g+.114*b
                        line.append(0 if a<128 else 1 if l<95 else 2 if l<200 else 3)
                    values.append(line)
                data=encode(values)
                if data not in pool:assert nexttile<252;pool[data]=nexttile;nexttile+=1
                t=pool[data];chrdata[t*16:(t+1)*16]=data;new[(top+ty)*32+col+tx]=t
    # New '*' is an explicit font glyph, outside the unchanged native alphabet.
    chrdata[63*16:64*16]=encode([[3 if (x==3 and 1<=y<=5)or(y==3 and 1<=x<=5)or(x==y and 2<=x<=4)or(x+y==6 and 2<=x<=4)else 0 for x in range(8)]for y in range(8)])
    packed=bytearray((ROOT/'chr/characters/packed-mmc5-roster-expanded.chr').read_bytes());packed[4096:8192]=chrdata
    (out/'menu.nam').write_bytes(new);(out/'packed.chr').write_bytes(packed)
    runs=bytearray()
    for value,group in groupby(new):
        count=len(list(group))
        while count:
            n=min(255,count);runs+=bytes([n,value]);count-=n
    runs.append(0);(out/'menu.rle').write_bytes(runs)
    nav={}
    for s in range(SLOT_COUNT):
        row=list(range(s//8*8,min(s//8*8+8,SLOT_COUNT)));i=row.index(s)
        nav[s]={'left':row[(i-1)%len(row)],'right':row[(i+1)%len(row)]}
        for name,delta in [('up',-1),('down',1)]:
            rr=(s//8+delta)%4;nav[s][name]=min(range(rr*8,min(rr*8+8,SLOT_COUNT)),key=lambda v:(abs(v%8-s%8),v))
    lines=['; Four rows/eight columns. Seven32B tables replace eight28B tables.',
           '; Unused X5MenuPresent removed; all original following router PCs stay fixed.']
    for direction in ['left','right','up','down']:
        lines+=['X5Menu'+direction.title()+':',' .byte '+','.join(str(nav[s][direction])if s<SLOT_COUNT else '0'for s in range(32))]
    for name,values in [('Characters',RAW),('CursorLo',[((position(s)[0]+1)*32+position(s)[1]-1)&255 for s in range(32)]),('CursorHi',[32+((position(s)[0]+1)*32+position(s)[1]-1)//256 for s in range(32)])]:
        lines+=['X5Menu'+name+':',' .byte '+','.join(map(str,values))]
    save(out/'src/roster_expansion_menu.inc','\n'.join(lines)+'\n')
    return dict(slots=SLOT_COUNT,columns=8,rows=4,portrait_tiles=nexttile-64,navigation=nav)


def source(out):
    original=(BASE/'src/character_select.s').read_text();s=original
    s=s.replace('  farcall InitializeNameTables\n  lda PPUSTATUS','  lda #0\n  sta FmAlts\n  sta FmGroups\n  farcall InitializeNameTables\n  lda PPUSTATUS',1)
    s=s.replace('  farcall CheatsApplyStartingLevel','  farcall FmPending\n  bcc FmStartReady\n  lda #Sfx_Bump\n  sta Square1SoundQueue\n  jmp MenuIdle\nFmStartReady:\n  lda #0\n  sta FmAlts\n  sta FmGroups\n  farcall CheatsApplyStartingLevel',1)
    s=s.replace('CheckDirection:\n.if ::ENABLE_MMC5_EXPANDED','CheckDirection:\n.if ::ENABLE_MMC5_EXPANDED\n  farcall FmToggle\n  bcc FmLegacyToggle\n  lda CrossoverMenuIndex\n  jmp Changed\nFmLegacyToggle:',1)
    s=s.replace('farcall CmHostResolveCharacter,jmp','farcall FmResolve,jmp',1)
    s=s.replace('.proc QueueSelection\n','.proc QueueSelection\n  farcall FmPending\n  bcc FmNativeSelection\n  farcall FmQueueName\n  lda #$fd\n  jsr QueueCursor\n  jmp MenuPreviewBudget\nFmNativeSelection:\n  farcall FmNativePrepare\n',1)
    s=s.replace('.proc DrawSelectionPreview\n','.proc DrawSelectionPreview\n  farcall FmPending\n  bcc FmNativePreview\n  farcall FmDrawPreview,jmp\nFmNativePreview:\n',1)
    s=s.replace('  .repeat 9\n','  .repeat 13\n',1)
    # Direct PPU loading is still confined to BuildScreen's rendering-off path.
    start=s.index('  ldx #4\n  ldy #0\nCopyPage:')
    end=s.index('  lda #2\n  sta CrossoverMenuState',start)
    s=s[:start]+'''  ldy #0
CopyRle:
  lda (R0),y
  beq CopyDone
  tax
  iny
  bne :+
  inc R1
:
  lda (R0),y
  iny
  bne :+
  inc R1
:
CopyRun:
  sta PPUDATA
  dex
  bne CopyRun
  jmp CopyRle
CopyDone:
'''+s[end:]
    s=s.replace('.incbin "chr/raw/roster-expansion-menu.bin"','.incbin "'+(out/'menu.rle').as_posix()+'"')
    marker='  .incbin "chr/raw/character-select.bin"\n.endif\n.popseg'
    assert s.count(marker)==1
    s=s.replace(marker,'  .incbin "chr/raw/character-select.bin"\n.endif\n.if ::ENABLE_MMC5_EXPANDED\n.res $c8c-(*-CrossoverMenuInput),$ff\n.endif\n.popseg')
    save(out/'src/character_select.s',s)
    save(out/'src/menu_vram_budget.s',(PARENT/'src/menu_vram_budget.s').read_text())
    save(out/'src/full_roster_menu.s',(ROOT/'src/full_roster_menu.s').read_text())
    entry=(BASE/'entrypoint.s').read_text().replace('.incbin "chr/characters/packed-mmc5-roster-expanded.chr"','.incbin "'+(out/'packed.chr').as_posix()+'"')
    entry+='\n.include "full_roster_menu.s"\n.pushseg\n.segment "FULL_ROSTER_PREVIEW_CHR"\n.incbin "'+(out/'pending-previews.chr').as_posix()+'"\n.popseg\n'
    save(out/'entrypoint.s',entry)
    cfg=(BASE/'smb1base-mmc5-expanded.cfg').read_text()
    old='X5_NEW_4C: start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$4c;'
    assert cfg.count(old)==1
    cfg=cfg.replace(old,'X5_NEW_4C: start=$c000, size=$1979, type=ro, file=%O, fill=yes, fillval=$ff, bank=$4c;\n    FULL_MENU_MEM: start=$b979, size=$687, type=ro, file=%O, fill=yes, fillval=$ff, bank=$4c;')
    cfg=cfg.replace('VIC_GFX:load=X5_NEW_4C,type=ro;','VIC_GFX:load=X5_NEW_4C,type=ro;\n    FULL_ROSTER_MENU:load=FULL_MENU_MEM,type=ro;')
    cfg=cfg.replace('KAMIKAZE_CHR: load=LM_UNUSED_CHR_MEM,type=ro,start=$ae000,optional=yes;','KAMIKAZE_CHR: load=LM_UNUSED_CHR_MEM,type=ro,start=$ae000,optional=yes;\n    FULL_ROSTER_PREVIEW_CHR:load=LM_UNUSED_CHR_MEM,type=ro,start=$af000;')
    save(out/'full-menu.cfg',cfg)


def build(out):
    proof=json.loads((PARENT/'build-proof.json').read_text());commands=[]
    for raw in proof['commands']:
        command=list(raw)
        if Path(command[0]).name.lower()=='ca65.exe':
            command[1:1]=['-I',str(out/'src')]
            for key in ['-o','--create-full-dep']:
                ix=command.index(key)+1;command[ix]=str(out/Path(command[ix]).name)
            if command[-1]==str(BASE/'entrypoint.s'):command[-1]=str(out/'entrypoint.s')
        else:
            for i,a in enumerate(command):
                if a.startswith('--dbgfile,'):command[i]='--dbgfile,'+str(out/'candidate.dbg')
                elif a==str(BASE/'smb1base-mmc5-expanded.cfg'):command[i]=str(out/'full-menu.cfg')
                elif a in [str(PARENT/n)for n in ['main.o','skin.o','gb.o','candidate.nes','candidate.lbl']]:command[i]=str(out/Path(a).name)
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        save(out/'build-last.log',result.stdout+result.stderr)
        assert result.returncode==0,result.stdout+result.stderr
        commands.append(command)
    sys.path.insert(0,str(ROOT/'tools'));from prepare_cv3_dmc_mirror import prepare
    prepare(ROOT,out/'candidate.nes')
    return commands


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'build/full-roster-menu-v1');args=ap.parse_args();out=args.output.resolve()
    (out/'src').mkdir(parents=True,exist_ok=True)
    pictures,facts,bindings=assets(out);layout=pack(out,pictures);source(out);commands=build(out)
    parent=(PARENT/'candidate.nes').read_bytes();candidate=(out/'candidate.nes').read_bytes()
    assert len(parent)==len(candidate)==2097168 and parent[:16]==candidate[:16]
    chrchanges=sorted({(i-1048592)//1024 for i in range(1048592,len(parent))if parent[i]!=candidate[i]})
    assert set(chrchanges)<=set([4,5,6,7,700,701,702,703]),chrchanges
    for p in [Path(__file__),ROOT/'src/full_roster_menu.s',PARENT/'build-proof.json',PARENT/'candidate.nes']+list((out/'src').glob('*'))+[out/'full-menu.cfg',out/'entrypoint.s',out/'menu.nam',out/'packed.chr',out/'pending-previews.chr',out/'candidate.nes',out/'candidate.lbl',out/'candidate.dbg']:
        bindings[str(p)]=sha(p)
    report=dict(status='SOURCE_BUILT_MENU_NATIVE_VERIFICATION_PENDING',parent=sha(PARENT/'candidate.nes'),candidate=sha(out/'candidate.nes'),layout=layout,pending_profiles=facts,CHR_changed=chrchanges,commands=commands,bindings=bindings)
    save(out/'build-proof.json',json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(candidate=report['candidate'],layout={k:v for k,v in layout.items()if k!='navigation'},missing_art=[r['key']for r in facts if r['placeholder']],CHR_changed=chrchanges)))


if __name__=='__main__':main()
