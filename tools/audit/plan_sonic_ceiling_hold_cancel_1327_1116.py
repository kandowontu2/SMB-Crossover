"""Detached combined hidden-head/held-ceiling response; no successor CPU."""
from pathlib import Path
from hashlib import sha256
import json
import plan_sonic_hidden_heads_1327_1116 as Previous

R,ROM,H,PIN,CHR=Previous.R,Previous.ROM,Previous.H,Previous.PIN,Previous.CHR
PREVIOUS_SHA='72389119e42a6f84ef71bbfdea78c3132799cae779a2c6d99219cb549c118901'
TIMER=0xc058
PENDING=0xc122
HELPER_PC=0xd371
HELPER=bytes.fromhex('8d22c1a9008d58c0a90160')


def descriptor(raw):
    assert H(raw)==PIN and H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    prior=Previous.descriptor(raw);assert prior['receipt_SHA256']=='6140b1334cc35e2c3bc258e275036e4d6a24e0f533e743b027cca60c8c2056f2'
    page=lambda p:raw[CHR+p*1024:CHR+(p+1)*1024]
    kernel=b''.join(page(p)for p in Previous.PAGES[:8]);meta=page(328)
    commit=bytes.fromhex('ad52c06d53c08d62c0');assert kernel.count(commit)==1
    first_negative_writer_PC=0xa000+kernel.index(commit)+6
    needle=bytes.fromhex('a9018d22c1');found=[]
    for bank,pc,data,file in((3,0xa000,kernel,None),(2,0xd000,meta,CHR+328*1024)):
        offset=0
        while True:
            offset=data.find(needle,offset)
            if offset<0:break
            found.append(dict(tag=bank,PC=pc+offset+2,file=file+offset+2 if file is not None else None,context=data[offset-8:offset+15].hex()));offset+=1
    assert len(found)==1 and found[0]['tag']==2,'Unique actual MetaVertical Pending store in owning metadata'
    hook=found[0];at=hook['PC']-0xd000
    # Require actual kind4 test and LDA1 immediately before this store.
    prefix=meta[at-9:at];assert prefix[:6]==bytes.fromhex('adb6c0c904d0')and prefix[-2:]==b'\xa9\x01'
    old_hook=meta[at:at+3];assert old_hook==bytes.fromhex('8d22c1')
    new_hook=b'\x20'+HELPER_PC.to_bytes(2,'little')
    assert meta[0x344:]==b'\xff'*188 and len(HELPER)==11
    new_kernel=kernel[:0x1b26]+Previous.NEW+kernel[0x1b39:]
    new_meta=bytearray(meta);new_meta[at:at+3]=new_hook;new_meta[0x344:0x371]=Previous.HELPER;new_meta[0x371:0x37c]=HELPER
    assert new_kernel[:5526]==kernel[:5526]
    cookie=raw[1034472:1034488]
    new_cookie=cookie[:3]+sha256(new_kernel+bytes(new_meta)+page(333)+page(334)+page(224)+page(226)).digest()[:13]
    spans=((1384246,Previous.OLD,Previous.NEW,'existing hidden5F60 selector trampoline'),
        (hook['file'],old_hook,new_hook,'actual kind4 MetaVertical Pending store ->11B timer helper'),
        (CHR+328*1024+0x344,b'\xff'*56,Previous.HELPER+HELPER,'existing45B selector plus new11B ceiling response'),
        (1034472,cookie,new_cookie,'existing full13-page Sonic cookie'))
    owned=set();changed=set();digest=sha256();cursor=0
    for file,old,new,role in sorted(spans):
        assert len(old)==len(new)and raw[file:file+len(old)]==old and file>=cursor
        owned.update(range(file,file+len(old)));changed.update(file+i for i,(a,b)in enumerate(zip(old,new))if a!=b)
        digest.update(raw[cursor:file]);digest.update(new);cursor=file+len(old)
    digest.update(raw[cursor:])
    domains=((3,0xa000,kernel),(2,0xd000,meta),(2,0xd400,page(333)),(2,0xd800,page(334)))
    words=[];controls=[];branches=[]
    for bank,origin,data in domains:
        for i in range(len(data)-1):
            target=int.from_bytes(data[i:i+2],'little')
            if 0xd370<=target<0xd37c:words.append(dict(tag=bank,PC=origin+i,target=target))
        for i in range(len(data)-2):
            op=data[i];target=int.from_bytes(data[i+1:i+3],'little')
            if op in(0x20,0x4c,0x6c)and 0xd371<=target<0xd37c:controls.append(dict(tag=bank,PC=origin+i,target=target))
            if op in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                target=origin+i+2+int.from_bytes(data[i+1:i+2],'little',signed=True)
                if 0xd371<=target<0xd37c:branches.append(dict(tag=bank,PC=origin+i,target=target))
    source=R/'build/sonic-original-composed-frame-1110/component.s'
    assert H(source.read_bytes())=='f73192961c4fccab1cdc42c3c9ca10d05373accbd16611b7d883ddb2842a228d'
    text=source.read_text()
    assert ' lda $58\n bne Continue' in text and 'ContactYVelocity:\n lda #0\n sta $60\n sta $61\n sta $62' in text
    assert 'Suppress:\n lda $56\n and #$f7\n sta $56\n jmp Stop' in text
    out=dict(detached=True,source_lease_ready=False,parent_SHA256=PIN,source_SHA256=H(Path(__file__).read_bytes()),
        prior80B_plan_SHA256=PREVIOUS_SHA,prior80B_f7_source_status='Narrow classifier/natural/fullstage/IRQ qualified; held ascent remains a real physics follow-up, no physical promotion.',
        hook=hook,old_hook_hex=old_hook.hex(),new_hook_hex=new_hook.hex(),helper_PC=HELPER_PC,helper_bytes=len(HELPER),helper_hex=HELPER.hex(),helper_SHA256=H(HELPER),
        change='Only after accepted source kind4 ceiling: reproduce Pending1 store, clear original JumpTimerC058, restoreA1 and return. Existing next-frame Suppress clearsflag08 and applies gravity naturally. Original motor and all flags stay unpatched.',
        ABI='EntryA1/N0/Z0 and kind4 CMP C1 proven by actual preceding bytes. STA Pending;LDA0/STA Timer;LDA1/RTS preserves A/X/Y/C/V/I/D and N/Z. JSR adds2 transient stack bytes; no ZP/mapper/SMC/newstate.',
        scope='All actual native upward ceilings use existing kind4 path, including revealed hidden and visible blocks. Floors/sides/empty/rejected/67/68 do not reach this hook. Header/Ready admission unchanged.',
        original_motor5526_SHA256=H(kernel[:5526]),original_motor_preserved=True,JumpTimer_existing=0xc058,HeadPending_existing=0xc122,
        source_reference_SHA256=H(source.read_bytes()),metadata_tail_declared=[0xd31f,0xd400],original_used_end=0xd344,
        new_helper_end=0xd37c,remaining_declared_tail=132,tail_words=words,tail_controls=controls,tail_relative=branches,
        old_cookie=cookie.hex(),new_cookie=new_cookie.hex(),owned_bytes=len(owned),changed_bytes=len(changed),predicted_candidate_SHA256=digest.hexdigest(),
        physical_spans=[dict(file=f,bytes=len(a),old_hex=a.hex(),new_hex=b.hex(),old_SHA256=H(a),new_SHA256=H(b),role=r)for f,a,b,r in spans],
        causal_writer_receipt='902a4915f51f1ebcf78a49e1080cc9e3443baf14ee2c1a018d49aa80ebe2e3b4',
        actual_first_complete_negative_VY_writer=dict(tag=3,PC=first_negative_writer_PC,opcode='8d62c0',result=[128,252,255]),
        pending='Root independent funding/field/consumer review and new source lease, then finite callerABI/live-stack, realISR+no upward continuation, naturalLboth/fullstageboth/foreign/cold.',
        proposed_CPU_executed=False,whole_candidate_created=False,outputs=0)
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(descriptor(ROM.read_bytes()),separators=(',',':')),flush=True)
