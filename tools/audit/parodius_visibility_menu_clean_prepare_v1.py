"""Prepare a freshly pinned clean menu/NMI candidate; never launch an emulator."""
from pathlib import Path
import argparse,copy,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OLD=D/'parodius-menub0-preparation-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','source-ready','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--expected-sha256',required=True);a=p.parse_args();P=a.candidate;SHA=a.expected_sha256;assert not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True,exist_ok=False)
 assert sha(P/'candidate.nes')==SHA
 build=json.loads(a.source_ready.read_text());assert build['passed']and not build.get('native_run',False)
 original_shots=D/'root-chip-hud-composed-v1/source/src/protoman_legacy_shots.inc'
 assert(P/'source/src/protoman_legacy_shots.inc').read_bytes()==original_shots.read_bytes()
 assert'MM_PROTO_SHOT_MUX:'not in(P/'source/smb1base-mmc5-expanded.cfg').read_text()
 assert'MENU_VRAM_BUDGET:'in(P/'source/smb1base-mmc5-expanded.cfg').read_text()
 for n,h in json.loads((P/'source-manifest.json').read_text()).items():assert sha(P/'source'/n)==h,n
 prior=json.loads((OLD/'menu/preparation.json').read_text());old=Path(prior['script']);assert sha(old)==prior['script_sha256']
 for f,h in prior['dependencies'].items():assert sha(f)==h,f
 original=old.read_text();c=json.loads(old.with_name('config.json').read_text());before=copy.deepcopy(c)
 assert(c['mode'],c['variant'],c['character'],c['limit'],c['lifecycle']['kind'])==(0,1,18,1800,'menu')
 b=scoped_load(P/'candidate.nes');changes=[]
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   was=copy.deepcopy(h)
   if name in ['NmiReturn','IrqReturn']:
    n='NonMaskableInterrupt'if name=='NmiReturn'else'IrqScrollSplit';at=address(b,n)+int(b['syms'][n]['size'],0)-1;bank=(location(b,n)-16)//8192
   else:at=address(b,name);bank=(location(b,name)-16)//8192
   h.update(address=at,bank=bank,bytes=list(b['raw'][16+bank*8192+at%8192:16+bank*8192+at%8192+len(h['bytes'])]))
   if h!=was:changes.append(dict(family=family,name=name,before=was,after=h))
 for family in ['ram','profile_ram','hud_ram','lifecycle_ram']:
  for name,v in c[family].items():assert address(b,name)==v,(family,name)
 for q in c['body_sources'].values():
  off=16+q['bank']*8192+q['pointer']%8192;assert list(b['raw'][off:off+len(q['bytes'])])==q['bytes']
 assert len(c['body_sources'])==131
 assert(P/'source/chr/characters/parodius-hud.chr').read_bytes()==(D/'root-chip-hud-composed-v1/source/chr/characters/parodius-hud.chr').read_bytes()
 raw=b['raw'];labels=list(raw[location(b,'PnHudCells'):location(b,'PnHudCells')+84]);assert c['hud_labels']=={str(v):labels[(v-1)*28:v*28]for v in range(1,4)}
 dma=c['dma_protocol'];assert dma['next_pc']==0xe005 and dma['complete_pc']==0xe008 and dma['next_bytes']==list(raw[location(b,'OAMandReadJoypad')+5:location(b,'OAMandReadJoypad')+13])
 timing_hooks={}
 for alias,name in [('NmiEntry','NonMaskableInterrupt'),('UpdateScreen','UpdateScreen')]:
  off=location(b,name);timing_hooks[alias]=dict(pc=address(b,name),bank=(off-16)//8192,bytes=list(raw[off:off+3]))
 timing_hooks['DmaBefore']=dict(pc=dma['next_pc'],bank=127,bytes=dma['next_bytes'])
 timing_hooks['DmaComplete']=dict(pc=dma['complete_pc'],bank=127,bytes=dma['next_bytes'][3:])
 names=['DisableScreenFlag','CrossoverMenuState','OperMode','OperMode_Task','GameEngineSubroutine','NmiR0','NmiR1']
 c['early_timing']=dict(hooks=timing_hooks,ram={n:address(b,n)for n in names})
 out=a.output/'menu/baseline-early';out.mkdir(parents=True);controller=a.output/'menu/controller';shutil.copytree(OLD/'menu/controller',controller)
 for f in controller.glob('*.lua'):f.write_text(f.read_text().replace((OLD/'menu/controller').as_posix(),controller.as_posix()),encoding='utf-8')
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/')
 split=original.index('\nROSTER_CONFIG=');text='PARODIUS_VISIBILITY='+lua(c)+original[split:]
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((OLD/'menu/controller').as_posix(),controller.as_posix())
 timing=(R/'tools/audit/parodius_visibility_menu59_timing_v2.lua').read_text()
 # The additive module registers before the existing original observers and stop.
 text=text[:text.index('\nROSTER_CONFIG=')]+'\n'+timing+text[text.index('\nROSTER_CONFIG='):]
 norm=text.replace('\n'+timing,'',1);norm=norm[norm.index('\nROSTER_CONFIG='):].replace(out.as_posix(),old.parent.as_posix()).replace(controller.as_posix(),(OLD/'menu/controller').as_posix());assert norm==original[split:]
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(P/('candidate'+ext),out/('candidate'+ext))
 script=out/'run.lua';script.write_text(text,encoding='utf-8');put(out/'config.json',c)
 sys.path.insert(0,str(D/'final-tmnt-items-v1/lua-parser-deps-v1'));from luaparser import ast;ast.parse(text)
 for n in ['expected-hud-fonts.bin','expected-all5376-HUD-pixels.bin','expected-hud-art.json']:shutil.copy2(OLD/n,a.output/n)
 art=json.loads((a.output/'expected-hud-art.json').read_text());art['ROM_sha256']=SHA;put(a.output/'expected-hud-art.json',art)
 put(a.output/'hook-reconciliation.json',dict(passed=True,all_hook_bytes_actual=True,changed_hooks=changes,all_RAM_exact=True,all131_body_records_exact=True,original_E008_protocol_exact=True,early_timing=timing_hooks))
 deps=dict(prior['dependencies']);deps.update({str(f.resolve()):sha(f)for f in [Path(__file__),R/'tools/audit/parodius_visibility_menu59_timing_v2.lua',a.source_ready,P/'source-manifest.json',D/'parodius-menu-budget-c9-source-ready-v1/proof.json',D/'parodius-menu-budget-c9-source-ready-v1/manifest.json']})
 q=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,parent_ROM_sha256=prior['ROM_sha256'],kind='menu',mode=0,variant=1,limit=1800,script=str(script.resolve()),script_sha256=sha(script),dependencies=deps,parent_preparation_sha256=sha(OLD/'menu/preparation.json'),config_deltas=[k for k in c if k not in before or c[k]!=before[k]],changed_hook_count=len(changes),all_original_controller_tail_and_six_guard_bodies_exact=True,all131_body_records_RAM_and_current_HUD_art_exact=True,original3cee_shot_source_exact=True,no_MM_PROTO_SHOT_MUX_segment=True,full5376pixel_reference_retained=True,controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},additive_ungated_timing_observer_sha256=sha(R/'tools/audit/parodius_visibility_menu59_timing_v2.lua'),no_emulated_writes=True,scope='PREPARATION ONLY. Exact original b0/3cee menu1800 controller and six semantic guards; genuine clean-candidate hooks/E008256 protocol. Additive ungated timing/hardware/NT-CHR-palette-OAM-start ownership callbacks before original observers and finalizer before stop. No native grant/run, death/area/Hard/overlap/adoption. Originalb0visualFALSE and areaFALSE remain unchanged.')
 put(a.output/'menu/preparation.json',q);put(a.output/'proof.json',q);print(json.dumps(dict(script_sha256=sha(script),preparation_sha256=sha(a.output/'menu/preparation.json'),changed_hooks=len(changes),config_deltas=q['config_deltas']),indent=2))
if __name__=='__main__':main()
