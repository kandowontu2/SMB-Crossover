"""Detached full status/size fit on00bb; no proposed CPU/image/overlay."""
from hashlib import sha256
from pathlib import Path
import json
import plan_jay_status_publication_00bb_1116 as Old

R,ROM,PIN,H=Old.R,Old.ROM,Old.PIN,Old.H
OLD_PLAN_SHA='0ae3ac71e6fa8f7e0f40fe0da13ce33af9ad79dec18367f01b0ae9698bbb0295'
PRODUCER='tools/audit/check_jay_silius_shotgun_transport_1111.py'
PRODUCER_SHA='a115b62d583ce8eb64944e54fe1266bcdd4f1e1aa8a99b985ae7144ad6b0d8f1'
TRANSFER_SOURCE='tools/reference/jay_silius_shotgun_transport_1111.s'
TRANSFER_SHA='55c52e409edeaacba0a5e852316d4228226d91cf8093cb3c00128a1c59c95783'
TRANSFER64=bytes.fromhex('a90085038505a9a48504a9b48506a000a20bb1039105d105d01ac8d0f5e604e606cad0eeb1039105d105d008c8c0e0d0f34c00d01860eaeaeaeaeaeaeaeaeaea')
TAIL=bytes.fromhex('ad3e5f0aa9004cd7beea')
LEAF=bytes.fromhex('8d59072a8d5b0760')


def descriptor(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    assert H(Path(Old.__file__).read_bytes())==OLD_PLAN_SHA
    assert H((R/PRODUCER).read_bytes())==PRODUCER_SHA and H((R/TRANSFER_SOURCE).read_bytes())==TRANSFER_SHA
    source=(R/PRODUCER).read_text()
    for text in("carrier = bytearray(b'\\xea' * 1024)","copy_pages = 11 if extra_segments else 8 if movement else 3",
                 "transfer_defs += 'CopyTailBytes=224\\n'","{'TRANSFER': (TRANSFER, 64)}",
                 'carrier[TRANSFER - 0xa400:TRANSFER - 0xa400 + len(copy)] = copy'):
        assert text in source,text
    old=Old.descriptor(raw);oldmain=bytes.fromhex(old['exact_spans'][0]['old_hex'])
    main=bytearray.fromhex(old['proposed_main_hex'])
    assert main[0x2c:0x32].hex()=='ad3e5f20d7be'
    main[0x2c:0x32]=bytes.fromhex('20f6b74c32b8')
    main=bytes(main)
    copyat=1048592+222*1024+0x3c0
    assert raw[copyat:copyat+64]==TRANSFER64
    assert len(TRANSFER64)==64 and TRANSFER64[52:54]==bytes.fromhex('1860')and TRANSFER64[54:]==b'\xea'*10
    assert len(TAIL)==10 and len(LEAF)==8 and TAIL[-1]==0xea
    at=lambda bank,pc:16+bank*8192+(pc&8191)
    original=raw[at(96,0xa2df):at(96,0xa2df)+15]
    assert original.hex()=='ad3e5f0aa9002a8d5b07a9008d5907'
    # Factored LDA#0 is shared: the same A=0 stores size before its ROL.
    assert TAIL[:6].hex()=='ad3e5f0aa900'and LEAF.hex()=='8d59072a8d5b0760'
    formula=[]
    for stars in range(256):
        expected=(0,stars>>7)
        observed=(0,((0<<1)|(stars>>7))&255)
        assert observed==expected;formula.append(observed)
    cookie=bytes.fromhex('aa10200e')+sha256(b'Jay full status-size publication detached1116\0'+bytes.fromhex(PIN)+Old.COOKIE+main+TAIL+LEAF).digest()[:12]
    rows=[(1286160,oldmain,main,'same50-byte private guard/reject block'),
          (copyat+54,b'\xea'*10,TAIL,'explicit CopyAlternate64 producer tail10'),
          (1288935,b'\xea'*8,LEAF,'explicit retired Steve token entry pad8')]
    rows +=[(i,Old.COOKIE,cookie,'existing full cookie view')for i in(534328,774911,1429421)]
    owned=set();changed=set();digest=sha256();cursor=0
    for file,before,after,role in sorted(rows):
        assert len(before)==len(after)and raw[file:file+len(before)]==before and file>=cursor
        owned.update(range(file,file+len(before)))
        changed.update(file+i for i,(a,b)in enumerate(zip(before,after))if a!=b)
        digest.update(raw[cursor:file]);digest.update(after);cursor=file+len(before)
    digest.update(raw[cursor:])
    assert len(owned)==116 and len(changed)==72
    assert not any(owned.intersection(range(1048592+p*1024,1048592+(p+1)*1024))for p in(331,332))
    metal=((1561533,bytes.fromhex('1036')),(212991,bytes.fromhex('a7232fc62354dfbde732156cd49e287a')),
           (817141,bytes.fromhex('a7232fc62354dfbde732156cd49e287a')))
    for i,b in metal:assert raw[i:i+len(b)]==b and not owned.intersection(range(i,i+len(b)))
    # Instruction costs excluding shared StageRejected and followingLDAReady.
    parent_cycles=6*2+3
    accepted_cycles=3+6+4+2+2+3+4+2+4+6+3
    assert parent_cycles==15 and accepted_cycles==39
    out=dict(detached=True,source_lease_ready=False,parent_SHA256=PIN,
        failed_partial_candidate_SHA256='df0e009bad3240122629da681dfd20e559b1fdba2b235b6a00c3ffeefda88afe',
        causal_receipt='5d02c293721c27839e8637f5e81bb804d59105a0ecc5e5ca5ab892418bf54d87',
        predecessor_plan_SHA256=OLD_PLAN_SHA,predecessor_plan_receipt=old['receipt_SHA256'],
        producer_SHA256=PRODUCER_SHA,transfer_source_SHA256=TRANSFER_SHA,
        original_native_status_size15_hex=original.hex(),pure_formula_cases=len(formula),
        fullsync_main50_hex=main.hex(),runtime_tail10=dict(PC=0xb7f6,hex=TAIL.hex(),SHA256=H(TAIL)),
        size_status_leaf8=dict(PC=0xbed7,hex=LEAF.hex(),SHA256=H(LEAF)),
        original_transfer64_SHA256=H(TRANSFER64),preserved_transfer54_SHA256=H(TRANSFER64[:54]),
        CopyFailed_CLC_RTS_preserved='B7F4/B7F5 (cold stagedA7F4/A7F5)',
        return_edges='StageRejectedB825->A7E6->B828; mainJSRB7F6 tailJMPBED7 leafRTS->B82F thenJMP SupportedB832',
        accepted_extra_cycles_estimate=accepted_cycles-parent_cycles,rejected_stage_delta=-12,early_reject_delta=0,
        extra_nested_JSR_stack_bytes=0,stack_contract='One new helperJSR, as partialproposal; tailJMP avoids secondJSR. New candidateCPU/IRQ proof still required.',
        store_order='New Size0 before Statusbit7; old nativeStatusbit7 before Size0. No foreground observer between; actualISR consumer/effect proof required.',
        logical_runtime_alias='New helper raw3B7F6/C-windowD7F6; staged raw3A7F6/C7F6 exists only during coldcopy. DecodedprimaryA7F6ProgressMux stays byte-exact.',
        primary331_332_and_all34Metal_bytes_preserved=True,no_new_RAM_or_carriers_or_helpers=True,
        proposed_cookie=cookie.hex(),cookie_files=[534328,774911,1429421],owned_bytes=len(owned),changed_bytes=len(changed),
        predicted_candidate_SHA256=digest.hexdigest(),
        physical_spans=[dict(file=f,bytes=len(b),old_hex=b.hex(),new_hex=a.hex(),old_SHA256=H(b),new_SHA256=H(a),role=r)for f,b,a,r in rows],
        remaining='Independent allalias/reader/staging-before-header closure; newsourcelease; then exactC/inverse/fullsizeABI/lifecycle/head-oracle/IRQ/naturalF andallPlayerSize consumers.',
        CPU_executed=False,ROM_overlay=False,whole_candidate_created=False,outputs=0)
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(descriptor(ROM.read_bytes()),separators=(',',':')),flush=True)
