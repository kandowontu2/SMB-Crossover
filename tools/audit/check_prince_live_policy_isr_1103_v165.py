"""Current159 first8/palette/name and newcold seams under actual FF/IRQ."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
N,O,I=V.N,V.O,V.I


def environment():
 V.A.C.loaded=V.loaded;V.A.C.image=V.M.image;V.A.bind();e,text=V.A.H.helpers()['environment']()
 marker="  if interrupt is not None and not injected and cut==interrupt[1]:";assert marker in text
 start=text.index('  cut=(c.pc,c.sp,m.rawtags[1],');end=text.index(marker,start);old=text[start:end]
 old=old.replace("N.get(m,'NmiDisable')==255","N.get(m,'NmiDisable')==255 and target!='PrinceColdProposed'")
 extra="""  if N.get(m,'NmiDisable')==255:
   if target=='PrinceColdProposed':
    if bank==3 and $BFC4<=c.pc<$BFDF or bank==2 and $C766<=c.pc<$C77F or bank==193 and $A7DC<=c.pc<$A7EF:cuts.add(cut)
   elif bank==3 and $BFA3<=c.pc<$BFD8 or bank==2 and lab['PpNativeColors']<=c.pc<lab['PpColorsEnd']:cuts.add(cut)
""".replace('$','0x')
 text=text[:start]+old+extra+text[end:]
 text=text.replace('range(500000)','range(4000000)')
 text=text.replace("m[address(b,'SafecallA_SMC')+1]=83","m[address(b,'SafecallA_SMC')+1]=0 if target=='WriteGameText'else 83")
 original_address=e['address'];original_location=e['location']
 e['address']=lambda b,n:0xae00 if n=='PrinceColdProposed'else original_address(b,n)
 e['location']=lambda b,n:16+65*8192+0xe00 if n=='PrinceColdProposed'else original_location(b,n)
 exec(compile(text,str(Path(__file__)),'exec'),e);return e,text


def scenarios():
 e,source=environment();_,m,lab=V.loaded();N.put(m,NmiDisable=255,VRAM_Buffer1_Offset=0);m[0x2001]=30
 firste,first,firstlab=V.first8()
 result=[('actual-first8-original-constructor',first,'GameLoop'),('native-GetPlayerColors',N.fork(m),'GetPlayerColors'),('native-WriteGameText0',N.fork(m),'WriteGameText')]
 base,q=V.M.image();cold=N.fresh(base)
 for k in [2,3]:cold.ram[k][:]=bytes([0x9d])*8192;cold.ram[k][0x1fe0:0x1ff0]=bytes(16)
 V.C.fields(cold,38);result.append(('new-cold-stage-installer-only',cold,'PrinceColdProposed'))
 return e,lab,result,source


def main():
 e,lab,cases,source=scenarios();counts={};rows=[];minimum=224
 for name,seed,target in cases:
  m=N.fork(seed);ref=e['run'](m,target,lab);want=V.A.U.C.V.normalized_state(m);cuts=V.A.U.V.fold(ref['cuts']);assert cuts
  print('Current159 policy ISR',name,len(cuts),flush=True);one={}
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    if kind=='IRQ'and cut[3]:continue
    z=N.fork(seed);out=e['run'](z,target,lab,(kind,cut));assert out['regs']==ref['regs']and V.A.U.C.V.normalized_state(z)==want,(name,kind,cut)
    minimum=min(minimum,out['minSP']);counts[kind]=counts.get(kind,0)+1;one[kind]=one.get(kind,0)+1
   print(name,kind,one,minimum,flush=True)
  rows.append(dict(name=name,cuts=len(cuts),I1_FF_cuts=sum(bool(c[3])for c in cuts),foreground_minSP=ref['minSP'],counts=one))
 q=dict(passed=True,CPU_only=True,source_code_injected=False,ROM_written=False,memory_SHA256=V.M.image()[1]['expected_memory_only_SHA256'],real_IRQ_and_genuine_FF_NMI=counts,minimum_SP=minimum,scenarios=rows,source_fixture_SHA256=V.M.sha(source.encode()),scope='Actual159 source-backed completecold/currentheaders. First8 genuine originalconstructor/GameLoop and fullnative colors/name callers: old watchedgateway/transport PCs plus every new live/palette PC and all actualI1 foreground PCs. Coldonly separately covers every new finalizer staging/installer/selector thunk PC at actualI1 (no standaloneIRQ whenI1), not all historicaldecoder PCs. ActualFF negative branch/INC/no regularbranch and fullprivate/R0..7/SMC/maps/AXYP/SP/native state except source-tracked07D8/DA; nestedIRQ still separate. No groundedwalk/nativebody/menu/install qualification inferred.',bindings={p.relative_to(R).as_posix():V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'backdrop-manifest-v159.json',O/'backdrop-binding-v157.json',O/'grounded-order-v163.json',O/'palette-gateway-CPU-v164.json',R/'src/reset.s']})
 (O/'live-policy-ISR-v165.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'live-policy-ISR-negative-v165.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
