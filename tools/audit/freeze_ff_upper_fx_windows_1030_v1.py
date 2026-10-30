"""Freeze exact FF upper sprite-window source and hardware-consumer controls."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/ff-upper-fx-windows-1030-v1'
O=R/'build/ff-upper-fx-windows-qualified-1030-v1'
Q=R/'docs/qa/checkpoints/2026-10-30/ff-upper-spell-windows'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def compact(v):
    if isinstance(v,dict):return{k:compact(x)for k,x in v.items()if k not in['rows','bindings']}
    return v


def main():
    assert not O.exists()and not Q.exists()
    parents=[P/'source-closure.json',P/'upper-window-controls-v2.json',P/'upper-window-ISR-v2.json']
    negatives=[P/'upper-window-controls-negative-v1.json',P/'upper-window-ISR-negative-v1.json']
    files={Path(__file__)}
    for p in parents+negatives:
        h=json.loads(p.read_text());assert h['passed']==(p in parents),p
        for n,v in h['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,h['bindings']))
    tools=[R/'tools/audit'/n for n in['prepare_ff_upper_fx_windows_1030_v1.py',
        'ff_upper_fx_windows_controls_1030_v1.py','ff_upper_fx_windows_controls_1030_v2.py',
        'ff_upper_fx_windows_isr_1030_v1.py','ff_upper_fx_windows_isr_1030_v2.py']]+[Path(__file__)]
    local={p for p in P.rglob('*')if p.is_file()and'__pycache__'not in p.parts}
    files|=local|set(tools);O.mkdir();Q.mkdir(parents=True)
    controls=json.loads(parents[1].read_text())
    isr=json.loads(parents[2].read_text())
    checks=compact(controls['checks']);checks.update(compact(isr['checks']))
    proof=dict(passed=True,native=False,admitted=False,status='FROZEN_ACTUAL_FF_UPPER_SPELL_WINDOWS_CPU_PASS',
        candidate=str(P/'joint/candidate.nes'),candidate_sha256=sha(P/'joint/candidate.nes'),
        parent_sha256=sha(R/'build/ff-joint-native-flash-1030-v1/joint/candidate.nes'),
        RAM3_sha256=sha(P/'joint/ram3.bin'),cookie=list((P/'joint/ff-cookie.bin').read_bytes()),checks=checks,
        changes=['Existing FF spell hardware windows move from1/2/3 to5/6/7, with8x16 tile biases41/81/C1.',
            'Host decoder grows2B; original CORE/ART/CHR source data remain unchanged. Actual cache image/cookie/carrier updated together.',
            'Compiled native actor descriptors use only windows0..4; actual mouse renderer is disabled.',
            '90 whole DrawAll+normalNMI cases compare complete admitted spell source records and final OAM/CHR bytes, preserving actual mushroom/Goomba world patterns and windows1..4.',
            'All existing body/world palette/capacity/cold/Main/vector controls repeated, plus active upper-window lagNMI/IRQ cuts ending in actual normalNMI/OAM DMA.',
            'No new RAM/PRG/CHR allocation; all existing public entry PCs exact except the owned host-render end label +2.'],
        negative_explanations=['V1 graphics observer missed the optimized NativeGoombaRender OAM writer. V2 observes both actual entries with their shared returnPC/stack depth. Native Goomba visibility assertion and engine bytes unchanged.',
            'V1 active-interrupt stress exhausted real OAM allowance before window5. V2 uses three separate source Fire pages that fit and requires all5/6/7 actual publishers. The oversized negative remains preserved; no publisher/result injection.'],
        limits=['Private source-only successor; no native emulator, installed build, roster readiness,1-1 completion or earned-powerup claim.',
            'FX palette sharing/sword/optional ink, shared composition/audio/readiness and native gameplay remain unfinished.',
            'NormalNMI runs only after completed foreground OAM/palette publication; active-transaction cuts use genuine lagNMI/IRQ.',
            'Per-update source/graphics correctness does not establish60Hz performance.'],
        parents=[str(p)for p in parents],bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    hp=O/'handoff.json';hp.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    for p in parents+negatives+[P/'source-hooks.patch',hp]:(Q/p.name).write_bytes(p.read_bytes())
    archive=Q/'source-packet.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(local|set(tools)):
            if p.suffix.lower()=='.nes':continue
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        members=z.namelist()
        for n in members:assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
    receipt=dict(passed=True,native=False,installed=False,handoff_sha256=sha(hp),
        ROM_sha256=proof['candidate_sha256'],archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
        archive_members=len(members),all_archived_member_hashes_verified=True,original_ROMs_included=False,
        checks=checks,limits=proof['limits'])
    (Q/'checkpoint.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(handoff=str(hp),handoff_sha256=sha(hp),ROM=proof['candidate_sha256'],
        bindings=len(proof['bindings']),archive_bytes=receipt['archive_bytes'],archive_members=len(members))),flush=True)


if __name__=='__main__':main()
