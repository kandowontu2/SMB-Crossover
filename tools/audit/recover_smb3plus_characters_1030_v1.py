"""Recover Infidelity's actual Toad/Peach draw, palette and CHR consumers.

This produces source assets and CPU evidence, not a playable-host admission.
"""
from pathlib import Path
import hashlib
import json
import sys
from PIL import Image, ImageDraw
from py65.disassembler import Disassembler

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from discover_smb3plus_chr_routes_1030_v1 import ChrRomBus,DONOR,EXPECTED
from benj_mario_donor_trace_1030_v1 import MPU

O=R/'build/smb3plus-original-characters-1030-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not O.exists()and sha(DONOR)==EXPECTED
    raw=DONOR.read_bytes();original_chr=raw[16+524288:]
    native={}
    for name,character in [('toad',2),('peach',3)]:
        packet=R/f'build/smb3plus-{name}-donor-native-1030-v2/discovery'
        q=json.loads((packet/'ready.json').read_text())
        result=json.loads((packet/'capture/binding.json').read_text())
        assert result['exit_code']==0 and result['ROM_sha256']==EXPECTED
        for p,s in result['bindings'].items():assert sha(p)==s,p
        assert (packet/'capture/ram3230.bin').read_bytes()[0x119]==character
        native[name]=dict(packet=str(packet),ready_sha256=sha(packet/'ready.json'),
            result_sha256=sha(packet/'capture/binding.json'),selected_character=character,
            scope='Native controller-only selection/map observations, not a source physics or campaign test.')
    snapshot=(Path(native['peach']['packet'])/'capture/ram3600.bin').read_bytes()
    bus=ChrRomBus(raw);cpu=MPU(memory=bus);bus.cpu=cpu

    def state(character,form,frame,facing):
        bus.ram[:0x8000]=snapshot
        bus.select=0x47;bus.reg[6]=29;bus.reg[7]=snapshot[0x720];bus.remap()
        values={0x119:character,0x11e:character,0x726:0,0xed:form,0xee:frame,0xef:facing,
            0x90:64,0xa2:160,0x87:0,0x543:0,0x544:0,0x545:0,0xfd:0,0x517:0,
            0x140:0,0x142:0,0x144:0,0x145:0}
        for address,value in values.items():bus.ram[address]=value
        bus.ram[0x552:0x556]=bytes(4)

    def run(entry,stop=0x300):
        cpu.pc=entry;cpu.sp=0xfd;cpu.p=0x30
        bus.ram[0x1fe:0x200]=bytes([0xff,2])
        start=cpu.processorCycles
        for count in range(10000):
            if cpu.pc==stop:return cpu.processorCycles-start
            assert bus[cpu.pc]!=0,('BRK',hex(cpu.pc),bus.banks)
            cpu.step()
        raise AssertionError(('Bounded source function did not finish',hex(cpu.pc)))

    palettes=[]
    for character in [0,1,2,3]:
        for player in [0,1]:
            for form in range(9):
                state(character,0,0,0)
                bus.reg[7]=32;bus.remap();bus.ram[0x726]=player
                cpu.x=form
                cost=run(0xa040,0xa073)
                actual=bytes(bus.ram[0x7d2:0x7d5])
                table=16+32*8192+0x560+character*24
                index=raw[16+32*8192+0x553+form]
                assert actual==raw[table+index:table+index+3]
                palettes.append(dict(character=character,player=player,form=form,
                    visible_colors=list(actual),CPU=cost,source_offsets=list(range(table+index,table+index+3))))
    drawings=[];reference={};ordinary_pages={0:set(),2:set(),3:set()}
    for character in [0,2,3]:
        for form in range(7):
            for frame in range(81):
                for facing in [0,64]:
                    state(character,form,frame,facing)
                    cost=run(0xce9f)
                    oam=bytes(bus.ram[0x200:0x218]);page=bus.ram[0x71b]
                    ordinary_pages[character].add(page)
                    key=form,frame,facing
                    if character==0:reference[key]=oam
                    else:assert oam==reference[key],('Distinct geometry requires explicit new records',character,key)
                    drawings.append(dict(character=character,form=form,frame=frame,facing=facing,
                        original_page=page,original_OAM=oam.hex(),CPU=cost))
    roots={character:list(raw[16+29*8192+0x1b72+character*7:16+29*8192+0x1b79+character*7])for character in [2,3]}
    assert roots=={2:[168,172,172,160,168,152,156],3:[144,148,148,136,144,128,132]}
    # These extra pages have genuine dedicated source readers, beyond roots:
    # frog walk, frog jump, small ground pound/spin and frog ground pound.
    extras={}
    for character in [2,3]:
        tables=[0x1a5f,0x1a63,0x1af8,0x1afc,0x1b38]
        extras[character]=[raw[16+29*8192+t+character]for t in tables]
    assert extras=={2:[234,190,214,166,218],3:[235,191,215,167,219]}
    O.mkdir(parents=True)
    assets=[]
    for character,name in [(2,'toad'),(3,'peach')]:
        # Keep each form block in the current host's root order, followed by
        # the five explicitly read special pages. No recoloring or redrawing.
        pages=[p for root in [roots[character][3],roots[character][5],roots[character][6],
                             roots[character][0],roots[character][1]]for p in range(root,root+4)]
        pages+=extras[character]
        assert len(pages)==len(set(pages))==25
        assert ordinary_pages[character].issubset(set(pages))
        data=b''.join(original_chr[p*1024:(p+1)*1024]for p in pages)
        target=O/(name+'-all-original-body-pages.chr');target.write_bytes(data)
        assets.append(dict(character=character,name=name,pages=pages,bytes=len(data),
            path=str(target),sha256=sha(target),original_offsets=[16+524288+p*1024 for p in pages]))
    save(O/'palette-consumers.json',palettes)
    save(O/'draw-consumers.json',drawings)
    # Retain exact instruction excerpts with their original file offsets.
    # These are discovery references, not assembled or joined host routines.
    dis=Disassembler(cpu);excerpts=[]
    ranges=[(29,'C',0xda1f,0xdab0),(29,'C',0xdac3,0xdb8f),
        (30,'A',0xb9f3,0xba1a),(30,'A',0xbac0,0xbb1c),(30,'A',0xbb50,0xbb5f),
        (32,'A',0xa003,0xa029),(32,'A',0xa040,0xa073),(38,'A',0xac82,0xacc9)]
    lines=[]
    for bank,window,lo,hi in ranges:
        bus.reg[6 if window=='C' else 7]=bank;bus.remap();pc=lo
        lines.append(f'; Original bank{bank:02X}, {window}-view {lo:04X}..{hi:04X}')
        while pc<hi:
            n,asm=dis.instruction_at(pc)
            data=bytes(bus[pc:pc+n]);offset=16+bank*8192+pc%8192
            assert data==raw[offset:offset+n]
            excerpts.append(dict(bank=bank,pc=pc,source_offset=offset,bytes=data.hex(),instruction=asm))
            lines.append(f'; {pc:04X} / file{offset:06X}: {data.hex(" "):9} {asm}')
            pc+=n
    (O/'original-instruction-reference.s').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    save(O/'original-instructions.json',excerpts)
    # Source-derived sprite contact sheets. Palette RGB values are display
    # approximations; original numeric NES color roles above are authoritative.
    rgb={0x0f:(0,0,0),0x07:(90,49,0),0x11:(0,101,210),0x16:(180,0,30),
         0x17:(135,55,0),0x25:(232,65,202),0x27:(230,155,70),0x2a:(70,190,65),
         0x30:(255,255,255),0x36:(255,186,210)}
    atlas=Image.new('RGB',(7*80,2*112),(30,37,56));draw=ImageDraw.Draw(atlas)
    stands=[0x3e,0x0e,0x0e,2,0,2,0x0e]
    for row,character in enumerate([2,3]):
        for form,frame in enumerate(stands):
            record=next(q for q in drawings if q['character']==character and q['form']==form and q['frame']==frame and q['facing']==0)
            colors=next(q['visible_colors']for q in palettes if q['character']==character and q['player']==0 and q['form']==form)
            oam=bytes.fromhex(record['original_OAM']);page=record['original_page']
            draw.text((form*80+3,row*112+3),f'{"Toad"if character==2 else"Peach"} {form}',fill='white')
            for at in range(0,24,4):
                y,tile,attr,x=oam[at:at+4]
                if y>=240:continue
                for yy in range(16):
                    ty=15-yy if attr&128 else yy
                    base=page*1024+(tile&62)*16+(ty//8)*16+ty%8
                    lo,hi=original_chr[base],original_chr[base+8]
                    for xx in range(8):
                        bit=xx if attr&64 else 7-xx
                        value=(lo>>bit&1)|((hi>>bit&1)<<1)
                        if value:
                            color=rgb[colors[value-1]]
                            ox=form*80+12+(x-64)*2;oy=row*112+23+(y-160)*2
                            draw.rectangle((ox+xx*2,oy+yy*2,ox+xx*2+1,oy+yy*2+1),fill=color)
    atlas.save(O/'source-forms.png')
    files=[p for p in O.iterdir()if p.is_file()]
    d=dict(status='ORIGINAL_SMB3PLUS_CHARACTER_SOURCE_RECOVERED_NOT_HOST_ADMISSION',source=True,
        native_host=False,installed=False,credit='Infidelity',donor_sha256=EXPECTED,
        original_character_state=dict(player1='0119',player2='011E',values=dict(Toad=2,Peach=3)),
        native_donor_selection=native,draw_cases=len(drawings),unchanged_geometry_pairs=2268,
        palette_cases=len(palettes),assets=assets,CHR_pages_required=50,
        roots=roots,extra_pages=extras,
        limits=['No playable-host change, readiness, native host physics or1-1/every-powerup qualification.',
            'Ordinary draw CPU cases control special state; explicit special-page readers are retained separately.',
            'Source excerpts still require coherent translation and native movement/combat/lifecycle joining.'],
        bindings={str(p):sha(p)for p in [Path(__file__),DONOR,
            R/'tools/audit/discover_smb3plus_chr_routes_1030_v1.py',
            R/'tools/audit/benj_mario_donor_trace_1030_v1.py',*files]})
    save(O/'source-proof.json',d)
    print(json.dumps(dict(source=True,installed=False,draw_cases=len(drawings),geometry_pairs=2268,
        palette_cases=len(palettes),body_CHR_pages=50,proof_sha256=sha(O/'source-proof.json'))))


if __name__=='__main__':main()
