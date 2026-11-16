"""Filtered actual gate trace reaches the final private leaf, unchanged controls."""
from pathlib import Path
import inspect,json
import check_battletoads_food_admission_6a3_1116 as Previous

def run(raw):
    source=inspect.getsource(Previous.run)
    old="if tracing and len(path)<120:path.append(dict(tag=tag,PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,bytes=bytes(m[self.pc:self.pc+4]).hex()))"
    new="if tracing and len(path)<120 and(tag==3 or(self.pc>=0x8000 and m[self.pc]in(0x20,0x4c,0x60,0x6c))):path.append(dict(tag=tag,PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,bytes=bytes(m[self.pc+i]for i in range(4)).hex()))"
    assert source.count(old)==1;source=source.replace(old,new,1)
    namespace=dict(Previous.__dict__);exec(compile(source,str(Path(__file__))+':filtered-readonly-path','exec'),namespace)
    return namespace['run'](raw)

if __name__=='__main__':print('RESULT '+json.dumps(run(Previous.Previous.F.ROM.read_bytes()),separators=(',',':')),flush=True)
