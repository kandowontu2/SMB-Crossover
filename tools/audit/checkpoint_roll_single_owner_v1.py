"""Archive small reviewed receipts; large lossless Roll evidence stays external."""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/final-roll-items-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=ROOT/'docs/qa/checkpoints/2026-10-25/roll-owner-9bac';assert not out.exists();out.mkdir(parents=True)
    refs={
        'adoption.json':'adoption-single-owner-v1/proof.json',
        'native-packet.json':'native-packet-single-owner4c70-v1/proof.json',
        'agent-native.json':'aggregate-single-owner4c70-v1/proof.json',
        'root-native-reaggregation.json':'root-aggregate-v1/proof.json',
        'root-owner-cpu.json':'root-single-owner-cpu-v1/proof.json',
        'root-resource-cpu.json':'root-resource-cpu-v1/proof.json',
        'implementation.patch':'drop-single-owner-private4c70-v1/sourcepatch.patch',
        'first-wrong-native-write.json':'drop-owner-hard-v2/drop-owner-proof.json',
        'source-build.json':'drop-single-owner-private4c70-v1/proof.json',
        'visual-review.json':'visual-review-single-owner4c70-v1/proof.json',
        'visual-owner-label-correction.json':'visual-review-single-owner4c70-v1/shared-owner-label-correction.json',
        'report-binding.json':'owner-final-report-v2/proof.json',
    }
    for name,source in refs.items():shutil.copy2(D/source,out/name)
    tools=sorted((ROOT/'tools/audit').glob('final_roll_items*'))
    tools += [ROOT/'tools/audit/adopt_roll_single_owner_once_v1.py',Path(__file__)]
    manifest=dict(ROM_sha256=json.loads((out/'adoption.json').read_text())['ROM_sha256'],goal_complete=False,
                  external_archive=str(D),files={n:sha(out/n)for n in refs},tools={str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in tools},
                  source_sha256=sha(ROOT/'src/roll_weapons.s'),report_sha256=sha(ROOT/'docs/qa/final-roll-items-2026-10-25.txt'),
                  limits='Single drop owner accepted; missing late-life fade remains open. Two staged native item modes, not an all37 current native campaign or source-perfect mobile gameplay claim. Raw captures remain external, including failed fixtures and documented Hard419/420 label limitation.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    note='''

2026-10-25 Roll drop owner accepted
Current MMC5 is9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c.
ROOT canonical compile and Downloads/default bytes agree. Only18 redundant local
drop-update bytes inbank119 changed from4c70; shared object dispatcher owns the
single update. Both native modes72steps/624defeats/139natural drops pass;
ROOT independently reran412owner+8140resource CPU cases and reaggregated all427
raw event captures. Checkpoint:docs/qa/checkpoints/2026-10-25/roll-owner-9bac.
Missing Roll fade remains open. Existing full-roster1-1 run is8ff-only:37/38
profiles passed across36identities; BassHard controller contact failure retained
and retry running. SMB3 P-bar transient font withdrawal is independently found,
private fix under CPU/native qualification; no current P-bar fix claim yet.
No new characters/menu row. Continue existing37 identities and every powerup.
'''
    for name in ['docs/qa/CLAUDE-HANDOFF-2026-10-24.txt','docs/qa/current-work-pr-2026-10-24.md','docs/qa/ten-agent-work-2026-10-25.txt']:
        p=ROOT/name;old=p.read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n';p.write_bytes(old+note.replace('\n',nl.decode()).encode())
    print(json.dumps(dict(checkpoint=str(out),manifest_sha256=sha(out/'manifest.json'),files=len(refs))))


if __name__=='__main__':main()
