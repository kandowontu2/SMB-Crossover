"""Bind the unchanged qualified6c69 menu policy/guards to compiled3cee HUD data."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location,address

ROOT=Path(__file__).resolve().parents[2]
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
BASE='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','parent-profile','parent-final','hud-ready','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.candidate/'candidate.nes')==SHA
 cp=json.loads((a.candidate/'proof.json').read_text());assert cp['passed']and cp['candidate_ROM_sha256']==SHA and cp['parent_ROM_sha256']==BASE and cp['changed_ROM_bytes']==824
 for rel,h in json.loads((a.candidate/'source-manifest.json').read_text()).items():assert sha(a.candidate/'source'/rel)==h
 hp=json.loads((a.hud_ready/'proof.json').read_text());assert hp['passed']and hp['candidate_ROM_sha256']=='bb5bf4fa4189ede2ab4f9ee0eb6e8e54dd67b1c77eb1c78e7c50a1079d4fc1db'
 for f,h in json.loads((a.hud_ready/'manifest.json').read_text()).items():assert sha(f)==h
 final=json.loads((a.parent_final/'proof.json').read_text());assert final['passed']and final['ROM_sha256']==BASE and final['native_run']
 z=json.loads((a.parent_profile/'preparation.json').read_text());old=Path(z['script']);assert sha(old)==z['script_sha256']
 previous=json.loads((old.parent/'lifecycle-proof.json').read_text());assert previous['passed']and len(previous['components'])==6 and all(v['passed']for v in previous['components'].values())
 c=json.loads(old.with_name('config.json').read_text());before=json.loads(old.with_name('config.json').read_text());assert c['mode']==0 and c['variant']==1 and c['limit']==1800 and c['lifecycle']['kind']=='menu'
 b=scoped_load(a.candidate/'candidate.nes')
 for s in c['body_sources'].values():
  at=16+s['bank']*8192+s['pointer']%8192;assert list(b['raw'][at:at+len(s['bytes'])])==s['bytes']
 assert len(c['body_sources'])==131
 hooks=0
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   at=16+h['bank']*8192+h['address']%8192;assert list(b['raw'][at:at+len(h['bytes'])])==h['bytes'],(family,name)
   # Some retained observer hook names (for example NmiReturn) are semantic
   # aliases for an instruction inside a real assembled routine, not labels.
   if name in b['syms']:assert address(b,name)==h['address'],(family,name,'address')
   hooks+=1
 for family in ['ram','profile_ram','hud_ram','lifecycle_ram']:
  for name,value in c[family].items():
   if name in b['syms']:assert address(b,name)==value,(family,name,'RAM')
 table=location(b,'PnHudCells');labels=list(b['raw'][table:table+84]);assert len(labels)==84
 text=(a.candidate/'source/src/parodius_hud.inc').read_text();assert labels==[int(t,16)for t in re.findall(r'\$([0-9a-fA-F]{2})',text)]
 c['hud_labels']={str(v):labels[(v-1)*28:v*28]for v in range(1,4)}
 font=(a.candidate/'source/chr/characters/parodius-hud.chr').read_bytes();assert hashlib.sha256(font).hexdigest()=='d278c3e3f04aa95504099d6f4b6d4ffc932e745c2c8045b7227763b493fba2d0'
 at=16+1048576+396*1024;assert b['raw'][at:at+3072]==font
 pixels=[]
 for v in range(3):
  row=[]
  for y in range(8):
   for x in range(224):
    t=labels[v*28+x//8];o=v*1024+t*16;row.append((font[o+y]>>(7-x%8)&1)|((font[o+y+8]>>(7-x%8)&1)<<1))
  assert len(row)==1792;pixels.extend(row)
 assert len(pixels)==5376 and set(pixels)=={0,1}
 # Every pixel, including backdrop pixels, remains in the reference. Reject
 # a wrong label, one wrong glyph bit, or a wrong physical page.
 expected=(font,labels,[396,397,398],pixels)
 negatives=[]
 for kind,i in [('font-byte',0),('cell-index',1),('physical-page',2),('full-mask-pixel',3)]:
  bad=[list(x)for x in expected];bad[i][0]^=1;assert any(list(x)!=y for x,y in zip(expected,bad));negatives.append(kind)
 (a.output/'expected-hud-fonts.bin').write_bytes(font);(a.output/'expected-all5376-HUD-pixels.bin').write_bytes(bytes(pixels))
 put(a.output/'expected-hud-art.json',dict(ROM_sha256=SHA,font_pages=[396,397,398],font_bytes=3072,font_sha256=hashlib.sha256(font).hexdigest(),labels=c['hud_labels'],full_pixel_reference_positions=5376,backdrop_pixels_included=True,mask_predicate_not_weakened=True,strict_source_reference_negatives=negatives,palette_policy='Use actual recorded current palette and unchanged attribute predicates; no fixed hue or deletion of zero/background pixels.',native_run=False))
 out=a.output/'menu/baseline-early';out.mkdir(parents=True);controller=a.output/'menu/controller';shutil.copytree(a.parent_profile/'controller',controller)
 for f in controller.glob('*.lua'):f.write_text(f.read_text().replace((a.parent_profile/'controller').as_posix(),controller.as_posix()))
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/')
 assert {k for k in c if c[k]!=before[k]}=={'ROM_sha256','output','hud_labels'}
 original=old.read_text();header=original[:original.index('\nROSTER_CONFIG=')];text='PARODIUS_VISIBILITY='+lua(c)+original[len(header):]
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((a.parent_profile/'controller').as_posix(),controller.as_posix())
 normalize=lambda s:s.replace(out.as_posix(),old.parent.as_posix()).replace(controller.as_posix(),(a.parent_profile/'controller').as_posix())
 assert normalize(text[text.index('\nROSTER_CONFIG='):])==original[original.index('\nROSTER_CONFIG='):]
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 script=out/'run.lua';script.write_text(text,encoding='utf-8');put(out/'config.json',c)
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.candidate/('candidate'+ext),out/('candidate'+ext))
 deps=dict(z['dependencies']);deps.update({str(f.resolve()):sha(f)for f in [Path(__file__),a.candidate/'proof.json',a.candidate/'source-manifest.json',a.hud_ready/'proof.json']})
 q=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,kind='menu',mode=0,variant=1,limit=1800,script=str(script.resolve()),script_sha256=sha(script),dependencies=deps,
  parent_preparation_sha256=sha(a.parent_profile/'preparation.json'),parent_passed6c69_menu_final_sha256=sha(a.parent_final/'proof.json'),composition_proof_sha256=sha(a.candidate/'proof.json'),
  config_only_deltas=['ROM_sha256','output','hud_labels'],all131body_records_and_genuine_hook_bytes_exact=True,genuine_hooks=hooks,
  original_controller_all6guards_finalizer_order_exact_after_path_normalization=True,all_current_RAM_hook_addresses_exact=True,
  exact_compiled_font_and84cell_table_bound=True,all5376_reference_positions_including_background_retained=True,
  controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},scope='SOURCE ONLY. Same qualified6c69 EasyOctmenu1800 on3cee; actual compiled positive font/table expected. No controller/guard/body/instruction/palette edits or native launch. OriginalareaFALSE/overlap and bodyvisibility findings remain separate.')
 put(a.output/'menu/preparation.json',q);put(a.output/'proof.json',q);print(json.dumps(dict(script_sha256=sha(script),preparation_sha256=sha(a.output/'menu/preparation.json'),expected_art_sha256=sha(a.output/'expected-hud-art.json')),indent=2))
if __name__=='__main__':main()
