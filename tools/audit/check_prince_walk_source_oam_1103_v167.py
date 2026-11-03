"""Current source OAM with the already-qualified source1->native0 palette."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_walk_oam_1103_v166 as V
O=V.O


def main():
 text=inspect.getsource(V.main).replace('v166','v167').replace("p['attribute']","(p['attribute']&0xfc)")
 env=dict(V.__dict__,__file__=str(Path(__file__)));exec(compile(text,str(Path(V.__file__)),'exec'),env);env['main']()
 path=O/'walk-oam-CPU-v167.json';q=json.loads(path.read_text());q.update(native_palette_selector=0,original_palette_selector=1,existing_palette_mapping='Frozen32/42 maps original sourcepalette1 to nativeplayer0, preserving actual27/16/20 foreground hues.166 incorrectly compared original palette-select bits directly; negative retained. No renderer/palette/physics change made.')
 q['bindings'].update({p.relative_to(R).as_posix():V.V.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'walk-oam-negative-v166.json',R/'tools/audit/measure_prince_palette_contact_1102_v32.py',R/'tools/audit/measure_prince_native_link_1102_v42.py']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':
 try:main()
 except Exception as error:
  (O/'walk-oam-negative-v167.json').write_text(json.dumps(dict(passed=False,exception=repr(error)),indent=2)+'\n');raise
