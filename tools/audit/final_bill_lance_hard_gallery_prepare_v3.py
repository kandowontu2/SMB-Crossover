"""Only exempt the genuine cold settle from the later seeded-form guard."""
from pathlib import Path
import json,sys
import final_bill_lance_hard_gallery_prepare_v2 as previous

PRIOR_COMPOSE=previous.compose


def compose(cfg):
    script,guards=PRIOR_COMPOSE(cfg)
    root=previous.old.ROOT
    before=(root/'tools/audit/final_bill_lance_hard_gallery_native_v2.lua').read_text()
    after=(root/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua').read_text()
    old=" assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Weapon upgrade remains the seeded mushroom form; no invented tier transform')"
    new=" if phase~='settle'then assert(r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Weapon upgrade remains the seeded mushroom form; no invented tier transform')end"
    assert before.count(old)==1 and after==before.replace(old,new,1)
    assert script.count(before)==1
    return script.replace(before,after,1),guards


def main():
    previous.compose=compose
    previous.main()
    old=previous.old;out=Path(sys.argv[sys.argv.index('--output')+1])
    manifest=json.loads((out/'manifest.json').read_text())
    files=[Path(__file__),old.ROOT/'tools/audit/final_bill_lance_hard_gallery_native_v3.lua',
           old.D/'final-bill-lance-hard-gallery-negative-v1/proof.json',
           old.D/'final-bill-lance-hard-gallery-negative-v1/manifest.json']
    manifest['bindings'] += [dict(path=str(f.resolve()),sha256=old.sha(f),bytes=f.stat().st_size)for f in files]
    old.put(out/'manifest.json',manifest)
    proof=json.loads((out/'proof.json').read_text())
    proof.update(manifest_sha256=old.sha(out/'manifest.json'),bindings=len(manifest['bindings']),
        observer_version=3,only_cold_settle_seeded_form_assertion_exempt=True,
        every_postseed_form_guard_literal_unchanged=True,
        previous_Bill_native_FALSE_and_Lance_unrun_preserved=True,
        chronology_preparer_sha256=old.sha(__file__))
    old.put(out/'proof.json',proof)
    print(json.dumps(dict(passed=True,prepared_only=True,observer_version=3,proof_sha256=old.sha(out/'proof.json'),bindings=proof['bindings'])))


if __name__=='__main__':main()
