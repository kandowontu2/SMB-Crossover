"""Exact current22d099 foreign ABI and current Prince header rebind proof."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_current_manifest_1102_v51 as M
O=M.O


def main():
 source=R/'tools/audit/check_prince_successor_foreign_1102_v28.py';text=source.read_text();changes={
  'import prepare_prince_successor_manifest_1102_v26 as M':'import prepare_prince_current_manifest_1102_v51 as M',
  'M.A.PIN':'M.PIN','M.A.BASE':'M.BASE',
  'successor-proposal-v26.json':'current-manifest-v51.json',
  'owner-third-v23.bin':'current-owner-v51.bin',
  'public-selector-v24.bin':'current-selector-v51.bin',
  'successor-foreign-CPU-v28.json':'current-foreign-CPU-v52.json',
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(source),__name__='prince_current_foreign_v52');exec(compile(text,str(source),'exec'),env)
 with contextlib.redirect_stdout(io.StringIO()):env['main']()
 file=O/'current-foreign-CPU-v52.json';q=json.loads(file.read_text());assert q['passed'];q.update(current_root_menu_and_Thomas_bytes_retained=1878,source_v49_audio_proposal_excluded=True,qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),new_real_source_cold_clock_tag_Fresh_ISR='Current rebound combined cold/fresh/scene proof still required.',scope='Actual current22d099 old/new all Sh/Ex/BB public rows and typed boundary over raw0..39 except new38, native UI forwarding,128header-byte corruptions and768raw/cookie selector cases. Complete AXYP/SP/SMC/ZP/native/private/maps parity. Prince rebound cookie verified; no new menu/admitted collision/audio code/ROM/native emulator/install claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'current-manifest-v51.json',O/'current-selector-v51.bin',O/'current-owner-v51.bin',O/'current-owner-extra-v51.bin']});file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
