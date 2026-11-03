"""Exact transport0179 parameter lifetime across actual public owner rows."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import check_prince_post_return_core_1102_v79 as A
import check_prince_native_stack_1102_v72 as S
import check_prince_successor_services_1102_v27 as I
N,O=S.N,A.O


def main():
 b,seed,lab=A.loaded();shared=A.V.A.P.T.labels(O/'shared-frame-v22.lbl');selector=A.V.A.P.T.labels(O/'deferred-selector-v79.lbl')
 stage=selector['PrPrince']+3;load=lab['PpNativeRoute']+1
 assert bytes(seed.bundle['raw'][16+65*8192+stage-0xa000:16+65*8192+stage-0xa000+3])==bytes.fromhex('8d7901')
 assert bytes(seed.ram[2][load-0xc000:load-0xc000+3])==bytes.fromhex('ad7901')
 actual=N.NesMPU;frames=[];pending=None;events=Counter();sources=set();tags=set();shadow=[]
 offsets=[0x162,0x16a,0x16c,0x16d,0x179]
 class Trace(actual):
  def step(self):
   nonlocal pending
   m=self.memory;bank=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
   if bank==193 and self.pc==shared['ShDispatch']:
    frames.append(bytes(m[x]for x in offsets));events['owner_frames_entered']+=1
   if bank==193 and self.pc==shared['ShDispatchEnd']-1:
    assert frames and frames.pop()==bytes(m[x]for x in offsets),'Owner failed exact five-SMC restore'
    events['owner_frames_five_SMC_restored']+=1
   if bank==193 and self.pc==stage:
    assert pending is None;pending=self.a;assert pending<114 and pending%3==0
    assert S.N.get(m,'SelectedCharacter')==38
    sources.add(m.rawtags[2]);tags.add(pending);events['stage_store']+=1
   elif pending is not None and bytes(m[self.pc:self.pc+3])==bytes.fromhex('8d7901'):
    raise AssertionError(('Transport overwrote unread tag',hex(self.pc),bank,pending))
   if bank==2 and self.pc==load:
    assert pending is not None and m[0x179]==pending;events['tag_consumed_before_native_rewrite']+=1;pending=None
   return super().step()
 N.NesMPU=Trace
 try:
  for cwindow in [2,201]:
   for row in range(37):
    m=N.fork(seed);m.raw_page(2,cwindow);N.put(m,CurrentBankC=cwindow,FrameCounter=1)
    # Legitimate callback contracts: X0 player, head probe6, side probe9.
    y=6 if row==10 else 9 if row==14 else 109
    try:I.invoke(m,193,0xb08c+3*row,(83,0,y,0x21))
    except Exception as error:raise AssertionError(('Tag row failure',cwindow,row,repr(error)))from error
    assert not frames and pending is None
    if row==19:assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
  for bank in [2,3]:
   for index in range(16):
    m=N.fork(seed);m.ram[bank][0x1fe0+index]^=1;before=events['stage_store'];out=I.invoke(m,193,0xb08c,(83,0,109,0x21));assert not out['regs'][3]&1 and events['stage_store']==before and not frames and pending is None
  # Exact authenticated retirement invalidates both headers before any later
  # public dispatch can stage or consume an old parameter.
  m=N.fork(seed);manager=A.V.A.P.T.labels(O/'collision-owner-v59.lbl');I.invoke(m,193,manager['PrRetire']);assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0
  before=events['stage_store'];out=I.invoke(m,193,0xb08c+21,(83,0,109,0x21));assert not out['regs'][3]&1 and events['stage_store']==before and not frames
 finally:N.NesMPU=actual
 assert tags==set(range(0,111,3))-{57} and sources=={2,201} and events['stage_store']==events['tag_consumed_before_native_rewrite'],(sorted(tags),sorted(sources),dict(events),hex(stage),hex(load))
 q=dict(passed=True,CPU_only=True,source_injected=True,qualified_full_cold=False,ROM_written=False,physical_operand=0x179,all37_published_public_rows_exercised=True,parameter_rows=sorted(tags),row19_direct_authenticated_retirement_not_parameterized=True,C_windows_at_stage=sorted(sources),counts=dict(events),bad_header_bytes_rejected_before_stage=32,actual_retire_then_dispatch_reject=True,selector_growth=0,foreign_selector_instructions_unchanged=True,lifetime='0179 is exclusively the transport-owned result-A instruction operand, already one of its five saved bytes. Selected38 exact full-header/range admission stages the tag there. Actual shared caller restores original A/X/Y/P and mapsC2 before RAM3/2 dispatch. FarCallCommon writes0179 only after the private call returns; first private router load consumes the tag before any possible nested native call. All actual owner returns restore allfive original SMC bytes. No world SavedY alias or new scratch allocation.',required='Changed-image cold/backing/cookie/current-owner carry fix, deepest IRQ aggregate and original C766/packet lifetime amendment before native admission.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(A.__file__),O/'native-public-v78.s',O/'native-services-v78.s',O/'deferred-selector-v79.s',O/'shared-frame-v22.s',O/'post-return-measurement-v78.json',O/'deferred-death-CPU-v79.json']})
 (O/'tag-transport-CPU-v84.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','parameter_rows']}))


if __name__=='__main__':main()
