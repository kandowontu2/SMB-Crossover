"""Independent aggregation of all retained v47/v48 crowd counterexamples."""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/verification/goomba47-48-crowd-review-a.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()
    report=dict(result='unaccepted-analysis',inputs=[],runs=[],negative_rows=[],
        canonical_updates=0,all_raw_negatives_retained=True,
        qualification='Physical frames and OAM visibility depend on phase; CPU savings do not promise universal redraw or visibility improvement.')
    metrics=('physicalFrames','drawAllCalls','skippedNmis','visibleEnemyFrames',
             'fullyInvisibleEnemyFrames','physicalDmas','meanForegroundExcludingDrawCycles')
    for family in ('three','other','six-repeat'):
        p=ROOT/f'build/verification/plain-walking-v47-v48a-terrain-{family}-comparison.json'
        d=json.loads(p.read_text())
        assert d['canonical_mismatch_count']==0
        report['inputs'].append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p)))
        for run in d['runs']:
            assert run['canonical_rows']==1200 and run['canonical_observation_fields']==204
            assert run['canonical_before_sha256']==run['canonical_after_sha256']
            report['canonical_updates']+=run['canonical_rows']
            scenes=run['scenes']
            totals={name:{side:sum(s[name][side] for s in scenes)for side in ('before','after')}
                    for name in metrics if not name.startswith('mean')}
            report['runs'].append(dict(family=family,character=run['character'],
                canonical_rows=run['canonical_rows'],totals=totals))
            for scene in scenes:
                negative=[]
                for name in ('physicalFrames','skippedNmis','fullyInvisibleEnemyFrames'):
                    if scene[name]['after']>scene[name]['before']:negative.append(name)
                for name in ('drawAllCalls','visibleEnemyFrames','physicalDmas'):
                    if scene[name]['after']<scene[name]['before']:negative.append(name)
                if negative:
                    report['negative_rows'].append(dict(family=family,character=run['character'],
                        scene=scene['scene'],mode=scene['mode'],outlinesOff=scene['outlinesOff'],
                        enemies=scene['enemies'],negative_metrics=negative,
                        metrics={name:scene[name]for name in metrics}))
    assert report['canonical_updates']==13200 and len(report['runs'])==11
    report.update(result='reviewed-all-13200-matched-gameplay-updates',script_sha256=sha(Path(__file__)))
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(report['result'],'negative rows retained:',len(report['negative_rows']))
    for r in report['runs']:
        if r['family']=='six-repeat':print(r['character'],json.dumps(r['totals']))

if __name__=='__main__':main()
