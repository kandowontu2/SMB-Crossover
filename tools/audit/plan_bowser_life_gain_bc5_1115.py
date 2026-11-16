"""Detached exact40-byte Bowser Ensure repair/funding; no game/ROM mount."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse,json
import current_bowser_stock_bc5_1115 as Current
from verify_native_relocation import NesMPU
from py65.disassembler import Disassembler

R,PIN=Current.R,Current.PIN
digest=lambda data:sha256(data).hexdigest()

def proposal(raw):
    proof=Current.preservation(raw);b=Current.bundle(raw);image=Current.frozen_image()
    address=lambda name:Current.W.address(b,name)
    start,end=address('BwEnsure'),address('BwImport');assert(end-start)==40
    old=image[start-0xa000:end-0xa000]
    ctor=address('BwConstruct');ready=address('BwReady');key=address('BwPlayerKey');saved=address('BwPersistent')+2
    current=address('CurrentPlayer');lives=address('NumberofLives')
    code=bytearray();labels={};branches=[]
    def emit(*values):code.extend(values)
    def absolute(op,at):emit(op,at&255,at>>8)
    def branch(op,label):emit(op,0);branches.append((len(code)-1,label))
    absolute(0xad,ready);emit(0xc9,0xb7);branch(0xd0,'Construct')
    absolute(0xad,current);emit(0x29,1,0x0a,0x0a);absolute(0xcd,key);branch(0xd0,'Construct')
    absolute(0xae,key);absolute(0xad,lives);absolute(0xdd,saved)
    branch(0x90,'Construct');branch(0xf0,'Done');absolute(0x9d,saved)
    labels['Done']=len(code);emit(0x60)
    labels['Construct']=len(code);absolute(0x4c,ctor)
    used=len(code);assert used==39
    for at,label in branches:
        delta=labels[label]-at-1;assert-128<=delta<128;code[at]=delta&255
    code.append(0xea);new=bytes(code);assert len(new)==len(old)==40
    after=image[:start-0xa000]+new+image[end-0xa000:]
    assert len(after)==8192 and after[:start-0xa000]==image[:start-0xa000] and after[end-0xa000:]==image[end-0xa000:]
    return b,image,after,dict(start=start,end=end,old=old,new=new,used=used,labels={k:start+v for k,v in labels.items()},proof=proof)

def decoded(memory,start,end):
    d=Disassembler(NesMPU(memory=memory));rows=[];pc=start
    while pc<end:
        size,text=d.instruction_at(pc);rows.append(dict(PC=pc,bytes=bytes(memory[pc:pc+size]).hex(),instruction=text));pc+=size
    assert pc==end;return rows

def closure(before,row,b):
    memory=bytearray(65536);memory[0xa000:0xc000]=before;cpu=NesMPU(memory=memory);d=Disassembler(cpu)
    todo=[0xa000+3*i for i in range(36)];seen={};unresolved=[]
    branch_ops={0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0}
    while todo:
        pc=todo.pop()
        if pc in seen or not 0xa000<=pc<0xaa37:continue
        size,text=d.instruction_at(pc);op=memory[pc];seen[pc]=(size,text)
        if op in(0x00,0x40,0x60):continue
        if op==0x6c:unresolved.append(dict(PC=pc,instruction=text));continue
        if op in(0x20,0x4c):
            target=int.from_bytes(memory[pc+1:pc+3],'little');todo.append(target)
            if op==0x4c:continue
        if op in branch_ops:
            delta=memory[pc+1];delta=delta-256 if delta&128 else delta;todo.append(pc+2+delta)
        todo.append(pc+size)
    absolute=[];relative=[];aliases=[];writers=[]
    persistent=Current.W.address(b,'BwPersistent')
    for at,(size,text)in sorted(seen.items()):
        op=memory[at]
        if op in(0x20,0x4c):
            target=int.from_bytes(memory[at+1:at+3],'little')
            if row['start']<=target<row['end']:absolute.append(dict(PC=at,target=target,instruction=text))
        if op in branch_ops:
            delta=memory[at+1];delta=delta-256 if delta&128 else delta;target=at+2+delta
            if row['start']<=target<row['end']and not row['start']<=at<row['end']:relative.append(dict(PC=at,target=target,instruction=text))
        if op in(0x8c,0x8d,0x8e,0x99,0x9d,0xce,0xde,0xee,0xfe):
            target=int.from_bytes(memory[at+1:at+3],'little')
            if persistent<=target<persistent+8:writers.append(dict(PC=at,target=target,instruction=text,bytes=bytes(memory[at:at+size]).hex()))
    for i in range(len(before)-1):
        target=int.from_bytes(before[i:i+2],'little')
        if row['start']<=target<row['end']and not row['start']<=0xa000+i<row['end']:
            owner=seen.get(0xa000+i-1)
            aliases.append(dict(PC=0xa000+i,target=target,owner=owner[1]if owner else None,
                context=before[max(0,i-2):i+4].hex()))
    assert absolute and all(r['target']==row['start']for r in absolute)
    assert not relative
    # Indirect source dispatch is reported, never silently declared resolved.
    return dict(reached_instruction_boundaries=len(seen),public_table_entries=36,
        actual_reached_absolute_ingress=absolute,external_relative_ingress=relative,raw_word_aliases=aliases,
        indirect_JMPs=unresolved,current_saved_player_writers=writers,
        scope='Recursive control-flow from all36 public JMP entries; opaque native farcalls do not become packet interior ingress')

def inspect_plan(raw):
    b,before,after,row=proposal(raw);address=lambda name:Current.W.address(b,name)
    memory=bytearray(65536);memory[0xa000:0xc000]=before
    old=decoded(memory,row['start'],row['end']);memory[row['start']:row['end']]=row['new'];new=decoded(memory,row['start'],row['end'])
    image_hits=[];at=raw.find(before)
    while at>=0:image_hits.append(at);at=raw.find(before,at+1)
    cookies=[];at=raw.find(Current.COOKIE)
    while at>=0:cookies.append(at);at=raw.find(Current.COOKIE,at+1)
    assert len(image_hits)==1 and cookies==[565244,693672]
    assert image_hits[0]==1997840
    cookie=Current.COOKIE[:4]+sha256(after).digest()[:12]
    views=[]
    for label,at,old_view,new_view in(
        ('Ensure inside existing CHR927..934 executable carrier',image_hits[0]+row['start']-0xa000,row['old'],row['new']),
        ('BwLoad inline copied fingerprint',cookies[0],Current.COOKIE,cookie),
        ('BwCheck expected fingerprint',cookies[1],Current.COOKIE,cookie)):
        assert raw[at:at+len(old_view)]==old_view
        views.append(dict(name=label,file_half_open=[at,at+len(old_view)],bytes=len(old_view),old_hex=old_view.hex(),new_hex=new_view.hex(),
            old_SHA256=digest(old_view),new_SHA256=digest(new_view),changed_bytes=sum(x!=y for x,y in zip(old_view,new_view))))
    callers=[]
    for name in('BwSavePlayer','BwSelectPlayer','BwEnsure','BwConstruct'):
        target=address(name);hits=[]
        for i in range(2615-2):
            if before[i]in(0x20,0x4c)and int.from_bytes(before[i+1:i+3],'little')==target:
                hits.append(dict(PC=0xa000+i,opcode=before[i],context=before[max(0,i-6):i+9].hex()))
        callers.append(dict(name=name,entry=target,absolute_JSR_JMP_candidates=hits))
    q=dict(passed=True,scope='Detached owning bc5 proposal, not ROM composition or game overlay',ROM_SHA256=PIN,
        old_packet_SHA256=digest(before),proposed_packet_SHA256=digest(after),
        old_executable2615_SHA256=digest(before[:2615]),proposed_executable2615_SHA256=digest(after[:2615]),
        span=dict(CPU_half_open=[row['start'],row['end']],decoded_half_open=[row['start']-0xa000,row['end']-0xa000],owned_bytes=40,used_bytes=39,
            old_hex=row['old'].hex(),new_hex=row['new'].hex(),old_SHA256=digest(row['old']),new_SHA256=digest(row['new']),
            changed_bytes=sum(a!=b for a,b in zip(row['old'],row['new']))),
        old_instructions=old,new_instructions=new,labels=row['labels'],callers=callers,ingress=closure(before,row,b),
        complete_original_packet_physical_matches=image_hits,cookie_physical_matches=cookies,
        cookie_view=dict(old=Current.COOKIE.hex(),proposed=cookie.hex(),bytes=16),required_physical_views=views,
        projected_owned_physical_bytes=sum(v['bytes']for v in views),projected_changed_physical_bytes=sum(v['changed_bytes']for v in views),
        semantics='Active valid same-player life equal returns unchanged; increase stores existing saved-life byte only; decrease/invalid-ready/member mismatch keep original Construct',
        funding='Share the existing constructor JMP across local branches; new code39 fits exact old Ensure40, with one unreachable NOP inside that function',
        other_guest_bytes_exact=True,SelectPlayer_SavePlayer_Construct_unchanged=True,new_RAM_or_shared_loader_bytes=0,
        physical_ROM_header_changes=0,source_model_mounts=0,ROM_composed=False,outputs=0,Mesen=False)
    return q

if __name__=='__main__':
    raw=Current.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Detached Bowser plan attempted files/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=inspect_plan(raw)
    q['receipt_SHA256']=digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
