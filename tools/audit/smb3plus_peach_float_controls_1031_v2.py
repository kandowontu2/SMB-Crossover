"""Repeat unchanged original-instruction assertions on the form-gate repair."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import smb3plus_peach_float_controls_1031_v1 as P


def main():
    P.O=R/'build/smb3plus-peach-float-host-1031-v4';P.J=P.O/'joint'
    P.main()
    p=P.O/'float-controls-v1.json';d=json.loads(p.read_text())
    d['bindings'][str(Path(__file__))]=P.B.sha(__file__)
    negative=R/'build/smb3plus-peach-float-host-1031-v3/float-negative-v1.json'
    d['retained_negative']=str(negative)
    d['bindings'][str(negative)]=P.B.sha(negative)
    P.B.write(P.O/'float-controls-v2.json',json.dumps(d,indent=2)+'\n')


if __name__=='__main__':main()
