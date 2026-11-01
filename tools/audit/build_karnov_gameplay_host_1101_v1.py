"""Link the declared Karnov WIP services and retain all existing host owners."""
from pathlib import Path
import argparse,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import build_karnov_cache_host_1101_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
O,A,W,J=B.O,B.A,B.W,B.J

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--ingress',action='store_true');ap.add_argument('--scene',action='store_true');ap.add_argument('--menu',action='store_true');ap.add_argument('--compact-menu',action='store_true');ap.add_argument('--rebound',action='store_true');ap.add_argument('--health',action='store_true');ap.add_argument('--menu-input',action='store_true');ap.add_argument('--pickups',action='store_true');ap.add_argument('--combat',action='store_true');args=ap.parse_args()
    assert not args.ingress or args.render
    assert not args.scene or args.ingress
    assert not args.menu or args.scene
    assert not args.compact_menu or args.menu
    assert not args.rebound or args.scene
    assert args.rebound or not(O/'kr-rebound.inc').exists(),'Keep --rebound after separating private post-BG from public bounce'
    assert not args.health or args.rebound
    assert args.health or not(O/'kr-health.inc').exists(),'Keep --health after integrating source injury/death'
    assert not args.menu_input or args.compact_menu
    assert args.menu_input or not(O/'menu-input-entry.s').exists(),'Keep --menu-input after the menu input repair'
    assert not args.pickups or args.health
    assert args.pickups or not(O/'kr-pickup-kernel-v3.inc').exists(),'Keep --pickups after integrating earned source upgrades'
    assert not args.combat or args.pickups
    assert args.combat or not(O/'kr-combat-v7.inc').exists(),'Keep --combat after integrating native contacts'
    assert args.menu or not(O/'kr-menu.inc').exists(),'This root now contains menu sources; keep --menu enabled'
    assert not(O/'source-stage.json').exists()
    paths=[Path(__file__),Path(B.__file__),R/'tools/reference/karnov_cache_kernel_1101_v1.s',R/'tools/reference/karnov_cache_resident_1101_v1.inc',R/'tools/reference/karnov_host_terrain_1101_v1.inc',A/'portable_actor.inc',A/'portable_dispatch.inc',W/'portable_weapon.inc',W/'portable_clear.inc']
    compact=R/'build/menu-wwf-compact-1101-v1'
    if args.compact_menu:
        proof=json.loads((compact/'assembly-stage.json').read_text());assert proof['passed']
        for p,h in proof['bindings'].items():assert B.sha(p)==h,p
        B.write(O/'character_select.s',(compact/'character_select.s').read_text())
        paths += [compact/'character_select.s',compact/'assembly-stage.json',O/'character_select.s']
    else:
        assert 'WfCompactX:'not in(O/'character_select.s').read_text(),'Keep --compact-menu after carrying the delivered fix'
    kernel=paths[2].read_text();vector_marker='.repeat 36\n jmp KrReject\n.endrepeat';assert kernel.count(vector_marker)==1
    services={0:'KrMovement',10:'KrHead',11:'KrBodyPolicy',12:'KrAdder',13:'KrBoxProfile',14:'KrSide',15:'KrConstruct',16:'KrBox',27:'KrPostTerrain',28:'KrHeadWithin'}
    terrain=paths[4].read_text()
    resident=paths[3].read_text();union_command=None
    if args.ingress:
        from prepare_karnov_ingress_1101_v1 import prepare as ingress_prepare
        resident,union_command,refs=ingress_prepare(resident,B.write);paths+=refs
    if args.scene:
        from prepare_karnov_scene_1101_v1 import prepare as scene_prepare
        resident,terrain,refs=scene_prepare(resident,terrain,B.write);paths+=refs
    if args.menu:
        from prepare_karnov_menu_1101_v1 import prepare as menu_prepare
        resident,refs=menu_prepare(resident,B.write);paths+=refs
    if args.rebound:
        from prepare_karnov_rebound_1101_v2 import prepare as rebound_prepare
        resident,refs=rebound_prepare(resident,B.write);paths+=refs
        services.update({27:'KrBounce',31:'KrBounce',36:'KrPostTerrain'})
    if args.health:
        health=R/'tools/reference/karnov_health_1101_v2.inc'
        B.write(O/'kr-health.inc',health.read_text());paths += [health,O/'kr-health.inc']
        services.update({5:'KrHealthInjury',6:'KrHealthStatus',7:'KrHealthDeathStart',8:'KrHealthDeathUpdate'})
    if args.render:
        # The native four-color writer restores the area's universal backdrop
        # after the black lives screen. Retain its exact eight-entry table.
        parent=scoped_load(J/'candidate.nes');at=location(parent,'BackgroundColors')
        (O/'kr-native-bg.bin').write_bytes(parent['raw'][at:at+8]);paths.append(O/'kr-native-bg.bin')
        art=json.loads((O/'render-art.json').read_text());assert art['passed']
        for p,h in art['bindings'].items():assert B.sha(p)==h,p
        paths += [R/'tools/reference/karnov_host_render_1101_v1.inc',R/'tools/audit/prepare_karnov_host_art_1101_v1.py',O/'render-art.json',O/'kr-pose-meta.bin',O/'kr-body.chr',O/'kr-shot-tiles.bin']
        services.update({1:'KrGraphics',2:'KrDraw',26:'KrColors'})
        old=' lda #$a7\n sta KrReady';assert terrain.count(old)==1
        terrain=terrain.replace(old,' jsr KrCopyArt\n'+old)
        old=' jsr KrSourceFrame\n inc KrState+$e8';assert terrain.count(old)==1
        terrain=terrain.replace(old,' jsr KrSourceFrame\n jsr KrSourceWeapons\n inc KrState+$e8')
        old=' lda FrameCounter\n sta KrLastEpoch';assert terrain.count(old)==1
        terrain=terrain.replace(old,' jsr KrRebaseShots\n'+old)
    service_count=37 if args.rebound else 36
    kernel=kernel.replace(vector_marker,'\n'.join(' jmp '+services.get(i,'KrReject')for i in range(service_count)))
    kernel=kernel.replace('.include "portable_actor.inc"','.include "kr-host-actor.inc"').replace('KrKernelEnd:','.include "kr-terrain.inc"\nKrKernelEnd:')
    if args.render:
        kernel=kernel.replace('KrKernelEnd:','.include "kr-render.inc"\nKrKernelEnd:')
        B.write(O/'kr-render.inc',(R/'tools/reference/karnov_host_render_1101_v1.inc').read_text())
    if args.rebound:
        kernel=kernel.replace('KrKernelEnd:','.include "kr-rebound.inc"\nKrKernelEnd:')
    if args.health:
        kernel=kernel.replace('KrKernelEnd:','.include "kr-health.inc"\nKrKernelEnd:')
    actor=(A/'portable_actor.inc').read_text();old='Kr_FA06: LDX #$10 ; original 0xfa06';assert actor.count(old)==1
    actor=actor.replace(old,'Kr_FA06: JMP Kr_FA5C ; SMB owns viewport clamps; retain original facing update')
    if args.menu_input:
        from prepare_menu_input_1101_v3 import proposal,REFERENCE
        config=(O/'candidate.cfg').read_text()
        line='\n    MENU_INPUT_COLD_V3: load=X5_NEW_42_TAIL,type=ro,start=$beb5,optional=yes;'
        assert config.count(line)<=1
        config=config.replace(line,'')
        command=json.loads((O/'main-build.json').read_text())['command']
        candidates=[Path(command[i+1])/'characters.s'for i,v in enumerate(command[:-1])if v=='-I'and Path(command[i+1])!=O]
        character_source=next(p for p in candidates if p.exists())
        assert character_source==R/'build/bt-p2-cf-menu-source-1031-v2/joint/src/characters.s'
        texts=list(proposal((O/'character_select.s').read_text(),character_source.read_text(),(J/'menu/entrypoint.s').read_text(),config))
        # ca65's include filename parser rejects this Windows drive path.
        # Keep an exact local copy and bind both it and the reference source.
        B.write(O/'menu-input.inc',REFERENCE.read_text())
        texts[2]=texts[2].replace(REFERENCE.as_posix(),'menu-input.inc')
        marker='\n; Actual original segment owners endBEB5 and restartBF00.'
        assert texts[0].count(marker)==1
        select,cold=texts[0].split(marker)
        texts[0]=select+'\n'
        cold=cold[cold.index('.pushseg'):].replace('.segment "MENU_INPUT_COLD_V3"','.segment "PROTO_PALETTE_ACK"')
        texts[2]+='\n; Append after the original palette-ACK emitter; no new segment.\n'+cold+'\n.assert MnMenuColdInit=$beb5,lderror,"Funded cold helper start"\n.assert MnMenuColdInit+26=$becf,lderror,"Funded cold helper end"\n'
        texts[3]=texts[3].replace(line,'')
        for name,t in zip(['character_select.s','characters.s','menu-input-entry.s','candidate.cfg'],texts):B.write(O/name,t)
        paths += [R/'tools/audit/prepare_menu_input_1101_v3.py',REFERENCE,character_source,O/'menu-input.inc',O/'characters.s',O/'menu-input-entry.s',O/'candidate.cfg']
    # Same exact main inputs as prior phase; export actual linked host owners.
    entry=((O/'menu-input-entry.s')if args.menu_input else(J/'menu/entrypoint.s')).read_text()
    names=['CurrentPlayer','NumberofLives','WorldNumber','AreaAddrsLOffset','FrameCounter','OperMode','GamePauseStatus','PlayerFacingDir','PlayerSize','CrouchingFlag','Player_X_Scroll','Player_XSpeedAbsolute','Player_Pos_ForScroll','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Rel_XPos','Player_Rel_YPos','BoundingBox_UL_Corner','BoundingBox_LR_Corner','Block_Buffer_1','Block_Buffer_2','AreaType','CrossoverBehaviorVersion','GuestBodyStompAllowed','GuestBodyNoStomp']
    if args.render:names += ['ObjectMetasprite','SmPosePtr','Player_SprAttrib','VRAM_Buffer1','VRAM_Buffer1_Offset','X5SetPhysicalChr','MetaspriteRenderLoop']
    if args.health:names += ['MmDeathFlag','MmDeathAge','MmDeathPit','TimerControl','EventMusicQueue','StarInvincibleTimer','MTileAttribute']
    entry+='\n.export '+','.join(names)+'\n'
    t=(R/'build/hogan-thomas-current/src/cf_menu_body.inc').read_text();old='.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart),$ff';assert t.count(old)==1
    t=t.replace(old,'''KrResidentBegin:
.export KrResidentBegin,KrResidentLimit
.include "kr-resident.inc"
.assert KrResidentEnd<=$bfb0,lderror,"Karnov resident exceeds menu padding"
.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart)-(KrResidentEnd-KrResidentBegin),$ff
KrResidentLimit:
''')
    if args.pickups:
        from prepare_karnov_pickup_host_1101_v5 import transform_sources
        graft=transform_sources(kernel=kernel,resident=resident,terrain=terrain,entrypoint=entry,cf_menu=t)
        kernel,resident,terrain,entry,t=[graft[n]for n in ['kernel','resident','terrain','entrypoint','cf_menu']]
        for name,text in graft['fragments'].items():B.write(O/name,text)
        paths += [R/'tools/audit/prepare_karnov_pickup_host_1101_v3.py',R/'tools/audit/prepare_karnov_pickup_host_1101_v4.py',R/'tools/audit/prepare_karnov_pickup_host_1101_v5.py',R/'tools/reference/karnov_pickups_1101_v2.inc',*[O/n for n in graft['fragments']]]
        services.update(graft['service_rows'])
    if args.combat:
        from prepare_karnov_combat_host_1101_v7 import transform_sources as combat_graft
        config=(O/'candidate.cfg').read_text()
        config=re.sub(r'(?m)^KR_COMBAT_RAM_MEM:[^\n]+\n','',config)
        config=config.replace('\nSEGMENTS { KR_COMBAT_ROM:load=KR_COMBAT_RAM_MEM,type=ro; KR_COMBAT_IMAGE:load=CF_CHR_POST,type=ro,start=$fec00; }\n','')
        graft=combat_graft(kernel=kernel,resident=resident,terrain=terrain,entrypoint=entry,config=config,output=O)
        kernel,resident,terrain,entry=[graft[n]for n in ['kernel','resident','terrain','entrypoint']]
        B.write(O/'candidate.cfg',graft['config'])
        for name,text in graft['fragments'].items():B.write(O/name,text)
        paths += [R/'tools/audit/prepare_karnov_combat_host_1101_v7.py',R/'tools/audit/prepare_karnov_combat_stack_1101_v3.py',R/'tools/audit/prepare_karnov_loader_funding_1101_v6.py',R/'tools/reference/karnov_combat_1101_v2.inc',R/'tools/reference/karnov_combat_carrier_loader_1101_v3.inc',*[O/n for n in graft['fragments']]]
        services.update(graft['service_rows'])
    cookie=bytes([167,7,1,14 if args.combat else 13 if args.pickups else 10 if args.menu_input else 9 if args.health else 8 if args.rebound else 7 if args.compact_menu else 6 if args.menu else 5 if args.scene else 4 if args.ingress else 3 if args.render else 2])+hashlib.sha256(b''.join(p.read_bytes()for p in paths)+bytes.fromhex(B.sha(J/'candidate.nes'))).digest()[:12]
    (O/'kr-cookie.bin').write_bytes(cookie)
    for name,text in [('kr-kernel.s',kernel),('kr-resident.inc',resident),('kr-terrain.inc',terrain),('kr-host-actor.inc',actor),('entrypoint.s',entry),('cf_menu_body.inc',t)]:B.write(O/name,text)
    build=json.loads((O/'main-build.json').read_text())['command'][:]
    for opt in ['-I','--bin-include-dir']:build[1:1]=[opt,str(O)]
    B.run('terrain-main-build',build)
    if union_command:B.run('ingress-union-build',union_command)
    cc=R/'tools/Windows/cc65/bin/ca65.exe'
    B.run('terrain-kernel-build',[str(cc),'-g','-I',str(O),'-I',str(A),'-I',str(W),'--bin-include-dir',str(O),'-o',str(O/'kr-kernel.o'),str(O/'kr-kernel.s')])
    link=json.loads((O/'link.json').read_text())['command'][:]+[str(O/'kr-kernel.o')]
    if args.ingress:
        old_union=str(R/'build/hogan-thomas-current/union.o');assert link.count(old_union)==1
        link[link.index(old_union)]=str(O/'union.o')
    B.run('terrain-first-link',link)
    image=(O/'kr-kernel.bin').read_bytes();assert len(image)==8192 and image[0x1fe0:0x1ff0]==cookie
    B.write(O/'kr-images.s','.segment "KR_KERNEL_IMAGE"\n.incbin "kr-kernel.bin"\n.segment "KR_BODY_CHR"\n.incbin "'+('kr-body.chr'if args.render else'body.chr')+'"\n'+('.segment "KR_COMBAT_IMAGE"\n.incbin "kr-combat.bin"\n'if args.combat else''))
    B.run('terrain-images-build',[str(cc),'-g','--bin-include-dir',str(O),'--bin-include-dir',str(R/'build/karnov-original-art-1101-v1'),'-o',str(O/'kr-images.o'),str(O/'kr-images.s')])
    link.append(str(O/'kr-images.o'));B.run('terrain-final-link',link);assert(O/'kr-kernel.bin').read_bytes()==image
    dbg=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'}
    dbg.write_bytes(b''.join(l for l in dbg.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes')
    old=scoped_load(J/'candidate.nes');new=scoped_load(O/'candidate.nes')
    for row in range(service_count):
        target=address(new,services.get(row,'KrReject'))
        assert image[row*3:row*3+3]==bytes([0x4c,target&255,target>>8]),('Emitted service vector',row)
    changed=[n for n,s in old['syms'].items()if(n not in new['syms']or s['val']!=new['syms'][n]['val'])and '$anon-SCOPE-'not in n and n!='_FARCALL_COUNT']
    permitted=[]
    if args.ingress:
        permitted=[n for n in changed if n=='MarioWaterCoast::ProductHi'or old['segs'].get(old['syms'][n].get('seg'),{}).get('name')=='"CHARACTER_HOST_UNION"']
    if args.scene:
        permitted += [n for n in changed if n=='HotPlayerGraphics::Foreign']
    if args.compact_menu:
        permitted += [n for n in changed if n.startswith('DrawSelectionPreview::')]
        aliases={'PreviewPriority','PreviewPriorityDone','PreviewX','FmNativeOtherPreview','FmNativeDkPreview','FmPendingGenericPreview','FmNativePreview','FmPendingPreview'}
        for n in set(changed)&aliases:
            assert location(old,'DrawSelectionPreview')<=location(old,n)<location(old,'QueueVariantHint')
            assert location(new,'DrawSelectionPreview')<=location(new,n)<location(new,'QueueVariantHint')
            permitted.append(n)
    assert set(changed)<=set(permitted),[n for n in changed if n not in permitted][:20]
    lo,hi=[address(new,n)for n in ['KrResidentBegin','KrResidentLimit']]
    allowed=[(16+29*8192+lo-0xa000,16+29*8192+hi-0xa000),(1048592+399*1024,1048592+412*1024)]
    if args.combat:allowed.append((1048592+1019*1024,1048592+1021*1024))
    if args.ingress:
        # Occupied source data is swapped with an exact relocated copy; the
        # old multiply routine changes only its three table operands.
        allowed += [(location(old,'MarioWaterCoast'),location(old,'MarioWaterCoast::ProductHi')+256),(location(old,'HuStart'),location(old,'HuEnd'))]
        assert address(new,'HuResolve')==0xba54 and address(new,'KrServiceVeneers')==0xb400
    if args.scene:
        allowed.append((location(old,'InitScreen'),location(old,'InitScreen')+32))
        allowed.append((location(old,'ThPostNativeHot'),location(old,'HotPlayerGraphics')+226))
    if args.menu:
        allowed += [(location(old,'FmPending'),location(old,'FmResolve')+40),(location(old,'FmStartFlags'),location(old,'FmStartFlags')+28),(location(old,'FmNames')+32,location(old,'FmNames')+48),(location(old,'GmOnlyHigh')+1,location(old,'GmOnlyHigh')+2)]
    if args.compact_menu:
        allowed += [(location(old,'DrawSelectionPreview'),location(old,'QueueVariantHint'))]
    if args.menu_input:
        # Exact source-funded menu patch intervals, previously independently
        # assembled against the actual native consumers. All PCs stay fixed.
        intervals=[(541893,20),(542080,6),(82358,18),(544976,107),(548549,26)]
        allowed += [(start,start+size)for start,size in intervals]
    delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b];assert delta and all(any(a<=i<b for a,b in allowed)for i in delta)
    paths += [J/'candidate.nes',J/'candidate.dbg',O/'entrypoint.s',O/'cf_menu_body.inc',O/'kr-kernel.s',O/'kr-resident.inc',O/'kr-terrain.inc',O/'kr-host-actor.inc',O/'kr-cookie.bin',O/'kr-kernel.bin',O/'kr-images.s',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'terrain-final-link.json']
    if args.combat:paths.append(O/'kr-combat.bin')
    if args.render:paths.append(O/'kr-render.inc')
    if args.ingress:paths.append(O/'ingress-union-build.json')
    B.save(O/'terrain-assembly.json',dict(passed=True,render=args.render,ingress=args.ingress,scene=args.scene,menu=args.menu,compact_menu=args.compact_menu,rebound=args.rebound,health=args.health,menu_input=args.menu_input,pickups=args.pickups,combat=args.combat,carrier_ownership_granted=False,service_count=service_count,source_CPU=False,native=False,installed=False,menu_admitted=args.menu,ROM_sha256=B.sha(O/'candidate.nes'),cookie=cookie.hex(),resident_bytes=address(new,'KrResidentEnd')-lo,kernel_bytes=address(new,'KrKernelEnd')-0xa000,implemented_services=services,all_existing_runtime_symbols_exact=not changed,moved_source_symbols=permitted,changed_bytes=len(delta),allowed_ROM_ranges=allowed,viewport_adaptation='Only FA06 clamps redirect to original FA5C facing; SMB owns absolute boundaries. Original jump/fall/walk instructions and data retained.',bindings={str(p.resolve()):B.sha(p)for p in paths}))
    print(json.dumps(dict(passed=True,candidate=B.sha(O/'candidate.nes'),resident_bytes=address(new,'KrResidentEnd')-lo,kernel_bytes=address(new,'KrKernelEnd')-0xa000,services=services,menu_admitted=args.menu)))

if __name__=='__main__':main()
