"""Freeze a new observer revision while retaining the same ROM/controllers."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--rom',type=Path);p.add_argument('--expect-sha');p.add_argument('--strict',action='store_true');p.add_argument('--route',type=Path);p.add_argument('--behavior',choices=['easy','hard'],default='easy');p.add_argument('--variant',type=int,choices=[1,2,3],default=1);p.add_argument('--name',choices=['octopus','twinbee','pentarou'],default='octopus');p.add_argument('--adaptive',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.parent/'preparation.json').read_text(encoding='utf-8'));old=Path(z['script']).parent;controller=a.parent/'controller'
 if a.route:
  controller=a.output/'controller';controller.mkdir()
  for name in ['harness.lua','policy.lua','inputs.csv','manifest.json']:shutil.copy2(a.route/name,controller/name)
  original_guard=a.route.parent/'native-guard.lua';shutil.copy2(original_guard,controller/'native-guard.lua');text=(controller/'policy.lua').read_text(encoding='utf-8');assert text.count(original_guard.as_posix())==1;(controller/'policy.lua').write_text(text.replace(original_guard.as_posix(),(controller/'native-guard.lua').as_posix()),encoding='utf-8')
 c=json.loads((old/'config.json').read_text(encoding='utf-8'));out=a.output/'baseline-early';out.mkdir();c['output']=out.as_posix()+'/';c['diagnostic']=not a.strict;c['mode']=int(a.behavior=='hard');c['variant']=a.variant
 actual=a.rom or old/'candidate.nes';assert not a.rom or a.expect_sha and sha(actual)==a.expect_sha;c['ROM_sha256']=sha(actual)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(actual.with_suffix(ext),out/('candidate'+ext))
 b=scoped_load(out/'candidate.nes');c['profile_hooks']=['SamusFreezeUpdateScreen','UpdateScreen','BankSwitchCHR','AudioUpdate','OAMandReadJoypad'];c['profile_ram']={n:address(b,n)for n in ['NmiDisable','DisableScreenFlag','VRAM_Buffer_AddrCtrl','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','NmiR0','NmiR1','ReloadCHRBank','FrameCounter','Sprite0HitDetectFlag']}
 for n in c['profile_hooks']:
  at=location(b,n);c['hooks'][n]=dict(address=address(b,n),bank=(at-16)//8192,bytes=list(b['raw'][at:at+3]))
 n='IrqScrollSplit';delta=int(b['syms'][n]['size'],0)-1;at=location(b,n)+delta;assert b['raw'][at]==64;c['hooks']['IrqReturn']=dict(address=address(b,n)+delta,bank=(at-16)//8192,bytes=[64])
 cfg=dict(name=a.name,slot=17,character=18,variant=a.variant,variantSymbol='VvVariant',menuName=a.name.upper(),mapper='mmc5',behavior=a.behavior,limit=18000,out=out.as_posix()+'/',record=False,allowDeaths=False,segmented=False,capture=0,policy=(controller/'policy.lua').as_posix(),replay=None if a.adaptive else(controller/'inputs.csv').as_posix())
 module=ROOT/'tools/audit/parodius_visibility_observer.lua';script=out/'run.lua';script.write_text('PARODIUS_VISIBILITY='+lua(c)+'\nROSTER_CONFIG='+lua(cfg)+'\n'+module.read_text(encoding='utf-8')+'\ndofile('+lua((controller/'harness.lua').as_posix())+')\n',encoding='utf-8');(out/'config.json').write_text(json.dumps(c,indent=2)+'\n',encoding='utf-8')
 sys.path.insert(0,str(a.parser_root));from luaparser import ast;ast.parse(script.read_text(encoding='utf-8'))
 deps={str(p):sha(p)for p in [Path(__file__),module,ROOT/'tools/audit/parodius_visibility_run.py',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/audit/final_roll_items_prepare.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/check_tmnt_render_oa.py']}
 snapshots=a.output/'dependency-snapshots';snapshots.mkdir();snapshot_bindings={}
 for name,digest in deps.items():dest=snapshots/Path(name).name;shutil.copy2(name,dest);assert sha(dest)==digest;snapshot_bindings[name]=str(dest)
 q=dict(z,ROM_sha256=c['ROM_sha256'],mode=c['mode'],variant=c['variant'],input_mode='fresh legal adaptive menu/route inputs, recorded to inputs.csv'if a.adaptive else'exact frozen historical input stream',controller={p.name:sha(p)for p in controller.iterdir()if p.is_file()},strict=bool(a.strict),script=str(script),script_sha256=sha(script),observer_sha256=sha(module),dependencies=deps,dependency_snapshots=snapshot_bindings,parent_preparation_sha256=sha(a.parent/'preparation.json'),scope='Exact pinned ROM and disclosed historical/adaptive controller; actual DMA/PPU/routine-cost observer. Diagnostic mode retains failures as overallpassed=false; strict mode stops on any such failure. No emulated state changes.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(preparation_sha256=sha(a.output/'preparation.json'),script_sha256=sha(script))))
if __name__=='__main__':main()
