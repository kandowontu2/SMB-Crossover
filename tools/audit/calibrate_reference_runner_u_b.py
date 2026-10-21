"""Calibrate retained native/FFV1/MP4 capture on an exact known negative.

This is a recording-pipeline check, not a successful gameplay playthrough.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/mm48-private-reference-runner-u'
OUT=ROOT/'build/verification/root-reference-runner-u-recording-b'
NATIVE=ROOT/'build/roster-through-2-2/root-reference-u-capture-b-1-v0-mmc3'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not OUT.exists()and not NATIVE.exists()
    assert sha(PACKET/'frozen.json')=='366567ffa66ab34c5dce25e1f4b08b35b5b1a19a6faa2771c715a1e4ae1258cf'
    frozen=json.loads((PACKET/'frozen.json').read_text())
    def verify():
        for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
        for n,r in frozen['inputs'].items():assert sha(ROOT/n)==r['sha256']
    verify()
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    before=workspace_bytes(ROOT)
    own_reserve=1_000_000_000;other_reserve=20_000_000
    assert before+own_reserve+other_reserve<50_000_000_000
    plan=json.loads((PACKET/'equivalence-plan.json').read_text())
    command=list(plan['root_command'])
    command[command.index('--tag')+1]='root-reference-u-capture-b'
    command[command.index('--reference-reserve-bytes')+1]=str(own_reserve)
    command+=['--record-segments','--segment-frames','512','--keep-avi']
    OUT.mkdir()
    admission={'workspace_before':before,'own_reserve':own_reserve,'other_future_reserve':other_reserve,
               'cap':50_000_000_000,'command':command,'old_negative_unchanged':True}
    (OUT/'admission.json').write_text(json.dumps(admission,indent=2)+'\n')
    with (OUT/'driver.log').open('wb')as log:
        native=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    assert native.returncode==plan['expected_native_exit'],str(OUT/'driver.log')
    old=ROOT/plan['existing_negative_folder'];m=json.loads((NATIVE/'manifest.json').read_text())
    assert m['result']==plan['expected_result']and not m['verified_through_2_2']and not m['recording_verified']
    shared={}
    for n,pin in plan['CSV_literal_equality_required'].items():
        assert sha(old/n)==pin['sha256']and(old/n).read_bytes()==(NATIVE/n).read_bytes(),n
        shared[n]=sha(NATIVE/n)
    proof=NATIVE/'playthrough-lossless.verification/report.json'
    lossless=json.loads(proof.read_text());assert lossless['result']=='passed-exact-rgb-and-pcm'
    assert m['assemble_exit']==m['delivery_exit']==0 and m['native_parts_retained']
    assert 'recording_failure'not in m
    files=list(NATIVE.glob('*.avi'))+[NATIVE/n for n in ('native-audio.wav','playthrough-lossless.mkv','playthrough.mp4')]
    assert len(files)>=6 and all(p.exists()and p.stat().st_size>0 for p in files)
    verify()
    report={'status':'PASS_RETAINED_SEGMENTED_NATIVE_RGB_PCM_AND_DELIVERY_CALIBRATION',
            'script_sha256':sha(Path(__file__)),'native_exit':native.returncode,'result':m['result'],
            'all9CSV_literal':shared,'lossless_report_sha256':sha(proof),
            'delivery_report_sha256':sha(NATIVE/'playthrough.delivery.json'),
            'retained_files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)}for p in files},
            'workspace_after':workspace_bytes(ROOT),'goal_complete':False,'accepted_release':False,
            'qualification':'Original1483-frame death is preserved. No full route/roster/final video claim. Native AVI, continuous WAV, lossless MKV and MP4 are all retained.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json')}))

if __name__=='__main__':main()
