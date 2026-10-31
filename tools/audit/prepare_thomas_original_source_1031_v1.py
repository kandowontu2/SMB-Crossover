"""Recover a small, relocatable Thomas source core from the pinned Kung Fu ROM.

This is an isolated source lab, not a roster build or a host allocation.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

R=Path(__file__).resolve().parents[2]
O=R/'build/thomas-original-source-v1'
DONOR=Path('C:/NES/Kung Fu (Japan, USA) (En).nes')
OLD=Path('C:/Users/kando/Documents/ChatGPT/mario in kid icarus/kungfu')
EXPECTED='2275213352411a23df7428496ad03991348ddee3034ac6db83d2d16f0d1f8554'
sys.path.insert(0,str(R/'tools/audit'))
from private_build_outputs_v1 import validate
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def recover(rom):
    m=MPU();m.memory[0x8000:]=rom[16:0x8010];d=Disassembler(m)
    lo,hi=0xa482,0xa936
    instructions={};a=lo
    while a<hi:
        n,text=d.instruction_at(a)
        assert text!='???',(hex(a),text)
        instructions[a]=(n,text);a+=n
    assert a==hi
    def symbol(a):
        if lo<=a<hi:
            assert a in instructions,hex(a)
            return f'Th_{a:04X}'
        if 0x9b09<=a<0x9baf:return f'ThData_{a:04X}'
        if a==0xc462:return 'ThomasNativeDamage'
        return None
    core=['; Original instruction bodies A482..<A936. Labels, not absolute aliases, bind internal control/data.']
    external=[]
    for a,(n,text) in instructions.items():
        op=m.memory[a];_,mode=m.disassemble[op]
        if mode in ('abs','abx','aby','rel'):
            q=re.search(r'\$([0-9a-fA-F]{4})',text);assert q,text
            target=int(q[1],16);label=symbol(target)
            if label:text=text[:q.start()]+label+text[q.end():]
            elif target>=0x8000:external.append(dict(pc=a,target=target,instruction=text))
            elif mode in ('abs','abx','aby') and target<256:
                text=text[:q.start()]+'a:'+text[q.start():]
        core.append(f'Th_{a:04X}: {text.lower() if "Th" not in text else text} ; donor ${a:04X}')
    data=[];words={}
    for a in range(0x9b09,0x9b25,2):words[a]=m.memory[a]|m.memory[a+1]<<8
    for a in range(0x9b61,0x9b6b,2):words[a]=m.memory[a]|m.memory[a+1]<<8
    for a in range(0x9b09,0x9baf):
        if a in words:expr='<'+symbol(words[a])
        elif a-1 in words:expr='>'+symbol(words[a-1])
        else:expr=f'${m.memory[a]:02x}'
        data.append(f'ThData_{a:04X}: .byte {expr}')
    assert not external,external
    return '\n'.join(core)+'\n','\n'.join(data)+'\n',instructions,words

def main():
    global O
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=O);args=ap.parse_args();O=args.output.resolve()
    assert not O.exists(),'A successor directory is required; never mutate a frozen lab'
    O.mkdir(parents=True);(O/'source').mkdir()
    rom=DONOR.read_bytes();assert sha(DONOR)==EXPECTED
    assert len(rom)==40976 and rom[4:8]==bytes([2,1,1,8])
    # These are generated input slices, not a claim to a full semantic disassembly.
    (O/'original.prg').write_bytes(rom[16:0x8010])
    (O/'original.chr').write_bytes(rom[0x8010:])
    core,data,ins,words=recover(rom)
    (O/'source/thomas_core.inc').write_text(core,encoding='utf-8')
    (O/'source/thomas_tables.inc').write_text(data,encoding='utf-8')
    (O/'source/reproduce.s').write_text(''' .setcpu "6502"
 .segment "PRG"
 ThomasNativeDamage=$c462
 .incbin "../original.prg",0,$1b09
 .include "thomas_tables.inc"
 .incbin "../original.prg",$1baf,$2482-$1baf
 .include "thomas_core.inc"
 .incbin "../original.prg",$2936,$8000-$2936
''',encoding='utf-8')
    (O/'source/component.s').write_text(''' .setcpu "6502"
 .import ThomasNativeDamage
 .export ThomasInput,ThomasMove,ThomasAnimate,ThomasSelectPose
 .export ThomasGroundAnimate,ThomasAirAnimate,ThomasCrouchAnimate
 ThomasInput=Th_A482
 ThomasMove=Th_A696
 ThomasAnimate=Th_A826
 ThomasSelectPose=Th_A8EB
 ThomasGroundAnimate=Th_A86D
 ThomasAirAnimate=Th_A8A9
 ThomasCrouchAnimate=Th_A8DC
 .segment "THOMAS_TABLES"
 .include "thomas_tables.inc"
 .segment "THOMAS_CORE"
 .include "thomas_core.inc"
''',encoding='utf-8')
    (O/'source/lab_native_import.s').write_text('''; Explicit original-oracle dependency, not a host import or allocation.
 .export ThomasNativeDamage
 ThomasNativeDamage=$c462
''',encoding='utf-8')
    (O/'source/reproduce.cfg').write_text('MEMORY { PRG: start=$8000,size=$8000,file=%O; }\nSEGMENTS { PRG: load=PRG,type=ro; }\n',encoding='utf-8')
    (O/'source/component.cfg').write_text('MEMORY { LAB: start=$6000,size=$1000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { THOMAS_CORE: load=LAB,type=ro,start=$6000; THOMAS_TABLES: load=LAB,type=ro,start=$6800; }\n',encoding='utf-8')
    cc=R/'tools/Windows/cc65/bin'
    assert cc.exists(),cc
    commands=[]
    def run(cmd):
        proof=validate(cmd,O,cwd=O/'source')
        p=subprocess.run([str(x)for x in cmd],cwd=O/'source',capture_output=True,text=True)
        commands.append(dict(command=[str(x)for x in cmd],guard=proof,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
        assert p.returncode==0,p.stderr
    for name in ['reproduce','component','lab_native_import']:
        run([cc/'ca65.exe',O/f'source/{name}.s','-g','-o',O/f'{name}.o','-l',O/f'{name}.lst','--create-full-dep',O/f'{name}.dep'])
    for name,objects in [('reproduce',['reproduce']),('component',['component','lab_native_import'])]:
        run([cc/'ld65.exe','-C',O/f'source/{name}.cfg',*[O/f'{v}.o'for v in objects],'-o',O/f'{name}.bin','--dbgfile',O/f'{name}.dbg','-Ln',O/f'{name}.lbl','-m',O/f'{name}.map'])
    dump(O/'build-commands.json',commands)
    assert (O/'reproduce.bin').read_bytes()==rom[16:0x8010]
    plan=dict(status='ISOLATED_ORIGINAL_SOURCE_CORE_NOT_HOST_ADMITTED',donor=str(DONOR),donor_sha256=EXPECTED,
      mapper=0,prg_bytes=32768,chr_bytes=8192,old_port_reference=str(OLD),
      recovered_core=dict(start='A482',end_exclusive='A936',bytes=0x4b4,instructions=len(ins)),
      recovered_tables=dict(start='9B09',end_exclusive='9BAF',bytes=166,relocated_pointer_words=len(words)),
      source_reproduction='Entire original 32768 PRG bytes exact; recovered instructions/tables plus explicit untouched incbin ranges. Not a full semantic disassembly.',
      portable_lab='Same recovered instructions source-linked at6000; tables at6800; original native RAM offsets retained only inside isolated lab. No host RAM/ROM allocation.',
      external_dependency='ThomasNativeDamage genuine original C462 remains explicitly bound in lab; native world/camera/boss/grab RAM consumers retained. Host adapter not implemented.',
      authentic_controls=dict(input_byte='6A',right=1,left=2,down=4,jump_up=8,punch_B=64,kick_A=128,
          action='69 bit0 right-facing,bit1 crouch,bit2 air,bit3 hurt,bit4 punch,bit5 kick',
          horizontal='049E adds20 each movement update, producing1 or2 native pixel steps; no invented acceleration',
          jump='68 starts10;9B82 timer and9B9C absoluteY tables drive original11-position arc',
          health='04A6 starts30hex;037A damage subtract; signednegative enters native death',
          audio='FB..FF queue source events consumed by genuine F831 once per original NMI'),
      actual_caller_order=['82D6 NMI transfers prior frame+timers21..34','87D2 A696 movement','87D5 native actors','87DD A482 onlywhen038F==0','882E A826 animation','8842 A8EB pose selection'],
      next_steps=['CPU differential: original core vs relocated source, legal coherent action sequences/allflags','Decode actual original background pose scripts through native DAEA/DB3E PPU consumer; preserve both facings and real palettes','Recover native player damage and audio driver APIs with ordered RAM/APU comparisons','Only then propose explicit selected-owner state/code/CHR and real host head/feet/contact/progression adapters'],
      exclusions=['No roster/menu/Start/common edits','No native run or readiness claim','No host collision/camera/grab/death/audio integration claim'],
      start_constraint='Ryu/Shinobi/Thomas FmAlts4/64 menu exists; current Start drops newbits. Current393/400 helper last7 also proposed WWF6; no ownership claim.',
      inputs={str(p):sha(p)for p in [DONOR,OLD/'tools/build.py',OLD/'src/mario.s',OLD/'build/native.asm',Path(__file__),R/'tools/audit/private_build_outputs_v1.py']})
    dump(O/'plan.json',plan)
    dump(O/'source-stage.json',dict(status='SOURCE_LINKED_ORIGINAL_PRG_EXACT',source_files={str(p):sha(p)for p in sorted((O/'source').iterdir())},outputs={str(O/n):sha(O/n)for n in ['component.bin','component.dbg','component.lbl','reproduce.bin','build-commands.json','plan.json']}))
    print(json.dumps(dict(result='PASS',directory=str(O),original_prg_exact=True,core_bytes=1204,table_bytes=166,source_stage_sha256=sha(O/'source-stage.json'))))

if __name__=='__main__':main()
