"""Isolated authentic Rockman CX source routines and Quick Man pose pack."""
from pathlib import Path
import hashlib,json,sys,subprocess
from PIL import Image,ImageDraw
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'build/quickman-source-v1'
ROM=Path('C:/NES/the stash/Rockman_CX-world44.spcs.bio.nes')
sys.path.insert(0,str(Path(__file__).parent))
from quickman_source_pose_review_v1 import Bus
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class CoreBus(Bus):
    def __init__(self,b):super().__init__(b);self.bank=0x3c;self.bank7=0x3d
    def __getitem__(self,a):
        if isinstance(a,slice):return [self[i]for i in range(a.start or 0,a.stop,a.step or 1)]
        if 0xa000<=a<0xc000:return self.b[16+self.bank7*8192+a-0xa000]
        return super().__getitem__(a)
    def __setitem__(self,a,v):
        if a==0x8001 and self.reg==7:self.bank7=v;self.events.append([a,v]);return
        super().__setitem__(a,v)

def run(bus,pc,limit=30000):
    bus.ram[0x1fe]=0xfe;bus.ram[0x1ff]=0x7f
    m=MPU(memory=bus);m.pc=pc;m.sp=0xfd;steps=0;pcs=[]
    while m.pc!=0x7fff:
        pcs.append(m.pc);m.step();steps+=1;assert steps<limit,(hex(m.pc),steps)
    return dict(steps=steps,cycles=m.processorCycles,pc_sha256=hashlib.sha256(b''.join(x.to_bytes(2,'little')for x in pcs)).hexdigest(),unique_PCs=[f'{x:04X}'for x in sorted(set(pcs))])

def source(b):
    d=OUT/'source';d.mkdir(parents=True,exist_ok=True)
    for name,at,n in [('motion-core-3c3d',0x78010,16384),('fixed-core-3e3f',0x7c010,16384),('sprite-tables-1c',0x38010,8192),('sprite-data-1415',0x28010,16384),('weapon-AI-1e',0x3c010,8192),('progression-1f',0x3e010,8192)]:
        (d/f'{name}.bin').write_bytes(b[at:at+n])
    m=MPU();m.memory[0x8000:]=b[0x78010:];ds=Disassembler(m)
    ranges=[(0x84ee,0x8783),(0x879d,0x8818),(0x8818,0x8906),(0x8922,0x8a71),(0x8a86,0x8d00),(0xbdaa,0xbdcc),(0xbe81,0xbf8a),(0xcd92,0xce88),(0xd3a0,0xd3c7),(0xd3d4,0xd44c),(0xda50,0xdaac),(0xdcdf,0xdd17),(0xdf31,0xdf3c),(0xeecd,0xef85),(0xf859,0xf868),(0xf8ae,0xf8eD)]
    rows=[]
    for lo,hi in ranges:
        rows.append(f'; Actual CX CPU${lo:04X}..${hi:04X}; mapped bank3C/3D belowC000, fixed3E/3F above.');p=lo
        while p<hi:
            n,s=ds.instruction_at(p);raw=bytes(m.memory[p:p+n]);rows.append(f'{p:04X} {raw.hex():<8} {s}');p+=n
    (d/'native-instructions.txt').write_text('\n'.join(rows)+'\n')
    for bank,lo,hi,name in [(0x1e,0x8290,0x8318,'boomerang-AI'),(0x1f,0x9cae,0x9d4b,'quick-man-init'),(0x1f,0x989c,0x98cc,'quick-man-health-init')]:
        m.memory[0x8000:0xa000]=b[16+bank*8192:16+(bank+1)*8192];ds=Disassembler(m);p=lo;rows=[]
        while p<hi:
            n,s=ds.instruction_at(p);raw=bytes(m.memory[p:p+n]);rows.append(f'{p:04X} {raw.hex():<8} {s}');p+=n
        (d/f'{name}-bank{bank:02x}.txt').write_text('\n'.join(rows)+'\n')
    records=[];chr=bytearray();at=0x1bd40;count=b[at];at+=1
    for i in range(count):
        page,n,bank=b[at:at+3];at+=3;source_at=16+bank*16384+(page-0x80)*256;chunk=b[source_at:source_at+n*256]
        records.append(dict(source_file_offset=f'{source_at:X}',source_bank16=f'{bank:02X}',source_CPU=f'{page:02X}00',bytes=len(chunk),CHR_destination=f'{len(chr):04X}'));chr.extend(chunk)
    assert len(chr)==8192
    (d/'quick-man-native-CHR.bin').write_bytes(chr)
    return bytes(chr),records

def poses(b,chr):
    out=OUT/'poses';out.mkdir(exist_ok=True);by_frame={};types=[];excluded=[]
    bases=list(b[0x7d3d7:0x7d3e4]);assert bases==[0x1a,0x19,0x18,0,0x10,8,0xc,0x10,0x14,0x1c,0x20,0x26,4]
    # Native player state table with firing variants plus explicit wall poses.
    ids=sorted(set(v+s for v in bases for s in range(2))|{0x7e,0x7f})
    colors=[[(0,0,0),(0,0,0),(209,213,0),(255,0,160)],[(0,0,0),(0,0,0),(255,255,255),(236,238,78)]]
    for typ in ids:
        ptr=b[0x39010+typ]+256*b[0x390d0+typ];at=0x38010+ptr-0x8000;last,delay=b[at:at+2]
        if last>=64:continue
        frames=list(b[at+2:at+3+last]);types.append(dict(type=f'{typ:02X}',script_CPU=f'{ptr:04X}',last_index=last,delay=delay,frames=frames,game_states=[i for i,v in enumerate(bases)if v==typ or v+1==typ]))
        for index,frame in enumerate(frames):
            if frame==0 or frame in by_frame:continue
            bus=Bus(b);bus.ram[0x420]=0xc0;bus.ram[0x400]=typ;bus.ram[0x6a0]=index;bus.ram[0x460]=128;bus.ram[0x4a0]=128
            result=run(bus,0xcd92);n=bus.ram[6]//4;assert 0<n<=32
            cells=[list(bus.ram[0x200+i*4:0x204+i*4])for i in range(n)]
            if any((c[2]&3)>1 for c in cells):
                excluded.append(dict(type=f'{typ:02X}',frame=frame,reason='Native pose requests palette2/3; no authenticated RGB mapping installed.'));continue
            im=Image.new('RGBA',(256,240))
            for y,tile,attr,x in reversed(cells):
                for yy in range(8):
                    py=7-yy if attr&128 else yy
                    for xx in range(8):
                        px=7-xx if attr&64 else xx;at=tile*16;v=((chr[at+py]>>(7-px))&1)|(((chr[at+py+8]>>(7-px))&1)<<1)
                        if v:
                            assert attr&3<2,(typ,frame,attr)
                            im.putpixel((x+xx,y+1+yy),colors[attr&3][v]+(255,))
            if not im.getbbox():continue
            box=im.getbbox();crop=im.crop(box);by_frame[frame]=dict(frame=frame,from_type=f'{typ:02X}',index=index,OAM=cells,bbox=box,size=crop.size,opaque_pixels=sum(bool(v)for v in crop.getchannel('A').getdata()),sprites=n,max_body_sprites_per_scanline=max(sum(y+1<=row<y+9 for y,t,a,x in cells)for row in range(240)),CPU=result,image=crop)
    values=list(by_frame.values());atlas=Image.new('RGBA',(8*48,((len(values)+7)//8)*48));contact=Image.new('RGB',atlas.size,'#004444');draw=ImageDraw.Draw(contact)
    for i,v in enumerate(values):
        im=v.pop('image');x=i%8*48;y=i//8*48;pos=(x+(48-im.width)//2,y+46-im.height);atlas.alpha_composite(im,pos);contact.paste(im,pos,im);draw.text((x+2,y+1),f'{v["frame"]:02X}',fill='white');v['atlas_cell']=[x,y,48,48]
    atlas.save(out/'quick-man-source-poses.png');contact.resize((contact.width*2,contact.height*2),Image.Resampling.NEAREST).save(out/'contact.png')
    report=dict(scope='Actual CD92 entity renderer, native player script/frame/geometry/flip/OAM; native alternate CHR upload list. RGB palette-role colors from original game rip. Isolated source fixtures, not live unlocked Quick Man gameplay.',types=types,frames=values,excluded=excluded,body_only_OAM_limit=max(v['max_body_sprites_per_scanline']for v in values),host_allocations=False)
    (out/'pose-manifest.json').write_text(json.dumps(report,indent=2)+'\n');return len(values)

def benches(b):
    rows=[]
    # Native horizontal speed owner, including state12 Down+A fast wall jump.
    for state in [4,5,6,12]:
        for down in [0,0x20]:
            bus=CoreBus(b);bus.ram[0x2c]=state;bus.ram[0x4e0]=down;bus.ram[0x420]=0xc0
            cpu=run(bus,0x8818);v=bus.ram[0x600]+bus.ram[0x620]/256
            rows.append(dict(kind='native_speed_owner',state=state,down_latch=down,speed_px_per_tick=v,velocity=[bus.ram[0x600],bus.ram[0x620]],CPU=cpu))
    # Full native firing dispatch and triple Quick Boomerang construction.
    for facing in [0x80,0xc0]:
        bus=CoreBus(b);r=bus.ram;r[0x9b]=0x80;r[0xac]=1;r[0x420]=facing;r[0x460]=128;r[0x440]=1;r[0x4a0]=100;r[0x2c]=6
        cpu=run(bus,0xda50);objects=[]
        for slot in range(2,5):
            objects.append(dict(slot=slot,type=r[0x400+slot],flags=r[0x420+slot],X=[r[0x440+slot],r[0x460+slot]],Y=r[0x4a0+slot],vx=[r[0x600+slot],r[0x620+slot]],vy=[r[0x640+slot],r[0x660+slot]]))
        assert all(q['flags']&128 for q in objects)
        rows.append(dict(kind='native_Quick_Man_firing_dispatch',flag_9b=128,facing=facing,objects=objects,CPU=cpu))
    # Post-collision native wall-state tail, preserving native report inputs.
    # This isolates the owner after movement, rather than faking a full wall.
    for facing in [0x80,0xc0]:
        for held in [0,0x40,0x80,0xa0]:
            for guard in [0,3]:
                for material in [1,8]:
                    bus=CoreBus(b);r=bus.ram
                    for a,v in {0x9b:128,0x2c:12,0x23:held,0x420:facing,0xb0:guard,0x6d:material}.items():r[a]=v
                    cpu=run(bus,0xbf3e)
                    rows.append(dict(kind='wall_state_post_collision_tail',entry='BF3E',before=dict(facing=facing,held=held,guard=guard,material=material,support_report=0),after=dict(state=r[0x2c],facing=r[0x420],guard=r[0xb0],down_latch=r[0x4e0],vy=[r[0x640],r[0x660]],pose=r[0x400]),CPU=cpu))
    # Actual jump-store entry, with source initialized dry-land jump parameters.
    for latch in [0,0x20]:
        bus=CoreBus(b);r=bus.ram;r[0x3b]=0xdf;r[0x3c]=4;r[0x4e0]=latch;r[0x2c]=12;r[0x420]=0xc0
        speed=run(bus,0x8818);cpu=run(bus,0x859f)
        assert (r[0x640],r[0x660])==(4,0xdf)
        rows.append(dict(kind='jump_store_after_native_state12_speed',entry='859F',scope='Original jump parameters and integer speed owner. Full movement/collision/A-edge transition remains separate.',down_latch=latch,vy=[r[0x640],r[0x660]],vx=[r[0x600],r[0x620]],state=r[0x2c],CPU=cpu,speed_CPU=speed))
    trajectories=[]
    for facing,player_x in [(0x80,160),(0xc0,96)]:
        bus=CoreBus(b);r=bus.ram
        for a,v in {0x9b:128,0xac:1,0x420:facing,0x460:player_x,0x440:1,0x4a0:100,0x2c:6,0x61:0x3c,0x62:0x3d,0x20:1}.items():r[a]=v
        run(bus,0xda50);ticks=[]
        for tick in range(1,201):
            r[0x1c]=tick&255;cpu=run(bus,0xdcdf)
            objects=[dict(slot=i,active=bool(r[0x420+i]&128),flags=r[0x420+i],X=[r[0x440+i],r[0x460+i],r[0x480+i]],Y=[r[0x4a0+i],r[0x4c0+i]],timer=r[0x4e0+i],vx=[r[0x600+i],r[0x620+i]],vy=[r[0x640+i],r[0x660+i]])for i in range(2,5)]
            ticks.append(dict(tick=tick,cycles=cpu['cycles'],objects=objects))
            if not any(q['active']for q in objects):break
        assert not any(q['active']for q in objects)
        trajectories.append(dict(facing=facing,player_X=player_x,player_Y=100,scope='Actual DCDF weapon update, native collision dispatch, bank1E:8290 AI, EECD motion/boundaries; empty enemy fixture, fixed viewportpage1. No live-emulator or enemy-hit claim.',all_released_at_tick=tick,max_cycles=max(x['cycles']for x in ticks),ticks=ticks))
    (OUT/'boomerang-trajectories.json').write_text(json.dumps(trajectories,indent=2)+'\n')
    (OUT/'benches.json').write_text(json.dumps(dict(status='ISOLATED_ORIGINAL_INSTRUCTION_BENCHES',cases=rows,native_gameplay=False),indent=2)+'\n');return len(rows)

def reassemble(b):
    out=OUT/'instruction-roundtrip';out.mkdir(exist_ok=True)
    ca=ROOT/'tools/Windows/cc65/bin/ca65.exe';ld=ROOT/'tools/Windows/cc65/bin/ld65.exe'
    cases=[]
    for bank,lo,hi,name in [(0x3c,0x87fd,0x8818,'facing'),(0x3c,0x8818,0x8906,'speed'),(0x3c,0x859f,0x85b0,'jump-store'),(0x3d,0xbdaa,0xbdcc,'boomerang-create'),(0x3d,0xbf3e,0xbf8a,'wall-tail'),(0x3e,0xcdf9,0xce88,'metasprite-owner'),(0x3e,0xdf31,0xdf3c,'boomerang-dispatch'),(0x1e,0x8290,0x8318,'boomerang-AI')]:
        base=0x8000 if bank in [0x3c,0x1e]else 0xa000 if bank==0x3d else 0xc000 if bank==0x3e else 0xe000
        at=16+bank*8192+lo-base;raw=b[at:at+hi-lo];m=MPU();m.memory[lo:hi]=raw;ds=Disassembler(m);p=lo;lines=[]
        while p<hi:
            n,s=ds.instruction_at(p);assert s!='???';lines.append(s);p+=n
        assert p==hi
        src=out/f'{name}.s';obj=out/f'{name}.o';cfg=out/f'{name}.cfg';binary=out/f'{name}.bin'
        src.write_text('.setcpu "6502"\n.segment "CODE"\n.org $'+f'{lo:04X}'+'\n'+'\n'.join(lines)+'\n')
        cfg.write_text(f'MEMORY {{ R:file=%O,start=${lo:04X},size=${len(raw):04X}; }}\nSEGMENTS {{ CODE:load=R,type=ro; }}\n')
        commands=[[str(ca),str(src),'-o',str(obj)],[str(ld),'-C',str(cfg),'-o',str(binary),str(obj)]]
        for command in commands:
            p=subprocess.run(command,capture_output=True,text=True);assert p.returncode==0,(command,p.stdout,p.stderr)
        assert binary.read_bytes()==raw,name
        cases.append(dict(name=name,source_CPU=f'bank{bank:02X}:{lo:04X}..{hi:04X}',source_file_offset=f'{at:X}',bytes=len(raw),source_sha256=hashlib.sha256(raw).hexdigest(),assembled=str(binary),assembled_sha256=sha(binary),source=str(src),commands=commands))
    report=dict(status='EIGHT_ACTUAL_INSTRUCTION_RANGES_REASSEMBLE_BYTE_EXACT',cases=cases,ca65_sha256=sha(ca),ld65_sha256=sha(ld),relocatable_host_kernel=False,no_original_ROM_modification=True)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');return len(cases)

def findings():
    poses=json.loads((OUT/'poses/pose-manifest.json').read_text());chr=(OUT/'source/quick-man-native-CHR.bin').read_bytes()
    tiles={c[1]for f in poses['frames']for c in f['OAM']};patterns={chr[t*16:t*16+16]for t in tiles}
    data=dict(status='SOURCE_CONFIRMED_WITH_EXPLICIT_FIXTURE_LIMITS',native_version='Supplied Japanese2016v1.0; no2024 wallkick recoil update imported.',owners=dict(identity=dict(address='009B bit7',persistent_save='7426+save-slot',source='bank1F:98AD sets80; source Start transform92DB..937A clears bit7, swaps currentHP with7FF1, restores maxHP from7420+slot.'),input=dict(held='0023',new_edges='0027',native_bits=dict(A=1,B=2,Select=4,Start=8,Up=16,Down=32,Left=64,Right=128)),player=dict(state='002C',pose='0400',shoot_pose_offset='003D',X_page_pixel_sub=['0440','0460','0480'],Y_pixel_sub=['04A0','04C0'],VX_hi_sub=['0600','0620'],VY_hi_sub=['0640','0660'],wall_facing_guard='00B0',wall_down_speed_latch='04E0',wall_material='006D'),health=dict(current='06C0',maximum='0099',normal_saved_maximum='7420+save-slot',Quick_Man_init_HP=40,normal_new_game_HP=24,container_increment=4,source='bank1F:98A1 /98B9; core3C:8391. Complete acquisition/cap and live progression unqualified.'),firing=dict(entry='DA50',held_B_gate='core3C:879D',Quick_Man_branch='DA93->core3D:BDAA',native_object_type='0E',native_slots=[2,3,4],shot_offsets_from_player_X=[-12,12],velocities_magnitude=dict(diagonals=[6,128],center=[8,128]),vertical_velocities=[[253,0],[3,0],[0,0]],native_fan_attempt_period_ticks=3,energy='Default weapon0 Quick Man branch performs no weapon-energy subtraction. Native weapon menu is replaced by the Start transform path; low upgrade bits share009B.')),wall=dict(entry_gate='core3C:8653..8685',source_conditions=['009B bit7 set','Material rejection table8B5B and no vertical-page overflow','Falling negativeYvelocity','Held direction into current wall/facing'],entry_state=12,facing_guard_ticks=3,owner='core3D:BE81..BF89',native_slide_VY=[255,0],wall_speed=1.75,wall_speed_with_Down_latch=2.75,jump_entry='859F copies native3B/3C into0660/0640; dry-land initialization at8163 is04DF (Y velocity is subtracted from position).',jump_scope='Post-collision tail and jump-store isolated separately. Full native movement/A-edge/contact transition remains open.'),boomerang=dict(dispatch='DCDF uses type0E -> DF31 -> farcall bank1E:8290',physics_and_boundary='EECD..EF85',initial_motion_ticks='Updates1..14 include native movement; at timer13 the post-motion owner zeros all velocity.',retarget='At timer42 (update43), native bank1E:82B6 selects a native target or player fallback, callsF18B, then continues original motion.',empty_enemy_fixture='Two facings, three shots, fixed viewport. All native active flags released at update84; max whole weapon-update cost8689cycles.',unqualified=['Actual enemy damage/immunity/contact','Capacity/partial-busy slot behavior','Live native Quick Man replay','Host enemy targeting/collision adapter']),resource_floor=dict(source_unique_8x8_tile_indices=len(tiles),source_unique_8x8_patterns=len(patterns),pattern_bytes=len(patterns)*16,source_pose_frames=len(poses['frames']),source_OAM_cells=sum(f['sprites']for f in poses['frames']),max_OAM_cells_per_pose=max(f['sprites']for f in poses['frames']),max_native_8x8_body_sprites_per_scanline=poses['body_only_OAM_limit'],exact_sprite_palette_roles=2,complete_native_CHR_upload_bytes=8192,first_player_upload_bytes=2304,reassembled_instruction_subset_bytes=682,scope='Floors and actual native8x8 usage only. Host8x16 repack, full source closure, RAM, PRG, CHR and palettes require root leases; no fit/admission claim.'),host_adaptation=dict(status='NOT_IMPLEMENTED_NO_LEASE',intent=['Root owns Bass/Roll/Quick Man Select cycle; retain SMB Start pause rather than importing CX fortress form-swap UI.','A jump; hold direction into a wall to enter the source wall state while falling; A again to climb by wall jumps; Down+A fast jump uses the source speed latch.','Held B emits native three-boomerang fan; reserve independent host projectile owners before integration.','Use host collision/material/target adapters at documented native ownership boundaries; preserve source motion and timeout/return order.','Keep nativeHP/upgrade semantics explicit; no direct reuse of CX009B, player entity RAM or host global leases.','Keep source SFX queue writes behind the host audio adapter.']),negative_fixture=dict(entry='bank1F:98A1',result='A full isolated health-init attempt reached nativeC0BA frame-wait after30000instructions. No fake NMI was supplied; only exact initialization stores are source-confirmed.'))
    (OUT/'findings.json').write_text(json.dumps(data,indent=2)+'\n')

def main():
    assert sha(ROM)=='e04a4523e4ff0a0c7bfad1d30acedb9140c0972fa3be1c62e5d42a09664b5f6e';OUT.mkdir(parents=True,exist_ok=True);b=ROM.read_bytes()
    chr,records=source(b);n=poses(b,chr);tests=benches(b);roundtrip=reassemble(b);findings()
    manifest=dict(status='PRIVATE_CX_QUICK_MAN_SOURCE_KERNEL_NOT_HOST_INTEGRATED',ROM=str(ROM),ROM_sha256=sha(ROM),mapper=4,PRG_KiB=512,CHR_RAM_KiB=8,CHR_upload_records=records,authentic_unique_pose_frames=n,source_bench_cases=tests,byte_exact_instruction_roundtrips=roundtrip,no_host_RAM_PRG_CHR_palette_leases=True,no_ROM_patch=True,no_native_Quick_Man_gameplay_claim=True,tools={str(p):sha(p)for p in [Path(__file__),ROOT/'tools/audit/quickman_source_pose_review_v1.py']},art_manifest=str(ROOT/'build/full-menu-quickman-art-v1/manifest.json'),art_manifest_sha256=sha(ROOT/'build/full-menu-quickman-art-v1/manifest.json'),remaining=['Full native wall-contact/movement/A-edge transition fixture','Boomerang enemy-hit and capacity/contact cases','Health-container and weapon/transform progression complete call-path qualification','Strict original controller replay unlocking Quick Man','Host adaptation, 8x16 sprite repack and resource lease'],bindings={str(p):sha(p)for p in sorted(OUT.rglob('*'))if p.is_file()and p.name!='handoff.json'})
    p=OUT/'handoff.json';p.write_text(json.dumps(manifest,indent=2)+'\n');print(p);print(sha(p));print('poses',n,'benches',tests)
if __name__=='__main__':main()
