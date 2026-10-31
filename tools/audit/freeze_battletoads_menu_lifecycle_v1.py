"""Freeze the exact BT menu/P1 retirement and real lifecycle source successor.

This packet is not a ready/menu-parser/Main or native gameplay qualification.
"""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from check_tmnt_render_oa import load, address, location

P = R / 'build/battletoads-menu-lease-v7'
J = P / 'joint'
O = R / 'docs/qa/checkpoints/2026-10-31/battletoads-menu-lifecycle-v1'
PREV = R / 'docs/qa/checkpoints/2026-10-31/battletoads-native-boundaries-v1'
EXPECTED = '358422853c2a7904d7282357cb055ac7d2dbb42b0e614d6576148a52c7712200'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, obj):
    p.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def verify(p):
    q = json.loads(p.read_text())
    if 'passed' in q:
        assert q['passed'], p
    for name, expected in q.get('bindings', {}).items():
        assert sha(name) == expected, (p, name)
    return q


def main():
    assert not O.exists(), O
    assert sha(J / 'candidate.nes') == EXPECTED
    assert sha(PREV / 'handoff.json') == '3f11383b80c0601c86b0de0b34d832f893704ad54c39543d395922e929c5d10e'
    receipts = [P / (n + '.json') for n in [
        'source-stage', 'menu-controls', 'protocol-controls', 'boundary-controls',
        'attack-controls', 'lifecycle-controls', 'lifecycle-vectors']]
    checked = {p.stem: verify(p) for p in receipts}
    verify(PREV / 'handoff.json')
    assert checked['menu-controls']['checks']['typed_Select']['pairs'] == 5120
    assert checked['menu-controls']['checks']['Start_masks']['actual_rows'] == 10240
    assert checked['protocol-controls']['checks']['real_vectors']['cases'] == 612
    assert checked['lifecycle-controls']['pairs'] == 512
    assert checked['lifecycle-vectors']['actual_vector_cases'] == 372
    assert checked['attack-controls']['pairs'] == 208
    O.mkdir(parents=True)
    b = load(J / 'candidate.nes')

    def symbol(name):
        s = b['syms'][name]
        result = dict(name=name, address=address(b, name))
        if 'seg' in s and 'ooffs' in b['segs'][s['seg']]:
            off = location(b, name)
            result.update(file_offset=off, physical_bank=(off - 16) // 8192,
                          raw_ROM_bank=((off - 16) // 8192) | 128)
        return result

    grant = json.loads((R / 'build/battletoads-current64-host-v1/root-grant-and-partition.json').read_text())
    grant.update(
        status='ROOT_GRANTED_PRIVATE_BT_MENU_LIFECYCLE_RETIRED_P1_SOURCE_SUCCESSOR',
        menu_lease=dict(address='Existing FmGroups $5FE8', bit5='BT Rash/Zitz only',
                        bit6='Temporary BT P1 lease only', bit7='Existing CF P1 lease',
                        low5='Existing WWF bits0..2 and CF bits3..4',
                        root_authority='Root approved temporary bit6 only inside existing <=400B FmCfRestoreP1 helper; preserve bit5/CF/WWF; retire before mask.',
                        actual_emitted_helper_bytes=393, approved_helper_limit=400,
                        physical_bank=29, start='B49B', fixed_following_boundary='BFB0',
                        FmToggle_bytes=278, FmStartFlags_bytes=28,
                        source_writer_reader_evidence='menu-controls.json::checks.source_consumers.references',
                        CF_toggle='ADD8/EORold/AND18/EORold preserves highE0 and low3; old ADC8/AND31 loss retained as negative.',
                        Start='Retire valid A7/family33 cache; restore GroundPaletteData+24 P1 if either marker; then retain Alts80/20/08 only slots31/9/26 and Groups20/18 only slots23/30.',
                        title='Existing full clear unchanged; unconditional tagged BtRetire also handles a stale cache after title already cleared its marker.',
                        temporary_world_limitation='Original BT secondary P1 is also used during selected play; native P1 actors may tint. No all-world palette or native claim.'),
        exact_private_candidate=EXPECTED,
        source_only=True, ready=False, native=False,
        latest_installed_f56_Peach_three_constants_not_composed=True,
        no_new_lease=True,
        new_common_or_global_RAM0_bytes=0)
    write(O / 'grant-and-partition.json', grant)

    rows = []
    names = ['BtMovement','BtGraphics','BtDraw','BtUnavailable','BtWeapons','BtInjury',
             'BtInjuryStatus','BtDeathStart','BtNativeDeath','BtUnavailable','BtNativeHead',
             'BtBody','BtNativeAdder','BtNativeBox','BtNativeSide','BtFresh','BtFullBox',
             'BtDraw','BtUnavailable','BtScene','BtUnavailable','BtUnavailable',
             'BtUnavailable','BtUnavailable','BtPickup','BtFullPower','BtColors',
             'BtUnavailable','BtHeadWithin','BtUnavailable','BtUnavailable',
             'BtUnavailable','BtUnavailable','BtUnavailable','BtWeapons','BtUnavailable']
    for i, name in enumerate(names):
        rows.append(dict(service=i, cache_entry=0xA000 + 3*i, target=symbol(name)))
    api = dict(
        candidate=EXPECTED, parent_current64='98048319d382e7a5c4e7186704b6e3b939eda4eec9bdd6e098c402cbd30799b6',
        source_parent_not_Bowser_joint=True,
        symbols=[symbol(n) for n in ['BtServiceVeneers','BtCacheServices','BtCheck','BtLoad',
                    'BtAcquire','BtRetire','BtColdPortrait','BtColdColors','BtFresh','BtScene',
                    'BtEnsure','FmCfRestoreP1','FmStartRetireFlags']],
        cache_rows=rows,
        exact_cache_cookie=dict(tag=167, family=33, version=1, source_state_bytes=117,
                                full_cookie=(J/'bt/cookie.bin').read_bytes().hex(),
                                invalid_first='BFE0=0 before copy',
                                code='8192 bytes copied and verified',
                                valid_last='full fingerprint published, then source BtHostReady last'),
        genuine_mixed_cold_row_proposal={
            '3':'Decline/no OAM, not a second portrait draw',
            '15':'Full valid BT cookie -> actual RAM3 row15/BtFresh; invalid -> genuine CmHostFresh only. Defer load/Ensure to legal forced-blank Colors26.',
            '17':'Always genuine ROM BtColdPortrait; no cache read or source initialization',
            '18':'Genuine FmQueueName ROM target; actual Rash/Zitz string funding still pending',
            '19':'Full valid BT cookie -> actual RAM3 row19/BtScene; invalid -> genuine JnResetDispatch only',
            '26':'Always ROM BtColdColors: queue original P0/P1 then BtAcquire; loader rejects hover/active/unqualified phase, copies/Ensure only under its real forced-blank guards',
            '30':'Decline custom BT status name; retain native text without claiming custom label',
            '32':'Genuine HuNativeWorldPalette ROM target'},
        loaded_lifecycle=dict(
            Fresh='Native CmHostFresh once; preserve its actual returned AXYP/SP and ordered native writes; original source constructor/health47/frame0 and ReadyLast.',
            Scene='Native JnResetDispatch once; preserve its actual returned AXYP/SP and native writes; reset current player motion/animation and pending old E2, retain health and foreground clock.'),
        caller_ABI=dict(
            outer='Actual linked FarCallCommon contract: returned NZ reflects returned A; intentional carry documented per callback. No arbitrary incoming NZ preservation claim.',
            internal_dead_A='Only three cold internal targets omit SafecallA write: native kernel/area backdrop/Acquire overwrite or do not consume incoming A. Outer caller A/P/X/Y saved; 3072 actual caller cases bound.',
            cold_portrait='8 genuine native OAM parts; source24x33 envelope, physical915, actual native X+8/Y+20/high1; no RAM3 read/init. Caller R0/1/3..7 scratch, C map restored.',
            colors='Original two source roles; no universal shortcut; native backdrop callback; incoming outer AXYP preserved; sets bit40 only when queue accepted.',
            NMI='No BT NMI clock. One original source foreground-end clock only. All33SMC/livepage1/rawmaps/R0/1/R6/7 restored across actual legal interrupts.'),
        shared_composition_pending=[
            'Do not replace frozen Bowser B020/BwBtResolve bytes blindly; integrate genuine source imports and regenerate fingerprint/carrier.',
            'Sibling owns actual mixed27/33 resolver. New BtFresh/BtScene and invalid fallbacks above are not yet in its frozen candidate.',
            'Ready raw33 must take native-other preview branch, not raw>=28 DK/Arthur-only shortcut.',
            'Current names are generic BATTLETOADS placeholder and BT remains pending. No ready flag was changed here.',
            'BwStartFlags remains consumed in sibling frozen Bowser candidate. Only after composing new FmStartFlags source and proving no consumers may its old bytes be reclaimed.',
            'Retain exact installed f56 three Peach palette constants when composing.',
            'Actual ready menu/Start/full native parser/Main, body/collision and native firstlook still required.'])
    write(O / 'row-and-cold-API.json', api)

    build_receipts = sorted(P.glob('*-build.json')) + [P/'initial-link.json',P/'final-link.json']
    commands = []
    inputs = {}
    for p in build_receipts:
        q = json.loads(p.read_text())
        assert q['returncode'] == 0, p
        assert q['validated_outputs']['outputs_validated_before_execution'], p
        commands.append(dict(receipt=str(p.relative_to(R)), sha256=sha(p),
                             command=q['command'], output_validation=q['validated_outputs']))
        for arg in q['command']:
            v = Path(arg)
            if v.is_file() and v.suffix in ['.s','.inc','.cfg','.o']:
                inputs[str(v.resolve())] = sha(v)
    write(O/'actual-build-inventory.json', dict(
        commands=commands, exact_actual_inputs=inputs,
        own_recompiled_objects=['bt-main.o','bt/api.o','bt/core.o','bt/art.o','bt/loader.o',
                                'bt/router.o','bt/preview.o','bt/stream.o'],
        inherited_genuine_union='battletoads-current64-transport-v1/joint/bt-union.o; actual144 linked target expressions include BmFresh/BmColors',
        no_binary_overlay=True,
        rebuild='Commands are exact original recipes, not safe output destinations for reuse. New successor must rewrite ALL outputs and actual MEMORY file= side outputs and validate before every invocation. Inherited current64 objects/source are dependencies, not newly owned files.'))

    own = dict(
        private_root=str(P), canonical_sources_edited=[], installed_ROM_edited=False,
        native_emulator_launched=False, Git_index_or_commit_changed=False,
        changed_producers=[str(J/'src/full_roster_menu.s'),str(J/'src/cf_menu_body.inc'),
                           str(J/'bt/api.s'),str(J/'bt/preview.s')],
        own_source_inventory=[str(p) for p in sorted((J/'bt').iterdir())
                              if p.suffix in ['.s','.inc','.chr'] or p.name=='cookie.bin'],
        preserved_public_boundaries=['FmToggle278B','FmStartFlags28B','FmCfRestoreP1 entry',
                                     'BFB0 following reset','BtServiceVeneers','BtCheck','BtLoad',
                                     'all current64 readiness/art and nonowned bytes'],
        source_parent='95f141fa frozen native-boundaries milestone',
        archive_excludes=['NES','EXE','object files','compiled cache/carrier images','emulator output'],
        no_native_or_full_Main_claim=True)
    write(O/'owned-files.json',own)

    readme = '''Private BT menu-retirement and real Fresh/Scene source successor

Exact candidate35842285 is built on genuine current64/98048319 through frozen
95f141fa. Installed f56e55cd has three separate Peach palette constants; those
must be preserved during shared composition. This packet changes no readiness,
header, old64 artwork or nonowned bytes and is not installed/native-qualified.

Root granted bit5 as BT variant and bit6 only as temporary P1 lease. Existing
CFbit7/CFbits3..4/WWFlow3 survive toggles. Exact393/400B menu helper retires the
tagged BT cache and native GroundPaletteData P1 before Start masks can discard
either marker. Start retains only the selected family bits. FmToggle278B and
FmStartFlags28B remain fixed. No new ROM/RAM/ZP/header grant is used.

Source-owned Fresh15 and Scene19 call genuine native callbacks once and retain
their actual results. Fresh initializes real original health and foreground
clock; Scene preserves those while clearing motion and the old punch event.
Retained v6 negative shows the pending E2 leak at an area transition before fix.

Exact controls: all83 current profiles/664 real Start+A boundaries;5120 Select;
10240 Start;3072 internal dead-A/actual outer caller pairs;512 lifecycle pairs;
612 menu and372 lifecycle true-vector cuts;2048 original health+96food pairs;
600 integrator ticks;96 source/native-kernel pose pixels;208 true B/E2 enemy
consumers. All applicable AXYP/SP,33SMC,livepage1,maps and ordered native writes
are checked. Source clock is once per foreground tick, not NMI; native audio
still runs once per real NMI. Stale FF/Arthur AudioOwner/pending SFX are covered.

These are source boundaries, not a full gameplay claim. Shared mixed27/33 ROM
cold targets and the raw33 preview seam must be genuinely composed next, followed
by actual menu/Start/parser/Main and a bounded native firstlook. No manually
seeded cache result qualifies a ready roster gate. See row-and-cold-API.json.
Original BT P1 secondary colors may tint native P1 actors while BT is selected;
retirement restores native foreign palette. Extended combos/grabs/depth/water
specials/source music/custom HUD and vine moves remain outside this basic core.

Source archive includes exact own changed producers, commands, controls and
retained failed ancestors. Rebuilding also needs frozen current64 and the bound
95f source milestone. Its own source-and-controls.zip is included as a verified
predecessor. No ROM/object/executable/capture payloads are archived.
'''
    (O/'README.txt').write_text(readme,encoding='utf-8')
    files = set(receipts + build_receipts)
    files.update([J/'entrypoint.s',J/'private.cfg',J/'main.dep',
                  J/'src/full_roster_menu.s',J/'src/cf_menu_body.inc'])
    files.update(p for p in (J/'bt').iterdir()
                 if p.suffix in ['.s','.inc','.chr'] or p.name=='cookie.bin')
    for v in range(1,8):
        root=R/f'build/battletoads-menu-lease-v{v}'
        files.update(root.glob('*.json'))
    for pattern in ['prepare_battletoads_menu_lease_v*.py','battletoads_menu_*controls_v*.py',
                    'battletoads_lifecycle*.py']:
        files.update((R/'tools/audit').glob(pattern))
    files.add(Path(__file__))
    files.add(R/'tools/audit/private_build_outputs_v1.py')
    files.update(p for p in PREV.iterdir() if p.is_file())
    files.update(p for p in O.iterdir() if p.is_file())
    assert all(p.exists() for p in files)
    assert all(p.suffix.lower() not in ['.nes','.o','.exe','.png','.mp4'] for p in files)
    manifest={p.relative_to(R).as_posix():sha(p) for p in sorted(files)}
    archive=O/'source-and-controls.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(manifest)
        for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    write(O/'source-members.json',manifest)
    bindings=set(receipts+[Path(__file__),archive,O/'source-members.json',
        O/'grant-and-partition.json',O/'row-and-cold-API.json',O/'owned-files.json',
        O/'actual-build-inventory.json',O/'README.txt',PREV/'handoff.json',
        J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl'])
    bindings.update(p for p in files if p.suffix != '.zip')
    q=dict(status='FROZEN_BT_MENU_RETIREMENT_LIFECYCLE_SOURCE_NO_UNLOCK',
           candidate=EXPECTED,native=False,ready=False,
           source_archive_members=len(manifest),source_archive_bytes=archive.stat().st_size,
           source_archive_sha256=sha(archive),
           previous64ready_preserved=True,all83profiles_preserved=True,
           helper_bytes=393,helper_approved_limit=400,
           actual_vector_cases=984,new_global_RAM0_bytes=0,
           latest_f56_Peach_three_constants_not_composed=True,
           pending='Actual shared mixed-cold resolver/ready menu/parser/Main/native firstlook',
           bindings={str(p.resolve()):sha(p) for p in sorted(bindings)})
    write(O/'handoff.json',q)
    verify(O/'handoff.json')
    print(json.dumps(dict(status=q['status'],handoff_sha256=sha(O/'handoff.json'),
                          members=len(manifest),bindings=len(q['bindings']),
                          archive_bytes=archive.stat().st_size)))


if __name__ == '__main__':
    main()
