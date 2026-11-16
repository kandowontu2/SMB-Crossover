"""Read installed packet/producer targets only; no CPU or proposed overlay."""
from hashlib import sha256
from pathlib import Path
import json,re
import plan_jay_status_publication_00bb_1116 as Plan

H=Plan.H
PAGES=(371,375,379,336,338,167,304,306,307)


def primary(raw):
    stage=raw[1048592+331*1024:1048592+333*1024]
    assert stage[606:609]==bytes.fromhex('4c00a0')
    packed=stage[:606]+stage[609:];at=257;out=bytearray()
    while len(out)<0x8c0:
        flags=packed[at];at+=1
        for bit in range(8):
            if len(out)==0x8c0:break
            if flags&(1<<bit):
                lo,hi=packed[at:at+2];at+=2;distance=lo+((hi>>4)<<8);n=(hi&15)+3
                assert 0<distance<=len(out)
                for _ in range(n):out.append(out[-distance])
            else:out.append(packed[at]);at+=1
            assert len(out)<=0x8c0
    assert at==2045 and H(out)=='81902bfd3f641209e2c47749fbd14377203112545a3f945f9b9b1ba6c70db092'
    return bytes(out)


def packet(raw):
    page=lambda p:raw[1048592+p*1024:1048592+(p+1)*1024]
    stream=b''.join(map(page,PAGES))+page(739)[192:]
    head=stream[:941]
    assert head[925:941]==Plan.COOKIE
    # Authenticate the installed NextBlock reader and derive its actual table.
    sites=[i for i in range(80,925-32)if head[i]==174 and head[i+3]==189 and head[i+6:i+9]==bytes.fromhex('8503bd')]
    assert sites==[666]
    site=sites[0];tablepc=int.from_bytes(head[site+4:site+6],'little')
    tableat=80+tablepc-0xb850
    assert tablepc==0xbb2f and tableat==815
    table=head[tableat:925];assert len(table)==110
    rows=[(int.from_bytes(table[i:i+2],'little'),table[i+2],int.from_bytes(table[i+3:i+5],'little'))for i in range(0,len(table),5)]
    assert len(rows)==22 and all(bank in(1,2,3)and 0xc000<=pc<0xe000 and pc+n<=0xe000 for pc,bank,n in rows)
    assert head[258:268].hex()=='a9ad850aa9038dcfba20'
    offset=0x3ad;assert offset==941
    dictionary=stream[offset:offset+16];tokens=int.from_bytes(stream[offset+16:],'little');bits=0
    def take(n):
        nonlocal tokens,bits
        result=tokens&((1<<n)-1);tokens>>=n;bits+=n;return result
    total=sum(n for _,_,n in rows);out=bytearray()
    while len(out)<total:
        if take(1):
            lo,hi=take(8),take(8);distance=lo+((hi&240)<<4);n=(hi&15)+3
            assert 0<distance<=len(out)and len(out)+n<=total
            for _ in range(n):out.append(out[-distance])
        else:out.append(dictionary[take(4)]if take(1)else take(8))
    consumed=offset+16+(bits+7)//8
    assert all(v==255 for v in stream[consumed:])
    blocks=[];at=0
    for pc,bank,n in rows:blocks.append((bank,pc,bytes(out[at:at+n])));at+=n
    return head,blocks,dict(rows=[dict(bank=b,PC=p,bytes=n)for p,b,n in rows],decoded_bytes=total,
        decoded_SHA256=H(out),cold941_SHA256=H(head),table_PC=tablepc,table_SHA256=H(table),consumed=consumed)


def run(raw):
    assert H(raw)==Plan.PIN
    planned=Plan.descriptor(raw)
    page=lambda p:raw[1048592+p*1024:1048592+(p+1)*1024]
    head,blocks,codec=packet(raw)
    # Logical runtime A-window views. Raw3 C-window aliases have +2000.
    domains=[('Jay primary',3,0xa000,primary(raw)),('Jay services',3,0xafc0,page(218)),
        ('shotgun/support',3,0xb400,page(222)),('motion',3,0xb800,page(232)),('extra',3,0xbc00,page(234))]
    domains += [('scatter'+str(i),bank,pc-0x2000,data)for i,(bank,pc,data)in enumerate(blocks)]
    domains += [('Steve cold boot',3,0xa000,head[:64]),
                ('Steve cold',1,0xb850,head[80:])]
    # One complete installed-byte audit, never a raw-ROM graphics call scan.
    # All words into the retired/moved intervals are retained for classification.
    intervals=((0xb828,0xb832),(0xbed7,0xbedf),(0xd828,0xd832),(0xded7,0xdedf))
    words=[];controls=[];branches=[]
    for name,bank,origin,data in domains:
        for i in range(len(data)-1):
            target=int.from_bytes(data[i:i+2],'little')
            if any(lo<=target<hi or lo<=target+1<hi for lo,hi in intervals):
                words.append(dict(domain=name,bank=bank,PC=origin+i,target=target,around=data[max(0,i-3):i+5].hex()))
        for i in range(len(data)-2):
            if data[i]in(0x20,0x4c,0x6c):
                target=int.from_bytes(data[i+1:i+3],'little')
                if any(lo<=target<hi for lo,hi in intervals):controls.append(dict(domain=name,bank=bank,PC=origin+i,target=target,opcode=data[i]))
            if data[i]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                d=data[i+1];target=origin+i+2+(d if d<128 else d-256)
                if any(lo<=target<hi for lo,hi in intervals):branches.append(dict(domain=name,bank=bank,PC=origin+i,target=target,opcode=data[i],around=data[max(0,i-2):i+4].hex()))
    # Named producer/reference labels and exports in the exact admitted family.
    paths=sorted(set((Plan.R/'tools/reference').glob('jay_silius*.s'))|set((Plan.R/'tools/reference').glob('steve*.s')))
    source_hits=[]
    for p in paths:
        for lineno,line in enumerate(p.read_text().splitlines(),1):
            if re.search(r'\bUnsupported\b|\$(?:b83[01]|bed[7-9a-e]|d83[01]|ded[7-9a-e])\b',line,re.I):
                source_hits.append(dict(path=p.relative_to(Plan.R).as_posix(),line=lineno,text=line.strip()))
    assert controls==[]
    assert [(r['domain'],r['bank'],r['PC'],r['target'])for r in branches]==[
        ('motion',3,pc,0xb830)for pc in(0xb805,0xb80c,0xb812,0xb818,0xb81d,0xb823)]
    assert [(r['domain'],r['bank'],r['PC'],r['target'])for r in words]==[
        ('scatter7',1,0xa536,0xdedc),('scatter13',2,0xb15d,0xded7),('scatter17',3,0xab4f,0xd827)]
    # Classify every deliberately overinclusive word hit using current bytes,
    # matching source data declarations/instruction boundaries, and bank type.
    armor=blocks[7][2];late=blocks[13][2];companion=blocks[17][2]
    posebytes=bytes((*range(0xc4,0xd4,2),*range(0xda,0xf0,2)))
    assert armor[0x52c]==0x60 and armor[0x52d:0x52d+len(posebytes)]==posebytes
    art=(Plan.R/'tools/audit/steve_armor_art_1112.py').read_text()
    assert 'POSES = (*range(0xc4, 0xd4, 2), *range(0xda, 0xf0, 2))'in art
    assert late[0x15b:0x161].hex()=='9db7d7decdd7'
    assert companion[0x4e:0x51].hex()=='2027d8'
    target=next(data[0x27:0x47]for bank,pc,data in blocks if bank==2 and pc==0xd800)
    assert target.hex()=='a90420cdd5ad6ac9304c2cf6c13016ad0cc9cd70c9ad0dc9ed71c99004c91090'
    # The original call/return edge is intentional; the new BCC goes exactly
    # at its old return PC. There is no other published interior entry.
    assert page(232)[0x25:0x32].hex()=='20e6a7eaeaeaeaeaea90021860'
    assert page(234)[0x2d0:0x2e2].hex()=='881081604c00c2eaeaeaeaeaeaeaea'+'ad7707'
    hotat=16+94*8192+(0xb27f&8191);hot=raw[hotat:hotat+112]
    assert hot.count(bytes.fromhex('a2b38e6d01a9038d6c01205a01'))==1
    direct=head[743:783]
    assert direct.hex()=='00c4030a0000000400c8030b0000000400cc030c0000000400d4020e0000000400d0030f4000bf03'
    assert head[783:815]==bytes((115,119,123,80,82,167,48,50,51,227,222,232,234,75,76,218,
                                1,1,1,1,1,0,1,1,1,2,0,0,0,1,1,0))
    copy=page(222)[0x3c0:]
    assert copy[:22].hex()=='a90085038505a9a48504a9b48506a000a20bb1039105'
    assert bytes.fromhex('d105')in copy and bytes.fromhex('c0e0')in copy and bytes.fromhex('4c00d0')in copy
    # The source declares Unsupported locally only. The old final stage
    # branch was replaced by StageRejected's call before the current six.
    assert all(r['path']=='tools/reference/jay_silius_camera_handoff_1111.s'or
        (r['path']=='tools/reference/jay_silius_machinegun_1111.s'and r['text'].startswith(';'))for r in source_hits)
    classified=[dict(domain='scatter7',kind='ArmorPoseIds BYTE ladder, not a pointer',PC=0xa536,
                    bytes=posebytes.hex(),source='steve_armor_art_1112.py::POSES'),
                dict(domain='scatter13',kind='cross-instruction bytes, not an operand',PC=0xd15d,
                    instructions='D15B STA D7B7,X; D15E DEC D7CD,X',hex='9db7d7decdd7'),
                dict(domain='scatter17',kind='unchanged typed C2 companion call; no raw3 reject/pad target',
                    call_PC=0xab4e,target_bank=2,target_PC=0xd827,target_first32=target.hex(),
                    note='D827 itself is also outside moved B830/B831; widened RTS-minus-one word filter retained it.')]
    out=dict(passed=True,scope='detached prelease private-label/code-data consumer closure only',
        parent_SHA256=H(raw),frozen_plan_SHA256=H(Path(Plan.__file__).read_bytes()),plan_receipt=planned['receipt_SHA256'],
        domains=[dict(name=n,bank=b,PC=p,bytes=len(d),SHA256=H(d))for n,b,p,d in domains],codec=codec,
        target_words_including_RTS_minus1=words,control_operand_candidates=controls,relative_branch_candidates=branches,
        classified_words=classified,allowed_retargets=[dict(bank=3,operand=pc+1,old=0xb830,new=0xb82a)for pc in(0xb805,0xb80c,0xb812,0xb818,0xb81d,0xb823)],
        allowed_dynamic_return=dict(bank=3,call_PC=0xb825,callee=0xa7e6,return_PC=0xb828,
            new_return_instruction='BCC consumes original StageRejected carry'),
        preserved_public_entries=dict(Hot94_private_target='raw3:B303',PrivateUpdate='raw3:B800',Supported='raw3:B832',
            SteveCombat='raw3:BED4 JMP raw2:C200',SteveAttackMain='raw3:BEDF'),
        code_as_data_readers=dict(DirectRows_PC=0xbae7,DirectRows_hex=direct.hex(),SourceRows='222/232/234 -> raw3 C400/C800/CC00',
            transfer='staged A7C0 (row222+3C0) -> B400..BFDF, 11 pages plus224 tail; exact compare after each store',
            transfer64_SHA256=H(copy),original_data_semantics='copy/compare, not a pointer into Unsupported or padding'),
        pointer_tables='Current scatter/direct descriptors, original probe words, armor BYTE pose IDs and code-label publishers do not export Unsupported/pad. No generic private-entry contract admits arbitrary interior PCs.',
        retained_source_label_consumers=source_hits,no_CPU_or_proposed_overlay=True,outputs=0,
        remaining='No proposed-code ABI, IRQ, lifecycle, cold or natural reward claim. Public foreign-Y closure is independent30805c18.')
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(run(Plan.ROM.read_bytes()),separators=(',',':')),flush=True)
