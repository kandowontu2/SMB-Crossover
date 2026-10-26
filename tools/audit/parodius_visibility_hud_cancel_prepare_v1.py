"""Rebind one immutable death controller to privateF35 source/metadata/guards."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
SHA='f35f0ec2f70d5dcb6eb1bbfcbd84359d9f6da68c39719d75217aed149edb0631'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['parent-profile','candidate','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.parent_profile/'preparation.json').read_text());old=Path(z['script']);assert sha(old)==z['script_sha256'] and sha(a.candidate/'candidate.nes')==SHA
 c=json.loads(old.with_name('config.json').read_text());assert c['mode']==0 and c['variant']==1 and c['limit']==2200
 b=scoped_load(a.candidate/'candidate.nes');out=a.output/'death/baseline-early';out.mkdir(parents=True);controller=a.output/'death/controller';shutil.copytree(a.parent_profile/'controller',controller)
 counts={}
 for family in ['body_sources','death_sources']:
  for key,s in c[family].items():
   assert key==str(s['bank'])+':'+str(s['pointer']);at=16+s['bank']*8192+s['pointer']%8192;assert list(b['raw'][at:at+len(s['bytes'])])==s['bytes']
  counts[family]=len(c[family])
 assert counts==dict(body_sources=131,death_sources=13)
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   at=16+h['bank']*8192+h['address']%8192;assert list(b['raw'][at:at+len(h['bytes'])])==h['bytes'],name
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/')
 text=old.read_text();header=text[:text.index('\nROSTER_CONFIG=')];text='PARODIUS_VISIBILITY='+lua(c)+text[len(header):]
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((a.parent_profile/'controller').as_posix(),controller.as_posix())
 layer=ROOT/'tools/audit/parodius_visibility_hud_lease_native_v1.lua';anchor='\ndofile('+lua((controller/'harness.lua').as_posix())+')';assert text.count(anchor)==1;text=text.replace(anchor,'\n'+layer.read_text()+anchor)
 script=out/'run.lua';script.write_text(text,encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n')
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.candidate/('candidate'+ext),out/('candidate'+ext))
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 dependencies=dict(z['dependencies']);dependencies.update({str(f.resolve()):sha(f)for f in [Path(__file__),layer]})
 q=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,script=str(script.resolve()),script_sha256=sha(script),mode=0,variant=1,
        parent_preparation_sha256=sha(a.parent_profile/'preparation.json'),dependencies=dependencies,body_records=131,death_records=13,old_hook_bytes_exact=True,
        scope='Same frozen controller/death2200, new private cancellation ROM. All original five component guards and static observer retained; adds read-only all-life displayed label/font pairing. No native run/grant/adoption.')
 (a.output/'death/preparation.json').write_text(json.dumps(q,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
