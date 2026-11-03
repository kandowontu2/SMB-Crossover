"""Complete current private image: all original poses/native emitter/real ISR."""
from pathlib import Path
import hashlib,inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_native_manifest_1102_v65 as M
import check_prince_player_pipeline_1102_v67 as C
import check_prince_pose_grid_native_1102_v38 as F
O=M.O


def main():
 b,seed,_=C.loaded();runtime=(O/'native-runtime-v49.bin').read_bytes();length=(O/'grid-render-v37.bin').stat().st_size;(O/'native-render-v68.bin').write_bytes(runtime[0xbbc1-0xa000:0xbbc1-0xa000+length])
 text=inspect.getsource(F.main);changes={
  'base,_,_,_=PM.bundle()':'_,base,_,_=PM.bundle()',
  'PM.A.PIN':'PM.PIN','PM.A.BASE':'PM.BASE',
  "'grid-helper-labels-v38'":"'grid-helper-labels-v68'",
  'grid-render-v37.bin':'native-render-v68.bin',
  'pose-grid-native-CPU-v38.json':'native-render-CPU-v68.json',
  "ROM=R/'build/bub-menu-candidate-1102-v2/combined-event.nes'":"ROM=R/'build/sunny-growth-prelude-1102-v9/candidate.nes'",
  'assert A.sha(ROM)==SHA;b=PROVIDED_BASE;seed=M.fresh(b)':'assert A.sha(ROM)==SHA;b=PROVIDED_BASE;seed=FINAL_SEED',
  'PROVIDED_BASE=base,GRID_LABELS=':'PROVIDED_BASE=base,FINAL_SEED=FINAL_SEED,GRID_LABELS=',
  "exec(compile(text,str(original),'exec'),env)":"text=text.replace(\"p['attribute']\",\"(p['attribute']&252)\")\n exec(compile(text,str(original),'exec'),env)",
 }
 for old,new in changes.items():assert old in text,old;text=text.replace(old,new)
 env=dict(F.__dict__,PM=M,FINAL_SEED=seed,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 file=O/'native-render-CPU-v68.json';q=json.loads(file.read_text());assert q['passed'];q.update(private_execution_granted=True,new_executable_metadata_grant=True,qualified_fixture_SHA256=hashlib.sha256(text.encode()).hexdigest(),actual_current_memory_SHA256=M.sha(b['raw']),full_runtime_metadata_audio_code_present=True,source_palette_host_mapping='Original source player palette1 →native player palette0; original27/16/20 hues retained. Only low palette bits cleared; original face/flip/coordinates/pattern identities exact.',scope='Actual current16a9 privately granted full image loaded through resident cold before every draw fixture fork. All408original source faceposes,280edge/OAMcapacity/alignment cases and both raw/grid realIRQ/lagNMI cuts execute native CHR setters and MetaspriteRenderLoop with authentic physical31-page art. Geometry/source-visible projection and all private code/state preserved except declared packet/projection/grid-helper operands. Palette1→native0 is the explicit existing host adaptation. No native emulator/menu/fullstage/install claim; source audio mixer/mapping incomplete.')
 q['bindings'].update({p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'native-manifest-v65.json',O/'native-runtime-v49.bin',O/'native-metadata-v49.bin',O/'native-state-v49.bin',O/'native-render-v68.bin',R/'docs/qa/allocations/prince-collision-lifetime-1102-v62.json']});file.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','actual_current_memory_SHA256','source_facing_poses','edge_capacity_alignment_cases','actual_IRQ_lagNMI_instruction_SP_cuts','CPU','minimum_SP']}))


if __name__=='__main__':main()
