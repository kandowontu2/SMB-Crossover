"""Reuse the proven exact unsupported-item UI leaf with the current fixes."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-item-side-pv/candidate-v2')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(BASE/'candidate.nes')=='b94aabbcdcb84484cd2f4cca7332e1d63c25e2dacd72740664b97f8e4aaa525f'
 s=a.output/'source';shutil.copytree(BASE/'source',s);f=s/'src/x5_bounce.s';v=f.read_text();old=' farcall InventoryUiTick,jmp\nLegacy:';assert v.count(old)==1;v=v.replace(old,' jmp X5NativeInventoryUiLeaf\n .res 15,$ea\nLegacy:')
 native=(s/'src/inventory.s').read_text();at=native.index('.proc InventoryUiTick\n');end=native.index('  jsr InventorySupported',at);leaf=native[at:end].replace('.proc InventoryUiTick','.proc X5NativeInventoryUiLeaf',1)
 leaf+='''  ldx SelectedCharacter
  clc
  lda InvHudActive
  beq Done
  lda #0
  sta InvHudActive
  inc ReloadCHRBank
  inc InvDirty
  lda #0
Done:rts
.endproc
'''
 v+='\n.pushseg\n.segment "X5_BOUNCE"\n'+leaf+'\n.popseg\n';f.write_text(v)
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
 (a.output/'preparation.json').write_text(json.dumps(dict(prepared=True,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),changed_source='src/x5_bounce.s',scope='Exact native unsupported-item UI leaf; lifecycle/hurt/input/stale-HUD semantics retained. No new RAM.'),indent=2)+'\n');print(sha(a.output/'candidate.nes'))
if __name__=='__main__':main()
