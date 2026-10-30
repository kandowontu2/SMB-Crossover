"""Freeze actual FF native flash and unchanged native DrawAll contracts."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/ff-joint-native-flash-1030-v1'
O=R/'build/ff-joint-native-flash-qualified-1030-v1'
Q=R/'docs/qa/checkpoints/2026-10-30/ff-native-enemy-flash'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()and not Q.exists()
    parents=[P/'source-closure.json',P/'native-flash-controls-v3.json']
    files={Path(__file__)}
    for p in parents:
        h=json.loads(p.read_text());assert h['passed'],p
        for n,v in h['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,h['bindings']))
    negatives=[P/f'native-flash-controls-negative-v{i}.json'for i in[1,2]]
    for p in negatives:
        h=json.loads(p.read_text());assert not h['passed']
        for n,v in h['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,h['bindings']))
    diagnostic=P/'drawall-native-C-contract-diagnostic.json'
    assert json.loads(diagnostic.read_text())['passed'];files.add(diagnostic)
    tools=[R/'tools/audit/prepare_ff_joint_native_flash_1030_v1.py',
           R/'tools/reference/final_fantasy_host_palette_v3.s',Path(__file__)]
    tools +=[R/f'tools/audit/ff_joint_native_flash_controls_1030_v{i}.py'for i in[1,2,3]]
    local={p for p in P.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
    files|=local|set(tools);O.mkdir();Q.mkdir(parents=True)
    checks=json.loads(parents[1].read_text())['checks']
    summary={k:{n:v for n,v in h.items()if n!='rows'}for k,h in checks.items()}
    proof=dict(passed=True,native=False,admitted=False,status='FROZEN_ACTUAL_FF_NATIVE_ENEMY_FLASH_CPU_PASS',
        candidate=str(P/'joint/candidate.nes'),candidate_sha256=sha(P/'joint/candidate.nes'),
        parent_sha256=sha(R/'build/ff-joint-body-palette-1030-v2/joint/candidate.nes'),
        RAM3_sha256=sha(P/'joint/ram3.bin'),checks=summary,
        actual_changes=['FF NPCs now use the genuine native flash calculation, including validated Bowser primary/rear ownership.',
            'Native SamusFreezeDrawAll relocates into the last59B of the existing owned202B A62 alignment. Genuine draw/freeze order and returned registers/flags/C publications remain identical.',
            'The freed native11B contains a7B FF-owner probe plus4B padding. All prior native public entries remain exact.',
            'Cold palette mode0/1 uses ASL/BEQ for mode0/2, saving3B with all previous queue/phase/cold/NMI/Main/ISR controls repeated.',
            'Header,CHR,RAM3,cookie and all unlisted ROM bytes remain exact; no new RAM or ROM lease.'],
        negative_explanations=['The first CPU assertion expected7extraCPU for every foreign actor; genuine Link already branches straight to native flash before the new probe and remains0extraCPU. All actor state/output equality assertions were retained.',
            'The second harness incorrectly required DrawAll to leave C unchanged. Original DrawAll genuinely publishes the graphics C bank; the successor compares actual old/new publications, ordered writes, full live page1 and exact returned registers instead. Baseline diagnostic retained.'],
        limits=['Private source successor; no native emulator,menu admission,installed build or full1-1 completion claim.',
            'An extra145CPU per complete DrawAll and0..7CPU per NPC are measured; no performance improvement or60Hz claim.',
            'FF FX palette allocation/optional ink,actual sharedpostBG/audio/readiness/earned upgrades remain open.',
            'Source lineage remains private FF07cda with terrain/combat/palette successors; shared composition must retain installeda7cc Celeste/Kamikaze/Rogue changes.'],
        parents=[str(p)for p in parents],bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    hp=O/'handoff.json';hp.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    for p in parents+[P/'source-hooks.patch',diagnostic,hp]+negatives:(Q/p.name).write_bytes(p.read_bytes())
    archive=Q/'source-packet.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(local|set(tools)):
            if p.name=='candidate.nes':continue
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        members=z.namelist()
        for n in members:assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
    receipt=dict(passed=True,native=False,installed=False,handoff_sha256=sha(hp),
        ROM_sha256=proof['candidate_sha256'],archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        archive_members=len(members),all_archived_member_hashes_verified=True,original_ROMs_included=False,
        checks=summary,limits=proof['limits'])
    (Q/'checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(handoff=str(hp),handoff_sha256=sha(hp),ROM=proof['candidate_sha256'],
        archive_bytes=receipt['archive_bytes'],archive_members=len(members))),flush=True)


if __name__=='__main__':main()
