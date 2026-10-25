"""Freeze the bounded source-only Parodius music proposal and exact receipts.

No game patch, mapper configuration, emulator, Git or Downloads write occurs.
The owned QA text is generated from the receipts to avoid stale numeric claims.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
DP = ARCHIVE / 'parodius-native-music-v1'
CURRENT = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
SOURCE = 'ef1dd05ad5b6095d1d8e9a9f81fcb549b5cf0248779d4e76eb7bd9b139de4c9a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, default=ROOT / 'build/smb-crossover-mmc5-expanded.nes')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.rom) == CURRENT
    a.output.mkdir(parents=True, exist_ok=False)
    refs = {
        'original_full': DP / 'full-v2/coverage.json',
        'pointer_closure': DP / 'pointer-closure-v1/coverage.json',
        'multiply': DP / 'multiply-v3/proof.json',
        'requests': DP / 'request-sites-v2/tables.json',
        'current_routes': DP / 'current50b5-routes-v1/proof.json',
        'layout': DP / 'layout-current50b5-v1/layout.json',
        'data_plan': DP / 'data-plan-current50b5-v3/proposal.json',
    }
    q = {name: json.loads(path.read_text()) for name, path in refs.items()}
    for name in ['original_full', 'pointer_closure', 'multiply', 'current_routes', 'layout', 'data_plan']:
        assert q[name]['passed']
    assert q['original_full']['source_sha256'] == SOURCE
    assert q['current_routes']['ROM_sha256'] == CURRENT
    assert q['layout']['ROM_sha256'] == CURRENT
    assert q['data_plan']['layout_ROM_sha256'] == CURRENT
    assert q['data_plan']['allocated_nothing'] and q['data_plan']['final_indirect_pointer_plus_Y_bound']
    assert q['multiply']['actual_source_calls'] == q['original_full']['original_calls'] == 396044
    assert q['multiply']['exact_ordered_APU_stores'] == q['original_full']['original_ordered_APU_stores'] == 1252908
    assert q['pointer_closure']['exact_reference_prefix_calls'] == 55201
    assert q['pointer_closure']['exact_reference_prefix_APU_stores'] == 200329
    assert not q['pointer_closure']['unknown_pointer_origins']
    assert q['current_routes']['identities'] == 37
    for name in ['probe', 'merge', 'multiply', 'requests', 'routes', 'layout', 'data_plan', 'pointer_closure', 'finalize']:
        path = ROOT / f'tools/audit/parodius_native_music_{name}.py'
        assert path.exists()
        dest = a.output / 'tools' / path.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(path, dest)

    # Source snapshots support the proposal and the routing result. They are
    # read-only bindings, not a complete canonical-build source archive.
    names = [
        'smb1base-mmc5-expanded.cfg', 'src/gradius_audio.s', 'src/expanded_audio.s',
        'src/mac_native_music.s', 'src/mike_native_music.s', 'src/guest_audio.s',
        'src/cv3_dmc_complete.s', 'src/remaining_audio.s', 'src/reset.s',
        'src/mmc5.s', 'src/x5_menu_ui.s', 'src/entrypoint.s',
        'tools/prepare_cv3_dmc_mirror.py', 'tools/reference/build_new_roster_audio.py',
        'reference/new-roster-audio/encoding-report.json',
    ]
    bindings = {}
    for name in names:
        source = ROOT / name
        dest = a.output / 'source-bindings' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        bindings[name] = sha(source)
    for suffix in ['.nes', '.dbg', '.lbl', '.map']:
        source = a.rom.with_suffix(suffix)
        if source.exists():
            dest = a.output / 'parent' / ('current50b5' + suffix)
            dest.parent.mkdir(exist_ok=True)
            shutil.copyfile(source, dest)

    reads = set().union(*(set(v['source_RAM_reads']) for v in q['original_full']['tracks'].values()))
    writes = set().union(*(set(v['source_RAM_writes']) for v in q['original_full']['tracks'].values()))
    assert not {x for x in reads | writes if not (0x100 <= x < 0x200 or 0x500 <= x < 0x600 or x in q['original_full']['ZP'])}
    loops = []
    for song, row in q['pointer_closure']['tracks'].items():
        with gzip.open(DP / 'pointer-closure-v1' / f'song-{int(song):02x}.jsonl.gz', 'rt') as stream:
            for line in stream:
                final = json.loads(line)
        repeat = row['exact_state_repeats'][0]
        source_lanes = final['state'][23:29]  # source500 has state index17
        loops.append(dict(request=int(song), first_equal_states=repeat,
                          source_0506_to_050B=source_lanes,
                          all_source_request_lanes_zero=not any(source_lanes)))
    routes = [(r['identity'], ', '.join(r['source_music'])) for r in q['current_routes']['rows']]
    (a.output / 'current-music-routes.tsv').write_text(
        'Identity\tActually executed music source\n' + '\n'.join('\t'.join(r) for r in routes) + '\n')
    source_rows = q['multiply']['rows']
    lines = [
        'PARODIUS ORIGINAL MUSIC: SOURCE/CPU PROPOSAL, 2026-10-25',
        '',
        'STATUS: OPEN. No game implementation is installed by this packet.',
        'No Mesen process was launched; no game src/config, Git or Downloads was changed.',
        'This packet preserves the earlier ready Mike music files and every TMNT/CV3 reservation.',
        f'Current routing/layout parent: {CURRENT}',
        f'Original Parodius Da! (Japan).nes: {SOURCE}',
        'Original local source: C:/NES/Parodius Da! (Japan).nes',
        'External packet: ' + str(a.output),
        '',
        '1. AUTHENTIC EXECUTABLE AND GOLDENS',
        'Original cartridge FE07/FE36/80A2 binds music play; FE16/C542 binds reset;',
        'FE20/C58D binds request. Banks12/13 are the original8000/A000 windows,',
        'with original14/15 fixed atC000/E000. Requests46,4A,...,9A are hexadecimal.',
        'All22 groups run18,000 play calls each, plus reset/request:396,044 source',
        'calls and1,252,908 ordered APU stores. The fresh goldens compare every call',
        'against the earlier independent probe: cycles, ordered stores and the full',
        'original CPU-RAM plus6000..7FFF hash, not only a selected state subset.',
        'The persistent source domain is45 andE0..EF plus500..5FF (273 bytes).',
        'Actual writes areE0..EA/EC..EE and500..5E9;45 is only read. Source8F is',
        'not a music-driver input: actual game request sites choose the hero music.',
        'Source stack use is balanced; minimum observed SP isF6 from entryFD.',
        '',
        'The v2 ROM_data_reads field tracked loads only. The plan explicitly adds',
        '272 bytes read by CMP tables:11,013 complete data bytes, plus3,233 source',
        'instruction bytes. All14,217 actually read original ROM bytes are accounted',
        'for;29 retained instruction operand bytes were skipped by the source CPU',
        'on untaken branches. Nothing is declared free merely because it is FF.',
        '',
        'The original v2 pointer log described the pointer before its Y index.',
        'A new source replay through every first exact-state repeat binds final',
        'pointer+Y targets:55,201 calls,200,329 ordered stores,43,740 accesses,',
        '442 pointer-origin pairs and zero unknown origins. Cycles, every ordered',
        'store,273-byte state and entire original-RAM hash match the full goldens.',
        'It reaches the same1,431 original instructions and11,013 complete data',
        'bytes. The full goldens remain unchanged; the correction is explicit.',
        '',
        '2. SOURCE REQUEST SELECTION AND LOOPS',
        'The real original E276 block loadsEADA[source8F] then callsFE20.',
        'Actual original basic-block execution proves Vic4E, Octopus52, TwinBee56,',
        'Pentarou5A. No song title is guessed from request order.',
        'Original E235..E259 was executed for144 seeded legal stage/hero/progress',
        'cases, plus the four direct hero cases. With source96=0A and source60<4,',
        'stages0..6 select the hero; stages7+ select7A. With source60>=4, source81',
        '(stage) selects E937[stage+1]:5E,62,66,6A,6E,72,76,7A,7A forstages0..8.',
        'These are original executable selector cases, not a complete original',
        'playthrough or a proven SMB area-role adaptation. Death/boss request',
        'call sites are retained, but their complete scene control flow is open.',
        '',
        'First identical persistent states, source play-step convention:',
        'Request | first state | repeated state | period | source request lanes',
    ]
    for row in loops:
        lo, hi, period = row['first_equal_states']
        status = 'all0506..050B zero' if row['all_source_request_lanes_zero'] else 'active'
        lines.append(f"{row['request']:02X} | {lo} | {hi} | {period} | {status}")
    lines += [
        'These are exact source-state recurrences. A zero source request lane does',
        'not prove real hardware DMC completion. No rendered-waveform claim is made.',
        '',
        '3. SOURCE-EQUIVALENT HOT PATH',
        'Original895C..8970 repeatedly adds050C,X for each duration. A private',
        '94-byte helper replaces that arithmetic, retaining the authentic final',
        'ADC carry/overflow and final DEC N/Z. All396,044 source calls,1,252,908',
        'ordered stores and273-byte source states match.262,144 direct cases',
        'cover256 multipliers x256 input counts x four independent incoming flag',
        'patterns20,22,61,E3. No tick, channel, sample or source APU store is cut.',
        'Helper code is temporarily at7000 with7100..7103 scratch in the private',
        'original-ROM CPU model. These are not allocated game addresses.',
        '',
        'Request | original peak | optimized peak | original mean | optimized mean',
    ]
    for row in source_rows:
        lines.append(f"{row['song']:02X} | {row['source_peak']} | {row['optimized_peak']} | {row['source_mean']:.3f} | {row['optimized_mean']:.3f}")
    lines += [
        'The13,194-cycle worst original request spike becomes6,196; the overall',
        'new maximum is9,929. Several other request peaks rise24..48cycles and',
        'some means rise about4cycles. This is source CPU work only: no mixer,',
        'real DMC DMA, IRQ/NMI, whole-game draw count or60Hz acceptance is proved.',
        'APU order/value/tick remain exact; intra-call store cycle positions change.',
        '',
        'Negative v2 is retained. It assumed incoming Z matched A; actual source',
        'group46 step2 reachesA=0,Z=0 and legally performs256 additions. The draft',
        'failed that real source call. V3 preserves incoming Z before comparing A.',
        'The v1 inner-loop helper also remains as earlier source-equivalent proof.',
        '',
        '4. CURRENT COMPILED ROUTING: ALL37 IDENTITIES',
        'Actual physical entrypoints in AudioUpdate were observed in1,036 cold',
        'contexts:37 identities xEasy/Hard numeric0/1 x7 area and7 event bits.',
        'Four updates/context give4,144 calls. The following is dispatch evidence,',
        'not a new authenticity/campaign qualification for every existing family.',
        'Identity | executed music source',
    ]
    lines += [f'{identity} | {source}' for identity, source in routes]
    lines += [
        'Chip/Dale, SMB3Mario/Luigi and all three Parodius alternates still execute',
        'Pit fallback. All four turtles execute Rygar fallback. The historical',
        'native TMNT candidate remains held for measured combat cadence regressions.',
        'ZeldaII Link still uses Zelda1 music; CV3 alternates still use CV1 music;',
        'Darkwing uses DuckTales and Roll shares Bass. CV3 DMC effects do not make',
        'its separately requested music a CV3 implementation.',
        'The new-roster encoder defaults only toKirby/Meta and its current report',
        'contains those two roles. Full_roster_music.inc has14 entries for those',
        'roles, not a working soundtrack for every added identity. That producer',
        'also excludes19,630 source DPCM stores from its tonal packed captures.',
        'Presence of an NSF, capture or playlist name is not actual dispatch proof.',
        '',
        '5. LEGITIMATE PRG/RAM PLAN; NO ALLOCATION APPLIED',
        'Current50b5 declared tails, preserving every old segment/prefix:',
        '  bank62:A300..BFFF,7,424 bytes for new code/adapter. Original code3,233B',
        '  plus the94-byte optimized arithmetic fits the raw budget; real assembly',
        '  with relocated branches, tables, writers and mixer remains required.',
        '  bank94:C300..DFFF,7,424 bytes; planned observed data6,690B,734B spare.',
        '  bank95:C400..DFFF,7,168 bytes; planned observed data5,435B,1,733B spare.',
        '  Existing bank95 A000-prefix would remain at its exact address while',
        '  its new tail receives a separate C400 linker-memory declaration.',
        'This includes the real contiguous474-byte8DA5 header table, not a forged',
        'virtual label. It also closes every observed affine base-to-final-target',
        'span and direct indexed table span, retaining11,286 unique data bytes.',
        'The per-bank copies contain12,125 bytes in total. A balanced2,000-order',
        'search retains useful spare space. This is byte-set feasibility, not a',
        'linked connected-pointer layout. Fixed locations for common absolute',
        'tables, all pointer rewrites and every actual request still need proof.',
        '',
        'No new global SRAM is proposed. Inactive XgLzHistory7400..7BFF is the',
        'candidate owner for source500..5FF and saved source zero-page state, as',
        'already done by mutually exclusive native Gradius/Mac/Mike. A character',
        'change must restart the compressed decoder. The14-byteDE..EB decoder',
        'slab is protected by current InitializeMemory. A later source-equivalent',
        'direct-field/ZP remap may avoid per-tick borrowing, but is not qualified',
        'here. Native foreground, life/area reset and IRQ ownership remain open.',
        '',
        'Keep VgAudioDispatch at its current C38 23-byte span. For character18,',
        'map a unified A62 selector. Parodius variants stay inA62; variant0 uses',
        'the established resident farcall tail to original GradiusA122. Other',
        'identities retain LmNativeMusicGate. Never map A away from a live A-window',
        'helper. All callers, flags, stack, SMC scratch and IRQ boundaries must',
        'be tested; no LOWCODE padding is requested or consumed.',
        '',
        '6. DPCM MIRROR: CONCRETE REMAINING RESOURCE CONSTRAINT',
        'Original sample bytesC040..C540 inclusive are1,281 bytes. The source',
        'starts are4012=1,10,15,20(decimal), lengths4013=36,20,20,4(decimal).',
        'All source rate/DAC/start/length combinations remain in the goldens.',
        'Real DMA continues after music returns, while gameplay changes C banks.',
        'A temporary C bank during the audio call cannot preserve these samples.',
        'The candidate design needs an E clone retaining all fixed code/vectors,',
        'with source samples atF140..F640 (4012 relocation deltaC4). Every source',
        'sample byte, rate, DAC initialization and status transition must survive.',
        '',
        'Reserved bank125 is not free: CV3 samples occupyF140..F580 andF5C0..F680,',
        'with its manager at physical1AF7 and copied resident helpers/vectors.',
        'Future TMNT cold code explicitly owns physical1700..1AF6. Overlaying',
        'Parodius samples would destroy live CV3 content. Current native Mac123,',
        'future TMNT63/124, shared125, resident126 and fixed127 remain reserved.',
        'There is no unreserved whole8KiB PRG bank in the current linker map.',
        '',
        'A reviewable coordinated path is to rehouse future TMNT B124 in bank99,',
        'which has a preserved138-byte menu-UI prefix and8,054-byte declared tail.',
        'Its leading connected TMNT streams must first be relocated into the',
        'deliberate TMNT A writer reserve, retaining every loop/pointer and linear',
        'continuation. Then124 could become the Parodius E mirror. This is only',
        'a proposal: no reservation was changed, no TMNT stream was moved, and',
        'the original all16-song192,016-call TMNT goldens must pass such a move.',
        'Root current TMNT A200/A300 arithmetic work must also be retained.',
        'Current CV3 uses BassDmcActive=3; historical TMNTv7 also used3. Both',
        'future native integrations need a coordinated owner namespace and real',
        'DMA completion, pause/silence/exit and another-owner-precedence tests.',
        '',
        '7. REMAINING IMPLEMENTATION / ACCEPTANCE',
        'Assemble actual code and connected data relocation; choose an explicit',
        'SMB area/event adaptation bound to real original requests; implement the',
        'persistent DMC mirror and shared ownership; compare every original call',
        'through the actual linked writers; prove all non-Parodius outer audio',
        'ABI/register/RAM/APU outcomes and both ordinary flag-off builds unchanged.',
        'Only then qualify actual native hardware/APU/DMA, interrupt bank/stack,',
        'OAM/CHR and pause/event transitions, followed by matched completed game',
        'updates AND draws in both modes. Original music rate/channels/stores must',
        'not be reduced to manufacture performance. Parodius music remains open.',
        '',
        'KEY RECEIPTS (SHA256)',
    ]
    lines += [f'{name}: {sha(path)}\n  {path}' for name, path in refs.items()]
    lines += [
        '',
        'Historical negative/raw artifacts are retained under multiply-v1/v2/v3,',
        'pilot-v1, full-v2-a/b, full-v2, pointer-closure-v1 and data-plan*.',
        'The broad parent source bindings are read-only evidence; this packet has',
        'no deployable game patch and does not reopen frozen Mike qualifications.',
    ]
    report = '\n'.join(lines) + '\n'
    report_path = ROOT / 'docs/qa/parodius-native-music-2026-10-25.txt'
    assert not report_path.exists(), 'Preserve any earlier report before publishing a revision.'
    report_path.write_text(report)
    (a.output / 'report.txt').write_text(report)
    receipt = dict(
        passed=True, source_CPU_proposal_only=True, game_implementation_installed=False,
        native_emulator_launched=False, production_game_writes=False,
        parent_ROM_sha256=CURRENT, original_ROM_sha256=SOURCE,
        golden_calls=396044, golden_ordered_APU_stores=1252908,
        pointer_closure_calls=55201, pointer_closure_APU_stores=200329,
        arithmetic_cases=262144, report_sha256=sha(report_path),
        proofs={name: dict(path=str(path), sha256=sha(path)) for name, path in refs.items()},
        source_bindings=bindings,
        tools={path.name: sha(path) for path in sorted((a.output / 'tools').glob('*.py'))},
        current_routes=routes, original_loops=loops,
        reserved_banks_untouched=[63, 123, 124, 125, 126, 127],
        open=['actual linked code/data relocation', 'source-bound SMB area/event mapping',
              'persistent DPCM mirror and coordinated owners', 'outer audio compatibility',
              'native hardware/IRQ/OAM/CHR/draw cadence'],
        limits='Source equivalence and resource feasibility are demonstrated. No game integration, real DMA, interrupt, native cadence or overall music-completion claim.')
    assert all(sha(ROOT / name) == value for name, value in bindings.items())
    assert sha(a.rom) == CURRENT
    (a.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: receipt[k] for k in ['passed', 'parent_ROM_sha256', 'report_sha256', 'golden_calls', 'pointer_closure_calls', 'open']}, indent=2))


if __name__ == '__main__':
    main()
