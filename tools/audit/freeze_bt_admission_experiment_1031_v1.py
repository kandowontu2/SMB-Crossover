"""Save BT admission source plus failed native evidence, without publishing ROM."""
from pathlib import Path
import hashlib
import json
import zipfile

R=Path(__file__).resolve().parents[2]
J=R/'build/bt-ready-menu-1031-v2/joint'
D=R/'docs/qa/checkpoints/2026-10-31/bt-admission-experiment-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not D.exists()
    stage=J.parent/'source-stage.json';s=json.loads(stage.read_text())
    assert s['candidate']=='f0b7b9b80ac59b546cee599b9efcb5337b970b11638a669ace78a67dd024724d'
    for p,h in s['bindings'].items():assert sha(p)==h,p
    files={Path(__file__),stage,*[J/n for n in ['src/character_select.s','src/full_roster_menu.s','bt/api.s','bt/loader.s','bt/stream.s','private.cfg','entrypoint.s']]}
    tools=[R/'tools/audit'/n for n in ['prepare_bt_ready_menu_1031_v1.py','prepare_bt_ready_menu_1031_v2.py',
           'prepare_bt_ready_native_1031_v1.py','prepare_bt_lives_diagnostic_1031_v1.py','prepare_bt_visible_native_1031_v1.py']]
    files.update(tools)
    for p in J.parent.glob('*.json'):files.add(p)
    files.update(p for p in (R/'build/bt-ready-menu-1031-v1').glob('*.json')if p.is_file())
    roots=[R/'build/bt-ready-native-1031-v1',R/'build/bt-ready-native-1031-v2',R/'build/bt-lives-diagnostic-1031-v1']
    for root in roots:
        files.update(p for p in root.rglob('*')if p.is_file())
    assert all(p.suffix.lower()in['.s','.inc','.cfg','.py','.json','.lua','.csv','.png','.log']for p in files)
    assert sum(p.stat().st_size for p in files)<8*1024*1024
    D.mkdir(parents=True)
    archive=D/'source-and-failed-native.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    manifest=dict(status='EXPERIMENT_SOURCE_MENU_PASS_NATIVE_REJECTED_DO_NOT_ADMIT',candidate=s['candidate'],
                  installed=False,native_admitted=False,readiness_installed=68,source_menu_ready=70,individual_identities=86,
                  actual_native_findings=['Selected Rash8parts/488pixels and own source palettes/name pass.',
                    'Lives P0[22,39,24]/P1[28,54,23] persist until entrance: late text path overwrites original colors.',
                    'BtMovement/CoreStep execute60times/90gameframes, but gameplay body invisible: BtDraw runs without BtGraphics preparation.',
                    'Two-player CheckPlayerName later overwrites guest status prefix; cosmetic limitation remains.'],
                  actual_native_result='Failures and explicit diagnostic-only exit1 retained. No successful admission/native claim.',
                  source_menu_only_claim='Both real Select variants resolve/Start; current68 source menus/Main remain preserved. This is insufficient for native unlock.',
                  storage_workspace_bytes_last_native_preflight=55692074819,storage_cap_bytes=70000000000,
                  files={p.relative_to(R).as_posix():sha(p)for p in sorted(files)},
                  archive_sha256=sha(archive),archive_members=len(files),goal_complete=False)
    (D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    (D/'README.md').write_text('Private source experiment only. Native testing rejected admission: wrong lives colors and an invisible gameplay body. The correct selection image and successful movement do not qualify an unlock. A separate source successor must fix both defects and pass visible-body emulator checks. Downloads remains the verified68-character build.\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(checkpoint=str(D),members=len(files),archive_bytes=archive.stat().st_size,native_admitted=False)))


if __name__=='__main__':main()
