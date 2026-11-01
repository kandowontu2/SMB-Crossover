"""Confirm completed delivery after the publisher's locale-only README failure."""
from pathlib import Path
import hashlib,json,zipfile
import publish_ready81_nightly_bounded_v1 as P


def main():
    o=P.R/'build/ready81-delivery-final-1101-v1';o.mkdir(exist_ok=True)
    stage=P.bound(P.J/'source-stage.json');receipt=json.loads((P.R/'docs/qa/nightly-2026-11-01-ready81.json').read_text())
    assert stage['passed'] and stage['native'] and P.sha(P.DEST)==P.EXPECTED==receipt['output_sha256']
    text=(P.R/'README.md').read_text(encoding='utf-8');assert '**81 playable identities**'in text and '**5 individual identities**'in text
    for key in ['source','native']:
        asset=receipt['verification'][key];path=P.R/asset['path'];assert P.sha(path)==asset['sha256']
        with zipfile.ZipFile(path)as z:assert z.testzip()is None
    q=dict(passed=True,installed=True,backup_created=False,ROM_sha256=P.EXPECTED,playable=81,source_stage_sha256=P.sha(P.J/'source-stage.json'),
           source_and_native_archives_verified=True,README_completed_as_UTF8=True,
           note='Original publisher completed ROM/receipts, then failed to decode the README using the Windows locale. UTF8 documentation edit was completed separately; tested ROM and immutable source stage unchanged.',
           cleanup_candidates=['wwf-native-1101-v1-hogan','wwf-native-1101-v1-diagnostic','wwf-native-1101-v1-stack','wwf-native-1101-v1-banks','wwf-native-1101-v2-hogan','wwf-native-1101-v3-hogan'],
           bindings={str(p.resolve()):P.sha(p)for p in[Path(__file__),P.J/'source-stage.json',P.R/'README.md',P.R/'docs/qa/nightly-2026-11-01-ready81.json']})
    before=P.R/'build/wwf-native-1101-v1-banks/capture/result.json'
    if before.exists():
        old=json.loads(before.read_text());q['fixed_bank_regression']=dict(old_ROM=old['ROM_sha256'],old_passed=old['passed'],last_bank_writes=old['bank_events'],cause='Audio restored hardware A but left CurrentBank at191; a later far return selected graphics data. Source now restores the software owner from the saved AudioUpdate frame.')
    P.save(o/'result.json',q);P.save(P.R/'docs/qa/nightly-2026-11-01-ready81-finalization.json',q)
    print(json.dumps(dict(passed=True,installed=True,ROM=P.EXPECTED,playable=81)))


if __name__=='__main__':main()
