"""Publish reviewed source-only CF dependencies without installing candidates."""
from pathlib import Path
import json
import shutil
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_functional_roster_visuals58_v1 as B


def main():
    review=R/'docs/qa/checkpoints/2026-10-31/cf-transport-root-review-v1/review.json'
    checked=json.loads(review.read_text());B.bound(checked)
    assert checked['passed'] and len(checked['packets'])==3
    destinations=[]
    for row,slug in zip(checked['packets'][1:],['contra-force-retirement','contra-force-checkpoint-loader']):
        packet=Path(row['packet']);assert B.sha(packet)==row['handoff_sha256']
        archive=Path(row['archive']);assert B.sha(archive)==row['archive_sha256']
        d=R/'docs/qa/checkpoints/2026-10-31'/slug;assert not d.exists();d.mkdir(parents=True)
        for p in [packet,archive,packet.parent/'API.json']:
            assert p.is_file();shutil.copy2(p,d/p.name)
        (d/'README.md').write_text(
            'Frozen Contra Force source dependency, independently rehashed by root. '
            'The sibling handoff describes its actual API, tests, retained fixture failures and '
            'explicit limits. Its small source delta archive is relative to the predecessor '
            'named in the handoff; original ROM/object/debug binaries are excluded.\n\n'
            'Retirement invalidates stale CF code before another family reuses mapped RAM. '
            'The checkpoint loader invokes the real native CHR publisher internally before '
            'its buffered24KB transfer. These isolated workers do not establish installed '
            'menu/scene coverage. The full source composition and character presentation '
            'are separate ongoing work. CF and Battletoads remain pending; Downloads stays '
            'on the verified66-character Bowser build.\n',encoding='utf-8',newline='\n')
        destinations.append(str(d))
    p=review.parent/'publication.json'
    B.write(p,json.dumps(dict(source_only=True,native=False,installed=False,CF_pending=True,BT_pending=True,
        checkpoints=destinations,bindings={str(x):B.sha(x) for x in [Path(__file__),review]}),indent=2)+'\n')
    print(json.dumps(dict(source_only=True,checkpoints=destinations)))


if __name__=='__main__':main()
