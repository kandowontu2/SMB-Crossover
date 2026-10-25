"""Freeze current50b5 and a read-only actual-body/publication/PPU observer."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
CURRENT='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--route',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 assert sha(a.rom)==CURRENT;a.output.mkdir(parents=True,exist_ok=False);f=a.output/'frozen';f.mkdir()
 for n in ['src','inc','audio','chr']:shutil.copytree(ROOT/n,f/n)
 for n in ['build_options.ini','smb1base.cfg','smb1base-mmc5-expanded.cfg']:shutil.copy2(ROOT/n,f/n)
 for n in ['tools/reference','reference/parodius-nes']:shutil.copytree(ROOT/n,f/n)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.rom.with_suffix(ext),f/('candidate'+ext))
 for n in ['build_mmc5_expanded.py','prepare_cv3_dmc_mirror.py']:shutil.copy2(ROOT/'tools'/n,f/'tools'/n)
 (f/'tools/audit').mkdir(parents=True)
 ledger={q.relative_to(f).as_posix():sha(q)for q in sorted(f.rglob('*'))if q.is_file()};(a.output/'frozen-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
 b=scoped_load(f/'candidate.nes');manifest=json.loads((f/'reference/parodius-nes/art/packed/manifest.json').read_text());sources={};aliases={}
 for pool in manifest['pools']:
  variant=pool['variant'];base=location(b,'PnPool'+str(pool['index'])+'Lo');hi=location(b,'PnPool'+str(pool['index'])+'Hi');indices=location(b,'PnFrameIndexV'+str(variant));bank=(base-16)//8192
  for frame,parts in pool['records'].items():
   index=b['raw'][indices+int(frame)];assert index
   ptr=b['raw'][base+index]+256*b['raw'][hi+index];key=f'{bank}:{ptr}';at=16+bank*8192+ptr%8192;data=bytes([len(parts)*4]+[v for part in parts for v in part]);assert b['raw'][at:at+len(data)]==data
   ref=dict(pool=pool['index'],variant=variant,phase=pool['phase'],frame=int(frame),body=int(frame)in pool['body_frames']);aliases.setdefault(key,[]).append(ref)
   if ref['body']:
    label=next((n for n in b['syms']if re.fullmatch(r'PnRecordV\d+N\d+',n)and address(b,n)==ptr and(location(b,n)-16)//8192==bank),None);assert label
    sources[key]=dict(bank=bank,pointer=ptr,label=label,parts=parts,bytes=list(data),refs=[])
 for key,z in sources.items():z['refs']=aliases[key];assert all(q['body']for q in aliases[key])
 (a.output/'record-aliases.json').write_text(json.dumps(dict(all_records=aliases,body_sources=sources,body_nonbody_aliases=[]),indent=2)+'\n',encoding='utf-8')
 hooks={}
 for n in ['GameLoop','DrawAllMetasprites','PnDraw','DrawMetasprite','MetaspriteRenderLoop','RosterOamReady','NonMaskableInterrupt','IrqScrollSplit']:
  at=location(b,n);hooks[n]=dict(address=address(b,n),bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]))
 for key,n in [('NmiReturn','NonMaskableInterrupt')]:
  delta=int(b['syms'][n]['size'],0)-1;at=location(b,n)+delta;assert b['raw'][at]==64;hooks[key]=dict(address=address(b,n)+delta,bank=(at-16)//8192,bytes=[64])
 module=ROOT/'tools/audit/parodius_visibility_observer.lua';text=module.read_text(encoding='utf-8')
 needed=set(re.findall(r"\br\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'\bD\.([A-Za-z_][A-Za-z_0-9]*)',text));ram={n:address(b,n)for n in needed}
 c=dict(ROM_sha256=CURRENT,mode=0,variant=1,character=18,start_frame=500,capture_start=570,capture_end=620,limit=640,ram=ram,hooks=hooks,body_sources=sources,smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 controller=a.output/'controller';controller.mkdir()
 for name in ['harness.lua','policy.lua','inputs.csv','manifest.json']:shutil.copy2(a.route/name,controller/name)
 guard=a.route.parent/'native-guard.lua';shutil.copy2(guard,controller/'native-guard.lua')
 old=guard.as_posix();policy=(controller/'policy.lua').read_text(encoding='utf-8');assert policy.count(old)==1;(controller/'policy.lua').write_text(policy.replace(old,(controller/'native-guard.lua').as_posix()),encoding='utf-8')
 out=a.output/'baseline-early-v1';out.mkdir();c['output']=out.as_posix()+'/'
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(f/('candidate'+ext),out/('candidate'+ext))
 cfg=dict(name='octopus',slot=17,character=18,variant=1,variantSymbol='VvVariant',menuName='OCTOPUS',mapper='mmc5',behavior='easy',limit=18000,out=out.as_posix()+'/',record=False,allowDeaths=False,segmented=False,capture=0,policy=(controller/'policy.lua').as_posix(),replay=(controller/'inputs.csv').as_posix())
 script=out/'run.lua';script.write_text('PARODIUS_VISIBILITY='+lua(c)+'\nROSTER_CONFIG='+lua(cfg)+'\n'+text+'\ndofile('+lua((controller/'harness.lua').as_posix())+')\n',encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(script.read_text(encoding='utf-8'));assert not re.search(r'(?<!\w)(True|False)(?!\w)',script.read_text(encoding='utf-8'))
 deps={str(p):sha(p)for p in [Path(__file__),module,ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py']}
 prep=dict(prepared=True,native_passed=False,goal_complete=False,ROM_sha256=CURRENT,script=str(script),script_sha256=sha(script),observer_sha256=sha(module),dependencies=deps,frozen_ledger_sha256=sha(a.output/'frozen-ledger.json'),record_aliases_sha256=sha(a.output/'record-aliases.json'),controller={p.name:sha(p)for p in controller.iterdir()if p.is_file()},source_route_manifest_sha256=sha(a.route/'manifest.json'),source_inputs_sha256=sha(a.route/'inputs.csv'),scope='Read-only fixed historical Octopus Easy controller on frozen current50b5. Actual source/body/rotation/world-prefill/publication/DMA/PPU epochs; stop640, no clear claim. No emulated state or OAM writes. Historical frame586/587 is only a search region, not assumed current DMA/image alignment.')
 (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(preparation_sha256=sha(a.output/'preparation.json'),script_sha256=sha(script),body_records=len(sources),all_records=len(aliases))))
if __name__=='__main__':main()
