"""Final unchanged224 original-controller cases and2016 boundary cases."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import smb3plus_whole_controller_probe_1031_v2 as P


def main():
    P.O=R/'build/smb3plus-gravity-source-controls-1031-v1'
    P.J=R/'build/smb3plus-peach-gravity-consumer-1031-v1/joint';P.main()
    result=P.O/'probe.json';d=json.loads(result.read_text());assert d['passed']
    edge=R/'build/smb3plus-whole-controller-edges-1031-v3/probe.json'
    e=json.loads(edge.read_text());P.K.B.bound(e)
    assert e['passed'] and e['candidate']==d['candidate'] and len(e['cases'])==2016
    d['bindings'].update({str(p):P.K.B.sha(p) for p in [Path(__file__),edge]})
    d['additional_complete_controller_edges']=2016
    d['edge_fixture_correction']='Preserve actual native float thresholds7E98..9B; only copy the four original controller Tile_AttrTable quadrants at7E94..97. Earlier eight-byte copy overwrote an independent donor extension table. All2016 actual player/pad/sound/float fields now match, including Y2,176,255.'
    P.K.B.write(result,json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ordinary_cases=224,edge_cases=2016,candidate=d['candidate'])))


if __name__=='__main__':main()
