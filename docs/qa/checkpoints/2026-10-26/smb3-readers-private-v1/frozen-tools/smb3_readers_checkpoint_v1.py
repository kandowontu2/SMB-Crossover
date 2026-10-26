"""Small Git-review packet of unused SMB3 reader work; no source installation."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
O=D/'smb3-native-readers-opt-v2';Q=D/'smb3-music-current641-review-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert out.is_relative_to(R/'docs/qa/checkpoints');out.mkdir(parents=True,exist_ok=False)
 verified=0
 for folder,wanted in [(O/'final-readiness-v1','43f985cfaf22b9c416cbd2d9fe85ef92ae3848a33bdff5a0ed8ea2aac18c13f0'),(Q/'final-readiness-v1','639aa864534af2e7e80ac159bc2014a73dc7aca3d6fcac7541fbfeb3d1bfaf96')]:
  assert sha(folder/'readiness.json')==wanted
  for row in json.loads((folder/'bindings.json').read_text()):assert sha(row['path'])==row['sha256']and Path(row['path']).stat().st_size==row['bytes'],row['path'];verified+=1
 entries=[]
 def copy(src,dest,role):
  src=Path(src);dst=out/dest;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(src,dst);assert sha(src)==sha(dst)
  entries.append(dict(path=dest,bytes=dst.stat().st_size,sha256=sha(dst),original_path=str(src).replace('\\','/'),role=role))
 for report in ['smb3-native-readers-opt-2026-10-26.txt','smb3-music-current641-readonly-2026-10-26.txt']:copy(R/'docs/qa'/report,'reports/'+report,'bounded source/CPU recommendation')
 copy(O/'source/src/smb3_native_standalone.s','source-overlay/src/smb3_native_standalone.s','exact one-file private overlay; NOT a production overlay')
 for name in ['proof.json','source-delta.json','source-manifest.json','known-sites.json','build-command.json','candidate.build.json']:
  copy(O/name,'optimized/'+name,'optimized private source/bank/cost accounting')
 for name in ['readiness.json','bindings.json','implementation.patch']:copy(O/'final-readiness-v1'/name,'optimized/final-readiness/'+name,'original exact frozen source receipt/delta')
 for name in ['pilot-normal256-v1','reader-controls-v1','full-call-recurrences-v1','ordinary-controls-v1']:
  copy(O/name/'proof.json','optimized/'+name+'/proof.json','finite exact candidate controls; no native claim')
 for name in ['proof.json','actual-current-routes.json','current-layout-and-clones.json']:copy(Q/name,'current641-3b-readonly/'+name,'actual current route and stale-clone findings; no integration')
 for name in ['readiness.json','bindings.json']:copy(Q/'final-readiness-v1'/name,'current641-3b-readonly/final-readiness/'+name,'original74binding read-only receipt')
 copy(D/'smb3-native-readers-opt-v1/failure.json','retained-negatives/preparer-v1-failure.json','same-e578 initial bank-catalog failure before CPU')
 for name in ['smb3_music_current641_readonly_v1.py','smb3_native_readers_opt_prepare_v1.py','smb3_native_readers_opt_prepare_v2.py','smb3_native_readers_opt_controls_v1.py','smb3_native_readers_opt_calls_v1.py','smb3_native_core_cpu_v3.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','verify_native_relocation.py']:
  copy(R/'tools/audit'/name,'frozen-tools/'+name,'exact audit/CPU/reproduction tool')
 for name in ['build_mmc5_expanded.py','prepare_cv3_dmc_mirror.py']:copy(R/'tools'/name,'frozen-tools/'+name,'bound builder/producer source; runtime/assets external')
 copy(Path(__file__),'frozen-tools/'+Path(__file__).name,'checkpoint producer')
 readme='''SMB3 reader optimization: private, uninstalled source/CPU component

Unused parent a4be8e02de0f8c0c43e5a7c94e4719e8b62c2ae80c1b1769978b06e73f2cac98.
Optimized e578d0de91b0613ccfd6907467109c7c30dabd3fa69dcbefb4fe68c4ed4e2eff.
Current route observations apply only to641460e2...eb512c and private3b112e1d...a66287.
Neither current ROM contains this optimization or authentic SMB3 music integration.

Read review-files.json first. The two reports distinguish current Pit fallback,
authentic unused source, measured generic-reader costs, and the private change.
The overlay is the EXACT changed CRLF standalone file, not a safe current-tree
overlay. implementation.patch is its one-file delta against OLD unused a4be.
No live AudioUpdate hook, source RAM relocation, new RAM or native run exists.

Candidate results:18624 paired reader cases;10085 complete calls per ROM over
twelve first-source-recurrence roles;61695 ordered original APU stores and365
sample-request byte checks per ROM. Source state/AXYP/SP/maps/order/bytes exact.
Mean2339.74->1538.29 cycles (-34.25%); normal peak12552->7229. Remaining indirect
and host integration costs are unqualified; no native lag/waveform claim.
Ordinary MMC3 d444... and MMC5 f4ffd... remain exact, full hashes in receipts.

The initial v1 structural oracle omitted four INTENDED cold-site changes in86.
It failed before CPU checks; its SAME e578 compiled bytes are retained externally.
The corrected v2 permits38 plus those16bytes86. No game failure was erased.

CRITICAL REBASE WARNING: old70/97 clones each differ from current fixed127 in
949bytes OUTSIDE sample data. Never copy them into current. Future integration
must rebase the intended source/data declarations onto the eventual ADOPTED
current3b-derived source, then regenerate BOTH E clones from its FINAL127 and
overlay only declared samples, preserving current post-DMA/interrupt repairs.
BankPRGA only writes5115: CurrentBank is a foreground SHADOW, not a readable
hardware bank. The old fixture sets both A and shadow86; a future A lease must
preserve that host shadow and explicitly restore hardware ownership, not assume
the fixture's equality holds during temporary source-page mapping.

No raw NSF/NSFE/DMC/ROM/emulator/assets/captures/settings or full-source archive
is included. Hash catalogs name external files but do not contain their bytes.
Full reproduction requires the pinned external old a4be source+ROM/debug,
authentic original source traces/assets and compiler/CPU runtime; this compact
packet alone cannot build or replay those inputs. Frozen tools remain byte-exact
copies of repository tools; run them from tools/audit with original imports and
external paths, not from this rearranged review directory.

This checkpoint preserves private work for review/rollback. It installs nothing,
does not grant native execution, and does not transfer historical216012call or
current3b/native evidence to the optimized candidate.
'''
 (out/'README.txt').write_text(readme,encoding='utf-8')
 put(out/'review-files.json',dict(first='README.txt',primary=['reports/smb3-native-readers-opt-2026-10-26.txt','reports/smb3-music-current641-readonly-2026-10-26.txt'],implementation=['source-overlay/src/smb3_native_standalone.s','optimized/final-readiness/implementation.patch','optimized/source-delta.json'],candidate_controls=['optimized/proof.json','optimized/reader-controls-v1/proof.json','optimized/full-call-recurrences-v1/proof.json','optimized/ordinary-controls-v1/proof.json'],current_dispatch_clone_and_shadow=['current641-3b-readonly/proof.json','current641-3b-readonly/actual-current-routes.json','current641-3b-readonly/current-layout-and-clones.json'],retained_failure='retained-negatives/preparer-v1-failure.json',external_reproduction_limits='README.txt',not_current_or_native_evidence=True))
 for name in ['README.txt','review-files.json']:entries.append(dict(path=name,bytes=(out/name).stat().st_size,sha256=sha(out/name),role='checkpoint scope/review navigation'))
 put(out/'manifest.json',entries)
 result=dict(status='GIT_READY_PRIVATE_SOURCE_CPU_CHECKPOINT',installed=False,native_run=False,original_parent='a4be8e02de0f8c0c43e5a7c94e4719e8b62c2ae80c1b1769978b06e73f2cac98',optimized='e578d0de91b0613ccfd6907467109c7c30dabd3fa69dcbefb4fe68c4ed4e2eff',verified_original_bindings=verified,payload_files=len(entries),payload_bytes=sum(q['bytes']for q in entries),manifest_sha256=sha(out/'manifest.json'),review_files_sha256=sha(out/'review-files.json'),no_raw_assets_or_media=True,rebase_current_and_regenerate_E_clones_required=True)
 put(out/'checkpoint.json',result);assert all(sha(out/e['path'])==e['sha256']for e in entries);print(json.dumps(dict(result,checkpoint_sha256=sha(out/'checkpoint.json'),total_files=len(list(out.rglob('*'))),directory_bytes=sum(q.stat().st_size for q in out.rglob('*')if q.is_file())),indent=2))
if __name__=='__main__':main()
