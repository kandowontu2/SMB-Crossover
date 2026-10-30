"""Keep current source-linked loaders, FF items and joint speed work revertible."""
from pathlib import Path
import json
from checkpoint_roster_progress_1030_v2 import R,save,sha


def packets(items):
    allbindings={};reports=[]
    for name,d in items:
        p=R/name
        assert sha(p)==d,p
        h=json.loads(p.read_text());reports.append(h)
        for n,digest in h['bindings'].items():
            assert sha(n)==digest,n
            assert allbindings.get(n,digest)==digest,n
            allbindings[n]=digest
        allbindings[str(p.resolve())]=sha(p)
    allbindings[str(Path(__file__).resolve())]=sha(__file__)
    return reports,allbindings


if __name__=='__main__':
    hs,b=packets([
        ('build/final-fantasy-wram-host-v6/handoff.json','08261947cc24d941613a920302173f8071d506bd2b816df7753cd95501f9d83d'),
        ('build/final-fantasy-wram-host-v7/handoff.json','78d961e0b94018f86636a7768a14ceba55bd7a7b2ad4d09d0b288d3dac559e47'),
        ('build/final-fantasy-host-pickups-qualified-v1/handoff.json','db2e2d4fb28a7082836cc2611eb851107f2b8f36aa6a5c58728df55e7a99386d')])
    assert all(h['passed']and not h['native']for h in hs)
    loader=hs[1];pickup=hs[2]
    save('ff-real-loader-and-item-consumers',dict(
        status='PRIVATE_SOURCE_CPU_PASS_COMMON_CART_MAIN_ROUTES_PENDING',
        loader_ROM_sha256=loader['candidate_sha256'],
        loader_RAM3_sha256=loader['source_RAM3_sha256'],
        loader_ROM_bytes=loader['ROM_used'],loader_checks=loader['checks'],
        pickup_RAM3_sha256=pickup['image_sha256'],pickup_API=pickup['API'],
        pickup_counts=pickup['counts'],retained_negatives=pickup['retained_negatives'],
        limits=['Loaderv7 composes original source+combat492+terrain583. New399B pickup/body/freeze image is separately qualified and still needs loader payload/fingerprint successor; do not retagv7 as2ef76f0b.',
                'Original48ROM-only coldportraits and genuine forcedblank8KBcopy/verify are qualified; no private native/admission claim.',
                *pickup['remaining']]),b)
    hs,b=packets([
        ('build/character-host-union-rogue-dk-v3/handoff.json','136876b3114a0de6d147cf9bd519b261c7ac7d3f52552a57738804b761004d88'),
        ('build/character-host-union-rogue-fast-v4/handoff.json','e9f7f9defe6d8dfd5d112d50adb4f225ca29b6e3ac2ac88a27f1e1bf7f82a0c2'),
        ('build/character-host-union-rogue-fast-v5/handoff.json','e0ec049249a063e2dab07408efc8df457b935923e064956f6cf493cafc20ba83')])
    h=hs[2]
    save('joint-dk-rebase-and-foreign-dispatch',dict(
        status=h['status'],ROM_sha256=h['candidate_sha256'],checks=h['checks'],
        source_changes=[hs[0]['delta'],hs[1]['scope'],h['scope']],
        Bill_added_CPU_vs_required_RCR_parent=h['ordinary_Bill_CPU_delta_vs_required_RCR_parent'],
        Bill_source_CPU_savings_vs_initial_joint=h['ordinary_Bill_CPU_saving_vs_4154'],
        caller_dead_contract=h['caller_dead_contract'],capacity=h['capacity'],
        limits=[h['performance_blocker'],h['native_current_joint'],
                'DK original native07d5 flag-clear proof is retained, but current joint318f46f0 has source qualification only.',
                'No FF/Quick/Arthur admission or source union implied; standaloneArthurcommonA79 overlaps this joint.']),b)
    p=R/'docs/qa/host-integration-progress-2026-10-30.json';j=json.loads(p.read_text())
    j['root_completed_this_continuation'] += [
        'FF genuine forcedblank loader/coldportrait v6 and combat+terrain source-linked v7 qualified. v7ac0f0721 uses2128/3216ROMbytes, version2cookie, exactce4927338KBpayload;12loader/48coldportrait/120actual-loader-initializedhost-gatepairs/716hotvectors plus142coldISR/134maskedIRQ pass. No commonMainroutes or native admission.',
        'FF actual399B pickup/freeze/body/impulse source image2ef76f0b qualified:432progression/288star-life/720freezeupdates/288source-display/256body/256nativeX5impulse/96realdeferredscore-life/12three-tickfractioncases and2382realvectorcuts. No addedstate. Import-size and precise native BankPRGC pending-LDA observer negatives retained; product unchanged by observer repair. Loader composition is separate.',
        'Genuine DK22byte source rebase4154b52a preserves allotherROM/header/CHR and clears actual sourceMain→normalNMI→25underground. Typed foreign callback shortcuts plus inactiveZ2 wrapper flattening reduceBilladdedCPU735to600to463. Latest318f46f0 passes282foreignMain/12032callbacks/428Mainvectorcuts/960ownerMain; native cadence remains HOLD.'
    ]
    j['active_work']['Final_Fantasy']='Private loaderac0f0721 genuinely loads ce492733 combat+terrain. New399B pickup/body/freeze source2ef76f0b qualified separately and being source-composed with version3/fingerprint. Reset realcaller eventorder and arithmetic36service transport under source proof; allactualMainhooks/fullbody/OAM/palette/music/flashaging/nativeadmission pending.'
    j['active_work']['joint_resource_base']='Frozen source318f46f0 includes dedicated5FFF protocol, genuineDK22B flag fix and typed foreigndispatch optimizations;Bill+463CPU vs753parent remains HOLD. Next8B commonbegin-tail experiment source-only. HuEndBF93 leaves109B; no wholefreebank or implicit FF lease.'
    j['active_work']['Arthur']='Requiredblackink independentofShadows alreadytrue. Private09237b6f fair64recordpermutation/sourcebodyprefix qualified624Main/2748realvectors/104foreignMain0CPUdelta. Native400controller smoke in progress; meanadded1725CPU severe lag risk. StandaloneA79overlapwithjoint confirmed, no sharedinstallation or RAM1grant.'
    p.write_text(json.dumps(j,indent=2)+'\n')
