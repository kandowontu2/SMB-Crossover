"""Rebind the successful5354menu1800 behavior/guards to current private4285."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
ROOT=Path(__file__).resolve().parents[2]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','parent-profile','parent-final','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(a.candidate/'candidate.nes')==SHA
 final=json.loads((a.parent_final/'proof.json').read_text());assert final['passed']and final['ROM_sha256']=='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
 z=json.loads((a.parent_profile/'preparation.json').read_text());old=Path(z['script']);assert sha(old)==z['script_sha256']
 c=json.loads(old.with_name('config.json').read_text());assert c['limit']==1800 and c['mode']==0 and c['variant']==1 and c['lifecycle']['kind']=='menu'
 b=scoped_load(a.candidate/'candidate.nes');out=a.output/'menu/baseline-early';out.mkdir(parents=True);controller=a.output/'menu/controller';shutil.copytree(a.parent_profile/'controller',controller)
 for f in controller.glob('*.lua'):f.write_text(f.read_text().replace((a.parent_profile/'controller').as_posix(),controller.as_posix()))
 assert len(c['body_sources'])==131
 for s in c['body_sources'].values():
  at=16+s['bank']*8192+s['pointer']%8192;assert list(b['raw'][at:at+len(s['bytes'])])==s['bytes']
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   at=16+h['bank']*8192+h['address']%8192;assert list(b['raw'][at:at+len(h['bytes'])])==h['bytes'],name
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/')
 oldtext=old.read_text();header=oldtext[:oldtext.index('\nROSTER_CONFIG=')];text='PARODIUS_VISIBILITY='+lua(c)+oldtext[len(header):]
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((a.parent_profile/'controller').as_posix(),controller.as_posix())
 static=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';body=static.read_text();assert text.count(body)==1
 early='emu.addEventCallback(function()PARODIUS_HUD_LEASE_FINISH()end,emu.eventType.endFrame)\n'
 text=text.replace(body,early+body)
 layer=ROOT/'tools/audit/parodius_visibility_hud_lease_native_v2.lua';anchor='\ndofile('+lua((controller/'harness.lua').as_posix())+')';assert text.count(anchor)==1
 text=text.replace(anchor,'\n'+layer.read_text()+anchor)
 # Removing only additive lease layer/slot and normalizing isolated paths
 # leaves the complete historical menu controller/guard tail byte exact.
 normalize=lambda s:s.replace(out.as_posix(),old.parent.as_posix()).replace(controller.as_posix(),(a.parent_profile/'controller').as_posix())
 tail=text[text.index('\nROSTER_CONFIG='):].replace(early,'').replace('\n'+layer.read_text(),'')
 assert normalize(tail)==oldtext[oldtext.index('\nROSTER_CONFIG='):]
 script=out/'run.lua';script.write_text(text,encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.candidate/('candidate'+ext),out/('candidate'+ext))
 deps=dict(z['dependencies']);deps.update({str(f.resolve()):sha(f)for f in [Path(__file__),layer]})
 q=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,mode=0,variant=1,kind='menu',limit=1800,
        script=str(script.resolve()),script_sha256=sha(script),dependencies=deps,
        parent_final_sha256=sha(a.parent_final/'proof.json'),parent_preparation_sha256=sha(a.parent_profile/'preparation.json'),
        controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},
        all_original_menu_controller_and_guard_tail_exact_after_path_normalization=True,all131body_records_and_hook_bytes_exact=True,
        scope='SOURCE-ONLY separate focused1800 menu smoke; historical5354 all4variant/cancel/title/reentry behavior and every original5guard exact. Additional actualHUDpair layer finalizes before originalstop. No area/death/Hard/retry/adoption scope; originalareaFALSE/pendingBuffer2limitation untouched.')
 (a.output/'menu/preparation.json').write_text(json.dumps(q,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps(dict(script_sha256=sha(script),preparation_sha256=sha(a.output/'menu/preparation.json'),dependencies=len(deps)),indent=2))


if __name__=='__main__':main()
