"""All current owners complete cold/header/retirement on final130 backing."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
import prepare_prince_strike_manifest_1103_v130 as M
N,O,I=C.N,C.O,C.I
image=M.image;fields=C.fields;clear=C.clear;cold=C.cold


def loaded():
 base,q=image();m,out=cold(base,38)
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
 m[0x2001]=30
 return base,m,json.loads((O/'native-labels-v122.json').read_text())


def main():
 source=Path(C.__file__);text=inspect.getsource(C.main).replace('v98','v131').replace('post-owner-v97.lbl','post-owner-v130.lbl').replace('native-state-v78.bin','native-state-v122.bin')
 host_source=inspect.getsource(C.C.host).replace('v78','v122')
 henv=dict(C.C.__dict__);exec(compile(host_source,str(Path(C.C.__file__)),'exec'),henv)
 previous=C.C.host
 def host(base):
  C.C.C.H.W.PIN=M.M.sha(base['raw']);return henv['host'](base)
 C.C.host=host
 try:
  env=dict(C.__dict__,__file__=str(Path(__file__)),image=image);exec(compile(text,str(source),'exec'),env);env['main']()
 finally:C.C.host=previous
 path=O/'current-shared-cold-CPU-v131.json';q=json.loads(path.read_text());assert q['passed']
 q.update(source_runtime_version=122,cold_backing_version=129,current_parent_SHA256=M.PIN,scope='Actual final130 source-backed memory image over exact cf7. Complete shared531B manager, typed worker, all three packed streams, readback, original constructor and both complete header publications execute. Ex37/Prince38/Bub39, all nine ordered transitions, foreign-selected retirement and96 individual bad-header bytes qualified. Prince state audio suffix and every source constructor field exact. No source-code injection, ROM/menu/install/native emulator claim; hot/earned defeat/death/respawn/ISR remain separate.')
 q['bindings'].update({p.relative_to(R).as_posix():M.M.sha(p.read_bytes())for p in [Path(__file__),source,Path(M.__file__),O/'strike-manifest-v130.json',O/'native-labels-v122.json',O/'cold-link-storage-v129.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'strike-shared-cold-negative-v131.json').write_text(json.dumps(dict(passed=False,CPU_only=True,exception=repr(error)),indent=2)+'\n');raise
