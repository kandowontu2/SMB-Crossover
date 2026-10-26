"""Bind e11 reordered body records to the byte-exact completed cold observer."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
from final_roll_items_prepare import lua
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--bindings',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.parent/'preparation.json').read_text());old=Path(z['script']).parent;assert sha(old/'run.lua')==z['script_sha256'];assert json.loads((old/'scroll-proof.json').read_text())['passed'];frozen=a.bindings/'frozen';assert sha(frozen/'candidate.nes')=='e11c64ec155fd90a55604ec4cc8f9f722f97fa79140eb861dd4ffec31601d5da';data=json.loads((a.bindings/'body-aliases.json').read_text());sources=data['body_sources'];raw=(frozen/'candidate.nes').read_bytes()
 for key,v in sources.items():bank,ptr=map(int,key.split(':'));at=16+bank*8192+ptr%8192;assert raw[at:at+len(v['bytes'])]==bytes(v['bytes']);assert all(ref['body']for ref in v['refs'])
 out=a.output/'baseline-early';out.mkdir();controller=a.output/'controller';controller.mkdir();oldcontroller=a.parent/'controller'
 for f in oldcontroller.iterdir():
  if f.is_file():shutil.copy2(f,controller/f.name)
 policy=controller/'policy.lua';policy.write_text(policy.read_text().replace(oldcontroller.as_posix(),controller.as_posix()),encoding='utf-8')
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(frozen/('candidate'+ext),out/('candidate'+ext))
 c=json.loads((old/'config.json').read_text());original_config=json.loads(json.dumps(c));assert c['limit']==640 and c['mode']==0 and c['variant']==1;c.update(ROM_sha256=sha(out/'candidate.nes'),body_sources=sources,output=out.as_posix()+'/')
 for family in ['hooks','hud_hooks']:
  for name,h in c[family].items():at=16+h['bank']*8192+h['address']%8192;assert list(raw[at:at+len(h['bytes'])])==h['bytes'],name
 tail=(old/'run.lua').read_text().split('\n',1)[1];tail=tail.replace(old.as_posix(),out.as_posix()).replace(oldcontroller.as_posix(),controller.as_posix());text='PARODIUS_VISIBILITY='+lua(c)+'\n'+tail;script=out/'run.lua';script.write_text(text,encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
 static=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';assert text.count(static.read_text())==1;assert 'PARODIUS_INVALIDATE_PUBLICATION'not in text and 'PARODIUS_LIFECYCLE'not in text;assert text.rstrip().endswith('PARODIUS_STATIC_INSTALL_RETURNS()');sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 deps=dict(z['dependencies']);deps.update({str(f.resolve()):sha(f)for f in [Path(__file__),ROOT/'tools/audit/parodius_visibility_combined_cold_run_v1.py',a.bindings/'body-aliases.json',a.bindings/'frozen-ledger.json']});snap=a.output/'dependency-snapshots';snap.mkdir()
 for name,digest in deps.items():dest=snap/Path(name).name;shutil.copy2(name,dest);assert sha(dest)==digest
 q=dict(z,ROM_sha256=c['ROM_sha256'],script=str(script),script_sha256=sha(script),dependencies=deps,controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},parent_preparation_sha256=sha(a.parent/'preparation.json'),body_aliases_sha256=sha(a.bindings/'body-aliases.json'),source_frozen_ledger_sha256=sha(a.bindings/'frozen-ledger.json'),scope='SOURCE PREPARATION ONLY. Exact old completed OctEasy640 controller/HUD/scroll/static observer bodies; only ROM/body-source table/output paths rebound. No lifecycle module, latch invalidation, emulated state writes or new art. Actual PPU570..620 is a search window, never an assumed old DMA epoch.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');changed=sorted(k for k in c if c[k]!=original_config[k]);assert changed==['ROM_sha256','body_sources','output'];proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=c['ROM_sha256'],preparation_sha256=sha(a.output/'preparation.json'),script_sha256=sha(script),tool_sha256=sha(Path(__file__)),config_changed_fields=changed,body_records=len(sources),static_observer_sha256=sha(static),old_observer_body_exact=True,all_other_script_layers_exact_except_isolated_paths=True,original_input_stream_exact=sha(controller/'inputs.csv')==sha(oldcontroller/'inputs.csv'),controller_harness_exact=sha(controller/'harness.lua')==sha(oldcontroller/'harness.lua'),lifecycle_invalidation_present=False,scope='Separate initial cold control only. No native pass, crowded-pixel improvement, other-actor fairness or cadence claim.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof,indent=2))

if __name__=='__main__':main()
