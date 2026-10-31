"""Repeat unchanged complete donor assertions on the genuine consumer fixes."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import smb3plus_whole_controller_probe_1031_v2 as P


def main():
    P.O=R/'build/smb3plus-whole-controller-probe-1031-v3'
    P.J=R/'build/smb3plus-peach-complete-controller-1031-v3/joint'
    P.main()
    out=P.O/'probe.json';d=json.loads(out.read_text())
    d['bindings'][str(Path(__file__))]=P.K.B.sha(__file__)
    P.K.B.write(out,json.dumps(d,indent=2)+'\n')
    assert d['passed'],[(r['character'],r['form'],r['differences']) for r in d['cases'] if r['differences']]


if __name__=='__main__':main()
