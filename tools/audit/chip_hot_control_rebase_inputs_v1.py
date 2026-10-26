"""Prepare precise four-file current-source overlay; never import held music files."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);f=D/'chip-hot-control-v5/freeze-v2';ready=f/'readiness-source-only.json';assert sha(ready)=='c92ef08c85b74e67af1e8c48b89b3ecaab2831c26a04f1d735298006ac632537';manifest=json.loads((f/'source-manifest.json').read_text());overlay=a.output/'overlay';files=[]
 current=ROOT/'build/smb-crossover-mmc5-expanded.nes';current_sha=sha(current);assert current_sha.startswith('6c69'),current_sha
 for row in manifest:
  rel=row['relative_path'];before=ROOT/rel;after=f/'new'/rel;assert sha(before)==row['before_sha256']and sha(after)==row['after_sha256'];q=overlay/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(after,q);files.append(dict(relative_path=rel,current_before_sha256=sha(before),candidate_after_sha256=sha(q)))
 cfg=ROOT/'smb1base-mmc5-expanded.cfg';shutil.copyfile(cfg,overlay/cfg.name)
 assert not(overlay/'src/entrypoint.s').exists()and not(overlay/'src/chip_native_music.s').exists()and not(overlay/'src/chip_native_adapter.s').exists()
 proof=dict(prepared=True,compiled=False,native_executed=False,production_mutated=False,current_reference_ROM_sha256=current_sha,source_readiness_sha256=sha(ready),files=files,config=dict(path=str(overlay/cfg.name),sha256=sha(cfg),changed=False),held8b4_music_dependency=False,reason='Optimization touches only character controller/collision dispatch. Source leaf CdMovement is already installed; no native-music adapter, old entrypoint/config, audio assets, new RAM or cold initialization required. Current four preimages match exactly. Copy current CFG unchanged only because build_mmc5_expanded requires it in overlay.',command_for_ROOT_after_freezing_current_inputs=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(ROOT),'--source-overlay',str(overlay),'--output',str(a.output/'candidate.nes')],scope='PREPARATION ONLY. Four intended changed raw files plus byte-identical current CFG. Every other current source/HUD/CV3/world-pad/music file comes from ROOT. ROOT must freeze current inputs, freshly compile and qualify the new current ROM hash before adoption. Existing ad925 source/CPU evidence remains bound to frozen8b4 parent.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
