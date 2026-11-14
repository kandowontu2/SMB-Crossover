"""Exact source reconstruction and anchor census of current WorldMaterial.

No code allocation, mutation, ROM composition or ordinary gameplay overlay.
"""
from hashlib import sha256
import json,re
from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import prince_cold_packet_1111 as Packet
import replay_prince_pipe_usability_1114 as F

START,END=0xbde2,0xbfa3
SOURCE=Packet.R/'tools/reference/prince_host_world_1102_v8.s'


def source():
    text=SOURCE.read_text()
    symbols={n:int(a,16)for n,a in re.findall(r'(?m)^([A-Za-z_][A-Za-z_0-9]*)=\$([0-9a-fA-F]+)',text)}
    symbols.update(Prepare=0xc552,PpHostReadPoint=0xb310,Hand=0xa49a,PpQueryX=0xb369,PpQueryY=0xb36b)
    text=text.split('.segment "WORLD_MATERIAL"',1)[1].split('.segment "WORLD_ALIGN"',1)[0]
    # Exactly the two delivered transformations inside this owned function.
    assert text.count(' bcc AboveRow')==1;text=text.replace(' bcc AboveRow',' bmi AboveRow')
    assert text.count(' jsr PpHostReadPoint')==3
    text=text.replace(' jsr PpHostReadPoint',' jsr Hand',1)
    return text,symbols


def assemble(text,symbols):
    lines=[];serial=0
    inverse={'jcc':'bcs','jcs':'bcc','jne':'beq'}
    raw_lines=[raw.split(';',1)[0].strip()for raw in text.splitlines()]
    anonymous=[i for i,line in enumerate(raw_lines)if line==':']
    for index,line in enumerate(raw_lines):
        if not line or line.startswith('.'):continue
        if line==':':line=f'Anonymous{index}:'
        if ':+'in line:
            following=next(i for i in anonymous if i>index)
            line=line.replace(':+',f'Anonymous{following}')
        op=line.split()[0].lower()
        if op in inverse:
            name=f'LongSkip{serial}';serial+=1
            lines.extend((inverse[op]+' '+name,'jmp '+line.split()[1],name+':'))
        else:lines.append(line)
    labels={q[:-1]:START for q in lines if q.endswith(':')};labels.update(symbols)
    asm=Assembler(MPU())
    for _ in range(6):
        out=bytearray()
        for line in lines:
            if line.endswith(':'):labels[line[:-1]]=START+len(out);continue
            line=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',lambda m:f'${labels[m[1]]:04x}'if m[1]in labels else m[0],line)
            line=re.sub(r'\$([0-9a-fA-F]+)\+(\d+)',lambda m:f'${int(m[1],16)+int(m[2]):04x}',line)
            line=re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',line)
            out.extend(asm.assemble(line,pc=START+len(out)))
    return bytes(out),labels


def inspect(raw):
    assert sha256(raw).hexdigest()==F.PIN
    _,chunks,_=Packet.extract(raw);before=chunks[0][START-0xa000:END-0xa000]
    text,symbols=source();rebuilt,labels=assemble(text,symbols)
    diff=[i for i,(a,b)in enumerate(zip(before,rebuilt))if a!=b]
    refs=[]
    for k,c in enumerate(chunks):
        origin=(0xa000,0xc800,0xc100)[k]
        for i in range(len(c)-1):
            target=int.from_bytes(c[i:i+2],'little')
            if START<=target<END and not(k==0 and START<=origin+i<END):
                refs.append(dict(stream=k,at=hex(origin+i),target=hex(target)))
    memory=[0]*65536
    for origin,c in zip((0xa000,0xc800,0xc100),chunks):memory[origin:origin+len(c)]=c
    aliases={0xa87d:'8dbfc4',0xaa0b:'8dbfc4',0xae75:'8dbfc4',0xaea0:'8dbfc4',
        0xaebc:'6dbfc4',0xb1ef:'8dbfc4',0xbc4d:'a9be',0xd9d6:'20bedd',0xde4a:'b5be'}
    for r in refs:
        target=int(r['target'],16);pc=int(r['at'],16)
        if target in(START,START+3):
            assert memory[pc-1]==0x20,(r,'Unclassified public entry reference')
            r['classification']='JSR public entry'
        else:
            expected=bytes.fromhex(aliases[pc]);assert bytes(memory[pc:pc+len(expected)])==expected
            r['classification']='Opcode/operand overlap; not an address operand'
    d=Disassembler(MPU(memory=memory));incoming=[];nearby=[]
    # Any outside relative branch reaching the function must start within
    # 128 bytes. The nearby executable prefix ends at BDA2; the following
    # BDA2..BDE2 is bounded renderer data. Cold code starts exactly at BFA3.
    for first,last in((0xbd4b,0xbda2),(END,0xbfdf)):
        pc=first;branches=[]
        while pc<last:
            size,instruction=d.instruction_at(pc);assert instruction!='???',hex(pc)
            if memory[pc]&31==16:
                rel=memory[pc+1];dest=(pc+2+rel-(256 if rel&128 else 0))&65535
                branches.append([hex(pc),hex(dest)])
                if START<=dest<END:incoming.append([pc,dest])
            pc+=size
        assert pc==last,(hex(pc),hex(last))
        nearby.append(dict(half_open=[hex(first),hex(last)],relative_branches=branches))
    assert not incoming
    assert memory[0xbda1]==0x60 and memory[END]==0x4c
    original=(Packet.R/'build/prince-actor-1101-v1/contact-core.bin').read_bytes()
    assert chunks[0][0x1400:0x1ae5]==original[0x1400:0x1ae5]
    command=[int.from_bytes(chunks[0][i:i+2],'little')for i in range(0x1ba1,0x1ba1+30,2)]
    assert all(not START<=dest<END for dest in command)
    return dict(ROM_SHA256=F.PIN,function_half_open=[hex(START),hex(END)],bytes=len(before),
        preimage_SHA256=sha256(before).hexdigest(),source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),
        rebuilt_bytes=len(rebuilt),rebuild_exact=before==rebuilt,
        first_difference_offsets=diff[:12],external_literal_word_candidates=refs,
        outside_relative_ingress=incoming,nearby_executable_boundaries=nearby,
        preceding_renderer_data_half_open=['0xbda2','0xbde2'],
        original_scripts_half_open=['0xb400','0xbae5'],
        original_scripts_exact=True,script_SHA256=sha256(chunks[0][0x1400:0x1ae5]).hexdigest(),
        current_command_targets=[hex(q)for q in command],script_indirect_targets_outside_function=True,
        declared_entries=dict(PpWorldTile=hex(START),PpWorldTileY=hex(START+3)),
        constructor_boundary=hex(END),grant=False,outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(inspect(F.ROM.read_bytes()),separators=(',',':')),flush=True)
