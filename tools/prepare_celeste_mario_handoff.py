"""Seal only the owned Celeste leaf and exact finite CPU receipts."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    out=ROOT/'build/celeste-mario-module';rom=out/'candidate.nes'
    movement=json.loads((out/'source-controls.json').read_text())
    linked=json.loads((out/'linked-controls.json').read_text())
    build=json.loads((out/'link.json').read_text())
    digest=sha(rom)
    assert all(q['passed']and q['ROM_sha256']==digest for q in [movement,linked,build])
    assert all(sha(p)==h for p,h in build['inputs'].items()),'Rebuild before freeze: a link input changed'
    for proof in [movement,linked]:
        assert all(sha(q['path'])==q['sha256']for q in proof['bindings'])
    owned=[*sorted((ROOT/'src').glob('celeste_mario*')),
      *sorted((ROOT/'chr/characters').glob('celeste-mario*')),
      *sorted((ROOT/'tools').glob('prepare_celeste_mario*')),
      ROOT/'docs/qa/celeste-mario-source-controls-2026-10-28.txt',
      *[out/n for n in ['link.json','source-controls.json','linked-controls.json']]]
    refs=[rom,*[rom.with_suffix(s)for s in ['.dbg','.lbl','.map']],
      ROOT/'build/celeste-native-reference.nes',ROOT/'build/celeste-native-reference.lst',
      out/'sparse/src/entrypoint.s',out/'sparse/smb1base-mmc5-expanded.cfg']
    item=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=sha(p),bytes=p.stat().st_size)
    upstream=Path('C:/Users/kando/Documents/ChatGPT/SNES Ports/upstream-nes')
    native_inputs=[upstream/p for p in ['MG.65s','0000-07FF.65s','6000-7FFF.65s','Constants.65s',
      'src/Bank05_GameRoutines.65s','src/Bank07_BGEnemy02_Misc.65s','src/Bank08_BGEnemy03_Misc.65s',
      'src/BankA-1_BGEnemy0x_Misc.65s','src/BankN-2_IRQ.65s','IncBins/editor/generated/projectsettings.65s',
      'IncBins/editor/mg.chr','asm6.exe']]
    proof=dict(passed=True,native_run=False,ROM_sha256=digest,original_ROM_sha256=movement['original_ROM_sha256'],
      owned=[item(p)for p in owned],private_link_references=[item(p)for p in refs],
      native_reference_inputs=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)for p in native_inputs],
      counts=dict(core_bytes=linked['core_bytes'],core_capacity=4096,CHR_bytes=16384,
        movement_cases=len(movement['cases']),movement_updates=sum(q['updates']for q in movement['cases']),
        linked_rows=len(linked['rows']),art_records=len(linked['art']),interrupt_seams=len(linked['interrupts'])),
      integration='SelectedCharacter0/MarioVariant4; physical98 B000..BFFF, C98 data +2000; CHR740..755; no shared source edits.',
      source_build_scope='Genuine private sparse link includes ROOT concurrent roster integration. No claim of leaf-only delta against an older shared build.',
      unqualified=['Actual host dispatch and terrain/camera integration','Native PPU/deadline/cadence/crowding','Natural physical pickups and menu admission'])
    dest=out/'handoff-v1.json';dest.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,path=str(dest),sha256=sha(dest),counts=proof['counts'],owned=len(owned))))
if __name__=='__main__':main()
