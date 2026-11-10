"""Mask only prototype bits at older boolean Continue consumers.

Existing low deferred/campaign bits retain their original boolean semantics.
"""
from pathlib import Path
import json
import subprocess
import tempfile
import build_mike_alternate_prototypes_1110 as B

SOURCE=B.R/'tools/reference/mike_prototype_continue_1110.s'


def workers():
    with tempfile.TemporaryDirectory(prefix='continue-',dir=B.OUT) as tmp:
        root=Path(tmp)
        cfg,obj,binary=(root/f'worker.{ext}'for ext in ('cfg','o','bin'))
        cfg.write_text('MEMORY{M:start=$b12b,size=6,file=%O;D:start=$bd28,size=61,file=%O;A:start=$d1e3,size=37,file=%O;H:start=$ba97,size=48,file=%O;}SEGMENTS{MENU_MASK:load=M,type=ro;DK_RESOLVE:load=D,type=ro;AR_SELECT:load=A,type=ro;HU_RESOLVE:load=H,type=ro;}')
        cc=B.R/'tools/Windows/cc65/bin'
        for command in ((cc/'ca65.exe',SOURCE,'-o',obj),(cc/'ld65.exe','-C',cfg,obj,'-o',binary)):
            result=subprocess.run(list(map(str,command)),capture_output=True,text=True)
            assert result.returncode==0,result.stderr
        blob=binary.read_bytes()
        assert len(blob)==152
        return blob[:6],blob[6:67],blob[67:104],blob[104:]


def main():
    old=B.read(B.OUT/'linked-v2.json')
    assert old['expected_memory_only_SHA256']=='3fcf47575faf7f7cfc9f9f82f6a350c1cefd78995f58e7a486be382b2ab89884'
    new=json.loads(json.dumps(old))
    parent=B.source_bundle()['raw']
    helper,dk,ar,hu=workers()
    assert parent[B.off(66,0xb12b):B.off(66,0xb134)]==bytes([255])*9
    assert parent[B.off(66,0xb128):B.off(66,0xb12b)]==bytes.fromhex('4cbba4')
    assert parent[B.off(66,0xa82a):B.off(66,0xa82f)]==bytes.fromhex('ad0b73d003')
    added=[(66,0xb12b,helper,'Six-byte masked Continue reader in source-declared MnMenuEdges9-byte tail'),
           (66,0xa82a,bytes.fromhex('202bb1'),'Fresh initialization receives Continue with only bits60 removed'),
           (36,0xbd28,dk,'Exact DK61-byte resolver envelope, dead incoming-A marshaling funds AND9F'),
           (63,0xd1e3,ar,'Exact Ar37-byte selection envelope; direct constructor branches retire terminal trampoline and fund AND9F'),
           (79,0xba97,hu,'Exact Hu48-byte resolver suffix; shared farcall packet funds AND9F without XY clobber')]
    assert parent[B.off(63,0xd205):B.off(63,0xd208)]==bytes.fromhex('4c16d2')
    assert all(parent.find(bytes([op,0x05,0xd2]),16)==-1 for op in (0x20,0x4c)),'External absolute Ar trampoline ingress'
    for bank,pc,after,role in added:
        at=B.off(bank,pc)
        assert not any(max(at,row['file_offset'])<min(at+len(after),row['file_offset']+len(bytes.fromhex(row['new_hex'])))for row in new['patches'])
        new['patches'].append(dict(file_offset=at,old_hex=parent[at:at+len(after)].hex(),new_hex=after.hex(),role=role))
    raw=bytearray(parent)
    for row in new['patches']:
        at=row['file_offset'];before,after=(bytes.fromhex(row[k])for k in ('old_hex','new_hex'))
        assert raw[at:at+len(before)]==before
        raw[at:at+len(after)]=after
    new.update(version=3,expected_memory_only_SHA256=B.digest(raw),
               previous_private_SHA256=old['expected_memory_only_SHA256'],
               continue_predicate_repair=dict(mask=0x9f,fresh_load_file_offset=B.off(66,0xa82a),DK_resolver_file_offset=B.off(36,0xbd28),
                    native_ChkContinue='PRG9 BC14 ASL/BCC already consumes bit7 only',
                    preserved_boolean_domain=list(range(32))+list(range(128,160)),
                    complete_original_direct_boolean_readers=[[36,0xbd4b],[63,0xd1f5],[66,0xa82a],[79,0xba9b]],
                    source_funding={'menu_tail':[0xb12b,0xb134],'DK':'Unused incoming A; CmHostResolveCharacter source overwrites A before use',
                                    'Ar':'Two internal conditional branches reach D216 directly; original D205 JMP is retired',
                                    'Hu':'Two native transport packets share their common low/high/bank suffix; original saved-A stores retained'}))
    for path in (Path(__file__),SOURCE,B.R/'tools/reference/menu_input_1101_v3.inc',B.R/'src/celeste_mario_host.s'):
        new['source_bindings'][path.relative_to(B.R).as_posix()]=B.digest(path.read_bytes())
    (B.OUT/'linked-v3.json').write_text(json.dumps(new,indent=2)+'\n')
    print('Continue predicate source repair',new['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':main()
