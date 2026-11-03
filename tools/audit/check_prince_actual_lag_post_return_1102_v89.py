"""Trace the real negative-flag NMI branch and retain asynchronous SFX state."""
from collections import Counter
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_native_stack_1102_v72 as S
import check_prince_post_return_core_1102_v79 as A
O=A.O
COUNTS=Counter();AUDIO=Counter();PATH=None


def loaded():
 b,m,lab=A.loaded();S.N.put(m,NmiDisable=255)
 return b,m,lab


def fold_cuts(cuts):
 result={}
 for pc,sp,bank in cuts:
  key=(pc,bank)
  if key not in result or sp<result[key][1]:result[key]=(pc,sp,bank)
 return sorted(result.values())


def nmi_path(m):
 global PATH
 if PATH is None:
  assert S.address(m.bundle,'Squ2_SfxLenCounter')==0x7da
  code=bytes(m[0xe000:0x10000]);needle=bytes.fromhex('ad390110');hits=[]
  for i in range(len(code)-8):
   if code[i:i+4]==needle and code[i+5:i+8]==bytes.fromhex('ee3a01'):hits.append(i)
  assert len(hits)==1,hits
  start=0xe000+hits[0];offset=code[hits[0]+4];offset=offset-256 if offset&128 else offset
  PATH=(start+5,start+5+offset)
 return PATH


def normalized_state(m):
 # AudioUpdate owns this one SFX duration byte. Its actual value remains live;
 # run() proves IRQ cannot change it and the resumed foreground preserves the
 # exact post-NMI value. Every other byte in the original state view is exact.
 view=list(S.state(m));native=bytearray(view[4]);native[0x7da-0x200]=0;view[4]=bytes(native)
 return tuple(view)


def main():
 source=Path(S.__file__);text=source.read_text().replace('v72','v89')
 changes={
  'b,m,lab=C.loaded();fatal(m,b);scenarios=[]':"b,m,lab=CURRENT_LOADED();fresh=N.fork(m);fatal(m,b);scenarios=[]\n for i,v in enumerate([4,0,0]):m[address(b,'GameTimerDisplay')+i]=v",
  '_,m,_=C.loaded();N.put(m,ObjectOffset=5)':'m=N.fork(fresh);N.put(m,ObjectOffset=5)',
  "'GameRoutines'":"'GameCoreRoutine'",
  'if c.sp<=180 and (0x15a<=c.pc<0x17b':"if (bank==252 and(0xa760<=c.pc<0xa76e or 0xa795<=c.pc<0xa7a0 or c.pc==0xad75))or(0x15a<=c.pc<0x17b",
  "or bank==2 and lab['PpNativeTick']":"or bank==2 and lab['PpNativeRoute']<=c.pc<lab['PpNativePublicEnd'] or bank==2 and lab['PpNativeTick']",
  "assert ref['gateway_entries']==1,(name,ref)":"assert ref['gateway_entries']==(0 if name=='fatal-kill'else 1),(name,ref)",
  "cuts=sorted(ref['cuts'])":"cuts=fold_cuts(ref['cuts'])",
  ";minimum=min(minimum,ref['minSP'])":";print('Deepest actual lag cuts',name,len(cuts),flush=True);minimum=min(minimum,ref['minSP'])",
  "cuts=len(cuts)))":"cuts=len(cuts)))\n  print('Completed actual lag scenario',name,dict(COUNTS),minimum,flush=True)",
  'low=c.sp;cuts=set();injected=False;calls=Counter();gateway_return=None;gateway_entries=0':
   "low=c.sp;cuts=set();injected=False;calls=Counter();gateway_return=None;gateway_entries=0;audio_after=None",
  'assert not c.p&4\n':
   "assert not c.p&4;assert N.get(m,'NmiDisable')==255\n   lag_pc,regular_pc=nmi_path(m);lag_hits=0;regular_hits=0;audio_before=m[0x7da];skipped=N.get(m,'NmiSkipped')\n",
  "assert m[c.pc]!=0,('Stack ISR BRK',interrupt,hex(c.pc));c.step()":
   "lag_hits+=int(c.pc==lag_pc);regular_hits+=int(c.pc==regular_pc)\n    assert m[c.pc]!=0,('Stack ISR BRK',interrupt,hex(c.pc));c.step()",
  'assert regs[:3]==(c.a,c.x,c.y)':
   "audio_after=m[0x7da]\n   if interrupt[0]=='IRQ':assert lag_hits==regular_hits==0 and audio_after==audio_before\n   else:\n    assert lag_hits==1 and regular_hits==0,(interrupt,lag_hits,regular_hits)\n    assert N.get(m,'NmiSkipped')==(skipped+1)&255\n    AUDIO[(audio_before,audio_after)]+=1\n   COUNTS[interrupt[0]]+=1\n   assert regs[:3]==(c.a,c.x,c.y)",
  "assert c.sp==224 and gateway_return is None and(interrupt is None or injected)":
   "assert c.sp==224 and gateway_return is None and(interrupt is None or injected)\n if audio_after is not None:assert m[0x7da]==audio_after,('Foreground changed async SFX counter',interrupt,audio_after,m[0x7da])",
  "assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut)":
   "assert got['regs']==ref['regs']and state(z)==expected,(name,kind,cut,got['regs'],ref['regs'],[(hex(i+0x200),a,v)for i,(a,v)in enumerate(zip(expected[4],state(z)[4]))if a!=v][:8])",
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(Path(__file__)),__name__='prince_actual_lag_v89',CURRENT_LOADED=loaded,fold_cuts=fold_cuts,nmi_path=nmi_path,COUNTS=COUNTS,AUDIO=AUDIO)
 exec(compile(text,str(source),'exec'),env);env['state']=normalized_state
 try:env['main']()
 except Exception as error:
  (O/'post-return-stack-negative-v89.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error),actual_lag_branch_counts=dict(COUNTS)),indent=2)+'\n');raise
 path=O/'native-stack-CPU-v89.json';q=json.loads(path.read_text())
 assert q['real_IRQ_lagNMI_cuts']==dict(COUNTS)
 q.update(actual_lag_NmiDisable=255,actual_lag_branch_PC=PATH[0],forbidden_regular_NMI_branch_PC=PATH[1],all_lag_cuts_reached_lag_branch_exactly_once=True,all_lag_cuts_rejected_regular_branch=True,native_audio_counter=dict(address=0x7da,symbol='Squ2_SfxLenCounter',source='src/music_drivers/vanilla_sfx.s',transitions=[dict(before=a,after=z,cuts=n)for(a,z),n in sorted(AUDIO.items())],proof='Only this native audio duration byte is normalized in final cross-run comparison. IRQ preserves it; real lag AudioUpdate may advance it; every resumed foreground preserves exactly the post-NMI value. Full private RAM/R0..7/SMC/mapper/AXYP/SP and every other native0200..07FF byte remain exact.'),new_lifetimes_ungranted=True,source_code_injected=True,qualified_cold=False,supersedes_lag_wording=['v68 C67.loaded-derived positive1 regular NMI','v72 positive1 regular NMI','v80/v82/v85/v86 regular NMI'],scope='Actual complete GameCore earned source death at epoch20; native Kill only after resident return; row8 death update; star/1up native gateways. Every reached shared/SMC/hook/router/gateway instruction PC/A-bank pair at deepest actual SP runs genuine IRQ and FF lag NMI. No changed-image cold/auth/respawn/menu/emulator admission claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),source,Path(A.__file__),R/'src/game.s',R/'src/reset.s',R/'src/music_drivers/vanilla_sfx.s',O/'post-return-stack-negative-v88.json',O/'post-return-foreign-CPU-v81.json',O/'tag-transport-CPU-v84.json']})
 path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
