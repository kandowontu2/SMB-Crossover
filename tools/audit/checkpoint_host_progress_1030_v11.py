"""Save genuine new family source composition, renderer and measured holds."""
from pathlib import Path
import json
from checkpoint_host_progress_1030_v9 import packets
from checkpoint_roster_progress_1030_v2 import R,save,sha
from capture_budget import inventory,WORKSPACE_BYTES,WORKSPACE_SCAN_FILES


def checkpoint(name,items,notes):
    hs,b=packets(items)
    b[str(Path(__file__).resolve())]=sha(__file__)
    for p,d in list(b.items()):
        if Path(p).name!='source-closure-v4.json':continue
        closure=json.loads(Path(p).read_text())
        for relative,digest in closure['files'].items():
            source=R/relative
            assert sha(source)==digest,source
            b[str(source.resolve())]=digest
    save(name,dict(status='PRIVATE_SOURCE_QUALIFIED_PARTIAL_INTEGRATION_NO_SHARED_INSTALL',
        frozen_packets=[dict(path=path,sha256=d,status=h.get('status','QUALIFIED_EXPLICIT_SCOPE'))
                        for (path,d),h in zip(items,hs)],notes=notes),b)


if __name__=='__main__':
    checkpoint('ff-real-source-routing-and-full-renderer',[
        ('build/final-fantasy-wram-host-v13/handoff.json','b02d60745a884d10955c03c29b1a4b50ba324b15c9547c7f7c70f8239670b2df'),
        ('build/final-fantasy-joint-typed-v1/handoff.json','b44dd7368466afb584a6dc9117978718241cb1a2ef0e6f4fa90958d737d7c8a3'),
        ('build/final-fantasy-joint-consumers-v1/handoff.json','0690d996a7cc7d936d8c5c608a63081bcb4707d0ab16b07dbe268f9a8555c84d'),
        ('build/final-fantasy-host-render-qualified-v1/handoff.json','a3ea17134c498264c2a216c9f82ead3680f4e6b689db4a18c0291d3f5dcf5949')],[
        'Actual fast-v6 +FFv13 source merge eefce872 uses genuine forcedblank loader, exact2ef76f0b version3 payload. Typed active/auto/climb/item-maturity/nativeX5 contracts corrected from realcallers.128GameLoop and24nativeBG supplementary cases explicitlystage bank+PC selectors; not actualcarthooks.',
        'New independent c22aad37 RAM3 renderer code995+index116+predecoded1752 retains alloriginal CORE/publisher/ART/CHR/combat/terrain/items.4224nativechunkOAM/240fullclass/1056source-descriptor/11264cull/1296actualnativebody-reservation/528realvector cases PASS.',
        'Real overloadcounterperiod defect33of44visibleBoltparts fixed to44of44 with unchanged100draw pressure fixture. Nativeactualbodyheader budget replaces overlyconservative64B assumption. InitialtestwordY/highpage model andsourceassembler/config negatives retained.',
        'DefaultemptyShadowsOff callback149CPU, heavysingleBolt mean21715.9375CPU. No fullMain/native cadence ornaturalallpowerup claim. Palettes/worldsharing/audio/feet/postBG/flashaging/NewEnemy/admission stillpending.',
        'Later genuine shared55 sourcecart54364605 has separateactualFFMain128positive evidence and is undergoingfinalABI/ISRfreeze; thischeckpointdoesnotretag stagedeefce872 receipts as543 proof. Renderer requires newloader/version4 and actualearlydraw route.'
    ])
    checkpoint('joint-classifier-arthur-source-and-render-speed',[
        ('build/character-host-union-rogue-fast-v6/handoff.json','e086635f6d798a36c50dff3cf0dbdfef5011021100bd2c5e1dd0a9f9edd6f275'),
        ('build/character-host-union-high-owner-classifier-v1/handoff.json','01887f66fa3506e94f2da5126cf0a413b2d651696ea01bb5deb538313836c92a'),
        ('build/character-host-union-selector-prelude-v1/handoff.json','56893e9bc3b7711607316b1e405f3246dc698ceea5c498edb8e471f59d46dcfe'),
        ('build/arthur-joint-source-leaf-v1/handoff.json','03f06e994c1801ad1874faf63e96e949f8f5bdc077b200e77e6c2e1eeba2427e'),
        ('build/arthur-joint-source-qualification-v2/handoff.json','c3f2ed5417aab6de47b85ddb20233034843034f99b7f12512b7872fa5d1a8b42'),
        ('build/arthur-body-fair-fast-v4/handoff-v4.json','6860d076a6e02aeaad2ce3e7b62a6f9078d233a219bfd5340e93f4fc1d6fc23b')],[
        'Actual jointcommon begin-tail saves20CPU and retains oldcommonNMI/Boot/IsActivePCs; Bill+443CPU vsrequiredRCRparent remainsHOLD. Carry-safe22/32classifier source changes84ownedbytes/allotherROMincludingA79exact.',
        'Privateprelude17d365d3 changes37bytes/exact41842PCclosure;936actualMain/6656nativecaller suffix/104fresh/36pickupcomparisons/808realvectors. LegalPlayerSize0/1 typedcontract; all254illegal-size negatives retained. Bill+335CPUvs753parent, notparity.',
        'InheritedactualRoguefresh defect is BLOCKING: bothrules NrFresh callsCmHostFresh instead ofRdLifeFresh, health99/09→00/00; nextnativeMain action7/engine11. Sameinfast-v6/prelude, retainedasdefect, notpassingpickupclaim. SeparatetrueSamus-safe lifecycle repair authorized.',
        'Arthur10genuineproducer modules+732Bownservice component fit existingprivatePRG; duplicateold1939BA79common notcopied.2304sourceABI/220invalid/1824realvectors qualification is isolatedcomponent, notcompletejointMain/lifecycleadmission. RAM1move unnecessary/notgranted.',
        'Arthur16384268 fairfast renderer653B/2979of3072carrier passes6400permutations/624strictMain/104foreignzeroCPU/1806realvectors, mean188.405CPU savedvs09237. No newnative; retain actual09237 graphicsPASS/216lag/400performanceHOLD.',
        'Actualshared55transport leaves54ownedA79bytes butArreadiness/acquire/retire/palette/NMIandremainingFFhooks stillpending. No per-owner sourcecontract narrows fullroster/1-1/everypowerup objective.'
    ])
    p=R/'docs/qa/host-integration-progress-2026-10-30.json';j=json.loads(p.read_text())
    j['root_completed_this_continuation'] += [
        'FFfullsource995B renderer +116index/1752predecodedFX imagec22aad37 qualified4224nativechunk/240full4class/1056decode/11264cull/1296realbody-reservation/528realvectors. Realoverloadbugstarving11of44Boltparts fixed; unchanged100drawfixture now44/44. Defaultempty149CPU; heavyspells remain timingHOLD.',
        'FFsourcev13 loader7f2c704e/version3payload2ef76f0b +realcurrentfast-v6typedmergeeefce872 qualified. Actualcaller review fixes service23 maturity/24collect, active/4-5/climb/nativeX5. Staged128Main/24BG are explicitlyseparatefromlateractual54364605shared55source128Main proof, freezeongoing.',
        'Genuineclassifierba472dd3 preservesallpublicPCs/otherROM; shared55transport nowlinks withFFandArproducerobjects in54364605. Ar lifecycle/NMI notimplied. NewAr732Bcomponent2304ABI/1824ISR andfairfast16384268(624Main,mean-188.405CPU) qualified; noRAM1needed.',
        'Prelude17d365d3 actualowned16B/39Bgates saves108CPU/Bill+335vsparent;936Main/6656nativeSuffix/808vectors passlegal-sizecontract. ActualRoguefresh constructorhealth99/09→0 causesengine11 inbotholdandnew; recordedinstallationblockerandseparatelifecyclerepairunderway.'
    ]
    j['active_work']['Final_Fantasy']='Actualshared54364605 source routing runs128realGameLoops withoutselectorinterception. Newc22aad37fullFX renderer sourcequalified; composingversion4/earlyDrawShots successor. Palettes/worldsharing/music/feet/postBG/flashaging/NewEnemy/nativeadmission and1-1/everyupgrade pending.'
    j['active_work']['joint_resource_base']='Actual55sourcecart54364605 fits2538/2592A79; FF+Ar ownveneerpages andcarry-safeclassifier link. SourceABI/ISRqualification ongoing, Arlifecycle/NMIhooks pending. Separatetimingprelude17d saves108CPUtoBill+335; no native/performanceparityclaim.'
    j['active_work']['Arthur']='Requiredinkunconditional. Native09237graphicsPASSbut216lag/400. New16384268identicalfairOAMfastpath source624Main/1806vectors savesmean188.405CPU, no native. Genuine10module+732Bsourcecomponent compiled/qualifiedandjoint55linked; generation/cookie/acquire/retire/NMI/palettehooks beingcomposed. NoRAM1move.'
    j['active_work']['Rogue_Dawn']='ActualinheritedNrFreshdefecthealth→0/action7/engine11 foundinbothrules. GenericGmOnlyraw2 stilllegacy, isolatedmanualRdLifeFreshsmoke wasnotnaturalconstructorproof. Samus-safeactualrouteinventory/fix underway. Currentpublicpending; noadmission.'
    v=inventory(R,WORKSPACE_BYTES,WORKSPACE_SCAN_FILES);assert v.complete
    j['measured_workspace_bytes']=v.bytes;j['measured_workspace_files']=v.files
    p.write_text(json.dumps(j,indent=2)+'\n')
    print(json.dumps(dict(workspace_bytes=v.bytes,workspace_files=v.files,under70GB=True)))
