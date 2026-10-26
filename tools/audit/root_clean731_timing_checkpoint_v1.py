"""Freeze finite actual clean731 timing evidence without binaries or raw captures."""
from pathlib import Path
import collections
import hashlib
import json
import shutil
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT/'docs/qa/checkpoints/2026-10-26/presentation-timing-clean731'
ROM = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def main():
    assert not OUT.exists()
    p = D/'root-presentation450-731-v1'
    h = D/'root-clean731-hard1f-v1'
    review = json.loads((p/'ROOT-review-v1/proof.json').read_text(encoding='utf-8'))
    compare = json.loads((h/'native-launch-v1/comparison/proof.json').read_text(encoding='utf-8'))
    assert review['passed'] and review['ROM_sha256'] == ROM
    assert compare['passed'] and compare['ROM_sha256'] == ROM
    for f, digest in review['bindings'].items():
        assert sha(f) == digest, f
    ready = json.loads((h/'readiness-source-only.json').read_text(encoding='utf-8'))
    for f, digest in ready['all_frozen_bindings'].items():
        assert sha(f) == digest, f
    rows = [json.loads(s) for s in (h/'fixture/dma-bus.jsonl').read_text(encoding='utf-8').splitlines()]
    assert collections.Counter(r['kind'] for r in rows) == {'DMA-start':168, 'DMA-complete':168}
    for i in range(0, len(rows), 2):
        start, finish = rows[i:i+2]
        assert start['kind'] == 'DMA-start' and finish['kind'] == 'DMA-complete'
        assert len(bytes.fromhex(start['source_hex'])) == 256
        assert start['source_hex'] == finish['hardware_hex'] and finish['data_writes'] == 256
        assert start['stamp']['mask'] & 24 == 0 and finish['stamp']['mask'] & 24 == 0
    a, b = h/'fixture/case-end.argb', D/'root-composed3cee-hard1f-v1/fixture/case-end.argb'
    assert a.stat().st_size == 245760 and sha(a) == sha(b)
    OUT.mkdir(parents=True)
    files = {
        '450-readiness.json':p/'readiness.json',
        '450-grant.json':p/'ROOT-grant.json',
        '450-result.json':p/'result.json',
        '450-receipt.json':p/'native-receipt.json',
        '450-independent-review.json':p/'ROOT-review-v1/proof.json',
        '450-all275-RGB-hashes.json':p/'ROOT-review-v1/all275-RGB-hashes.json',
        '450-selected-actual-frames.png':p/'ROOT-review-v1/selected-actual-frames.png',
        'pressure-readiness.json':h/'readiness-source-only.json',
        'pressure-grant.json':h/'ROOT-grant.json',
        'pressure-launch.json':h/'native-launch-v1/proof.json',
        'pressure-native.json':h/'fixture/proof.json',
        'pressure-comparison.json':h/'native-launch-v1/comparison/proof.json',
        'pressure-DMA-bus.jsonl':h/'fixture/dma-bus.jsonl',
    }
    for name, source in files.items():
        shutil.copyfile(source, OUT/name)
    rgb = np.frombuffer(a.read_bytes(), dtype=np.uint8).reshape((240,256,4))[:,:,[2,1,0]]
    Image.fromarray(rgb).save(OUT/'pressure-actual-case-end.png')
    external = {str(f):sha(f) for parent in [p,h] for f in parent.rglob('*') if f.is_file()}
    put(OUT/'external-artifact-hashes.json', external)
    put(OUT/'proof.json', dict(
        passed=True, component_only=True, adopted=False, goal_complete=False, ROM_sha256=ROM,
        preflight_actual_PPU_frames=450, lossless_saved_frames=275,
        preflight_full256_DMA_checks=402, preflight_safe_enables=72,
        preflight_NMI_register_stack_SMC_checks=442, preflight_IRQ31_checks=79,
        pressure_complete_source_calls=280, pressure_APU_stores=850,
        independent_pressure_full256_DMA_checks=168,
        pressure_complete_game_updates=240, pressure_complete_game_draws=168,
        pressure_compared_frames=280, pressure_compared_draws=167,
        pressure_draw_prefix_deferrals=[], pressure_case_end_exact_3cee=True,
        pressure_case_end_ARGB_sha256=sha(a),
        source_readiness_bindings_reverified=len(ready['all_frozen_bindings']),
        visual_review='ROOT viewed the eight saved 450 wholeframes; menu and first-active372 HUD stable in this sample. Physical body/shot visibility remains open. The pressure case-end is independently byte-exact to actual3cee; viewing this image is separate.',
        limits='Finite actual timing checks only. 450 fixed physical-frame inputs are a new preflight, not an exact full historical replay. Pressure is the existing staged Hard1F240 source workload, not natural level completion. No all-menu/all-roster/whole-campaign, waveform, powerup, reduced-lag or sprite-fairness claim. No ROM, audio, settings or lossless payload copied.'))
    (OUT/'README.txt').write_text(
        'CLEAN731 FINITE TIMING COMPONENTS -- NOT AN ADOPTION RECEIPT\n\n'
        'Original Mega/Proto shots are restored; the held shot-budget experiment is absent.\n'
        'Fresh 450-frame physical input test:402 full DMA pages,72 safe enables,\n'
        '442 NMI returns and79 IRQ31 checks pass.275 actual PPU frames176..450\n'
        'are hashed; eight actual wholeframes appear on the sheet. ROOT viewed\n'
        'all eight. The first-active372 HUD does not wrap; enable is260:83 and\n'
        'DMA completion260:72. Queue/phase differences also affect that timing.\n\n'
        'Fresh staged heavy-audio Hard1F240 control passes the strict existing\n'
        'source/hardware/cadence comparison with3cee:280 source calls,850 APU\n'
        'stores and no draw-prefix deferral. Complete totals240updates/168draws;\n'
        'the compared280-frame scope has167draws. ROOT separately compared\n'
        'every byte of all168 physical DMA pages while rendering was disabled.\n'
        'The actual case-end ARGB is byte-exact to3cee. This preserves cadence;\n'
        'it does not remove existing gameplay lag or prove sprite visibility.\n\n'
        'Full-menu1800 review, broader gameplay and every-powerup work remain\n'
        'separate. Old b0/59 negative and prototype results keep their own hashes.\n'
        'External capture paths are hashes only; no private binaries are included.\n', encoding='utf-8')
    put(OUT/'manifest.json', {f.name:dict(sha256=sha(f),bytes=f.stat().st_size) for f in sorted(OUT.iterdir()) if f.is_file()})
    print(json.dumps(dict(passed=True, checkpoint=str(OUT), payload_files=len(list(OUT.iterdir())), bytes=sum(f.stat().st_size for f in OUT.iterdir()), proof_sha256=sha(OUT/'proof.json'))))


if __name__ == '__main__':
    main()
