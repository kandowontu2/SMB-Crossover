"""Recover all32 original Karnov player states into a relocatable source unit."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
O=R/'build/karnov-original-source-1101-v1';ROM=Path('C:/NES/Karnov (USA).nes')
EXPECTED='0d49c1120fc13ead1efe4429f7cbb4f01b90e2486c66661c46e922dda6dc830a'
LO,HI=0xf28d,0xfb16
DISPATCH={0xf29b:32,0xf326:8,0xf723:16,0xf7dd:16}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,t:p.write_text(t,encoding='utf-8',newline='\n')


def graph(raw,lo=LO,hi=HI,dispatch=DISPATCH,extra_bank=None,extra_data=()):
    m=MPU();m.memory[0xc000:]=raw[16+14*8192:16+16*8192]
    if extra_bank:
        window,bank=extra_bank;m.memory[0x8000+window*8192:0xa000+window*8192]=raw[16+bank*8192:16+(bank+1)*8192]
    d=Disassembler(m)
    todo=[lo];code={};tables={};external={};ram={};reads={}
    while todo:
        pc=todo.pop()
        if pc in code:continue
        assert lo<=pc<hi,hex(pc)
        n,text=d.instruction_at(pc);assert text!='???',(hex(pc),text)
        mnemonic,mode=m.disassemble[m.memory[pc]];operand=m.memory[pc+1]+(m.memory[pc+2]<<8 if n==3 else 0)if n>1 else None
        code[pc]=dict(bytes=list(m.memory[pc:pc+n]),size=n,text=text,mnemonic=mnemonic,mode=mode,operand=operand)
        if mnemonic=='JSR'and operand==0xc831:
            assert pc in dispatch,('Unknown inline dispatcher',hex(pc));count=dispatch[pc]
            for at in range(pc+3,pc+3+2*count,2):
                target=m.memory[at]+256*m.memory[at+1];assert lo<=target<hi
                tables[at]=target;todo.append(target)
            continue
        if mnemonic in ['JSR','JMP']:
            assert mode=='abs',(hex(pc),text)
            if lo<=operand<hi:todo.append(operand)
            else:external.setdefault(operand,[]).append(pc)
        elif mode=='rel':todo.append((pc+2+(operand if operand<128 else operand-256))&65535)
        elif mode in ['zpg','zpx','zpy','abs','abx','aby','iny','inx','ind']:
            target=operand
            (ram if target<0x8000 else reads).setdefault(target,[]).append(dict(pc=pc,mode=mode,mnemonic=mnemonic))
        if mnemonic not in ['RTS','RTI','JMP']:todo.append(pc+n)
    occupied={}
    for pc,z in code.items():
        for a in range(pc,pc+z['size']):assert a not in occupied,(hex(pc),hex(a));occupied[a]=pc
    for at in tables:assert at not in occupied and at+1 not in occupied
    assert all(lo<=at<hi or at in extra_data for at in reads),reads
    return m,code,tables,external,ram,reads


def emit(m,code,tables,portable,lo=LO,hi=HI,romdata=None):
    label=lambda a:f'Kr_{a:04X}'
    romdata=romdata or {};lines=[];pc=lo
    while pc<hi:
        if pc not in code:
            if pc in tables:value='<'+label(tables[pc])
            elif pc-1 in tables:value='>'+label(tables[pc-1])
            else:value=f'${m.memory[pc]:02x}'
            lines.append(label(pc)+': .byte '+value);pc+=1;continue
        z=code[pc];text=z['text'];mn=z['mnemonic'];mode=z['mode'];operand=z['operand']
        if mode=='rel':
            target=(pc+2+(operand if operand<128 else operand-256))&65535
            text=mn.lower()+' '+label(target)
            if portable:text='j'+text[1:]
        elif mode in ['abs','abx','aby','zpg','zpx','zpy','inx','iny','ind']:
            if mn in ['JSR','JMP']:
                target=label(operand)if lo<=operand<hi else'KrDispatch'if operand==0xc831 else f'KrExternal_{operand:04X}'
            elif lo<=operand<hi:target=label(operand)
            elif portable and operand in romdata:target=romdata[operand]
            elif portable:target='KrPointer'+('+'+str(operand-0x58)if operand!=0x58 else'')if operand in [0x58,0x59]else f'KrState+${operand:04x}'
            else:target=f'${operand:04x}'if z['size']==3 else f'${operand:02x}'
            old=re.search(r'\$[0-9a-fA-F]+',text);assert old,text;text=text[:old.start()]+target+text[old.end():]
            if not portable and z['size']==3 and operand<256:text=text.replace(target,'a:'+target,1)
            if portable and(mn,mode)in [('STY','zpx'),('STX','zpy')]:
                transfer='TYA'if mn=='STY'else'TXA';suffix=',X'if mn=='STY'else',Y'
                text='PHP\n PHA\n '+transfer+'\n STA '+target+suffix+'\n PLA\n PLP'
        lines.append(label(pc)+': '+text+' ; original '+hex(pc));pc+=z['size']
    return '\n'.join(lines)+'\n'


def main():
    O.mkdir(exist_ok=True);S=O/'source';S.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    raw=ROM.read_bytes();assert sha(ROM)==EXPECTED
    m,code,tables,external,ram,reads=graph(raw)
    native=json.loads((R/'build/karnov-native-reference-1101-v1/capture/reference.json').read_text());assert native['passed']and native['ROM_sha256']==EXPECTED
    observed={int(x,16)for x in native['executed_instructions']if LO<=int(x,16)<HI}
    assert observed<=code.keys(),[hex(x)for x in observed-code.keys()]
    fixed=raw[16+14*8192:16+16*8192];(O/'original-fixed.bin').write_bytes(fixed)
    write(S/'original_actor.inc',emit(m,code,tables,False));write(S/'portable_actor.inc',emit(m,code,tables,True))
    helper=[]
    pc=0xc831;d=Disassembler(m)
    while pc<0xc847:
        n,t=d.instruction_at(pc);helper.append(t);pc+=n
    original_helper='\n'.join(helper)+'\n'
    write(S/'original_dispatch.inc',original_helper)
    write(S/'portable_dispatch.inc',original_helper.replace('$58','KrPointer').replace('$59','KrPointer+1').replace('$0058','KrPointer'))
    extern=''.join(f'KrExternal_{a:04X}=${a:04x}\n'for a in external)
    write(S/'reproduce.s','.setcpu "6502"\n'+extern+''' .segment "LOW"
 .incbin "../original-fixed.bin",0,$831
KrDispatch:
 .include "original_dispatch.inc"
 .incbin "../original-fixed.bin",$847,$2000-$847
 .segment "HIGH"
 .incbin "../original-fixed.bin",$2000,$128d
 .include "original_actor.inc"
 .incbin "../original-fixed.bin",$3b16,$4000-$3b16
''')
    write(S/'reproduce.cfg','MEMORY { LOW:start=$c000,size=$2000,file=%O; HIGH:start=$e000,size=$2000,file=%O; }\nSEGMENTS { LOW:load=LOW,type=ro; HIGH:load=HIGH,type=ro; }\n')
    write(S/'portable.s','.setcpu "6502"\n.macpack longbranch\n'+extern+'''KrState=$6000
KrPointer=$00
KrSaved0=KrState+$7fe
KrSaved1=KrState+$7ff
 .export KrFrame,KrState,KrPointer,KrActorEnd
.segment "CODE"
KrDispatch:
 .include "portable_dispatch.inc"
 .include "portable_actor.inc"
KrFrame:
 lda KrPointer
 sta KrSaved0
 lda KrPointer+1
 sta KrSaved1
 jsr Kr_F28D
KrFrameResult:
 php
 pha
 lda KrSaved0
 sta KrPointer
 lda KrSaved1
 sta KrPointer+1
 pla
 plp
 rts
KrActorEnd:
''')
    write(S/'portable.cfg','MEMORY { LAB:start=$9000,size=$2000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { CODE:load=LAB,type=ro; }\n')
    commands=[];cc=R/'tools/Windows/cc65/bin'
    for mode in ['reproduce','portable']:
        recipes=[[cc/'ca65.exe','-g','-I',S,S/(mode+'.s'),'-o',O/(mode+'.o')],[cc/'ld65.exe','-C',S/(mode+'.cfg'),O/(mode+'.o'),'-o',O/(mode+'.bin'),'--dbgfile',O/(mode+'.dbg'),'-Ln',O/(mode+'.lbl')]]
        for command in recipes:
            command=list(map(str,command));guard=validate(command,O,cwd=S);q=subprocess.run(command,cwd=S,capture_output=True,text=True);commands.append(dict(command=command,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    save(O/'build-commands.json',commands);assert(O/'reproduce.bin').read_bytes()==fixed
    report=dict(passed=True,source=True,native_port=False,installed=False,donor=str(ROM),donor_sha256=EXPECTED,entire_fixed_16KiB_reproduced=True,semantic_actor_span=[LO,HI],actor_span_bytes=HI-LO,recovered_instructions=len(code),observed_original_instructions=len(observed),dispatch_states=32,secondary_input_dispatch=8,relocated_pointer_words=len(tables),external_callbacks={f'{a:04X}':[f'{x:04X}'for x in sites]for a,sites in external.items()},native_RAM_fields={f'{a:04X}':x for a,x in ram.items()},source_ROM_reads={f'{a:04X}':x for a,x in reads.items()},private_lab_only=dict(code_start=0x9000,state=[0x6000,0x6800],borrowed_pointer=[0,2],saved_pointer=[0x67fe,0x6800],new_host_global_or_ZP_bytes=0,no_host_grant=True),scope='All32 original player selector roots including attack, ladder, flight/swim, injury/death/script paths. Reconstructed original code/data plus explicit untouched fixed-bank ranges equals donor16KiB. Relocatable private source is assembled; differential CPU checks, graphics, callbacks, host resources/integration/native admission remain required.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),ROM,R/'build/karnov-native-reference-1101-v1/controls.json',R/'build/karnov-native-reference-1101-v1/capture/reference.json',O/'portable.bin',O/'portable.dbg',O/'reproduce.bin',O/'build-commands.json',*[p for p in S.iterdir()if p.is_file()]]})
    save(O/'assembly.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','native_RAM_fields','source_ROM_reads']}))


if __name__=='__main__':main()
