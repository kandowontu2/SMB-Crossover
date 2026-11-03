"""One compact source checkpoint and exact current-Sunny memory-only rebase."""
import hashlib,json,subprocess,tempfile,zipfile
from pathlib import Path

R=Path(__file__).resolve().parents[2];O=R/'build/bub-menu-candidate-1102-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'
SUNNY='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b'
PRIVATE='be8095fd18cbb3f1d2eac96a20c6600c16acb7e86052c04e18f0fe75b22c8d55'
COMBINED='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def main():
    manifest=O/'landing-v21-proposal.json';m=json.loads(manifest.read_text())
    assert sha(manifest)=='061172eb97e12a3303553e10e06df81274e5a3d032e5cef6205ade2a4f851351'
    assert m['base_ROM_sha256']==BASE and m['expected_candidate_sha256']==PRIVATE
    for rel,z in m['files'].items():assert sha(R/rel)==z['SHA256'],rel
    # The two flattened assembly sources are complete link inputs. Verify
    # them independently without replaying an old build dependency graph.
    cc=R/'tools/Windows/cc65/bin';linked=[]
    with tempfile.TemporaryDirectory(prefix='landing-source-link-',dir=O)as tmp:
        t=Path(tmp).resolve();assert t.is_relative_to(O.resolve())
        for stem in['leaves','helpers']:
            src=O/f'landing-v21-{stem}.s';cfg=O/f'landing-v21-{stem}.cfg'
            cfgtext=cfg.read_text().replace(O.as_posix()+'/landing-v21-',t.as_posix()+'/landing-v21-')
            assert O.as_posix()+'/landing-v21-'not in cfgtext
            tc=t/(stem+'.cfg');tc.write_text(cfgtext)
            for command in[[cc/'ca65.exe',src,'-o',t/(stem+'.o')],
                            [cc/'ld65.exe','-C',tc,t/(stem+'.o'),'-o',t/f'landing-v21-{stem}.bin']]:
                z=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert z.returncode==0,z.stderr
            names=['leaves','actor-hole','box-hole','sound-hole','admission']if stem=='leaves'else['helpers']
            for name in names:
                p=t/f'landing-v21-{name}.bin';expected=O/p.name
                assert p.read_bytes()==expected.read_bytes(),name;linked.append(dict(part=name,bytes=p.stat().st_size,SHA256=sha(p)))
        assert t.is_relative_to(O.resolve()) # exact scoped temporary cleanup
    sunny_receipt=R/'docs/qa/checkpoints/2026-11-02/sunny-palette-v9/receipt.json'
    s=json.loads(sunny_receipt.read_text());assert s['base_ROM_SHA256']==BASE and s['ROM_sha256']==SUNNY
    base=(R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes').read_bytes();assert hashlib.sha256(base).hexdigest()==BASE
    private=(O/'combined-landing.nes').read_bytes();assert hashlib.sha256(private).hexdigest()==PRIVATE
    raw=bytearray(base);domains=[]
    for rows in[s['patches'],m['patches']]:
        domain=set()
        for p in rows:
            a=p['offset'];old=bytes.fromhex(p['old']);new=bytes.fromhex(p['new'])
            assert len(old)==len(new)and base[a:a+len(old)]==old
            span=set(range(a,a+len(old)));assert not domain&span;domain|=span
            raw[a:a+len(new)]=new
        domains.append(domain)
    assert not domains[0]&domains[1]and hashlib.sha256(raw).hexdigest()==COMBINED
    current=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();assert hashlib.sha256(current).hexdigest()==SUNNY
    test=bytearray(current)
    for p in m['patches']:
        a=p['offset'];old=bytes.fromhex(p['old']);assert test[a:a+len(old)]==old;test[a:a+len(old)]=bytes.fromhex(p['new'])
    assert test==raw
    proposal=O/'landing-rebase-v27-proposal.json'
    assert not proposal.exists()
    proposal.write_text(json.dumps(dict(passed=True,proposal_only=True,ROM_written=False,native=False,installed=False,
        source_base_ROM_sha256=BASE,current_base_ROM_sha256=SUNNY,qualified_private_parent_sha256=PRIVATE,
        expected_rebased_ROM_sha256=COMBINED,patches=m['patches'],actual_Bub_changed_bytes=370,
        Sunny_five_patches_preserved=True,exact_byte_intervals_disjoint=True,
        existing_landing_private_approval='Root approved exactv21 three-span private landing patch; current16a9 composition remains a proposal pending source/native review.',
        native_status='v24 clears4pipes/2pits/natural15pops, v26 repeatsfirstfinalstairX2369 despite healthy source/observer. Full1-1 stillopen; v28 exactstairdiagnostic prepared. No production qualification or delivery claimed.',
        binding=dict(landing_manifest=sha(manifest),Sunny_checkpoint=sha(sunny_receipt))),indent=2)+'\n')
    sources=[
        'check_bub_runtime_facing_1102_v19.py','check_menu_family_simultaneous_1102_v19.py',
        'check_bub_stair_route_1102_v20.py','measure_bub_landing_1102_v21.py',
        'check_bub_landing_1102_v21.py','check_bub_landing_transport_1102_v21.py',
        'freeze_bub_landing_proposal_1102_v21.py','compose_bub_landing_1102_v21.py',
        'prepare_bub_landing_native_1102_v21.py','check_bub_rearm_phase_1102_v22.py',
        'prepare_bub_rearm_native_1102_v22.py','prepare_bub_intercept_native_1102_v23.py',
        'prepare_bub_intercept_observer_1102_v24.py','check_bub_final_stair_gap_1102_v25.py',
        'prepare_bub_final_stair_native_1102_v25.py','prepare_bub_final_stair_native_1102_v26.py',
        'prepare_bub_stair_diagnostic_1102_v28.py',Path(__file__).name]
    paths=[R/'tools/audit'/x for x in sources]
    names=['runtime-facing-v19.json','runtime-facing-v19.png','menu-family-simultaneous-v19.json','stair-route-v20-CPU.json',
        'landing-v21-layout.json','landing-v21-image.bin','landing-v21-helper.chr','landing-v21-CPU.json',
        'landing-v21-transport-CPU.json','landing-v21-proposal.json','combined-landing.json',
        'combined-landing.dbg','combined-landing.lbl','rearm-phase-v22-CPU.json','intercepted-route-v23.json',
        'callback-watchdog-v24.json','final-stair-gap-v25-CPU.json','final-stair-gap-v26-contract.json']
    names += ['landing-v21-'+stem+suffix for stem in['leaves','helpers']for suffix in['.s','.cfg','.lbl','.bin']]
    names += ['landing-v21-'+stem+'.bin'for stem in['actor-hole','box-hole','sound-hole','admission']]
    paths += [O/x for x in names]+[proposal,sunny_receipt]
    # Exact controller inputs only, never rehydrate entire native/source trees.
    controllers=['native-event-bub-full11-wide',
        'native-landing-bub-full11','native-landing-bob-full11',
        'native-landing-bub-full11-rearm2','native-landing-bob-full11-rearm2',
        'native-landing-bub-full11-intercept','native-landing-bob-full11-intercept',
        'native-landing-bub-full11-intercept2','native-landing-bub-full11-final-stair',
        'native-landing-bub-full11-supported-stair','native-landing-bob-full11-supported-stair',
        'native-landing-bub-stair-diagnostic']
    paths += [O/c/'controller.lua'for c in controllers]
    paths += [O/c/n for c in controllers[-3:]for n in['ready.json','run.py']]
    # These exact small negative receipts are direct inputs of the new source
    # preparers. Keep them once, without capture screenshots/log forests.
    paths += [O/c/'capture/full11.json'for c in[
        'native-event-bub-full11-wide','native-landing-bub-full11','native-landing-bub-full11-rearm2',
        'native-landing-bub-full11-intercept2','native-landing-bub-full11-supported-stair']]
    paths += [O/'native-landing-bub-full11-intercept/capture'/n for n in['bub-observer.json','combined-landing-controller.log']]
    paths=list(dict.fromkeys(paths));assert all(p.is_file()for p in paths)
    target=O/'landing-source-checkpoint-v27.zip';assert not target.exists()
    before={p:sha(p)for p in paths};assert sum(p.stat().st_size for p in paths)<5_000_000 and len(paths)<128
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for p in paths:archive.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(target)as archive:
        assert len(archive.namelist())==len(paths)
        for p,digest in before.items():assert hashlib.sha256(archive.read(p.relative_to(R).as_posix())).hexdigest()==digest==sha(p)
    receipt=O/'landing-source-checkpoint-v27.json';assert not receipt.exists()
    receipt.write_text(json.dumps(dict(passed=True,source_checkpoint=True,native_full11_passed=False,installed=False,
        archive=target.relative_to(R).as_posix(),archive_SHA256=sha(target),archive_bytes=target.stat().st_size,
        files={p.relative_to(R).as_posix():dict(SHA256=d,bytes=p.stat().st_size)for p,d in before.items()},
        flattened_source_relink_exact=linked,landing18B_funding=dict(dead_telemetry=10,existing_spare=8,new_RAM=0,new_pages=0,new_resident=0),
        current_private_candidate=PRIVATE,current_installed_Sunny=SUNNY,memory_only_rebase_candidate=COMBINED,
        current_native='All4pipes/first2pits/15naturalpops pass; finalstairnativeX2369 loop differs declaredCPUarena. v28 diagnostic ready, Bobheld. v25one-jumpunrunscaffold intentionallysuperseded by v26twosupportedjumpcontract; no fullstageclaim.',
        production_admitted=False,ROM_included=False,archive_bytecompare=True),indent=2)+'\n')
    commit=O/'landing-source-commit-files-v27.txt';assert not commit.exists()
    commit.write_text('\n'.join(['# Exact source-only stage list; root chooses durable checkpoint destination.']+
        ['tools/audit/'+x for x in sources]+[p.relative_to(R).as_posix()for p in[target,receipt,proposal,commit]])+'\n')
    print(json.dumps(dict(passed=True,source_archive=str(target),archive_SHA256=sha(target),archive_bytes=target.stat().st_size,
        files=len(paths),source_relink_exact=True,ROM_written=False,rebase_proposal=str(proposal),expected_rebase_SHA256=COMBINED,
        commit_list=str(commit))))


if __name__=='__main__':main()
