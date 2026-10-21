"""Freeze every native log, including failures, before another checkpoint run."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,zlib
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('checkpoint',type=Path);a=p.parse_args()
cp=a.checkpoint.resolve();summary=ROOT/f'build/verification/summary-{cp.name}.json'
d=json.loads(summary.read_text());out=cp/'validation';out.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert d['fixture_hashes_before']==d['fixture_hashes_after'] and not d['changed_fixtures']
assert all(sha(ROOT/n)==h for n,h in d['fixture_hashes_after'].items())
cases=[dict(c)for c in d['cases']]
for failure in d['failures']:
 m=re.fullmatch(r'(\S+) failed for (\S+)',failure);assert m,failure
 cases.append({'test':m[1],'rom':m[2],'result':'failed'})
assert len(cases)==761 and len({(c['rom'],c['test'])for c in cases})==761
for c in cases:
 rom=(ROOT/'build'if c['rom'].endswith('-baseline')else cp)/(c['rom']+'.nes')
 log=ROOT/'build/verification'/f"{c['rom']}-{c['test']}.log"
 raw=log.read_text();crc=re.search(r'File CRC32: 0x([0-9A-Fa-f]+)',raw)
 assert crc and int(crc[1],16)==zlib.crc32(rom.read_bytes()),(c,'Stale native log')
 if c['result']=='passed':assert 'PASS 'in raw and not re.search(r'\bFAIL\b|Lua error',raw),c
 dest=out/log.name;shutil.copyfile(log,dest)
 c.update(rom_sha256=sha(rom),log=dest.relative_to(ROOT).as_posix(),log_sha256=sha(dest))
 if c['result']=='failed':
  extra=out/'failed-artifacts';extra.mkdir(exist_ok=True)
  for q in log.parent.glob(f"{c['rom']}-{c['test']}*"):
   if q.is_file()and q!=log:shutil.copyfile(q,extra/q.name)
report={'result':d['result'],'single_full_run':True,'case_count':len(cases),
 'passed':sum(c['result']=='passed'for c in cases),'failed':sum(c['result']=='failed'for c in cases),
 'summary':summary.relative_to(ROOT).as_posix(),'summary_sha256':sha(summary),
 'roms':d['roms'],'fixtures_unchanged':True,'cases':cases,'script_sha256':sha(Path(__file__))}
(out/'bound-summary.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['result'],report['passed'],'passed',report['failed'],'failed',flush=True)
