"""Palette-preserving successor; keeps the actual186 attribute negative."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
import check_prince_pose_reservation_1103_v186 as V

def main():
    negative=V.O/'pose-palette-negative-v186.json'
    if not negative.exists():
        negative.write_text(json.dumps(dict(passed=False,ROM_written=False,
            memory_SHA256='67d62f8c76813d2ad888eac4f0385458777ba0b69c5fbb5d7ac0ac9654913320',
            first_source_pose=[1,0],first_native_difference=dict(address=0x202,expected=0,actual=1),
            cause='Recompiling the earlier v37 renderer omitted the existing v42 sourcepalette1->nativepalette0 adaptation; five emitted attribute bytes were1 instead0. No assertion weakened; successor retains exact native0/40 operands.',
            source_authority='tools/audit/measure_prince_native_link_1102_v42.py:223'),indent=2)+'\n')
    V.main('pose-CPU-v187.json')
    path=V.O/'pose-CPU-v187.json';q=json.loads(path.read_text())
    q['retained_negative']='pose-palette-negative-v186.json'
    q['bindings'].update({p.relative_to(R).as_posix():V.M.sha(p) for p in
                         [Path(__file__),negative,R/'tools/audit/measure_prince_native_link_1102_v42.py']})
    path.write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':
    try:main()
    except Exception as error:
        p=V.O/'pose-negative-v187.json'
        if not p.exists():p.write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
