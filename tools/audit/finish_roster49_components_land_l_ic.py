"""Finish unchanged L; bind the known zero-length DPCM marker separately."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-components-land-l-ia';K=V/'root49-components-combined-k'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
def main():
 out=O/'build-review-ic.json';assert not out.exists();prep=read(O/'preparation.json')
 for n,h in prep['source_hashes'].items():assert sha(O/'source'/n)==h
 cp=R/'build/checkpoints/roster-audit-v49-sophia-block-origin-hu/manifest.json';assert sha(cp)==prep['current_HU_checkpoint_sha256'];c=read(cp)
 original=R/'tools/audit/build_roster49_components_land_l_ia.py';assert sha(original)==prep['script_sha256'];shutil.copyfile(original,O/'builder-ia-metadata-negative.py.txt')
 syntax=V/'root49-components-land-l-ia-syntax-negative.py';assert syntax.exists()
 (O/'host-negative-ia.json').write_text(json.dumps(dict(kind='HOST_SYNTAX_THEN_ZERO_LENGTH_LINKER_MARKER_METADATA_NEGATIVES',syntax_script_sha256=sha(syntax),builder_before_metadata_fix_sha256=sha(original),symbol_delta_sha256=sha(O/'symbol-delta-ib.json'),scope='Initial syntax rejected before source/build. Corrected host script then assembled MMC3 successfully and asserted globalPC set due solely to the known empty DPCM_BANK0 marker moving with appended GUEST_GFX. No source/runtime change for either host successor. First source/ROM/logs retained.'),indent=2)+'\n',encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('land_ic_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'');after=O/'source/build'/(stem+'.nes');before=K/'source/build'/after.name
   if mapper!='mmc3'or baseline:
    with(O/(stem+'-build-ic.log')).open('wb')as log:q=subprocess.run([sys.executable,str(O/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
    assert q.returncode==0,(mapper,baseline)
   a,b=before.read_bytes(),after.read_bytes();layout={}
   if baseline:assert a==b
   else:
    old,new=im.Image(before),im.Image(after)
    assert all(new.ram[n]==v for n,v in old.ram.items())
    assert a[:16]==b[:16]and a[16+512*1024:]==b[16+512*1024:]
    def symbols(image):return{z['name']:z for z in image.data['sym']if z.get('scope')==1 and 'seg'in z and 'val'in z}
    og,ng=symbols(old),symbols(new);changed=[n for n,z in og.items()if n not in ng or z['val']!=ng[n]['val']];assert changed==['DPCM_BANK0']
    os={s['name']:s for s in old.segs.values()};ns={s['name']:s for s in new.segs.values()}
    marker=dict(old=old.segs[og['DPCM_BANK0']['seg']],new=new.segs[ng['DPCM_BANK0']['seg']]);assert marker['old']['size']==marker['new']['size']==0
    assert(marker['old']['ooffs']-16)//8192==(marker['new']['ooffs']-16)//8192==12
    assert ng['DPCM_BANK0']['val']-og['DPCM_BANK0']['val']==(292 if mapper=='mmc3'else 274)
    delta={n:ns[n]['size']-os[n]['size']for n in ns if ns[n]['size']!=os[n]['size']}
    assert delta=={'BILL_BODY_COLD':40,'SPECIAL_ROSTER':3,'GUEST_GFX':292 if mapper=='mmc3'else 274,'CHAR_SELECT':13}
    layout=dict(all_old_nonempty_global_PC_and_old_RAM_literal_K=True,zero_length_marker=marker,marker_semantics='DPCM_BANK0 has no bytes; known source references consume .bank only, unchanged12. Source invocations in mmc5.s/driver_famistudio.s and common.inc are unchanged.',new_semantic_aliases=sorted(set(new.ram)-set(old.ram)),header_CHR_literal=True,segment_growth=delta,SPECIAL_ROSTER_free=8192-ns['SPECIAL_ROSTER']['size'],new_helper_hooks={n:new.hook(n)for n in['SophiaHeadBlockOrigin','MegaManRushLandCharacterReset','MegaManRushLandBeginStatus','MegaManRushLandEnd']})
    assert layout['SPECIAL_ROSTER_free']==(76 if mapper=='mmc3'else 82)
   builds.append(dict(mapper=mapper,baseline=baseline,changed_bytes_vs_K=sum(x!=y for x,y in zip(a,b)),layout=layout,artifacts={ext:dict(path=str(after.with_suffix('.'+ext).relative_to(R)),sha256=sha(after.with_suffix('.'+ext)),bytes=after.with_suffix('.'+ext).stat().st_size)for ext in ['nes','dbg','lbl','map']}));print(stem,'PASS',layout.get('SPECIAL_ROSTER_free'),flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 out.write_text(json.dumps(dict(status='PASS_PRIVATE_L_FOUR_BUILDS_AND_LITERAL_BASELINES_COMBINED_NATIVE_PENDING',script_sha256=sha(__file__),preparation_sha256=sha(O/'preparation.json'),retained_host_negative_sha256=sha(O/'host-negative-ia.json'),builds=builds,limits=['K+HU+root-reviewed Land only; no HUD/Ryu/visibleWater.','All old nonempty global PCs/RAM/header/CHR and both baseline ROMs literalK; empty DPCM marker shifts inside samebank12 with no bytes.','Combined native/caller/source/lifecycle proofs remain pending.'],installed=False,main_changed=False,goal_complete=False),indent=2)+'\n',encoding='utf-8');print('COMBINED_L',sha(out),flush=True)
if __name__=='__main__':main()
