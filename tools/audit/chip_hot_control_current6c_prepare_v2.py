"""Compose only the qualified four-file delta on frozen current6c69 source."""
from pathlib import Path
import argparse,hashlib,json,shutil
from chip_hot_control_prepare_v4 import D,ROOT,sha,build
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);base=D/'world-firebar-padding-v2';expected='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a';assert sha(base/'candidate.nes')==expected;catalog=json.loads((base/'source-manifest.json').read_text());assert all(sha(base/'source'/n)==h for n,h in catalog.items());src=a.output/'source';shutil.copytree(base/'source',src);assert not(src/'src/chip_native_music.s').exists()and not(src/'src/chip_native_adapter.s').exists()
 build(src,a.output/'parent-rebuild.nes');assert sha(a.output/'parent-rebuild.nes')==expected
 prior=D/'chip-hot-control-v5/freeze-v2';manifest=json.loads((prior/'source-manifest.json').read_text());assert sha(prior/'readiness-source-only.json')=='c92ef08c85b74e67af1e8c48b89b3ecaab2831c26a04f1d735298006ac632537'
 for row in manifest:
  q=src/row['relative_path'];new=prior/'new'/row['relative_path'];assert sha(q)==row['before_sha256']and sha(new)==row['after_sha256'];shutil.copyfile(new,q)
 changed={n for n,h in catalog.items()if sha(src/n)!=h};assert changed==set(x['relative_path']for x in manifest)
 build(src,a.output/'candidate.nes');before=(a.output/'parent-rebuild.nes').read_bytes();after=(a.output/'candidate.nes').read_bytes();assert before[:16]==after[:16]and before[16+128*8192:]==after[16+128*8192:];diff={str(k):sum(x!=y for x,y in zip(before[16+k*8192:16+(k+1)*8192],after[16+k*8192:16+(k+1)*8192]))for k in range(128)};diff={k:v for k,v in diff.items()if v};assert diff=={'86':125,'89':23,'125':11,'126':32,'127':11}
 # Retain every byte of the accepted display timing/HUD fixes and all source
 # audio banks, rather than infer correspondence from the old donor hash.
 protected=['src/entrypoint.s','smb1base-mmc5-expanded.cfg','src/metasprite_engine.s','src/character_select.s','src/nmi_vram_fast.s','src/parodius_bells.s','src/parodius_hud_queue.s','src/parodius_render.s','src/reset.s','src/samus_freeze_render.s','src/screen_render.s','src/vic_adapter.s','src/roster_audio.s','src/cv3_source_audio.s','src/cv3_dmc_complete.s','src/cv3_remaining_source_fx.s']
 for rel in protected:assert(src/rel).read_bytes()==(base/'source'/rel).read_bytes(),rel
 proof=dict(prepared=True,native_executed=False,accepted=False,parent_ROM_sha256=expected,candidate_ROM_sha256=sha(a.output/'candidate.nes'),frozen_source_manifest_sha256=sha(base/'source-manifest.json'),frozen_manifest_files_checked=len(catalog),changed_source_files=sorted(changed),original_four_raw_source_afterimages_exact=True,held_Chip_music_imported=False,current_protected_source_files_exact=protected,changed_PRG_banks=diff,all_header_CHR_other_banks_exact=True,scope='Private current6c69 composition only. Fresh strict source/caller/IRQ/build checks required on this hash; prior ad925 native-free evidence is not relabelled.',tool_sha256=sha(__file__))
 (a.output/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
