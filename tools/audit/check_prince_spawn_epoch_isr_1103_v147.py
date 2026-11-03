"""Entire first8 ReadyA7 resync under genuine FF NMI and hardware IRQ."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_spawn_epoch_1103_v146 as P
N,O,A=P.N,P.O,P.A


def prepared():
 text=inspect.getsource(P.main);marker=" e=A.environment();pair=[N.fork(m),N.fork(m)];newlab=inject(pair[1]);outs=[]";assert marker in text
 text=text[:text.index(marker)]+" N.put(m,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0);e=A.environment();new=N.fork(m);labels=inject(new);return e,new,labels\n"
 env=dict(P.__dict__);exec(compile(text,str(Path(P.__file__)),'exec'),env);return env['main']()


def main():
 e,seed,lab=prepared();assert seed.ram[2][0xab]==0xa7 and seed.ram[2][0xaa]==0
 m=N.fork(seed);ref=e['run'](m,'GameLoop',lab);want=A.U.C.V.normalized_state(m);assert N.get(m,'Player_Y_Position')==176 and m.ram[2][0xaa]==1
 cuts=A.U.V.fold(ref['cuts']);counts={};minimum=224
 for kind in ['IRQ','lagNMI']:
  for cut in cuts:
   if kind=='IRQ'and cut[3]:continue
   z=N.fork(seed);out=e['run'](z,'GameLoop',lab,(kind,cut));assert out['regs']==ref['regs']and A.U.C.V.normalized_state(z)==want,(kind,cut);minimum=min(minimum,out['minSP']);counts[kind]=counts.get(kind,0)+1
  print('First8 ReadyA7 constructor',kind,counts,minimum,flush=True)
 # Non-stage epochs must never reset health or sword inventory.
 m.ram[2][0x6cf]=3;m.ram[2][0x6ee]=2
 for i in range(8):
  out=e['run'](m,'GameLoop',lab);assert m.ram[2][0x6cf]==3 and m.ram[2][0x6ee]==2 and N.get(m,'NumberofLives')==2
 q=dict(passed=True,CPU_only=True,source_code_injected=True,changed_full_cold_qualified=False,ROM_written=False,source_runtime_version=145,new_first8_caller_ready=0xa7,initial_epoch_valid=0,constructor_resync_nativeY=176,physical_foot=208,real_IRQ_actual_FF_lagNMI=counts,all_actual_FF_I1_cuts=sum(bool(c[3])for c in cuts),foreground_minimum_SP=ref['minSP'],minimum_SP=minimum,subsequent8_live_epochs_preserve_HP3_sword2=True,scope='Prototype145 only after actual130 cold and genuine native entrance7->8. Whole first realGameLoop ReadyA7/EpochValid0 resync reaches original constructor under genuine sourceFF interval, every recordedPC/A-bank/Iflag/deepestSP. Native IRQ I0only; FFNMI I0orI1 including CLI nested eligibility. Exact private/native/R0..7/SMC/maps/AXYP/SP with source-tracked07D8/DA audio only; actual lag branch/INC/no regular branch asserted. New source constructor reads native entrance coordinates; no fixedY. Later8sourceepochs retain HP3/sword2. New physical backing/cookie/fullcold and nestedIRQ/native still pending.',bindings={p.relative_to(R).as_posix():P.C.M.M.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),O/'deferred-strike-measurement-v145.json',O/'spawn-epoch-CPU-v146.json',O/'native-services-v145.s',O/'native-metadata-v145.bin',R/'src/reset.s',R/'src/music_drivers/vanilla_sfx.s']})
 (O/'spawn-epoch-ISR-CPU-v147.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'spawn-epoch-ISR-negative-v147.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
