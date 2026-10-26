"""Prepare one unchanged all-four-variant menu1800 on b0; never launches an emulator."""
from pathlib import Path
import argparse,copy,difflib,hashlib,json,re,shutil,sys
from final_roll_items_prepare import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'mm-proto-postdma-composed-v1'
OLD=D/'parodius-menu3cee-preparation-v2'
SHA='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'
BASE='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert not a.output.resolve().is_relative_to(R)
 assert sha(P/'candidate.nes')==SHA
 parent=json.loads((P/'ready-v1/receipt.json').read_text());assert parent['passed']and parent['ROM_sha256']==SHA
 for name in ['catalog.json','dependencies.json']:
  for f,h in json.loads((P/'ready-v1'/name).read_text()).items():assert sha(f)==h,f
 for f,h in json.loads((P/'source-manifest.json').read_text()).items():assert sha(P/'source'/f)==h,f
 previous=json.loads((D/'parodius-menu3cee-native-final-v1/proof.json').read_text());assert previous['passed']and previous['ROM_sha256']==BASE and previous['all6native_components_passed']
 prior=json.loads((OLD/'menu/preparation.json').read_text());old=Path(prior['script']);assert sha(old)==prior['script_sha256']
 for f,h in prior['dependencies'].items():assert sha(f)==h,f
 original=old.read_text();c=json.loads((old.parent/'config.json').read_text());before=copy.deepcopy(c)
 assert(c['mode'],c['variant'],c['character'],c['limit'],c['lifecycle']['kind'])==(0,1,18,1800,'menu')
 b=scoped_load(P/'candidate.nes');oldb=scoped_load(D/'root-chip-hud-composed-v1/candidate.nes')
 deltas=[]
 for family in ['hooks','hud_hooks','lifecycle_hooks']:
  for name,h in c[family].items():
   was=copy.deepcopy(h)
   if name in ['NmiReturn','IrqReturn']:
    n='NonMaskableInterrupt'if name=='NmiReturn'else'IrqScrollSplit';addr=address(b,n)+int(b['syms'][n]['size'],0)-1;bank=(location(b,n)-16)//8192
   else:addr=address(b,name);bank=(location(b,name)-16)//8192
   offset=16+bank*8192+addr%8192;h.update(address=addr,bank=bank,bytes=list(b['raw'][offset:offset+len(h['bytes'])]))
   if name.endswith('Return'):assert h['bytes'][0]==0x40
   if was!=h:deltas.append(dict(family=family,name=name,before=was,after=h))
 for family in ['ram','profile_ram','hud_ram','lifecycle_ram']:
  for name,v in c[family].items():assert address(b,name)==v,(family,name)
 for s in c['body_sources'].values():
  off=16+s['bank']*8192+s['pointer']%8192;assert list(b['raw'][off:off+len(s['bytes'])])==s['bytes']
 assert len(c['body_sources'])==131
 # Exact entire art/NMI-HUD banks retain every non-hook scroll/cell literal.
 for bank in [76,77,116,117]:
  # A77 has genuine moved-fixed-call operand changes, but guarded HUD code/data
  # below are independently byte-bound from actual labels and complete font.
  if bank in[76,117]:assert b['raw'][16+bank*8192:16+(bank+1)*8192]==oldb['raw'][16+bank*8192:16+(bank+1)*8192]
  if bank==116:
   left=oldb['raw'][16+bank*8192:16+(bank+1)*8192];right=b['raw'][16+bank*8192:16+(bank+1)*8192];assert [i for i in range(8192)if left[i]!=right[i]]==[0x50]and left[0x4f:0x52]==bytes([0x20,0x52,0xe0])and right[0x4f:0x52]==bytes([0x20,0x58,0xe0])
 font=(P/'source/chr/characters/parodius-hud.chr').read_bytes();assert font==(D/'root-chip-hud-composed-v1/source/chr/characters/parodius-hud.chr').read_bytes()
 assert b['raw'][16+1048576:]==oldb['raw'][16+1048576:]
 labels=list(b['raw'][location(b,'PnHudCells'):location(b,'PnHudCells')+84]);assert c['hud_labels']=={str(v):labels[(v-1)*28:v*28]for v in range(1,4)}
 off=location(b,'OAMandReadJoypad');addr=address(b,'OAMandReadJoypad');mask=address(b,'Mirror_PPUMASK')
 expected=bytes([0xa9,2,0x8d,0x14,0x40,0xad,mask&255,mask>>8,0x8d,1,0x20,0xa2,1]);assert b['raw'][off:off+13]==expected and addr==0xe000
 c['dma_protocol']=dict(next_pc=addr+5,next_bytes=list(expected[5:13]),complete_pc=addr+8,physical_bank=127,stage='exec after actual LDA before STA2001; completed DMA hardware while rendering remains disabled')
 out=a.output/'menu/baseline-early';out.mkdir(parents=True);controller=a.output/'menu/controller';shutil.copytree(OLD/'menu/controller',controller)
 for f in controller.glob('*.lua'):f.write_text(f.read_text().replace((OLD/'menu/controller').as_posix(),controller.as_posix()),encoding='utf-8')
 c.update(ROM_sha256=SHA,output=out.as_posix()+'/')
 header=original[:original.index('\nROSTER_CONFIG=')];text='PARODIUS_VISIBILITY='+lua(c)+original[len(header):]
 observer_changes={}
 for oldname,newname in [('parodius_visibility_hud_static_observer_v1.lua','parodius_visibility_postdma_static_observer_v1.lua'),('parodius_visibility_hud_lifecycle_bridge_v4.lua','parodius_visibility_postdma_bridge_v1.lua')]:
  left=(R/'tools/audit'/oldname).read_text();right=(R/'tools/audit'/newname).read_text();assert text.count(left)==1
  text=text.replace(left,right);observer_changes[oldname]=dict(successor=newname,old_sha256=sha(R/'tools/audit'/oldname),new_sha256=sha(R/'tools/audit'/newname))
  (a.output/(newname+'.patch')).write_text(''.join(difflib.unified_diff(left.splitlines(True),right.splitlines(True),fromfile=oldname,tofile=newname)),encoding='utf-8')
 text=text.replace(old.parent.as_posix(),out.as_posix()).replace((OLD/'menu/controller').as_posix(),controller.as_posix())
 normalized=text[text.index('\nROSTER_CONFIG='):].replace(out.as_posix(),old.parent.as_posix()).replace(controller.as_posix(),(OLD/'menu/controller').as_posix())
 for oldname,z in observer_changes.items():normalized=normalized.replace((R/'tools/audit'/z['successor']).read_text(),(R/'tools/audit'/oldname).read_text())
 assert normalized==original[original.index('\nROSTER_CONFIG='):]
 assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(P/('candidate'+ext),out/('candidate'+ext))
 script=out/'run.lua';script.write_text(text,encoding='utf-8');put(out/'config.json',c)
 sys.path.insert(0,str(D/'final-tmnt-items-v1/lua-parser-deps-v1'));from luaparser import ast;ast.parse(text)
 for n in ['expected-hud-fonts.bin','expected-all5376-HUD-pixels.bin','expected-hud-art.json']:shutil.copy2(OLD/n,a.output/n)
 art=json.loads((a.output/'expected-hud-art.json').read_text());art['ROM_sha256']=SHA;put(a.output/'expected-hud-art.json',art)
 put(a.output/'hook-reconciliation.json',dict(passed=True,changed_hooks=deltas,all_hook_bytes_from_actual_candidate=True,all_RAM_exact=True,all131_body_records_exact=True,postDMA=c['dma_protocol']))
 deps=dict(prior['dependencies']);deps.update({str(f.resolve()):sha(f)for f in [Path(__file__),R/'tools/audit/parodius_visibility_postdma_static_observer_v1.lua',R/'tools/audit/parodius_visibility_postdma_bridge_v1.lua',P/'ready-v1/receipt.json',P/'ready-v1/catalog.json',P/'ready-v1/dependencies.json',P/'source-manifest.json']})
 q=dict(prepared=True,native_passed=False,native_granted=False,ROM_sha256=SHA,parent_ROM_sha256=BASE,kind='menu',mode=0,variant=1,limit=1800,script=str(script.resolve()),script_sha256=sha(script),dependencies=deps,parent_preparation_sha256=sha(OLD/'menu/preparation.json'),parent_passed3cee_menu_final_sha256=sha(D/'parodius-menu3cee-native-final-v1/proof.json'),composition_readiness_sha256=sha(P/'ready-v1/receipt.json'),config_deltas=[k for k in c if k not in before or c[k]!=before[k]],changed_hook_count=len(deltas),all131body_records_and_RAM_exact=True,all_original_tail_controller_guard_bodies_exact_except_declared_DMA_protocol=True,controller={f.name:sha(f)for f in controller.iterdir()if f.is_file()},observer_changes=observer_changes,full_5376_HUD_pixel_reference_retained=True,no_emulated_writes=True,scope='SOURCE ONLY; ONE Easy all4variant menu1800 preparation. E008 post-LDA/pre-enable completed hardware observes unchanged256-byte exact-source/visible/init/PPU/CHR/body/NMI/IRQ/5SMC/stack guards. No native grant, run, retry, other mode, death, area or adoption. OriginalareaFALSE/naturalBuffer2 and mixed bodyvisibility/tinyfont limits remain.')
 put(a.output/'menu/preparation.json',q);put(a.output/'proof.json',q);print(json.dumps(dict(prepared=True,script_sha256=sha(script),preparation_sha256=sha(a.output/'menu/preparation.json'),hook_changes=len(deltas),config_deltas=q['config_deltas']),indent=2))
if __name__=='__main__':main()
