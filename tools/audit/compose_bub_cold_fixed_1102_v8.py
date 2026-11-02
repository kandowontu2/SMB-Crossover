"""Apply root's exact v8 repair and preserve the newly delivered WWF delta."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import sha
from plan_bub_combined_frontend_1102_v1 import fold_patches
O=R/'build/bub-menu-candidate-1102-v2';B=R/'build/bubble-bobble-source-1101-v1'
OLD='31c0de8d169c84a03465eea959961cb38da3666a1e3dffd4bda982efbac11f85'
STANDALONE='8bc54d015e95049d701ab31a259497c6c41675900fc101bb3e81de3466b95c70'
NEW='5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29'
WPIN='f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc'
MPIN='915adaac7268c5fc6fe9c6200f9323b9f25351f071f7683c2c900df1d9823561'

def main():
    base=O/'combined-stomp.nes';manifest=B/'native-cold-fix-successor-31c0.json';freeze=B/'native-cold-fix-qualified-1102-v8.json'
    assert sha(base)==OLD and sha(manifest)==MPIN
    m=json.loads(manifest.read_text());f=json.loads(freeze.read_text())
    assert m['passed'] and m['base_ROM_SHA256']==OLD and m['in_memory_candidate_SHA256']==STANDALONE
    assert f['passed'] and f['manifest_SHA256']==MPIN
    archive=R/f['archive'];assert sha(archive)==f['archive_SHA256']
    with zipfile.ZipFile(archive)as z:
        assert z.testzip()is None and set(z.namelist())==set(f['files'])
        for name,row in f['files'].items():assert sha(R/name)==row['SHA256'] and hashlib.sha256(z.read(name)).hexdigest()==row['SHA256'],name
    cpu=R/m['CPU_receipt']['path'];assert sha(cpu)==m['CPU_receipt']['SHA256'] and json.loads(cpu.read_text())['passed']
    original=R/'build/wwf-death-1102-v2/candidate.nes';wwf=R/'build/wwf-helper-stable-1102-v2/candidate2.nes';delivery=wwf.parent/'delivery.json'
    assert sha(original)=='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243' and sha(wwf)==WPIN
    d=json.loads(delivery.read_text());assert d['installed'] and d['downloads_launch_verified'] and d['ROM_sha256']==WPIN
    raw=base.read_bytes();standalone,_,changed=fold_patches(raw,m['patches'])
    assert len(m['patches'])==2 and len(changed)==m['changed_bytes']==16
    assert hashlib.sha256(standalone).hexdigest()==STANDALONE
    native=original.read_bytes();current=wwf.read_bytes();wwf_delta={i for i,(a,b)in enumerate(zip(native,current))if a!=b}
    bub_delta={i for i,(a,b)in enumerate(zip(native,standalone))if a!=b}
    assert len(wwf_delta)==951 and not wwf_delta&bub_delta
    out=bytearray(standalone)
    for i in wwf_delta:assert out[i]==native[i];out[i]=current[i]
    assert hashlib.sha256(out).hexdigest()==NEW and all(out[i]==current[i]for i in wwf_delta)
    grant=R/'docs/qa/allocations/bubble-cold-fixed-1102-v8.json'
    g=dict(passed=True,granted=True,private_native_testing_only=True,production_admitted=False,installed=False,
        approval_authority='Root explicit current-task approval, 2026-11-02',
        exact_root_approval='Approved exact v8 private relink + disjoint f5 rebase as reported; persist exact grant and candidate, prepare cold native checks for root queue.',
        base_ROM_SHA256=OLD,standalone_candidate_SHA256=STANDALONE,current_candidate_SHA256=NEW,
        proposal_SHA256=MPIN,freeze_SHA256=sha(freeze),archive_SHA256=sha(archive),CPU_receipt_SHA256=sha(cpu),
        exact_patch_records=2,actual_repair_changed_bytes=16,shared_changed_bytes=13,
        approved_spans=[dict(offset=p['offset'],bytes=len(bytes.fromhex(p['old'])),old_SHA256=hashlib.sha256(bytes.fromhex(p['old'])).hexdigest(),new_SHA256=hashlib.sha256(bytes.fromhex(p['new'])).hexdigest(),role=p['role'])for p in m['patches']],
        approved_current_rebase=dict(base_ROM_SHA256=sha(original),delivered_ROM_SHA256=WPIN,changed_bytes=951,intersection_with_Bub_frontend=[],delivery_receipt_SHA256=sha(delivery)),
        scope='Source-linked private admission/Tile23/84 veneer targets and complete16B BBcookie only; then exact disjoint delivered WWF helper delta. No additional RAM/route/menu allocation or production admission.')
    data=(json.dumps(g,indent=2)+'\n').encode()
    if grant.exists():assert grant.read_bytes()==data
    else:grant.write_bytes(data)
    rom=O/'combined-cold-fixed.nes';assert not rom.exists(),'No overwrite of frozen candidate';rom.write_bytes(out)
    assert sha(base.with_suffix('.dbg'))=='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
    for ext in['.dbg','.lbl']:rom.with_suffix(ext).write_bytes(base.with_suffix(ext).read_bytes())
    q=dict(passed=True,private_native_only=True,native=False,installed=False,production_admitted=False,
        base_ROM_SHA256=OLD,standalone_v8_in_memory_SHA256=STANDALONE,ROM=rom.relative_to(R).as_posix(),ROM_SHA256=NEW,
        source_manifest_SHA256=MPIN,grant=grant.relative_to(R).as_posix(),grant_SHA256=sha(grant),
        exact_patch_records=2,repair_changed_bytes=16,shared_repair_changed_bytes=13,
        current_WWF_rebase_SHA256=WPIN,WWF_changed_bytes=951,WWF_Bub_intersection=[],
        WWF_Metal_Arthur_Ex_frontend_preserved=True,debug_exact_native_passed=True,helpers_added_by_Bub=False,
        native_cold_Easy_controls_pop_full11_qualified=False,prior_negative_candidates_and_packets_immutable=True,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),base,manifest,freeze,archive,cpu,original,wwf,delivery,grant,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]})
    (O/'combined-cold-fixed.json').write_text(json.dumps(q,indent=2)+'\n')
    own=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in own)<32000000 and len(own)<1000
    print(json.dumps(dict(passed=True,ROM=rom.relative_to(R).as_posix(),ROM_SHA256=NEW,grant_SHA256=sha(grant),files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
