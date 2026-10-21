"""Root strict native-handler model replays for four separately admitted captures."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/agent49o2-sophia-interrupt-replay-h4'
OUT=ROOT/'build/verification/root49o2-sophia-interrupt-h4-replays-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(PACKET/'frozen.json')=='e9db1f60fb7e9e70e97e8135e4001a73d30dc746581180f20ec876364fed6ae9'
    OUT.mkdir();report=dict(status='RUNNING_STRICT_ACTUAL_H4_REPLAYS',script_sha256=sha(Path(__file__)),
                            accepted_release=False,goal_complete=False,cases=[])
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper,binding_sha in [('mmc3','4184ac25201b0b3d3e42299a09d1d43c28ce9a20ba0168473ccd00578c7d6a32'),
                               ('mmc5','4adcc4dd4fea86b06e7f8e0115c5c2b541f21fbe94177531d514b23b800427af')]:
        for side in ('before','after'):
            folder=ROOT/'build/verification'/f'root49o2-sophia-interrupt-i-{mapper}-{side}-a'
            review=ROOT/'build/verification'/f'root49o2-sophia-interrupt-j-{mapper}-{side}-review-a.json'
            native=json.loads(review.read_text());assert native['status']=='PASS_NATIVE_I_RAM_BUS_NEUTRALITY_NO_CLOSURE_PROMOTION'
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
    report.update(status='COMPLETE_H4_ACTUAL_HANDLER_REPLAYS_ALL_OUTCOMES_RETAINED',
                  qualification='Actual admitted complete native handlers only; precise DECabs accounting and exact attributed DMA transactions. No injected or universal/coherent helper-boundary proof or release acceptance.')
    save();print(json.dumps(dict(status=report['status'],report_sha256=sha(OUT/'report.json'),exits=[(c['mapper'],c['side'],c['exit'])for c in report['cases']])))

if __name__=='__main__':main()
