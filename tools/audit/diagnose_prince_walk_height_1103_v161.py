"""Bounded source/native walk trajectory after real native entrance."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as V
N,O=V.N,V.O


def main():
 e,m,lab=V.first8();rows=[]
 for epoch in range(49):
  if epoch:m.controller_pad=1;N.put(m,SavedJoypad1Bits=1,SavedJoypadBits=1)
  out=e['run'](m,'GameLoop',lab)
  rows.append(dict(epoch=epoch,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),Y=N.get(m,'Player_Y_Position'),YHigh=N.get(m,'Player_Y_HighPos'),foot=m.ram[2][0x84]+256*m.ram[2][0x85],sourceY=m.ram[2][0x611]+256*m.ram[2][0x612],sourceAction=m.ram[2][0x616],sourceNext=m.ram[2][0x617],phase=m.ram[2][0xa6],HP=m.ram[2][0x6cf],engine=N.get(m,'GameEngineSubroutine'),lives=N.get(m,'NumberofLives')))
 q=dict(diagnostic_only=True,ROM_written=False,source_code_injected=False,rows=rows,bindings={p.relative_to(R).as_posix():V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'backdrop-manifest-v159.json',O/'backdrop-native-negative-v160.json']})
 (O/'walk-height-diagnostic-v161.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(rows))


if __name__=='__main__':main()
