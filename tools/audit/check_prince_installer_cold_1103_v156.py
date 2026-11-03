"""Actual corrected C2 installer/fullcurrent-owner cold qualification."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_live_cold_1103_v152 as V
import prepare_prince_installer_manifest_1103_v155 as M
C,N,O,I=V.C,V.N,V.O,V.I


def loaded():
 base,q=M.image();m,out=C.cold(base,38)
 N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
 m[0x2001]=30
 return base,m,json.loads((O/'native-labels-v153.json').read_text())


def main():
 text=inspect.getsource(V.main).replace('v152','v156').replace('native-state-v149','native-state-v153').replace('native-labels-v149','native-labels-v153').replace('post-owner-v151.lbl','post-owner-v155.lbl')
 text=text.replace("C.M.M.A.L.P.T.labels(O/'post-selector-v149.lbl')","json.loads((O/'live-installer-measurement-v153.json').read_text())['shared_labels']")
 old="assert bytes(seed.ram[2][0x766:0x800])==state[1375:1529]";assert old in text
 text=text.replace(old,"expected_audio=bytearray(state[1375:1529]);expected_audio[:25]=(O/'native-installer-v153.bin').read_bytes();assert bytes(seed.ram[2][0x766:0x800])==expected_audio")
 text=text.replace("O/'post-selector-v149.s'","O/'post-selector-v153.s'")
 env=dict(V.__dict__,M=M,image=M.image,__file__=str(Path(__file__)));exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 path=O/'live-cold-CPU-v156.json';q=json.loads(path.read_text());q.update(C2_installer_actual_FarCall=True,old_resident_ROM_write_negative_retained='live-cold-negative-v152.json',scope=q['scope'].replace('copies/verifies53B','FarCalls owned C2 installer which copies/verifies53B').replace('clears staging','clears each readback-successful staging byte'))
 q['bindings'].update({p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'live-installer-measurement-v153.json',O/'native-installer-v153.bin',O/'native-final-v153.bin']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'live-cold-negative-v156.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
