"""Read-only current PlayerStatus reference inventory; no candidate placement."""
from bisect import bisect_right
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import json,re
import check_prince_full_fresh_current_1115 as Current
import prince_cold_packet_1111 as Packet

R=Path(__file__).resolve().parents[2]
W=Current.Base.Candidate.W
PIN='7a80f0f37e316436be0825bbd6fd9d372af6b0b7741f84ea87356282033d9b79'
OPS={0xad:'LDA',0xbd:'LDA,X',0xb9:'LDA,Y',0xae:'LDX',0xbe:'LDX,Y',0xac:'LDY',0xbc:'LDY,X',
 0xcd:'CMP',0xdd:'CMP,X',0xd9:'CMP,Y',0xec:'CPX',0xcc:'CPY',0x2d:'AND',0x3d:'AND,X',0x39:'AND,Y',
 0x0d:'ORA',0x1d:'ORA,X',0x19:'ORA,Y',0x4d:'EOR',0x5d:'EOR,X',0x59:'EOR,Y',
 0x6d:'ADC',0x7d:'ADC,X',0x79:'ADC,Y',0xed:'SBC',0xfd:'SBC,X',0xf9:'SBC,Y',0x2c:'BIT',
 0x8d:'STA',0x9d:'STA,X',0x99:'STA,Y',0x8e:'STX',0x8c:'STY',0xce:'DEC',0xde:'DEC,X',
 0xee:'INC',0xfe:'INC,X',0x0e:'ASL',0x1e:'ASL,X',0x2e:'ROL',0x3e:'ROL,X',0x4e:'LSR',0x5e:'LSR,X',0x6e:'ROR',0x7e:'ROR,X'}


def inventory(raw):
    assert sha256(raw).hexdigest()==PIN
    b=dict(W.Symbols.bundle(),raw=raw);assert W.address(b,'PlayerStatus')==0x75b
    symbols=defaultdict(list)
    for name,row in b['syms'].items():
        if 'seg'not in row:continue
        try:at=W.location(b,name);pc=W.address(b,name)
        except (KeyError,ValueError,AssertionError,TypeError):continue
        if 16<=at<16+128*8192:symbols[at].append((name,pc))
    positions=sorted(symbols)
    def nearest(at):
        i=bisect_right(positions,at)-1
        if i<0:return[]
        first=positions[i]
        if (first-16)//8192!=(at-16)//8192:return[]
        return[dict(name=name,PC=pc+at-first,delta=at-first)for name,pc in symbols[first]][:6]
    literal=[];groups=defaultdict(list)
    def scan(data,kind,origin=0,stream=None):
        for i in range(len(data)-2):
            if data[i]in OPS and data[i+1:i+3]==b'\x5b\x07':
                row=dict(op=OPS[data[i]],context=data[max(0,i-8):i+11].hex())
                if kind=='PRG':
                    at=16+i;row.update(physical=at,bank=i//8192,offset=i&8191,nearest=nearest(at))
                    groups[(row['op'],row['context'])].append(dict(physical=at,bank=row['bank'],nearest=row['nearest']))
                else:row.update(stream=stream,decoded_offset=i,PC=origin+i)
                literal.append(dict(kind=kind,**row))
    scan(raw[16:16+128*8192],'PRG')
    _,parts,_=Packet.extract(raw)
    for stream,(part,origin)in enumerate(zip(parts,(0xa000,0xc800,0xc100))):scan(part,'decoded',origin,stream)
    refs=[];bulk=[]
    for path in sorted((R/'src').rglob('*')):
        if path.suffix not in('.s','.inc'):continue
        owner='';last_label=''
        for number,line in enumerate(path.read_text().splitlines(),1):
            code=line.split(';',1)[0].strip()
            proc=re.match(r'\.(?:c?proc)\s+(\w+)',code)
            if proc:owner=proc[1]
            label=re.match(r'^(\w+):',code)
            if label:last_label=label[1]
            if re.search(r'\bPlayerStatus\b',code):
                refs.append(dict(path=path.relative_to(R).as_posix(),line=number,owner=owner or last_label,code=code))
            if re.search(r'\b(?:OnscreenPlayerInfo|OffscreenPlayerInfo|OffScr_PlayerInfo|TransposePlayers|InitializeMemory)\b',code):
                bulk.append(dict(path=path.relative_to(R).as_posix(),line=number,owner=owner or last_label,code=code))
            if code=='.endproc':owner=''
    q=dict(inventory_complete=False,current_ROM_SHA256=PIN,
        symbols={n:W.address(b,n)for n in('PlayerStatus','NumberofLives','OnscreenPlayerInfo','OffscreenPlayerInfo')if n in b['syms']},
        native_literal_sites=len([r for r in literal if r['kind']=='PRG']),
        native_distinct_contexts=[dict(op=k[0],context=k[1],sites=v)for k,v in groups.items()],
        decoded_literal_sites=[r for r in literal if r['kind']=='decoded'],source_references=refs,bulk_symbol_references=bulk,
        caveat='Raw opcode/operand candidates and nearest old symbols are not executable/ingress/reachability proofs; bulk/indirect aliases still require closure',
        source_outputs=0,Mesen=False,ROM_modified=False)
    q['inventory_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    q=inventory(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
