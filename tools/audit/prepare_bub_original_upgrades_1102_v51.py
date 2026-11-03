"""Correct the private pickup vector; preserve the v48 side-vector negative."""
import inspect,json
from pathlib import Path
import prepare_bub_original_upgrades_1102_v48 as U
R=U.R;O=R/'build/bub-upgrades-root-1102-v51';PIN=U.PIN;labels=U.labels
def main():
    text=inspect.getsource(U.main)
    old='image[14*3:14*3+3]';assert text.count(old)==1
    text=text.replace(old,'image[24*3:24*3+3]')
    env=dict(U.__dict__,O=O,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
    path=O/'proposal.json';q=json.loads(path.read_text());q['public_pickup_row']=24
    q['native_side_row14_retained']=True
    q['retained_negative']='v48 incorrectly bound native side14 to pickup; v49 actualMain caught15px displacement before any ROM emission; v50 source trace972instructions exactly equal. Correct pickup is tag72/3=24 in actual public router.'
    q['bindings'][str(Path(U.__file__).relative_to(R))]=U.sha(Path(U.__file__))
    path.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
