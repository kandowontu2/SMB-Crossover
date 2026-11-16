"""Same ordinary controls: actual mature-admission carry and bounded CPU path."""
from pathlib import Path
import inspect,json
import check_battletoads_food_causal_6a3_1116 as Previous

PARENT_SHA=''

def run(raw):
    source=inspect.getsource(Previous.run)
    def once(old,new):
        nonlocal source
        assert source.count(old)==1,old;source=source.replace(old,new,1)
    first=source.index('    watched=');last=source.index('    def frame(',first)
    source=source[:first]+'''    watched={};descriptors=[];returns=[];counts={};path=[];tracing={}
    for name in('PowerUpObjHandler','NrPickupCollision','JnCollisionDispatch','M3PickupCollision','RemainingNormalPlayerCollision','PlayerEnemyCollision','PlayerCollisionCore','HandlePowerUpCollision','NrPickup','BtPickup'):
        if name not in b['syms']:continue
        pc=W.address(b,name)
        if name.startswith('Bt'):tag=3;at=F.Current.CACHE+(pc&8191)
        else:at=W.location(b,name);tag=((at-16)//8192)|128
        watched[tag,pc]=name;descriptors.append(dict(name=name,PC=pc,tag=tag,file=at,bytes=raw[at:at+12].hex()))
    class CPU(base):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            for q in returns[:]:
                if(self.pc,self.sp)==(q['returnPC'],q['returnSP']):
                    returns.remove(q);q.update(returnA=self.a,returnX=self.x,returnY=self.y,returnP=self.p,returnCarry=self.p&1,return_tag=tag)
                    if tracing.get('q')is q:tracing.clear()
            if tracing and len(path)<120:path.append(dict(tag=tag,PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,bytes=bytes(m[self.pc:self.pc+4]).hex()))
            name=watched.get((tag,self.pc))
            if name and self.x==5 and N.get(m,'Enemy_ID',5)==46 and N.get(m,'Enemy_Flag',5)==1 and N.get(m,'Enemy_State',5)>=128:
                counts[name]=counts.get(name,0)+1;q=state(m);pb,ib=q['player_box'],q['item_box']
                width=min(pb[2],ib[2])-max(pb[0],ib[0])+1;height=min(pb[3],ib[3])-max(pb[1],ib[1])+1
                if width>0 and height>0 and len(calls)<24:
                    q.update(name=name,PC=self.pc,SP=self.sp,tag=tag,A=self.a,X=self.x,Y=self.y,P=self.p,overlap=[width,height],
                        returnPC=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535,returnSP=(self.sp+2)&255)
                    calls.append(q);returns.append(q)
                    if name=='NrPickupCollision'and not path:tracing['q']=q
            return super().step()
''' +source[last:]
    once("    result['source_receipt_SHA256']=", "    result.update(actual_call_descriptors=descriptors,mature_call_counts=counts,first_positive_NrPickupCollision_path=path)\n    result['source_receipt_SHA256']=")
    namespace=dict(Previous.__dict__);exec(compile(source,str(Path(__file__))+':readonly-carry-observer','exec'),namespace)
    return namespace['run'](raw)

if __name__=='__main__':
    q=run(Previous.F.ROM.read_bytes());print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
