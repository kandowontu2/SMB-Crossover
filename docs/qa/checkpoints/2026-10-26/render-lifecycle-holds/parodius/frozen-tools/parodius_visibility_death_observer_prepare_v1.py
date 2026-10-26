"""Prepare a separately versioned same-ROM death observer; never launch Mesen."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['parent-profile','records-proof','parser-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 proof=json.loads((a.records_proof/'proof.json').read_text());assert proof['passed'] and proof['ROM_sha256']==SHA and proof['death_records']==13
 for n,h in proof['files'].items():assert sha(a.records_proof/n)==h
 z=json.loads((a.parent_profile/'preparation.json').read_text());old=Path(z['script']);assert sha(old)==z['script_sha256'] and sha(old.with_name('candidate.nes'))==SHA
 parent=json.loads(old.with_name('config.json').read_text());assert parent['mode']==0 and parent['variant']==1 and len(parent['body_sources'])==131
 cfg=json.loads(json.dumps(parent));sources=json.loads((a.records_proof/'death-sources.json').read_text())
 for v in sources.values():v['refs']=[dict(variant=v['variant'],frame=v['frame'],phase='death',body=True,native_death=True)]
 assert set(sources).isdisjoint(parent['body_sources']);cfg['death_sources']=sources
 out=a.output/'death/baseline-early';out.mkdir(parents=True)
 controller=a.output/'death/controller';shutil.copytree(a.parent_profile/'controller',controller)
 b=scoped_load(old.with_name('candidate.nes'))
 for n in ['MmDeathFlag','PnSkin','PnAnimation','ObjectMetasprite','SmChrBank','CurrentCHRBank','X5ChrMode']:cfg['ram'][n]=address(b,n)
 for n in ['VvGraphics','PnDeathGraphics']:
  at=location(b,n);cfg['hooks'][n]=dict(address=address(b,n),bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]))
 cfg['output']=out.as_posix()+'/'
 static1=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';static2=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v2.lua'
 before=static1.read_text();after=static2.read_text()
 first=after.index('-- Separately qualified death records');last=after.index("hook('MetaspriteRenderLoop',function()",first)
 restored=(after[:first]+after[last:]).replace("local source=assert(bodySource(ptr,physical),'Actual body immutable record alias')","local source=assert(C.body_sources[tostring(physical)..':'..ptr],'Actual body immutable record alias')")
 assert restored==before,'All original guard bodies remain exact except narrow qualified-source lookup'
 text=old.read_text();assert text.count(before)==1
 text=text.replace(before,after)
 old_header=text[:text.index('\nROSTER_CONFIG=')];assert old_header.startswith('PARODIUS_VISIBILITY=')
 text='PARODIUS_VISIBILITY='+lua(cfg)+text[len(old_header):]
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((a.parent_profile/'controller').as_posix(),controller.as_posix())
 script=out/'run.lua';script.write_text(text,encoding='utf-8');(out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 assert cfg['body_sources']==parent['body_sources']
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(old.with_name('candidate'+ext),out/('candidate'+ext))
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(text)
 prep=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,script=str(script.resolve()),script_sha256=sha(script),
           parent_preparation_sha256=sha(a.parent_profile/'preparation.json'),body_records=131,death_records=13,mode=0,variant=1,
           dependencies={str(f.resolve()):sha(f)for f in [Path(__file__),static1,static2,ROOT/'tools/audit/final_roll_items_prepare.py',a.records_proof/'proof.json',a.records_proof/'death-sources.json']},
           scope='Same5354, same original death controller and original lifecycle/PPU/DMA/NMI/IRQ/CHR guards. Separate source-only immutable death metadata and owner guard; no native launch/coverage.',
           original131live_sources_exact=True,old_guard_bodies_restored_text_exact=True,no_emulated_writes=True)
 (a.output/'death/preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
 (a.output/'proof.json').write_text(json.dumps(dict(**prep,profiles=[dict(kind='death',limit=2200,packet=str((a.output/'death').resolve()))]),indent=2)+'\n')
 bindings={str(f.resolve()):sha(f)for f in a.output.rglob('*')if f.is_file()}
 bindings[str(a.parent_profile/'preparation.json')]=sha(a.parent_profile/'preparation.json')
 (a.output/'manifest.json').write_text(json.dumps(bindings,indent=2)+'\n');print(json.dumps(prep,indent=2))


if __name__=='__main__':main()
