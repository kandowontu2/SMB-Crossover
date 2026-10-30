"""Freeze real FF enemy initialization and natural Main weapon ingress."""
from pathlib import Path
import hashlib,json,zipfile

R=Path(__file__).resolve().parents[2]
P=R/'build/ff-joint-combat-hooks-1030-v5'
O=R/'build/ff-joint-combat-hooks-qualified-1030-v1'
Q=R/'docs/qa/checkpoints/2026-10-30/ff-combat-hooks'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()and not Q.exists()
    parents=[P/'source-closure.json',P/'combat-controls-v3.json']
    files={Path(__file__)}
    for p in parents:
        h=json.loads(p.read_text());assert h['passed'],p
        for n,v in h['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,h['bindings']))
    negatives=[R/'build/ff-joint-combat-hooks-1030-v1/source-negative.json',
       R/'build/ff-joint-combat-hooks-1030-v2/source-negative.json',
       R/'build/ff-joint-combat-hooks-1030-v3/combat-controls-negative-v1.json',
       R/'build/ff-joint-combat-hooks-1030-v4/source-negative.json',P/'combat-controls-negative-v2.json']
    for p in negatives:
        h=json.loads(p.read_text());assert not h['passed'],p
        # Negative receipts can bind the original script/ROM without declaring
        # their incomplete guard pipeline a successful source predecessor.
        for n,v in h.get('bindings',{}).items():assert sha(n)==v,n
        files.add(p);files|=set(map(Path,h.get('bindings',{})))
    tools=[R/f'tools/audit/prepare_ff_joint_combat_hooks_1030_v{i}.py'for i in range(1,6)]
    tools +=[R/f'tools/audit/ff_joint_combat_hooks_controls_1030_v{i}.py'for i in range(1,4)]
    tools +=[Path(__file__)]
    local={p for p in P.rglob('*')if p.is_file()and '__pycache__'not in p.parts}
    files|=local|set(tools);O.mkdir();Q.mkdir(parents=True)
    checks=json.loads((P/'combat-controls-v3.json').read_text())['checks']
    summary={k:{n:v for n,v in h.items()if n not in['rows','own']}for k,h in checks.items()}
    source=json.loads((P/'source-closure.json').read_text())
    proof=dict(passed=True,native=False,admitted=False,status='FROZEN_ACTUAL_FF_ENEMY_INIT_AND_MAIN_WEAPONS_CPU_PASS',
       candidate=str(P/'joint/candidate.nes'),candidate_sha256=sha(P/'joint/candidate.nes'),
       RAM3_sha256=source['RAM3_sha256'],cookie=source['cookie'],checks=summary,
       actual_changes=['Native CheckpointEnemyID still executes its original41B HP/flash/contact clears before authenticated FF slot reuse.',
        'Every reused slot clears its bit from FfHits and all three actual projectile hit dictionaries.',
        'Actual NrObjectWeaponTail service34 now reaches FwHostWeapons exactly once in Main; prior service4 alone was not reached.',
        'Source flash counters age once per accepted source weapon tick, with original pause/timer/death guards.'],
       negative_explanations=['Existing90B debris helper was full; renderer branch was withdrawn instead of expanding its lease.',
        'Source producer diff/symbol allowlists initially omitted owned moved combat labels and the intended veneer34 operands.',
        'Real full Main first exposed zero weapon callbacks; actual source veneer34 repairs it.',
        'The first multi-input flash assertion sampled before the whole Main; native enemy spawning legitimately clears counters before the later FF tick. Corrected passive checks bracket the actual flash age loop, preserving all48 exact-once assertions.'],
       limits=['Private source successor, not installed or native tested.',
        'FF flash renderer,shared postBG ingress,palette/audio and actual earned-powerup1-1 tests remain open.',
        'Native enemy constructor incurs174 extraCPU per initialization for foreign characters; not a hot per-frame path or60Hz claim.',
        'Source predecessor is frozen FF07cda+terrain2219, not a replacement for current18de/Arthur/Celeste source composition.'],
       parents=[str(p)for p in parents],bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    hp=O/'handoff.json';hp.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    for p in parents+[P/'source-hooks.patch',hp]:(Q/p.name).write_bytes(p.read_bytes())
    for i,p in enumerate(negatives,1):(Q/f'negative-{i}.json').write_bytes(p.read_bytes())
    archive=Q/'source-packet.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(local|set(tools)):
            if p.name=='candidate.nes':continue
            z.write(p,p.relative_to(R).as_posix())
    receipt=dict(passed=True,native=False,installed=False,handoff_sha256=sha(hp),
       ROM_sha256=proof['candidate_sha256'],archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
       archive_members=len(zipfile.ZipFile(archive).namelist()),original_ROMs_included=False,checks=summary,limits=proof['limits'])
    (Q/'checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(handoff=str(hp),handoff_sha256=sha(hp),ROM=proof['candidate_sha256'],
       RAM3=proof['RAM3_sha256'],cookie=proof['cookie'],archive_bytes=receipt['archive_bytes'])),flush=True)


if __name__=='__main__':main()
