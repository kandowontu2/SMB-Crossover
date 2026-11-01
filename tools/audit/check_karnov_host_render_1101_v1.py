"""Execute original and actual linked body/shot rendering and native palette NMI."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address
from recover_karnov_art_1101_v1 import pixels
O=R/'build/karnov-host-resource-base-1101-v1';A=R/'build/karnov-original-art-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

class PaletteBus(OverlayMemory):
    def __setitem__(self,k,v):
        if k==0x2007 and self.ppu_addr>=0x3f00:
            p=self.ppu_addr&31
            if p in [16,20,24,28]:p-=16
            self.native_palette[p]=v&63;self.palette_writes.append((self.ppu_addr,p,v&63))
        super().__setitem__(k,v)

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text());art=json.loads((O/'render-art.json').read_text());body=json.loads((A/'art-controls.json').read_text())
        assert stage['passed']and stage['render']and art['passed']
        for d in [stage,art]:
            for p,h in d['bindings'].items():assert sha(p)==h,p
        b=H.C.qualified(O/'candidate.nes');chrbase=1048592;nativebody=(A/'body.chr').read_bytes();mapping=dict(zip(art['source_tiles'],art['host_tiles']))
        def service(m,row,**kw):
            c=H.start(m,'KrServiceVeneers',**kw);pc=address(b,'KrServiceVeneers')+3*row
            m[address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
            trace=[]
            def hook(mem,c,step):
                if row==15 and c.pc in [address(b,n)for n in ['KrDispatch','KrCheckCode','KrDispatchNo','KrConstruct','KrConstructNo','KrCopyArt']]:trace.append((hex(c.pc),c.a,c.x,c.y,c.p,mem.rawtags[:],mem[address(b,'FarcallJmpTarget_SMC')+1:address(b,'FarcallJmpTarget_SMC')+3]))
            c=H.finish(m,c,hook)[0]
            if row==15 and not c.p&1:q['construction_trace']=trace
            return c
        seed=L.make(b);H.put(seed,SelectedCharacter=7,FmAlts=1,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=112,Player_Y_HighPos=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,CurrentOAMOffset=0)
        c,_=L.call(seed,'KrLoad');assert c.p&1;c=service(seed,15)
        assert c.p&1,('construct',c.a,c.x,c.y,c.p,H.get(seed,'SelectedCharacter'),H.get(seed,'FmAlts'),H.get(seed,'DisableScreenFlag'),H.get(seed,'Mirror_PPUMASK'),H.get(seed,'NmiDisable'),H.get(seed,'FamilyMainCommit'),seed.ram[2][address(b,'KrReady')&8191],seed.ram[2][0x1fe0:0x1ff0].hex(),seed.ram[3][0x1fe0:0x1ff0].hex())
        blob=(O/'kr-pose-meta.bin').read_bytes();assert bytes(seed.ram[2][0x1000:0x1000+len(blob)])==blob
        image=bytes(seed.ram[3]);metadata=bytes(seed.ram[2][0x1000:0x1800]);digest=hashlib.sha256()
        published=L.fork(seed);L.call(published,'X5PublishChr');world_windows=published.chr_latches[4:8]
        def reset(m):
            H.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,Player_SprAttrib=0)
            m[0x200:0x300]=[248,0,0,0]*64
        def cells(m):return[tuple(m[0x200+i:0x204+i])for i in range(0,H.get(m,'CurrentOAMOffset'),4)if m[0x200+i]<240]
        def rendered_pixels(m,records):
            out={}
            for y,t,a,x in records:
                ppu=(t&1)*4096+(t&254)*16;physical=m.chr_latches[ppu//1024]
                pat=b['raw'][chrbase+physical*1024+(ppu&1023):chrbase+physical*1024+(ppu&1023)+32]
                for(dx,dy),v in pixels(pat,a).items():out.setdefault((x+dx,y+dy),v)
            return out
        count=0;render_cycles=[];preview={}
        for pose in body['poses']:
            m=L.fork(seed);reset(m)
            for at,value in {0x62:pose['state']|pose['facing'],0x68:pose['hurt'],0xe8:pose['phase']}.items():m.ram[2][at]=value
            before=[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Pos_ForScroll']]
            draw_cpu=service(m,2);render_cycles.append(draw_cpu.processorCycles);L.call(m,'X5PublishChr')
            packet=pose['packet'];expected=[];expected_pixels={}
            for i in range(1,len(packet),4):
                tile,attr,dy,dx=packet[i:i+4];dy=dy-256 if dy>=128 else dy;dx=dx-256 if dx>=128 else dx
                expected.append((144+dy,tile,attr,128+dx));at=pose['packed_page']*1024+tile*16
                for(px,py),v in pixels(nativebody[at:at+32],attr).items():expected_pixels.setdefault((128+dx+px,144+dy+py),v)
            actual=cells(m);assert actual==expected,('body OAM order',pose['state'],pose['facing'],pose['hurt'],pose['phase'],actual,expected)
            assert rendered_pixels(m,actual)==expected_pixels,('actual physical body pixels',pose)
            if pose['state']in [0,1,5,6,8,9,15,25]and not pose['facing']and not pose['hurt']and not pose['phase']:preview[pose['state']]=expected_pixels
            assert m.chr_latches[0]==407+pose['packed_page']and m.chr_latches[3]==410,('CHR publish',pose['state'],pose['hurt'],pose['phase'],m.chr_latches[:8],pose['packed_page'])
            assert m.chr_latches[4:8]==world_windows
            assert[H.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_Pos_ForScroll']]==before
            assert bytes(m.ram[3])==image and bytes(m.ram[2][0x1000:0x1800])==metadata
            digest.update(bytes(v for cell in actual for v in cell));count+=1
        # Match every original shot flag/animation mode at its actual viewport
        # coordinate. Blank body state29 keeps the shot OAM independently exact.
        shots=0
        for mode,flag,clock in itertools.product([0,1,2,8],[0,0x84,0xc4,0x94,0xa4,0xb4],range(32)):
            m=L.fork(seed);reset(m);m.ram[2][0x62]=29;m.ram[2][0x65]=mode;m.ram[2][0xe8]=clock
            for n in range(9):m.ram[2][0x6e+3*n]=flag;m.ram[2][0x6f+3*n]=40+20*n;m.ram[2][0x70+3*n]=120+16*(n%3)
            draw_cpu=service(m,2);render_cycles.append(draw_cpu.processorCycles);L.call(m,'X5PublishChr');expected=[]
            for n in range(1 if mode==8 else 9):
                if not flag&128:continue
                source=0x61+((clock&12)>>1)if mode==8 else 0x69 if flag&48 else 0x77 if clock&16 else 0x75
                expected.append((120+16*(n%3),mapping[source],0,40+20*n))
            actual=cells(m);assert actual==expected,('shot OAM',mode,flag,clock,actual,expected)
            assert m.chr_latches[3]==410
            digest.update(bytes(v for cell in actual for v in cell));shots+=1
        # Native publisher keeps all world pattern windows4..7 intact.
        m=L.fork(seed);L.call(m,'X5PublishChr');world=m.chr_latches[4:8];service(m,1);L.call(m,'X5PublishChr');assert m.chr_latches[4:8]==world
        capacity_cases=0
        for prefix,rotation in itertools.product([0,196,220,236,248,252],[0,4,128,252]):
            m=L.fork(seed);reset(m);H.put(m,CurrentOAMOffset=prefix,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation)
            m.ram[2][0x65]=2
            for n in range(9):m.ram[2][0x6e+3*n]=0x84;m.ram[2][0x6f+3*n]=40+20*n;m.ram[2][0x70+3*n]=120
            before=bytes(m[0x200:0x300]);service(m,2);cursor=prefix;allowed=set()
            for size in [20,*([4]*9)]:
                if cursor+size>255:continue
                for i in range(size):allowed.add((cursor+rotation+i)&255)
                cursor+=size
            assert H.get(m,'CurrentOAMOffset')==cursor
            assert all(m[0x200+i]==before[i]for i in range(256)if i not in allowed),('OAM capacity/rotation escape',prefix,rotation)
            capacity_cases+=1
        camera_cases=0
        for oldcam,newcam,shotx in [(0,12,40),(0,12,5),(255,256,50),(500,505,90)]:
            m=L.fork(seed);reset(m);m.ram[2][0x62]=29;m.ram[2][0x6e]=0x84;m.ram[2][0x6f]=shotx;m.ram[2][0x70]=120
            for name,value in [('KrCameraLo',oldcam&255),('KrCameraHi',oldcam>>8)]:m.ram[2][address(b,name)&8191]=value
            H.put(m,ScreenLeft_X_Pos=newcam&255,ScreenLeft_PageLoc=newcam>>8);service(m,2)
            actual=cells(m);x=shotx-(newcam-oldcam)
            assert actual==([(120,mapping[0x75],0,x)]if x>=0 else[]),('post-move camera render',oldcam,newcam,shotx,actual);camera_cases+=1
        # Palette queue writes only the three opaque sprite colors. Execute the
        # real normal NMI writer, modeling the NES universal-color mirroring.
        palette_cases=0
        for blue,offset in itertools.product([0,128],[0,12,66,71,72,80]):
            m=L.fork(seed);m.ram[2][0x68]=blue;H.put(m,VRAM_Buffer1_Offset=offset)
            at=address(b,'VRAM_Buffer1');m[at:at+84]=[0x55]*84;before=bytes(m[at:at+84]);service(m,26)
            if offset>=72:assert bytes(m[at:at+84])==before and H.get(m,'VRAM_Buffer1_Offset')==offset
            else:
                colors=[16,28,15]if blue else[40,22,15]
                assert bytes(m[at+offset:at+offset+7])==bytes([63,17,3,*colors,0])
                assert bytes(m[at:at+offset])==before[:offset]and H.get(m,'VRAM_Buffer1_Offset')==offset+6
            palette_cases+=1
        native_palette_cases=0
        for blue in [0,128]:
            m=L.fork(seed);m.ram[2][0x68]=blue;H.put(m,VRAM_Buffer1_Offset=0,NmiDisable=0)
            service(m,26);m.__class__=PaletteBus;m.native_palette=bytearray([0x21]*32);m.palette_writes=[]
            c=H.start(m,'KrCheckCode');H.finish(m,c);V.interrupt(m,c,'NMI')
            assert m.native_palette[0]==0x21 and m.native_palette[17:20]==bytes([16,28,15]if blue else[40,22,15]),('native palette',blue,m.palette_writes)
            assert not any(p==0 for _,p,_ in m.palette_writes)
            native_palette_cases+=1
        # One bounded technical preview from the actual CPU-rendered pattern
        # pixels, not a native gameplay capture or replacement character art.
        from PIL import Image,ImageDraw
        pal=(R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes();rgb=lambda i:tuple(pal[i*3:i*3+3])
        img=Image.new('RGB',(640,148),'#131c29');draw=ImageDraw.Draw(img);draw.text((6,2),'KARNOV - CPU SPRITE PREVIEW',fill='white')
        for column,(state,pix)in enumerate(sorted(preview.items())):
            draw.rectangle((column*80,18,column*80+79,117),fill=rgb(0x22));draw.text((column*80+3,20),str(state),fill='black')
            left=min(x for x,y in pix);right=max(x for x,y in pix);origin=column*80+(80-2*(right-left+1))//2
            for(x,y),v in pix.items():
                xx=origin+(x-left)*2;yy=110+(y-144)*2
                draw.rectangle((xx,yy,xx+1,yy+1),fill=rgb([0,40,22,15][v]))
        for column,tile in enumerate(art['host_tiles']):
            at=3*1024+(tile-192)*16;pat=(O/'kr-body.chr').read_bytes()[at:at+32]
            for(x,y),v in pixels(pat,0).items():img.putpixel((8+column*32+x,126+y),rgb([0,40,22,15][v]))
        img.save(O/'render-preview.png')
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],body_cases=count,shot_cases=shots,capacity_rotation_cases=capacity_cases,post_movement_camera_cases=camera_cases,palette_queue_cases=palette_cases,actual_native_palette_NMI=native_palette_cases,draw_cycle_range=[min(render_cycles),max(render_cycles)],trace_sha256=digest.hexdigest(),original_body_OAM_order=True,actual_physical_pattern_pixels=True,all_world_sprite_CHR_windows_preserved=True,metadata_survives_native_farcalls=True,universal_background_color_unchanged=True,scope='Actual linked JMP-row graphics/draw/color services, ordinary native renderer and physical CHR publisher; all256 original body contexts and768 source shot contexts. Native NMI palette writer executes with NES palette mirroring modeled. No raster capture, controller traversal, combat hit/upgrade progression or menu admission claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),O/'terrain-assembly.json',O/'render-art.json',O/'candidate.nes',O/'candidate.dbg',O/'kr-kernel.bin',A/'art-controls.json',A/'body.chr']}
    (O/'render-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
