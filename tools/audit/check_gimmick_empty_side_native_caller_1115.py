"""Declared real native side-loop marker/solid fixtures; memory only."""
from hashlib import sha256
import json
import compose_gimmick_empty_side_1115 as C
import check_gimmick_empty_side_components_1115 as Parts
N,W=Parts.N,Parts.W


if __name__=='__main__':
    parent,boundary=C.load590();candidate,info=C.proposal(parent);rows=[]
    for tile in(0,35,81,97,96):
        pair=[]
        for raw,new in((parent,False),(candidate,True)):
            m=Parts.seed(Parts.bundle(raw,new));base=W.address(m.bundle,'Block_Buffer_1')
            for i in range(416):m[base+i]=0
            m[base+125]=tile
            N.put(m,Local_eb=0,Player_CollisionBits=255,SideCollisionTimer=0,GuestHurtTicks=0,PlayerFacingDir=2)
            z=N.invoke(m,'DoPlayerSideCheck',a=93,x=77,y=0,p=0x31)
            pair.append(dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),vx=N.get(m,'Player_X_Speed'),
                side_timer=N.get(m,'SideCollisionTimer'),marker=m[base+125],CPU=z['CPU'],returned=Parts.regs(z)))
        if tile==35:assert pair[0]['x']==1247 and pair[1]['x']==1231 and pair[1]['marker']==35,pair
        else:assert {k:v for k,v in pair[0].items()if k!='CPU'}=={k:v for k,v in pair[1].items()if k!='CPU'},(tile,pair)
        rows.append(dict(tile=tile,parent=pair[0],proposal=pair[1]))
    q=dict(passed=True,rows=rows,candidate_SHA256=info['candidate_SHA256'],scope='Declared tile/anchor native-side-loop fixtures; not ordinary gameplay',input_binding=boundary,outputs=0,Mesen_run=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
