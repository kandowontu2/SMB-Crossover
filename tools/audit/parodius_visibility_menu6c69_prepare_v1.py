"""Metadata-only rebind of the exact passed4285menu fixture to three-byte6c69."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
ROOT=Path(__file__).resolve().parents[2]
SHA='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','source-ready','parent-profile','parent-final','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(a.source_ready)=='9225b3bafce11ac542d6d10725d7e2ca99757bf586d908ff469af943f045722f'
 assert sha(a.candidate/'candidate.nes')==SHA
 final=json.loads((a.parent_final/'proof.json').read_text());assert final['passed']and final['current_menu_all6native_components_passed']and final['ROM_sha256']=='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
 z=json.loads((a.parent_profile/'preparation.json').read_text());old=Path(z['script']);assert sha(old)==z['script_sha256']
 before=old.with_name('candidate.nes').read_bytes();after=(a.candidate/'candidate.nes').read_bytes();different=[i for i,(x,y)in enumerate(zip(before,after))if x!=y]
 assert len(before)==len(after)and different==[33409,33410,33411]and before[33409:33412]==b'\xea\xea\xea'and after[33409:33412]==b'\x4c\x85\xa2'
 assert old.with_name('candidate.lbl').read_bytes()==(a.candidate/'candidate.lbl').read_bytes(),'All public/RAM labels byte-exact'
 c=json.loads(old.with_name('config.json').read_text());assert c['mode']==0 and c['variant']==1 and c['limit']==1800 and c['lifecycle']['kind']=='menu'
 b=scoped_load(a.candidate/'candidate.nes')
 for s in c['body_sources'].values():
  at=16+s['bank']*8192+s['pointer']%8192;assert list(b['raw'][at:at+len(s['bytes'])])==s['bytes']
 assert len(c['body_sources'])==131
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   at=16+h['bank']*8192+h['address']%8192;assert list(b['raw'][at:at+len(h['bytes'])])==h['bytes'],name
 out=a.output/'menu/baseline-early';out.mkdir(parents=True);controller=a.output/'menu/controller';shutil.copytree(a.parent_profile/'controller',controller)
 for f in controller.glob('*.lua'):f.write_text(f.read_text().replace((a.parent_profile/'controller').as_posix(),controller.as_posix()))
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/')
 original=old.read_text();header=original[:original.index('\nROSTER_CONFIG=')];text='PARODIUS_VISIBILITY='+lua(c)+original[len(header):]
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((a.parent_profile/'controller').as_posix(),controller.as_posix())
 normalize=lambda s:s.replace(out.as_posix(),old.parent.as_posix()).replace(controller.as_posix(),(a.parent_profile/'controller').as_posix())
 assert normalize(text[text.index('\nROSTER_CONFIG='):])==original[original.index('\nROSTER_CONFIG='):]
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 script=out/'run.lua';script.write_text(text,encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.candidate/('candidate'+ext),out/('candidate'+ext))
 dependencies=dict(z['dependencies']);dependencies.update({str(f.resolve()):sha(f)for f in [Path(__file__),a.source_ready]})
 q=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,kind='menu',mode=0,variant=1,limit=1800,
        script=str(script.resolve()),script_sha256=sha(script),dependencies=dependencies,parent_preparation_sha256=sha(a.parent_profile/'preparation.json'),
        parent_passed_menu_final_sha256=sha(a.parent_final/'proof.json'),padding_source_ready_sha256=sha(a.source_ready),
        exact_ROM_delta_offsets=different,public_RAM_label_file_exact=True,all131body_records_and_hook_bytes_exact=True,
        original_controller_all6guards_finalizer_order_exact_after_path_normalization=True,
        controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},
        scope='SOURCE ONLY, one exactsame menu1800 on6c69. Only ROM/output metadata and isolated runtime paths differ. No newcontroller/guard/art/game-source edit or native launch. OriginalareaFALSE and overlap limitation remain separate.')
 (a.output/'menu/preparation.json').write_text(json.dumps(q,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(script_sha256=sha(script),preparation_sha256=sha(a.output/'menu/preparation.json')),indent=2))


if __name__=='__main__':main()
