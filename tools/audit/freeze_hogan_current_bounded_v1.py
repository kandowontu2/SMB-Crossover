"""Freeze the small current-Hogan delta and honest pending native evidence."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/hogan-current';J=R/'build/hogan-adapter'
O=R/'build/hogan-current-review'
D=R/'docs/qa/checkpoints/2026-10-31/hogan-current-camera-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not O.exists()and not D.exists()
    for root in [P,J]:
        q=json.loads((root/'source-stage.json').read_text())
        assert q['passed']and q['candidate']==sha(root/'candidate.nes')
        for p,h in q['bindings'].items():assert sha(p)==h,p
    controls=J/'checks/controls.json';c=json.loads(controls.read_text())
    assert c['passed']and not c['native']and c['candidate']==sha(J/'candidate.nes')
    for p,h in c['bindings'].items():assert sha(p)==h,p
    g=c['gameplay'];assert g['gameplay_Main']==607 and g['maximum_camera']==257 and g['native_defeat_calls']==1
    old=R/'build/hogan-native-review';negative=json.loads((old/'record.json').read_text())
    assert not negative['passed']and not negative['qualified']and sha(old/'native-attempt.zip')==negative['archive_sha256']
    O.mkdir();D.mkdir(parents=True)
    tools=['join_hogan_current_bounded_v1.py','fix_hogan_camera_bounded_v1.py',
           'check_hogan_current_bounded_v1.py','trace_hogan_cold_scroll_v1.py',
           'prepare_hogan_native_bounded_v1.py','freeze_hogan_native_attempt_v1.py',
           'freeze_hogan_current_bounded_v1.py','run_bounded_build_v1.py',
           'check_build_storage_guard_v1.py']
    files={R/'tools/audit'/n for n in tools}
    files|={R/'tools/reference/hogan_native_bounded_v1.lua',controls,P/'scroll-cpu/trace.json',old/'record.json'}
    for root in [P,J]:
        files|={p for p in root.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg','.dep']}
        files|={p for p in root.glob('*.json')}
    files|={J/'cookie.bin'}
    assert len(files)<90 and sum(p.stat().st_size for p in files)<2_000_000
    archive=D/'source-only.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    shutil.copyfile(old/'native-attempt.zip',D/'native-incomplete.zip')
    parents={
        'original_Hogan':'docs/qa/checkpoints/2026-10-31/wwf-hogan-basic-loop-source-v3/handoff.json',
        'current_CF':'docs/qa/checkpoints/2026-10-31/contra-force-projectile-contact-source-v1/handoff.json',
    }
    q=dict(source=True,native_qualified=False,installed=False,candidate=sha(J/'candidate.nes'),
           merged_parent=sha(P/'candidate.nes'),installed_parent='f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182',
           installed_playable=74,private_source_playable=75,
           source_checks={k:v for k,v in g.items()if k!='rows'},menu=c['menu'],
           scope='Actual linked Main and normal NMI in declared CPU/peripheral model; no native route/full1-1/audio/endurance qualification.',
           repair='Hogan own pre-step scroll publication; A/P preserved, one native ScrollHandler per Main. Rebuild actual C2 carrier and both cookie consumers after three genuine relocated operand bytes change.',
           native_negative=negative,
           pending=['Exact-hash Mesen route','Investigate possible45px lives-background displacement with delayed visible capture','Remaining five wrestlers, source music, endurance/advanced moves','All characters clear1-1 and use every powerup'],
           parent_handoffs={p:sha(R/p)for p in parents.values()},
           archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
           native_archive_sha256=sha(D/'native-incomplete.zip'),
           members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)})
    save(D/'handoff.json',q)
    (D/'README.md').write_text('''# Hogan current camera integration — source only

The current Contra Force cartridge and Hogan source component were freshly
linked together. The first merge is byte-exact to the two disjoint reviewed
changes from their shared parent. No wholesale historical source tree was copied.

The initial native attempt reached424Main/1252video frames before its90second
host limit, without completing the route. It exposed a stationary camera.
Hogan raw29 bypassed the shared13..27 scroll-position publisher. His own
resident now publishes the same pre-movement value while preserving A/P.
Native ScrollHandler still runs once per Main. Three C2 operand bytes moved;
the real carrier and both cookie consumers were rebuilt from final link output.

Actual code checks cover86identities/688Start-or-A cases. Only Hogan becomes
privately available. Real native parser167Main, route607Main,774normal NMIs,
60px jump, original punch and one native Goomba defeat reach world369/camera257.
These are CPU/peripheral-model checks, not a native emulator qualification.

The incomplete native images/observer are retained compactly. A possible45px
lives-background shift needs a later visible capture and PPU-state diagnostics.
The revised observer requires distinct displayed colours and delayed lives
capture. Another project currently occupies Mesen; its sessions are untouched.
Installed Downloads remains the74-character f476 cartridge.

This packet stores only the small source/recipe/test delta. Parent checkpoints
are pinned, not recursively copied. No ROM/object/debug/frame forest is archived.
''',encoding='utf-8')
    save(O/'freeze.json',dict(passed=True,native_qualified=False,checkpoint=str(D),handoff_sha256=sha(D/'handoff.json'),archive_bytes=q['archive_bytes'],members=len(files)))
    print((O/'freeze.json').read_text())


if __name__=='__main__':main()
