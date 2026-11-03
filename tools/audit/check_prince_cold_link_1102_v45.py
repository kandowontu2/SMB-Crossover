"""Actual typed cold bootstrap/44-page/readback/constructor successor proof."""
from pathlib import Path
import contextlib,hashlib,io,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
import check_prince_native_link_1102_v43 as C
O=C.O


def main():
 base,_,_,_=M.bundle();C.H.W.PIN=M.A.PIN
 source=R/'tools/audit/check_prince_cold_worker_1102_v19.py';text=source.read_text();changes={
  "b=W.scoped_load(C.E.C.BASE)":"b=PROVIDED_BASE",
  '795,291]':'795,291,514]',
  'cold-pool-v19.bin':'cold-pool-v44.bin',
  'cold-worker-v19':'cold-worker-v44',
  'cold-decoder-v19':'cold-decoder-v25',
  'cold-worker-layout-v19.json':'cold-link-storage-v44.json',
  'native-runtime-v18.bin':'native-runtime-v42.bin',
  'native-metadata-v18.bin':'native-metadata-v42.bin',
  'expected=C.host(b)':'expected=HOST_SUCCESSOR(b)',
  'physical_spare=44032-len(payload)':'physical_spare=45056-len(payload)',
  'base_ROM_SHA256=C.E.C.PIN':'base_ROM_SHA256=SUCCESSOR_PIN',
  "C.E.C.BASE]":"SUCCESSOR_BASE]",
  "O/'cold-worker-CPU-v19.json'":"O/'cold-link-CPU-v45.json'",
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(__file__=str(source),__name__='prince_actual_cold_v45',PROVIDED_BASE=base,HOST_SUCCESSOR=C.host,SUCCESSOR_PIN=M.A.PIN,SUCCESSOR_BASE=M.A.BASE);exec(compile(text,str(source),'exec'),env)
 with contextlib.redirect_stdout(io.StringIO()):env['main']()
 file=O/'cold-link-CPU-v45.json';q=json.loads(file.read_text());assert q['passed'];q.update(private_proposal=True,new_live_execution_scope_granted=False,physical_pool_pages=44,typed_worker_source_table_includes514=True,metadata_phase_only_fragment=[0xc300,0xc800],live_metadata_end=0xdfa2,shared_clock_untouched=[0xdfd0,0xdfd3],source_constructor_floor_reference_initialized=True,qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),scope='Actual613b host/peripheral instructions execute private typed254B decoder/444B boot+worker over44granted carriers, three stream independent reread/readback, source-code finalizer and new NativeInit floor reference. Complete new live images/source-state match, guards/corruption fail closed. Resident manager operands/cookie/header lifetime, complete reader amendment and remaining native collision policies remain required; no ROM/native-emulator/menu/install claim.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'cold-link-storage-v44.json',O/'native-link-measurement-v42.json',O/'native-link-CPU-v43.json',O/'native-runtime-v42.bin',O/'native-metadata-v42.bin']});file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','physical_carriers','corruption_fail_closed']}))


if __name__=='__main__':main()
