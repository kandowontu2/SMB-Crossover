"""Verify source archive and freeze both root-run factor native checks."""
from pathlib import Path
import hashlib
import json
import zipfile

R = Path(__file__).resolve().parents[2]
S = R/'docs/qa/checkpoints/2026-10-31/smb3plus-low-table-factor-v1'
P = R/'build/smb3plus-low-factor-native-1031-v1'
N = R/'build/smb3plus-low-factor-native-1031-v2'
O = R/'docs/qa/checkpoints/2026-10-31/smb3plus-low-factor-native-v1'
EXPECTED = 'e54b91fa15b335bb17fd24fa7a0b667ef50bf31c8fad900d6c1a1ec38526116a'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()
    assert sha(S/'handoff.json') == 'fea3b4521242846abe7b38053f2bb0283d261c626cd351c1ba48f3d405fdb260'
    h = json.loads((S/'handoff.json').read_text())
    assert h['candidate'] == EXPECTED and len(h['bindings']) == 785
    for p, digest in h['bindings'].items():
        assert sha(p) == digest, p
    members = json.loads((S/'source-members.json').read_text())
    assert len(members) == 699
    with zipfile.ZipFile(S/'source-and-controls.zip') as z:
        assert len(z.namelist()) == len(set(z.namelist())) == 699
        for name, digest in members.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest == sha(R/name)
    files = {Path(__file__), R/'tools/audit/prepare_smb3plus_low_factor_native_retry_1031_v1.py'}
    files.update(p for p in P.rglob('*') if p.is_file())
    files.update(p for p in N.rglob('*') if p.is_file())
    rows = []
    for name, main, lag in [('toad',359,14), ('peach',360,0)]:
        q = N/name/'capture'
        d, binding = [json.loads((q/f).read_text()) for f in ['result.json','binding.json']]
        assert d['passed'] and binding['exit_code'] == 0 and d['ROM_sha256'] == EXPECTED
        for p, digest in binding['bindings'].items():
            assert sha(p) == digest, p
        assert d['gameplay_frames'] == 360 and d['completed_Main_returns'] == main
        assert d['vector_guards'] == 720 and d['timing']['lag_nmi'] == lag
        assert d['jumped'] and d['landed'] and d['body_P0_source_exact']
        png = sorted(q.glob('*.png')); assert len(png) == 4
        parent = R/'build/smb3plus-current66-native-1031-v1'/name/'capture'
        rows.append(dict(identity=name, actual_Main=main, physical_frames=360, real_ISR_restores=720,
            lag_NMIs=lag, timing=d['timing'], actual_UI_DMA=d['actual_UI_DMA_checks'],
            root_reviewed_full_frame_PNGs={p.name: sha(p) for p in png},
            equal_predecessor_captured_PNGs={p.name: sha(p) == sha(parent/p.name) for p in png},
            result_sha256=sha(q/'result.json')))
    assert len(files) < 64 and sum(p.stat().st_size for p in files) < 4194304
    assert all(p.suffix.lower() in ['.py','.lua','.json','.csv','.log','.png'] for p in files)
    O.mkdir(parents=True)
    archive = O/'bounded-native-results.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        for p in files:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    out = dict(passed=True, candidate=EXPECTED, native=True, installed=False, ready_count=68,
        source_bindings_verified=785, source_archive_members_verified=699, native_checks=rows,
        retained_negative='The first rootToad run reached323/360 frames but hit terminal60s Mesen wall timeout, with no latched product assertion or storage-budget violation. New90s packets keep controller bytes,360frames and all file/image/storage limits unchanged. Toad then finished65.458s; Peach56.255s.',
        qualified_use='Source/native-qualified factoring prerequisite for future coherent common join; installed Downloads remains01a4. Source-equivalent graphics table factoring reclaims398B, of which67B has a separate conditional CF source reservation.',
        limits=['Finite menu/lives/idle/walk/jump/hover/land scope; no full1-1 or every-powerup/complete donor special move claim.',
                'Toad still has14 lagNMIs in this run. No general60Hz or complete-roster performance claim.',
                'The reserved CF restore worker is not present in this candidate; CF/BT remain pending.'],
        archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
        members={p.relative_to(R).as_posix(): sha(p) for p in sorted(files)})
    (O/'manifest.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    (O/'README.txt').write_text('Root verified the frozen e54b91fa source785bindings and699 ZIPmembers, then ran both genuine controller-only360-frame policies. All eight full PNGs reviewed; real select/lives OAM/physicalCHR/PPU pixels and720 actual interrupt restore checks each. Toad359Main/14lag and Peach360Main/0lag. Captures and exact scopes are in manifest.json. Initial60s walltimeout is retained;90s retry changes host allowance only, keeping full controller policy and capture/storage caps. No video.\n\nThis qualifies the source factoring as a private common-join prerequisite, not a new installed character, all-level/powerup audit or a completed CF palette repair. Latest Downloads remains01a4. All broader work stays active.\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True, candidate=EXPECTED, archive_bytes=archive.stat().st_size,
        members=len(files), native_checks=[{k:r[k] for k in ['identity','actual_Main','lag_NMIs','equal_predecessor_captured_PNGs']} for r in rows])))


if __name__ == '__main__':
    main()
