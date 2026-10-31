"""Extend the isolated Thomas lab with genuine health source, art and audio APIs."""
from pathlib import Path
import argparse,copy,hashlib,json,re,shutil,subprocess,sys
from PIL import Image,ImageDraw
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
import thomas_original_cpu_1031_v1 as t
from private_build_outputs_v1 import validate
O=R/'build/thomas-original-component-v3';P=R/'build/thomas-original-source-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def code(c,lo,hi,prefix,*,reachable=False):
    d=Disassembler(c);ins={}
    todo=[lo]
    if reachable:
        while todo:
            a=todo.pop();known_z=None;known_n=None
            while lo<=a<hi and a not in ins:
                n,text=d.instruction_at(a);assert text!='???',(hex(a),text)
                ins[a]=(n,text);op=c.memory[a];name,mode=c.disassemble[op]
                if name in ['RTS','RTI','BRK']:break
                if mode=='rel':
                    target=(a+2+((c.memory[a+1]+128)%256-128))&65535
                    condition={'BEQ':known_z,'BNE':None if known_z is None else not known_z,
                        'BMI':known_n,'BPL':None if known_n is None else not known_n}.get(name)
                    if condition is not False:todo.append(target)
                    if condition is True:break
                if name in ['JSR','JMP']and mode=='abs':
                    target=c.memory[a+1]|c.memory[a+2]<<8
                    if lo<=target<hi:todo.append(target)
                    if name=='JMP':break
                assert not(name=='JMP'and mode=='ind'),'Indirect audio code requires explicit target review'
                if name in ['LDA','LDX','LDY']and mode=='imm':
                    value=c.memory[a+1];known_z=value==0;known_n=bool(value&128)
                elif name not in ['STA','STX','STY','PHA','PHP','NOP','BEQ','BNE','BPL','BMI','BCC','BCS','BVC','BVS']:
                    known_z=known_n=None
                a+=n
    else:
        a=lo
        while a<hi:
            n,text=d.instruction_at(a);assert text!='???',(hex(a),text)
            ins[a]=(n,text);a+=n
        assert a==hi
    covered={p for a,(n,_)in ins.items()for p in range(a,a+n)}
    assert len(covered)==sum(n for n,_ in ins.values()),'No overlapping source instructions'
    def ref(target):
        if lo<=target<hi:
            # Legitimate indexed-data bases can be instruction operand bytes.
            a=target
            while a not in ins and a in covered:a-=1
            if a in ins:return f'{prefix}_{a:04X}'+(f'+{target-a}'if a!=target else '')
            return f'{prefix}_{target:04X}'
        return None
    lines=[];external={};a=lo
    while a<hi:
        if a in ins:
            n,text=ins[a];_,mode=c.disassemble[c.memory[a]]
            if mode in ['abs','abx','aby','rel']:
                m=re.search(r'\$([0-9a-fA-F]{4})',text);assert m,text
                target=int(m[1],16);label=ref(target)
                if label:text=text[:m.start()]+label+text[m.end():]
                elif target>=0x8000:
                    label=f'ThomasOriginal_{target:04X}';external[label]=target;text=text[:m.start()]+label+text[m.end():]
                elif mode!='rel'and target<256:text=text[:m.start()]+'a:'+text[m.start():]
            lines.append(f'{prefix}_{a:04X}: {text} ; donor ${a:04X}');a+=n
        else:
            lines.append(f'{prefix}_{a:04X}: .byte ${c.memory[a]:02X}');a+=1
    return '\n'.join(lines)+'\n',external,len(ins)

def main():
    global O
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=O);args=ap.parse_args();O=args.output.resolve()
    assert not O.exists();O.mkdir(parents=True);(O/'source').mkdir();(O/'assets').mkdir()
    assert sha(P/'source-stage.json')=='bfb39214d1d5362f0e6481c4bfdbaceb69d5472a692baa3df5eb5973f56becd0'
    rom=t.donor();c=t.machine(rom)
    health,imports,hcount=code(c,0xc462,0xc5fd,'ThHealth')
    audio,aimports,acount=code(c,0xf831,0xfff0,'ThAudio',reachable=True)
    for name in ['thomas_core.inc','thomas_tables.inc']:shutil.copyfile(P/'source'/name,O/'source'/name)
    (O/'source/thomas_health.inc').write_text(health,encoding='utf-8')
    (O/'source/thomas_audio_original.inc').write_text(audio,encoding='utf-8')
    for name in ['original.prg','original.chr']:shutil.copyfile(P/name,O/name)
    (O/'source/component.s').write_text((P/'source/component.s').read_text(encoding='utf-8'),encoding='utf-8')
    (O/'source/health.s').write_text(' .setcpu "6502"\n .export ThomasNativeDamage,ThomasHealthPlayerDeath\n ThomasNativeDamage=ThHealth_C462\n ThomasHealthPlayerDeath=ThHealth_C4E5\n'+''.join(f' .import {n}\n'for n in imports)+' .segment "THOMAS_HEALTH"\n'+health,encoding='utf-8')
    (O/'source/lab_native_import.s').write_text('; Original nonplayer data/services: explicitly lab-only, not a host ABI.\n'+''.join(f' .export {n}\n {n}=${v:04X}\n'for n,v in sorted(imports.items())),encoding='utf-8')
    original_defs=''.join(f'{n}=${v:04X}\n'for n,v in sorted((imports|aimports).items()))
    (O/'source/reproduce.s').write_text(''' .setcpu "6502"
 .segment "PRG"
 ThomasNativeDamage=ThHealth_C462
'''+original_defs+''' .incbin "../original.prg",0,$1b09
 .include "thomas_tables.inc"
 .incbin "../original.prg",$1baf,$2482-$1baf
 .include "thomas_core.inc"
 .incbin "../original.prg",$2936,$4462-$2936
 .include "thomas_health.inc"
 .incbin "../original.prg",$45fd,$7831-$45fd
 .include "thomas_audio_original.inc"
 .incbin "../original.prg",$7ff0,$10
''',encoding='utf-8')
    shutil.copyfile(P/'source/reproduce.cfg',O/'source/reproduce.cfg')
    (O/'source/component.cfg').write_text('MEMORY { LAB: start=$6000,size=$1000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { THOMAS_CORE: load=LAB,type=ro,start=$6000; THOMAS_HEALTH: load=LAB,type=ro,start=$6500; THOMAS_TABLES: load=LAB,type=ro,start=$6800; }\n',encoding='utf-8')
    commands=[];cc=R/'tools/Windows/cc65/bin'
    def run(cmd):
        guard=validate(cmd,O,cwd=O/'source');p=subprocess.run([str(v)for v in cmd],cwd=O/'source',capture_output=True,text=True)
        commands.append(dict(command=[str(v)for v in cmd],guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
    for name in ['component','health','lab_native_import','reproduce']:
        run([cc/'ca65.exe',O/f'source/{name}.s','-g','-o',O/f'{name}.o','-l',O/f'{name}.lst','--create-full-dep',O/f'{name}.dep'])
    for name,objects in [('reproduce',['reproduce']),('component',['component','health','lab_native_import'])]:
        run([cc/'ld65.exe','-C',O/f'source/{name}.cfg',*[O/f'{n}.o'for n in objects],'-o',O/f'{name}.bin','--dbgfile',O/f'{name}.dbg','-Ln',O/f'{name}.lbl','-m',O/f'{name}.map'])
    dump(O/'build-commands.json',commands)
    assert(O/'reproduce.bin').read_bytes()==rom[16:0x8010]
    # Native original CPU cold/Start produces the palette; the old hardware
    # capture independently verifies exactly the same visible background role.
    base=t.boot()
    for f in range(600):t.frame(base,0x10 if 120<=f<125 else 0)
    palette=list(base.memory.ppu[0x3f0c:0x3f10]);assert palette==[15,39,48,15]
    hardware=R/'build/full-menu-final-art-v1/native/thomas-timing/endframe.palette.bin'
    assert list(hardware.read_bytes()[12:16])==palette
    rgb={15:(0,0,0),39:(212,178,94),48:(236,238,236)}
    # NES colors use the existing project's display palette exactly.
    sys.path.insert(0,str(R/'build/full-menu-final-art-v1'))
    import export as native_export
    rgb={i:tuple(native_export.RGB[i])for i in palette}
    atlas=Image.new('RGBA',(7*64,6*96));draw=ImageDraw.Draw(atlas)
    poses=[];tiles={};patterns=bytearray();descriptors=bytearray();semantic_bytes=bytearray()
    # The displayed background hero is at a fixed screen position in the donor.
    # Retain the full untrimmed48x80 envelope and a separate original script.
    x0,y0,w,h=104,104,48,80
    def pixel(tile,yy,xx):
        off=0x1000+tile*16+yy;b=rom[0x8010+off];hi=rom[0x8010+off+8]
        return(b>>(7-xx)&1)|((hi>>(7-xx)&1)<<1)
    for index,pose in enumerate(range(0x25,0x4f)):
        d=t.machine();d.memory.ctrl=base.memory.ctrl;d.memory[0x10]=base.memory[0x10]
        ptr=d.memory[0x8056+pose]|d.memory[0x80a5+pose]<<8;d.memory[0]=ptr&255;d.memory[1]=ptr>>8
        # Source empty wall/floor, matching the native adjacent floor witness.
        d.memory.ppu[0x2000:0x23c0]=bytes([0xfc])*960;d.memory.ppu[0x23c0:0x2400]=bytes([255])*64
        d.memory.ppu[0x2000+22*32:0x2000+23*32]=bytes([0x2a])*32
        t.run(d,0xdb3e)
        assert all(0x2000<=a<0x23c0 for a,_ in d.memory.ppuwrites)
        pixels=bytearray(w*h);im=Image.new('RGBA',(w,h));removed=0
        for yy in range(h):
            for xx in range(w):
                gy,gx=y0+yy,x0+xx;tile=d.memory.ppu[0x2000+(gy//8)*32+gx//8];v=pixel(tile,gy&7,gx&7)
                if gy//8==22 and v==pixel(0x2a,gy&7,gx&7):
                    if v:removed+=1
                    v=0
                pixels[yy*w+xx]=v
                if v:im.putpixel((xx,yy),rgb[palette[v]]+(255,))
        records=[];start=len(descriptors)
        for cy in range(0,h,16):
            for cx in range(0,w,8):
                pair=bytearray(32)
                for yy in range(16):
                    for xx in range(8):
                        v=pixels[(cy+yy)*w+cx+xx];off=(yy//8)*16+(yy&7)
                        pair[off]|=(v&1)<<(7-xx);pair[off+8]|=((v>>1)&1)<<(7-xx)
                if not any(pair):continue
                key=bytes(pair)
                if key not in tiles:tiles[key]=len(patterns)//32;patterns.extend(pair)
                tile=tiles[key];assert tile<65536
                records.append([cy,tile,0,cx]);descriptors.extend(bytes([cy,tile&255,tile>>8,0,cx]))
        semantic_bytes.extend(pixels)
        reconstructed=bytearray(w*h)
        for cy,tile,attr,cx in records:
            pair=patterns[tile*32:tile*32+32]
            for yy in range(16):
                for xx in range(8):
                    off=(yy//8)*16+(yy&7);v=(pair[off]>>(7-xx)&1)|((pair[off+8]>>(7-xx)&1)<<1)
                    if v:reconstructed[(cy+yy)*w+cx+xx]=v
        assert reconstructed==pixels,(pose,'source sprite conversion')
        for yy in range(h):assert sum(1 for cy,_,_,cx in records if cy<=yy<cy+16)<=6
        atlas.alpha_composite(im,((index%7)*64+8,(index//7)*96+12));draw.text(((index%7)*64+4,(index//7)*96+1),f'{pose:02X}',fill=(200,200,200,255))
        poses.append(dict(command=pose,original_script=f'{ptr:04X}',bbox=im.getbbox(),records=records,descriptor_offset=start,parts=len(records),floor_pixels_subtracted=removed,
          native_ppu_writes=d.memory.ppuwrites,source_index_sha256=hashlib.sha256(pixels).hexdigest()))
    atlas.save(O/'assets/thomas-original-42-poses.png')
    (O/'assets/thomas-8x16.chr').write_bytes(patterns)
    (O/'assets/thomas-descriptors.bin').write_bytes(descriptors)
    (O/'assets/thomas-source-indices.bin').write_bytes(semantic_bytes)
    dump(O/'assets/poses.json',dict(poses=poses,palette=palette,original_pattern_table=4096,envelope=dict(x=x0,y=y0,width=w,height=h),
        conversion='Original DAEA/DB3E CPU consumer; index0 transparent, row22 removes only same-position adjacent floor2A pixels. Every remaining opaque source pixel includingblack is retained; omit whollyzero8x16pairs. Descriptor y/u16pair/attr/x is source-lab metadata, not assigned hardware tile numbers; per-pose bank packing remains future work.',
        anchor='Native screen coordinate envelope only. Host must normalize sourceB6 and baked background jump position together; do not apply a second jump displacement.',
        source_hardware_palette=dict(path=str(hardware),sha256=sha(hardware)),unique_8x16_pairs=len(tiles),max_parts=max(p['parts']for p in poses)))
    api=dict(status='ISOLATED_SOURCE_COMPONENT_NOT_HOST_READY',parent_source_stage=sha(P/'source-stage.json'),donor_sha256=t.EXPECTED,
      sizes=dict(input_move_animation=1204,tables=166,health=411,original_audio_region=1983,audio_decoded_instructions=acount,art_chr=len(patterns),art_descriptors=len(descriptors)),
      health=dict(entry='ThomasNativeDamage',input='X6 player;037A damage;04A6 native signedHP',source_instructions=hcount,lab_external_original_imports=imports),
      audio=dict(entry='F831',source_file='source/thomas_audio_original.inc',source_original_prg_exact=True,
        input='FB..FF queues, source priority, timersF1..F9 and07D8..07FA',output='Ordered4000..4017 writes; clears all5queues',
        portability='Original-address audio source reconstruction only. Song/data pointers are not relocated or host-integrated.',external_original_refs=aimports),
      graphics=dict(pose_commands='25..4E,42 complete original background command scripts',original_palette=palette,output='One atlas+source-index corpus+deduplicated8x16patterns and descriptors',
        palette_claim='Actual native backgroundrole3 colors; no assumption that current host sprite P0/P1 are available.'),
      host_gaps=['Explicit selected-owner RAM/state+ROM/CHR allocation needed','Split native horizontal world/camera/boss boundary from SMB native head/feet/support','Native attack rectangles/damage/defeat must be connected to current host actors','Normalize original background art anchors against sourceB6 without double jump','Map native health/death/life/powerup safely','Audio driver/state/channel ownership and rawNMI restore not integrated','Thomas Startmask64 remains future coordinatedcompaction; no7Bclaim'],
      no_shared_or_native_changes=True,bindings={str(p):sha(p)for p in [Path(__file__),Path(t.__file__),P/'source-stage.json',hardware]})
    dump(O/'component-api.json',api)
    files=[p for p in O.rglob('*')if p.is_file()and p.suffix not in ['.o']]
    dump(O/'source-stage.json',dict(result='SOURCE_LINKED_PRG_EXACT_ART_PIXEL_CONVERSION_PASS',donor_sha256=t.EXPECTED,
        full_original_prg_exact=True,source_inputs={str(p):sha(p)for p in sorted(files)}))
    print(json.dumps(dict(result='PASS',source_stage_sha256=sha(O/'source-stage.json'),sizes=api['sizes'],max_parts=max(p['parts']for p in poses))))

if __name__=='__main__':main()
