"""Exact current7a80 detached Prince tier2 fit; no ROM or gameplay mount."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,struct
import prince_cold_packet_1111 as Packet
import build_prince_worldmaterial_research_1114 as Assembly

PIN='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'
R=Path(__file__).resolve().parents[2]
PICKUP='''
Pickup:
 lda $c6cf
 beq Done
 lda $34,x
 lsr a
 bne NativePickup
 lda $1f,x
 bpl Done
 bcs Sword
 lda $c6cf
 cmp #5
 bcs Mushroom
 inc $c6cf
 bne Mushroom
Sword:
 txa
 pha
 lda #2
 sta $075b
 lsr a
 sta $c6ee
 lda #91
 jsr $aa51
 pla
 tax
Consume:
 jsr $8d2f
 lda #6
 jsr $98b5
Done:
 sec
 rts
NativeDeathUpdate:
 ldy #3
 bne NativeGo
NativePickup:
 ldy #2
NativeGo:
 jmp $da1b
Mushroom:
 lda $075b
 bne Consume
 inc $075b
 bne Consume
'''

def digest(data):return sha256(data).hexdigest()

def arrays(raw):
    assert isinstance(raw,bytes)and digest(raw)==PIN,'Expected exact current7a80'
    header,parts,sizes=Packet.extract(raw)
    ctor=parts[2][:80]
    assert digest(ctor)=='c988607848391b5f80cbef683e0875d7485178a905ff8b4503fc7d33641f2c01'
    assert ctor[-10:]==b'\x38\x60'+bytes(8)
    newctor=ctor[:-10]+bytes.fromhex('ad5b074a8deec63860')+bytes(1)
    start=0xc65f+(0xc7b3-0xc766)-0xc100
    old=parts[2][start:start+77]
    assert digest(old)=='21cf8aafac46a1e7b430f10ec072649d8e8116121e67fbbc768b98a8e8b600e5'
    code,labels,_=Assembly.assemble(PICKUP,{},origin=0xc7b3,check_entries=False)
    assert len(code)==75 and labels['NativeDeathUpdate']==0xc7eb
    pickup=code+bytes(2)
    # Only the current Prince-owned death-update shim reaches the moved label.
    # The other two absolute-word matches are the constructor cold copy and
    # actual PpNativeInit JSR. A separate ingress proof accompanies this plan.
    shim=0xdf7c-0xc800
    assert parts[1][shim-1:shim+2]==bytes.fromhex('4ceac7')
    rows=[dict(name='HostInit',stream=2,decoded_half_open=[0,80],live_CPU_half_open=[0xc0b0,0xc100],old=ctor,new=newctor),
        dict(name='Pickup and Mushroom helper',stream=2,decoded_half_open=[start,start+77],live_CPU_half_open=[0xc7b3,0xc800],old=old,new=pickup),
        dict(name='Prince death-update JMP low operand',stream=1,decoded_half_open=[shim,shim+1],live_CPU_half_open=[0xdf7c,0xdf7d],old=b'\xea',new=b'\xeb')]
    assert all(len(row['old'])==len(row['new'])for row in rows)
    return header,parts,sizes,rows,labels

def plan(raw):
    header,before,old_sizes,rows,labels=arrays(raw);after=list(map(bytearray,before))
    for row in rows:
        stream=row['stream'];lo,hi=row['decoded_half_open'];after[stream][lo:hi]=row['new']
    for stream,(old,new)in enumerate(zip(before,after,strict=True)):
        owned={at for row in rows if row['stream']==stream for at in range(*row['decoded_half_open'])}
        assert len(old)==len(new)and all(a==b for at,(a,b)in enumerate(zip(old,new,strict=True))if at not in owned)
    parts=tuple(map(bytes,after));packed=tuple(map(Packet.encode,parts));sizes=tuple(map(len,packed))
    newhead=bytearray(header);config=len(header)-54;words=struct.unpack_from('<12H',header,config)
    newwords=(0xc500,0xa000,sizes[0],len(parts[0]),0xe100-sizes[1],0xc800,sizes[1],len(parts[1]),0xc300,0xc100,sizes[2],len(parts[2]))
    struct.pack_into('<12H',newhead,config,*newwords)
    edits=[dict(index=i,old=a,new=b)for i,(a,b)in enumerate(zip(words,newwords,strict=True))if a!=b]
    assert {row['index']for row in edits}<={2,4,6,10}
    ownedhead={config+2*row['index']+byte for row in edits for byte in(0,1)}
    assert all(a==b for at,(a,b)in enumerate(zip(header,newhead,strict=True))if at not in ownedhead)
    capacity=45*1024;used=len(header)+sum(sizes)
    assert used<=capacity and sizes[0]<=6528 and 0xe100-sizes[1]>=0xc900 and sizes[2]<=1280
    q=dict(passed=True,scope='Detached arrays and encoding plan only; no gameplay mount or combined ROM',parent_SHA256=PIN,
        spans=[{**{k:v for k,v in row.items()if k not in('old','new')},'bytes':len(row['old']),
            'preimage_SHA256':digest(row['old']),'proposed_SHA256':digest(row['new']),
            'old_hex':row['old'].hex(),'new_hex':row['new'].hex()}for row in rows],
        owned_bytes=sum(len(row['old'])for row in rows),changed_bytes=sum(sum(a!=b for a,b in zip(row['old'],row['new'],strict=True))for row in rows),
        pickup_labels=labels,ctor_new_meaningful_bytes=79,pickup_new_meaningful_bytes=75,
        old_packed_stream_bytes=old_sizes,new_packed_stream_bytes=sizes,header_word_edits=edits,
        planned_cookie=Packet.cookie(parts,bytes(newhead)+b''.join(packed)).hex(),carrier_spare_bytes=capacity-used,
        physical_carrier_half_open=[[Packet.CHR+page*1024,Packet.CHR+(page+1)*1024]for page in Packet.PAGES],
        physical_cookie_half_open=[Packet.COOKIE,Packet.COOKIE+16],
        all_other_decoded_bytes_exact=True,head_art_decoder_loader_and_tables_exact=True,
        physical_ROM_constructed=False,gameplay_mounts=0,Mesen=False,outputs=0)
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    return q

if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Detached tier2 plan attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=plan(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
