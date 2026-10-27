"""Prepare only: replace the failed Av-index HUD admission with source-call ownership."""
from pathlib import Path
import json,sys
import final_bill_lance_combined_prepare_v2 as old
from final_bill_lance_combined_prepare_v2 import ROOT,D,PARENT,SHA,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

original_compose=old.compose


def compose(cfg):
    b=scoped_load(PARENT/'candidate.nes');assert sha(PARENT/'candidate.nes')==SHA
    h=location(b,'RemainingDraw::Hud');end=location(b,'RemainingDraw::Draw')
    helper=address(b,'BillHudAnchor');needle=bytes([0x20,helper&255,helper>>8])
    points=[i for i in range(h,end-2)if b['raw'][i:i+3]==needle];assert len(points)==1
    srcbank=(h-16)//8192;assert srcbank==61
    for n in ['RemainingDraw']:
        pos=location(b,n);cfg['hooks'][n]=dict(address=address(b,n),physical_bank=(pos-16)//8192,bytes=list(b['raw'][pos:pos+3]))
    cfg['hud_call_chain']=dict(helper_after=address(b,'RemainingDraw::Hud')+points[0]-h+3,
        pointer_after=address(b,'RemainingDraw::Draw')+6,source_bank=srcbank,
        render_return=address(b,'FarcallJmpTarget_SMC')+3,render_after=address(b,'RemainingDraw::Next'),render_sp_delta=-5,
        source_chain_bytes=list(b['raw'][points[0]:location(b,'RemainingDraw::Next')]),
        abi='Real JSR helper/ArtPointer at same SP; after pointer return farcall pushes two-byte outer return, one saved A-bank, two-byte SMC JSR return. Metasprite entry SP=pointer-return SP-5; stacked source bank61|128 and outer return $B922.')
    for item,record in cfg['hud_records'].items():record['art']=b['raw'][location(b,'RemainingDraw::PickupArts')+8+int(item)]
    script,guards=original_compose(cfg)
    before=(ROOT/'tools/audit/final_bill_lance_combined_hud_v1.lua').read_text()
    after=(ROOT/'tools/audit/final_bill_lance_combined_hud_v2.lua').read_text()
    assert script.count(before)==1
    return script.replace(before,after,1),guards


def main():
    old.compose=compose;old.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]);manifest=json.loads((output/'manifest.json').read_text())
    files={Path(z['path'])for z in manifest['bindings']}
    files.update([Path(__file__),ROOT/'tools/audit/final_bill_lance_combined_hud_v2.lua',
        D/'final-bill-lance-combined-ce635-first-false-v1/proof.json',D/'final-bill-lance-combined-ce635-first-false-v1/manifest.json'])
    put(output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=sha(f),bytes=f.stat().st_size)for f in sorted(files)]))
    proof=json.loads((output/'proof.json').read_text());proof.update(manifest_sha256=sha(output/'manifest.json'),bindings=len(files),
        HUD_observer_version=2,first_combined_machine_FALSE_retained=True,
        source_game_unchanged=True,corrected_scope='Actual helper/source return -> successful real ArtPointer -> immediate compiled farcall renderer stack/PC/bank; no Av-index-only ownership.',
        successor_preparer_sha256=sha(__file__))
    put(output/'proof.json',proof)
    print(json.dumps(dict(prepared_only=True,native_run=False,proof_sha256=sha(output/'proof.json'),bindings=len(files))))


if __name__=='__main__':main()
