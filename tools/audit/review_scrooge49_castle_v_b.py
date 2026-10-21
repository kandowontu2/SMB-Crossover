"""Correct one host observer's firebar Y-register interpretation, no replay.

At the captured R5=1 contact, Y is the table index0 left by LDY R5,
not the tested player coordinate. The original V negative remains literal.
"""
from pathlib import Path
import difflib,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/mm49n-scrooge-castle-observer-v'
OUT=ROOT/'build/verification/root49n-scrooge-castle-v-host-review-b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(PACKET/'freeze.json')=='141e0ce6ff5dc7e05108ea9731c0b142f9a1d15206e1a2549d98651f62b71003'
    frozen=json.loads((PACKET/'freeze.json').read_text())
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    negative=ROOT/'build/verification/root49n-scrooge-castle-observe-v-review-a.json'
    old_negative_pin=sha(negative)
    original=(PACKET/'check.py').read_text()
    old="  assert int(positive['Y'])==(int(positive['y'])+12*r[5])%256\n  mag=lambda v:min(v%256,(-v)%256)\n  dy=mag(int(positive['Y'])-r[7]);dx=mag((relative[0]+4)%256-r[6])"
    new="""  assert r[5]==1 and int(positive['Y'])==0,'This actual contact follows first indexed retry, not the initial TYA sample'
  h=im.hook('FirebarYPos');table=list(im.raw[h['rom_offset']:h['rom_offset']+2]);assert table==[12,24]
  tested_y=(int(positive['y'])+table[int(positive['Y'])])%256
  mag=lambda v:min(v%256,(-v)%256)
  dy=mag(tested_y-r[7]);dx=mag((relative[0]+4)%256-r[6])"""
    assert original.count(old)==1
    derived=original.replace(old,new)
    marker="'native_abs_deltas':[dx,dy],'actual_saved_return':expected_return}"
    assert derived.count(marker)==1
    derived=derived.replace(marker,"'native_abs_deltas':[dx,dy],'actual_saved_return':expected_return,'actual_tested_player_point':[(relative[0]+4)%256,tested_y],'literal_FirebarYPos':table,'Y_register_is_retry_table_index':int(positive['Y'])}")
    OUT.mkdir();(OUT/'derived-check.py').write_text(derived)
    (OUT/'host-check-only.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),derived.splitlines(True),fromfile='original-V-check',tofile='actual-indexed-point-check')))
    args=sys.argv;sys.argv=[str(PACKET/'check.py'),'--native-exit','1','--out',str(OUT/'review.json')]
    try:
        try:exec(compile(derived,str(OUT/'derived-check.py'),'exec'),{'__file__':str(PACKET/'check.py'),'__name__':'__main__'})
        except SystemExit as e:assert e.code==0
    finally:sys.argv=args
    assert sha(negative)==old_negative_pin
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    reviewed=json.loads((OUT/'review.json').read_text());owner=reviewed['actual_firebar_owner']
    receipt={'status':'PASS_FULL9CSV_NEUTRALITY_AND_ACTUAL_INDEXED_FIREBAR_CONTACT',
             'script_sha256':sha(Path(__file__)),'original_frozen_packet_sha256':sha(PACKET/'freeze.json'),
             'original_negative_sha256':old_negative_pin,'derived_check_sha256':sha(OUT/'derived-check.py'),
             'review_sha256':sha(OUT/'review.json'),'native_abs_deltas':owner['native_abs_deltas'],
             'tested_point':owner['actual_tested_player_point'],'slot':owner['slot'],
             'new_native_CPU_model_runs':0,'qualification':'Only the observed R5=1/Y=0 indexed retry is admitted. Native G death remains negative; no route clear or source hitbox fidelity claim.'}
    (OUT/'report.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))

if __name__=='__main__':main()
