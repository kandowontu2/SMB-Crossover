"""Same interception controls: capped real-actor/caller trace, no state writes."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_battletoads_food_intercept_6a3_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

def run(raw):
    family=F.family();N,W=F.N,F.W;b=F.Current.bundle(raw);frames=Runner.Frames.frame;base=N.NesMPU
    rows=[];calls=[];last=None;opening=[]
    def state(m):
        def r(n,i=0):return N.get(m,n,i)
        return dict(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),power=r('PlayerStatus'),
            sourceHP=m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191],
            actor=dict(flag=r('Enemy_Flag',5),kind=r('PowerUpType',5),state=r('Enemy_State',5),
                x=r('Enemy_X_Position',5)+256*r('Enemy_PageLoc',5),y=r('Enemy_Y_Position',5),
                vx=r('Enemy_X_Speed',5),moving=r('Enemy_MovingDir',5)),
            player_box=[r('BoundingBox_UL_Corner',i)for i in range(4)],
            item_box=[r('EnemyBoundingBoxCoord',20+i)for i in range(4)])
    watched={W.address(b,n):n for n in('HandlePowerUpCollision','EraseEnemyObject')}
    class CPU(base):
        def step(self):
            m=self.memory
            if self.pc in watched and self.x==5 and N.get(m,'Enemy_ID',5)==46 and N.get(m,'Enemy_Flag',5)==1:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                if tag&128:
                    q=state(m);q.update(PC=self.pc,SP=self.sp,physical_PRG=tag&127,callee=watched[self.pc],
                        returnPC=m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)
                    if len(calls)<8:calls.append(q)
            return super().step()
    def frame(m,*args,**kwargs):
        nonlocal last
        out=frames(m,*args,**kwargs)
        if kwargs.get('whole_pass')and N.get(m,'Enemy_ID',5)==46:
            q=state(m);a=q['actor'];key=(a['flag'],a['state'],a['x']//16,a['y']//16,q['x']//16)
            if a['state']>=128 and key!=last:
                last=key;rows.append(q)
                if len(rows)>20:del rows[6]
        return out
    def cold(image,key):
        m,q=F.Current.cold(image,key,True);opening.append(q);return m
    def deny(*args,**kw):raise AssertionError('Causal trace attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),\
        patch.object(Runner,'Factory',family),patch.object(Runner,'strict_metadata',family.metadata),patch.object(Runner,'cold',cold),\
        patch.object(N,'NesMPU',CPU),patch.object(Runner.Frames,'frame',frame):q=Model.run(raw,'rash',850)
    result=dict(passed=True,scope='Readonly same-controls diagnosis; original collection gate remains negative',
        underlying_passed=q['passed'],underlying_receipt_SHA256=q['source_receipt_SHA256'],reason=q['receipt']['reason'],
        terminal=q['receipt']['terminal'],controller_SHA256=q['metadata']['controller_SHA256'],actual_cold_readback=opening,
        real_actor_trajectory=rows,actual_collect_or_erase_callers=calls,outputs=0,gameplay_seeds=0)
    result['source_receipt_SHA256']=F.Current.digest(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    return result

if __name__=='__main__':print('RESULT '+json.dumps(run(F.ROM.read_bytes()),separators=(',',':')),flush=True)
