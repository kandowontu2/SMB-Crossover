"""Link Karnov's native terrain/movement boundary; menu admission stays disabled."""
from pathlib import Path
import argparse,hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import build_karnov_cache_host_1101_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
O,A,W,J=B.O,B.A,B.W,B.J

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--render',action='store_true');ap.add_argument('--ingress',action='store_true');ap.add_argument('--scene',action='store_true');args=ap.parse_args()
    assert not args.ingress or args.render
    assert not args.scene or args.ingress
    assert not(O/'source-stage.json').exists()
    paths=[Path(__file__),Path(B.__file__),R/'tools/reference/karnov_cache_kernel_1101_v1.s',R/'tools/reference/karnov_cache_resident_1101_v1.inc',R/'tools/reference/karnov_host_terrain_1101_v1.inc',A/'portable_actor.inc',A/'portable_dispatch.inc',W/'portable_weapon.inc',W/'portable_clear.inc']
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
    if args.render:
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
    kernel=kernel.replace(vector_marker,'\n'.join(' jmp '+services.get(i,'KrReject')for i in range(36)))
    kernel=kernel.replace('.include "portable_actor.inc"','.include "kr-host-actor.inc"').replace('KrKernelEnd:','.include "kr-terrain.inc"\nKrKernelEnd:')
    if args.render:
        kernel=kernel.replace('KrKernelEnd:','.include "kr-render.inc"\nKrKernelEnd:')
        B.write(O/'kr-render.inc',(R/'tools/reference/karnov_host_render_1101_v1.inc').read_text())
    actor=paths[5].read_text();old='Kr_FA06: LDX #$10 ; original 0xfa06';assert actor.count(old)==1
    actor=actor.replace(old,'Kr_FA06: JMP Kr_FA5C ; SMB owns viewport clamps; retain original facing update')
    cookie=bytes([167,7,1,5 if args.scene else 4 if args.ingress else 3 if args.render else 2])+hashlib.sha256(b''.join(p.read_bytes()for p in paths)+bytes.fromhex(B.sha(J/'candidate.nes'))).digest()[:12]
    (O/'kr-cookie.bin').write_bytes(cookie)
    for name,t in [('kr-kernel.s',kernel),('kr-resident.inc',resident),('kr-terrain.inc',terrain),('kr-host-actor.inc',actor)]:B.write(O/name,t)
    # Same exact main inputs as prior phase; export actual linked host owners.
    entry=(J/'menu/entrypoint.s').read_text()
    names=['CurrentPlayer','NumberofLives','WorldNumber','AreaAddrsLOffset','FrameCounter','OperMode','GamePauseStatus','PlayerFacingDir','PlayerSize','CrouchingFlag','Player_X_Scroll','Player_XSpeedAbsolute','Player_Pos_ForScroll','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Rel_XPos','Player_Rel_YPos','BoundingBox_UL_Corner','BoundingBox_LR_Corner','Block_Buffer_1','Block_Buffer_2','AreaType','CrossoverBehaviorVersion','GuestBodyStompAllowed','GuestBodyNoStomp']
    if args.render:names += ['ObjectMetasprite','SmPosePtr','Player_SprAttrib','VRAM_Buffer1','VRAM_Buffer1_Offset','X5SetPhysicalChr','MetaspriteRenderLoop']
    entry+='\n.export '+','.join(names)+'\n';B.write(O/'entrypoint.s',entry)
    t=(R/'build/hogan-thomas-current/src/cf_menu_body.inc').read_text();old='.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart),$ff';assert t.count(old)==1
    t=t.replace(old,'''KrResidentBegin:
.export KrResidentBegin,KrResidentLimit
.include "kr-resident.inc"
.assert KrResidentEnd<=$bfb0,lderror,"Karnov resident exceeds menu padding"
.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart)-(KrResidentEnd-KrResidentBegin),$ff
KrResidentLimit:
''');B.write(O/'cf_menu_body.inc',t)
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
    B.write(O/'kr-images.s','.segment "KR_KERNEL_IMAGE"\n.incbin "kr-kernel.bin"\n.segment "KR_BODY_CHR"\n.incbin "'+('kr-body.chr'if args.render else'body.chr')+'"\n')
    B.run('terrain-images-build',[str(cc),'-g','--bin-include-dir',str(O),'--bin-include-dir',str(R/'build/karnov-original-art-1101-v1'),'-o',str(O/'kr-images.o'),str(O/'kr-images.s')])
    link.append(str(O/'kr-images.o'));B.run('terrain-final-link',link);assert(O/'kr-kernel.bin').read_bytes()==image
    dbg=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'}
    dbg.write_bytes(b''.join(l for l in dbg.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes')
    old=scoped_load(J/'candidate.nes');new=scoped_load(O/'candidate.nes')
    for row in range(36):
        target=address(new,services.get(row,'KrReject'))
        assert image[row*3:row*3+3]==bytes([0x4c,target&255,target>>8]),('Emitted service vector',row)
    changed=[n for n,s in old['syms'].items()if(n not in new['syms']or s['val']!=new['syms'][n]['val'])and '$anon-SCOPE-'not in n and n!='_FARCALL_COUNT']
    permitted=[]
    if args.ingress:
        permitted=[n for n in changed if n=='MarioWaterCoast::ProductHi'or old['segs'].get(old['syms'][n].get('seg'),{}).get('name')=='"CHARACTER_HOST_UNION"']
    if args.scene:
        permitted += [n for n in changed if n=='HotPlayerGraphics::Foreign']
    assert set(changed)<=set(permitted),[n for n in changed if n not in permitted][:20]
    lo,hi=[address(new,n)for n in ['KrResidentBegin','KrResidentLimit']]
    allowed=[(16+29*8192+lo-0xa000,16+29*8192+hi-0xa000),(1048592+399*1024,1048592+412*1024)]
    if args.ingress:
        # Occupied source data is swapped with an exact relocated copy; the
        # old multiply routine changes only its three table operands.
        allowed += [(location(old,'MarioWaterCoast'),location(old,'MarioWaterCoast::ProductHi')+256),(location(old,'HuStart'),location(old,'HuEnd'))]
        assert address(new,'HuResolve')==0xba54 and address(new,'KrServiceVeneers')==0xb400
    if args.scene:
        allowed.append((location(old,'InitScreen'),location(old,'InitScreen')+32))
        allowed.append((location(old,'ThPostNativeHot'),location(old,'HotPlayerGraphics')+226))
    delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b];assert delta and all(any(a<=i<b for a,b in allowed)for i in delta)
    paths += [J/'candidate.nes',J/'candidate.dbg',O/'entrypoint.s',O/'cf_menu_body.inc',O/'kr-kernel.s',O/'kr-resident.inc',O/'kr-terrain.inc',O/'kr-host-actor.inc',O/'kr-cookie.bin',O/'kr-kernel.bin',O/'kr-images.s',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'terrain-final-link.json']
    if args.render:paths.append(O/'kr-render.inc')
    if args.ingress:paths.append(O/'ingress-union-build.json')
    B.save(O/'terrain-assembly.json',dict(passed=True,render=args.render,ingress=args.ingress,scene=args.scene,source_CPU=False,native=False,installed=False,menu_admitted=False,ROM_sha256=B.sha(O/'candidate.nes'),cookie=cookie.hex(),resident_bytes=address(new,'KrResidentEnd')-lo,kernel_bytes=address(new,'KrKernelEnd')-0xa000,implemented_services=services,all_existing_runtime_symbols_exact=not changed,moved_source_symbols=permitted,changed_bytes=len(delta),allowed_ROM_ranges=allowed,viewport_adaptation='Only FA06 clamps redirect to original FA5C facing; SMB owns absolute boundaries. Original jump/fall/walk instructions and data retained.',bindings={str(p.resolve()):B.sha(p)for p in paths}))
    print(json.dumps(dict(passed=True,candidate=B.sha(O/'candidate.nes'),resident_bytes=address(new,'KrResidentEnd')-lo,kernel_bytes=address(new,'KrKernelEnd')-0xa000,services=services,menu_admitted=False)))

if __name__=='__main__':main()
