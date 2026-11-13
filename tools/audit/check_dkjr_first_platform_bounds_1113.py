"""Declared native center parameter fixture; never a natural-route claim."""
from contextlib import redirect_stdout
import argparse
from hashlib import sha256
import io
import json

import check_dkjr_platform_contact_1113 as Q

P,H,N,W,L,T,C=Q.P,Q.H,Q.N,Q.W,Q.L,Q.T,Q.C


def motion(seed):
    rows=[];C.SLOT=3
    for center in(128,*range(180,201)):
        m=C.setup(seed)
        C.field(m,'Enemy_Y_Position',192)
        N.invoke(m,'InitEnemyObject',x=C.SLOT)
        C.field(m,'YPlatformCenterYPos',center)
        C.field(m,'PlatformCollisionFlag',255)
        points=[]
        for age in range(1024):
            N.put(m,FrameCounter=age&255,ObjectOffset=C.SLOT)
            N.invoke(m,'YMovingPlatform',x=C.SLOT)
            points.append(N.get(m,'Enemy_Y_Position',C.SLOT))
        rows.append(dict(center=center,initial_top=192,minimum=min(points),maximum=max(points),
            first512_bounds=[min(points[:512]),max(points[:512])],
            first750_bounds=[min(points[:750]),max(points[:750])],
            path_SHA256=sha256(bytes(points)).hexdigest()))
    return rows


def head(seed,candidate,center):
    m=Q.mounted(seed,candidate);writes=[]
    text=T.controller(candidate)
    text=P.once(text,"r('Enemy_Y_Position',p)<=180","r('Enemy_Y_Position',p)<=192")
    def observe(memory,cpu):
        if cpu.pc!=0xbd3d or memory.rawtags[1]!=3:return
        slot=cpu.x
        if slot>5 or N.get(memory,'Enemy_ID',slot)!=37:return
        x=N.get(memory,'Enemy_X_Position',slot)+256*N.get(memory,'Enemy_PageLoc',slot)
        if x!=336:return
        assert not writes and N.get(memory,'Enemy_Y_Position',slot)==192
        at=W.address(memory.bundle,'YPlatformCenterYPos')+slot
        writes.append(dict(PC=cpu.pc,slot=slot,address=at,old=memory[at],new=center))
        memory[at]=center
    with redirect_stdout(io.StringIO()):result=P.B.route(m,candidate,2000,
        controller_text=text,observe_extra=observe)
    assert len(writes)==1
    receipt=result['receipt']
    return dict(center=center,fixture_native_parameter_writes=writes,
        controller_SHA256=sha256(text.encode()).hexdigest(),passed=result['passed'],
        logical_updates=result['logical_updates'],final=result['final'],
        reason=receipt['reason'],head_effects=receipt['head_effects'],
        helper_births=receipt['helper_births'],item_birth=receipt.get('item_birth'),
        mature=receipt.get('mature'),pickup_return=receipt.get('pickup_return'),
        followup_updates=receipt.get('followup_updates'),best_head=receipt.get('best_head'))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--motion-only',action='store_true');args=ap.parse_args()
    parent=T.load_parent()
    candidate,_=T.transform(parent)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    print('DKJR_FIRST_NATIVE_BOUNDS '+json.dumps(dict(candidate_SHA256=T.PIN,rows=motion(seed)),separators=(',',':')),flush=True)
    for center in(()if args.motion_only else(192,)):
        print('DKJR_FIRST_CENTER_HEAD '+json.dumps(head(seed,candidate,center),separators=(',',':')),flush=True)
    print('DKJR_FIRST_CENTER_SCOPE '+json.dumps(dict(ROM_written=False,outputs_written=0,
        source_or_powerup_state_writes=False,
        scope='Original native ID25 motion and genuine authored head/item procedures, with one explicitly declared constructor center-parameter write and bump threshold controls. Not an unmodified/controller-only or Mesen proof.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
