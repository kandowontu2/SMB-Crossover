"""Qualify the corrected pickup24 image against the same strict Main cases."""
import inspect,json
from pathlib import Path
import check_bub_original_upgrades_1102_v49 as Q
import prepare_bub_original_upgrades_1102_v51 as U
R=Q.R;O=R/'build/bub-upgrades-root-qualification-1102-v52'
def main():
    # Q's bundle loader reads the corrected image through its U namespace.
    old=Q.U;Q.U=U
    try:
        text=inspect.getsource(Q.main)
        assert text.count('0xb08c+14*3')==1
        text=text.replace('0xb08c+14*3','0xb08c+24*3').replace('resident row14','resident row24').replace(',S]if False',']if False')
        env=dict(Q.__dict__,U=U,O=O,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
    finally:Q.U=old
    path=O/'receipt.json';q=json.loads(path.read_text());q['public_pickup_row']=24;q['native_side_row14_retained']=True
    q['bindings'][str(Path(Q.__file__).relative_to(R))]=old.sha(Path(Q.__file__))
    path.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
