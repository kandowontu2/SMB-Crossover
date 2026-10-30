"""Stage source-only frozen marker/proposal/model lineage; never Git stage."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
D=R/'docs/qa/checkpoints/2026-10-30/ff-source-epoch-preparation'

def main():
    assert not D.exists();D.mkdir(parents=True)
    packets={
        'build/ff-fx-world-marker-proposal-v2/handoff.json':'ea94867c9b3c808ea6124560be6330970dad9ac79d000d5b7f826856fffa83e3',
        'build/ff-fx-epoch-proposal-v1/proposal.json':'0dd2539798b60c67cd5ebceb22640d206a5f221abcea9a8077dde3de35cc672a',
        'build/ff-fx-epoch-model-qualified-v1/handoff.json':'5598592e11dc20cb0fcc9b349dc30b304d49cb507edade5842c78a1690d11e64',
    }
    files={Path(__file__)}
    for path,h in packets.items():
        p=R/path;assert B.sha(p)==h
        q=json.loads(p.read_text());files.add(p)
        for name,v in q['bindings'].items():assert B.sha(name)==v,name
    names=[
        'build/ff-fx-world-marker-proposal-v2/source-closure.json',
        'build/ff-fx-world-marker-proposal-v2/source.patch',
        'build/ff-fx-world-marker-proposal-v2/README.md',
        'build/ff-fx-world-marker-proposal-v2/marker-controls-v2.json',
        'build/ff-fx-world-marker-proposal-v2/main-and-isr-controls-v3.json',
        'build/ff-fx-world-marker-proposal-v2/main-and-isr-negative-v2.json',
        'build/ff-fx-world-marker-proposal-v1/main-and-isr-negative-v1.json',
        'build/ff-fx-world-marker-reference-v1/source-closure.json',
        'build/ff-fx-epoch-model-qualified-v1/README.md',
        'build/ff-fx-epoch-oracle-v3/controls.json',
        'build/ff-fx-epoch-oracle-v2/negative-controls.json',
        'build/ff-fx-epoch-oracle-v1/negative-controls.json',
        'build/ff-fx-epoch-alias-proposal-v1/proposal.json',
        'build/ff-fx-epoch-workers-sizing-v1/sizing.json',
        'build/ff-fx-epoch-workers-sizing-v2/sizing.json',
        'build/ff-fx-epoch-workers-sizing-v3/sizing.json',
        'build/ff-fx-epoch-workers-sizing-v3/workers.s',
        'build/ff-fx-epoch-workers-sizing-v3/rom.s',
        'docs/qa/checkpoints/2026-10-30/ff-source-epoch-reservations/receipt.json',
        'docs/qa/checkpoints/2026-10-30/ff-source-epoch-reservations/runtime-alias-reservation.json',
    ]
    tools=[
        'prepare_ff_fx_world_marker_v2.py','prepare_ff_fx_world_marker_reference_v1.py',
        'ff_fx_world_marker_controls_v3.py','ff_fx_world_marker_main_v3.py','freeze_ff_fx_world_marker_v1.py',
        'prepare_ff_fx_epoch_proposal_v1.py','ff_fx_epoch_oracle_v1.py','ff_fx_epoch_oracle_v2.py',
        'ff_fx_epoch_oracle_v3.py','ff_fx_epoch_alias_proposal_v1.py',
        'prepare_ff_fx_epoch_workers_sizing_v1.py','prepare_ff_fx_epoch_workers_sizing_v2.py',
        'prepare_ff_fx_epoch_workers_sizing_v3.py','freeze_ff_fx_epoch_model_v1.py',
        'prepare_ff_fx_epoch_cart_v1.py',
    ]
    names+=['tools/audit/'+name for name in tools]
    names+=['tools/reference/'+name for name in[
        'ff_fx_world_marker_v1.s','ff_fx_epoch_rom_proposal_v1.s','ff_fx_epoch_workers_proposal_v1.s']]
    files|={R/name for name in names}
    assert all(f.is_file()for f in files)
    assert all(f.suffix.lower()in['.py','.json','.md','.patch','.s','.inc','.txt']for f in files)
    archive=D/'source-evidence.zip'
    rows={str(f.relative_to(R)).replace('\\','/'):{'sha256':B.sha(f),'bytes':f.stat().st_size}for f in sorted(files)}
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in sorted(files):z.write(f,f.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(rows)
        for n,v in rows.items():assert hashlib.sha256(z.read(n)).hexdigest()==v['sha256']
    B.write(D/'README.md','''FF exact-color epoch source preparation checkpoint.

Frozen marker5c225bb9 tags complete native mixed-palette objects in ignored
OAM bit4. Its genuine source/Main/ISR controls preserve original execution
except metadata. It retains the source graphics-selector and observer failures.

The sizing proposal and read-only model are distinct from an implemented
scheduler.480 completed native DrawAll/NMI fixtures feed an independent model;
all admitted opaque source colors, body0, complete mixed groups and nativeP2/P3
are preserved. Oracle negatives remain, including invalid seeded rotation and
the mixed flower's actualP0 head. Later unlinked source uses98B ROM/480B RAM3
within granted104B/593B. Earlier C-bank and absolute-pointer design faults were
corrected before cartridge linking/execution and are documented separately.

Exact alias reuse is now approved in the linked reservation receipt, but these
frozen packets themselves neither install nor execute that scheduler. A later
private source-cartridge branch must source-rebuild cookie/carrier and qualify
actual OAM, heartbeat, fullqueue, lifecycle, fullMain/foreign/ISR/loader behavior.
No native campaign/readiness/cadence/admission/install claim is made here.

source-evidence.zip contains only readable source, receipts and retained
negatives. No ROM, CHR/image, object, debugger, or executable binary is included.
manifest.json binds every member and verifies exact current packet inputs.
Files were staged on disk only; Git index/commits were not touched.
''')
    B.save(D/'manifest.json',dict(passed=True,source_only=True,native=False,admitted=False,
        exact_frozen_packets=packets,archive_sha256=B.sha(archive),archive_bytes=archive.stat().st_size,
        member_count=len(rows),members=rows,archive_roundtrip_exact=True,
        forbidden_binary_members=0,no_Git_index_or_commit_action=True))
    print(json.dumps(dict(directory=str(D),members=len(rows),bytes=archive.stat().st_size,manifest_sha256=B.sha(D/'manifest.json'))),flush=True)

if __name__=='__main__':main()
