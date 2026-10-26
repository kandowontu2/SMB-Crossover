"""Small public rollback/review checkpoint for clean menu/IRQ source only."""
from pathlib import Path
import difflib, hashlib, json, shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'mm-proto-clean-menu-candidates-v1'
BASE = D / 'root-chip-hud-composed-v1'
OUT = R / 'docs/qa/checkpoints/2026-10-26/clean-menu-irq-family'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
load = lambda p: json.loads(Path(p).read_text())


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    assert sha(P/'freeze-v1/receipt.json') == 'c09ef626784647442221799efc8449944a32825bdb85ae30a4fd415d07c51040'
    assert sha(BASE/'candidate.nes') == '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
    assert load(P/'proof.json')['passed'] and load(P/'cpu-v3/proof.json')['passed']
    native = D/'root-presentation450-731-v1/native-receipt.json'
    actual = load(native)
    assert actual['passed'] and actual['ROM_sha256'] == '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
    expected = {'smb1base-mmc5-expanded.cfg','src/character_select.s','src/reset.s','src/menu_vram_budget.s'}
    deltas = {}
    for variant in ['clean-menu','clean-menu-irq']:
        source=P/variant/'source'
        manifest=load(P/variant/'source-manifest.json')
        changed=[]
        for rel,h in manifest.items():
            assert sha(source/rel) == h
            if not (BASE/'source'/rel).exists() or sha(BASE/'source'/rel) != h:
                changed.append(rel)
        assert set(changed) == expected, changed
        assert sha(source/'src/protoman_legacy_shots.inc') == 'ad0241e8872468679f0cb33b7aa4c179e1bd185a3ae45905633f6d304027a73e'
        rows={}
        patch=[]
        for rel in sorted(changed):
            old,new=BASE/'source'/rel,source/rel
            oldtext=old.read_text() if old.exists() else ''
            patch.extend(difflib.unified_diff(oldtext.splitlines(True),new.read_text().splitlines(True),fromfile='published3cee/'+rel,tofile=variant+'/'+rel))
            rows[rel]=dict(parent_sha256=sha(old) if old.exists() else None,candidate_sha256=sha(new),bytes=new.stat().st_size,new_file=not old.exists())
            # Common byte-exact files are shared in the small public packet.
            group=variant if rel=='src/reset.s' else 'common'
            q=OUT/'source-overlay'/group/rel;q.parent.mkdir(parents=True,exist_ok=True)
            if q.exists():assert sha(q)==sha(new)
            else:shutil.copyfile(new,q)
        deltas[variant]=dict(ROM_sha256=sha(P/variant/'candidate.nes'),source_manifest_sha256=sha(P/variant/'source-manifest.json'),changed_inputs=rows,unchanged_inputs=len(manifest)-len(changed))
        (OUT/'source-overlay'/(variant+'.patch')).write_text(''.join(patch))
    (OUT/'source-overlay/delta-manifest.json').write_text(json.dumps(deltas,indent=2)+'\n')
    copies={
        'build/family-proof.json':P/'proof.json',
        'build/menu-proof.json':P/'clean-menu/proof.json',
        'build/menu-irq-proof.json':P/'clean-menu-irq/proof.json',
        'build/menu-prototype-removal.patch':P/'clean-menu/source.patch',
        'build/menu-irq-prototype-removal.patch':P/'clean-menu-irq/source.patch',
        'build/menu-exact-deltas.json':P/'clean-menu/exact-ROM-deltas.json',
        'build/menu-irq-exact-deltas.json':P/'clean-menu-irq/exact-ROM-deltas.json',
        'build/removed-private-symbols.json':P/'clean-menu-irq/removed-genuine-private-symbols.json',
        'CPU/fresh-clean-pair-proof.json':P/'cpu-v3/proof.json',
        'CPU/CLI-deferred.json':P/'cpu-v3/CLI-deferred.json',
        'CPU/schedule.json':P/'cpu-v3/schedule.json',
        'native/ROOT-731-only450-receipt.json':native,
        'native/ROOT-actual-pixel-review.json':native.parent/'ROOT-review-v1/proof.json',
        'reports/clean-source-controls.txt':R/'docs/qa/mm-proto-clean-menu-candidates-2026-10-26.txt',
        'reports/IRQ-component-scope.txt':R/'docs/qa/mm-proto-irq-arm-cpu-2026-10-26.txt',
        'reports/first-active-face-readonly.txt':R/'docs/qa/mm-proto-first-active-face-2026-10-26.txt',
        'external-freeze-receipt.json':P/'freeze-v1/receipt.json',
    }
    for n,p in copies.items():
        q=OUT/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);assert sha(p)==sha(q)
    oldfailure=D/'mm-proto-irq-arm-cpu-v1/failure.json'
    failure=load(oldfailure)
    assert not failure['passed'] and len(failure['completed_NMI'])==1536
    summary=dict(passed=False,classification='v1 checker parity-oracle failure retained, not a game failure or relaxed state assertion',
        error=failure['error'],completed_NMI=1536,original_failure=str(oldfailure),original_failure_sha256=sha(oldfailure),
        correction='Separatev2 requires exact literal preSTA4014+4 parity equation per case; no broad±1 tolerance. Every no-stall code delta0 and all original state/IO guards remain.',
        first_failed_case='SpriteFlag0 char0/title/regular/reload0, modeled1466->1467 because7odd preDMA cycles move, flipping513/514.')
    (OUT/'CPU/v1-parity-negative-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    toolnames=['mm_proto_clean_menu_candidates_v1.py','mm_proto_irq_arm_cpu_v1.py','mm_proto_irq_arm_cpu_v2.py','mm_proto_irq_arm_cpu_v3.py','mm_proto_clean_menu_checkpoint_v1.py']
    for n in toolnames:
        q=OUT/'tools'/n;q.parent.mkdir(exist_ok=True);shutil.copyfile(R/'tools/audit'/n,q)
    frozen_catalog=load(P/'freeze-v1/catalog.json')
    import_hashes={n:v for n,v in frozen_catalog.items() if '/tools/' in n.replace('\\','/') or '/site-packages/py65/' in n.replace('\\','/') or n.endswith('python.exe')}
    (OUT/'tools/import-hashes.json').write_text(json.dumps(import_hashes,indent=2)+'\n')
    paths=[P/'freeze-v1/receipt.json',P/'freeze-v1/catalog.json',P/'freeze-v1/commands.json',P/'freeze-v1/source-archives.json',
           P/'freeze-v1/clean-menu-source.zip',P/'freeze-v1/clean-menu-irq-source.zip',BASE/'source-manifest.json',BASE/'candidate.nes',
           P/'cpu-v3/cases.json',P/'cpu-v3/inputs.json',P/'cpu-v3/IRQ-cases.json',oldfailure,
           D/'mm-proto-irq-arm-cpu-v2/freeze-v1/receipt.json',D/'mm-proto-irq-arm-cpu-v3/freeze-v1/receipt.json',
           native.parent/'readiness.json',native.parent/'launch.json',native.parent/'result.json',native.parent/'ROOT-review-v1/all275-RGB-hashes.json',
           D/'mm-proto-postdma-native-ready-v3/first-active-palette-inspection-v1/opaque-coordinate-colors.json',
           D/'mm-proto-postdma-native-ready-v3/first-active-palette-inspection-v1/compiled-palette-tables.json']+list(copies.values())
    for v in ['clean-menu','clean-menu-irq']:
        paths += [P/v/n for n in ['candidate.nes','candidate.dbg','candidate.map','candidate.lbl','source-manifest.json','canonical.nes','ordinary-mmc3.nes','ordinary-mmc5.nes']]
    refs={str(p):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(paths))}
    (OUT/'external-bindings.json').write_text(json.dumps(refs,indent=2)+'\n')
    readme='''CLEAN MENU / IRQ TIMING FAMILY -- REVIEW CHECKPOINT, 2026-10-26

Source/build/CPU PASS. ROOT's single clean731 startup450 diagnostic PASS.
Full menu1800/heavyHard controls and adoption are NOT claimed by this packet.
No ROM, NSF/audio, ZIP, settings or raw/lossless payload is in this checkpoint.

BASE / VARIANTS
Published3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99.
Clean menu43f84bb4544d2d8ca6be43886857bedd36adb23744ddad5b0a2d650ff14e1bc6.
Clean menu+IRQ731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c.

RESTORE EXACT SOURCE, WITHOUT THE HELD SHOT EXPERIMENT
Start from the frozen published3cee source bound in external-bindings.json.
Copy source-overlay/common's3files, then the chosen variant's src/reset.s.
These are the EXACT4 input changes versus3cee; src/menu_vram_budget.s is new.
The delta-manifest binds all parent/new bytes and unchanged input counts.
Patches are text review aids; the raw full overlay files preserve exact EOLs.
The unchanged original protoman_legacy_shots.inc is SHAad0241e8... on900,
published3cee and the observed default. Do not apply this overlay to an
unrelated current checkout or copy stale inherited .nes/debug outputs.

ROOT/B own the menu admission and post-DMA/IRQ timing repairs. This agent
removed the known unaccepted shot helper from their exact prototypes and
qualified the clean family independently. The MM_PROTO_SHOT_MUX segment is
absent; MENU_VRAM_BUDGET stays pinnedBB50. Each clean version differs from
its c9/59 prototype by EXACT144 PRG66 bytes:3byte originalLDA plus141oldFF.
All61,248 retained genuine qualified symbols/RAM/CHR/other banks are exact;
6real private helper labels are removed, individually listed, without aliases.
The clean pair differs only30bytes in each fixed mirror125/127. Both variants
canonically reproduce and ordinary MMC3/MMC5 builds retain exact hashes.

FRESH CPU, ORIGINAL FAILURE PRESERVED
Exact clean43/731 pair:1786completeNMI,512all-byte input/parity and1042actual
IRQ cases PASS.12physical first-postCLI defer boundaries are explicitly
excluded from immediate py65 injection and documented, not called hardware
acceptance tests. All return/state/5SMC/banks/input/IO reads and every other
ordered nonstack write match. Only5203/5204 ordering changes intentionally;
their values/order match separately. No memory/OAM-byte masks were loosened.
Code-only0cycle cost, PPUMASK advances20/7 codecycles onflag1/0. Modeledtotal
-1..+1 is EXACT the literal recorded preSTA4014+4 DMA-parity equation. The
original v1 failed total0 assumption after1536 passes is retained externally;
its summary and exact tool are included. v2/v3 corrections do not change
source or weaken state/output assertions. All prior08/59/native failures
and heldMM bodies/shot visibility evidence remain unchanged, not retagged.

LIMITED ROOT NATIVE SNAPSHOT
The copied ROOT731450 receipt is one fixed-input MegaEasy startup/menu/first
active diagnostic:402exact256hardwareDMAs,72scoped enables,442NMI and79IRQ31
checks,275actualPPU captures,0late enables and0hardware mismatches. ROOT
viewed8actualframes. This does not establish a full menu run, campaign,
sprite fairness or adoption. It belongs to ROOT's exact731 fixture only.
First-visible green-face impression also exists on old3cee; separate report
shows a background-shaped face hole, not green body colors. Old372 OAM/CHR
owner is unlogged, and731 runtime palette numbers are not invented here.

REVIEW / REPRODUCE
Read reports/clean-source-controls.txt and the component scope report for
exact commands and synthetic limits. tools/ contains exact small builder and
CPU versions; import-hashes.json plus external-bindings.json bind reused
modules and complete immutable source ZIPs/manifests without copying them.
Use create-only NEW external outputs for rebuild/requalification. Included
readiness/proofs are evidence, never a fresh permission to launch an emulator.
No staging/commit/push, production/default/settings mutation or Mesen run was
performed by this checkpoint builder. Native grants remain ROOT-controlled.
'''
    (OUT/'README.txt').write_text(readme)
    (OUT/'review-files.json').write_text(json.dumps(dict(owned_stage_paths=[OUT.relative_to(R).as_posix()],
        only_this_owned_checkpoint_directory=True,stage_global_production_or_binary_files=False,
        optional_original_owned_tools=[str(R/'tools/audit'/n) for n in toolnames],
        no_global_tool_staging_required=True),indent=2)+'\n')
    catalog={p.relative_to(OUT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file()}
    assert all(Path(n).suffix.lower() not in ['.nes','.nsf','.nsfe','.dmc','.zip','.gz','.wav','.mp4','.argb'] for n in catalog)
    (OUT/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    result=dict(checkpoint_integrity_passed=True,source_build_CPU_controls_passed=True,
        ROOT_native450_passed=True,full_menu_or_heavy_native_acceptance_claim=False,adopted=False,
        source_delta_against_published3cee_exact_four_inputs_each=True,shot_budget_helper_absent=True,
        ROMs={v:deltas[v]['ROM_sha256'] for v in deltas},
        external_freeze_sha256=sha(P/'freeze-v1/receipt.json'),fresh_CPU_proof_sha256=sha(P/'cpu-v3/proof.json'),
        ROOT_native450_receipt_sha256=sha(native),catalog_files=len(catalog),catalog_sha256=sha(OUT/'catalog.json'),
        public_payload_bytes=sum(x['bytes'] for x in catalog.values()),external_bindings=len(refs),
        external_bindings_sha256=sha(OUT/'external-bindings.json'),builder_sha256=sha(__file__),
        no_ROM_audio_ZIP_settings_lossless_payload=True,staging_or_Git_or_native_or_production_actions=False)
    (OUT/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),proof_sha256=sha(OUT/'proof.json'),**result),indent=2))


if __name__=='__main__':
    main()
