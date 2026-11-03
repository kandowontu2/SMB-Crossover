"""Bind actual native primitive ingresses and current resident references."""
import itertools
import json
from pathlib import Path
import check_bub_shared_auth_contracts_1103_v77 as P
from check_tmnt_render_oa import location

R,O,N,Q,address,sha=P.R,P.O,P.N,P.Q,P.address,P.sha


def image():
    old,manifest=P.P.F.D.image()
    proof=O/'shared-auth-v76-funding.json'
    q=json.loads(proof.read_text())
    for rel,value in q['bindings'].items():
        assert sha(R/rel)==value,rel
    raw=bytearray(old['raw']);origin=16+65*8192
    for row in q['patches']:
        at=origin+row['CPU']-0xa000
        before,after=bytes.fromhex(row['old_hex']),bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(before)]==before
        raw[at:at+len(after)]=after
    for off in q['selector_auth_reference']:
        assert raw[origin+off:origin+off+3]==bytes([32])+q['old_labels']['CoCheckCode'].to_bytes(2,'little')
        raw[origin+off+1:origin+off+3]=q['new_labels']['CoCheckCode'].to_bytes(2,'little')
    for row in [9,14,34]:
        at=origin+0x108c+row*3
        assert raw[at:at+3]==bytes.fromhex('4c40a7')
        raw[at:at+3]=bytes([76])+q['new_labels']['CoNativePrimitive'].to_bytes(2,'little')
    return old,dict(old,raw=bytes(raw)),q,manifest


def main():
    destination=O/'complete-auth-v82-ingress.json';assert not destination.exists()
    old,new,q,manifest=image()
    route=P.P.F.C.bundle()[1]
    # Actual native high-owner stubs save A/Y/P, classify the owner and tail
    # FarCallCommon+3. Its final LDA restores A and therefore sets N/Z, on
    # both old and proposed paths. We never infer arbitrary direct-call flags.
    common=location(old,'HuCommonRestore')
    assert old['raw'][common:common+6]==bytes.fromhex('68a8284c5d01')
    stub=[]
    for name,row in [('HuVisible',9),('HuSide',14),('HuWeaponTail',34)]:
        at=location(old,name)
        code=bytes.fromhex('8d6a01089848a0')+bytes([row])+bytes.fromhex('4c40b8')
        assert old['raw'][at:at+11]==new['raw'][at:at+11]==code
        stub.append(dict(name=name,row=row,physical_PRG=(at-16)//8192,CPU=address(old,name),actual_hex=code.hex()))
    mmc=(R/'src/mmc5.s').read_text()
    assert 'SMC_StoreValue SafereturnA, a\n  pla\n  sta CurrentBank\n  BankPRGA a\n  SMC SafereturnA, { lda #SMC_Value }\n  rts' in mmc
    seeds={identity:[Q.Q.fresh(bb,route,identity)for bb in [old,new]]for identity in [0,1]}
    cases=poisons=0;native_entries=[]
    for identity in [0,1]:
        for name,row in [('HuVisible',9),('HuSide',14),('HuWeaponTail',34)]:
            for a,y,flags in itertools.product([0,1,83,128,255],[0,9,109],[0x20,0x21,0x71,0xf1]):
                pair=[N.fork(m)for m in seeds[identity]]
                outputs=[N.invoke(m,name,a=a,x=0,y=y,p=flags)for m in pair]
                P.parity(*pair,outputs)
                assert outputs[1]['P']&0x82==(0x80 if outputs[1]['A']&128 else 2 if outputs[1]['A']==0 else 0)
                cases+=1
            for bank in [2,3]:
                for off in range(16):
                    pair=[N.fork(m)for m in seeds[identity]]
                    for m in pair:m.ram[bank][0x1fe0+off]^=1
                    outputs=[N.invoke(m,name,a=128,x=0,y=9,p=0x71)for m in pair]
                    P.parity(*pair,outputs);assert not outputs[1]['P']&1
                    poisons+=1
            native_entries.append(dict(identity=identity,name=name,legal_header_cases=60,individual_header_faults=32))
    origin=16+65*8192;bank=old['raw'][origin:origin+8192]
    references={}
    for name in ['CoCheckCode','CoCheckHeaders','CoRetireOwners','CoSmc']:
        target=q['old_labels'][name]
        words=[i for i in range(8191)if bank[i:i+2]==target.to_bytes(2,'little')]
        rows=[]
        for i in words:
            owner=0xe00<=i<0x1013
            if not owner:
                assert name=='CoCheckCode'and i-1 in q['selector_auth_reference']
                assert bank[i-1]==32
                selector=(P.P.F.D.O/'native-selector-v79.s').read_text()
                assert selector.count(' jsr CoCheckCode\n')==1
                assert 'PrOdd:\n jsr CoCheckCode\n bcc DkLocalNo\n' in selector
            rows.append(dict(CPU=0xa000+i-1,actual_hex=bank[i-1:i+2].hex(),
                source='reassembled native-owner-v79.s/shared-auth-v76.s'if owner else'native-selector-v79.s PrOdd',
                rebinding='internal source expression'if owner else'one exact external JSR operand'))
        references[name]=rows
    assert len(references['CoCheckCode'])==1
    assert len(references['CoCheckHeaders'])==3
    assert len(references['CoRetireOwners'])==2
    assert len(references['CoSmc'])==2
    # No resident same-bank JSR/JMP or contiguous pointer names the three
    # specialized public entries. Their real native ingress is above. This
    # conservative word inventory is not a global indirect-pointer proof.
    for row in [9,14,34]:
        target=0xb08c+row*3
        assert all(bank[i:i+2]!=target.to_bytes(2,'little')for i in range(8191))
    shrefs=[]
    expected={0xa7ab:'native-selector-v79.s PrSh',0xa8dd:'shinobi_resident_loader_1101_v1.inc ShLoad',
              0xabda:'shinobi_chr_1101_v6.inc ShChr',0xac8d:'shinobi_damage_1101_v10.inc ShInjury'}
    sites=[0xa000+i for i in range(8190)if bank[i:i+3]==bytes.fromhex('2000a8')]
    assert set(sites)==set(expected),sites
    for pc in sites:
        assert new['raw'][origin+pc-0xa000:origin+pc-0xa000+3]==bytes.fromhex('2000a8')
        shrefs.append(dict(CPU=pc,source=expected[pc],entry_preserved=0xa800))
    # Address-taken cookie and SMC data remain exact; no caller can point at
    # a moved cookie. Only the internal CoSmc data location is rebound.
    for index in range(4):
        pointers=[]
        for bb,key in [(old,'old_labels'),(new,'new_labels')]:
            lo=origin+q[key]['CoCookieLo']-0xa000
            hi=origin+q[key]['CoCookieHi']-0xa000
            pointers.append(bb['raw'][lo+index]+256*bb['raw'][hi+index])
        assert pointers[0]==pointers[1]
        at=origin+pointers[0]-0xa000
        assert old['raw'][at:at+16]==new['raw'][at:at+16]
    assert old['raw'][origin+0xa78:origin+0xa88]==new['raw'][origin+0xa78:origin+0xa88]
    result=dict(passed=True,CPU_only=True,candidate_allowed=False,ROM_written=False,
        native_ingresses=stub,actual_native_entry_cases=cases,header_fault_cases=poisons,
        native_entry_results=native_entries,
        flags_contract='Exact actual HuVisible/HuSide/HuWeaponTail -> HuCommonRestore -> FarCallCommon+3 entry and final LDA return. N/Z derive from returned A; all actual public AXYP/SP/state/maps/SMC match. Arbitrary same-bank raw direct-entry N/Z is deliberately not claimed.',
        bank65_all_contiguous_word_references=references,actual_preserved_Sh_callers=shrefs,
        cookies_unchanged=True,
        checkpoint81_field_erratum=dict(field='source_proposal_memory_SHA256',
            actual_meaning='SHA256 of shared-auth-v76-funding.json, not a cartridge or memory image',
            expected=sha(O/'shared-auth-v76-funding.json')),
        scope='Actual native ingresses and conservative complete bank65 word references, with source-bound selector and unchanged fixed entry points. This does not claim a new global legal writer inventory or authorize authentication caching.',
        remaining=['Canonical combined101/108 source fit and exact rebind; source funding is not additive.',
            'Conservative other-bank farcall/pointer inventory remains to be classified before declaring every possible external reference closed.',
            'Root permission still required before any cartridge placement or native packet.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(P.__file__),
            O/'shared-auth-v76-funding.json',O/'complete-auth-source-v81.json',
            P.P.F.D.O/'native-selector-v79.s',P.P.F.D.O/'native-owner-v79.s',
            R/'src/mmc5.s',R/'tools/reference/shinobi_resident_loader_1101_v1.inc',
            R/'tools/reference/shinobi_chr_1101_v6.inc',R/'tools/reference/shinobi_damage_1101_v10.inc']})
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key]for key in ['passed','actual_native_entry_cases','header_fault_cases','actual_preserved_Sh_callers']}))


if __name__=='__main__':main()
