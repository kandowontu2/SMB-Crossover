"""Root strict native-handler model replays for four separately admitted captures."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/agent49o2-sophia-interrupt-replay-h5'
OUT=ROOT/'build/verification/root49o2-sophia-interrupt-h5-replays-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(PACKET/'frozen.json')=='795d8fdc7581b648466e95c7013a15f1b80939dcf5f031495e2767eb0425d456'
    OUT.mkdir();report=dict(status='RUNNING_STRICT_ACTUAL_H5_REPLAYS',script_sha256=sha(Path(__file__)),
                            accepted_release=False,goal_complete=False,cases=[])
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper,binding_sha in [('mmc5','4adcc4dd4fea86b06e7f8e0115c5c2b541f21fbe94177531d514b23b800427af')]:
        for side in ('before','after'):
            folder=ROOT/'build/verification'/f'root49o2-sophia-interrupt-l-{mapper}-{side}-a'
            review=ROOT/'build/verification'/f'root49o2-sophia-interrupt-l-{mapper}-{side}-review-a.json'
            native=json.loads(review.read_text());assert native['status']=='PASS_NATIVE_L_RAM_BUS_NEUTRALITY_LAG_MODE_NO_CLOSURE_PROMOTION'
            assert native['case']['mapper']==mapper and native['case']['side']==side
            result=OUT/f'{mapper}-{side}.json'
            command=['C:/Users/kando/AppData/Local/Programs/Python/Python314/python.exe',str(PACKET/'verify.py'),
                     '--folder',str(folder),'--native-review',str(review),'--native-review-sha256',sha(review),
                     '--binding',str(ROOT/'build/verification/agent49o2-sophia-friction-checker-e'/f'binding-{mapper}.json'),
                     '--binding-sha256',binding_sha,'--suite','replay','--seconds','600','--out',str(result)]
            c=dict(mapper=mapper,side=side,command=command,native_review_sha256=sha(review));report['cases'].append(c);save()
            log=OUT/f'{mapper}-{side}.log'
            with log.open('wb')as stream:p=subprocess.run(command,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
            c.update(exit=p.returncode,log_sha256=sha(log))
            if result.exists():c.update(result=json.loads(result.read_text()),result_sha256=sha(result))
            save()
    report.update(status='COMPLETE_H5_ACTUAL_HANDLER_REPLAYS_ALL_OUTCOMES_RETAINED',
                  qualification='Actual admitted complete native handlers only; precise DECabs accounting and exact attributed DMA transactions. No injected or universal/coherent helper-boundary proof or release acceptance.')
    save();print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'),exits=[(c['mapper'],c['side'],c['exit'])for c in report['cases']])))

if __name__=='__main__':main()
