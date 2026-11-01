"""Execute exact native OAM/CHR helpers with original Metal body/shot pixels."""
from pathlib import Path
import hashlib,itertools,json,random,sys,traceback
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import metal_storm_cpu_1101_v2 as M
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from PIL import Image,ImageDraw
import prepare_metal_storm_render_host_1101_v7 as P
OUT=P.OUT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    q=dict(passed=False,native=False,installed=False,admitted=False)
    try:
        stage=json.loads((OUT/'assembly.json').read_text());art=json.loads((OUT/'art.json').read_text());w=json.loads((OUT/'native-render-witness.json').read_text());lab=stage['labels']
        for path,h in stage['bindings'].items():assert sha(path)==h,path
        for path,h in art['bindings'].items():assert sha(path)==h,path
        raw=bytearray(w['raw_length'])
        for s in w['spans']:
            data=bytes.fromhex(s['hex']);assert len(data)==s['size']and hashlib.sha256(data).hexdigest()==s['sha256'];raw[s['offset']:s['offset']+len(data)]=data
        # Gate9000 is an unfunded fixture fragment in fixed testROM126.
        gate=(OUT/'gate.bin').read_bytes();raw[16+126*8192+0x1000:16+126*8192+0x1000+len(gate)]=gate
        body=(OUT/'body.chr').read_bytes();shots=(OUT/'shots.chr').read_bytes();raw[1048592+800*1024:1048592+805*1024]=body;raw[1048592+805*1024:1048592+806*1024]=shots
        b=dict(raw=raw,syms=w['syms'],segs=w['segs']);actor=(OUT/'actor.bin').read_bytes();renderer=(OUT/'render.bin').read_bytes();digest=hashlib.sha256();minimum=224;maxcycles=0;helperhits={};previews=[]
        def put(m,**kw):
            for n,v in kw.items():m[address(b,n)]=v
        def make():
            m=OverlayMemory(b);m.raw_page(1,3);m.raw_page(2,2);m.ram[3][:len(actor)]=actor;m.ram[2][0xd00:0xd00+len(renderer)]=renderer
            m.ram[3][0x1fe0:0x1ff0]=(OUT/'actor-cookie.bin').read_bytes();m.ram[2][0x1fe0:0x1ff0]=(OUT/'render-cookie.bin').read_bytes()
            put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,SsChrActive=0,InvHudActive=0,X5WideChrActive=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0,VRAM_Buffer1_Offset=0)
            m[0xc800]=167
            for i in range(8):m[3+i]=(29*i+17)&255
            for i in range(12):m[address(b,'CurrentCHRBank')+i]=20+i;m[address(b,'X5ChrMode')+i]=0
            m[0x200:0x300]=bytes([240,0,0,0])*64;m.writes.clear();m.ram_writes.clear();return m
        def run(m,pc,a=85,x=7,y=91,p=0x71,ports=(),stop=None,deny_c2=False):
            nonlocal minimum,maxcycles
            c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);trace=[];start=c.processorCycles
            for _ in range(100000):
                if c.pc==0x5fff:break
                minimum=min(minimum,c.sp)
                if deny_c2:assert not 0xcd00<=c.pc<0xdfe0,('C2 opcode before authentication',hex(c.pc))
                if c.pc==stop or c.pc in ports:c.pc=(c.stPopWord()+1)&65535;continue
                if isinstance(m,OverlayMemory):
                    for name in ['MetaspriteRenderLoop','X5SetPhysicalChr','X5PublishChr']:
                        if c.pc==address(b,name):helperhits[name]=helperhits.get(name,0)+1
                    if c.pc==lab['MsRBody']:trace.append('body')
                    if c.pc==lab['MsRShot']:trace.append(m[0xc829])
                assert m[c.pc]!=0,('BRK',hex(c.pc),m.rawtags);c.step()
            else:raise AssertionError(('CPU bound',hex(c.pc),m.rawtags))
            assert c.sp==224;maxcycles=max(maxcycles,c.processorCycles-start)
            return(c.a,c.x,c.y,c.p&0xcf),trace
        def invoke(m,name):
            abi=bytes(m[3:11]);smc=bytes(m[i]for i in[0x16a,0x16c,0x16d]);maps=m.rawtags[:];result,trace=run(m,lab[name]);assert result==(85,7,91,0x41),(name,result)
            assert bytes(m[3:11])==abi and bytes(m[i]for i in[0x16a,0x16c,0x16d])==smc and m.rawtags==maps,(name,'ABI/SMC/maps',bytes(m[3:11]),abi,m.rawtags,maps)
            return trace
        def publish(m):
            m[address(b,'SafecallA_SMC')+1]=85;target=address(b,'X5PublishChr');m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
            run(m,address(b,'FarCallCommon'),a=190)
            assert m.rawtags[1:3]==[3,2]and m.upper==0
        def pixelmap(cells,chrdata,world=(128,112)):
            pixels={}
            for cell in cells:
                attr=cell['attributes'];pattern=chrdata[cell['pattern_index']*32:cell['pattern_index']*32+32]
                for yy,xx in itertools.product(range(16),range(8)):
                    px=7-xx if attr&64 else xx;py=15-yy if attr&128 else yy;at=(py//8)*16+(py&7);v=((pattern[at]>>(7-px))&1)+2*((pattern[at+8]>>(7-px))&1)
                    x=world[0]+cell['dx']+xx;y=world[1]+cell['dy']+yy
                    if v and 0<=x<256 and 0<=y<240:pixels.setdefault((x,y),(attr&3,v))
            return pixels
        def drawn(m):
            cells=[]
            for off in range(0,m[address(b,'CurrentOAMOffset')],4):
                y,t,a,x=m[0x200+off:0x204+off];physical=m.chr_latches[4+((t&254)*16)//1024];start=1048592+physical*1024+((t&254)*16)%1024
                cells.append(dict(dx=x,dy=y+1,pattern_index=0,attributes=a,pattern=bytes(raw[start:start+32])))
            pixels={}
            for cell in cells:
                for key,value in pixelmap([cell],cell['pattern'],(0,0)).items():pixels.setdefault(key,value)
            return pixels,cells
        def setbody(m,r,world=(128,112),camera=0):
            for a,v in [(0x480,world[0]&255),(0x498,(world[0]>>8)&255),(0x4b0,world[1]%240),(0x4c8,(world[1]//240)&255),(0x510,128),(0x4e0,r['state']),(0x4f8,r['frame']),(0x540,r['facing']|r['gravity'])]:m[0xc000+a]=v
            put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
        bodycases=0
        for r in art['body_packets']:
            m=make();setbody(m,r);invoke(m,'MsRenderGate');publish(m);got,cells=drawn(m);want=pixelmap(r['cells'],body)
            assert got==want,('body pixels',r['state'],r['frame'],r['facing'],r['gravity'],len(got),len(want),list(set(got)^set(want))[:3])
            if r['state']==0 and r['frame']==0:previews.append((f"H{r['facing']//64} V{r['gravity']//128}",got))
            physical=bytes.fromhex(next(s['hex']for s in w['spans']if s['name']=='ChrPhysicalMap'))
            assert [m.chr_latches[i]for i in[0,1,2,3,7,8,9,10,11]]==[physical[i]for i in[20,21,22,23,27,28,29,30,31]]
            digest.update(repr(sorted(got.items())).encode());bodycases+=1
        q['body_original_pixel_contexts']=bodycases
        shotcases=0
        for r in art['shot_packets']:
            if r['type']==0x83 and r['phase']>2:continue # beyond original terminator, not a reachable impact phase
            m=make()
            for a,v in [(0x482,128),(0x49a,0),(0x4b2,112),(0x4ca,0),(0x512,128),(0x52a,r['type']),(0x542,r['flags']),(0x55a,0 if r['vertical']else 12),(0x632,r['phase']),(0x64a,0)]:m[0xc000+a]=v
            invoke(m,'MsRenderGate');publish(m);got,cells=drawn(m);want=pixelmap(r['cells'],shots)
            assert got==want,('shot pixels',r['type'],r['vertical'],r['flags'],r['phase'],len(got),len(want),list(set(got)^set(want))[:3])
            if r['flags']==0 and r['phase']==0 and ((r['type']in[128,131]and not r['vertical'])or r['type']==129):previews.append((f"SHOT {r['type']:02X}"+(' V'if r['vertical']else''),got))
            if r['retired']:assert m[0xc512]==0 and m[0xc49a]==128 and m[0xc6aa]==0
            digest.update(repr(sorted(got.items())).encode());shotcases+=1
        q['shot_original_pixel_contexts']=shotcases
        # Source/world camera displacement is integrated only here, once.
        cameracases=0
        for world,camera,yy in itertools.product([120,255,320,511],[80,180,300],[40,112,200]):
            m=make();r=art['body_packets'][0];setbody(m,r,(world,yy),camera);invoke(m,'MsRenderGate');publish(m);got,_=drawn(m)
            want=pixelmap(r['cells'],body,(world-camera,yy));assert got==want,('camera/clip',world,camera,yy,len(got),len(want));cameracases+=1
        q['camera_clipping_cases']=cameracases
        m=make();setbody(m,art['body_packets'][0]);m[0xc512]=128;m[0xc52a]=128;m[0xc482]=100;m[0xc4b2]=112;m[0xc660+2]=20
        for clock,order in[(0,['body',1,2,3]),(1,[3,2,1,'body'])]:
            m[0xc053]=clock;put(m,CurrentOAMOffset=0);assert invoke(m,'MsRenderGate')==order
        q['source_draw_parity_orders']=2
        # Capacity is the real native all-or-none packet rule, not donor raster equivalence.
        capacities=0
        for offset,rot in itertools.product([0,4,224,228,232,236,240,244,248,252],[0,1]):
            m=make();setbody(m,art['body_packets'][0]);put(m,CurrentOAMOffset=offset,GuestOamRotationActive=rot,RgOamRotation=76);invoke(m,'MsRenderGate')
            assert m[address(b,'CurrentOAMOffset')]in[offset,(offset+24)&255]
            assert all(0x200<=a<0x300 for a,v in m.writes if 0x200<=a<0x300);capacities+=1
        q['native_capacity_rotation_cases']=capacities
        for offset in[0,6,71,72,80]:
            m=make();put(m,VRAM_Buffer1_Offset=offset);before=bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+96]);invoke(m,'MsColorsGate')
            if offset<72:assert bytes(m[address(b,'VRAM_Buffer1')+offset:address(b,'VRAM_Buffer1')+offset+13])==bytes.fromhex('3f1103260f153f150321200100')
            else:assert bytes(m[address(b,'VRAM_Buffer1'):address(b,'VRAM_Buffer1')+96])==before
        q['palette_queue_cases']=5
        m=make();put(m,ObjectMetasprite=31,SmPosePtr=170);invoke(m,'MsGraphicsGate');assert m[address(b,'ObjectMetasprite')]==0
        negatives=0
        for page,offset in itertools.product([2,3],range(16)):
            m=make();m.ram[page][0x1fe0+offset]^=1;before=bytes(m.ram[2]);r,_=run(m,lab['MsRenderGate'],deny_c2=True);assert r==(85,7,91,0x40)and bytes(m.ram[2])==before;negatives+=1
        for n,v in[('SelectedCharacter',11),('OperMode',0),('GameEngineSubroutine',7)]:
            m=make();put(m,**{n:v});before=bytes(m.ram[2]);r,_=run(m,lab['MsRenderGate'],deny_c2=True);assert r==(85,7,91,0x40)and bytes(m.ram[2])==before;negatives+=1
        m=make();m[0xc800]=0;before=bytes(m.ram[2]);r,_=run(m,lab['MsRenderGate'],deny_c2=True);assert r==(85,7,91,0x40)and bytes(m.ram[2])==before;negatives+=1
        q['full_header_eligibility_rejections']=negatives
        # Exact original entity leaves; random fixtures are in-memory only.
        rng=random.Random(0x110107);life=0
        for pc,name in[(0x8e54,'MsLife_8E54'),(0x8eae,'MsLife_8EAE'),(0xeeae,'MsLife_EEAE')]:
            for case in range(256):
                original=M.machine();om=original.memory;om.regs[6:8]=[4,5];om.map();initial=bytes(rng.randrange(256)for _ in range(2048));om[:2048]=initial;nm=make();nm[0xc000:0xc800]=initial;x=1+case%3
                if pc==0xeeae:om[0x648+x]=nm[0xc648+x]=0
                def donor_run():
                    c=NesMPU(memory=om,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,x,91,0x71,224;c.stPushWord(0x5ffe)
                    for _ in range(1000):
                        if c.pc==0x5fff:break
                        c.step()
                    else:raise AssertionError(('donor life bound',hex(c.pc)))
                    return c.a,c.x,c.y,c.p&0xcf
                want=donor_run();got,_=run(nm,lab[name],x=x)
                assert got==want and all(nm[0xc000+i]==om[i]for i in range(2048)if not 0x100<=i<0x200),('life',hex(pc),case,got,want)
                life+=1
        q['original_lifecycle_differential_cases']=life
        # Compose native original constructor, real actor/contact/order, real
        # entityAI and native OAM. Scene/map/audio leaves remain explicit ports.
        fields=json.loads((P.V6/'assembly.json').read_text())['source_fields']
        raw[16+126*8192+0x15d8:16+126*8192+0x15dc]=bytes([0,208,3,3])
        raw[16+127*8192+0xf36+0x61]=1 # private solid semantic attribute fixture
        def terrain(om,nm):
            for row,col in itertools.product(range(15),range(20)):
                solid=row>=13;om[0x300+row*20+col]=248 if solid else 0
                if row>=2:nm[0x300+(col//16)*208+(row-2)*16+(col&15)]=0x61 if solid else 0
        oldports={0x8874,0x9ed7,0xff18,0xff39};newports={0x5000,0x5006,0x5009,0x5018}
        def omrun(om,pc,**kw):
            # Original untimed CPU uses the same bounded executor, but none of
            # its program bytes come from the native helper witness.
            return run(om,pc,**kw)
        def original_draw(om):
            sourcecamera=bytes(om[0x710:0x714])
            om.regs[6:8]=[12,13];om.map();table=om[0x800e]+256*om[0x800f];om[0x24]=table&255;om[0x25]=table>>8
            om[0x61]=0;om[0x710]=0;om[0x711]=0;om[0x713]=0;om[0x42]=252
            slots=([3,2,1,0]if om[0x53]&1 else[0,1,2,3])
            for slot in slots:
                if om[0x510+slot]&128:omrun(om,0xf282,x=slot,y=om[0x61])
            om[0x710:0x714]=sourcecamera # model actual native camera only for draw boundary
            om.regs[6:8]=[0,1];om.map()
        frames=duplicates=paused=shotsseen=visibilitydiffs=0;gravityset=set()
        for axis in ['walk','jump','reverse','shoot-right','shoot-up','shoot-down']:
            nm=make();nm[0xc000:0xc800]=bytes([90])*2048
            for name,v in dict(Player_X_Position=72,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0).items():nm[fields[name]]=v
            nm[0xc732]=255;nm[0xc733]=7;om=M.machine().memory;om.regs[6:8]=[0,1];om.map();terrain(om,nm)
            result,_=run(nm,lab['MsNativeConstruct']);assert result[3]&1
            om[:2048]=bytes(nm[0xc000:0xc800]);terrain(om,nm)
            for tick in range(96):
                pad=(1 if tick<48 else 2)if axis=='walk'else (0x81 if tick%48<20 else 1)if axis=='jump'else (0x88 if tick in[4,5]else 0x84 if tick in[48,49]else 0)if axis=='reverse'else 0x40 if axis=='shoot-right'else 0x48 if axis=='shoot-up'else 0x44
                nm[fields['SavedJoypadBits']]=pad;nm[fields['FrameCounter']]=(tick+200)&255
                omrun(om,0xad8c,ports=oldports)
                om.regs[6:8]=[4,5];om.map()
                for slot in[3,2,1]:
                    if om[0x510+slot]&128:omrun(om,0x8e54 if om[0x528+slot]==0x83 else 0x8eae,x=slot)
                om.regs[6:8]=[0,1];om.map()
                result,_=run(nm,lab['MsHostStep'],ports=newports);assert result==(85,7,91,0x41),('composed step',axis,tick,result)
                om[0x31]=int(f'{pad:08b}'[::-1],2)
                # Renderer source scratch20..7A and its staging100..1FF are
                # intentionally independent; durable actor state is exact.
                original_draw(om);put(nm,CurrentOAMOffset=0);invoke(nm,'MsRenderGate')
                visibilitydiffs+=sum(om[i]!=nm[0xc000+i]for i in range(0x6a8,0x6ac))
                diffs=[(hex(i),om[i],nm[0xc000+i])for i in range(0x480,0x750)if not 0x6a8<=i<0x6ac and om[i]!=nm[0xc000+i]]
                assert not diffs,('composed actor/life/render',axis,tick,diffs[:12],[(hex(i),om[i])for i in[0x480,0x498,0x4b0,0x4c8,0x4e0,0x4f8,0x540,0x50]])
                before=bytes(nm[0xc000:0xc800]);run(nm,lab['MsHostStep'],ports=newports);assert before==bytes(nm[0xc000:0xc800]);duplicates+=1
                nm[fields['GamePauseStatus']]=1;nm[fields['FrameCounter']]=(tick+201)&255;run(nm,lab['MsHostStep'],ports=newports);assert before==bytes(nm[0xc000:0xc800]);nm[fields['GamePauseStatus']]=0;paused+=1
                run(nm,lab['MsNativeApplyDelta']);gravityset.add(om[0x734]);shotsseen+=bool(om[0x512]|om[0x513]);frames+=1
        assert gravityset=={0,128}and shotsseen
        q.update(composed_actor_lifecycle_render_frames=frames,composed_original_constructors=6,composed_duplicate_epochs=duplicates,composed_paused_epochs=paused,composed_gravity_directions=sorted(gravityset),composed_frames_with_shots=shotsseen,composed_external_scene_audio_ports=sorted(newports),composed_native_visibility_differences=visibilitydiffs,composed_exact_durable_source_state='0480..074F except native OAM cursor visibility06A8..06AB; source renderer scratch/staging excluded explicitly')
        sheet=Image.new('RGB',(448,240),(23,27,37));draw=ImageDraw.Draw(sheet)
        colors={0x0f:(0,0,0),0x26:(248,120,88),0x15:(168,0,32),0x21:(60,188,252),0x20:(248,248,248),0x01:(0,0,252)}
        for i,(label,pixels)in enumerate(previews):
            x0,y0=(i%4)*112,(i//4)*120;draw.text((x0+8,y0+8),label,fill=(230,230,235))
            for (xx,yy),(pal,value)in pixels.items():
                xx=x0+8+(xx-128)*3;yy=y0+22+(yy-112)*3
                draw.rectangle((xx,yy,xx+2,yy+2),fill=colors[art['source_sprite_palette'][pal*4+value]])
        sheet.save(OUT/'native-render-preview.png');q['native_producer_preview_cells']=len(previews)
        q.update(passed=True,actor_bytes=len(actor),renderer_bytes=len(renderer),unfunded_gate_bytes=len(gate),minimum_standalone_SP=minimum,max_standalone_cycles=maxcycles,actual_native_helper_hits=helperhits,aggregate_pixels_sha256=digest.hexdigest(),actual_native_emitted_helper_bytes=1059,scope='CPU model executes exact linked native producer/CHR publication with source-authentic body/shot art and lifecycle. Fixture caches and physical CHR800..805 are not loader/resource/native admission. Main/ISR/raster cadence, actual play, source hurt blink/health, scene/audio/combat remain unqualified.')
        q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(P.__file__),P.REF,Path(M.__file__),M.ROM,OUT/'assembly.json',OUT/'native-render-witness.json',OUT/'actor.bin',OUT/'render.bin',OUT/'gate.bin',OUT/'art.json']}
    except Exception:q['error']=traceback.format_exc();raise
    finally:(OUT/'CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','error']}))
if __name__=='__main__':main()
