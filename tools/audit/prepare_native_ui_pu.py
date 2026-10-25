"""Inline the exact unsupported legacy-UI leaf for native item owners."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v3')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    assert sha(BASE/'candidate.nes')=='ad021817f1cd67683e52c2895e85bb5932c91cea9f53434768e85dca3b631ec7'
    source=a.output/'source';shutil.copytree(BASE/'source',source)
    path=source/'src/x5_bounce.s';old=path.read_text();anchor=' farcall InventoryUiTick,jmp\nLegacy:'
    assert old.count(anchor)==1
    text=old.replace(anchor,' jmp X5NativeInventoryUiLeaf\n .res 15,$ea ; retain the original18-byte tail-call span\nLegacy:')
    native=(source/'src/inventory.s').read_text();at=native.index('.proc InventoryUiTick\n');end=native.index('  jsr InventorySupported',at)
    leaf=native[at:end].replace('.proc InventoryUiTick','.proc X5NativeInventoryUiLeaf',1)
    leaf+='''  ; The admitted native item owners always return unsupported, with
  ; X=ID and C=0. The legacy UI then only clears a stale legacy overlay.
  ldx SelectedCharacter
  clc
  lda InvHudActive
  beq Done
  lda #0
  sta InvHudActive
  inc ReloadCHRBank
  inc InvDirty
  lda #0                       ; old farcall return reloads A and its N/Z
Done:
  rts
.endproc
'''
    text+='\n.pushseg\n.segment "X5_BOUNCE"\n'+leaf+'\n.popseg\n';path.write_text(text)
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
      '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=source,capture_output=True,text=True)
    (a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2000:]
    q=dict(prepared=True,accepted=False,goal_complete=False,parent_ROM_sha256=sha(BASE/'candidate.nes'),ROM_sha256=sha(a.output/'candidate.nes'),
      changed_source='src/x5_bounce.s',source_before=sha(BASE/'source/src/x5_bounce.s'),source_after=sha(path),
      scope='Exact existing hurt/input-history and unsupported HUD cleanup, only the five already admitted native-item owners. No new RAM or inventory semantics; native equivalence/performance acceptance pending.')
    (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(q['ROM_sha256'],flush=True)
if __name__=='__main__':main()
