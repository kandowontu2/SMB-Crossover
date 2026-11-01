"""Preserve private menu/native opening progress, without playable admission."""
from pathlib import Path
import hashlib,json,zipfile
from build_storage_guard_v1 import preflight
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-host-resource-base-1101-v1';D=O/'menu-checkpoint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def validate(q):
    for p,h in q['bindings'].items():assert sha(p)==h,p


def pack(path,files):
    manifest={n:dict(sha256=sha(p),bytes=p.stat().st_size,original=str(p.resolve()))for n,p in files.items()}
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sorted(files.items()):z.writestr(n,p.read_bytes())
        z.writestr('files.json',json.dumps(manifest,indent=2)+'\n')
    assert path.stat().st_size<600000
    return dict(file=path.name,sha256=sha(path),bytes=path.stat().st_size,members=len(files)+1)


def main():
    preflight(private_root=O,reserved_bytes=1200000,reserved_files=4,fresh=True)
    proofs={n:json.loads((O/n).read_text())for n in ['terrain-assembly.json','scene-CPU-controls.json','ingress-CPU-controls.json','render-art.json','terrain-CPU-controls.json','render-CPU-controls.json','shot-motion-CPU-controls.json','terrain-vectors.json','menu-CPU-controls.json']}
    candidate=sha(O/'candidate.nes')
    for n,q in proofs.items():
        assert q['passed']and(n=='render-art.json'or q['ROM_sha256']==candidate);validate(q)
    native={};native_files={}
    for name,root in [('menu',R/'build/karnov-menu-native-1101-v2'),('opening',R/'build/karnov-native-opening-1101-v1/run2')]:
        ready=json.loads((root/'ready.json').read_text());validate(ready)
        binding=json.loads((root/'capture/binding.json').read_text());q=json.loads((root/'capture/result.json').read_text())
        assert binding['exit_code']==0 and q['passed']and q['ROM_sha256']==binding['ROM_sha256']==candidate
        assert binding['ready_sha256']==sha(root/'ready.json')
        files=[p for p in root.rglob('*')if p.is_file()];assert len(files)<=64 and sum(p.suffix=='.png'for p in files)<=4
        for p in files:native_files[name+'/'+p.relative_to(root).as_posix()]=p
        native[name]=q
    assert native['menu']['heading_errors']==native['menu']['visible_mask_writes']==0 and len(native['menu']['transitions'])==124
    assert native['opening']['Main']==288 and native['opening']['background_checks']==422 and native['opening']['jumped']and native['opening']['landed']
    # Read one immediate prior manifest; do not expand any dependency archive.
    prior=R/'docs/qa/checkpoints/2026-11-01/karnov-scene-component-v1/source-proof.zip'
    with zipfile.ZipFile(prior)as z:manifest=json.loads(z.read('files.json'))
    files={n:Path(q['original'])for n,q in manifest.items()}
    for n in ['prepare_karnov_menu_1101_v1.py','check_karnov_menu_1101_v1.py','probe_karnov_menu_paths_1101_v1.py','prepare_karnov_menu_native_1101_v1.py','prepare_karnov_menu_probe_native_1101_v1.py','prepare_karnov_opening_native_1101_v1.py','freeze_karnov_menu_1101_v1.py']:
        files['tools/audit/'+n]=R/'tools/audit'/n
    files['tools/reference/karnov_host_menu_1101_v1.inc']=R/'tools/reference/karnov_host_menu_1101_v1.inc'
    files['tools/reference/karnov_menu_probe_native_1101_v1.lua']=R/'tools/reference/karnov_menu_probe_native_1101_v1.lua'
    for n in ['full_roster_menu.s','full_roster_menu_art.inc','new_roster_dispatch.s','kr-menu.inc','kr-native-bg.bin','menu-CPU-controls.json']:files['host/'+n]=O/n
    for n,p in [('full_roster_menu.s',R/'build/doki-current-component-1101-v1/menu/full_roster_menu.s'),('full_roster_menu_art.inc',R/'build/hogan-thomas-current/src/full_roster_menu_art.inc'),('new_roster_dispatch.s',R/'build/ready76-visible/new_roster_dispatch.s')]:files['parent-source/'+n]=p
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(nightly)=='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
    D.mkdir(exist_ok=True)
    source=pack(D/'source-proof.zip',files);natives=pack(D/'native-results.zip',native_files)
    a,s,m,c=[proofs[n]for n in ['terrain-assembly.json','scene-CPU-controls.json','menu-CPU-controls.json','render-CPU-controls.json']]
    result=dict(passed=True,progress_only=True,private_menu_enabled=True,native_opening=True,native_admitted=False,installed=False,playable=85,private_selectable=86,total_menu_identities=90,private_candidate=candidate,installed_nightly=sha(nightly),source_proof=source,native_proof=natives,resident_bytes=a['resident_bytes'],kernel_bytes=a['kernel_bytes'],real_Select_Start_A_cases=m['real_Select_Start_A_cases'],old_menu_contexts_unchanged=m['legacy_menu_contexts_unchanged'],real_Karnov_Select_Start=s['real_Karnov_Select_Start'],actual_Main_ISR_cuts=s['actual_Main_ISR_cuts'],minimum_Main_ISR_SP=s['minimum_Main_ISR_SP'],palette_queue_contexts=c['palette_queue_cases'],actual_palette_NMI_contexts=c['actual_native_palette_NMI'],native_menu=dict(transitions=124,physical_frames=native['menu']['frames'],heading_errors=0,visible_mask_writes=0),native_opening_results={k:v for k,v in native['opening'].items()if k not in ['display','scope','reason']},fixed=['Karnov now resolves to real runtime34 through normal Select/Start; his alternate bit survives native fresh-game cleanup.','Immutable ROM portrait/name/palette handlers work before any RAM cache construction. Guarded typed UI routing admits runtime34 rather than indexing legacy12-owner tables.','Actual native opening caught black sky inherited from lives. Both cold and initialized colors now restore the exact native area/control backdrop; menu stays black.'],previous='docs/qa/checkpoints/2026-11-01/karnov-scene-component-v1',next=['Audit remaining direct-ID inventory/cheat/collision leaves, retaining full old-owner equivalence.','Implement native projectile/enemy/block effects, health/injury, stomp bounce, earned source gear/options and original audio.','Qualify actual normal1-1 and shortcut/item/scene behavior before user-facing admission and nightly replacement.'],limits=['Installed nightly stays85; private selectable86 is not playable86 qualification.','Opening stops at worldX221/camera141, with no enemy defeat/damage or controller-earned powerup. Source shot updates are observed; native projectile pixel/hit qualification remains.','Menu gate proves heading stability and zero visible PPUMASK writes across124 transitions. Static gray-portrait overlap diagnostics remain; this is not a claim that every menu pixel is clean.','Source audio is not connected. Native APU activity is the existing host audio, not a Karnov-track proof.','Earlier native menu-rectangle suspicion was not reproduced as a candidate regression: complete Mario screenshots matched the installed baseline byte-for-byte at the pixel level.'],storage=preflight(fresh=True))
    (D/'handoff.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (D/'README.md').write_text('''# Karnov cold menu and native opening — private progress

Normal Select on Rygar now selects original Karnov, with his real idle body,
palette and name; Start retains runtime34 and loads the guarded source actor.
The other89 menu contexts match their old OAM, graphics selection and queues.
All85 old scene owners keep their outputs and existing public entry addresses.

One native controller opening passes288 Main updates, source actor and projectile
updates, jump/landing and camera141. Original body art is observed on selection,
lives and gameplay. Real ISR returns preserve registers and SMC. This opening
does not encounter combat or collect an upgrade and does not clear1-1.

The first native run exposed a black sky retained from the lives screen. The
four-color writer now restores the actual native area's universal background.
132 queue contexts and22 real NMI writer contexts cover native background
control and both source body palettes;422 native gameplay frames check the fix.
The current candidate also passes the124-transition heading/PPUMASK menu gate.
Existing tall-portrait overlap diagnostics are retained for later cleanup.

Combat, injury/health, earned source equipment, option usage, source audio and
remaining raw-ID leaf audits still precede playable admission. Downloads keeps
the tested85-character nightly. No new-nightly or playable86 claim is made.

The two ZIPs contain exact small source/assets/receipts and bounded native
controllers/results, excluding ROMs, linker/debug objects and video sequences.
The prior source checkpoint is historical; use this packet for the new hash.
''',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
