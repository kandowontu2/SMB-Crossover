from pathlib import Path
import json,itertools,hashlib,statistics
D=Path(__file__).resolve().parent;t=(D/'test_native_probes_qa_cpu_v2.py').read_text();t=t[:t.index('rows=[]')];t=t.replace("O=D/'native-probes-qa-v2/cpu-v1'","O=D/'native-probes-qa-v2/cpu-other-v1'").replace('dict(SelectedCharacter=1,','dict(SelectedCharacter=CHAR,')
ns={'__file__':str(__file__),'__name__':'_negative'};exec(compile(t,str(__file__),'exec'),ns)
rows=[]
for char in [n for n in range(20)if n!=1]:
 ns['CHAR']=char
 for case in itertools.product((15,127,248),(31,125,208),(0,1),(7,42,77),(0x30,0xff),(0xdd,)):
  for name in ('CrossoverHeadProbe','CrossoverSourceSideProbe'):
   a=ns['invoke'](ns['old'],name,case);b=ns['invoke'](ns['new'],name,case)
   assert a[:2]==b[:2]and a[3]==b[3],(char,name,case,a,b)
   rows.append((char,name,b[2]-a[2]))
q=dict(passed=True,ROM_sha256=hashlib.sha256(ns['new']['raw']).hexdigest(),cases=len(rows),other_selectors=19,exact_other_query_registers_RAM_and_banks=True,extra_cycles_by_query={n:sorted(set(c for k,key,c in rows if key==n))for n in ('CrossoverHeadProbe','CrossoverSourceSideProbe')},scope='Actual assembled other-selector query differentials in explicit zero/profile-state CPU scenes; not a replacement for native source-form, weapon, scene or timing/interrupt regressions.')
(ns['O']/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))

