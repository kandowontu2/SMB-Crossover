"""Sparse Rogue art/render source controls, with actual compiled host draw loop.

No live game, NMI/PPU emulator or native/render deadline qualification. Executes
original sprite/animation/palette instructions and the real host OAM loop.
"""
from pathlib import Path
import argparse,itertools,json,re,subprocess
from py65.devices.mpu6502 import MPU
import prepare_rogue_dawn_art_v1 as art
import rogue_dawn_map_v1 as ref
ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT/'build/roster-expansion-first-link-v2'
RAM=['SmPosePtr','SmChrBank','SmTemp','CurrentBankC','CurrentCHRBank','X5ChrMode',
     'ReloadCHRBank','X5WideChrActive','ObjectMetasprite','R0','R1','R3','R4','R5','R6','R7',
     'MetaspriteRenderLoop','CurrentOAMOffset','GuestOamRotationActive','RgOamRotation']

def symbols(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.match(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if m:out[m[2]]=int(m[1],16)
    return out

def build(folder,base):
    folder.mkdir(parents=True,exist_ok=True);s=symbols(HOST.with_suffix('.lbl'))
    mmc=(ROOT/'src/mmc5.s').read_text()
    macros='\n'.join(re.search(r'\.macro '+n+r'\b[\s\S]*?\.endmacro',mmc)[0] for n in ['BankPRGC','_BANK_INNER'])
    db=HOST.with_suffix('.dbg').read_text();match=re.search(r'name="METASPRITE_SAMUS_BODY"[^\n]*val=0x([0-9A-Fa-f]+)',db)
    assert match
    pre='\n'.join(f'{n}=${s[n]:04x}' for n in RAM)+'\n'
    pre+=f'METASPRITE_SAMUS_BODY=${int(match[1],16):02x}\nRD_FIRST_CHR={base}\n'
    pre+='ENABLE_CROSSOVER=1\nMMC5_PRG_ROM=$80\nMMC5_PRG_BANK_C=$5116\n'+macros+'\n'
    wrapper=folder/'render.s';wrapper.write_text(pre+'.include "rogue_dawn_art.inc"\n.include "rogue_dawn.s"\n.include "rogue_dawn_weapons.s"\n.include "rogue_dawn_render.s"\n')
    cfg=folder/'render.cfg';cfg.write_text('MEMORY { K:start=$B000,size=$1000,bank=124,file=%O; A:start=$D300,size=$D00,bank=94,file="'+str((folder/'art.bin').resolve()).replace('\\','/')+'"; }\nSEGMENTS { ROGUE_DAWN_CORE:load=K,type=ro; ROGUE_DAWN_ART:load=A,type=ro; }\n')
    cc=ROOT/'tools/Windows/cc65/bin'
    subprocess.run([str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(wrapper),'-o',str(folder/'render.o')],check=True)
    subprocess.run([str(cc/'ld65.exe'),'-C',str(cfg),'-o',str(folder/'render.bin'),'-Ln',str(folder/'render.lbl'),
                    '--dbgfile',str(folder/'render.dbg'),str(folder/'render.o')],check=True)
    code=(folder/'render.bin').read_bytes();data=(folder/'art.bin').read_bytes();s.update(symbols(folder/'render.lbl'))
    assert code[:1942]==(ROOT/'build/rogue-dawn-weapons-v1/weapons.bin').read_bytes()
    return code,data,s

def memory(code,data):
    m=art.Memory(bytes((i*7+11)&255 for i in range(65536)))
    m[0xb000:0xb000+len(code)]=code;m[0xd300:0xd300+len(data)]=data
    m[0x5c7d]=0 # Source69B3 default costume is the selected rendering domain.
    return m

def image(m,s,chrdata,base,weapon=False):
    """Execute actual host MetaspriteRenderLoop at real PC/physicalA4."""
    rom=HOST.with_suffix('.nes').read_bytes()
    m[0xa000:0xc000]=rom[16+4*8192:16+5*8192]
    m[s['CurrentOAMOffset']]=0;m[s['GuestOamRotationActive']]=0;m[s['RgOamRotation']]=0
    m[s['R3']]=0;m[s['R4']]=128 if weapon else 120;m[s['R5']]=0;m[s['R6']]=128 if weapon else 112;m[s['R7']]=1
    if not weapon:
        m[s['R0']]=m[s['SmPosePtr']];m[s['R1']]=m[s['SmPosePtr']+1]
    c=art.call(m,s['MetaspriteRenderLoop'])
    parts=[list(m[i:i+4])for i in range(0x200,0x200+m[s['CurrentOAMOffset']],4)]
    pixels={}
    for y,t,attr,x in reversed(parts):
        page=(7+(t//64-2)) if weapon else (m[s['SmChrBank']]-(base&255))
        pair=(t&63)//2;start=page*1024+pair*32
        for yy in range(16):
            for xx in range(8):
                sy=15-yy if attr&128 else yy;sx=7-xx if attr&64 else xx
                at=start+(sy//8)*16+sy%8
                v=((chrdata[at]>>(7-sx))&1)|(((chrdata[at+8]>>(7-sx))&1)<<1)
                if v:pixels[x-128+xx,y+1-128+yy]=(v,attr&0x23)
    return pixels,c.processorCycles,parts

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-art-v1')
    ap.add_argument('--first-chr',type=int,default=680);args=ap.parse_args()
    proof=dict(passed=False,native_run=False,host_integration=False)
    try:
        raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
        extraction=json.loads((args.output/'extraction.json').read_text())
        code,data,s=build(args.output,args.first_chr);chrdata=(ROOT/'chr/characters/rogue-dawn.chr').read_bytes()
        assert len(data)<=3328 and len(code)<=4096
        assert raw[16+62*8192+0x8a:16+62*8192+0x92]==bytes.fromhex('a9908d002085ffa9')
        mappings=[]
        for alt in [0,1]:
            q=art.Memory(ref.cpu_image(raw,lower_bank=2));q[0x23]=1;q[0x69b3]=alt
            art.call(q,0xc606);reg=0;writes={}
            for at,v in q.stores:
                if at==0x8000:reg=v&7
                elif at==0x8001:writes[reg]=v
            assert (writes[0]&254,writes[1]&254)==(8+2*alt,10+2*alt)
            mappings.append(dict(alt=alt,actual_MMC3_registers=writes))
        cases=[];costs={};samples=[]
        for fact in extraction['records']:
            m=memory(code,data);frame=fact['frame'];weapon=fact['kind']=='weapon'
            if weapon:
                m[0x5c2f]=0xd0;m[0x5c43]=frame;m[0x5c3c]=fact['color']
            else:m[0x5c03]=frame;m[0x5c2c]=fact['face']
            before=bytes(m)
            c=art.call(m,s['RdRenderWeapon'if weapon else'RdRenderPlayer'])
            assert m[s['CurrentBankC']]==0xde and m[0x5116]==0xde
            allowed={s['CurrentBankC'],0x5116,s['R0'],s['R1']}
            allowed|={0x5c41,0x5c42}if weapon else {0x5c01,0x5c02,s['SmPosePtr'],s['SmPosePtr']+1,s['SmChrBank'],s['ObjectMetasprite']}
            assert all(at in allowed or 0x100<=at<0x200 for at in m.writes)
            assert all(before[i]==m[i] for i in range(65536)if i not in allowed and not 0x100<=i<0x200)
            expected=art.source_pixels(raw,fact['source_OAM'])
            actual,drawcycles,parts=image(m,s,chrdata,args.first_chr,weapon)
            assert actual==expected,('actual host full OAM pixel/attribute mismatch',fact)
            if (fact['kind'],frame,fact['choice'])in [('body',8,0),('body',4,1),('body',27,0),('body',43,0),
                                                      ('weapon',40,0),('weapon',75,1),('weapon',78,0),('weapon',77,0)]:
                samples.append((fact,expected,actual))
            cases.append(dict(kind=fact['kind'],frame=frame,face=fact['face'],color=fact['color'],opaque=len(actual),parts=len(parts),
                              selector_cycles=c.processorCycles,host_draw_cycles=drawcycles))
        common=0
        for bank in [2,4,6,8,10]:
            for fact in extraction['records']:
                parts,_,_,_=art.native_render(raw,fact['frame'],fact['face'],fact['kind']=='weapon',fact['color'],bank)
                assert parts==fact['source_OAM'],('area source pose differs',bank,fact)
                common+=1
        invalid=0
        for frame in range(256):
            for face in [0,1]:
                m=memory(code,data);m[0x5c03]=frame;m[0x5c2c]=face
                c=art.call(m,s['RdRenderPlayer'])
                assert bool(c.p&1)==(frame in art.BODY)
                assert m[s['ObjectMetasprite']]==(0xe9 if frame in art.BODY else 0)
                invalid+=1
        for slot in range(256):
            m=memory(code,data);m[0x5b73+slot]=40;m[0x5c2f]=slot;m[0x5c3c]=0
            before=bytes(m);c=art.call(m,s['RdRenderWeapon'])
            assert bool(c.p&1)==(slot in [0xd0,0xe0,0xf0])
            if slot not in [0xd0,0xe0,0xf0]:assert bytes(m[0x5c00:0x5c80])==before[0x5c00:0x5c80]
            invalid+=1
        for alt in range(1,256):
            for weapon in [False,True]:
                m=memory(code,data);m[0x5c7d]=alt;m[0x5c03]=8;m[0x5c2f]=0xd0;m[0x5c43]=40;m[0x5c3c]=0
                before=bytes(m[0x5c00:0x5c80]);c=art.call(m,s['RdRenderWeapon'if weapon else'RdRenderPlayer'])
                assert not c.p&1 and bytes(m[0x5c00:0x5c80])==before
                invalid+=1
        for color in range(256):
            m=memory(code,data);m[0x5c2f]=0xd0;m[0x5c43]=40;m[0x5c3c]=color
            c=art.call(m,s['RdRenderWeapon']);assert bool(c.p&1)==(color in [0,129]);invalid+=1
        animation=0;animcost=[]
        seqs=[(0,0),(4,4),(7,7),(9,9),(11,12),(14,14),(22,22),(26,22),(29,29),(32,32),(38,39),(39,39),(50,50),(52,52),(55,55),(59,59),(61,61),(63,63)]
        for index,reset in seqs:
            for delay,a,p in itertools.product([0,1,2,255],[1,3,4,5],[0x30,0x31,0x70,0x71]):
                q=art.Memory(ref.cpu_image(raw,lower_bank=2));m=memory(code,data)
                q[0x4b]=0;q[0x0303]=0x99;q[0x0304]=delay;q[0x0305]=reset;q[0x0306]=index
                m[0x5c03]=0x99;m[0x5c04]=delay;m[0x5c05]=reset;m[0x5c06]=index
                c=art.call(q,0xdc8f,a=a,p=p);d=art.call(m,s['RdAdvancePlayerFrame'],a=a,p=p)
                assert q[0x0303:0x0307]==m[0x5c03:0x5c07]
                assert(c.a,c.x,c.y,c.p,c.sp)==(d.a,d.x,d.y,d.p,d.sp)
                assert all(k in [0x5c03,0x5c04,0x5c06]or 0x100<=k<0x200 for k in m.writes)
                animation+=1;animcost.append([c.processorCycles,d.processorCycles])
        palette=0
        for row in extraction['palettes']['rows']:
            m=memory(code,data);m[0x5fb0]=row['gear_suit'];m[0x5c27]=row['missile'];m[0x5c7d]=row['alt']
            art.call(m,s['RdRenderPalettePointer']);ptr=m[s['R0']]|m[s['R1']]<<8
            assert list(m[ptr:ptr+16])==row['sprite_colors'];palette+=1
            assert all(k in [s['CurrentBankC'],0x5116,s['SmTemp'],s['R0'],s['R1']]or 0x100<=k<0x200 for k in m.writes)
        publication=0
        for page,priorlow,priorhigh,dirty in itertools.product(range(7),[0,255],[0,0x82],[0,1]):
            m=memory(code,data);m[s['SmChrBank']]=(args.first_chr+page)&255
            for i in range(4):m[s['CurrentCHRBank']+i]=priorlow;m[s['X5ChrMode']+i]=priorhigh
            m[s['ReloadCHRBank']]=dirty
            c=art.call(m,s['RdRenderPublishChr'])
            expected=[(args.first_chr+page)&255,priorlow,(args.first_chr+7)&255,(args.first_chr+8)&255]
            assert list(m[s['CurrentCHRBank']:s['CurrentCHRBank']+4])==expected
            assert m[s['X5ChrMode']+1]==priorhigh and m[s['X5WideChrActive']]==1
            assert all(k in [s['CurrentCHRBank']+i for i in[0,2,3]]+[s['X5ChrMode']+i for i in[0,2,3]]+[s['X5WideChrActive'],s['ReloadCHRBank']]or 0x100<=k<0x200 for k in m.writes)
            publication+=1
        for page,dirty in itertools.product(range(7),[0,1]):
            m=memory(code,data);m[s['SmChrBank']]=(args.first_chr+page)&255
            for window,p in [(0,page),(2,7),(3,8)]:
                m[s['CurrentCHRBank']+window]=(args.first_chr+p)&255;m[s['X5ChrMode']+window]=0x80|(args.first_chr>>8)
            m[s['ReloadCHRBank']]=dirty;before=bytes(m)
            art.call(m,s['RdRenderPublishChr'])
            assert m[s['ReloadCHRBank']]==dirty
            assert all(k==s['X5WideChrActive']or 0x100<=k<0x200 for k in m.writes)
            publication+=1
        from PIL import Image,ImageDraw
        nespath=ROOT/'tools/Windows/NEXXT 3.0/defaults/nes.pal';nes=nespath.read_bytes()
        assert len(samples)==8 and len(nes)==192
        sheet=Image.new('RGB',(600,720),(20,25,31));draw=ImageDraw.Draw(sheet)
        colors=extraction['palettes']['rows'][0]['sprite_colors']
        for i,(fact,original,repacked)in enumerate(samples):
            gx=(i%2)*300;gy=(i//2)*180
            draw.text((gx+5,gy+4),fact['meaning']+' /'+str(fact['choice']),fill='white')
            for j,pixels in enumerate([original,repacked]):
                pane=Image.new('RGB',(48,48),(42,49,56))
                for (x,y),(v,attr)in pixels.items():
                    assert -24<=x<24 and -24<=y<24
                    c=colors[(attr&3)*4+v];pane.putpixel((x+24,y+24),tuple(nes[c*3:c*3+3]))
                px=gx+j*148+2;py=gy+30
                sheet.paste(pane.resize((144,144),Image.Resampling.NEAREST),(px,py))
                draw.rectangle((px-1,py-1,px+144,py+144),outline=(240,210,40))
                draw.text((px,gy+18),'original CPU'if j==0 else'host CPU',fill=(215,220,230))
        sheet.save(args.output/'source-host-eight.png')
        proof.update(passed=True,scope=__doc__,original_ROM=ref.binding(ref.ROM),
                     compiled_host=[ref.binding(HOST.with_suffix(e))for e in ['.nes','.dbg','.lbl']],
                     full_source_to_actual_host_pixel_cases=cases,original_five_area_OAM_cells=common,
                     five_area_palettes=[art.palettes(raw,b)for b in[2,4,6,8,10]],
                     admission_cells=invalid,animation_cells=animation,
                     animation_source_port_cycle_ranges=[min(x[0]for x in animcost),max(x[0]for x in animcost),min(x[1]for x in animcost),max(x[1]for x in animcost)],
                     palette_rows=palette,CHR_publication_cells=publication,actual_original_MMC3_mapping=mappings,
                     code_bytes=len(code),render_bytes=len(code)-1942,CORE_end=f'{0xb000+len(code):04X}',
                     ART_bytes=len(data),ART_end=f'{0xd300+len(data):04X}',first_CHR=args.first_chr,
                     CHR_reserved_bytes=16384,CHR_used_pages=9,body_window=0,weapon_windows=[2,3],window1_unchanged=True,
                     frozen_weapons_prefix_exact=True,
                     source_host_preview=ref.binding(args.output/'source-host-eight.png'),illustrative_NES_RGB_palette=ref.binding(nespath),
                     inputs=[ref.binding(ROOT/p)for p in ['src/rogue_dawn_render.s','src/rogue_dawn_art.inc','chr/characters/rogue-dawn.chr',
                            'tools/prepare_rogue_dawn_art_v1.py','tools/rogue_dawn_render_controls_v1.py','src/mmc5.s',
                            'build/rogue-dawn-art-v1/extraction.json','build/rogue-dawn-weapons-v1/handoff.json','build/rogue-dawn-chr-reservation-v1.json']],
                     limitations=['No native NMI/IRQ/PPU timing, host gameplay adapter or collision integration',
                                  'Body source center=(host top-leftX+8,Y+16); weapons use actual source center. Gameplay import/export remains explicit integration work',
                                  'Palette pointer is a source role description, not permission to replace shared enemy palettes',
                                  'Dynamic death explosion, alternate pattern costume69B3 and hurt/Screw flash overrides not selected',
                                  'Host8x16 regrouping preserves full visible pixel/attribute mask, not original8x8 transparent OAM count or clipping at every screen edge'])
    except Exception as exc:
        proof['error']=repr(exc);raise
    finally:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['passed','code_bytes','render_bytes','ART_bytes','admission_cells','animation_cells','palette_rows','CHR_publication_cells']}))

if __name__=='__main__':main()
