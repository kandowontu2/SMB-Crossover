"""One sparse source build: exact disjoint9d1 HUD delta over canonical4a."""
from pathlib import Path
import configparser,difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';P='samus_fixed_hud_current4a'
BASE=B/'smb-crossover-mmc5-expanded.nes';EXPECTED='4a0394b0892e6c54940856791e44bcbe9fe4e469047aca3982c3f59112a61b8b'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from patch_samus_fixed_hud_v2 import plan
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 assert sha(BASE)==EXPECTED
 historical=json.loads((B/'samus_fixed_hud_handoff.json').read_text())
 assert all(sha(q['path'])==q['sha256']for q in historical['bindings'])
 old=scoped_load(BASE);raw=old['raw'];prior=(B/'samus_fixed_hud.nes').read_bytes();original=(B/'proto_palette_ack.nes').read_bytes()
 delta=[i for i,(a,b)in enumerate(zip(original,prior))if a!=b];assert len(delta)==70
 assert all(raw[i]==original[i]for i in delta),'Current parent overlaps historical HUD delta'
 changed,recipe=plan(R,BASE)
 changed['src/remaining_weapons.s']=(B/'samus_fixed_hud_remaining_weapons.s').read_bytes()
 changed['src/samus_fixed_hud.s']=(B/'samus_fixed_hud_samus_fixed_hud.s').read_bytes()
 ep=(R/'src/entrypoint.s').read_bytes();nl=b'\r\n'if b'\r\n'in ep else b'\n'
 changed['src/entrypoint.s']=ep+nl+nl.join([b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5',b'.include "samus_fixed_hud.s"',b'.endif',b''])
 pack=(R/'tools/reference/pack_chr.py').read_bytes();nlp=b'\r\n'if b'\r\n'in pack else b'\n'
 token=b"    (ROOT/'build/chr-packing.json').write_text(json.dumps(report,indent=2)+'\\n')"
 assert pack.count(token)==1
 hook=nlp.join([b'    # Optional expanded-only overlay; both ordinary outputs/assets stay exact.',b'    from patch_samus_fixed_hud_v2 import apply_expanded_assets',b'    apply_expanded_assets(folder)'])
 changed['tools/reference/pack_chr.py']=pack.replace(token,token+nlp+hook)
 paths={}
 for name,blob in changed.items():
  path=B/(P+'_'+Path(name).name);assert not path.exists();path.write_bytes(blob);paths[name]=path
 ep=paths['src/entrypoint.s'];text=ep.read_bytes()
 for name in ['remaining_weapons.s','samus_fixed_hud.s']:text=text.replace(b'.include "'+name.encode()+b'"',b'.include "'+paths['src/'+name].name.encode()+b'"')
 text=text.replace(b'.incbin "chr/characters/packed-mmc5-expanded.chr"',b'.incbin "build/'+paths['chr/characters/packed-mmc5-expanded.chr'].name.encode()+b'"');ep.write_bytes(text)
 c=B/(P+'_main.c');assert not c.exists();c.write_bytes((R/'src/main.c').read_bytes())
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(R/'build_options.ini');defs={k:v for s in cfg.values()for k,v in s.items()};defs.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
 out=B/(P+'.nes');assert not out.exists()
 cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(R/'smb1base-mmc5-expanded.cfg'),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),'--include-dir',str(R),'--asm-include-dir',str(B),'--asm-include-dir',str(R/'src'),'--asm-include-dir',str(R),'--bin-include-dir',str(R),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
 for k,v in defs.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd+=[str(c),str(ep)];z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,z.stdout+z.stderr
 sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare;prepare(R,out)
 new=scoped_load(out);expected=bytearray(raw)
 for i in delta:expected[i]=prior[i]
 assert new['raw']==expected,'Source build must equal exact disjoint byteunion'
 assert all(new['syms'].get(n,{}).get('val')==s.get('val')and new['syms'].get(n,{}).get('seg')==s.get('seg')for n,s in old['syms'].items())
 assert sha(BASE)==EXPECTED
 patch=[]
 for name,blob in changed.items():
  if not name.endswith('.chr'):patch+=difflib.unified_diff((R/name).read_text().splitlines(True)if(R/name).exists()else[],blob.decode().splitlines(True),fromfile='a/'+name,tofile='b/'+name)
 pp=B/(P+'.patch');pp.write_text(''.join(patch),newline='\n')
 proof=dict(source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(out),ROM=str(out),disjoint_exact9d1_union=True,changed_PRG_bytes=46,PRG_bank=61,changed_CHR_bytes=24,CHR_page=20,all_old_symbol_values_segments_exact=len(old['syms']),source_overlay={n:dict(path=str(p),sha256=sha(p))for n,p in paths.items()},recipe=recipe,ordinary_native_enemies_untouched=True,ordinary_packed_assets_untouched=True,command=cmd,bindings={str(p):sha(p)for p in [Path(__file__),R/'tools/reference/patch_samus_fixed_hud_v2.py',BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),B/'samus_fixed_hud_handoff.json',B/'samus_fixed_hud_controls.json',R/'tools/reference/pack_chr.py',R/'chr/mmc5/sprites_enemies.chr',R/'chr/characters/packed-mmc5.chr',R/'chr/characters/packed-mmc3.chr',pp]})
 p=B/(P+'_build.json');assert not p.exists();p.write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print(json.dumps(dict(ROM_sha256=sha(out),proof_sha256=sha(p))))
if __name__=='__main__':main()
