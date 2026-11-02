"""Exact current lifecycle/world/geometry backing and cold state placement."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prince_host_lifecycle_model_1102_v12 as C
import measure_prince_lzdict_1102_v9 as D
P,O=C.P,C.O


def main():
 h=C.World();runtime=bytes(h.m.ram[3][:0x1fdf]);state=bytearray(0x55f)
 coords=(O/'world-coordinates-v7.bin').read_bytes();state[0x50:0x150]=coords[:256];state[0x185:0x185+len(coords)-256]=coords[256:]
 blob=(O/'host-life-v12.bin').read_bytes();layout=json.loads((O/'host-life-layout-v12.json').read_text())
 for q in layout['regions']:
  at,end=q['half_open']
  if at>=0xc000:state[at-0xc0b0:end-0xc0b0]=blob[q['source_file_offset']:q['source_file_offset']+q['bytes']]
 (O/'host-runtime-v12.bin').write_bytes(runtime);(O/'host-state-code-v12.bin').write_bytes(state)
 src=Path(D.__file__);text=src.read_text()
 changes={"O/f'world-{name}-v8.bin'":"(O/'prince-pose-packets-v11.bin')if name=='metadata'else(O/f'host-{name.replace(\"_\",\"-\")}-v12.bin')","world-{name}-v9.lzdict":"host-{name}-v12.lzdict","world-codec-v9.json":"host-storage-v12.json"}
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 # Correct the wrapper's source evidence list; the frozen codec is reused,
 # while these current byte images supply its actual decoded payloads.
 text=text.replace("*[O/f'world-{n}-v8.bin'for n in ['runtime','state_code','metadata']]","O/'host-runtime-v12.bin',O/'host-state-code-v12.bin',O/'prince-pose-packets-v11.bin'")
 env=dict(__file__=str(src),__name__='prince_lifecycle_storage');exec(compile(text,str(src),'exec'),env);env['main']()
 file=O/'host-storage-v12.json';q=json.loads(file.read_text())
 # Run the actual60B RAM3 retirement/copy/clear/constructor, retaining no
 # initialized-source code until the decoder is safely out of that window.
 expected=bytes(h.s[:0x800]);meta=bytes(h.s[0x800:0x1d32]);h.s[:0x800]=bytes([0x9d])*0x800
 h.s[0x100:0x100+len(state)]=state
 c=h.source('PpHostColdFinalize');assert c.p&1 and bytes(h.s[:0x800])==expected
 assert bytes(h.s[0x800:0x1d32])==meta
 q.update(private_proposal_only=True,host_ROM_created=False,base_ROM_SHA256=C.PIN,world_state_image_live_half_open=[0xc0b0,0xc60f],world_state_image_cold_decode_half_open=[0xc100,0xc65f],actual_cold_finalizer_bytes=60,actual_cold_finalizer_CPU=c.processorCycles,cold_move_and_full_source_zero_constructor_exact=True,runtime_image_half_open=[0xa000,0xbfdf],runtime_remaining_before_header=1,sword_component_not_in_initial_unarmed_live_image=True,source_component_is_still_host_unbound=True,descriptor_and_remaining_callbacks_not_counted=True,fit_before_remaining_native_services=q['spare_42pages']>=0,scope='Actual249B lossless decoder for compiled original core/native point/render/world/lifecycle and408-pose compact geometry. State stream decodes above its live slot, actualRAM3 finalizer moves it down, erases all cold/live gaps and runs source-backed actor constructor. Audio/scene/death/combat/owner/auth/cold descriptor remain separate, so this is measured private backing fit, not a host-callable ROM.',wrapper_SHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 q['bindings'].update({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),Path(C.__file__),O/'host-runtime-v12.bin',O/'host-state-code-v12.bin',O/'host-life-v12.bin']})
 file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','rows']}))


if __name__=='__main__':main()
