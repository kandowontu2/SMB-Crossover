"""Use every old performance assertion for all eight frozen native fixtures."""
from pathlib import Path
import argparse,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 source=(ROOT/'tools/audit/summarize_tmnt_audio_performance_oc.py').read_text();old="for name in ['leonardo','donatello']:";assert source.count(old)==1
 source=source.replace(old,"for name in [n+'-'+m for n in ['leonardo','raphael','michelangelo','donatello']for m in ['easy','hard']]:")
 source=source.replace('Two arranged600-update native components','Eight arranged600-update native components')
 # External copy resolves ROOT through its own location; bind the real workspace.
 source=source.replace('ROOT=Path(__file__).resolve().parents[2]', 'ROOT=Path('+repr(str(ROOT))+')')
 tool=a.output.with_suffix('.checker.py');tool.write_text(source);z=subprocess.run([sys.executable,str(tool),'--baseline',str(a.baseline),'--candidate',str(a.candidate),'--output',str(a.output)],capture_output=True,text=True)
 a.output.with_suffix('.log').write_text(z.stdout+z.stderr)
 import json
 if a.output.exists():
  q=json.loads(a.output.read_text());print('performance_gate',q['passed'])
  for name,r in q['runs'].items():print(name,{k:[v['old']['lag_NMIs'],v['new']['lag_NMIs']]for k,v in r['phases'].items()})
 else:print((z.stdout+z.stderr)[-2000:])
 return z.returncode
if __name__=='__main__':raise SystemExit(main())
