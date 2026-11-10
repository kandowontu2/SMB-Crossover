"""Final-minus ordinary frames, exact sine tails, and bbox restoration for70aa."""
from hashlib import sha256
import json
from pathlib import Path

import check_manual_roster_ff_foot_1110 as F
import check_manual_wide_horizontal_qualification_1110 as Q

I,P,N,W,R=F.I,F.P,F.N,F.W,F.R
PROOF=I.OUT/'ff-foot-proof.json'
SHA=lambda p:sha256(Path(p).read_bytes()).hexdigest()


def boxes(b):
    seed=F.Motion.scene(b,22,0)
    F.Carry.horizontal(seed,22)
    [(slot,_)]=W.D.owned(seed,0x28)
    count=0
    for bottom in range(256):
        m=P.slim_fork(seed);m[0x65b]=bottom
        before=bytes(m[0x658:0x65c])
        N.put(m,ObjectOffset=slot)
        N.invoke(m,'HpNativePlatformDispatch',x=slot)
        assert bytes(m[0x658:0x65c])==before,(bottom,before,bytes(m[0x658:0x65c]))
        count+=1
    return dict(cases=count,whole_ordinary_bbox_restored=True,bottom_domain=[0,255],
        fixture='Actual controller-boarded nativeH platform before each isolated boundary value.')


def frontend(b):
    original=N.NesMPU;calls=[0]
    pc=int(b['syms']['ManualRosterInput']['val'])
    class Trace(original):
        def step(self):
            if self.pc==pc and self.memory.rawtags[1]==154:calls[0]+=1
            return original.step(self)
    N.NesMPU=Trace
    try:
        for owner in (22,29):
            m=F.Motion.scene(b,owner,0)
            N.put(m,OperMode=0,OperMode_Task=3,CrossoverMenuState=2,
                CrossoverMenuIndex=owner-1,CrossoverTitleDrawn=1,
                SavedJoypad1Bits=0x28,SavedJoypad2Bits=0,NmiDisable=255)
            m[0x73d1]=128;m[0x73d2]=m[0x73d3]=0
            start=calls[0]
            N.invoke(m,'GameLoop')
            assert calls[0]==start and not W.D.owned(m)
        return dict(actual_title_GameLoop_cases=2,manual_ingress_calls=0,
            stale_engine8_and_UpSelect_rejected_by_real_frontend=True)
    finally:N.NesMPU=original


def main():
    q=json.loads(PROOF.read_text())
    for name,digest in q['bindings'].items():assert SHA(R/name)==digest,name
    raw=I.BASE.read_bytes();assert I.SHA(raw)==q['parent_SHA256']==I.PIN
    new=P.install(raw,q['patches']);assert I.SHA(new)==q['expected_memory_only_SHA256']
    b=F.bundle(new,q['labels']);before=I.bundle(raw,q['labels'])
    values,_,reader,_=W.table(W.BASE.read_bytes())
    sine={}
    for name,table,pc in (('H',values,reader),('V',bytes(raw[P.at(26,q['layout']['vertical']):P.at(26,q['layout']['vertical'])+256]),q['layout']['vertical_reader'])):
        sine[name]=Q.sine(before,b,dict(format=dict(reader_pc=pc,table_values=table.hex())))
        print('Exact complete native sine tail',name,sine[name],flush=True)
    exact_boxes=boxes(b);print('bbox restoration',exact_boxes,flush=True)
    title=frontend(b);print('actual frontend',title,flush=True)
    inputs=I.input_cases(b);print('all variants/both pads',len(inputs),flush=True)
    parity=I.regular(raw,new,q['labels'])
    frames=I.actual_frames(b,new)
    result=dict(passed=True,source_CPU_only=True,Mesen_run=False,ROM_written=False,
        expected_memory_only_SHA256=q['expected_memory_only_SHA256'],ff_foot_proof_SHA256=SHA(PROOF),
        sine=sine,bbox=exact_boxes,frontend=title,inputs=inputs,regular=parity,actual_GameCore=frames,
        scope='Exact old74fde versus70aa ordinary GameCore publicstate/AXYP, only3declared manual bytes normalized for22/29; complete native signed sine tails; all ordinarybbox bytes restored.',
        bindings={p.relative_to(R).as_posix():SHA(p) for p in (Path(__file__),PROOF,Path(F.__file__),Path(Q.__file__))})
    (I.OUT/'ff-foot-qualification.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
