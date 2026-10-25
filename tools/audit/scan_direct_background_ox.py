"""Run a diagnostic background scan only on verified direct physical frames."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys
import scan_background_transients_oq as original

SCOPE = ('Every timestamped direct PNG is hashed against its verified PPU frame index and decoded. '
         'Only active same-area adjacent physical frames with actual retained DMA coverage enter transient comparisons. '
         'Conservative neighbor sprite masks and outer8pixels remain excluded. Diagnostic image alignment spans0..8pixels '
         'to accommodate independently observed skipped-publication catch-up; it is not a relaxed gameplay/camera assertion '
         'or a claim that rendered jumps are acceptable. Same-before/after yet different-middle12pixel clusters are '
         'candidates requiring human/source investigation. Persistent corruption, longer flashes, sprite/body omissions, '
         'missing actors, every item and other graphical or source-fidelity defects are outside this detector. '
         'An empty candidate list is not an all-graphics pass. Older asynchronous decoder PNGs are not scanned here.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capture', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    capture = json.loads((a.capture / 'proof.json').read_text())
    assert capture['passed'] and capture['fixed_inputs_and_trace_exact']
    assert capture['actual_PPU_frame_ids_complete'] and capture['every_saved_PNG_RGB_exact']
    assert capture['result']['cleared'] and capture['result']['deaths'] == 0
    index = a.capture / 'direct-frame-index.csv'
    assert sha(index) == capture['frame_index_sha256']
    records = list(csv.DictReader(index.open()))
    assert len(records) == capture['direct_frames']
    for row in records:
        assert row['frame'] == row['ppuFrame']
        assert sha(a.capture / 'frames' / f"{int(row['frame']):06d}.png") == row['PNG_sha256']
    metadata = dict(fixed_replay=True, exit=0, ROM_sha256=capture['ROM_sha256'], result=capture['result'],
                    config=dict(name=capture['identity'], behavior=capture['mode']))
    source = Path(original.__file__).read_text()
    replacements = {
        "manifest=json.loads((a.route/'manifest.json').read_text())": 'manifest=explicit_metadata',
        "manifest_sha256=sha(a.route/'manifest.json')": "direct_capture_proof_sha256=sha(a.route/'proof.json')",
    }
    for before, after in replacements.items():
        assert source.count(before) == 1
        source = source.replace(before, after)
    assert source.count('range(5)') == 2
    source = source.replace('range(5)', 'range(9)')
    start = source.index("        scope='Every retained PNG")
    end = source.index('\n    (a.output', start)
    source = source[:start] + '        scope=DIRECT_CAPTURE_SCOPE)' + source[end:]
    namespace = dict(__name__='direct_physical_frame_diagnostic', __file__=str(Path(__file__)),
                     explicit_metadata=metadata, DIRECT_CAPTURE_SCOPE=SCOPE)
    exec(compile(source, '<direct physical frame diagnostic>', 'exec'), namespace)
    sys.argv = [str(Path(__file__)), '--route', str(a.capture), '--output', str(a.output)]
    namespace['main']()
    proof = a.output / 'proof.json'
    q = json.loads(proof.read_text())
    q.update(direct_PPU_frames=True, every_PNG_frame_index_hash_exact=True,
             direct_frame_index_sha256=sha(index), alignment_search_max_pixels=8,
             original_scanner_sha256=sha(Path(original.__file__)), adapter_sha256=sha(Path(__file__)))
    proof.write_text(json.dumps(q, indent=2) + '\n')


if __name__ == '__main__':
    main()
