"""Detached current67-byte point proposal; no ROM composition/game overlay."""
from hashlib import sha256
from pathlib import Path
import argparse,json,re,struct
from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU
import current_prince_stock_174fa_1115 as Current

R,C,N,W=Current.C.R,Current.C,Current.N,Current.W
START,END=0xb310,0xb353
FIELDS=dict(PpQueryX=0xb369,PpQueryY=0xb36b,Raw=0xb36d,BlockBufferAddr=0x95d8,Block_Buffer_1=0x300,MTileAttribute=0xef36,ChkInvisibleMTiles=0x9eca,ReadLow=START)
H=lambda b:sha256(b).hexdigest()

def assemble(text):
    lines=[]
    for raw in text.replace('Read:lda','Read:\n lda').splitlines():
        line=raw.split(';',1)[0].strip()
        if line and not line.startswith('.'):lines.append(line)
    labels={line[:-1]:START for line in lines if line.endswith(':')};labels.update(FIELDS)
    a=Assembler(MPU())
    for _ in range(6):
        labels['ReadLow']=labels['Read']+1
        out=bytearray()
        for line in lines:
            if line.endswith(':'):labels[line[:-1]]=START+len(out);continue
            line=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',lambda m:f'${labels[m[1]]:04x}'if m[1]in labels else m[0],line)
            line=re.sub(r'\$([\da-fA-F]+)\+(\d+)',lambda m:f'${int(m[1],16)+int(m[2]):04x}',line)
            line=re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',line)
            out.extend(a.assemble(line,pc=START+len(out)))
    return bytes(out),labels

def arrays(raw):
    Current.reference(raw);head,parts,lengths=C.Packet.extract(raw)
    source=(R/'tools/reference/prince_point_read_compact_1110_v6.s').read_text();text=source
    old,labels=assemble(text);assert len(old)==67 and old==parts[0][START-0xa000:END-0xa000]
    before=''' lda $b36a
 and #1
 tax
 lda $b369
 lsr a
 lsr a
 lsr a
 lsr a
 clc
 adc BlockBufferAddr,x
 sta ReadLow'''
    after=''' lda $b36a
 lsr a
 lda $b369
 ror a
 lsr a
 cmp #64
 ror a
 cmp #128
 ror a
 clv
 sta ReadLow'''
    assert text.count(before)==1;text=text.replace(before,after,1)
    assert text.count(' txa\n pha\n tya\n pha')==1;text=text.replace(' txa\n pha\n tya\n pha',' tya\n pha',1)
    assert text.count(' pla\n tay\n pla\n tax')==1;text=text.replace(' pla\n tay\n pla\n tax',' pla\n tay',1)
    before='''Read:
 lda Block_Buffer_1,y
 tax
 lda MTileAttribute,x
 lsr a
 txa'''
    after='''Read:
 lda Block_Buffer_1,y
 jsr ChkInvisibleMTiles
 beq Empty
 tay
 lda MTileAttribute,y
 lsr a
 tya'''
    assert text.count(before)==1;text=text.replace(before,after,1)
    proposed,newlabels=assemble(text);assert len(proposed)==67 and proposed[-1]==old[-1]==0x60
    # This only constructs proposed decoded arrays for sizing. It never
    # creates a ROM, mounts a NesBus array, or writes a packet/carrier.
    chunks=list(parts);runtime=bytearray(chunks[0]);runtime[START-0xa000:END-0xa000]=proposed;chunks[0]=bytes(runtime)
    packed=tuple(map(C.Packet.encode,chunks));sizes=tuple(map(len,packed))
    header=bytearray(head);fields=struct.unpack_from('<12H',header,len(header)-54)
    assert fields[2]==lengths[0] and sizes[1:]==lengths[1:]
    struct.pack_into('<H',header,len(header)-54+4,sizes[0]);payload=bytes(header)+b''.join(packed)
    assert len(payload)<=45*1024
    # Read the actual owning native ROM constants through their exact bank.
    bundle=dict(W.Symbols.bundle(),raw=raw);where=W.location(bundle,'BlockBufferAddr')
    assert W.address(bundle,'BlockBufferAddr')==0x95d8 and raw[where:where+2]==bytes((0,208))
    invisat=W.location(bundle,'ChkInvisibleMTiles');invisible=raw[invisat:invisat+7]
    assert W.address(bundle,'ChkInvisibleMTiles')==0x9eca and(invisat-16)//8192==126 and invisible==bytes.fromhex('c95ff002c96060')
    attrat=W.location(bundle,'MTileAttribute');assert W.address(bundle,'MTileAttribute')==0xef36
    attrs=raw[attrat:attrat+256];assert len(attrs)==256 and attrs[95]&1 and attrs[96]==65
    refs=[]
    for stream,part in enumerate(parts):
        for i in range(len(part)-1):
            target=int.from_bytes(part[i:i+2],'little')
            if START<=target<END and not(stream==0 and START-0xa000<=i<END-0xa000):
                refs.append(dict(stream=stream,decoded_offset=i,target=target,preceding=part[max(0,i-1):i+3].hex()))
    aliases={(0,1175):'184cb3a4',(0,4314):'1820b3d7',(1,6001):'684cb3c7'}
    for row in refs:
        key=(row['stream'],row['decoded_offset'])
        if row['target']==START:
            assert parts[key[0]][key[1]-1]in(0x20,0x4c)
            row['classification']='Unchanged public JSR/JMP B310'
        else:
            assert aliases[key]==row['preceding']
            row['classification']='JMP/JSR opcode plus low operand; actual target outside point'
    assert sum(row['target']!=START for row in refs)==3
    relatives=[]
    for lo,hi in((START-128,START),(END,END+126)):
        for pc in range(lo,hi):
            opcode=parts[0][pc-0xa000]
            if opcode&31!=16:continue
            displacement=parts[0][pc+1-0xa000];target=(pc+2+displacement-(256 if displacement&128 else 0))&65535
            if START<=target<END:relatives.append(dict(PC=pc,opcode=opcode,target=target))
    assert relatives==[dict(PC=0xb356,opcode=0x90,target=0xb352),dict(PC=0xb35b,opcode=0xf0,target=0xb352)],relatives
    commands=[int.from_bytes(parts[0][i:i+2],'little')for i in range(0x1ba1,0x1ba1+30,2)]
    assert len(commands)==15 and all(not START<=x<END for x in commands)
    info=dict(passed=True,ROM_SHA256=Current.PIN,decoded_stream=0,live_half_open=[START,END],owned_code_bytes=67,old_SHA256=H(old),proposed_SHA256=H(proposed),old_hex=old.hex(),proposed_hex=proposed.hex(),assembled_bytes=67,pad_bytes=0,changed_bytes=sum(a!=b for a,b in zip(old,proposed)),funding='Exact00/D0 column math including CLV saves1 byte; Y holds raw tile so X is never modified and its save/restore saves4; existing native ChkInvisibleMTiles call/BEQ costs5',fixed_fields={k:v for k,v in FIELDS.items()if k!='ReadLow'},old_Read=labels['Read'],new_Read=newlabels['Read'],old_SMC_low_operand=labels['Read']+1,new_SMC_low_operand=newlabels['Read']+1,live_probe_entry=0xb353,shared_RTS_anchor=0xb352,unchanged_probe_padding_and_fields_SHA256=H(parts[0][0x1353:0x136e]),native_BlockBufferAddr=[0,208],native_invisible_filter=dict(bank=126,PC=0x9eca,bytes=invisible.hex()),native_invisible_attributes=[attrs[95],attrs[96]],classified_absolute_references=refs,conservative_all_byte_relative_ingress=relatives,source_command_targets15_exclude_point=True,command_table_SHA256=H(parts[0][0x1ba1:0x1bbf]),packed_sizes=sizes,old_packed_sizes=lengths,head_words_changed=[2]if sizes[0]!=lengths[0]else[],spare=45*1024-len(payload),hypothetical_cookie=C.Packet.cookie(chunks,payload).hex(),ROM_composed=False,NesBus_mounted=False,new_resources=0,outputs=0,Mesen=False)
    return old,proposed,labels,newlabels,attrs,invisible,info

class Flat(list):
    def __setitem__(self,key,value):
        if isinstance(key,int):self.changed.add(key)
        return super().__setitem__(key,value)

def primitive(raw):
    old,new,ol,nl,attrs,invisible,info=arrays(raw);arenas=[]
    for code in(old,new):
        m=Flat([0]*65536);m.changed=set();m[START:END]=code;m[0x95d8:0x95da]=[0,208];m[0xef36:0xf036]=attrs;m[0x9eca:0x9ed1]=invisible;arenas.append(m)
    coords=((0,32),(15,47),(16,48),(255,239),(256,32),(511,239),(512,32),(65535,239))
    flags=(0x20,0x21,0x28,0x29,0x60,0x61,0x68,0x69);cases=0;changed=0;cycles=[];trace=sha256()
    def invoke(index,x,y,tile,p):
        m=arenas[index];lab=(ol,nl)[index]
        m[0x300:0x4a0]=[0]*416;m[0xb369:0xb36d]=[x&255,x>>8,y&255,y>>8]
        if 32<=y<=239:m[0x300+(208 if(x>>8)&1 else 0)+((x&255)>>4)+(y&240)-32]=tile
        c=N.NesMPU(memory=m,pc=START);c.a,c.x,c.y,c.p,c.sp=83,(tile*7+x)&255,(tile*11+y)&255,p,224
        original=(c.x,c.y);c.stPushWord(0x5aff);protected=bytes(m[0x1df:0x200]);m.changed.clear()
        for _ in range(128):
            if c.pc==0x5b00:break
            assert m[c.pc];c.step()
        else:raise AssertionError('Detached point primitive bound')
        assert(c.x,c.y,c.sp)==(*original,224)and bytes(m[0x1df:0x200])==protected
        allowed={lab['Read']+1,0xb36d}|set(range(0x100,0x200));assert m.changed<=allowed
        assert bytes(m[0xb369:0xb36d])==bytes((x&255,x>>8,y&255,y>>8))
        if 32<=y<=239:assert m[lab['Read']+1]==((208 if(x>>8)&1 else 0)+((x&255)>>4))and m[lab['Read']+2]==3
        return(c.a,c.x,c.y,c.p,c.sp,c.processorCycles)
    def compare(x,y,tile,p):
        nonlocal cases,changed
        a,b=invoke(0,x,y,tile,p),invoke(1,x,y,tile,p)
        intended=32<=y<=239 and tile in(95,96)
        if intended:
            assert b[0]==0 and not(b[3]&1)and a[0]==tile and a[3]&1
            assert a[1:3]==b[1:3]and(a[3]&~0x83)==(b[3]&~0x83)and a[4]==b[4];changed+=1
        else:assert a[:5]==b[:5],(x,y,tile,p,a,b)
        cycles.append(b[5]-a[5]);trace.update(bytes((tile,p,a[0],b[0],a[3],b[3])));cases+=1
    for x,y in coords:
        for tile in range(256):
            for p in flags:compare(x,y,tile,p)
    for x in range(512):
        for p in(0x20,0x60):compare(x,32,17,p)
    for y in(0,15,31,240,255,256,65535):
        for tile in(0,17,95,96,255):
            for p in flags:compare(65535,y,tile,p)
    info.update(flat_primitive_only=True,primitive_cases=cases,intended_hidden_cases=changed,coordinate_classes=512,all16bit_X_reduce_to512_parity_classes=True,other_tiles_and_invalid_bounds_exact=True,registers_flags_stack_and_write_domain_exact_except_declared_hidden_ACNZ=True,cycle_delta_range=[min(cycles),max(cycles)],primitive_trace_SHA256=trace.hexdigest())
    return info

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--primitive',action='store_true');a=p.parse_args()
    raw=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    q=primitive(raw)if a.primitive else arrays(raw)[-1]
    q['receipt_SHA256']=H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());print(json.dumps(q,separators=(',',':')),flush=True)
