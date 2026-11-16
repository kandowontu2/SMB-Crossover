"""Detached current Sonic selector/tail consumer census; no CPU or overlay."""
from pathlib import Path
import json
import plan_sonic_hidden_heads_1327_1116 as P

PLAN_SHA='72389119e42a6f84ef71bbfdea78c3132799cae779a2c6d99219cb549c118901'


def review(raw):
    assert P.H(Path(P.__file__).read_bytes())==PLAN_SHA
    d=P.descriptor(raw)
    page=lambda n:raw[P.CHR+n*1024:P.CHR+(n+1)*1024]
    kernel=b''.join(page(n)for n in P.PAGES[:8]);meta=page(328)
    domains=((3,0xa000,kernel),(2,0xd000,meta),(2,0xd400,page(333)),(2,0xd800,page(334)))
    words=[];controls=[];branches=[];writes=[];indirect=[]
    write_ops=(0x8c,0x8d,0x8e,0x99,0x9d,0xce,0xde,0xee,0xfe,0x0e,0x1e,0x2e,0x3e,0x4e,0x5e,0x6e,0x7e)
    for bank,base,data in domains:
        for i in range(len(data)-1):
            target=int.from_bytes(data[i:i+2],'little')
            if any(lo-1<=target<hi for lo,hi in((0xbb26,0xbb39),(0xdb26,0xdb39))):
                words.append(dict(bank=bank,PC=base+i,target=target,context=data[max(0,i-3):i+5].hex()))
        for i in range(len(data)-2):
            pc=base+i;op=data[i];target=int.from_bytes(data[i+1:i+3],'little')
            if op in(0x20,0x4c,0x6c)and any(lo<=target<hi for lo,hi in((0xbb26,0xbb39),(0xdb26,0xdb39))):
                controls.append(dict(bank=bank,PC=pc,opcode=op,target=target))
            if op in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                dest=pc+2+int.from_bytes(data[i+1:i+2],'little',signed=True)
                if 0xbb26<=dest<0xbb39:branches.append(dict(bank=bank,PC=pc,opcode=op,target=dest))
            if op in write_ops:
                extent=255 if op in(0x99,0x9d,0xde,0xfe,0x1e,0x3e,0x5e,0x7e)else 0
                if target<=0xd370 and target+extent>=0xd344:writes.append(dict(bank=bank,PC=pc,opcode=op,base=target,maximum_extent=extent))
            if op==0x6c:indirect.append(dict(bank=bank,PC=pc,pointer=target))
    selector=P.R/'tools/reference/sonic_sms_native_swept_selector_1110.py'
    text=selector.read_text();part=text.split('CheckSpecial:\n',1)[1].split('EmptyCell:\n',1)[0]
    assert part.startswith(' lda PTile\n cmp #$5f\n beq Unsupported\n')
    assert ':'not in part,'No internal label inside the replaced19 bytes or following normal stage'
    assert "not any(x['mode']in('zpg','zpx','zpy','inx','iny','ind')" in text
    services=[int.from_bytes(meta[i+1:i+3],'little')for i in range(0x100,0x172,3)]
    assert len(services)==38 and not any(0xbb26<=x<0xbb39 or 0xd344<=x<0xd371 for x in services)
    out=dict(passed=not words and not controls and not writes,ROM_SHA256=P.PIN,source_SHA256=P.H(Path(__file__).read_bytes()),
        plan_SHA256=PLAN_SHA,plan_receipt=d['receipt_SHA256'],selector_source_SHA256=P.H(selector.read_bytes()),
        selector_word_leads=words,selector_control_leads=controls,selector_relative_leads=branches,
        selector_before_and_after=kernel[0x1b10:0x1b42].hex(),
        prospective_tail_direct_or_maximum_indexed_write_leads=writes,existing_indirect_JMP_byte_leads=indirect,
        tail_scope='Current owning kernel/metadata/ring/feedback absolute/indexed stores and selector source. Cold bulk copies and foreign cache replacement are lifecycle writers; no blanket arbitrary-pointer exclusion.',
        root_capacity_receipt='b5a1b55da03f22874490617cc0339e80fd9a631cc92072a0ff76043cca9575e0',
        changed_addresses_not_executed=True,whole_image_created=False,outputs=0,allocation=False)
    out['receipt_SHA256']=P.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(review(P.ROM.read_bytes()),separators=(',',':')),flush=True)
