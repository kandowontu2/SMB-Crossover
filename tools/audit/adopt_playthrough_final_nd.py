"""Compose the remaining reviewed roster packets with exact preimage checks."""
from pathlib import Path
import argparse, hashlib, json, shutil

R = Path(__file__).resolve().parents[2]
V = R/'build/verification'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mac-manifest-sha', required=True)
    a = p.parse_args()
    mac = V/'play-mac-mike-m3-nd/handoff'
    turtles = V/'play-vic-turtles-nd'
    out = V/'new-roster-1-1-nd/adoption-b'
    assert not out.exists()
    assert sha(mac/'manifest.json') == a.mac_manifest_sha
    assert sha(turtles/'manifest.json') == '6ffeeacf04d1f8e6a6fe7ac2ef514d9acbc88d52b2628c68b0c16ac4249f2e3d'
    m = json.loads((mac/'manifest.json').read_text())
    t = json.loads((turtles/'manifest.json').read_text())
    assert sha(mac/'owned-source.zip') == m['sourcezip_SHA256']
    assert sha(mac/'owned-source.patch') == m['context_patch_SHA256']
    for name, digest in m['proofs'].items():
        assert sha(mac/name) == digest, name
    staged = {}
    for item in m['owned_changes']:
        name = item['path']
        assert sha(R/name) == item['before_SHA256'], (name, 'preimage')
        source = mac/'overlay'/name
        assert sha(source) == item['after_SHA256'], (name, 'afterimage')
        staged[name] = source.read_bytes()
    art = json.loads((mac/'world-art-proof/manifest.json').read_text())
    for name, item in art['owned'].items():
        assert hashlib.sha256(staged[name]).hexdigest() == item['after_sha256'], name
    assert sha(mac/'world-art-proof/pixel-proof.json') == art['pixel_proof_sha256']
    assert sha(mac/'world-art-proof/independent-pixel-proof.json') == art['independent_pixel_proof_sha256']
    body = R/'chr/characters/smb3-mario.chr'
    assert body.read_bytes()[:20480] == staged['chr/characters/smb3-mario.chr'][:20480]
    assert len(staged['chr/characters/smb3-mario.chr']) == body.stat().st_size == 21504
    for item in t['owned_sources']:
        if not item['owned']:
            continue
        name = item['path']
        assert name not in staged and sha(R/name) == item['base_sha256'], name
        source = turtles/item['afterimage']
        assert sha(source) == item['staged_sha256'], name
        staged[name] = source.read_bytes()
    h = t['foreign_hunks'][0]
    name = h['file']
    text = staged[name].decode().replace('\r\n', '\n')
    assert text.count(h['old_context']) == 1
    assert 'sta GuestBodyStompAllowed' in text, 'Preserve the earlier body-gate repair'
    text = text.replace(h['old_context'], h['new_context'])
    staged[name] = text.encode()
    out.mkdir(parents=True)
    report = {}
    for name, data in staged.items():
        target = R/name
        backup = out/'before'/name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(target, backup)
        report[name] = dict(before=sha(target), after=hashlib.sha256(data).hexdigest())
        target.write_bytes(data)
        assert sha(target) == report[name]['after']
    receipt = dict(files=report, mac_manifest_sha256=a.mac_manifest_sha,
        turtle_manifest_sha256=sha(turtles/'manifest.json'),
        composed_file=h['file'], turtle_hunk=h,
        only_smb3_world_CHR_page_changed=True, smb3_body_CHR_exact=True)
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(installed=len(staged), receipt=str(out/'receipt.json'))))


if __name__ == '__main__':
    main()
