"""Compact direct performance proposal inputs; no ROM/debug trees or expansion."""
import hashlib,json,zipfile
from pathlib import Path
import build_storage_guard_v1 as G

R=Path(__file__).resolve().parents[2];O=R/'build/bub-menu-candidate-1102-v2'
sha=lambda x:hashlib.sha256(x).hexdigest()


def main():
    G.preflight(private_root=O,reserved_bytes=500000,reserved_files=3,fresh=True)
    scripts=[
        'profile_bub_clock_bridge_1102_v46.py','audit_bub_auth_lifetime_1102_v48.py',
        'measure_bub_resident_compaction_1102_v49.py','measure_bub_scoped_auth_1102_v50.py',
        'check_bub_scoped_auth_interrupts_1102_v51.py',Path(__file__).name]
    receipts=['clock-bridge-profile-v46.json','auth-lifetime-v48.json','resident-compaction-v49.json',
        'scoped-auth-v50-measurement.json','scoped-auth-v51-ISR.json']
    sources=['auth-frame-v49-reproduce','auth-frame-v49-compact','auth-scope-v50-owner','auth-scope-v50-routes']
    files=[R/'tools/audit'/n for n in scripts]+[O/n for n in receipts]
    files += [O/(stem+suffix) for stem in sources for suffix in ['.s','.cfg','.bin','.lbl']]
    files += [O/('auth-scope-v50-'+n+'.bin') for n in ['route-veneers','route-foreign','route-foreign-bank',
        'route-scene-gate','route-scene-own','route-retire-stub','typed-contact']]
    # These are the exact small source inputs, not their recursive historical
    # dependency graphs. Current ROMs and inherited checkpoints are hash-only.
    files += [R/'tools/audit/measure_bub_landing_1102_v21.py',
        R/'build/bubble-bobble-source-1101-v1/native-event-v9-owner.s',
        R/'build/bubble-bobble-source-1101-v1/native-event-v9-owner.lbl',
        R/'build/bubble-bobble-source-1101-v1/native-proxy-routes.s',
        R/'build/bubble-bobble-source-1101-v1/native-proxy-routes.cfg',
        R/'build/bubble-bobble-source-1101-v1/native-proxy-routes.lbl',
        O/'landing-v21-layout.json',O/'combined-current-landing.json']
    files=list(dict.fromkeys(files));assert len(files)==len(set(files))
    members={str(p.relative_to(R)).replace('\\','/'):p.read_bytes() for p in files}
    assert all(not n.endswith(('.nes','.dbg','.o','.png','.zip')) for n in members)
    for name in receipts:
        q=json.loads((O/name).read_text());assert q['passed']
        for path,digest in q.get('bindings',{}).items():
            assert sha((R/path).read_bytes())==digest,(name,path)
    v50=json.loads((O/'scoped-auth-v50-measurement.json').read_text())
    v51=json.loads((O/'scoped-auth-v51-ISR.json').read_text())
    assert v50['qualified'] is v51['qualified'] is False
    assert v50['rejected_unannounced_writer_control']['qualification'] is False
    # Read one exact archived scheduler source member directly in memory.
    inherited=json.loads((O/'auth-lifetime-v48.json').read_text())['inherited_dedicated_byte_evidence']
    archive=R/inherited['archive'];assert sha(archive.read_bytes())==inherited['SHA256']
    with zipfile.ZipFile(archive) as z:data=z.read(inherited['member'])
    assert sha(data)==inherited['member_SHA256']
    members['inherited-source/rogue_dawn_audio_scheduler_hooks_v5.s']=data
    commit=O/'performance-source-commit-files-v52.txt'
    commit_text='\n'.join('tools/audit/'+n for n in scripts)+'\n'
    commit.write_text(commit_text)
    members[str(commit.relative_to(R)).replace('\\','/')]=commit_text.encode()
    manifest={n:dict(bytes=len(data),sha256=sha(data)) for n,data in sorted(members.items())}
    dst=O/'performance-source-v52.zip';assert not dst.exists()
    with zipfile.ZipFile(dst,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,data in sorted(members.items()):z.writestr(n,data)
    with zipfile.ZipFile(dst) as z:
        assert set(z.namelist())==set(members)
        for name,item in manifest.items():assert sha(z.read(name))==item['sha256']
    out=dict(passed=True,checkpoint_only=True,ROM_written=False,native=False,
        ROM_SHA256='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15',
        installed_ROM_unchanged=True,cache_candidate_qualified=False,lease_bit_granted=False,
        archive=dict(path=str(dst.relative_to(R)),bytes=dst.stat().st_size,sha256=sha(dst.read_bytes()),members=len(manifest)),
        source_commit_files=['tools/audit/'+n for n in scripts],members=manifest,
        measured_summary=dict(current_empty_idle_Main_CPU=47529,full_checks_per_Main=13,
            full_auth_CPU_per_Main=10088,prototype_empty_Main_saved_CPU=9276,
            prototype_saving_percent_about=19.26,owner_bytes=531,dispatch_bytes=192,
            callback_entry_exit_AXYP_SP_SMC_R0_7_maps_exact=13,new_gate_IRQ_cuts=48,new_gate_lagNMI_cuts=48),
        retained_negative=v50['rejected_unannounced_writer_control'],
        scope='Original one-NMI scheduler opportunity proof and current9cf budget; source-exact resident funding; conditional byte/cycle prototype and actual ISR continuations. No scoped-cache safety/admission/native timing/60Hz claim. The unannounced-header-writer negative is intentionally retained; complete current writer/Main/direct-call/owner lifetime proof remains mandatory.',
        external_read_only_inputs=dict(current_ROM='build/bub-menu-candidate-1102-v2/combined-current-landing.nes',
            dedicated_protocol_archive=inherited,previous_landing_checkpoint='docs/qa/checkpoints/2026-11-02/bub-landing-v27'),
        no_capture_cleanup_requested=True,no_recursive_expansion=True)
    receipt=O/'performance-source-v52.json';assert not receipt.exists()
    receipt.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,archive=out['archive'],receipt=str(receipt.relative_to(R)),
        receipt_SHA256=sha(receipt.read_bytes()),source_commit_list=str(commit.relative_to(R)),
        task_storage=G.inventory(O,G.TASK_BYTES,G.TASK_FILES))))


if __name__=='__main__':main()
