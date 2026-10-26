"""Small Git-review payload for unadopted source-only64ccd, no media/ROM copy."""
from pathlib import Path
import argparse,json,shutil
from smb3_host_current3b_cpu_v1 import D,R,sha,put

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True);assert not (a.output/'manifest.json').exists();packet=D/'smb3-host-hot6-v2';ready=packet/'source-freeze-v1/readiness.json';assert sha(ready)=='1aef9bc708b4f8b55dece8efd069177660b1a4d97c85a9a515080765ce5fb939'
 payload={
 'source-readiness.json':ready,'implementation.patch':packet/'source-freeze-v1/implementation.patch',
 'source-overlay/src/smb3_native_standalone.s':packet/'source/src/smb3_native_standalone.s',
 'receipts/preparation.json':packet/'preparation.json','receipts/layout.json':packet/'layout.json',
 'receipts/reader-controls.json':packet/'reader-controls-v2/proof.json','receipts/role-lifecycle-controls.json':packet/'controls-v1/proof.json',
 'receipts/IRQ-and-completion-controls.json':packet/'boundaries-v1/proof.json','receipts/paired768-whole.json':packet/'whole-v1/proof.json',
 'receipts/reader-profile.json':packet/'profile-v1/proof.json','receipts/canonical-and-flagoffs.json':packet/'build-controls-v1/proof.json',
 'negative-drafts/initial-site-count.json':D/'smb3-host-hot6-v1/failure.json','negative-drafts/initial-flat-bus-oracle.json':packet/'reader-controls-v1/failure.json',
 'separate-unallocated-cache/finite-ownership-probe.json':D/'smb3-host-cache-ownership-v1/proof.json',
 'preceding-profile/proof.json':D/'smb3-host-reader-profile-v2/proof.json','preceding-profile/freeze.json':D/'smb3-host-reader-profile-v2/freeze.json',
 'reports/smb3-host-reader-profile-2026-10-26.txt':R/'docs/qa/smb3-host-reader-profile-2026-10-26.txt',
 'reports/smb3-host-hot6-source-2026-10-26.txt':R/'docs/qa/smb3-host-hot6-source-2026-10-26.txt'}
 rows=[]
 for name,source in payload.items():
  target=a.output/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target) if not target.exists() else None;assert sha(target)==sha(source);rows.append(dict(path=name,source=str(source).replace('\\','/'),sha256=sha(source),bytes=source.stat().st_size))
 owned=['tools/audit/'+n for n in ['smb3_host_reader_profile_v1.py','smb3_host_reader_profile_v2.py','smb3_host_cache_ownership_v1.py','smb3_host_hot6_prepare_v1.py','smb3_host_hot6_prepare_v2.py','smb3_host_hot6_controls_v1.py','smb3_host_hot6_controls_v2.py','smb3_host_hot6_whole_v1.py','smb3_host_hot6_profile_v1.py','smb3_host_hot6_build_v1.py','smb3_host_hot6_freeze_v1.py','smb3_host_hot6_checkpoint_v1.py','smb3_host_hot6_checkpoint_v2.py']]+['docs/qa/smb3-host-reader-profile-2026-10-26.txt','docs/qa/smb3-host-hot6-source-2026-10-26.txt']
 ownedrows=[dict(path=n,sha256=sha(R/n),bytes=(R/n).stat().st_size)for n in owned]
 (a.output/'OWNED-FILES.txt').write_text('\n'.join(owned)+'\n'+str(a.output.relative_to(R)).replace('\\','/')+'/\n',encoding='utf-8')
 text='''SOURCE-ONLY / HELD PARTIAL MUSIC OPTIMIZATION. No native run or adoption.
Production3b stays unchanged. Parent7469 remains rejected for98actual lost
draws. Private64ccd changes one source file:13 authentic fixed-page readers
plus A86 return bridge, no RAM/cache/assets/CHR/sample/tick/event changes.
Paired768CPU calls preserve declared state and ordered hardware stores;
767steady calls save184..1102cycles, mean225.327. Native cadence is unproved.
Actual source return hook is now a genuine C38 bridge; E70/97/127 guards stay.
Read reports before interpreting adapter scratch7B0B/7B0C exceptions.
Draft site-count and flat-IO-oracle failures remain unchanged. Cache probe is
finite and UNALLOCATED, not a completed cache ownership/budget qualification.
External source/binary/original-NSF evidence is hash-bound but not duplicated.
This checkpoint contains no ROM, NSF, DMC, settings or captured media payload.
OWNED-FILES lists stable new tools/reports for ROOT's separate Git review.
No current mixer exploration tools are included or frozen by this packet.
'''
 (a.output/'README.txt').write_text(text,encoding='utf-8')
 put(a.output/'manifest.json',dict(source_only=True,native_run=False,native_ready=False,adopted=False,parent_held_ROM_sha256='7469d9f62af3161c896b844546ead66002bb425ba8b5143692b1c2ae1d9f1219',candidate_ROM_sha256='64ccd5038c26cabd3c57c4c3ed13b1fe467b275238610f3a227ceaa48e1ac2b6',source_readiness_sha256=sha(ready),payloads=rows,stable_owned_files=ownedrows,checker_sha256=sha(__file__),external_reproduction_limit='Requires pinned local original source/NSF and frozen parent7469/current3b evidence listed in source-readiness; those binary payloads are intentionally excluded.'))
 total=sum(q.stat().st_size for q in a.output.rglob('*')if q.is_file());print(json.dumps(dict(passed=True,files=len([q for q in a.output.rglob('*')if q.is_file()]),bytes=total,manifest_sha256=sha(a.output/'manifest.json'),owned_files=len(owned))))
if __name__=='__main__':main()
