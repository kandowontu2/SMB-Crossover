"""Keep the reviewed Roll fade adoption and its exact historical boundaries."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P = D / 'roll-fade-current9e0e-v1'
FINAL = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def append(path, note, prepend=False):
    old = path.read_bytes()
    nl = '\r\n' if b'\r\n' in old else '\n'
    extra = note.replace('\n', nl).encode('ascii')
    path.write_bytes(extra + old if prepend else old + extra)


def main():
    adopted = json.loads((P / 'adoption-v1/proof.json').read_text())
    assert adopted['adopted'] and adopted['ROM_sha256'] == FINAL
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == FINAL
    out = ROOT / 'docs/qa/checkpoints/2026-10-25/roll-fade-50b5'
    out.mkdir(parents=True, exist_ok=False)
    sources = {
        'adoption.json': 'adoption-v1/proof.json',
        'qualification.json': 'final-packet-v3/proof.json',
        'qualification-bindings.json': 'final-packet-v3/manifest.json',
        'pre-adoption-report.txt': 'final-packet-v3/final-roll-items-fade-current-2026-10-25.txt',
        'commands.txt': 'final-packet-v3/commands.txt',
        'source-build.json': 'proof.json',
        'implementation.patch': 'sourcepatch.patch',
        'parent-source-ledger.json': 'parent-source-ledger.json',
        'candidate-source-ledger.json': 'candidate-source-ledger.json',
        'ROOT-fade-CPU.json': 'root-fade-cpu-v1/proof.json',
        'ROOT-owner-CPU.json': 'root-owner-cpu-v1/proof.json',
        'ROOT-raw-RGB.json': 'root-calm-rgb-v1/proof.json',
        'parent-resources-CPU.json': 'cpu-parent-resource-v1/proof.json',
        'candidate-resources-CPU.json': 'cpu-candidate-resource-v1/proof.json',
        'native-preparation.json': 'native-preparation/preparation.json',
        'visual-review.json': 'visual-review-v1/proof.json',
    }
    # Read actual review filename rather than guessing another artifact.
    visual = list((P / 'visual-review-v1').glob('*.json'))
    assert len(visual) == 1
    sources['visual-review.json'] = visual[0].relative_to(P).as_posix()
    for role in ['baseline', 'candidate']:
        for mode in ['easy', 'hard']:
            name = role + '-' + mode
            sources['native-' + name + '.json'] = 'native-' + name + '-v1/proof.json'
    for name, path in sources.items():
        if name in ['ROOT-fade-CPU.json', 'ROOT-owner-CPU.json',
                    'parent-resources-CPU.json', 'candidate-resources-CPU.json']:
            obj = json.loads((P / path).read_text())
            checks = obj.pop('checks')
            obj['complete_raw_receipt'] = dict(path=str(P / path), sha256=sha(P / path),
                                               check_rows=len(checks), retained_external=True)
            (out / name).write_text(json.dumps(obj, indent=2)+'\n')
        else:
            shutil.copy2(P / path, out / name)
    for name in ['baseline-hard-calm-ages236-247.png', 'candidate-hard-calm-ages236-247.png',
                 'candidate-easy-calm-ages236-247.png']:
        shutil.copy2(P / 'root-calm-rgb-v1' / name, out / name)
    historical = D / 'final-roll-items-v1/fade-native-final-packet-v2/proof.json'
    shutil.copy2(historical, out / 'HISTORICAL-9bac-c32b-pool-and-calm.json')
    note = '''

2026-10-25 Roll pickup fade adopted on current Mike parent
Current MMC5:50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363.
Downloads/default/debug metadata match the fresh canonical ROOT build.
Only36 PRG bytes119 change versus9e0e:3-byte LDA->JSR and33-byte helper in
genuine FF tail. Three source files:roll.s,roll_render.s,new roll_drop_fade.s.
All72217 old scoped symbol addresses, RAM/CHR/art and other ROM bytes exact.
Roll now follows actual shared pickup fade admission: nonempty, age>=240
(or nonzero high age) and odd native FrameCounter is hidden. Native pickups
still update once, remain collectible and expire at their real420-update end.
Fresh current-parent181028 CPU cases, including ROOT independent164748 cases;
four native calm profiles: both candidate modes pass, both parent mechanics
pass while expected missing-fade negatives remain unchanged. ROOT independently
recomputed all48 captured PPU/RGB checks and viewed36 selected actual images.
Current four-profile totals5882 updates/7372wallframes,10 genuine births,
32 real defeats,6 natural expiries,4 pickups;5878NMI/IRQ,70536CHR,5773DMA checks.
No resource/RNG/drop-age/outcome injection; staged terrain and test arena are
explicit. Idle both modes each120 updates/120wallframes/120renders; mean extra
inclusive60 CPUcycles. Easy all+60, Hard range-60..180; no causal guess, universal
60Hz or campaign performance claim. Four empty source admissions cost+60.
Historical9bac/c32b full-pool/live-fire/fade coverage remains historical;
no current full-pool or original mobile executable fidelity claim is implied.
Checkpoint:docs/qa/checkpoints/2026-10-25/roll-fade-50b5.
Rollback:external roll-fade-current9e0e-v1/adoption-v1. Do not rerun
adopt_roll_drop_fade_once_v1.py. The agent's first offline reporter expected
every Hard inclusive delta+60; retained failure, corrected mean/range reporting,
and all raw native/CPU receipts remain unchanged.
CV3 remaining source SFX are rebasing privately onto50b5 before native tests.
Parodius native music/source-safe duration optimization and actual crowded-body
visibility remain active private tasks. Body record ordering has an offline
source-preserving lead, not an installed visibility fix. Current37 identities
and every-powerup verification remain the priority; new characters come later.
'''
    # Keep the original worker report byte-exact: its absolute path is bound
    # by the immutable qualification manifest. Publish adoption separately.
    report = ROOT / 'docs/qa/roll-drop-fade-adopted-2026-10-25.txt'
    report.write_text('Roll pickup fade adopted\n' + note, encoding='ascii')
    for name in ['docs/qa/CLAUDE-HANDOFF-2026-10-24.txt',
                 'docs/qa/current-work-pr-2026-10-24.md',
                 'docs/qa/ten-agent-work-2026-10-25.txt']:
        append(ROOT / name, note)
    tools = sorted((ROOT / 'tools/audit').glob('final_roll_items_fade_*'))
    tools += [ROOT / 'tools/audit' / n for n in ['adopt_roll_drop_fade_once_v1.py', 'checkpoint_roll_drop_fade_v1.py']]
    obj = dict(ROM_sha256=FINAL, goal_complete=False, files={p.name: sha(p) for p in out.iterdir() if p.is_file()},
               tools={str(p.relative_to(ROOT)): sha(p) for p in tools if p.is_file()},
               adopted_report_sha256=sha(report), external_archive=str(P),
               limitations=adopted['remaining'])
    (out / 'manifest.json').write_text(json.dumps(obj, indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(out), manifest_sha256=sha(out / 'manifest.json'))))


if __name__ == '__main__':
    main()
