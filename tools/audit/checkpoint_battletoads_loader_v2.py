"""Compact immutable BT source/grant/loader checkpoint for root Git staging."""
from pathlib import Path
import hashlib,json,shutil,zipfile

R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-30/battletoads-source-core-loader-v2'
P=R/'build/battletoads-source-core-packet-v3'
L=R/'build/battletoads-current-host-v4'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not O.exists();O.mkdir(parents=True)
    original=json.loads((P/'handoff.json').read_text())
    for name,h in original['bindings'].items():assert sha(name)==h,name
    with zipfile.ZipFile(P/'source-and-controls.zip')as z:
        members=json.loads((P/'source-members.json').read_text())
        assert len(members)==456
        for n,h in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    for n in ['source-stage.json','loader-controls.json','loader-vectors-v2.json']:
        q=json.loads((L/n).read_text())
        if 'passed'in q:assert q['passed']
        for name,h in q['bindings'].items():assert sha(name)==h,name
    shutil.copyfile(P/'source-and-controls.zip',O/'original-core-source-and-controls.zip')
    shutil.copyfile(P/'handoff.json',O/'original-core-handoff.json')
    shutil.copyfile(L/'root-grant-and-partition.json',O/'root-grant-and-partition.json')
    files=set()
    for p in (L/'joint/bt').iterdir():
        if p.suffix in ['.s','.bin']:files.add(p)
    for p in L.iterdir():
        if p.suffix=='.json':files.add(p)
    files.add(L/'joint/private.cfg');files.add(Path(__file__))
    for pattern in ['prepare_battletoads_current_host_v*.py','battletoads_current_loader_*_v*.py']:
        files.update(R.joinpath('tools/audit').glob(pattern))
    files.update(R.glob('build/battletoads-current-host-v*/**/*negative*.json'))
    manifest={str(p.relative_to(R)).replace('\\','/'):sha(p)for p in sorted(files)}
    archive=O/'current-loader-source-and-controls.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,str(p.relative_to(R)).replace('\\','/'))
    with zipfile.ZipFile(archive)as z:
        for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    (O/'current-source-members.json').write_text(json.dumps(manifest,indent=2)+'\n')
    own=[str(p.resolve())for p in sorted(files)]
    owned=dict(canonical_sources_edited=[],private_root=str(L.resolve()),
        actual_mutated_source_files=[str(p.resolve())for p in sorted((L/'joint/bt').glob('*.s'))]+[str((L/'joint/private.cfg').resolve())],
        tools=[str(p.resolve())for p in sorted(files)if p.parent==R/'tools/audit'],
        evidence_files=own,source_only_archives_exclude=['Full candidate ROM','compiler object/executable','emulator media'],
        parent_dependency='Exact dfdb/fae1 source checkpoint is already separately frozen; immutable parent objects are linked read-only, not duplicated/overlaid',
        continuing_output='Use NEW derivative directory for any later host/menu/collision source change; keep this packet unchanged')
    (O/'owned-files.json').write_text(json.dumps(owned,indent=2)+'\n')
    notes='''Original Battletoads source + approved current-host cold loader

Original source packet0cce2968 is retained byte-for-byte (99bindings,
456source ZIPmembers). New exactdfdb leaf5ba13a49 source-links BT only in the
approved950B Quick partition andCHR915..<927. Existing62 code/readiness/menu,
all old global values, header, foreign RAM1/2/FF payloads and all other bytes
are exact. The genuine final127→125 mirror producer is retained.

BT loader477/487B, ROM36row/router209/224B; preview239B is still unimplemented.
12true cold buffered8192B copy/verify cases,9guard/error negatives,
1088fullflags/cookie pairs,148typedrow pairs and1380actualNMI/IRQ seams pass.
Real normal/lag/paused NMI calls originalAudioUpdate once and restores all33
SMC bytes, livepage1, A/C maps and borrowed pairs. SourceInit publication is
interrupted too. No cache fixture preload is used.

Retained private negatives: omitted inherited125mirror; Python helper path;
original BtLoad missing5FFFbusy guard (fixed in v4); vector reporter duplicate
kind field (product unchanged). None changes or damages the frozen parent.

This is a functional loader/core milestone, NOT a playable unlock. Source
terrain/hit callbacks, native HP/progression/realMain, ROM selected/lives art,
raw33 shared ingress, FmGroups20 and menu58/62 integration are still pending.
Root grants are recorded in root-grant-and-partition.json; no new global RAM
or wider ROM/CHR lease is taken. No emulator launched or download changed.
'''
    (O/'README.txt').write_text(notes,encoding='utf-8')
    q=dict(status='FROZEN_BT_ORIGINAL_SOURCE_PLUS_APPROVED_LOADER_NO_UNLOCK',source=True,native=False,
        original_handoff_sha256=sha(P/'handoff.json'),original_bindings=99,original_source_members=456,
        exact_current_parent='dfdb194ac73438ae8deb05b5fc93f241b1109d45a84b3ad333d0e632008d7fc7',
        candidate='5ba13a49d770b46d9dd878f16cb50d3d34c88c457c2b7582ed10c8239b186d4c',
        current_source_archive_members=len(manifest),cold_loader_cases=12,typed_row_pairs=148,actual_vector_cases=1380,
        no_native_or_shared_edit=True,bindings={str(p.resolve()):sha(p)for p in[
            Path(__file__),P/'handoff.json',L/'source-stage.json',L/'loader-controls.json',L/'loader-vectors-v2.json',
            O/'original-core-source-and-controls.zip',O/'original-core-handoff.json',archive,O/'current-source-members.json',
            O/'owned-files.json',O/'README.txt',O/'root-grant-and-partition.json']})
    (O/'checkpoint.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(status=q['status'],checkpoint_sha256=sha(O/'checkpoint.json'),
        current_source_members=len(manifest),current_archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
