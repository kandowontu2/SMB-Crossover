"""Bounded source component recovery for the pending Excitebike slot."""
from pathlib import Path
import copy,hashlib,json,random,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import excitebike_original_cpu_1101_v2 as E
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
O=R/'build/excite-prince-component-1101-v2'

def save(name,q):
    (O/name).write_text(json.dumps(q,indent=2)+'\n')

def main():
    O.mkdir(exist_ok=True)
    c=E.boot();summary=[];counts={};calls={};states=[]
    def trace(c):
        pc=c.pc;counts[pc]=counts.get(pc,0)+1
        if c.memory[pc]==0x20:
            t=c.memory[pc+1]|c.memory[pc+2]<<8
            calls[t]=calls.get(t,0)+1
    for f in range(800):
        E.frame(c,0x10 if 120<=f<123 or 300<=f<303 else 0,trace)
        if f%30==0:summary.append(dict(frame=f,mode=c.memory[0x40],scene=c.memory[0x41],phase=c.memory[0x44],pad=c.memory[0x14],p15=c.memory[0x15],ram40=list(c.memory[0x40:0x50]),ram300=list(c.memory[0x300:0x340])))
        if f in [359,599,799]:states.append((f,bytes(c.memory[:2048])))
    save('discovery.json',dict(source_SHA=E.SHA,untimed_CPU_only=True,summary=summary,calls={f'{p:04X}':n for p,n in sorted(calls.items())},executed={f'{p:04X}':n for p,n in sorted(counts.items())}))
    # Only three selected initialized states; no frame/state forest.
    for f,ram in states:(O/f'state-{f}.bin').write_bytes(ram)
    print('Excitebike original reset/NMI/main discovery',len(counts),'PCs',len(calls),'calls',flush=True)
    build_component()
    source_sequences(c)
    source_art(c)
    prince_audit()
    # Publication outputs are consumers of this receipt, never its inputs.
    # Including their prior versions makes every --resume freeze self-stale.
    files=[p for p in O.iterdir()if p.is_file()and p.name not in {'review.json','handoff.json','source-and-proof.zip'}]
    dependencies=[Path(__file__).resolve(),R/'tools/reference/excitebike_original_cpu_1101_v2.py',R/'tools/reference/excitebike_component_1101_v2.md',R/'tools/audit/thomas_original_cpu_1031_v1.py',R/'tools/audit/verify_native_relocation.py',R/'tools/Windows/cc65/bin/ca65.exe',R/'tools/Windows/cc65/bin/ld65.exe']
    save('review.json',dict(passed=True,status='REVIEWABLE_EXCITEBIKE_ORIGINAL_ASSEMBLY_COMPONENT_NO_HOST_UNLOCK',native=False,installed=False,output_bytes=sum(p.stat().st_size for p in files),output_files=len(files),bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in files+dependencies},next='Read tools/reference/excitebike_component_1101_v2.md. Root owns host integration, native admission and nightly delivery. Prince audit is hardware/art provenance only.'))

BLOCKS=[(0xcd1f,0xced0),(0xdca0,0xdd8d),(0xda58,0xda6a),(0xe359,0xe3f4)]
TABLES=[(0xc0bc,0xc0d6),(0xd868,0xd892),(0xd8f7,0xd8ff)]
ENTRY={'ExMotor':0xcd59,'ExMotorAll':0xcd1f,'ExSlopePose':0xdca0,'ExAirStep':0xdcf2,'ExAirLaunch':0xdd38,'ExFractionalX':0xda58,'ExTemperature':0xe359}
BRANCH={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc','BVS':'jvs','BVC':'jvc'}

def build_component():
    source=E.machine();d=Disassembler(source);ins={}
    for lo,hi in BLOCKS:
        pc=lo
        while pc<hi:
            n,display=d.instruction_at(pc);mn,mode=source.disassemble[source.memory[pc]]
            assert mn!='???',(hex(pc),display)
            v=int.from_bytes(bytes(source.memory[pc+1:pc+n]),'little')
            ins[pc]=dict(n=n,mn=mn,mode=mode,value=v,display=display)
            pc+=n
        assert pc==hi,(hex(pc),hex(hi))
    def ref(a):
        assert a in ins,('Unrecovered code boundary',hex(a))
        return f'ExN_{a:04X}'
    def data(a):
        if a<0x2000:return f'ExState+${a&2047:03x}'
        assert any(lo<=a<hi for lo,hi in TABLES),('Unrecovered data boundary',hex(a))
        return f'ExData_{a:04X}'
    out=['; Original Excitebike NES instructions; generated from authenticated donor.\n.setcpu "6502"\n.macpack longbranch\n.export ExState\nExState=$c000\n.segment "EX_CODE"\n']
    for name,pc in ENTRY.items():out.append(f'.export {name}\n{name}=ExN_{pc:04X}\n')
    for pc,v in ins.items():
        mn,mode,a=v['mn'],v['mode'],v['value'];operand=''
        out.append(f'.export ExN_{pc:04X}\nExN_{pc:04X}: ; native ${pc:04X}: {v["display"]}\n')
        if (mn,mode) in [('STY','zpx'),('STX','zpy')]:
            # 6502 lacks STY abs,X / STX abs,Y. Preserve the source A/P contract.
            move,index=('tya','x')if mn=='STY'else('txa','y')
            out.append(f' php\n pha\n {move}\n sta {data(a)},{index}\n pla\n plp\n')
            continue
        if mode=='rel':operand=ref((pc+2+(a if a<128 else a-256))&65535);mn=BRANCH[mn]
        elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
            operand=ref(a)if mn in ['JSR','JMP']else data(a)
            operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
        elif mode=='imm':operand=f'#${a:02x}'
        elif mode=='acc':operand='a'
        else:assert mode=='imp',(pc,mode)
        out.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
    out.append('.export ExCodeEnd\nExCodeEnd:\n.segment "EX_DATA"\n')
    for lo,hi in TABLES:
        for a in range(lo,hi):out.append(f'.export ExData_{a:04X}\nExData_{a:04X}: .byte ${source.memory[a]:02x}\n')
    (O/'excitebike-component.s').write_text(''.join(out))
    (O/'component.cfg').write_text('MEMORY { CODE: start=$a000,size=$1000,file=%O,fill=yes; }\nSEGMENTS { EX_CODE:load=CODE,type=ro; EX_DATA:load=CODE,type=ro,start=$a900; }\n')
    ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe'
    commands=[[str(ca),'-o',str(O/'component.o'),str(O/'excitebike-component.s')],[str(ld),'-C',str(O/'component.cfg'),'-o',str(O/'component.bin'),'-Ln',str(O/'component.lbl'),str(O/'component.o')]]
    logs=[]
    for cmd in commands:
        r=subprocess.run(cmd,capture_output=True,text=True);logs.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stderr
    save('compile.json',logs)
    names=E.T.labels(O/'component.lbl');image=(O/'component.bin').read_bytes();assert names['ExCodeEnd']<0xa900
    rng=random.Random(0xe9c17e);cases=0;cycles=[10**9,0];entry_counts={};paths=set()
    # Structured input/phase/actor cohorts, plus randomized velocity/fraction
    # and crash/recovery fixtures. Actor and input low bits correlate here;
    # this is not an exhaustive cross-product of every control and actor.
    seeds=[(O/f'state-{f}.bin').read_bytes()for f in [359,599,799]]
    for name,pc in ENTRY.items():
        ncases=512 if name in ['ExMotor','ExMotorAll'] else 256
        for i in range(ncases):
            ram=bytearray(seeds[i%3]);x=i&3
            for p in [0x90+x,0x394+x,0x380+x,0x384+x,0x378+x]:ram[p]=rng.randrange(256)
            ram[0x94+x]=rng.randrange(7);ram[0x5c+x]=i&255;ram[0x4c]=(i>>2)&3
            ram[0xb0+x]=(i>>4)&3;ram[0x98+x]=0 if i%5 else 255;ram[0x9c+x]=(i>>6)%6
            ram[0x26+x]=0 if i%3 else rng.randrange(16);ram[0x2a+x]=0 if i%3 else 8
            ram[0x374+x]=0 if i%4 else 4;ram[0xac+x]=rng.randrange(14);ram[0xd4+x]=i%7
            ram[0x52]=(i>>3)%3;ram[0xa4+x]=(i>>4)%4;ram[0x70+x]=i%5;ram[0xb8+x]=8+i%49
            ram[0x3b6]=i%34;ram[0x3e0]=0 if i%7 else 1;ram[0x3c]=0 if i%5 else 8;ram[0x4f]=i&1
            old=E.machine();list.__setitem__(old.memory,slice(0,2048),ram)
            class Flat(list):pass
            new=E.T.NesMPU(memory=Flat([0]*65536),pc=names[name]);new.memory[0xa000:0xb000]=image;new.memory[0xc000:0xc800]=ram
            for p in range(256):new.memory[p]=rng.randrange(256)
            zp=bytes(new.memory[:256]);args=dict(a=rng.randrange(256),x=x,y=rng.randrange(6),p=0x20|(rng.randrange(16)&13))
            a=E.call(old,pc,**args);b=E.T.run(new,names[name],**args)
            after=bytes(old.memory[:256]+old.memory[512:2048]);actual=bytes(new.memory[0xc000:0xc100]+new.memory[0xc200:0xc800])
            assert actual==after,(name,i,next((p,u,v)for p,(u,v)in enumerate(zip(after,actual))if u!=v))
            assert a[:3]==b[:3] and a[4]==b[4] and (a[3]&0xef)==(b[3]&0xef),(name,i,a,b)
            assert bytes(new.memory[:256])==zp,(name,i,'Host ZP changed')
            cycles[0]=min(cycles[0],b[5]);cycles[1]=max(cycles[1],b[5]);cases+=1
        entry_counts[name]=ncases
    report=dict(passed=True,donor=str(E.DONOR),donor_sha256=E.SHA,source_CPU_only=True,native_host=False,installed=False,actor_component_cases=cases,entries=entry_counts,source_ranges=[[hex(a),hex(b)]for a,b in BLOCKS],table_ranges=[[hex(a),hex(b)]for a,b in TABLES],component_code_bytes=names['ExCodeEnd']-0xa000,table_bytes=sum(b-a for a,b in TABLES),state_base='C000',state_bytes=2048,host_zero_page_preserved=True,all_application_RAM_registers_flags_SP_exact=True,cycle_range=cycles,limits=['Explicit CPU fixtures; original quarter-frame phase imported at4C.','No native SMB terrain, health/combat, audio, menu dispatch or playable unlock.','Original vertical movement is top-down track perspective; importing it as a platform jump needs a deliberate host adapter.','Untimed PPU status alternates ready bits; this is not a raster or donor-native qualification.'],bindings={str(p.relative_to(R)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__).resolve(),R/'tools/reference/excitebike_original_cpu_1101_v2.py',O/'excitebike-component.s',O/'component.bin',O/'component.lbl']})
    report['status_flags_comparison']='Physical N/V/D/I/Z/C flags exact; PHP/PLP synthetic B bit ignored.'
    save('component-CPU-controls.json',report)
    print('Excitebike private-state assembled component',cases,'cases passed;',report['component_code_bytes'],'code bytes',flush=True)

def source_sequences(base):
    names=E.T.labels(O/'component.lbl');image=(O/'component.bin').read_bytes()
    mapping={pc:names[name]for name,pc in ENTRY.items()}
    old,new=copy.deepcopy(base),copy.deepcopy(base);counts={};phases=set();air=set();angles=set();temps=[];speeds=[]
    def relay(c):
        if c.pc not in mapping:return
        pc=c.pc;counts[pc]=counts.get(pc,0)+1
        class Flat(list):pass
        p=E.T.NesMPU(memory=Flat([0]*65536),pc=mapping[pc]);p.memory[0xa000:0xb000]=image;p.memory[0xc000:0xc800]=bytes(c.memory[:2048])
        result=E.T.run(p,mapping[pc],a=c.a,x=c.x,y=c.y,p=c.p)
        reference=E.machine();list.__setitem__(reference.memory,slice(0,2048),bytes(c.memory[:2048]))
        expected=E.call(reference,pc,a=c.a,x=c.x,y=c.y,p=c.p)
        aa=bytes(reference.memory[:256]+reference.memory[512:2048]);bb=bytes(p.memory[0xc000:0xc100]+p.memory[0xc200:0xc800])
        assert aa==bb,('Natural replacement diff',hex(pc),c.x,next((hex(k if k<256 else k+256),a,b)for k,(a,b)in enumerate(zip(aa,bb))if a!=b))
        # A callable replacement executes only this component, with its source
        # result returned to the real donor NMI/camera/terrain/render/audio order.
        for lo,hi in [(0,256),(512,2048)]:list.__setitem__(c.memory,slice(lo,hi),p.memory[0xc000+lo:0xc000+hi])
        c.a,c.x,c.y=result[:3];c.p=(result[3]&0xef)|(c.p&0x10);c.pc=(c.stPopWord()+1)&65535
    segments=[('A-accelerate',180,0x80),('B-turbo',240,0x40),('B-wheelie',120,0x42),('B-forward-tilt',120,0x41),('lane-up',90,0x88),('lane-down',90,0x84),('coast-cool',180,0)]
    total=0;rows=[]
    for title,n,pad in segments:
        for i in range(n):
            E.frame(old,pad);E.frame(new,pad,relay)
            aa=bytes(old.memory[:256]+old.memory[512:2048]);bb=bytes(new.memory[:256]+new.memory[512:2048])
            assert aa==bb,(title,i,'Application RAM',[(hex(k if k<256 else k+256),a,b)for k,(a,b)in enumerate(zip(aa,bb))if a!=b][:12])
            assert (old.a,old.x,old.y,old.sp,old.p&0xef)==(new.a,new.x,new.y,new.sp,new.p&0xef),(title,i,'CPU ABI')
            assert old.memory.ppu==new.memory.ppu and old.memory.oam==new.memory.oam and old.memory.apu==new.memory.apu,(title,i,'PPU/OAM/APU')
            phases.add(old.memory[0x4c]);air.add(old.memory[0xb0]);angles.add(old.memory[0xac]);temps.append(old.memory[0x3b6]);speeds.append(old.memory[0x94]*256+old.memory[0x90]);total+=1
        rows.append(dict(segment=title,frames=n,end_speed=old.memory[0x94]*256+old.memory[0x90],end_temperature=old.memory[0x3b6],end_angle=old.memory[0xac],end_airborne=old.memory[0xb0],end_crash=old.memory[0x98]))
    save('source-sequencing-CPU-controls.json',dict(passed=True,donor_sha256=E.SHA,source_CPU_only=True,host_native=False,installed=False,frames=total,natural_startup_frames=800,replaced_calls={hex(p):n for p,n in counts.items()},segments=rows,quarter_phases=sorted(phases),airborne_states=sorted(air),angles=sorted(angles),temperature_range=[min(temps),max(temps)],speed_range=[min(speeds),max(speeds)],all_frame_application_RAM_CPU_PPU_OAM_APU_exact=True,limitations=['Component runs in callable CPU substitute; this is not an integrated NES candidate.','Original track terrain, timing services and other actors remain donor-owned.','Bus has untimed status readiness and no acoustic rendering.','Observed natural airborne states0/2, heat8..29 and one launch do not prove the complete overheat/crash/recovery lifecycle.']))
    print('Excitebike real source sequencing',total,'frames',sum(counts.values()),'replacement calls passed',flush=True)

def source_art(base):
    from PIL import Image
    palette=(R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes();chr=E.donor()[16400:];variants={};cases=0
    for angle in range(16):
      for recover in range(6):
       for air in [0,1,2]:
        for phase in range(16):
            c=E.machine();list.__setitem__(c.memory,slice(0,2048),bytes(base.memory[:2048]));c.memory[0xac]=angle;c.memory[0x9c]=recover;c.memory[0xb0]=air;c.memory[0x3f]=phase;c.memory[0x36]=phase%7
            c.memory[0x90]=1 if phase&1 else 0;c.memory[0x94]=1 if phase&2 else 0;c.memory[0x58]=0;c.memory[0x98]=0;c.memory[0xdc]=[0,1,255][phase%3]
            E.call(c,0xe1f9,x=0);pose=c.a;cases+=1
            if pose in variants:continue
            c.memory[0x80]=80;c.memory[0x8c]=120;c.memory[4]=112;c.memory[0xb]=c.memory[0xd8c9]
            E.call(c,0xe1a3,x=0)
            cells=[]
            for at in range(112,148,4):
                y,t,a,x=c.memory[0x200+at:0x204+at]
                if t==0xfc:continue
                cells.append(dict(x=x-80,y=y-120,tile=t,attr=a))
            variants[pose]=dict(source_pose=pose,cells=cells,source_fixture=dict(angle=angle,recovery=recover,airborne=air,phase=phase),palette=list(base.memory.ppu[0x3f10:0x3f20]))
    used=sorted({v['tile']for q in variants.values()for v in q['cells']});basechr=4096 if base.memory.ctrl&8 else 0
    patterns=b''.join(chr[basechr+t*16:basechr+t*16+16]for t in used)
    (O/'excitebike-body-patterns.bin').write_bytes(patterns)
    save('source-art.json',dict(donor_sha256=E.SHA,source_CPU_only=True,fixture_count=cases,pose_count=len(variants),source_sprite_height=8,pattern_base=basechr,used_tiles=used,packed_tile_map={str(t):i for i,t in enumerate(used)},source_pattern_bytes=len(patterns),poses=[variants[k]for k in sorted(variants)],limits=['All packets generated by genuine E1F9/E1A3/D1C7 instructions. Fixture coverage does not prove every packet is eligible during host play.','No NES sprite-limit/native hardware visual qualification. Palette is original course initialized data.']))
    sheet=Image.new('RGB',(8*48,((len(variants)+7)//8)*48),'#565c74')
    for i,q in enumerate(variants.values()):
      for v in reversed(q['cells']):
       for y in range(8):
        for x in range(8):
            py=7-y if v['attr']&128 else y;px=7-x if v['attr']&64 else x;at=basechr+v['tile']*16
            z=((chr[at+py]>>(7-px))&1)|(((chr[at+py+8]>>(7-px))&1)<<1)
            if z:
                color=q['palette'][(v['attr']&3)*4+z]&63;dest=(i%8*48+v['x']+x+10,i//8*48+v['y']+y+10)
                if 0<=dest[0]<sheet.width and 0<=dest[1]<sheet.height:sheet.putpixel(dest,tuple(palette[color*3:color*3+3]))
    sheet.resize((sheet.width*2,sheet.height*2),Image.Resampling.NEAREST).save(O/'source-poses.png')
    print('Excitebike original art',len(variants),'poses',len(used),'patterns',flush=True)

def prince_audit():
    from PIL import Image
    rom=Path('C:/NES/Prince of Persia (USA).nes');raw=rom.read_bytes();digest=hashlib.sha256(raw).hexdigest()
    assert digest=='5f14d4d31cc588ddcdfb2b4d46eb7051b06d02655c9208037ef7ae137c4740e4'
    assert raw[4]==8 and raw[5]==0 and raw[6]>>4==2
    memory=bytearray(65536);memory[0x8000:0xc000]=raw[16:16400];memory[0xc000:]=raw[-16384:]
    cpu=MPU(memory=memory);dis=Disassembler(cpu);lines=[]
    for title,pc,limit in [('reset',0xc008,100),('NMI',0xff13,70)]:
        lines.append('; '+title+' fixed PRG bank7\n')
        for _ in range(limit):
            n,text=dis.instruction_at(pc);lines.append(f'{pc:04X}  {bytes(memory[pc:pc+n]).hex():8} {text}\n');pc+=n
            if text in ['RTS','RTI']or pc>=0xfff0:break
    (O/'prince-fixed-entry-disassembly.txt').write_text(''.join(lines))
    archive=R/'build/_recovery/legacy-sources-2026-10-31.zip'
    with zipfile.ZipFile(archive)as z:
        index=json.loads(z.read('index.json'));original='full-menu-source-art-v1/native/persia-discovery-v1/'
        def object(name):
            record=next(q for q in index if q['path']==original+name);data=z.read('objects/'+record['sha256']);assert hashlib.sha256(data).hexdigest()==record['sha256'];return data,record
        snapshot,record=object('frame-01200.bin');launch,lrecord=object('launch.json');launch=json.loads(launch)
    assert len(snapshot)==14638 and snapshot[:8]==b'NATIVE01'and launch['ROM_sha256']==digest
    oam=snapshot[14:270];patterns=snapshot[270:8462];palette=snapshot[8462:8494];cells=[]
    for i in range(43,52):
        y,t,a,x=oam[4*i:4*i+4];cells.append(dict(x=x,y=y+1,tile=t,attr=a))
    origin=[min(q['x']for q in cells),min(q['y']for q in cells)]
    for q in cells:q['x']-=origin[0];q['y']-=origin[1]
    used=sorted({q['tile']for q in cells});(O/'prince-body-patterns.bin').write_bytes(b''.join(patterns[t*16:t*16+16]for t in used))
    extent=[max(q['x']for q in cells)+8,max(q['y']for q in cells)+8]
    pal=(R/'tools/Windows/NEXXT 3.0/defaults/nes.pal').read_bytes();preview=Image.new('RGB',tuple(extent),'#565c74');pixels=0
    for q in reversed(cells):
      for y in range(8):
       for x in range(8):
        py=7-y if q['attr']&128 else y;px=7-x if q['attr']&64 else x;at=q['tile']*16;v=((patterns[at+py]>>(7-px))&1)|(((patterns[at+py+8]>>(7-px))&1)<<1)
        if v:
            color=palette[16+(q['attr']&3)*4+v]&63;preview.putpixel((q['x']+x,q['y']+y),tuple(pal[3*color:3*color+3]));pixels+=1
    assert pixels==262,pixels
    preview.resize((extent[0]*4,extent[1]*4),Image.Resampling.NEAREST).save(O/'prince-source-body.png')
    save('prince-source-audit.json',dict(status='PRINCE_FIXED_ENTRY_AND_HISTORICAL_BODY_PROVENANCE_ONLY',donor=str(rom),donor_sha256=digest,mapper=2,NES2_submapper=raw[8]>>4,PRG_bytes=131072,CHR_ROM_bytes=0,CHR_RAM_bytes=64<<(raw[11]&15),fixed_bank=7,reset='C008',NMI='FF13',original_native_packet=record,original_launch_object=lrecord,original_capture_rerun=False,source_pattern_base=0,late_endFrame_PPUCTRL=snapshot[12],source_cells=cells,source_palette=list(palette[16:]),source_origin=origin,source_packet_extent=extent,source_pattern_tiles=used,packed_tile_map={str(t):i for i,t in enumerate(used)},source_opaque_pixels=pixels,limits=['Only original fixed entry bytes and an existing authenticated native body packet, not Prince movement/animation recovery.','CHR RAM is uploaded by the original engine. ROM tile ordinals alone are not a valid art source.','Body packet uses source visible pattern base0000; the historical endFrame control is a later loading state. No new screenshot agreement claim.','No assembled Prince actor or native host integration/admission.']))
    print('Prince source audit: fixed-bank entry and authenticated262-pixel body only',flush=True)

if __name__=='__main__':main()
