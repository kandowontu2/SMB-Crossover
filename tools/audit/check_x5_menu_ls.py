"""Check menu reachability for every subset of the seven future third-row slots."""
from pathlib import Path
import importlib.util
import json

R=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('x5menu',R/'tools/reference/build_x5_menu.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def main():
    cases=edges=0
    for mask in range(128):
        slots=list(range(12))+[12+i for i in range(7) if mask&(1<<i)]
        nav=m.navigation(slots)
        reached={0};todo=[0]
        while todo:
            s=todo.pop()
            for direction,target in nav[s].items():
                assert target in slots,'Disabled profiles cannot be navigation targets'
                if direction in ('left','right'):
                    inverse='right' if direction=='left' else 'left'
                    assert nav[target][inverse]==s,'Horizontal row wrap must be reversible'
                if target not in reached:reached.add(target);todo.append(target)
                edges+=1
        assert reached==set(slots),'Every ready portrait is reachable from Mario'
        cases+=1
    full=m.navigation(list(range(19)))
    # Independent layout examples: 6/6/7 is deliberately not a modulo+6 grid.
    assert full[5]['right']==0 and full[0]['left']==5
    assert full[11]['right']==6 and full[6]['left']==11
    assert full[18]['right']==12 and full[12]['left']==18
    assert full[0]['down']==6 and full[6]['down']==12 and full[12]['down']==0
    assert full[5]['down']==11 and full[11]['down']==18 and full[18]['down']==5
    assert full[0]['up']==12 and full[18]['up']==11
    out=R/'build/verification/third-row-lp/menu-navigation.json'
    report=dict(passed=True,ready_subsets=cases,traversed_edges=edges,
                full_grid=full,scope='Menu graph only. Unimplemented characters remain disabled.')
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=True,ready_subsets=cases,traversed_edges=edges)))


if __name__=='__main__':main()
