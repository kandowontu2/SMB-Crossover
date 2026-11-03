"""Distinct current consumer replay retaining160 trajectory assertion negative."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
O=V.O


def main():
 text=inspect.getsource(V.main).replace('v160','v162')
 needle="assert N.get(m,'NumberofLives')==2 and N.get(m,'Player_Y_Position')==176"
 assert needle in text;text=text.replace(needle,needle+",('Right epoch',epoch,N.get(m,'NumberofLives'),N.get(m,'Player_Y_Position'),N.get(m,'GameEngineSubroutine'),xs[-1],m.ram[2][0x6cf],m.ram[2][0x616])")
 env=dict(V.__dict__,__file__=str(Path(__file__)));exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 path=O/'backdrop-native-CPU-v162.json';q=json.loads(path.read_text());q['bindings'].update({p.relative_to(R).as_posix():V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'walk-height-diagnostic-v161.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'backdrop-native-negative-v162.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
