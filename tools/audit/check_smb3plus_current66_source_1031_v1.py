"""Rebind established SMB3 source and current66 foreign checks; no native."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
O=R/'build/smb3plus-current66-source-1031-v2';J=O/'joint'
C=R/'build/bowser-playable-jump-v1/joint'
import prepare_functional_roster_visuals58_v1 as B


def bind(out,paths):
    q=json.loads(out.read_text());q.setdefault('bindings',{})
    q['bindings'].update({str(p.resolve()):B.sha(p)for p in[Path(__file__),O/'source-stage.json',*paths]})
    B.write(out,json.dumps(q,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',choices=['regressions','menu','whole','foreign','vectors'],required=True)
    a=parser.parse_args()
    stage=json.loads(B.read(O/'source-stage.json'));B.bound(stage)
    assert stage['candidate']=='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
    if a.check=='regressions':
        import smb3plus_gravity_regressions_1031_v1 as M
        M.O=O;M.J=J;M.main()
        bind(O/'regressions-v1.json',[Path(M.__file__)])
    elif a.check=='menu':
        p=R/'tools/audit/smb3plus_menu_controls_1031_v1.py';s=p.read_text()
        s=s.replace("O=R/'build/smb3plus-menu-host-1031-v4';J=O/'joint'",f"O=R/{O.relative_to(R).as_posix()!r};J=O/'joint'")
        s=s.replace("P=R/'build/smb3plus-peach-float-host-1031-v4/joint'",f"P=R/{C.relative_to(R).as_posix()!r}")
        s=s.replace("stage['status_names'][variant]","['MARIO3 ','LUIGI3 ',' TOAD3 ',' PEACH3'][variant]")
        s=s.replace("stage['limits']","stage['limitations']")
        ns={'__file__':str(Path(__file__).resolve()),'__name__':'rebound_current66_menu'}
        exec(compile(s,str(p),'exec'),ns);ns['main']()
        bind(O/'menu-controls-v1.json',[p])
    elif a.check=='whole':
        p=R/'tools/audit/smb3plus_whole_controller_edges_1031_v1.py';s=p.read_text()
        s=s.replace('smb3plus-whole-controller-edges-1031-v1','smb3plus-current66-whole-controller-1031-v1')
        s=s.replace('smb3plus-peach-complete-controller-1031-v3','smb3plus-current66-source-1031-v2')
        # Same corrected four-quadrant native attribute ownership as frozen
        # root edges-v3, preserving the donor's separate float thresholds.
        s=s.replace('text=prior.read_text()',"text=prior.read_text().replace('for i in range(8):bus.ram','for i in range(4):bus.ram')")
        ns={'__file__':str(Path(__file__).resolve()),'__name__':'rebound_current66_whole_controller'}
        exec(compile(s,str(p),'exec'),ns);ns['main']()
        bind(R/'build/smb3plus-current66-whole-controller-1031-v1/probe.json',
             [p,R/'tools/audit/smb3plus_whole_controller_edges_1031_v3.py'])
    elif a.check=='foreign':
        import cf_bt_shared_foreign_main_v1 as M
        M.J=J;M.P=C;M.O=R/'build/smb3plus-current66-foreign-main-1031-v1';M.main()
        bind(M.O/'controls.json',[Path(M.__file__)])
    elif a.check=='vectors':
        p=R/'tools/audit/smb3plus_gravity_vectors_1031_v1.py';s=p.read_text()
        s=s.replace('smb3plus-peach-gravity-consumer-1031-v1','smb3plus-current66-source-1031-v2')
        ns={'__file__':str(Path(__file__).resolve()),'__name__':'rebound_current66_vectors'}
        exec(compile(s,str(p),'exec'),ns);ns['main']()
        bind(O/'vectors-v1.json',[p])


if __name__=='__main__':main()
