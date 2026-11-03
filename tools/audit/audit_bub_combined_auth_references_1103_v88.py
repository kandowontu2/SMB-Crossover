"""Classify actual combined83 resident words and standard ROM farcalls."""
import json
from pathlib import Path
import check_bub_combined_auth_contracts_1103_v84 as P
from check_tmnt_render_oa import location

R,O,sha=P.R,P.O,P.sha


def main():
    out=O/'combined-auth-v88-references.json';assert not out.exists()
    old,new,parent,q=P.image();ol=parent['manager_labels'];nl=q['labels']
    origin=16+65*8192;bank=old['raw'][origin:origin+8192]
    assert old['raw'][origin+0x740:origin+0x7f0]==new['raw'][origin+0x740:origin+0x7f0]
    unchanged=['CoCold','CoRetire','CoCheckCode','CoSmc','PrTypedWorker','PrCopyLive','PrCopyLiveDone','PrCookie']
    assert all(ol[name]==nl[name]for name in unchanged)
    assert all(old['raw'][origin+off:origin+off+16]==new['raw'][origin+off:origin+off+16]for off in [0xfe2,0xff2])
    # All contiguous address/pointer words in the physical manager bank,
    # including data. Every moved helper/table reference is internal to the
    # fully reassembled manager/extra unit. No discovery-based rebinding.
    names=['CoCheckHeaders','CoRetireOwners','CoSelectIndex','CoCookieHi','CoDescriptorLo',
        'CoDescriptorHi','CoRetireLo','CoRetireHi']
    references=[]
    for name in names:
        target=ol[name];positions=[]
        for i in range(8191):
            if bank[i:i+2]!=target.to_bytes(2,'little'):continue
            assert 0xe00<=i<0x1013 or 0xb72<=i<0xbd4,(name,hex(0xa000+i))
            positions.append(dict(CPU=0xa000+i,previous_opcode=bank[i-1],inside_reassembled_source=True))
        references.append(dict(symbol=name,old=target,new=nl[name],word_references=positions))
    # Exact current macro-emitted FarCallCommon JSR/tail-JMP forms. The
    # dynamic high-owner classifier is a separate source-bound path below.
    prg=old['raw'][16:1048592];calls=[]
    moved={ol[name]for name in names if ol[name]!=nl[name]}
    for opcode in [32,76]:
        needle=bytes([169,193,opcode,90,1]);pos=0
        while(pos:=prg.find(needle,pos))>=0:
            prefix=prg[pos-10:pos]
            assert prefix[:1]==bytes([169])and prefix[2:6]==bytes.fromhex('8d6c01a9')and prefix[7:]==bytes.fromhex('8d6d01')
            target=prefix[1]+256*prefix[6]
            assert target not in moved
            at=16+pos-10;blob=old['raw'][at:16+pos+5]
            assert new['raw'][at:16+pos+5]==blob
            calls.append(dict(physical_PRG=pos//8192,file_offset=at,target=target,
                kind='JSR'if opcode==32 else'tailJMP',actual_hex=blob.hex(),unchanged=True))
            pos+=1
    assert len(calls)==11
    # Native ingresses and their final FarCallCommon normalization were
    # physically qualified in82.83's relevant entry sources are identical.
    actual=[]
    for name in ['HuVisible','HuSide','HuWeaponTail','HuCommonRestore']:
        at=location(old,name);size=6 if name=='HuCommonRestore' else 11
        assert old['raw'][at:at+size]==new['raw'][at:at+size]
        actual.append(dict(name=name,file_offset=at,actual_hex=old['raw'][at:at+size].hex()))
    for row in [9,14,34]:
        at=origin+0x108c+row*3
        assert old['raw'][at:at+3]==bytes.fromhex('4c40a7')
        assert new['raw'][at:at+3]==bytes([76])+nl['CoNativePrimitive'].to_bytes(2,'little')
    # Current source names internal helpers only inside their owner unit;
    # external selector calls the unchanged CoCheckCode AEE3 and A800.
    selector=(P.P.D.O/'native-combined-selector-v101.s').read_text()
    assert selector.count(' jsr CoCheckCode\n')==selector.count(' jsr ShCheckCode\n')==1
    assert not any(name in selector for name in names)
    result=dict(passed=True,CPU_only=True,candidate_allowed=False,ROM_written=False,
        preserved_external_manager_entries={name:ol[name]for name in unchanged},
        entire_selector_byte_identical=True,all_cookie_addresses_and_bytes_unchanged=True,
        moved_private_resident_references=references,standard_constant_bank193_FRC_calls=calls,
        physically_qualified_native_entry_preimages=actual,
        footer_binding='Exact101 footerB002..B013 is bound by108 finite fetch/direct/indexed/indirect-reader closure;83 only usesB002..B00B for Side tail and retains8EAs. No existing cookie reader extends toB002.',
        scope='Current manager/extra all-word references and complete standard constant-bank193 FRC macro forms; actual dynamic high-owner ingress source/selector and published rows remain bound. This is not a global arbitrary indirect-pointer census or external legal-writer proof and authorizes no authentication cache.',
        remaining=['Root review of typed external import boundaries and exact shared-span placement before candidate permission. No global arbitrary-pointer/cache claim.'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),Path(P.__file__),
            O/'combined-auth-v83-measurement.json',O/'complete-auth-v82-ingress.json',
            P.P.D.O/'native-combined-selector-v101.s',P.P.D.O/'native-combined-padding-v108.json',
            O/'combined-auth-v83.s',O/'combined-auth-v83.bin',O/'combined-auth-v83-extra.bin',
            O/'combined-auth-v83-Sh.bin',O/'combined-auth-v83-selector.bin']})
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,preserved_entries=result['preserved_external_manager_entries'],
        standard_FRC_calls=len(calls),moved_private_symbols=len(references))))


if __name__=='__main__':main()
