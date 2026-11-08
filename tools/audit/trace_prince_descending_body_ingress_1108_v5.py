"""Bind the current Easy reader chain and a narrow unimplemented latch plan."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import measure_prince_easy_stomp_seam_1108_v3 as E
import trace_prince_descending_floor_1108_v4 as T
Q=E.Q


def main():
    src=inspect.getsource(E.main);needle='    class Trace(native):'
    assert src.count(needle)==1
    src=src.replace(needle,'''    for label in ['GuestBodyContactBridge','KbBodyDispatch','GuestBodyContact','GuestSourceStompPolicy','LmBodyGate','X5EasyBodyContact']:
        points[((I.location(base,label)-16)//8192|128,addr(label))]=label
'''+needle)
    src=src.replace("O/'easy-contact-seam.json'","O/'descending-body-ingress.json'")
    src=src.replace("O/'landing-contract.json'","Q.O/'landing-contract.json'")
    src=src.replace("    print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))",'')
    env=dict(E.__dict__,O=T.O,__file__=str(Path(__file__)))
    exec(compile(src,str(Path(__file__)),'exec'),env);env['main']()
    p=T.O/'descending-body-ingress.json';q=json.loads(p.read_text())
    names=['GuestBodyContactBridge','KbBodyDispatch','GuestBodyContact','GuestSourceStompPolicy']
    for case in q['cases']:
        events=case['events'];order=[event['name'] for event in events if event['name'] in names]
        assert order==names,(case['case'],order)
        assert not any(event['name'] in ['LmBodyGate','X5EasyBodyContact'] for event in events)
    q['conclusion']='Actual raw38 body ingress is fixed ED B1 -> bank74 BF03/ABDC -> bank10 B5A1 and GuestSourceStompPolicy; no LmBodyGate or X5EasyBodyContact. Stock Easy positive DY stomps; native DY0 uses original injury tag15. Source tag81 on success is an unhandled no-op.'
    q['latch_plan']={
        'writer':'At authenticated Prince vertical export, before native BG floor, compare exact C084 physical sole vs C086 old sole. Only fresh source Advance output C0A6&3==1, raw38/engine8/Easy/land/same valid screen high and strictly positive bounded delta. Hold-phase repeated positive DY is NOT fresh descent.',
        'reader':'Before stock stomp/injury decision in actual bank10 body policy, only after true native rectangle overlap, exact raw38/engine8/Easy/land, DY=0 and State=0 from floor snap, native enemy 0..3 or6 in ordinary state0/1, same valid screen high. Require old sole<=actual enemy top<=current sole using actual enemy bounding box; latch may encode prior sole because player bottom already published from source. Then supply positive native DY1 to existing stock resolver, keeping source damage unchanged for other cases.',
        'lifetime':'Clear on each GameCore and no new legal source advance; consume once on success. Existing X5FootDescending at7FFE is reset in X5EasyFootBox; reuse requires explicitly bound raw38 writer/reset/consumer lifetime, or a new documented owner grant. Stale latch across phase, pause, scene/death or IRQ is not admitted.',
        'bounce':'Existing tag81 returns CLC without updating source. Native recoil alone is overwritten by subsequent original vertical export; a donor-script bounce or explicit scoped adapter requires source semantics and actual post-stomp motion proof. Do not force Mario jump or script state based on native velocity alone.',
        'status':'Source plan only; no executable spans granted and no integration bytes proposed.'}
    q['bindings'].update({file.relative_to(R).as_posix():Q.M.sha(file) for file in [Path(E.__file__),Path(T.__file__),T.O/'descending-floor-trace.json',R/'src/guest_body_contact.s',R/'src/guest_source_stomp.s']})
    p.write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(q['cases']),actual_order=names,unused=['LmBodyGate','X5EasyBodyContact'],scope=q['latch_plan']['status'])))


if __name__=='__main__':main()
