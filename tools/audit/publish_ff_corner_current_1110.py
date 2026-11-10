"""Publish only the tested FF Downloads image as the sole Current IPS, in RAM."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from check_ff_physical_routes_stdout_1110 import R, PIN, SCRIPT, SCRIPT_PIN, NIGHTLY, CANDIDATE
from deliver_manual_title_1110 import ips_for, apply_ips, SOURCE_BASE
from nightly_patch_guard_v1 import check
import check_ff_head_corner_1110_v2 as Fix

REPO = 'kandowontu2/SMB-Crossover'
ASSET = 'SMB-Crossover-Latest-WIP-MMC5.ips'
PATCH_PIN = '0a1960fecf87202e175a26004e6b8f384ff93fdb40fffd1ed582fbc28fd57ab0'
OLD_PATCH = '76c918b4bd1fb51319a28f1e09a19f98ba1b47b063c647616cc23530e059e663'
REPORT = R / 'docs/qa/ff-head-corner-1110.md'
RECEIPTS = (
    '5ff65b833f37a33f2805cfe78a0b3f3d4e94c4fd3889e9f4cd64605b6e2ecd3d',
    'e459a78ab4c82dc4dff14a586502efa1a131ccb1ca0aa59454d61e703c34b03c',
    '526700c034bb471ce7ab68d84fdc983224b0f173917f01bb26afd2a2fc231477',
    '989cc82be327567590df4f88f627d51e245d965d0fbb39f3d3f5f3ff7a2026ef')


def api(endpoint, method='GET', data=None, binary=False):
    command = ['gh', 'api', endpoint, '--method', method]
    if data is not None:
        command += ['--input', '-']
        if binary:
            # uploads.github.com requires a known length for stdin bodies.
            command += ['-H', 'Content-Type: application/octet-stream',
                        '-H', f'Content-Length: {len(data)}']
    elif binary:
        command += ['-H', 'Accept: application/octet-stream']
    p = subprocess.run(command, input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return p.stdout if binary and data is None else (json.loads(p.stdout) if p.stdout else None)


def upload(url, payload):
    assert url.startswith(f'https://uploads.github.com/repos/{REPO}/releases/')
    return api(url.split('{', 1)[0] + '?name=' + ASSET, 'POST', payload, binary=True)


def release_body(head):
    return ('Current MMC5 WIP nightly. Apply the sole IPS to clean headered Super Mario Bros. (World).\n\n'
        f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
        'All 100 named roster entries remain startable; some added characters still use borrowed prototype moves.\n\n'
        'Fixes Final Fantasy staircase head/side corners and automatic side-pipe entry. '
        'All four classes earned mushroom and flower, used their upgraded attack, cleared 1-1 and entered '
        'underground 1-2 without injury in actual Mesen. The installed Downloads ROM repeated the run. '
        'Star/1UP and Black Mage Bolt/Ice have separate CPU qualifications.\n\n'
        'Heavy FF lag, further abilities and visual review remain unfinished. The separate guard optimization '
        'is source-only and is not in this ROM. No helper platform locations changed.\n')

def main(report_sha=None):
    if report_sha is None:
        ap = argparse.ArgumentParser(description=__doc__)
        ap.add_argument('--report-sha', required=True)
        report_sha = ap.parse_args().report_sha
    report_path = REPORT
    report = report_path.read_bytes()
    assert sha256(report).hexdigest() == report_sha
    assert all(value.encode() in report for value in (*RECEIPTS, SCRIPT_PIN, PIN, PATCH_PIN))
    assert sha256(SCRIPT.read_bytes()).hexdigest() == SCRIPT_PIN
    guard = check(NIGHTLY)
    assert guard['ROM_sha256'] == PIN
    raw = NIGHTLY.read_bytes()
    # The installed exact image and qualified source are authoritative after
    # its byte-identical disposable build copy has been pruned for storage.
    assert Fix.proposal(Fix.V1.BASE.read_bytes())[0] == raw
    if CANDIDATE.exists():
        assert CANDIDATE.read_bytes() == raw
    patch = ips_for(raw)
    assert sha256(patch).hexdigest() == PATCH_PIN
    assert apply_ips(SOURCE_BASE.read_bytes(), patch)[0] == raw
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    remote = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/master'], text=True).split()[0]
    assert head == remote, 'Push the tested source before refreshing Current'
    current = api(f'repos/{REPO}/releases/tags/Current')
    asset, = current['assets']
    assert current['tag_name'] == 'Current' and asset['name'] == ASSET
    assert asset['digest'] in ('sha256:' + OLD_PATCH, 'sha256:' + PATCH_PIN)
    if asset['digest'] != 'sha256:' + PATCH_PIN:
        # Retain the previous public IPS in memory only for upload rollback.
        previous = api(f'repos/{REPO}/releases/assets/{asset["id"]}', binary=True)
        assert sha256(previous).hexdigest() == OLD_PATCH
        api(f'repos/{REPO}/releases/assets/{asset["id"]}', 'DELETE')
        try:
            upload(current['upload_url'], patch)
        except BaseException:
            remaining = api(f'repos/{REPO}/releases/{current["id"]}')['assets']
            if not remaining:
                upload(current['upload_url'], previous)
            raise
    body = release_body(head)
    api(f'repos/{REPO}/releases/{current["id"]}', 'PATCH', json.dumps(dict(body=body, make_latest='true')).encode())
    latest = api(f'repos/{REPO}/releases/latest')
    asset, = latest['assets']
    assert latest['id'] == current['id'] and latest['tag_name'] == 'Current'
    assert asset['name'] == ASSET and asset['digest'] == 'sha256:' + PATCH_PIN
    downloaded = api(f'repos/{REPO}/releases/assets/{asset["id"]}', binary=True)
    assert downloaded == patch and apply_ips(SOURCE_BASE.read_bytes(), downloaded)[0] == NIGHTLY.read_bytes() == raw
    after = check(NIGHTLY)
    assert after['ROM_sha256'] == PIN
    print(json.dumps(dict(passed=True, Current_and_Latest=True, sole_asset=ASSET,
        source_commit=head, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN, IPS_bytes=len(patch),
        remote_asset_id=asset['id'], downloaded_roundtrip_equals_Downloads=True,
        automatic_patch_guard=after, generated_files=0, private_ROM_published=False,
        report_SHA256=report_sha, native_receipts=RECEIPTS)), flush=True)


if __name__ == '__main__':
    main()
