"""Detached hidden5F/60 selector proposal; no CPU or whole-image overlay."""
from pathlib import Path
from hashlib import sha256
import json,re

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d'
H=lambda b:sha256(b).hexdigest()
CHR=1048592
OLD=bytes.fromhex('ad04c1c95ff070c960f06cc967f068c968f064')
NEW=bytes.fromhex('4c44d3')+b'\xea'*16
HELPER=bytes.fromhex('ad04c1c95ff00fc960f00bc967f01bc968f0174c39bbadb7c0c901d00aadb8c0c901d0034c39bb4c5fbb4c9dbb')
PAGES=(*range(321,328),330,328,333,334,224,226)


def descriptor(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    page=lambda p:raw[CHR+1024*p:CHR+1024*(p+1)]
    kernel=b''.join(page(p)for p in PAGES[:8]);meta=page(328)
    assert H(kernel)=='2b727a4a7856d477af9b5051ad30541f1ec97f4854cd247cfaf617203d648936'
    assert H(meta)=='367881d827a2cb80aafe71ea45dcdf4c8791ac3a129eaea781be4e579c9067f4'
    assert kernel[0x1b26:0x1b39]==OLD and len(OLD)==len(NEW)==19 and len(HELPER)==45
    assert kernel[0x1b39:0x1b40].hex()=='38add5c0edc8c0'and kernel[0x1b5f:0x1b6c].hex()=='ced7c0d008a9808dbac04c75b8'
    assert kernel[0x1b9d:0x1bab].hex()=='a907d002a90a8db5c0a9008db6c0'
    assert kernel.count(bytes.fromhex('adc3c08db7c0adc7c08db8c0'))==1
    assert meta[0x344:]==b'\xff'*188
    tail=meta[0x31f:0x344]
    assert tail.hex()=='c90ab00bc908d004a9d485044c68d2386041014201430144014501460147014a014d014e01'
    assert [int.from_bytes(meta[i:i+2],'little')for i in range(0x330,0x344,2)]==list(PAGES[:8]) +[333,334]
    source=R/'tools/reference/sonic_sms_ring_feedback_1110.py';s=source.read_text()
    for token in("{'SONIC_COLD': (0xd25e, 139), 'COLD_TAIL': (0xd31f, 225)}", "result['used']['COLD_TAIL'] == 37",
        "metadata[at+len(before):at+len(new)] == b'\\xff'*(len(new)-len(before))",
        "metadata[at:at+len(new)] = new"):
        assert token in s,token
    # Retain every overinclusive pointer/control lead for independent review.
    domains=[('kernel',3,0xa000,kernel),('metadata',2,0xd000,meta),('rings',2,0xd400,page(333)),('feedback',2,0xd800,page(334))]
    words=[];controls=[];relative=[]
    for name,bank,origin,data in domains:
        for i in range(len(data)-1):
            target=int.from_bytes(data[i:i+2],'little')
            if 0xd343<=target<0xd371:words.append(dict(domain=name,bank=bank,PC=origin+i,target=target,around=data[max(0,i-3):i+5].hex()))
        for i in range(len(data)-2):
            if data[i]in(0x20,0x4c,0x6c):
                target=int.from_bytes(data[i+1:i+3],'little')
                if 0xd344<=target<0xd371:controls.append(dict(domain=name,bank=bank,PC=origin+i,target=target,opcode=data[i]))
            if data[i]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                target=origin+i+2+int.from_bytes(data[i+1:i+2],'little',signed=True)
                if 0xd344<=target<0xd371:relative.append(dict(domain=name,bank=bank,PC=origin+i,target=target,opcode=data[i],around=data[max(0,i-2):i+4].hex()))
    # Component arrays and streamed digest only. No complete revised image.
    revised_kernel=kernel[:0x1b26]+NEW+kernel[0x1b39:]
    revised_meta=meta[:0x344]+HELPER+meta[0x371:]
    old_cookie=raw[1034472:1034488]
    assert old_cookie==bytes.fromhex('a72b01')+sha256(b''.join(map(page,PAGES))).digest()[:13]
    assert raw.count(old_cookie)==1
    cookie=old_cookie[:3]+sha256(revised_kernel+revised_meta+page(333)+page(334)+page(224)+page(226)).digest()[:13]
    at=CHR+327*1024+0x326
    rows=((at,OLD,NEW,'loaded raw3 selectorBB26..BB39'),(CHR+328*1024+0x344,b'\xff'*45,HELPER,'proposed raw2 metadata helperD344..D371'),
        (1034472,old_cookie,cookie,'existing Sonic full cookie'))
    owned=set();changed=set();digest=sha256();cursor=0
    for file,old,new,role in sorted(rows):
        assert raw[file:file+len(old)]==old and len(old)==len(new)and file>=cursor
        owned.update(range(file,file+len(old)));changed.update(file+i for i,(a,b)in enumerate(zip(old,new))if a!=b)
        digest.update(raw[cursor:file]);digest.update(new);cursor=file+len(old)
    digest.update(raw[cursor:])
    assert len(owned)==80
    cases=0
    for tile in range(256):
        for axis in(0,1,2,255):
            for negative in(0,1,128,255):
                old='reject'if tile in(0x5f,0x60,0x67,0x68)else'stage'
                new=('stage'if(axis,negative)==(1,1)else'empty')if tile in(0x5f,0x60)else old
                assert tile in(0x5f,0x60)or new==old
                assert tile not in(0x67,0x68)or new=='reject';cases+=1
    out=dict(detached=True,source_lease_ready=False,parent_SHA256=PIN,source_SHA256=H(Path(__file__).read_bytes()),
        causal_receipt='3919d0b5bf4cbab17b8fcbbf47aa0c1656d60f2ad39188910e9096a73b69b3b5',
        selector=dict(PC=0xbb26,end=0xbb39,old=OLD.hex(),new=NEW.hex(),old_SHA256=H(OLD),new_SHA256=H(NEW)),
        helper=dict(PC=0xd344,end=0xd371,bytes=45,hex=HELPER.hex(),SHA256=H(HELPER),
            preimage='45FF',funding_status='Source-derived tail capacity, not allocated. Root lease remains required.'),
        preserved_anchors=dict(stage=0xbb39,empty=0xbb5f,reject=0xbb9d,source_axis=0xc0b7,source_negative=0xc0b8,tile=0xc104),
        semantics='Only5F/60: axis1 AND negative1 use original normalstage and native ceiling/head effect; all otherdirections use existing EmptyCell. 67/68 retain reject. Original motor/contact code unchanged.',
        transport='JMP helper thenJMP originalstage/empty/reject. A-windowraw3/C-windowraw2 already required by current selector data reads; no mapper, farcallSMC, ZP or stack change.',
        ABI='X/Y and V/D/I unchanged. Non5F/60 repeat original comparison order/finalflags. Hiddenup transientA/C/N/Z are dead at unchangedStageSEC/LDA; explicit intended effect differs fromold rejection. Actual CPU/IRQ proof remains unrun.',
        capacity=dict(producer=source.relative_to(R).as_posix(),source_SHA256=H(source.read_bytes()),COLD_TAIL_start=0xd31f,declared=225,used=37,
            table_start=0xd330,table_entries=10,table_end=0xd344,current_tail_bytes=188,all_tail_FF=True),
        current_tail_word_leads=words,current_tail_control_leads=controls,current_tail_relative_leads=relative,
        pure_classification_cases=cases,cookie_old=old_cookie.hex(),cookie_new=cookie.hex(),owned_bytes=len(owned),changed_bytes=len(changed),
        predicted_candidate_SHA256=digest.hexdigest(),physical_spans=[dict(file=f,bytes=len(a),old_hex=a.hex(),new_hex=b.hex(),old_SHA256=H(a),new_SHA256=H(b),role=r)for f,a,b,r in rows],
        remaining='Root independent sourcecapacity/tableindexedreader and all currentingress review; newlease; then strictinverse/publicCPU/actualcold/foreign/lifecycle/IRQ/natural1UP throughrealceilingstop/physicalcollector/delayedlife+25 forbothforms.',
        CPU_executed=False,whole_candidate_created=False,outputs=0)
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(descriptor(ROM.read_bytes()),separators=(',',':')),flush=True)
