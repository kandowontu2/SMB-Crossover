"""Root execution and literal-stream review of the passive fixed Bill T replay."""
from pathlib import Path
import hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/agent49n-bill-castle-contact-observer-t'
OUT=ROOT/'build/verification/root49n-bill-castle-t-native-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(PACKET/'freeze.json')=='4fa3bf80dc4feb8da99cb306722b9fa681c6bafbe73462e578096a9bc0af9004'
    OUT.mkdir()
    with (OUT/'preflight.log').open('wb') as log:
        p=subprocess.run([sys.executable,str(PACKET/'preflight.py'),'--space','--other-reserve-bytes','170000000'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    assert p.returncode==0, str(OUT/'preflight.log')
    plan=json.loads((PACKET/'preparation.json').read_text())
    command=plan['root_command']
    command[0]=sys.executable
    report=dict(status='RUNNING_FIXED_PASSIVE_T',command=command,script_sha256=sha(Path(__file__)),
                packet_freeze_sha256=sha(PACKET/'freeze.json'),accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with (OUT/'native.log').open('wb') as log:
        p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    report.update(native_exit=p.returncode,native_log_sha256=sha(OUT/'native.log'));save()
    assert p.returncode==plan['expected_native_exit'],str(OUT/'native.log')
    review=OUT/'contact-review.json'
    with (OUT/'review.log').open('wb') as log:
        p=subprocess.run([sys.executable,str(PACKET/'check.py'),'--native-exit',str(p.returncode),'--out',str(review)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    report.update(review_exit=p.returncode,review_log_sha256=sha(OUT/'review.log'))
    if review.exists():report.update(review=json.loads(review.read_text()),review_sha256=sha(review))
    report.update(status='COMPLETE_FIXED_PASSIVE_T_NEGATIVE_RETAINED',
                  qualification='Private N ordinary fixed death replay with passive ownership observation; no clear, source-perfect collision or current P route claim.')
    save()
    print(json.dumps(dict(status=report['status'],native_exit=report['native_exit'],review_exit=p.returncode,report_sha256=sha(OUT/'report.json'))))
    assert p.returncode==0,str(OUT/'review.log')

if __name__=='__main__':main()
