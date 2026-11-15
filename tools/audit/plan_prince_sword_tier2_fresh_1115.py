"""Detached four-span successor retiring only the constructor-tail gap clear."""
from pathlib import Path
from unittest.mock import patch
import json,struct
import plan_prince_sword_tier2_1115 as Previous
from verify_native_relocation import NesMPU

R,Packet,PIN,digest=Previous.R,Previous.Packet,Previous.PIN,Previous.digest

def arrays(raw):
    head,parts,sizes,prior,labels=Previous.arrays(raw)
    lo,hi=0x13f1,0x13f9;old=parts[0][lo:hi];assert old==bytes.fromhex('a2079df8c0ca10fa')
    assert parts[0][lo-2:lo]==bytes.fromhex('a900')and parts[0][hi:hi+3]==bytes.fromhex('4ce7de')
    assert parts[1][0xdee7-0xc800:0xdee7-0xc800+2]==bytes.fromhex('a2af')
    row=dict(name='Retire Fresh clear of newly executable constructor tail',stream=0,decoded_half_open=[lo,hi],
        live_CPU_half_open=[0xb3f1,0xb3f9],old=old,new=b'\xea'*8)
    return head,parts,sizes,prior+[row],labels

def flat(parts):
    base=[0]*65536
    for at,part in zip((0xa000,0xc800,0xc0b0),parts):base[at:at+len(part)]=part
    cases=0;oldcycles=set();newcycles=set()
    for flags in(0x20,0x21,0x60,0x61,0xa0,0xa1,0xe0,0xe1):
      for x in(0,7,0x80,255):
       for y in(0,13,0x80,255):
        results=[]
        for proposed in(False,True):
            memory=base[:];memory[0xc0f8:0xc100]=bytes(range(0x91,0x99))
            if proposed:memory[0xb3f1:0xb3f9]=b'\xea'*8
            c=NesMPU(memory=memory);c.pc=0xb3ef;c.sp=221;c.a=85;c.x=x;c.y=y;c.p=flags
            for _ in range(100):
                if c.pc==0xdee9:break
                c.step()
            else:raise AssertionError('Fresh-to-ResetTail bound')
            assert(c.a,c.x,c.y,c.sp,c.pc)==(0,0xaf,y,221,0xdee9)
            assert c.p&(1|64)==flags&(1|64)
            assert memory[0xc0f8:0xc100]==(list(range(0x91,0x99))if proposed else[0]*8)
            results.append((memory,c))
        a,ca=results[0];b,cb=results[1]
        assert(ca.a,ca.x,ca.y,ca.p,ca.sp,ca.pc)==(cb.a,cb.x,cb.y,cb.p,cb.sp,cb.pc)
        allowed={*range(0xb3f1,0xb3f9),*range(0xc0f8,0xc100)}
        assert all(v==w for at,(v,w)in enumerate(zip(a,b))if at not in allowed)
        oldcycles.add(ca.processorCycles);newcycles.add(cb.processorCycles);cases+=1
    return dict(cases=cases,public_ResetTail_after_LDX_AF_regs_flags_stack_exact=True,
        all_nonowned_data_exact=True,old_cycles=sorted(oldcycles),new_cycles=sorted(newcycles),
        scope='Flat primitive at original Fresh entry; not gameplay or a packet mount')

def plan(raw):
    head,before,old_sizes,rows,_=arrays(raw);after=list(map(bytearray,before))
    for row in rows:
        stream=row['stream'];lo,hi=row['decoded_half_open'];after[stream][lo:hi]=row['new']
    parts=tuple(map(bytes,after));packed=tuple(map(Packet.encode,parts));sizes=tuple(map(len,packed))
    config=len(head)-54;oldwords=struct.unpack_from('<12H',head,config)
    words=(0xc500,0xa000,sizes[0],len(parts[0]),0xe100-sizes[1],0xc800,sizes[1],len(parts[1]),0xc300,0xc100,sizes[2],len(parts[2]))
    planned=bytearray(head);struct.pack_into('<12H',planned,config,*words)
    edits=[dict(index=i,old=a,new=b)for i,(a,b)in enumerate(zip(oldwords,words))if a!=b]
    assert {row['index']for row in edits}<={2,10}
    references=[]
    for stream,part in enumerate(before):
      for at in range(len(part)-1):
        target=int.from_bytes(part[at:at+2],'little')
        if 0xc0f8<=target<0xc100:references.append(dict(stream=stream,offset=at,target=target,context=part[max(0,at-1):at+4].hex(),
            role='Exact Fresh indexed clear'if(stream,at)==(0,5108)else'Immutable3174-byte pose data, not code ingress'))
    assert[(r['stream'],r['offset'])for r in references]==[(0,5108),(1,2308)]
    q=dict(passed=True,scope='Detached four-span successor plan, no combined ROM or game mount',parent_SHA256=PIN,
        retained5cfa_cold_failure='Fresh B3F3 erases appended constructor tail before second HostInit; BRK C0F9',
        spans=[{**{k:v for k,v in row.items()if k not in('old','new')},'bytes':len(row['old']),
            'preimage_SHA256':digest(row['old']),'proposed_SHA256':digest(row['new']),
            'old_hex':row['old'].hex(),'new_hex':row['new'].hex()}for row in rows],
        owned_bytes=sum(len(row['old'])for row in rows),changed_bytes=sum(sum(a!=b for a,b in zip(row['old'],row['new']))for row in rows),
        references=references,flat_fresh_boundary=flat(before),old_packed_stream_bytes=old_sizes,new_packed_stream_bytes=sizes,
        header_word_edits=edits,planned_cookie=Packet.cookie(parts,bytes(planned)+b''.join(packed)).hex(),
        carrier_spare_bytes=45*1024-len(head)-sum(sizes),source_model_mounts=0,ROM_composed=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Detached Fresh fit attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=plan(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
