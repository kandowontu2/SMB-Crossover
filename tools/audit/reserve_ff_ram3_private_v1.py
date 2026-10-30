"""Reserve a source-qualified private FF carrier/RAM image, with dense prerequisites."""
from pathlib import Path
import json
from checkpoint_roster_progress_1030_v2 import R, D, save, sha


if __name__ == '__main__':
    folder = R/'build/final-fantasy-execution-audit-v1'
    path = folder/'handoff.json'
    assert sha(path) == '6576763c124d3267cd243c7cac65057cb34a713fc39e3ad5ce0b708c112af866'
    handoff = json.loads(path.read_text())
    assert not handoff['allocation'] and not handoff['native']
    bindings = dict(handoff['bindings'])
    for child in list(bindings):
        if Path(child).suffix == '.json':
            value = json.loads(Path(child).read_text())
            for item, digest in value.get('bindings', {}).items():
                assert isinstance(digest, str) and len(digest) == 64, item
                assert item not in bindings or bindings[item] == digest, item
                bindings[item] = digest
    for item, digest in bindings.items():
        assert sha(item) == digest, item
    bindings[str(path)] = sha(path)
    bindings[str(Path(__file__).resolve())] = sha(__file__)
    base = R/'build/required-rcr-ink-v2/candidate/candidate.nes'
    assert sha(base) == '753b6bd1e51bb6c427206f841e63790bfd79fe2a3cca964e04254408f87ead53'
    raw = base.read_bytes()
    assert raw[1048592+893*1024:1048592+901*1024] == bytes(8192)
    name = 'ff-ram3-private-allocation'
    save(name, dict(
        status='CONDITIONAL_PRIVATE_FF_LOADER_ALLOCATION_NO_SHARED_HEADER_CHANGE',
        owner='Final Fantasy four-class source integration, selected raw22 only',
        source_audit_sha256=sha(path),
        source_proof=dict(current_host='aadbbb89', actual_motion_pairs=192,
                          source_updates=2304, render_pairs=160, publication_pairs=128,
                          real_vector_cases=804, source_bytes_preserved_per_vector=143),
        CHR=dict(first_page=893, page_count=8, end_exclusive=901, bytes=8192,
                 condition='Only after actual dense Parodius832..<868 source/table composition. Unmodified V13 genuinely publishes896..900 here and must never receive this carrier.',
                 preserve=['Arthur868..<884', 'Quick884..<893', 'all body graphics0..<868',
                           'FF graphics756..<788', 'unallocated901..<1024']),
        PRG_RAM=dict(private_header_bytes=32768, shared_header_bytes=8192,
                     bank0='Existing global6000..7FFF unchanged; never remap5113 or lock5102/5103.',
                     bank1='Quick source execution remains reserved.',
                     bank2='Quick/Arthur temporal ownership and sharedC2 cookie remain untouched.',
                     bank3='Exclusive FF code/host adapters in A000..BFFF with raw03 tag; same physical image may be inspected through C3.',
                     cookie='RAM3 offset1FE0..<1FF0; validityA7 published last, family22, class-independent code version/fingerprint. Never alias C2 cookie.'),
        retained_PRG='Existing FF A62:AA00..<B6903216B only, reclaimed through genuine source relocation for ROM loader/router/preview. No resident/new bank lease.',
        retained_ART='Existing C93:D000..<E0004096B, current3410B source metadata/palettes retained; no other C93 owner displaced.',
        requirements=[
            'Genuinely source-link private32KB-header candidate from exact current reproduction. No old PRG overlay or source-bank literal copied across a different host.',
            'Load at real native forced-blank InitScreen with NmiDisable negative; verify full8KB through actual buffered2007 reads before executing any byte.',
            'Invalidate cookie first, publish last. Correct cold/warm/new-game/life/area/retirement/alternate-player ownership must be verified.',
            'Preserve actual PPUCTRL/latch/scroll/upper/12CHR state, rawA/C maps and shadows, livepage1/all33SMC, IRQ/NMI and intentional FF R0/R1 outputs.',
            'Use raw03 FarCallCommon, not ROM83. Restore caller C explicitly around FF workers; source graphics legitimately leaves C=ROM93.',
            'Retain ROM-only menu/lives preview before verified RAM readiness; no frontend can execute an unbuilt cache.',
            'Genuine host terrain/combat/full OAM-palette/audio/powerup integration and native1-1/every-item tests remain required before promotion.'
        ],
        limits=['Resource grant only; virtual preload CPU proof is not a real loader or native playthrough.',
                'Shared Downloads remains ec2f23ed/8KBWRAM. No physical cartridge compatibility or constant60Hz claim.']), bindings)
    review = D/name/'root-review.json'
    reservation = D/name/'root-review-and-reservations.json'
    reservation.write_bytes(review.read_bytes())
    print(json.dumps(dict(reservations=str(reservation), sha256=sha(reservation))))
