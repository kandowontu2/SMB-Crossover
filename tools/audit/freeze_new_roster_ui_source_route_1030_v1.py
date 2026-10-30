"""Freeze the source-preserving UI optimization and rejected bypass evidence."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/new-roster-ui-source-route-1030-v5'
O=R/'build/new-roster-ui-source-route-qualified-1030-v1'
Q=R/'docs/qa/checkpoints/2026-10-30/new-roster-source-ui-fastpath'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists()and not Q.exists()
    parents=[P/'source-closure.json',P/'controls-v2.json']
    files={Path(__file__)}
    for p in parents:
        h=json.loads(p.read_text());assert h.get('passed',True)
        for n,v in h['bindings'].items():assert sha(n)==v,n
        files|={p}|set(map(Path,h['bindings']))
    negative=R/'build/new-roster-ui-fastpath-1030-v1/rejected-actual-FF-UI-negative.json'
    h=json.loads(negative.read_text());assert not h['passed']and h['reproduction_passed']
    for n,v in h['bindings'].items():assert sha(n)==v,n
    files.add(negative)
    flagnegative=R/'build/new-roster-ui-source-route-1030-v4/controls-negative-v1.json'
    h=json.loads(flagnegative.read_text());assert not h['passed']
    for n,v in h['bindings'].items():assert sha(n)==v,n
    files.add(flagnegative)
    compilernegative=R/'build/new-roster-ui-source-route-1030-v2/preparation-negative.json'
    files.add(compilernegative)
    tools=[R/'tools/audit'/n for n in['prepare_new_roster_ui_fastpath_1030_v1.py',
        'new_roster_ui_fastpath_negative_1030_v1.py',
        *[f'prepare_new_roster_ui_source_route_1030_v{i}.py'for i in[2,3,4,5]],
        'new_roster_ui_source_route_controls_1030_v1.py','new_roster_ui_source_route_controls_1030_v2.py']]+[Path(__file__)]
    local={p for p in P.iterdir()if p.is_file()};files|=local|set(tools)
    checks=json.loads(parents[1].read_text())['checks']
    summary={k:{n:v for n,v in h.items()if n!='rows'}for k,h in checks.items()}
    O.mkdir();Q.mkdir(parents=True)
    proof=dict(passed=True,native=False,admitted=False,status='FROZEN_SOURCE_PRESERVING_UI_CPU_PASS',
        candidate=str(P/'candidate.nes'),candidate_sha256=sha(P/'candidate.nes'),
        parent_sha256=sha(R/'build/current-character-composition-v2/joint/candidate.nes'),
        changes=['Newraw>=20 reaches the same genuine NrUi directly, skipping irrelevant Roll/Mac wrappers. Source UI, palette and ability services still execute.',
            'Existing X5OwnInventoryUi::HudRead becomes equivalent TXA/EOR17/BEQ/LDA/CLC/RTS. Every flag/return value is preserved, costing1extraCPU per use.',
            'Its existing15B region now contains a3B bridge;22B appended in already-owned X5_BOUNCE padding endsA79C,100B before fixed Dragon Power A800.',
            'No old public entry moves; original legacy SFC stub remains byte-exact. Header/CHR/other ROM/RAM allocations unchanged.'],
        checks=summary,measured_main_CPU_saved=297,
        negative_explanations=['The initial direct-native-inventory proposal saved more CPU but skipped actual FF palette queue/ack updates; explicitly rejected.',
            'A temporary compact HUD read returned wrong N/Z flags. Exact UI state/ordered-write assertions rejected it; TXA/EOR revision preserves all256flags.',
            'The first assembler probe assumed65C02 PLX byteFA; the source actually expands PLA/TAX. Prefix assertion caught this before candidate output.'],
        limits=['Private linked-CPU candidate, not native timing, installed update, readiness or1-1 completion.',
            'The297CPU reduction per tested Arthur/FF Main is a small change and does not resolve severe lag.',
            'Old-owner native HUD reads cost1extraCPU. All256raw selector UI fixtures and complete tested outputs remain exact.',
            'Shared current successor must compile the supplied source.patch and recheck its own exact hash.'],
        bindings={str(p.resolve()):sha(p)for p in sorted(files)})
    hp=O/'handoff.json';hp.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    archive=Q/'source-and-controls.zip'
    packed=local|set(tools)|{negative,flagnegative,compilernegative,hp}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7)as z:
        for p in sorted(packed):
            if p.suffix.lower()=='.nes':continue
            z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
        count=len(z.namelist())
    receipt=dict(passed=True,native=False,installed=False,ROM_sha256=proof['candidate_sha256'],
        handoff_sha256=sha(hp),checks=summary,limits=proof['limits'],
        archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,archive_members=count,
        all_member_hashes_verified=True,no_ROM_files=True)
    (Q/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',newline='\n')
    (Q/'source.patch').write_bytes((P/'source.patch').read_bytes())
    print(json.dumps(dict(handoff_sha256=sha(hp),ROM=proof['candidate_sha256'],bindings=len(files),members=count,archive_bytes=archive.stat().st_size)),flush=True)


if __name__=='__main__':main()
