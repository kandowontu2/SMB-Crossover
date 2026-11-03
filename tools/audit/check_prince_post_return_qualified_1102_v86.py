"""Correct native row8 gateway accounting; preserve v85 fixture negative."""
from pathlib import Path
import sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_deepest_post_return_1102_v85 as V


def main():
 source=Path(V.__file__);text=source.read_text().replace('v85','v86')
 marker=' marker=" env=dict(__file__"'
 assert marker in text
 text=text.replace(marker," text=text.replace(\"target=='GameCoreRoutine'\",\"name=='fatal-kill'\")\n"+marker)
 # This is one aggregate progress receipt, not a per-case output tree.
 needle=' text=text.replace(marker,injection+marker)'
 addition=''' injection+=" text=text.replace(\\\"cuts=len(cuts)))\\\",\\\"cuts=len(cuts)))\\\\n  print('IRQ scenario complete',name,dict(counts),minimum,flush=True)\\\\n  (O/'post-return-IRQ-progress-v86.json').write_text(json.dumps(dict(partial=True,rows=rows,counts=dict(counts),minimum_SP=minimum),indent=2)+'\\\\\\\\n')\\\")\\n"
'''
 # Keep progress logging simple; the final receipt remains the only proof.
 addition=" injection+=\" text=text.replace(\\\"cuts=len(cuts)))\\\",\\\"cuts=len(cuts)))\\\\n  print('IRQ scenario complete',name,dict(counts),minimum,flush=True)\\\")\\n\"\n"
 assert needle in text;text=text.replace(needle,addition+needle)
 env=dict(__file__=str(Path(__file__)),__name__='prince_postreturn_qualified_v86');exec(compile(text,str(source),'exec'),env);env['main']()


if __name__=='__main__':main()
