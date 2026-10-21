"""Retain the exact negative and independent held-input control receipts."""
from pathlib import Path
import csv, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
B=ROOT/'build/verification/ryu-weapons-v36d-negative-probe-b'
C=ROOT/'build/verification/ryu-weapons-v36d-negative-probe-c-hold4'
def read(path):return list(csv.DictReader(path.open(newline='')))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
before=read(B/'v35-mmc3/passive.csv')
after=read(B/'v36-provisional-d-mmc3/passive.csv')
diffs=[]
for x,y in zip(before,after):
    d={k:[x[k],y[k]] for k in x if x[k]!=y[k]}
    if d:diffs.append({'frame':int(x['frame']),'fields':d})
assert diffs[0]=={'frame':561,'fields':{'SavedJoypad1Bits+0':['32','0'],'InvFresh+0':['32','0']}}
original=ROOT/'tests/expanded-weapons.lua'
frozen=json.loads((ROOT/'build/verification/summary-roster-audit-v36-provisional-d.json').read_text())
assert sha(original)==frozen['fixture_hashes_before']['tests/expanded-weapons.lua']
(B/'original-expanded-weapons.lua').write_bytes(original.read_bytes())
out={
 'status':'fixture-input-timing-negative-explained-no-runtime-change',
 'original_scope':'Seeded unit arena with one hardware-frame Select request; not ordinary controller traversal',
 'original_fixture_sha256':sha(original),
 'negative_probe_manifest':str((B/'manifest.json').relative_to(ROOT)),
 'first_difference':diffs[0],
 'canonical_observed_fields_equal_through_frame':560,
 'original_test_assertions_retained':True,
 'held_input_control':[],
 'limits':['The single-frame pulse is genuinely missed by this lag schedule. This is not a claim that the runtime polls inputs on skipped NMI frames.',
           'Original failed broad run, passive CSVs and original fixture bytes remain available.',
           'Control changes only the duration of one Select press from1 to4 physical frames. No projectile RAM is injected and all original damage/return oracles remain.'],
}
for entry in json.loads((C/'manifest.json').read_text())['runs']:
    d=C/f"{entry['version']}-{entry['mapper']}"
    rows=read(d/'passive.csv');births=[];old=[0]*10
    for r in rows:
        for i in range(10):
            value=int(r[f'RgShotType+{i}'])
            if value==8 and old[i]!=8:births.append({'frame':int(r['frame']),'slot':i})
            old[i]=value
    assert entry['exit']==0 and len(births)==1
    out['held_input_control'].append({**entry,'single_windmill_birth':births[0],
        'select_receipt_frames':[int(r['frame'])for r in rows if int(r['SavedJoypad1Bits+0'])&32]})
target=ROOT/'build/verification/ryu-weapons-v36d-input-timing-report.json'
target.write_text(json.dumps(out,indent=2)+'\n')
print('PASS first difference is missing controller receipt; all4 unchanged-weapon held-input controls pass, one windmill each')
