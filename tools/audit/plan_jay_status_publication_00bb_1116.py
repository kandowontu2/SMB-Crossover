"""Detached fit only; shared-ingress/Jay-only proof is explicitly still open."""
from hashlib import sha256
from pathlib import Path
import json

R=Path(__file__).resolve().parents[2]
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='00bb2664647a4ef47b5dfa01c96d50549581d215a33d19a2a6390d1e09078e21'
REFERENCE='7c0f7902e5ef17ff552c2ce36ba08534fdd48f00fddc62a54834df18e68f3c98'
COOKIE=bytes.fromhex('aa10200c3c8114b6f52cd1db4b8564a0')
H=lambda b:sha256(b).hexdigest()


def descriptor(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    at=lambda bank,pc:16+bank*8192+(pc&8191)
    source_pins={
        'tools/audit/check_jay_silius_machinegun_1111.py':'9c04b71b17261e24b3803a2e452ffb010c0f02b5c95e8775422688ea49d2f01a',
        'tools/audit/check_steve_shatterhand_token_ingress_1111.py':'30c7b1b034cb9d14542fc1392006ed1b406b8edf3230e48fc5895b6aac5b5824',
        'tools/audit/current_jay_natural_stock_7c0f_1116.py':'b8c128b51bd47cb2c3f7dce828277a06c54ed034b7d2e1071f667fee41016aeb',
        'tools/audit/audit_jay_upgrade_publication_7c0f_1116.py':'90fb3980b175c38d303b00f31bf14c196311c1bddfbc344af418d89b9ac50df6'}
    for path,digest in source_pins.items():assert H((R/path).read_bytes())==digest
    source=(R/'tools/audit/check_jay_silius_machinegun_1111.py').read_text()
    assert "tested_stage = call('StageRejected') + b'\\xea'*6"in source
    assert "replace(motion, 0xb800, 0xb825, stage_guard + b'\\xf0', tested_stage + b'\\x90')"in source
    token=(R/'tools/audit/check_steve_shatterhand_token_ingress_1111.py').read_text()
    assert "patch(origin, before, b'\\x4c'+S.address_bytes(symbols['SteveTokenDispatch'])+b'\\xea'*8)"in token
    first=1048592+232*1024;extra=1048592+234*1024
    main=raw[first:first+50]
    assert main.hex()=='ad7107c901d029ad7307c903d022a50fc908d01cad77074ab016ad39011011adff5f4a900b20e6a7eaeaeaeaeaea90021860'
    assert raw[extra+0x2d4:extra+0x2df]==bytes.fromhex('4c00c2')+b'\xea'*8
    mirror=raw[at(96,0xa2df):at(96,0xa2e9)]
    assert mirror.hex()=='ad3e5f0aa9002a8d5b07'
    # Reorder only the already-owned support/reject block. It is NOT safe
    # to insert the mirror into the six NOPs before consuming StageRejected C.
    new=bytearray(main);branches=[]
    for offset in(5,12,18,24,29,35):
        assert main[offset]in(0xd0,0xb0,0x10,0x90)
        assert 0xb800+offset+2+main[offset+1]==0xb830
        new[offset+1]-=6
        branches.append(dict(PC=0xb800+offset,old_target=0xb830,new_target=0xb82a))
    assert main[0x25:0x32]==bytes.fromhex('20e6a7')+b'\xea'*6+bytes.fromhex('90021860')
    new[0x25:0x32]=bytes.fromhex('20e6a790021860ad3e5f20d7be')
    leaf=bytes.fromhex('0aa9002a8d5b0760')
    assert bytes(new[0x2c:0x2f])+leaf[:-1]==mirror
    cookie=bytes.fromhex('aa10200d')+sha256(b'Jay parity publication detached 1116\0'+bytes.fromhex(PIN)+COOKIE+bytes(new)+leaf).digest()[:12]
    rows=[(first,main,bytes(new),'current PrivateUpdate scope/reject block50'),
          (extra+0x2d7,b'\xea'*8,leaf,'Steve token dispatch explicitly retired8-byte pad')]
    cookies=(534328,774911,1429421)
    assert [i for i in range(len(raw)-15)if raw[i:i+16]==COOKIE]==list(cookies)
    for file in cookies:rows.append((file,COOKIE,cookie,'full existing cookie view'))
    # Known Metal bytes are read/qualified only and excluded from all edits.
    metal=((1561533,bytes.fromhex('1036')),
           (212991,bytes.fromhex('a7232fc62354dfbde732156cd49e287a')),
           (817141,bytes.fromhex('a7232fc62354dfbde732156cd49e287a')))
    owned=set();changes=set();digest=sha256();cursor=0
    for file,old,data,role in sorted(rows):
        assert len(old)==len(data)and raw[file:file+len(old)]==old and file>=cursor
        owned.update(range(file,file+len(old)))
        changes.update(file+i for i,(a,b)in enumerate(zip(old,data))if a!=b)
        digest.update(raw[cursor:file]);digest.update(data);cursor=file+len(old)
    digest.update(raw[cursor:])
    for file,data in metal:assert raw[file:file+len(data)]==data and not owned.intersection(range(file,file+len(data)))
    assert len(owned)==106
    hot=raw[at(94,0xb27f):at(94,0xb27f)+112]
    assert hot[:22].hex()=='08488a489848ad0260c910d046ad0b73691f2940f03d'
    packet=raw[1048592+218*1024:1048592+219*1024]
    assert packet[0x343:0x352].hex()=='4caab3baa201a0ff3809004c00b88d'
    assert packet[0x3ea:0x3f8].hex()=='082c0b737004284c7bb6284cd4be'
    report=dict(detached=True,lease_ready=False,owning_parent_SHA256=PIN,historical_reference_SHA256=REFERENCE,
        source_pins=source_pins,main_PC=0xb800,main_bytes=50,main_old_SHA256=H(main),main_new_SHA256=H(new),
        proposed_main_hex=bytes(new).hex(),redirected_private_reject_branches=branches,
        Supported_anchor_unchanged='B832',private_Unsupported_moved='B830->B82A; external ingress closure required',
        original_native_mirror=dict(bank=96,PC=0xa2df,hex=mirror.hex()),proposed_leaf=dict(PC=0xbed7,hex=leaf.hex()),
        source_declared_funding=['Jay StageRejected call replacement explicitly emits6NOP',
                                 'Steve token ingress explicitly replaces11B with JMP C200+8NOP'],
        no_new_RAM_or_carriers=True,all34_Metal_owned_bytes_preserved=True,
        proposed_cookie=cookie.hex(),cookie_views=[dict(file=f,role=r)for f,r in zip(cookies,
            ('PRG65 cold expected header','PRG94 hot expected header','CHR371+925 uncompressed StevePacketCold::ExpectedCookie'))],
        cookie_parent_shadow_unchanged='CHR371+64 historical prior-cookie shadow is NOT the live cookie',
        owned_bytes=len(owned),changed_bytes=len(changes),streamed_conditional_digest=digest.hexdigest(),
        exact_spans=[dict(file=f,bytes=len(o),old_hex=o.hex(),new_hex=n.hex(),old_SHA256=H(o),new_SHA256=H(n),role=r)for f,o,n,r in rows],
        shared_ingress_blocker='Current Hot94 admits BOTH Jay and Steve. No Jay-only gate fits these14 new publication bytes. Do not mount until all actual Steve/Mike ingress is proven nonexecuting or already mirror-equivalent, or a separately funded explicit gate is supplied.',
        live_guard_preservation='StageRejected carry consumed before mirror; early rejects retarget same CLC/RTS. Supported and Ready/epoch code unchanged.',
        expected_data_domain='Read JnStars5F3E; write only native PlayerStatus075B plus normal new JSR stack. Original Jay Q4/velocity/weapon/ammo/helpers unchanged.',
        source_gate_requirements=['actual current identity/variant/header/Ready/lifecycle and all three cookie consumers',
            'all external/interior readers of moved Unsupported and Steve8 pad',
            'actual Mike/Steve paired supported-update/collector/paused paths, not an assumed invariant',
            'actual public AXYP/meaningful flags/SMC/mapper/live stack and reached IRQ/busy NMI',
            'same ordinary genuine heart prefix then final prepared Flower kind and actual reward/usable ability policy'],
        CPU_executed=False,ROM_overlay=False,whole_candidate_created=False,outputs=0)
    report['receipt_SHA256']=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    return report


if __name__=='__main__':print('JAY_STATUS_PLAN '+json.dumps(descriptor(ROM.read_bytes()),separators=(',',':')),flush=True)
