"""Reverify every MMC5 slot after41d's two retained water-budget failures.

MMC3 must be byte identical to the fully checked41d ROM. Its383 passing
native/baseline slots are retained with current-CRC raw logs. All378 MMC5
slots execute again on41e. This is explicitly a staged run, not a single run.
"""
from pathlib import Path
import concurrent.futures,hashlib,json,re,shutil,subprocess,sys,zlib
ROOT=Path(__file__).resolve().parents[2]
CP=ROOT/'build/checkpoints/roster-audit-v41-provisional-e'
OLD=ROOT/'build/verification/summary-roster-audit-v41-provisional-d.json'
OUT=CP/'validation';OUT.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fixtures():
 paths=sorted(p for p in(ROOT/'tests').rglob('*')if p.is_file())+[ROOT/'tools/run_mesen.py']
 return {p.relative_to(ROOT).as_posix():sha(p)for p in paths}
old=json.loads(OLD.read_text());before=fixtures()
assert old['result']=='failed'and len(old['cases'])==759
assert sorted(old['failures'])==['bass-water-performance failed for smb-crossover-mmc5','megaman-water-performance failed for smb-crossover-mmc5']
assert old['fixture_hashes_before']==old['fixture_hashes_after']==before
roms={m:sha(CP/f'smb-crossover-{m}.nes')for m in('mmc3','mmc5')}
assert roms['mmc3']==old['roms']['mmc3']
names={c['test']for c in old['cases']if c['rom']=='smb-crossover-mmc5'}|{'megaman-water-performance','bass-water-performance'}
assert len(names)==378
cases=[];failures=[]
def bind_log(rom,test):
 p=ROOT/f'build/verification/{rom}-{test}.log';text=p.read_text()
 source=(ROOT/'build'/f'{rom}.nes')if rom.endswith('-baseline')else CP/f'{rom}.nes'
 crc=re.search(r'File CRC32: 0x([0-9A-Fa-f]+)',text)
 assert crc and int(crc[1],16)==zlib.crc32(source.read_bytes()),(rom,test,'Stale ROM log')
 assert 'PASS 'in text and not re.search(r'\bFAIL\b|Lua error',text),(rom,test,'Failure in native log')
 dest=OUT/p.name;shutil.copyfile(p,dest)
 return {'test':test,'rom':rom,'result':'passed','rom_sha256':sha(source),'log':dest.relative_to(ROOT).as_posix(),'log_sha256':sha(dest)}
for c in old['cases']:
 if c['rom']!='smb-crossover-mmc5':cases.append(bind_log(c['rom'],c['test']))
assert len(cases)==383
def test(name):
 args=[sys.executable,'tools/run_mesen.py',f'tests/{name}.lua',str(CP/'smb-crossover-mmc5.nes'),'--timeout','90']
 if name in('water-motion-differential','water-expansion-differential','water-corner-differential','water-oam-differential'):args+=['--timeout','80']
 if name=='sophia-native-products':args+=['--timeout','150']
 if name=='scrooge-ceiling-separation':args+=['--timeout','180']
 r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
 if r.returncode or'PASS 'not in r.stdout:
  print(r.stdout[-4000:]+r.stderr[-4000:],flush=True)
  raise RuntimeError(f'{name} failed MMC5 revalidation')
 entry=bind_log('smb-crossover-mmc5',name)
 print('PASS',name,flush=True)
 return entry
with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
 pending={pool.submit(test,n):n for n in sorted(names)}
 for f in concurrent.futures.as_completed(pending):
  try:cases.append(f.result())
  except Exception as exc:failures.append(str(exc))
after=fixtures();changed=sorted(n for n in before.keys()|after.keys()if before.get(n)!=after.get(n))
if changed:failures.append('Fixtures changed: '+', '.join(changed))
assert (ROOT/'build/verification/smb-crossover-mmc3-baseline-mario-trace.csv').read_bytes()==(ROOT/'build/verification/smb-crossover-mmc3-mario-trace.csv').read_bytes()
report={'result':'failed'if failures else'passed','method':'Staged:383 current-CRC MMC3/baseline slots retained from initial41d full run; all378 MMC5 slots rerun on41e. Original41d full failure retained.',
 'initial_failed_summary':str(OLD.relative_to(ROOT)),'initial_failed_summary_sha256':sha(OLD),'initial_full_log':'build/verification/roster-audit-v41d-full.log',
 'checkpoint':str(CP),'roms':roms,'cases':sorted(cases,key=lambda c:(c['rom'],c['test'])),'failures':failures,
 'fixture_hashes_before':before,'fixture_hashes_after':after,'changed_fixtures':changed,
 'script_sha256':sha(Path(__file__)),'single_full_run':False,'mario_replay':{'frames':521,'fields':19,'identical':True}}
target=ROOT/'build/verification/summary-roster-audit-v41-provisional-e.json'
target.write_text(json.dumps(report,indent=2)+'\n')
print(report['result'],len(cases),'current-ROM slots',failures,flush=True)
raise SystemExit(1 if failures else 0)
