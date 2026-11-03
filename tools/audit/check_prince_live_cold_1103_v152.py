"""Execute proposed151 fullcold, stage lifetime, current owners and Fresh."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_strike_cold_1103_v131 as C
import prepare_prince_live_manifest_1103_v151 as M
N,O,I=C.N,C.O,C.I
image=M.image


def loaded():
 base,q=image();m,out=C.cold(base,38)
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
 m[0x2001]=30
 return base,m,json.loads((O/'native-labels-v149.json').read_text())


def main():
 base,manifest=image();live=(O/'native-live-v149.bin').read_bytes();state=(O/'native-state-v149.bin').read_bytes();lab=json.loads((O/'native-labels-v149.json').read_text());owner=C.M.M.A.L.P.T.labels(O/'post-owner-v151.lbl');selector=C.M.M.A.L.P.T.labels(O/'post-selector-v149.lbl')
 actual=N.NesMPU;events=[];publish=[]
 class Trace(actual):
  def step(self):
   m=self.memory;pr=N.get(m,'SelectedCharacter')==38
   if pr and m.rawtags[1]==3 and self.pc==0xbfc4:
    events.append(dict(event='fully_copied_original_state',SP=self.sp,Cmap=m.rawtags[2]));assert bytes(m.ram[2][0xb0:0x60f])==state[:1375]
   if pr and m.rawtags[2]==2 and self.pc==lab['PpNativeResetTail']:
    events.append(dict(event='ResetTail_entry',SP=self.sp,Cmap=m.rawtags[2]));assert bytes(m.ram[2][0x200:0x235])==live
   if pr and m.rawtags[1]==193 and self.pc==selector['PrCopyLive']:
    events.append(dict(event='resident_after_finalizer_return',SP=self.sp,Cmap=m.rawtags[2]));assert m.rawtags[2]==2 and m.ram[2][0xab]==0xa7 and bytes(m.ram[2][0x200:0x235])==live
   if pr and any(m.ram[k][0x1fe0]for k in [2,3])and not getattr(self,'published',False):
    assert bytes(m.ram[2][0x200:0x235])==bytes(53)and bytes(m.ram[3][0x1fa3:0x1fd8])==live
    assert any(e['event']=='resident_after_finalizer_return'for e in events)
    publish.append(dict(SP=self.sp,PC=self.pc,Cmap=m.rawtags[2],headers=[m.ram[k][0x1fe0]for k in [2,3]]));self.published=True
   return super().step()
 N.NesMPU=Trace
 try:
  print('Actual151 Prince fullcold/lifetime.',flush=True);seed,out=C.cold(base,38)
 finally:N.NesMPU=actual
 assert [e['event']for e in events]==['fully_copied_original_state','ResetTail_entry','resident_after_finalizer_return'],events
 assert events[2]['SP']>events[1]['SP']and publish
 oldbase,_=C.image();oldseed,_=C.cold(oldbase,38)
 assert bytes(seed.ram[2][:0x766])==bytes(oldseed.ram[2][:0x766]),[(hex(i),a,z)for i,(a,z)in enumerate(zip(seed.ram[2][:0x766],oldseed.ram[2][:0x766]))if a!=z][:15]
 assert bytes(seed.ram[2][0x766:0x800])==state[1375:1529]
 seeds={38:seed};coldrows=[dict(owner=38,CPU=out['CPU'],minSP=out['minSP'])]
 for raw in [37,39]:
  print('Actual151 foreign complete cold',raw,flush=True);m,now=C.cold(base,raw);before,prior=C.cold(oldbase,raw)
  assert now['regs']==prior['regs']and all(bytes(a)==bytes(z)for a,z in zip(m.ram,before.ram)),('Foreign complete cold parity',raw)
  seeds[raw]=m;coldrows.append(dict(owner=raw,CPU=now['CPU'],oldCPU=prior['CPU'],minSP=now['minSP'],full_AXYP_SP_private_parity=True))
 transitions=[]
 for old in [37,38,39]:
  for new in [37,38,39]:
   print('Actual151 transition',old,new,flush=True);m=N.fork(seeds[old]);C.fields(m,new);now=I.invoke(m,193,0xae00,(83,71,109,0x21));assert now['regs'][3]&1
   assert all(bytes(m.ram[k][0x1fe0:0x1ff0])==bytes(seeds[new].ram[k][0x1fe0:0x1ff0])for k in [2,3])
   if new==38:assert bytes(m.ram[3][0x1fa3:0x1fd8])==live and bytes(m.ram[2][0x200:0x235])==bytes(53)
   transitions.append(dict(old=old,new=new,CPU=now['CPU'],minSP=now['minSP']))
  m=N.fork(seeds[old]);N.put(m,SelectedCharacter=0);now=I.invoke(m,193,0xae0b,(83,71,109,0x21));assert now['regs'][3]&1 and not m.ram[2][0x1fe0]and not m.ram[3][0x1fe0]
 fresh=[]
 for row in [15,36]:
  m=N.fork(seed);m.ram[2][0x6cf]=2;m.ram[2][0x6ee]=2;before=bytes(m.ram[3]);I.invoke(m,193,0xb08c+3*row)
  assert bytes(m.ram[3])==before and m.ram[2][0x6cf]==5 and not m.ram[2][0x6ee]and bytes(m.ram[2][0x200:0x235])==bytes(53)
  fresh.append(row)
 rejects=0
 for raw in [37,38,39]:
  for bank in [2,3]:
   for index in range(16):
    m=N.fork(seeds[raw]);m.ram[bank][0x1fe0+index]^=1;before=[bytes(a)for a in m.ram];now=I.invoke(m,193,0xb08c,(83,71,109,0x21));assert not now['regs'][3]&1 and before==[bytes(a)for a in m.ram];rejects+=1
 q=dict(passed=True,CPU_only=True,source_injection=False,ROM_written=False,private_proposal=True,root_execution_grant_required=True,memory_SHA256=manifest['expected_memory_only_SHA256'],cold=coldrows,lifetime_events=events,first_header_publication=publish,original_constructor_state_exact=True,packet_zero_before_live=True,all_ordered_transitions=transitions,foreign_retire_cases=3,warm_Fresh_preserves_live_code=fresh,bad_header_rejections=rejects,scope='Actual151 source-backed full manager/common worker/three packed streams/native constructor executes. Original1375B state fully copied before staging53B in source-dead OAM. CanonicalResetTail and NativeInit unwind before resident copies/verifies53B former-cold finalizer; clears staging before either header commit. Current Ex/Bub completecold retains fullprivate/AXYP/SP parity. Every transition reloads originalcoldcode before finalization; warmFresh never executes coldcode. No native emulator/menu/install admission.',bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),Path(M.__file__),O/'live-manifest-v151.json',O/'native-live-v149.bin',O/'native-state-v149.bin',O/'post-owner-v151.s',O/'post-selector-v149.s']})
 (O/'live-cold-CPU-v152.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','all_ordered_transitions']}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'live-cold-negative-v152.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
