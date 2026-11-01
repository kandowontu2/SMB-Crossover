"""Freeze the tested menu-only repair and replace Downloads, with no backup."""
from pathlib import Path
import hashlib,json,shutil,zipfile
from build_storage_guard_v1 import preflight
R=Path(__file__).resolve().parents[2];J=R/'build/menu-wwf-compact-1101-v1';O=R/'build/menu-wwf-compact-native-1101-v1'
EXPECTED='e40109ff598e060a4ad384a7cf77bafccfefbe2efa79599f817f832c93fca019'
PARENT='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def bindings(q):
    for section in ['bindings','input_objects','main_source_inputs']:
        for name,h in q.get(section,{}).items():
            p=Path(name);p=p if p.is_absolute()else R/p;assert sha(p)==h,p


def main():
    assert not(O/'binding.json').exists();assert sha(J/'candidate.nes')==EXPECTED
    stage=json.loads((J/'assembly-stage.json').read_text());cpu=json.loads((J/'menu-CPU-controls.json').read_text())
    for q in [stage,cpu]:assert q['passed']and q['ROM_sha256']==EXPECTED;bindings(q)
    assert cpu['menu_identities']==90 and cpu['playable']==85 and cpu['Start_A_cases']==720
    source=J/'source-and-proof.zip';source_handoff=json.loads((J/'handoff.json').read_text())
    assert sha(source)==source_handoff['archive']['sha256']
    with zipfile.ZipFile(source)as z:
        for n,h in json.loads(z.read('source-file-hashes.json')).items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
    native_files={};proofs={}
    for n in ['menu','hogan','dibiase','bam','honky','savage','andre']:
        p=O/n;ready=json.loads((p/'ready.json').read_text());bindings(ready)
        binding=json.loads((p/'capture/binding.json').read_text());q=json.loads((p/'capture/result.json').read_text())
        assert binding['exit_code']==0 and binding['ready_sha256']==sha(p/'ready.json')
        assert q['passed']and q['ROM_sha256']==binding['ROM_sha256']==EXPECTED
        files=[f for f in p.rglob('*')if f.is_file()];assert len(files)<=64 and sum(f.suffix=='.png'for f in files)<=4
        for f in files:native_files[n+'/'+f.relative_to(p).as_posix()]=f
        if n=='menu':assert len(q['transitions'])==124 and not q['anomalies']and q['heading_errors']==q['visible_mask_writes']==0
        else:assert q['main_updates']==30 and q['frontend_diagnostic']and set(['selected','lives','game'])<=set(q['body_DMA'])
        proofs[n]=q
    native_files['opening-suite.json']=O/'opening-suite.json'
    for n in ['prepare_wwf_compact_menu_native_1101_v1.py','prepare_wwf_compact_opening_native_1101_v1.py','deliver_wwf_compact_nightly_1101_v1.py']:native_files['tools/audit/'+n]=R/'tools/audit'/n
    manifest={n:dict(bytes=p.stat().st_size,sha256=sha(p))for n,p in native_files.items()}
    archive=O/'native-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sorted(native_files.items()):z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert archive.stat().st_size<1000000
    dest=R/'docs/qa/checkpoints/2026-11-01/ready85-compact-menu-native-v1';assert not dest.exists();dest.mkdir()
    shutil.copyfile(source,dest/'source.zip');shutil.copyfile(archive,dest/'native-results.zip')
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');old=sha(nightly);assert old==PARENT
    # User explicitly requests replacement of this one file, without backups.
    shutil.copyfile(J/'candidate.nes',nightly);assert sha(nightly)==EXPECTED
    summary=dict(passed=True,installed=True,backup_created=False,destination=str(nightly),output_sha256=EXPECTED,replaced_sha256=old,playable_identities=85,total_menu_identities=90,new_identities=[],change='Six WWF selection previews use existing original-body16x32 menu art, preventing overlap with gray roster and name. Full-size lives/gameplay sprites remain.',ROM_changed_bytes=stage['changed_bytes'],allowed_ROM_range=stage['allowed_ROM_range'],source=dict(path=str((dest/'source.zip').relative_to(R)).replace('\\','/'),sha256=sha(dest/'source.zip'),bytes=(dest/'source.zip').stat().st_size),native=dict(path=str((dest/'native-results.zip').relative_to(R)).replace('\\','/'),sha256=sha(dest/'native-results.zip'),bytes=(dest/'native-results.zip').stat().st_size),CPU=dict(menu_identities=90,playable=85,unchanged_non_WWF_contexts=84,Start_A_cases=720,X_all_indices_flags=8192),menu=dict(transitions=124,observed_frames=2480,physical_frames=proofs['menu']['frames'],gray_roster_anomalies=0,heading_errors=0,visible_mask_writes=0),opening={n:dict(Main=q['main_updates'],frames=q['frames'],ISR_returns=q['counters']['vectors'],source_updates=q['counters']['source'],minimum_ISR_SP=q['minimum_ISR_SP'],compact_selected=True,original_lives_game_art=True)for n,q in proofs.items()if n!='menu'},checkpoint=str(dest.relative_to(R)).replace('\\','/'),limits=['Menu-only193-byte repair within the original234-byte routine; engine/level/CHR bytes unchanged.','Six WWF30-Main openings qualify menu-to-lives/game restoration, not new full-stage/combat/upgrade/audio tests. Existing85 admission comes from prior checkpoints.','Karnov/Metal Storm/Shinobi/Excitebike remain private source/host progress; no new playable identities in this delivery.','Private Karnov still uses older85 parent; carry this exact compact menu repair into its next composition before any eventual release.'],storage=preflight(fresh=True))
    (dest/'handoff.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (dest/'README.md').write_text('''# Current85 compact WWF menu repair

The six WWF colored previews now use the existing16x32 original-body menu art.
Full-size source poses previously overlapped the bottom gray roster row and,
for some wrestlers, the selected name. Their lives/gameplay graphics stay full
size. The source change fits the same234-byte routine, alters193 ROM bytes,
keeps all public entry addresses and adds no RAM or stack slots.

CPU checks cover90 identities,720 Start/A cases,8192 X/flag combinations and
exact whole-application outputs for84 non-WWF contexts. The six WWF changes are
compared against the existing compact art pipeline with explicit draw-local
metadata differences and unchanged persistent identity/health/gear state.

The native sweep covers124 transitions/2480 observed frames, requiring an
unchanged sampled gray roster, exact heading and zero visible PPUMASK writes.
All six wrestlers then start through the real menu into their original lives
and gameplay display for30 Main updates each, with actual ISR-return checks.
This is a menu regression qualification, not another full-stage test.

Downloads was replaced directly, with no backup. Playable count remains85.
Original-source character components and private Karnov opening remain separate;
they are not unlocked by this delivery. Exact hashes/scopes are in handoff.json.
''',encoding='utf-8')
    (O/'binding.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))


if __name__=='__main__':main()
