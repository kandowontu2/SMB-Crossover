"""Read-only current-ROM identity census and conservative Excitebike proposals.

No bytes are allocated or patched. Unknown publisher domains stay unresolved.
"""
from pathlib import Path
import hashlib, json, sys
R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools'), str(R / 'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
import check_hogan_current_bounded_v1 as M
O = R / 'build/excitebike-pose-1101-v3'


def main():
    rom = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    baseline = R / 'build/metal-storm-idle-shots-1101-v41/candidate.nes'
    b = scoped_load(baseline)
    raw = rom.read_bytes()
    assert raw == b['raw'], 'Nightly changed; select its matching current symbol bundle'
    counts = [7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
    seed = M.fresh(b)
    rows = []
    menu_pages = set()
    for slot, count in enumerate(counts):
        m = M.fork(seed)
        M.put(m, CrossoverMenuIndex=slot)
        M.invoke(m, 'MenuResolveCharacter')
        M.invoke(m, 'QueueSelection')
        for variant in range(count):
            if variant:
                M.put(m, VRAM_Buffer1_Offset=0, CrossoverMenuButtons=0,
                      SavedJoypad1Bits=32, SavedJoypad2Bits=0)
                M.invoke(m, 'CrossoverMenuInput')
            M.invoke(m, 'X5PublishChr')
            menu_pages.update(m.chr_latches)
            assert not set(range(728,740)) & set(m.chr_latches), (slot, variant, m.chr_latches)
            rows.append(dict(slot=slot, variant=variant, raw=M.get(m, 'SelectedCharacter'),
                             alts=M.get(m, 'FmAlts'), published_pages=list(m.chr_latches)))
    assert len(rows) == 90
    assert not {37, 38} & {r['raw'] for r in rows}
    # Source-declared padding ends at common records offset1108. Root's
    # Shinobi resident allocation is0800..0e00; do not count that interval.
    prg_offset = 16 + 65 * 8192 + 0xe00
    pad = raw[prg_offset:16 + 65 * 8192 + 0x1108]
    assert pad == bytes([255]) * 776
    source = (R / 'src/protoman.s').read_text()
    assert '.res $1108-(*-ProtoArtBegin), $ff' in source
    common = R / 'chr/characters/protoman-common-records.bin'
    if common.exists():
        data = common.read_bytes()
        assert raw[16 + 65 * 8192 + 0x1108:16 + 65 * 8192 + 0x1108 + len(data)] == data
    at = location(b, 'SunnyChrLow')
    sunny = sorted(set(v + 512 for v in raw[at:at + 35]))
    assert sunny == [724, 725, 726, 727]
    proposals = []
    for page in range(728, 740):
        data = raw[1048592 + page * 1024:1048592 + (page + 1) * 1024]
        assert len(data) == 1024 and not any(data)
        proposals.append(dict(page=page, zero=True, sha256=hashlib.sha256(data).hexdigest()))
    result = dict(passed=True, installed_ROM_sha256=hashlib.sha256(raw).hexdigest(),
        current_menu_rows=rows, current_menu_final_publication_pages=sorted(menu_pages),
        proposed_raw_ids={'Excitebike':37, 'Prince':38},
        raw_identity_collision=False,
        PRG_proposal=dict(bank=65, physical_half_open=[3584,4360],
            A_PC_half_open=[44544,45320], bytes=776, preimage_SHA256=hashlib.sha256(pad).hexdigest(),
            evidence='Current all-FF source-declared ProtoArtBegin padding after Shinobi0800..0e00. Common records start1108.',
            root_review_required=True),
        CHR_proposals=proposals, current_Sunny_body_table_pages=sunny,
        conditional_RAM_proposal=dict(code_bank=3, state_bank=2, code_CPU_start=40960,
            state_CPU_half_open=[49152,51200], owner_headers=[49120,57312],
            condition='Mutually exclusive exact identity with all existing RAM2/3 owners; invalidate before foreign menu/scene/cold load, publish complete headers last.'),
        resource_granted=False, native_verified=False,
        unresolved=['CHR728..739 need complete current typed-publisher and loader closure, not only Sunny exclusion/zero bytes.',
                    'No runtime admission of raw37/38; all raw-ID dispatch/table bounds must be closed.',
                    '776 resident bytes is a proposed cold-loader budget, not measured fit. Dispatch/retirement and extra root Shinobi growth must fit disjointly.',
                    'Current binary menu census covers90 combinations; private Shinobi successor is not this installed hash.'],
        scope='Actual installed binary menu CPU and exact read-only bytes. Resource proposals only; no ROM changes.')
    (O / 'resource-census.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, menu_rows=len(rows), existing_raw_ids=sorted({r['raw'] for r in rows}),
                         proposed_PRG_bytes=776, proposed_CHR_pages=list(range(728,740)), resource_granted=False)))


if __name__ == '__main__':
    main()
