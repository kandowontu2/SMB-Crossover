"""Assemble original and private Metal Storm actor instructions, no host edits."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
from py65.disassembler import Disassembler
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
import metal_storm_cpu_1101_v2 as M
from private_build_outputs_v1 import validate
OUT=ROOT/'build/metal-storm-component-1101-v2'
SPANS=[(0xab53,0xbcad),(0xe324,0xe32b),(0xea4e,0xeb22)]
ROOTS=[0xad8c,0xab53,0xe324,0xea4e,0xbb16,0xbb6c]
ALIASES={0xff69:0xe324,0xff6c:0xea4e}
DATA=[(0xda09,0xda71),(0xfec8,0xff00)]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,s:p.write_text(s,encoding='utf-8',newline='\n')
inside=lambda a:any(lo<=a<hi for lo,hi in SPANS)
label=lambda a:f'Ms_{a:04X}'

def graph():
    c=M.machine();c.memory.regs[6:8]=[0,1];c.memory.map();d=Disassembler(c)
    code={};todo=ROOTS[:];external={};ram={};reads={}
    while todo:
        p=todo.pop()
        if p in code:continue
        assert inside(p),hex(p)
        n,t=d.instruction_at(p);mn,mode=c.disassemble[c.memory[p]]
        assert t!='???',(hex(p),t)
        a=c.memory[p+1]+(256*c.memory[p+2]if n==3 else 0)if n>1 else None
        code[p]=dict(bytes=list(c.memory[p:p+n]),size=n,text=t,mnemonic=mn,mode=mode,operand=a)
        if mn in ['JSR','JMP']:
            assert mode=='abs',(hex(p),t)
            if inside(a):todo.append(a)
            elif a in ALIASES:todo.append(ALIASES[a])
            else:external.setdefault(a,[]).append(p)
        elif mode=='rel':todo.append((p+2+(a if a<128 else a-256))&65535)
        elif mode in ['zpg','zpx','zpy','abs','abx','aby','iny','inx','ind']:
            (ram if a<0x8000 else reads).setdefault(a,[]).append(dict(pc=p,mnemonic=mn,mode=mode))
        if mn not in ['RTS','RTI','JMP']:todo.append(p+n)
    occupied={}
    for p,z in code.items():
        for a in range(p,p+z['size']):assert a not in occupied,(hex(a),hex(p));occupied[a]=p
    assert all(inside(a)or any(lo<=a<hi for lo,hi in DATA)for a in reads),[hex(a)for a in reads if not(inside(a)or any(lo<=a<hi for lo,hi in DATA))]
    return c,code,external,ram,reads

def emit(c,code,external,portable):
    result=[]
    for lo,hi in SPANS:
        p=lo
        while p<hi:
            if p not in code:result.append(f'{label(p)}: .byte ${c.memory[p]:02x}');p+=1;continue
            z=code[p];t=z['text'];mn=z['mnemonic'];mode=z['mode'];a=z['operand']
            if mode=='rel':
                target=(p+2+(a if a<128 else a-256))&65535
                t=mn.lower()+' '+label(target)
                if portable:t='j'+t[1:]
            elif mode in ['abs','abx','aby','zpg','zpx','zpy','inx','iny','ind']:
                if mn in ['JSR','JMP']:
                    target=label(a)if inside(a)else f'MsAlias_{a:04X}'if a in ALIASES else f'MsExternal_{a:04X}'
                elif portable:
                    if inside(a)or any(lo<=a<hi for lo,hi in DATA):target=label(a)
                    elif a in [0x6e,0x6f]:target='MsPointer'+(''if a==0x6e else'+1')
                    else:target=f'MsState+${a:04x}'
                else:target=f'${a:04x}'if z['size']==3 else f'${a:02x}'
                old=re.search(r'\$[0-9a-fA-F]+',t);assert old
                t=t[:old.start()]+target+t[old.end():]
                if not portable and z['size']==3 and a<256:t=t.replace(target,'a:'+target,1)
                if portable and(mn,mode)in [('STY','zpx'),('STX','zpy')]:
                    tr='TYA'if mn=='STY'else'TXA';suffix=',X'if mn=='STY'else',Y'
                    t='PHP\n PHA\n '+tr+'\n STA '+target+suffix+'\n PLA\n PLP'
            result.append(f'{label(p)}: {t} ; donor ${p:04x}');p+=z['size']
    return '\n'.join(result)+'\n'

def main():
    OUT.mkdir(exist_ok=True);s=OUT/'source';s.mkdir(exist_ok=True)
    c,code,external,ram,reads=graph();donor=M.donor()
    write(s/'original-actor.inc',emit(c,code,external,False));write(s/'portable-actor.inc',emit(c,code,external,True))
    # Reproduce all selected32KiB, keeping every gap exact, while the actor is semantic source.
    selected=bytes(c.memory[0x8000:]);(OUT/'donor-selected.bin').write_bytes(selected)
    original=''.join(f'MsExternal_{a:04X}=${a:04x}\n'for a in external)+''.join(f'MsAlias_{a:04X}=${a:04x}\n'for a in ALIASES)
    # Included spans are contiguous in the semantic include. Give each span its own segment.
    source=emit(c,code,external,False)
    for i,(lo,hi)in enumerate(SPANS):source=source.replace(label(lo)+':',f'.segment "PART{i}"\n'+label(lo)+':',1)
    write(s/'original-actor.inc',source)
    original='.setcpu "6502"\n'+original+''.join(f'.segment "GAP{i}"\n.incbin "../donor-selected.bin",${lo-0x8000:x},${hi-lo:x}\n'for i,(lo,hi)in enumerate([(0x8000,SPANS[0][0]),(SPANS[0][1],SPANS[1][0]),(SPANS[1][1],SPANS[2][0]),(SPANS[2][1],0x10000)]))+'.include "original-actor.inc"\n'
    write(s/'reproduce.s',original)
    cuts=[(0x8000,0xab53,'GAP0'),(0xab53,0xbcad,'PART0'),(0xbcad,0xe324,'GAP1'),(0xe324,0xe32b,'PART1'),(0xe32b,0xea4e,'GAP2'),(0xea4e,0xeb22,'PART2'),(0xeb22,0x10000,'GAP3')]
    write(s/'reproduce.cfg','MEMORY{'+''.join(f'{n}:start=${lo:x},size=${hi-lo:x},file=%O;'for lo,hi,n in cuts)+'}\nSEGMENTS{'+''.join(f'{n}:load={n},type=ro;'for _,_,n in cuts)+'}\n')
    portable='.setcpu "6502"\n.macpack longbranch\nMsState=$6000\nMsPointer=$00\nMsSaved0=MsState+$7fe\nMsSaved1=MsState+$7ff\n.segment "CODE"\n'
    portable+=''.join(f'MsExternal_{a:04X}=${0x5000+3*i:04x}\n'for i,a in enumerate(sorted(external)))
    portable+=''.join(f'MsAlias_{a:04X}: jmp {label(b)}\n'for a,b in ALIASES.items())
    portable+='.include "portable-actor.inc"\n'
    for lo,hi in DATA:
        for a in range(lo,hi):portable+=f'{label(a)}: .byte ${c.memory[a]:02x}\n'
    # Two borrowed host ZP bytes only; save/restore on every public actor entry.
    for name,pc in [('Frame',0xad8c),('Horizontal',0xac2f),('Gravity',0xe324),('JumpClock',0xea4e),('IntegrateY',0xac84),('Walls',0xbb08),('Support',0xb744)]:
        portable+=f'''.export Ms{name}
Ms{name}:
 lda MsPointer
 sta MsSaved0
 lda MsPointer+1
 sta MsSaved1
 jsr {label(pc)}
Ms{name}Result:
 php
 pha
 lda MsSaved0
 sta MsPointer
 lda MsSaved1
 sta MsPointer+1
 pla
 plp
 rts
'''
    portable+='MsEnd:\n.export MsEnd,MsState,MsPointer\n';write(s/'portable.s',portable)
    write(s/'portable.cfg','MEMORY{LAB:start=$9000,size=$3000,file=%O,fill=yes,fillval=$ff;}SEGMENTS{CODE:load=LAB,type=ro;}\n')
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    for mode in ['reproduce','portable']:
        for command in [[cc/'ca65.exe','-g','-I',s,s/(mode+'.s'),'-o',OUT/(mode+'.o')],[cc/'ld65.exe','-C',s/(mode+'.cfg'),OUT/(mode+'.o'),'-o',OUT/(mode+'.bin'),'--dbgfile',OUT/(mode+'.dbg'),'-Ln',OUT/(mode+'.lbl')]]:
            command=list(map(str,command));guard=validate(command,OUT,cwd=s);q=subprocess.run(command,cwd=s,capture_output=True,text=True);commands.append(dict(command=command,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    assert(OUT/'reproduce.bin').read_bytes()==selected
    save(OUT/'build-commands.json',commands)
    result=dict(passed=True,source_CPU_component=True,native=False,installed=False,donor_sha256=M.EXPECTED,source_spans=SPANS,source_bytes=sum(hi-lo for lo,hi in SPANS),recovered_instructions=len(code),entire_selected32KiB_reproduced=True,private_state=[0x6000,0x6800],borrowedZP=[0,2],external_callbacks={f'{a:04X}':x for a,x in external.items()},portable_callbacks={f'{a:04X}':0x5000+3*i for i,a in enumerate(sorted(external))},ram_fields={f'{a:04X}':x for a,x in ram.items()},rom_reads={f'{a:04X}':x for a,x in reads.items()},scope='Original player frame, movement, jump/gravity inversion, aim/shoot spawn and collision response instructions. External tile, scene, moving-platform, rendering and sound APIs require explicit host adapters. Two ZP bytes are borrowed/restored; no grant or host admission.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),M.ROM,Path(M.__file__),ROOT/'tools/audit/verify_native_relocation.py',ROOT/'tools/audit/private_build_outputs_v1.py',cc/'ca65.exe',cc/'ld65.exe',OUT/'portable.bin',OUT/'portable.dbg',OUT/'reproduce.bin',OUT/'build-commands.json',*[p for p in s.iterdir()if p.is_file()]]})
    save(OUT/'assembly.json',result);print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','ram_fields','rom_reads','external_callbacks']}))

if __name__=='__main__':main()
