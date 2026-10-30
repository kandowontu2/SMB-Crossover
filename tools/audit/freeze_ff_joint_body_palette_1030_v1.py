"""Freeze authenticated FF body/world palette source and actual queue controls."""
from pathlib import Path
import difflib,hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/ff-joint-body-palette-1030-v2'
OLD=R/'build/ff-joint-combat-hooks-1030-v5'
O=R/'build/ff-joint-body-palette-qualified-1030-v1'
Q=R/'docs/qa/checkpoints/2026-10-30/ff-body-world-palette'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()and not Q.exists()
    parents=[P/'source-closure.json',P/'body-palette-controls-v1.json']
    files={Path(__file__)}
    for p in parents:
        d=json.loads(p.read_text());assert d['passed'],p
        for n,v in d['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,d['bindings']))
    negative=R/'build/ff-joint-body-palette-1030-v1/source-negative.json'
    d=json.loads(negative.read_text());assert not d['passed']
    files.add(negative)
    tools=[R/f'tools/audit/prepare_ff_joint_body_palette_1030_v{i}.py'for i in[1,2]]
    tools +=[R/f'tools/reference/final_fantasy_host_palette_v{i}.s'for i in[1,2]]
    tools +=[R/'tools/audit/ff_joint_body_palette_controls_1030_v1.py',Path(__file__)]
    patch=[]
    for n in ['veneers.s','entrypoint.s','private.cfg','ff-palette.s']:
        before=(OLD/'joint'/n).read_text().splitlines(True)if(OLD/'joint'/n).exists()else[]
        after=(P/'joint'/n).read_text().splitlines(True)
        patch.extend(difflib.unified_diff(before,after,fromfile='parent/joint/'+n,tofile='candidate/joint/'+n))
    (P/'source-hooks.patch').write_text(''.join(patch),newline='\n')
    local={p for p in P.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
    files|=local|set(tools);O.mkdir();Q.mkdir(parents=True)
    source=json.loads(parents[0].read_text());checks=json.loads(parents[1].read_text())['checks']
    summary={k:{n:v for n,v in d.items()if n!='rows'}for k,d in checks.items()}
    proof=dict(passed=True,native=False,admitted=False,status='FROZEN_FF_BODY_WORLD_PALETTE_NATIVE_QUEUE_CPU_PASS',
        candidate=str(P/'joint/candidate.nes'),candidate_sha256=sha(P/'joint/candidate.nes'),
        parent_sha256=sha(OLD/'joint/candidate.nes'),RAM3_sha256=sha(P/'joint/ram3.bin'),
        checks=summary,own_A_bridge_bytes=source['own_A_bridge_bytes'],own_C_bridge_bytes=source['own_C_bridge_bytes'],
        actual_changes=['Service26 now queues genuine class body colors, native mushroom colors and native area palette3.',
            'Service29 caches phase changes and retries a full world/body refresh if the native queue was full.',
            'Service32 supplies the exact14B native area donor arithmetic used by the existing face/world helper.',
            'Class, powerup and star colors are read from authenticated source rows; cold selection never executes RAM3 or touches its ACK.',
            'All header,CHR,RAM3,cookie and existing public entry addresses remain exact. No new RAM or PRG lease.'],
        negative_explanation='Initial link attempted to import a private native donor symbol. The successor emits the exact original14B body in its own existing tail and verifies compiled equality. No shared code or lease was expanded.',
        limits=['Private source successor, not installed or native-emulator tested.',
            'This packet proves body/world colors only. FX/sword palette allocation, optional black ink and Bowser palette conflicts remain open.',
            'Full FF shared postBG ingress,audio,readiness,earned upgrades and1-1 completion remain open.',
            'Normal NMI consumers were tested after complete publication and on the cached no-write path; Main was observed owning the queue with NmiDisable set while appending.',
            'Source lineage is FF07cda with terrain/combat successors; shared composition must retain current a7cc Celeste/Kamikaze/Rogue changes.'],
        parents=[str(p)for p in parents],bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    hp=O/'handoff.json';hp.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    for p in parents+[P/'source-hooks.patch',hp]:(Q/p.name).write_bytes(p.read_bytes())
    (Q/'source-negative-v1.json').write_bytes(negative.read_bytes())
    archive=Q/'source-packet.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(local|set(tools)):
            if p.name=='candidate.nes':continue
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        members=z.namelist()
        for n in members:
            assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
    receipt=dict(passed=True,native=False,installed=False,handoff_sha256=sha(hp),
        ROM_sha256=proof['candidate_sha256'],archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        archive_members=len(members),all_archived_member_hashes_verified=True,original_ROMs_included=False,
        checks=summary,limits=proof['limits'])
    (Q/'checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(handoff=str(hp),handoff_sha256=sha(hp),ROM=proof['candidate_sha256'],
                        archive_bytes=receipt['archive_bytes'],archive_members=len(members))),flush=True)


if __name__=='__main__':main()
