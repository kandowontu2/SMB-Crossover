"""Compact combined source/cost/cold/foreign/hot milestone, no admission."""
import json
import zipfile
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R,O=A.R,A.O


def main():
    names=['measure_dkjr_prince_owner_1103_v101.py','check_dkjr_prince_cold_1103_v102.py',
        'audit_dkjr_prince_transition_1103_v103.py','check_dkjr_prince_cold_1103_v104.py',
        'check_dkjr_prince_foreign_1103_v105.py','check_dkjr_prince_hot_irq_1103_v106.py',
        'audit_dkjr_combined_padding_1103_v108.py',Path(__file__).name]
    sources=[R/'tools/audit'/n for n in names]
    receipts=['native-combined-owner-v101-measurement.json','native-combined-cold-v102-negative.json',
        'native-combined-transition-v103-diagnostic.json','native-combined-cold-v104-CPU.json',
        'native-combined-foreign-v105-CPU.json','native-combined-hot-v106-direct.json',
        'native-combined-hot-v106-nested.json','native-combined-padding-v108.json']
    for name in receipts:
        q=json.loads((O/name).read_text());assert bool(q['passed'])==('negative'not in name),name
        for rel,digest in q.get('bindings',{}).items():assert A.sha((R/rel).read_bytes())==digest,('stale',name,rel)
    generated=[O/n for n in receipts]
    for stem in ['native-combined-owner-v101','native-combined-selector-v101','native-combined-owner-v108']:
        generated += [O/f'{stem}.{ext}'for ext in ['s','cfg','bin','lbl']]
    generated += [O/'native-combined-extra-v101.bin',O/'native-combined-extra-v108.bin']
    archive=O/'native-combined-fit-v109-inputs.zip';members=[]
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(set(sources+generated)):
            rel,data=p.relative_to(R).as_posix(),p.read_bytes();z.writestr(rel,data)
            members.append(dict(path=rel,bytes=len(data),SHA256=A.sha(data)))
    proposal=json.loads((O/'native-combined-owner-v101-measurement.json').read_text())
    pad=json.loads((O/'native-combined-padding-v108.json').read_text())
    direct=json.loads((O/'native-combined-hot-v106-direct.json').read_text())
    nested=json.loads((O/'native-combined-hot-v106-nested.json').read_text())
    out=dict(passed=True,status='FROZEN_COMBINED159_DK90_SOURCE_FIT_COLD_FOREIGN_HOT',qualified=False,
        ROM_written=False,installed=False,native_owner_admitted=False,shared_resident_grant=False,menu_grant=False,
        archive=archive.relative_to(R).as_posix(),archive_bytes=archive.stat().st_size,archive_SHA256=A.sha(archive.read_bytes()),
        members=members,source_files=[dict(path=p.relative_to(R).as_posix(),SHA256=A.sha(p.read_bytes()))for p in sources],
        historical_canonical_Prince159_memory_SHA256=proposal['parent_memory_SHA256'],memory_only_SHA256=proposal['expected_memory_only_SHA256'],
        cookies={k:proposal[k]for k in ['Prince_cookie','Bub_cookie','DK_cookie']},
        resident=dict(manager_extent=[0xae00,0xb013],manager_file_bytes=531,extra_used=[0xab72,0xabd1],extra_lease_end=0xabd4,selector_used=[0xa740,0xa7f0],selector_lease_end=0xa7f2,
            new_source_generated_footer=[0xb002,0xb013],new_footer_bytes=17,foreign_UI_table=0xa7da,
            note='531 is padded filelength, not zero source-created spare.108 identicallabelonly assembly exposes footeraftercookies. No extraallocation assumed; externalreaderclosure/rootgrant stillneeded.'),
        evidence=[
            '101 fits canonicalinprogressPrince159+unchangedDK90typedpayload into existing531/98/178extents using source-backed genericfour-ownerretire/localreject/cold/header factoring; no sharedSh73B rewrite/cache/performanceclaim. PrinceC766installer incomingAdead store removed; exact38/40guard runs onlyPrince liveinstall.',
            '104 all4actualcold/16orderedtransitions/128individualheaderpoisons. DK8192code except16headercommit+2048metadata+2304zero exact; Prince53B BFA3liveinstalled/readback/C200zero/C766retained. Existing37/38/39 standalonecold completeprivateimages/maps exactcanonical159.',
            '102 retainedwholeRAMtailoracle:103locates36bytes outsidePrinceDFCCdecodedmetadata and outsidebothheaders; oldEx32pageclear gives0versusstandalone9D.104tests allnewowner exactcopied/initializedextents and fullheaders, explicitlyretains sharedclock exceptunchangedEx32pageclear.',
            '105 actualSh36A87Floader and37/38/39fullcold/Fresh;1216positivepublic comparisons cover37legacyrows+virtual37B029/twoCwindows/fourflags.5020inertrejectpairs cover251otherraws. Fullprivate/native/ZP/liveSMC/liveStack/maps/PPU/AXYP/SP parity; actualB0FBunchanged.',
            '106 completeCoCheckCode/selection/headercompare plusprivateAnchor/FullBox/ScoreFlush:417IRQ+417genuineFFlagNMI+4044independentnestedIRQ, minSP133/128. All reachedhotI1positionsincluded;count0. Full source/private/native/SMC/maps/foreground parity withonlybound outeraudio clocks.',
            '108 byteidenticallabelonly reassembly provesnewB002..B01317EAfooter. Eight compiledresidentroots/320instructions cannotfetch/readfooter; twoSMCindexedaliases X0..4/twoR5cookieoperationsY0..15staybelowit. Completeexternalcaller/sourceproducerclosure remainsseparate.',
        ],
        interrupts=dict(direct=direct['actual_interrupts'],nested=nested['actual_interrupts'],minimum_direct_SP=direct['minimum_ISR_SP'],minimum_nested_SP=nested['minimum_ISR_SP']),
        immutable_private_component=dict(manifest='build/dkjr-native-source-1102-v2/native-entrance-ready-v100.json',archive_SHA256='1811bf5bd1a0224d004f8856487b1d42c6181f41b84764e5116075517d321cb5',body8160=True,metadata_end=0xd7fc),
        external_direct_inputs=dict(Prince_manifest='build/prince-actor-1101-v1/backdrop-manifest-v159.json',SHA256=A.sha((R/'build/prince-actor-1101-v1/backdrop-manifest-v159.json').read_bytes()),
            source_files=['build/prince-actor-1101-v1/post-owner-v159.s','build/prince-actor-1101-v1/post-selector-v153.s','build/prince-actor-1101-v1/native-installer-v153.s'],
            scope='Other-agent read-only inprogresscostinput, not copied/staged or treatedasfinalnativecanonical here.159 laterpalette/name/IRQ/newgroundgeometry proofs are independentlyowned; thisfreeze doesnotadmitPrince or claimitsnativebugsresolved. Finalrebindmustuse itsstablecookie/payload/grant.'),
        remaining=[
            'FinalstablePrince/currentBubsource rebind; no-cachefullauthperformance factor is ownedbyexcitebike and mustbe jointlyplaced withoutdouble-spending structuralbytes/newfooter.101unchangedpendingreview.',
            'Exactexternalcaller/literal/ABI/finiteproducerclosure for changedCoCheckCode/CoSmc/cookie/tableaddresses andbefore-overwrite seam; coldcopy/readback/headercommit/guardedPrCopyLive actualFF/IRQ/lifetime proofs beyondhot106.',
            'PopulatedDKpause/Bubtraps/Princelifecycle/foreignretirement onfinalcombinedmanager, actualsource/nativeMain/entrance/HP/items/death/respawn/scene/hardwarepalette/OAM/cadence requalification.',
            'Native scene gate still37..39; raw40 sceneadmission/owningfocusedDK28↔Jr40 menuSelect/Start/name/sharedDKportrait/pending/lifepersistence exactproofandrootgrant beforeanyNES. No nativeSfx/ISRnewraw exemption assumed.',
            'RootownsMesenqueue/install/Git. Source15px jump stillrequires intendedvine/nativehelperstageproposal andassisted1-1verification; nohelpers/authoredfruit/vinesplaced here.',
        ],scope='Compactprivate combinedsource/costandaggregateCPU milestone only. No cartridge, DBG/object/captureforest, sharedfilemutation, nativeemulator/menuadmission, installation orcommit. Rootmaycopy ZIP/manifestandexplicit8ownsourcefiles; preserve all frozeninputs unchanged.')
    (O/'native-combined-fit-v109.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','status','archive_bytes','archive_SHA256','memory_only_SHA256','resident','interrupts']}))


if __name__=='__main__':main()
