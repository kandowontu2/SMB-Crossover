"""In-memory assembly only under the exact 449-byte source research lease.

No packet reconstruction, gameplay overlay, native runner or file outputs.
"""
from hashlib import sha256
import json,re
from pathlib import Path
from py65.assembler import Assembler
from py65.devices.mpu6502 import MPU
import prince_worldmaterial_fit_1114 as Old

R=Old.Packet.R
LEASE=R/'docs/qa/allocations/prince-worldmaterial-research-1114.json'
LEASE_SHA='0731c7526f8f181b33855ce7d09d3992f1ec29bea30f2c677c0ea6453a9ec482'
SOURCE=R/'tools/reference/prince_worldmaterial_research_1114.s'
BRANCHES={'bcc':'bcs','bcs':'bcc','beq':'bne','bne':'beq','bmi':'bpl','bpl':'bmi','bvc':'bvs','bvs':'bvc'}


def parent(raw):
    """Explicit delivered-common82 boundary; old frozen inputs stay strict."""
    import compose_shared_world_chr_reset_1114 as Reset
    if sha256(raw).hexdigest()==Reset.CANDIDATE:return Reset.inverse(raw)
    assert sha256(raw).hexdigest()==Old.F.PIN
    return raw


def assemble(text,symbols,*,origin=Old.START):
    lines=[q.split(';',1)[0].strip()for q in text.splitlines()]
    lines=[q for q in lines if q and not q.startswith('.')]
    sizes=[0 if q.endswith(':')else 5 if q.split()[0]in BRANCHES else 3 for q in lines]
    labels=dict(symbols);asm=Assembler(MPU())
    def render(q):
        q=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',lambda m:f'${labels[m[1]]:04x}'if m[1]in labels else m[0],q)
        q=re.sub(r'\$([0-9a-fA-F]+)\+(\d+)',lambda m:f'${int(m[1],16)+int(m[2]):04x}',q)
        return re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',q)
    for _ in range(30):
        pc=origin
        for q,size in zip(lines,sizes):
            if q.endswith(':'):labels[q[:-1]]=pc
            pc+=size
        out=bytearray();new=[];branches=[]
        for q in lines:
            pc=origin+len(out)
            if q.endswith(':'):new.append(0);continue
            op=q.split()[0]
            if op in BRANCHES:
                target=labels[q.split()[1]];delta=target-(pc+2)
                if -128<=delta<=127:code=asm.assemble(render(q),pc=pc)
                else:code=asm.assemble(f'{BRANCHES[op]} ${pc+5:04x}',pc=pc)+asm.assemble(f'jmp ${target:04x}',pc=pc+2)
                branches.append([pc,target,len(code)])
            else:code=asm.assemble(render(q),pc=pc)
            out.extend(code);new.append(len(code))
        if sizes==new:break
        sizes=new
    else:raise AssertionError('Assembly did not converge')
    assert labels['PpWorldTile']==origin and labels['PpWorldTileY']==origin+3
    for pc,target,size in branches:
        if size==2:
            delta=out[pc-origin+1];decoded=pc+2+delta-(256 if delta&128 else 0)
            assert decoded==target
    return bytes(out),labels,branches


def build(raw):
    assert sha256(LEASE.read_bytes()).hexdigest()==LEASE_SHA
    raw=parent(raw);q=Old.inspect(raw)
    assert q['rebuild_exact']and q['preimage_SHA256']=='c4377287449f719ccbc64a2721c9b6039c784566173114080881deced7ef088d'
    _,symbols=Old.source();code,labels,branches=assemble(SOURCE.read_text(),symbols)
    return code,labels,dict(parent_SHA256=sha256(raw).hexdigest(),lease_SHA256=LEASE_SHA,
        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(),code_SHA256=sha256(code).hexdigest(),
        assembled_bytes=len(code),leased_bytes=449,fit=len(code)<=449,
        excess_bytes=max(0,len(code)-449),short_branches=sum(q[2]==2 for q in branches),
        long_branches=sum(q[2]==5 for q in branches),entry_PC=[hex(labels[q])for q in('PpWorldTile','PpWorldTileY')],
        no_mount_or_semantic_qualification=True,outputs=0,Mesen=False)


if __name__=='__main__':print(json.dumps(build(Old.F.ROM.read_bytes())[2],separators=(',',':')),flush=True)
