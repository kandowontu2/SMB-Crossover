"""Compact exact-source BT native boundaries/cold-loader milestone; no unlock."""
from pathlib import Path
import hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[2]
O=R/'docs/qa/checkpoints/2026-10-31/battletoads-native-boundaries-v1'
P=R/'build/battletoads-cold-acquire-v4';J=P/'joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();O.mkdir(parents=True)
    assert sha(J/'candidate.nes')=='95f141fafffc1d58170cd09369d4e1cbaeb837e7439742f215a11d3d0829611f'
    receipts=[P/n for n in['source-stage.json','boundary-controls.json','cold-controls.json','loader-controls.json','attack-controls.json','acquire-vectors-v3.json']]
    receipts += [R/'build/battletoads-current64-only-v1/transport-controls.json',R/'build/battletoads-bowser-router-review-v1/controls.json']
    for p in receipts:
        q=json.loads(p.read_text())
        if 'passed'in q:assert q['passed'],p
        for n,h in q['bindings'].items():assert sha(n)==h,(p,n)
    files=set(receipts)
    roots=[R/'build'/n for n in['battletoads-current64-host-v1','battletoads-current64-transport-v1','battletoads-current64-only-v1',
        'battletoads-native-adapter-v10','battletoads-cold-preview-v2','battletoads-cold-acquire-v4','battletoads-bowser-router-review-v1']]
    for root in roots:
        files.update(root.glob('*.json'));files.update(root.glob('*.txt'))
        j=root/'joint'
        if j.exists():
            for n in['entrypoint.s','union.s','union_imports.inc','union_main_imports.inc','private.cfg','src/new_roster_dispatch.s']:
                if(j/n).exists():files.add(j/n)
            for p in(j/'bt').glob('*'):
                if p.suffix in['.s','.inc','.chr']or p.name=='cookie.bin':files.add(p)
    for root in R.joinpath('build').glob('battletoads-*'):
        if root.name.startswith(('battletoads-native-adapter-v','battletoads-cold-')):
            files.update(root.glob('*negative*.json'))
            for name in['initial-link.json','boundary-controls.json','loader-controls.json','loader-controls-v2.json','acquire-vectors.json','acquire-vectors-v2.json']:
                p=root/name
                if p.exists():
                    try:q=json.loads(p.read_text())
                    except Exception:continue
                    if q.get('passed')is False or q.get('returncode',0)!=0:files.add(p)
    for pattern in['*battletoads*current64*.py','*battletoads*native_adapter*.py','*battletoads*native_adapter*.s',
        '*battletoads*cold*.py','*battletoads*cold*.s','*battletoads*native_attack*.py','battletoads_bowser_router_review_v1.py']:
        files.update(R.joinpath('tools/audit').glob(pattern))
    files.add(Path(__file__))
    files.add(R/'tools/audit/private_build_outputs_v1.py')
    grant=R/'build/battletoads-current64-host-v1/root-grant-and-partition.json'
    assert grant.exists();shutil.copyfile(grant,O/'root-grant-and-partition.json')
    manifest={p.relative_to(R).as_posix():sha(p)for p in sorted(files)}
    archive=O/'source-and-controls.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(manifest)
        for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    (O/'source-members.json').write_text(json.dumps(manifest,indent=2)+'\n')
    own=dict(canonical_sources_edited=[],installed_ROM_edited=False,native_emulator_launched=False,
        final_private_root=str(P),actual_owned_sources=[str(p.resolve())for p in sorted(J.joinpath('bt').glob('*.s'))]+[str((J/'entrypoint.s').resolve()),str((J/'private.cfg').resolve())],
        predecessor_modified_sources=['src/new_roster_dispatch.s: bounded raw33 Only classifier','union.s:144 genuine target expressions compressed to46groups, same public suffix'],
        archive_excludes=['Candidate NES files','Compiler objects/executables','Compiled cache/stream code images','Emulator images/video'],
        rebuild_dependency='Retained immutable current64/Benj source and prior BT original/source-loader checkpoints. All actual compiler/link recipes are archived and guard their new outputs; no binary overlay.',
        next_private_leaf='battletoads-menu-lease-v3 (not part of this qualified milestone; own menu lease/bit6 tests pending)')
    (O/'owned-files.json').write_text(json.dumps(own,indent=2)+'\n')
    text='''BT native-boundary/cold-loader source milestone, no playable admission

Exact private candidate95f141fa source-rebases the approved BT950B/CHR915..<927
on genuine current64 source98048319. Latest installed f56e55cd differs from9804
only in three Peach palette constants outside every owned BT range; those
constants must be genuinely composed in a later rollout. This is not installed.

Root grants: selected-only RAM3 family33,117source+64host bytes,16B BFE0cookie;
Quick partition93:DC0..<FA7,87:1020..<1100,72:1011..<1100. No newglobalRAM0/ZP,
no lease expansion, no header change. Loader487/487B; cold preview239/239B.
BtCheckADC0/BtLoadAE01 remain fixed. Retired/internal loader entries moved with
actual linked-object import closure; all consumers of owned source functions
are genuinely reassembled. Original core2864B is preserved through relocation.

Qualified actual source/CPU boundaries:2048 original health+96food pairs,
600 genuine integrator ticks,96 native-kernel all12pose pixel/role/mirror cases,
208 original B-edge/E2 native enemy/immunity/Bowser cases,512 cold body and256
menu palette pairs with no cache reads,12 real buffered8192B loader cases,
512 true destination/allflags quotient cases,4 palette->load->Ensure constructors,
warm/active earned health+clock preservation and898 actual NMI/IRQ seams.
Cookie invalid-first/code verified/published then sourceReady-last. Legal cold
copy vectors use lagNMI/IRQ; warm checks additionally cover normal/paused NMI.
Every NMI calls originalAudioUpdate once; all33SMC/livepage1/maps restore.

Current64 raw33 transport:46 real linked target groups including BmFresh/BmColors;
all144/fullflag target and raw owner controls,2204 vectors preserve foreign paths
(0..12CPU shared,0..4Only). Independent Bowser4aacf router review additionally
passes4736 old/new BT allflag rows,1024 cookie poison,18432 target cases and272
real vector cuts; explicit extraBT cost0..113CPU. That review excludes Bowser's
retained graphicsnegative. New Bowser source is separately owned/frozen.

Still pending: actual mixed raw33 ROM cold3/17/26 table integration, true Menu
Resolve/Start/Fresh/parser/Main cohort, P1/cache retirement and BT Selectbit5,
native firstlook/route. Own source moves/punch/HP/body are implemented, but the
recorded movement controls use explicit support and enemy fixtures. No natural
terrain/fullMain/readiness/native claim follows from these unit consumers.

Retained negatives include wrongsource adder semantics; deferred CHR assertion;
hidden native Yhigh; sourcepalette LDY flag; initialA72→A93 nearcall sizing;
1B loader overflow; ROM83 vsRAM03 acquire; reporter duplicateR1; stale warmread
baseline and NmiDisable-dependent replay cut. Passing corrected receipts are
named explicitly and never overwrite those original negatives.
'''
    (O/'README.txt').write_text(text,encoding='utf-8')
    q=dict(status='FROZEN_BT_SOURCE_NATIVE_BOUNDARIES_AND_COLD_LOADER_NO_UNLOCK',native=False,ready=False,
        candidate=sha(J/'candidate.nes'),source_archive_members=len(manifest),source_archive_bytes=archive.stat().st_size,
        exact_current64_ancestor='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6',
        latest_Peach_constants_not_yet_composed=True,owned_global_RAM0_bytes=0,
        bindings={str(p.resolve()):sha(p)for p in receipts+[Path(__file__),archive,O/'source-members.json',O/'owned-files.json',O/'README.txt',O/'root-grant-and-partition.json']})
    (O/'handoff.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(status=q['status'],handoff_sha256=sha(O/'handoff.json'),members=len(manifest),archive_bytes=archive.stat().st_size)))
if __name__=='__main__':main()
