"""Freeze the exact private Benj source before native controller checks."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from finalize_ff_current_component_v3 import dependencies
import prepare_functional_roster_visuals58_v1 as B
O=R/'build/benj-menu-unlocked-1030-v3';J=O/'joint'
D=R/'docs/qa/checkpoints/2026-10-30/benj-current-menu-source'


def main():
    assert not D.exists() and not (O/'handoff.json').exists()
    parent=R/'build/coherent62-lives-fixes-v1/handoff.json'
    h=json.loads(B.read(parent));B.bound(h)
    controls=O/'menu-palette-controls.json';c=json.loads(B.read(controls));B.bound(c)
    assert c['passed'] and c['candidate']==B.sha(J/'candidate.nes')=='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6'
    own={p for p in J.rglob('*')if p.is_file()and p.suffix in ['.s','.inc','.cfg','.chr']}
    own|={J/n for n in ['native-pose-map.bin','toad-visible-pairs.bin','peach-visible-pairs.bin']}
    own|=set(dependencies(J/'main.dep'))|set(dependencies(J/'union.dep'))
    own|={Path(__file__),R/'tools/audit/prepare_benj_current_host_1030_v1.py',
          R/'tools/audit/prepare_benj_menu_unlocked_1030_v1.py',R/'tools/audit/benj_current_menu_controls_1030_v1.py'}
    own|={O/n for n in ['source-stage.json','menu-palette-controls.json','output-preflight.json','main-build.json','union-build.json','final-link.json']}
    own|={R/'build/benj-current-host-1030-v5'/n for n in ['source-stage.json','source.patch','main-build.json','union-build.json','chr-build.json','final-link.json']}
    own|={R/'build/benj-menu-unlocked-1030-v2/palette-consumer-negative.json'}
    forbidden={'.nes','.o','.dbg','.lbl','.map','.exe'}
    assert all(p.is_file() and p.resolve().is_relative_to(R) and p.suffix.lower()not in forbidden for p in own)
    D.mkdir(parents=True)
    archive=D/'source-only.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
        for p in sorted(own):z.write(p,p.relative_to(R).as_posix())
    assert archive.stat().st_size<5*1024*1024
    with zipfile.ZipFile(archive)as z:
        for p in own:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    bindings=dict(h['bindings'])
    bindings.update({str(p):B.sha(p)for p in own})
    bindings.update({str(p):B.sha(p)for p in [parent,J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',J/'main.o',J/'consumer-18.o',J/'benj-chr.o',archive]})
    d=dict(source=True,native=False,installed=False,status='FROZEN_PRIVATE_BENJ64_SOURCE_NATIVE_PENDING',
        candidate=c['candidate'],joint=str(J),parent=h['candidate'],enabled_if_qualified=64,
        CPU_checks=dict(menu_cycle=7,palette_packets=48,old_palette_pairs=240,controlled_Main_updates=160),
        archive_members=len(own),partial_contact_and_palette_behavior=True,
        limits=c['limits'],bindings=bindings)
    B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n')
    B.write(D/'handoff.json',B.read(O/'handoff.json'))
    B.write(D/'controls.json',B.read(controls))
    B.write(D/'README.md','Private Benj Toad/Peach candidate98048319, not installed. The actual current consumer-18 producer is recompiled; copying an older union-build recipe would omit the Fresh callback. The existing62 build is preserved. The new menu cycle is Mario, Luigi, Toad, Peach, Super Maaa, Kamikaze, Celeste. Actual source colors and native Mario movement plus the recovered Peach float vertical/ground/head-support producer are integrated. Native SMB enemy/platform contacts remain authoritative; special donor float contact consumers and fire/star/area palette progression are incomplete. The unjoined original cores remain in the prior frozenv5 source. Native checks and broader campaign coverage are still required.\n\nThe negative palette test caught the 6502 PHX/PHY macros replacing A before variant selection; the corrected source reloads the actual variant. Initial rebase attempts stopped on context, configuration or the old union tuple, and were not installed. The final source rebase preserves all earlier FF/S2 lives and Goku remap changes. No ROM, object, debug symbols or executable is included here.\n')
    manifest=dict(candidate=c['candidate'],handoff_sha256=B.sha(O/'handoff.json'),archive_sha256=B.sha(archive),
        archive_bytes=archive.stat().st_size,members={p.relative_to(R).as_posix():B.sha(p)for p in sorted(own)},native=False,installed=False)
    B.write(D/'manifest.json',json.dumps(manifest,indent=2)+'\n')
    files=[str(p.relative_to(R)).replace('\\','/')for p in sorted(D.iterdir())]
    files += [str(p.relative_to(R)).replace('\\','/')for p in own if p.parent==R/'tools/audit']
    B.write(D/'owned-files.txt','\n'.join(sorted(set(files+[(D/'owned-files.txt').relative_to(R).as_posix()])))+'\n')
    print(json.dumps(dict(candidate=c['candidate'],handoff=B.sha(O/'handoff.json'),bindings=len(bindings),archive_bytes=archive.stat().st_size,members=len(own))))


if __name__=='__main__':main()
