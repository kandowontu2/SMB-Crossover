"""Read-only actual second-gap native/source contact trace; no file output."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json

import replay_dkjr_descending_platform_1113 as R

T,Q,P,H=R.T,R.Q,R.P,R.H


def main():
    parent,candidate=T.load_inputs(reuse_private=True)
    _,seed=H.cold(parent,parent[P.B.COOKIE_AT:P.B.COOKIE_AT+16]);m=Q.mounted(seed,candidate)
    text=R.controller(candidate,descending_roof=(2,3),observe_prior=True,early_ledge=True)
    ticks=0;rows=[]
    points={(128,0xb98a):'dispatch',(128,0xb453):'LPC',
        (254,0x9a2c):'native-proc',(199,0xac18):'position-Y-store',
        (199,0xac29):'position-return',(3,0xb6a5):'source-carry',
        (3,0xa966):'source-land'}
    def after(m):
        nonlocal ticks
        ticks+=1
    def watch(m,c):
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        event=points.get((tag,c.pc));x=Q.N.get(m,'Player_X_Position')+256*Q.N.get(m,'Player_PageLoc')
        if not event or not 1360<=x<1424:return
        slots=[i for i in range(6)if Q.N.get(m,'Enemy_Flag',i)==1 and Q.N.get(m,'Enemy_ID',i)==40]
        if not slots:return
        slot=slots[0]
        row=dict(Main=ticks,event=event,pc=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,
            player_x=x,player_y=Q.N.get(m,'Player_Y_Position'),player_dy=Q.N.get(m,'Player_Y_Speed'),
            source_y=m.ram[2][0x210],source_current=m.ram[2][0x6b],source_prior=m.ram[2][0x6c],
            player_box=list(m[0x658:0x65c]),slot=slot,
            actor_x=Q.N.get(m,'Enemy_X_Position',slot)+256*Q.N.get(m,'Enemy_PageLoc',slot),
            actor_y=Q.N.get(m,'Enemy_Y_Position',slot),actor_box=list(m[0x65c+4*slot:0x660+4*slot]),
            flag=Q.N.get(m,'PlatformCollisionFlag',slot),body_control=Q.N.get(m,'Player_BoundBoxCtrl'))
        if len(rows)>=48:del rows[8]
        rows.append(row)
    with redirect_stdout(io.StringIO()):
        result=P.B.route(m,candidate,4500,controller_text=text,observe_extra=watch,after_frame=after)
    print('DKJR_HORIZONTAL_CONTACT_TRACE '+json.dumps(dict(candidate_SHA256=T.PIN,
        Lua_SHA256=sha256(text.encode()).hexdigest(),passed=result['passed'],
        logical_updates=result['logical_updates'],final=result['final'],
        reason=result['receipt'].get('reason'),trace=rows,
        receipt_SHA256=sha256(json.dumps(result['receipt'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        source_or_native_writes=False,outputs_written=0,physical_cadence_claim=False),separators=(',',':')),flush=True)


if __name__=='__main__':main()
