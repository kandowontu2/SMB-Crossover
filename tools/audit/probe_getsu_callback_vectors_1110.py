"""Diagnose exact current mapped draw IRQ/FF cuts without repeating sprite matrix."""
import argparse,inspect,json
from pathlib import Path
import check_getsu_powerup_callback_1110 as Q

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 out=a.output.resolve();out.mkdir(exist_ok=True)
 _,b,_,labels,_,_=Q.compose(out);m=Q.Earned.H.prepare(b)
 m[0x5116]=2;Q.Render.N.put(m,CurrentBankC=2);m[0xc030]=0;m[0xc021]=m[Q.Render.STATE['GfClock']]
 Q.Render.N.put(m,CurrentCHRBank=0,X5ChrMode=0)
 text=inspect.getsource(Q.Render.interrupt_controls)
 text=text.replace('assert cpu.pc == 0x5b00 and cpu.sp == 224 and bool(seen) == (cut is not None)',
                   "assert cpu.pc == 0x5b00 and cpu.sp == 224 and bool(seen) == (cut is not None),(cut,kind,cpu.pc,cpu.sp,seen)")
 text=text.replace('if cut == cpu.pc and not seen:',"if cut == cpu.pc and not seen:\n                print('CUT',hex(cut),kind,flush=True)")
 scope=dict(Q.Render.__dict__);exec(text,scope)
 rows=scope['interrupt_controls'](m,labels)
 (out/'vectors.json').write_text(json.dumps(rows,indent=2)+'\n');print(rows)

if __name__=='__main__':main()
