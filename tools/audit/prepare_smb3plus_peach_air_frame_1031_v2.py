"""Use the existing native alias of donor06B6; retain the failed v1 build."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_smb3plus_peach_air_frame_1031_v1 as P


def main():
    source=R/'tools/reference/smb3plus_peach_air_frame_1031_v2.s'
    text=P.S.read_text().replace('M3Native::Player_Microgoomba',
        'M3Native::Player_UphillSpeedIdx ; source alias of06B6')
    assert not source.exists();P.B.write(source,text)
    negative=R/'build/smb3plus-peach-air-frame-1031-v1/main-build.json'
    assert json.loads(P.B.read(negative))['returncode']!=0
    P.S=source;P.O=R/'build/smb3plus-peach-air-frame-1031-v2';P.J=P.O/'joint'
    P.main()
    receipt=P.O/'source-stage.json';d=json.loads(P.B.read(receipt))
    d['retained_negative']=str(negative)
    d['bindings'].update({str(p):P.B.sha(p) for p in [Path(__file__),negative]})
    P.B.write(receipt,json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
