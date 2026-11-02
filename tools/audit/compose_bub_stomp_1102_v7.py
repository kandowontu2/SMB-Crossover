"""Persist root's exact private grant and compose the reviewed Easy successor."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
from plan_bub_combined_frontend_1102_v1 import fold_patches
O=R/'build/bub-menu-candidate-1102-v2';B=R/'build/bubble-bobble-source-1101-v1'
BASE='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'
NEW='31c0de8d169c84a03465eea959961cb38da3666a1e3dffd4bda982efbac11f85'
MPIN='8a78fea08a0d7ef837673be363efa1362db7bd8dbf05d583fcb77381d155a593'

def main():
    base=O/'combined-visible.nes';manifest=B/'native-stomp-successor-4395.json';freeze=B/'native-stomp-qualified-1102-v7.json'
    assert sha(base)==BASE and sha(manifest)==MPIN
    m=json.loads(manifest.read_text());f=json.loads(freeze.read_text())
    assert m['passed'] and m['base_ROM_SHA256']==BASE and m['in_memory_candidate_SHA256']==NEW
    assert f['passed'] and f['manifest_SHA256']==MPIN
    archive=R/f['archive'];assert sha(archive)==f['archive_SHA256']
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None and set(z.namelist())==set(f['files'])
        for name,row in f['files'].items():
            assert sha(R/name)==row['SHA256'],name
            assert hashlib.sha256(z.read(name)).hexdigest()==row['SHA256'],name
    cpu=R/m['CPU_receipt']['path'];assert sha(cpu)==m['CPU_receipt']['SHA256'] and json.loads(cpu.read_text())['passed']
    patches=m['patches'];assert len(patches)==11
    grant=R/'docs/qa/allocations/bubble-stomp-1102-v7.json'
    approval='Root reviewed v7 source changes/CPU/freeze. Approve exact private successor manifest8a78fea08a0d7ef837673be363efa1362db7bd8dbf05d583fcb77381d155a593 over4395, expected31c0de8d169c84a03465eea959961cb38da3666a1e3dffd4bda982efbac11f85. Scope nineownedcarriers/16BBBcookie and CoRetireOwners lowoperand65:AF82 76→7A only; no additionalRAM/routers/menu.'
    g=dict(passed=True,granted=True,private_native_testing_only=True,production_admitted=False,installed=False,
        approval_authority='Root agent explicit approval in current shared task, 2026-11-02; root explicitly directed this composer to persist the durable grant.',
        exact_root_approval=approval,base_ROM_SHA256=BASE,candidate_SHA256=NEW,proposal_SHA256=MPIN,
        freeze_SHA256=sha(freeze),archive_SHA256=sha(archive),CPU_receipt_SHA256=sha(cpu),
        exact_patch_records=11,actual_changed_bytes=2433,shared_changed_bytes=14,
        scope='Nine already owned carrier pages, complete16B BBcookie, one CoRetireOwners low operand65:AF82 76→7A. No additional RAM, routes, menu or production admission.',
        approved_spans=[dict(offset=p['offset'],bytes=len(bytes.fromhex(p['old'])),old_SHA256=p['old_SHA256'],new_SHA256=p['new_SHA256'],role=p['role'])for p in patches])
    data=(json.dumps(g,indent=2)+'\n').encode()
    if grant.exists():assert grant.read_bytes()==data,'Grant already differs; root review required'
    else:grant.write_bytes(data)
    raw=base.read_bytes();out,owned,changed=fold_patches(raw,patches)
    assert len(changed)==g['actual_changed_bytes']==m['changed_bytes'] and hashlib.sha256(out).hexdigest()==NEW
    assert out[536466]==0x7a and raw[536466]==0x76
    assert out[792580:792583]==bytes.fromhex('3aaf88') and out[544116]==0x18
    assert all(raw[i]==out[i]for i in range(16,16+1024*1024)if not(536595<=i<536611 or i==536466))
    code=[p for p in patches if p['role'].startswith('Bub/Bob private code')]
    assert len(code)==8
    oldcode=b''.join(bytes.fromhex(p['old'])for p in code);newcode=b''.join(bytes.fromhex(p['new'])for p in code)
    assert oldcode[0x100:0x153a]==newcode[0x100:0x153a]
    art=next(p for p in patches if p['role'].startswith('Immutable helper441'))
    assert bytes.fromhex(art['old'])[:800]==bytes.fromhex(art['new'])[:800]
    rom=O/'combined-stomp.nes';assert not rom.exists(),'No overwrite of frozen candidate'
    rom.write_bytes(out)
    assert sha(base.with_suffix('.dbg'))=='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
    for ext in['.dbg','.lbl']:rom.with_suffix(ext).write_bytes(base.with_suffix(ext).read_bytes())
    q=dict(passed=True,private_native_only=True,native=False,installed=False,production_admitted=False,
        base_ROM_SHA256=BASE,ROM=rom.relative_to(R).as_posix(),ROM_SHA256=NEW,
        source_manifest_SHA256=MPIN,grant=grant.relative_to(R).as_posix(),grant_SHA256=sha(grant),
        exact_patch_records=11,changed_bytes=len(changed),shared_changed_bytes=14,
        no_other_current_bytes_changed=True,WWF_Metal_Arthur_Ex_frontend_preserved=True,
        original_A100_B53A_and800B_art_exact=True,debug_exact_native_passed=True,helpers_added=False,
        native_Easy_stomp_controls_combat_full11_qualified=False,
        prior4395_native_packets_immutable=True,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),base,manifest,freeze,archive,cpu,grant,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]})
    (O/'combined-stomp.json').write_text(json.dumps(q,indent=2)+'\n')
    own=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in own)<32000000 and len(own)<1000
    print(json.dumps(dict(passed=True,ROM_SHA256=NEW,ROM=rom.relative_to(R).as_posix(),grant_SHA256=sha(grant),files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
