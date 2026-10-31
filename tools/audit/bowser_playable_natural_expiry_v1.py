"""Real whole-Main expiry/re-hit, flat-ground jump measurement, no timer seeds."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_current64_host_checks_v1 as A
import bowser_playable_contact_controls_v1 as I
from check_tmnt_render_oa import load,address
H=A.H;N=A.N;P=R/'build/bowser-current64-v3/joint';J=I.J
O=R/'build/bowser-playable-natural-expiry-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frame(m,keys=0):
 H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
 z=N.invoke(m,'GameLoop');N.C.A.consume(m);return z
def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,expiry=[],apex=[])
 try:
  b=load(J/'candidate.nes')
  for form in[0,8]:
   m=A.boot(b,form);hp=m.ram[3][0x1e29];first=I.call(m,'InjurePlayer');rows=[]
   assert m.ram[3][0x1e29]==hp-1 and H.get(m,'InjuryTimer')==8
   for age in range(200):
    if H.get(m,'InjuryTimer')==0:break
    old=H.get(m,'InjuryTimer');z=frame(m)
    assert m.ram[3][0x1e29]==hp-1 and z['counts'].get('BwMovement')==1
    rows.append(dict(age=age,old_timer=old,new_timer=H.get(m,'InjuryTimer'),HP=m.ram[3][0x1e29],CPU=z['CPU']))
   else:raise AssertionError('real natural Main expiry bound')
   assert H.get(m,'InjuryTimer')==0
   second=I.call(m,'InjurePlayer');assert m.ram[3][0x1e29]==hp-2 and second['counts'].get('BwInjury')==1
   q['expiry'].append(dict(form=form,whole_Main_updates=len(rows),first=first,rows=rows,second=second,no_timer_assignments=True))
  for root in[P,J]:
   b=load(root/'candidate.nes');m=A.boot(b,8);ys=[]
   for age in range(120):
    z=frame(m,128 if age<8 else 0);ys.append(H.get(m,'Player_Y_Position'))
   q['apex'].append(dict(candidate=sha(root/'candidate.nes'),startY=176,minY=min(ys),rise=176-min(ys),Y=ys))
  assert q['apex'][0]['rise']==37 and q['apex'][1]['rise']>=64,q['apex']
  old=(P/'bowser.bin').read_bytes();new=(J/'bowser.bin').read_bytes()
  lo=address(b,'Bw1Gravity')-0xa000;hi=address(b,'BwCoreEnd')-0xa000
  assert old[lo:hi]==new[lo:hi]
  q.update(passed=True,original_falling_gravity_fraction_bytes_exact=True,native_duration='8intervals; whole Main expiry measured without timer result injection')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),Path(I.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin',P/'candidate.nes',P/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['expiry','apex','bindings']}));assert q['passed']
if __name__=='__main__':main()
