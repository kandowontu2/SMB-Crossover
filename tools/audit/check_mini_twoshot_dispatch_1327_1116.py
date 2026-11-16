"""Unchanged two-shot controls: actual current dispatch PC/tag diagnostic."""
from pathlib import Path
from unittest.mock import patch
import json
import replay_mini_flower_twoshot_1327_1116 as F
import check_smb1_alts_full11_1114 as Runner
import wwf_stock_source_model_1115 as Model

if __name__=='__main__':
    raw=F.ROM.read_bytes();opening=[];trace={};base=F.N.NesMPU
    assert F.H(Path(F.__file__).read_bytes())=='36f8fcb93b28145a58354d400bcd8aa49a9cfeb9f66d4f87d99f905ccc078b83'
    class Traced(base):
        def step(self):
            m=self.memory
            if self.pc>=0x8000 and m[0x75b]==2:
                tag=m.rawtags[(self.pc-0x8000)//8192]
                if(tag,self.pc)in((128,0xad9b),(128,0xadc0),(128,0xae27),(207,0xaada),(207,0xb53d),(252,0xa760),(252,0xad58),(3,0xa066),(2,0xd24f),(217,0xbcc0)):
                    key=f'{tag:02X}:{self.pc:04X}';row=trace.setdefault(key,dict(count=0));row['count']+=1
                    q=dict(PC=self.pc,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,held=m[0x558],previous=m[0x55b],saved=m[0xdc],power=m[0x75b],target=bytes(m[0x16c:0x16e]).hex())
                    row.setdefault('first',q);row['last']=q
            return super().step()
    def deny(*args,**kw):raise AssertionError('Mini dispatch diagnostic attempted artifacts/native')
    def cold(image,key):m,q=F.Current.cold(image,True);opening.append(q);return m
    family=F.family()
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Runner.Native,'run',deny),patch.object(F.N,'NesMPU',Traced),patch.object(Runner,'Factory',family),patch.object(Runner,'cold',cold),patch.object(Runner,'strict_metadata',family.metadata):q=Model.run(raw,'mini',5100)
    q['actual_cold']=opening;q['readonly_weapon_dispatch']=trace;print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
