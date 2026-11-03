"""Measure current four-owner cold/retirement without emitting a cartridge.

Existing resident spans are proposal funding, not a new shared grant. The
typed DK payload uses only its formally reserved eleven carriers/overlays.
"""
import json
import re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_prince_strike_cold_1103_v131 as C

R, O = A.R, A.O


def main():
    base, parent = C.image()
    assert A.sha(base['raw']) == 'cba497aabf91ccb357a9392a4407f261c8fd33a66032ae9d7b2e1ba790ef490d'
    q = json.loads((O/'native-event-v74-layout.json').read_text())
    body = (O/'native-event-v74.bin').read_bytes()
    code = bytearray([255])*8192
    code[:len(body)] = body
    assert code[0x1fe0:] == bytes([255])*32
    art = [bytearray((O/f'native-art-{page}-v38.chr').read_bytes()) for page in A.ART]
    art[1][576:768] = bytes([255])*192
    boot = (O/'admission-cold-v11.bin').read_bytes()
    assert len(boot) == 119
    art[1][606:606+len(boot)] = boot
    art[2][320:] = bytes([255])*704
    for kind, at in [('pause',320), ('main',606), ('ports',679)]:
        part = (O/f'native-event-{kind}-v74.bin').read_bytes()
        art[2][at:at+len(part)] = part
    assert len(art[2]) == 1024 and art[2][q['metadata_end']-0xd400:] == bytes([255])*q['metadata_spare']
    payload = bytes(code) + b''.join(art)
    assert len(payload) == 11264
    cookie = bytes([0xa7,40,1]) + bytes.fromhex(A.sha(payload))[:13]
    (O/'native-payload-v79.bin').write_bytes(payload)
    (O/'native-cookie-v79.bin').write_bytes(cookie)
    # Factor only long branches to the same exact reject continuation. Pin
    # ExForeignLo at its existing address, retaining every external indexed
    # UI consumer operand; insert cookie in the recovered preceding bytes.
    selector = (C.O/'post-selector-v130.s').read_text()
    selector = selector.replace('cmp #3\n bcc PrOdd', 'cmp #4\n bcc PrOdd')
    assert selector.count('cmp #39\n beq PrOddBB') == 1
    selector = selector.replace('cmp #39\n beq PrOddBB', 'cmp #37\n bne PrOddBB')
    for old, new in [('jcc ShDispatchNo','bcc DkLocalNo'), ('jne ShDispatchNo','bne DkLocalNo'), ('jcs ShDispatchNo','bcs DkLocalNo')]:
        selector = selector.replace(old, new)
    selector = selector.replace('PrSh:\n', 'DkLocalNo:\n jmp ShDispatchNo\nPrSh:\n')
    assert selector.count('ExForeignLo:\n') == 1
    selector = selector.replace('ExForeignLo:\n', '''.export PrFamily,DkCookie,DkDescriptorData,DkCopyDescriptor
DkCookie:
 .incbin "'''+(O/'native-cookie-v79.bin').as_posix()+'''"
 .res $9a-(*-ExDispatch),$ea
ExForeignLo:
''')
    selector += '''
DkDescriptorData:
 .byte 2,0,9,$d0,$c0,3,$c1,3
DkCopyDescriptor:
 ldy #7
:
 lda DkDescriptorData,y
 sta $dfe0,y
 dey
 bpl :-
 rts
'''
    select_cfg = 'MEMORY{S:start=$a740,size=$b2,file=%O;}SEGMENTS{EX_SELECT:load=S,type=ro;}'
    sb, SL = A.assemble('native-selector-v79', selector, select_cfg)
    assert len(sb) <= 178 and SL['ExForeignLo'] == 0xa7da and SL['PrFamily'] == 0xa743
    owner = (C.O/'post-owner-v130.s').read_text()
    owner = ('DkDescriptor=$dfe0\nDkCookie=$%04x\nDkCopyDescriptor=$%04x\n' % (SL['DkCookie'],SL['DkCopyDescriptor'])) + owner
    assert owner.count('cmp #3\n bcs CoSelectNo') == 1
    owner = owner.replace('cmp #3\n bcs CoSelectNo','cmp #4\n bcs CoSelectNo')
    old = ' jsr CoSelect\n jsr PrTypedWorker\n .res 15,$ea'
    new = ''' jsr CoSelect
 lda SelectedCharacter
 cmp #40
 bne :+
 jsr DkCopyDescriptor
:
 jsr PrTypedWorker
 .res 1,$ea'''
    assert owner.count(old) == 1
    owner = owner.replace(old,new)
    tables = []
    for name, value in [('CoCookieLo','<DkCookie'), ('CoCookieHi','>DkCookie'), ('CoDescriptorLo','<DkDescriptor'), ('CoDescriptorHi','>DkDescriptor')]:
        match = re.search('^'+name+r':\.byte [^\n]+\n',owner,re.M)
        assert match, name
        tables.append(match[0].rstrip()+','+value+'\n')
        owner = owner[:match.start()] + owner[match.end():]
    start,end = owner.index('CoRetireOwners:\n'),owner.index('CoInvalidate:\n')
    old_main_retire = owner[start:end]
    owner = owner[:start]+'''CoRetireOwners:
 ldx #3
CoRetireLoop:
 txa
 pha
 lda CoCookieLo,x
 sta R5
 lda CoCookieHi,x
 sta R6
 jsr CoCheckHeaders
 bcc CoRetireNext
 pla
 tax
 pha
 lda CoRetireLo,x
 beq CoRetireInvalidate
 sta FarcallJmpTarget_SMC+1
 lda CoRetireHi,x
 sta FarcallJmpTarget_SMC+2
 lda #2
 sta CurrentBankC
 sta $5116
 sta SafecallA_SMC+1
 lda #3
 jsr FarCallCommon
CoRetireInvalidate:
 jsr CoInvalidate
CoRetireNext:
 pla
 tax
 dex
 bpl CoRetireLoop
 jmp ShRetire
'''+owner[end:]
    start,end = owner.index('PrRetire:\n'),owner.index('PrCookie:\n')
    old_private_retire = owner[start:end]
    owner = owner[:start]+'PrRetire=CoRetireOwners\n'+owner[end:]
    old = ' cmp #38\n beq PrWorkerPrince'
    assert owner.count(old) == 1
    owner = owner.replace(old, ' cmp #40\n beq PrWorkerPrince\n'+old)
    owner = owner.replace('CoOwnerEnd:\n',' .res $213-(*-CoCold),$ea\nCoOwnerEnd:\n')
    data = ''.join(tables)+'CoRetireLo:.byte 0,<PrNativeRetire,<BbNativeRetire,<$d60c\nCoRetireHi:.byte 0,>PrNativeRetire,>BbNativeRetire,>$d60c\n'
    owner = owner.replace('PrExtraEnd:\n',data+'PrExtraEnd:\n')
    owner = '.export CoRetireOwners,CoRetireLoop,CoRetireLo,CoRetireHi\n'+owner
    cfg = 'MEMORY{M:start=$ae00,size=$213,file=%O;X:start=$ab72,size=$62,file="'+(O/'native-owner-extra-v79.bin').as_posix()+'";}SEGMENTS{COMMON_OWNER_PROPOSAL:load=M,type=ro;PR_EXTRA:load=X,type=ro;}'
    ob, OL = A.assemble('native-owner-v79',owner,cfg)
    extra = (O/'native-owner-extra-v79.bin').read_bytes()
    assert len(ob) == 531 and len(extra) <= 98 and OL['CoCold'] == 0xae00 and OL['CoRetire'] == 0xae0b
    selector = re.sub(r'CoCheckCode=\$[0-9a-f]+','CoCheckCode=$%04x'%OL['CoCheckCode'],selector)
    sb, SL2 = A.assemble('native-selector-v79',selector,select_cfg)
    assert SL == SL2 and len(sb) <= 178
    raw = bytearray(base['raw'])
    patches = []
    for pc, data, role in [(0xa740,sb,'Current local-reject selector factor, pinned foreign UI table and exact DK cookie/descriptor'),
            (0xab72,extra,'Current successful typed worker and factored four-owner retirement/address tables'),
            (0xae00,ob,'Current four-owner cold/auth/header/retire source factor')]:
        at = 16+65*8192+pc-0xa000
        old = raw[at:at+len(data)]
        raw[at:at+len(data)] = data
        patches.append(dict(physical_PRG=65,CPU_half_open=[pc,pc+len(data)],file_offset=at,
            old_hex=old.hex(),new_hex=data.hex(),role=role,shared_grant_required=True))
    pages = A.CODE+A.ART
    for i,page in enumerate(pages):
        at = 1048592+1024*page
        old,data = raw[at:at+1024],payload[i*1024:(i+1)*1024]
        raw[at:at+1024] = data
        patches.append(dict(physical_CHR=page,file_offset=at,old_hex=old.hex(),new_hex=data.hex(),role='Formally reserved exclusive DK code/art/helper carrier'))
    gates = json.loads((R/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json').read_text())
    # The frozen source layouts are exact proposal preimages already reviewed
    # by the root grant. Their copied records are explicit and independently
    # checked against the current parent; no discovery-based blank allocation.
    gate_rows = [json.loads((O/'native-bbox-v65-layout.json').read_text())['ungranted_shared_gate_proposal'],
        json.loads((O/'native-rare-gate-v71.json').read_text())['proposal']]
    for row in gate_rows:
        at = row['file_offset'];old,new = bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)] == old
        raw[at:at+len(new)] = new
        patches.append(dict(physical_PRG=row['physical_PRG'],CPU_half_open=row['CPU_half_open'],file_offset=at,
            old_hex=old.hex(),new_hex=new.hex(),role='Root-granted private bbox/rare gate',grant='docs/qa/allocations/dkjr-shared-gates-1103-v104.json'))
    out = dict(passed=True,qualified=False,ROM_written=False,shared_source_written=False,installed=False,native_owner_admitted=False,
        parent_memory_SHA256=A.sha(base['raw']),parent_source='build/prince-actor-1101-v1/strike-manifest-v130.json',
        parent_nightly_SHA256=parent['parent_memory_SHA256'],expected_memory_only_SHA256=A.sha(raw),
        code_pages=A.CODE,art_pages=A.ART,payload_bytes=len(payload),payload_SHA256=A.sha(payload),cookie=cookie.hex(),
        body_bytes=len(body),body_spare=q['header_spare'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],
        manager_bytes=len(ob),manager_labels=OL,extra_bytes=len(extra),selector_bytes=len(sb),selector_labels=SL,
        patches=patches,old_main_retire_source=old_main_retire,old_private_retire_source=old_private_retire,
        source_funding='Authenticated owner retirement loop replaces current repeated per-owner bodies and aliases old private PrRetire. Four existing address tables move into that reclaimed body. Local reject factor recovers executed branch bytes; foreign UI table stays exactly A7DA. Source-declared old resident extents only; no common123 spare or new RAM.',
        remaining=['Resident/menu/public source factor is still ungranted. Native scene range still admits only37..39; extend exact owning range only after source/foreign/carry proof.',
            'Actual current cold/readback/full headers/retirement, authenticated public rows/foreign parity/IRQ lifetimes and focused menu remain to qualify before any native ROM.',
            'Ten unsupported private policies remain explicit Cclear rejects; no complete public service or native gameplay claim.'],
        scope='Current cf7 plus exact Prince130 read-only input. Private compiled candidate exists only as typed11264B component and memory patch manifest; no NES ROM is emitted. This is a source-funded resident proposal, not permission to mutate shared spans.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),C.O/'strike-manifest-v130.json',
            C.O/'post-owner-v130.s',C.O/'post-selector-v130.s',O/'native-event-v74-layout.json',
            O/'native-event-v74.bin',O/'native-event-pause-v74.bin',O/'native-event-main-v74.bin',O/'native-event-ports-v74.bin',
            O/'native-payload-v79.bin',O/'native-cookie-v79.bin',O/'admission-cold-v11.bin',
            O/'native-owner-v79.s',O/'native-owner-v79.bin',O/'native-owner-extra-v79.bin',O/'native-selector-v79.s',O/'native-selector-v79.bin',
            R/'docs/qa/allocations/dkjr-private-resources-1102-v20.json',R/'docs/qa/allocations/dkjr-shared-gates-1103-v104.json']})
    (O/'native-owner-proposal-v79.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['passed','expected_memory_only_SHA256','payload_bytes','cookie','manager_bytes','extra_bytes','selector_bytes','metadata_end','metadata_spare']}))


def image():
    q=json.loads((O/'native-owner-proposal-v79.json').read_text())
    for rel,digest in q['bindings'].items():
        assert A.sha((R/rel).read_bytes())==digest,rel
    base,_=C.image();raw=bytearray(base['raw'])
    assert A.sha(raw)==q['parent_memory_SHA256']
    for row in q['patches']:
        at=row['file_offset'];old,new=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert A.sha(raw)==q['expected_memory_only_SHA256']
    return dict(base,raw=bytes(raw)),q


if __name__=='__main__':main()
