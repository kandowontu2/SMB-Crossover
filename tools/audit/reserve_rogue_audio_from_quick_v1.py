"""Conditionally partition ten proven unused Quick pages for the joint Rogue merge."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out = R/'docs/qa/checkpoints/2026-10-30/rogue-quick-audio-private-allocation'
    assert not out.exists()
    proposal_path = R/'build/quickman-wram-palette-v6/unused-PRG-review.json'
    proposal = json.loads(proposal_path.read_text())
    bindings = dict(proposal['bindings'])
    for path, digest in bindings.items():
        assert sha(path) == digest, path
    prior_path = R/'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation/root-review-and-reservations.json'
    prior = json.loads(prior_path.read_text())
    allowed = prior['Quick_Man']['PRG']
    blocks = proposal['conditional_ten_page_proposal']
    assert len(blocks) == 10 and sum(block['end']-block['start'] for block in blocks) == 2560
    cases = [
        (R/'build/character-host-union-resources-v1/ice/candidate.nes', '3925aa18859df68958ff782e5acc6558f877f1c0e81f22bd1e1ae54db9746ddb'),
        (R/'build/quickman-wram-palette-v6/candidate.nes', '710672e7f0451b136752b8b5455686e6df517027ecb4b7272f49785a40a07610'),
        (R/'build/rogue-current-menu-v8/candidate.nes', 'cdce3d9f26c26e367ca2aa1e4cfee0101c005bdb8f8ac10ea78a47fed3f8707f'),
        (R/'build/arthur-host-cache-v1/candidate.nes', '3daf811f57ce62a2e9c44707c5359d9f54af038bdd80c652dab3ffca22eee644')]
    roots = []
    for path, digest in cases:
        assert sha(path) == digest, path
        raw = path.read_bytes()
        for block in blocks:
            assert block['start'] % 256 == 0 and block['end']-block['start'] == 256
            assert any(lease['bank'] == block['bank'] and lease['start'] <= block['start'] and block['end'] <= lease['end'] for lease in allowed)
            start = 16+block['bank']*8192+block['start']
            assert raw[start:start+256] == bytes([255])*256, (path, block)
        bindings[str(path)] = digest
        roots.append(dict(path=str(path), sha256=digest, ten_pages_exact_FF=True))
    bindings.update({str(path): sha(path) for path in [proposal_path, prior_path, Path(__file__).resolve()]})
    report = dict(status='CONDITIONAL_PRIVATE_JOINT_SOURCE_ALLOCATION_NO_SHARED_ADOPTION',
        authority='These exact pages were already source-reviewed and granted to Quick. Actual current linked segments/symbols exclude them. Fill checks across four current roots confirm the partition; FF alone is not the ownership authority.',
        blocks=blocks, bytes=2560, prior_Quick_retained_bytes=10060,
        joint_branch_Quick_retained_bytes_after_partition=7500,
        Quick_current_PRG_used=1916, Quick_remaining_measured_unused=5584,
        preserved_growth='All A70 router, C82 loader and C98 cold-portrait growth gaps retained.',
        assigned_use='Ten exact nonexecuting Rogue source audio pages displaced from A79:B600..<C000 by the V13 union. No other allocation.',
        constraints=['Implement through genuine source segments/linker layout and all192logical-page bank/high map entries. Preserve low8bits and use A-window high addresses; do not binary-overlay independent images.',
                     'Preserve original ten page bytes and every source audio consumer/APU write/cycle, with real IRQ/NMI/raw-mapper restore controls.',
                     'Only unified private source producers based on these exact roots may use the partition. Old pre-WRAM Quick producers retain historical meanings and cannot be overlaid.',
                     'Do not change RAM0/WRAM/CHR/header or canonical/shared ROM through this grant.',
                     'Quick source audio and cadence future needs are not measured or guaranteed by the remaining headroom.'],
        preimages=roots, bindings=bindings, shared_installation=False)
    out.mkdir()
    target = out/'root-review-and-reservations.json'
    target.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(grant=str(target), sha256=sha(target), blocks=10, bytes=2560)))


if __name__ == '__main__':
    main()
