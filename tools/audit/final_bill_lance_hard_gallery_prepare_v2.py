"""Versioned real advanced-AvSlot observer successor; preserves old readiness."""
from pathlib import Path
import json,sys
import final_bill_lance_hard_gallery_prepare_v1 as old

ORIGINAL_COMPOSE=old.compose
B=None


def compose(cfg):
    global B
    if B is None:B=old.scoped_load(old.PARENT/'candidate.nes')
    pos=old.location(B,'RemainingDraw::Draw');at=old.address(B,'RemainingDraw::Draw')
    assert B['raw'][pos:pos+6]==bytes([0xad,old.address(B,'AvDrawArt')&255,old.address(B,'AvDrawArt')>>8,0x20,old.address(B,'RemainingDraw::ArtPointer')&255,old.address(B,'RemainingDraw::ArtPointer')>>8])
    cfg['advanced_after_pointer']=dict(pc=at+6,bank=(pos-16)//8192,bytes=list(B['raw'][pos:pos+12]))
    cfg['advanced_art_indices']=list(B['raw'][old.location(B,'BillAdvancedDrawArt::Arts'):old.location(B,'BillAdvancedDrawArt::Arts')+9])
    records={}
    for i in cfg['advanced_art_indices']:
        ptr=B['raw'][old.location(B,'AvArtRightLo')+i]+256*B['raw'][old.location(B,'AvArtRightHi')+i]
        bank=B['raw'][old.location(B,'AvArtBanks')+i]&127
        records[str(i)]=cfg['effect_records'][str(bank)+':'+str(ptr)]
    cfg['advanced_records']=records
    script,guards=ORIGINAL_COMPOSE(cfg)
    before=(old.ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v1.lua').read_text()
    after=(old.ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua').read_text()
    assert script.count(before)==1
    return script.replace(before,after,1),guards


def main():
    old.compose=compose
    old.main()
    out=Path(sys.argv[sys.argv.index('--output')+1])
    manifest=json.loads((out/'manifest.json').read_text())
    files=[Path(__file__),old.ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua',
           old.D/'final-bill-lance-hard-gallery-ready-v3/proof.json',
           old.D/'final-bill-lance-hard-gallery-ready-v3/manifest.json']
    for draft in ['final-bill-lance-hard-gallery-ready-v1','final-bill-lance-hard-gallery-ready-v2']:
        files.extend(f for f in(old.D/draft).iterdir()if f.is_file())
    manifest['bindings'] += [dict(path=str(f.resolve()),sha256=old.sha(f),bytes=f.stat().st_size)for f in files]
    old.put(out/'manifest.json',manifest)
    proof=json.loads((out/'proof.json').read_text())
    proof.update(manifest_sha256=old.sha(out/'manifest.json'),bindings=len(manifest['bindings']),
        observer_version=2,observer_correction='Legacy RgSlot versus qualified advanced AvSlot; actual source art and ArtPointer-success return; cleanup registered before any reject at genuine render return.',
        unchanged_mechanics_controller_guards_caps=True,prior_unrun_observer_bug_retained=True,
        successor_preparer_sha256=old.sha(__file__))
    old.put(out/'proof.json',proof)
    print(json.dumps(dict(passed=True,prepared_only=True,observer_version=2,proof_sha256=old.sha(out/'proof.json'),bindings=proof['bindings'])))


if __name__=='__main__':main()
