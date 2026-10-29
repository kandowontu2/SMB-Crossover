"""Recover Bowser's real SMB3 OAM poses and verify them against original CPU code."""
from pathlib import Path
import hashlib
import json
import re

from PIL import Image, ImageDraw
from acquire_nesasm_source_v1 import ROOT, bind
from verify_native_relocation import NesMPU

OUT=ROOT/'build/smb3-bowser-source-assets-v1'
MATCH=ROOT/'build/smb3-original-source-match-v1/proof.json'
ROM=Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes')


def digest(b):return hashlib.sha256(b).hexdigest()


def decode(tile):
    return bytes(((tile[y]>>(7-x))&1)|(((tile[y+8]>>(7-x))&1)<<1)for y in range(8)for x in range(8))


def labels():
    result={}
    for name,value in re.findall(r'^(\w+)\s+= \$([\dA-F]+)$',(MATCH.parent/'smb3.fns').read_text(),re.M):
        result[name]=int(value,16)
    return result


def source_draw(raw,s,frame,flips,counter):
    memory=[0]*65536
    for address,bank in [(0x8000,30),(0xa000,1),(0xc000,0),(0xe000,31)]:
        memory[address:address+8192]=raw[16+bank*8192:16+(bank+1)*8192]
    for name,value in [('Objects_X',96),('Objects_Y',64),('Objects_Frame',frame),
                        ('Objects_FlipBits',flips),('Counter_1',counter),('SlotIndexBackup',0)]:
        memory[s[name]]=value
    memory[0x200:0x300]=[0xf8]*256
    c=NesMPU(memory=memory,pc=s['Bowser_Draw']);c.x=0;c.sp=253;c.stPushWord(0x5aff)
    steps=0
    while c.pc!=0x5b00:
        steps+=1
        assert steps<10000,hex(c.pc)
        assert memory[c.pc]!=0,('Unexpected original BRK',hex(c.pc))
        c.step()
    assert c.sp==253 and c.x==0
    table=16+8192+(s['Bowser_SprRAMOff']&8191)+counter*16
    offsets=raw[table:table+12]
    parts=[list(memory[0x200+offset:0x204+offset])for offset in offsets]
    return parts,c.processorCycles


def main():
    assert not(OUT/'handoff.json').exists(),'Preserve frozen original art'
    proof=json.loads(MATCH.read_text());assert proof['original_PRG_exact']
    raw=ROM.read_bytes();assert bind(ROM)['sha256']==proof['original']['sha256']
    s=labels();chrdata=raw[16+262144:]
    def prg(bank,pc,size):return raw[16+bank*8192+(pc&8191):16+bank*8192+(pc&8191)+size]
    palette=list(prg(27,s['PalSet_Fort']+9*16+12,4))
    assert palette==[0xff,0x1a,0x30,0x27]
    # Actual Player_DoGameplay selects common sprite quarter4 in a fortress.
    # ObjNorm_Bowser selects quarters3A and3B. Tile71 comes from common4.
    banks={1:4,2:0x3a,3:0x3b}
    def pattern(tile):
        index=tile&0xfe
        quarter=index//64
        assert tile&1 and quarter in banks
        start=banks[quarter]*1024+(index&63)*16
        return chrdata[start:start+32]
    assert pattern(0x71)==bytes(32),'Do not invent the common blank pattern'
    source_cases=[];frames=[];pages=[]
    for frame in range(9):
        tiles=list(prg(1,s['Bowser_SprPats']+frame*16,12))
        intrinsic=frame in [4,6,7]
        yshift=4 if frame in [1,7]else 0
        for flips in [0,0x40,0x80,0xc0]:
            for counter in [0,1]:
                expected=[]
                for i,tile in enumerate(tiles):
                    row,column=divmod(i,4)
                    x=96+(3-column if flips&0x40 and not intrinsic else column)*8
                    y=64+(2-row if flips&0x80 else row)*16+yshift
                    attribute=flips
                    if intrinsic:attribute=(flips&0x80)|(0x40 if column>=2 else 0)
                    expected.append([y,tile,attribute|3,x])
                actual,cycles=source_draw(raw,s,frame,flips,counter)
                assert actual==expected,(frame,flips,counter,actual,expected)
                source_cases.append(dict(frame=frame,flips=flips,counter=counter,
                    original_CPU_cycles=cycles,original_OAM_sha256=digest(bytes(sum(actual,[])))))
        parts=[]
        for i,tile in enumerate(tiles):
            pair=pattern(tile)
            if not any(pair):continue
            row,column=divmod(i,4)
            parts.append((pair,column*8,row*16+yshift,0x40 if intrinsic and column>=2 else 0))
        needed=set(p for p,_,_,_ in parts)
        choices=[(len(needed-set(page)),i)for i,page in enumerate(pages)if len(needed|set(page))<=32]
        if choices:_,page_index=min(choices)
        else:page_index=len(pages);pages.append([])
        page=pages[page_index]
        for pair in sorted(needed):
            if pair not in page:page.append(pair)
        descriptor=[4*len(parts)];pixels=bytearray(32*52)
        for pair,x,y,attribute in parts:
            descriptor += [page.index(pair)*2,attribute,(y-1)&255,(x-8)&255]
            for half in range(2):
                values=decode(pair[half*16:half*16+16])
                for yy in range(8):
                    for xx in range(8):
                        destx=x+(7-xx if attribute&0x40 else xx)
                        pixels[(y+half*8+yy)*32+destx]=values[yy*8+xx]
        # Native packed-record reconstruction must retain all colored pixels.
        reconstructed=bytearray(32*52)
        for i in range(1,len(descriptor),4):
            tile,attr,dy,dx=descriptor[i:i+4];dx=dx-256 if dx>=128 else dx;dy=dy-256 if dy>=128 else dy
            pair=page[tile//2]
            for half in range(2):
                values=decode(pair[half*16:half*16+16])
                for yy in range(8):
                    for xx in range(8):
                        x=dx+8+(7-xx if attr&0x40 else xx);y=dy+1+half*8+yy
                        reconstructed[y*32+x]=values[yy*8+xx]
        assert reconstructed==pixels
        frames.append(dict(frame=frame,source_tiles=tiles,original_OAM_Y_shift=yshift,
            intrinsic_half_mirror=intrinsic,relative_CHR_page=page_index,descriptor=descriptor,
            original_pixels_exact=True,pixels_sha256=digest(pixels),parts=len(parts),_pixels=pixels))
    assert len(pages)<=4
    packed=b''.join(b''.join(page)+bytes((32-len(page))*32)for page in pages)
    packed+=bytes(4096-len(packed))
    OUT.mkdir(exist_ok=True);(OUT/'bowser3.chr').write_bytes(packed)
    lines=['; Source SMB3 Bowser, real original 12-part OAM table and half mirrors.',
        '; Data component only. Player controls/collision/lifecycle/audio not yet admitted.',
        '.segment "BOWSER_ART"','Bw3ArtStart:',
        'Bw3PosePages: .byte '+','.join(str(r['relative_CHR_page'])for r in frames),
        'Bw3PoseLo: .byte '+','.join('<Bw3Pose'+str(i)for i in range(9)),
        'Bw3PoseHi: .byte '+','.join('>Bw3Pose'+str(i)for i in range(9))]
    for row in frames:lines+=['Bw3Pose'+str(row['frame'])+': .byte '+','.join(map(str,row['descriptor']))]
    lines+=['Bw3Palette: .byte $0f,$1a,$30,$27','Bw3ArtEnd:']
    (OUT/'bowser3-art.inc').write_text('\n'.join(lines)+'\n')
    image=Image.new('RGB',(360,540),'#18242c');draw=ImageDraw.Draw(image)
    colors=['#18242c','#00a800','#ffffff','#fc9838']
    for row in frames:
        i=row['frame'];ox=(i%3)*120+12;oy=(i//3)*180+20
        draw.text((ox,oy-16),'BOWSER '+str(i),fill='white')
        for y in range(52):
            for x in range(32):
                v=row['_pixels'][y*32+x]
                if v:draw.rectangle((ox+x*3,oy+y*3,ox+x*3+2,oy+y*3+2),fill=colors[v])
        row.pop('_pixels')
    image.save(OUT/'original-bowser3-poses.png')
    result=dict(status='Original SMB3 Bowser art and genuine original renderer CPU controls only; not playable',
        original=bind(ROM),source_match=bind(MATCH),tool=bind(__file__),
        original_renderer=dict(bank=1,address=hex(s['Bowser_Draw']),genuine_original_cases=source_cases,
            source_records='Bowser_SprPats: nine 16-byte rows, first12 parts; preserve 1/7 Y+4 and 4/6/7 half mirrors.'),
        original_palette=palette,native_palette=[15,26,48,39],
        source_palette_path='Fortress/Bowser header LEVEL2_OBJPAL09 -> PalSet_Fort row9 -> spriteP3; FF transparent slot replaced with native area-owned universal color.',
        source_CHR_mapping=dict(common_PPU1400=4,boss_PPU1800=58,boss_PPU1c00=59,tile71_actual_32_bytes_zero=True),
        frames=frames,used_1KB_pages=len(pages),pattern_pairs_per_page=list(map(len,pages)),
        proposed_CHR=[824,827],remaining_Bowser_CHR=[828,831],
        preview='Approximate RGB representation of exact source palette indices; no native screenshot claim.',
        playable_adaptation='Original Bowser is a boss NPC. Playable movement, controls, terrain bounds and upgrades require authored crossover rules; no original player-physics claim.',
        source_credit='Southbird, https://www.sonicepoch.com/sm3mix/',
        outputs=[bind(OUT/n)for n in ['bowser3.chr','bowser3-art.inc','original-bowser3-poses.png']],
        native_run=False,host_integration=False)
    (OUT/'handoff.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(handoff=bind(OUT/'handoff.json'),frames=9,source_CPU_cases=len(source_cases),pages=len(pages))))


if __name__=='__main__':main()
