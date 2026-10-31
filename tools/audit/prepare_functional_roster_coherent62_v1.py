"""Genuine final62 producer composition on frozen visual58 dependencies.

SMB2 cold-render successor will be joined separately if not yet frozen.
No inherited compiler output path is trusted; validate every actual command.
"""
from pathlib import Path
import json,re,shutil,subprocess,sys,difflib
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as U
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address,location
P=R/'build/functional-roster-visuals58-v1';F=R/'build/ff-cold-preview-v5';OLDFF=R/'build/ff-current-ready-v2';BASE=R/'build/current-character-quick-ui-v13/joint'
O=R/'build/functional-roster-coherent62-v1';J=O/'joint';sha=U.sha;read=U.read;write=U.write

def once(t,a,b):assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
def main():
 assert not O.exists()
 inputs=[P/'handoff.json',F/'handoff-source-v1.json']
 for p in inputs:U.bound(json.loads(read(p)))
 shutil.copytree(P/'joint',J);patch=[]
 def retarget(t):return t.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
 for p in J.rglob('*'):
  if p.is_file()and p.suffix in ['.s','.inc','.cfg']:
   a=read(p);b=retarget(a)
   if a!=b:write(p,b)
 inventory=json.loads(read(F/'source-merge-inventory.json'))
 for src in inventory['full_owned_FF_sources']:
  p=Path(src)
  if p.name!='ram3.bin':shutil.copyfile(p,J/p.name)
 def edit(p,t):
  old=read(p);write(p,t);patch.extend(difflib.unified_diff(old.splitlines(True),t.splitlines(True),fromfile='visual58/'+p.relative_to(J).as_posix(),tofile='coherent62/'+p.relative_to(J).as_posix()))
 p=J/'ff-palette-lifecycle.s';t=read(p);t=once(t,'.import QwMenuResolve,','.import S2MenuResolve,');t=once(t,'MP_FAR QwMenuResolve,jmp','MP_FAR S2MenuResolve,jmp');write(p,t)
 # Exact genuine shared cold operand, without replacing current S2 or UI.
 p=J/'src/character_select.s';t=once(read(p),'farcall S2MenuResolve,jmp','farcall FwMuxMenuResolve,jmp');edit(p,'.import FwMuxMenuResolve\n'+t)
 p=J/'src/full_roster_menu.s';t=read(p);a=' lda $5fef\n and #3\n clc\n adc #5\n sec\n rts\nNotFF:';edit(p,once(t,a,a.replace(' sec\n',' clc\n')))
 p=J/'src/full_roster_menu_art.inc';t=read(p)
 for name in ['FF FIGHTER','FF WHITE MAGE','FF BLACK MAGE','FF THIEF']:t=once(t,'*'+name,' '+name)
 edit(p,t)
 for relative in ['src/samus_freeze_render.s','src/metasprite_engine.s']:
  # S2 and root visual/410 changes never owned either native source file.
  assert read(J/relative)==read(BASE/relative),relative
  edit(J/relative,read(F/'joint'/relative))
 # Lexical true native exports required by new owned consumers.
 p=J/'entrypoint.s';t=read(p);exports=set()
 for line in re.findall(r'^\.export (.+)$',t,re.M):exports.update(x.strip()for x in line.split(','))
 for n in ['SmFreezePalettePacket','SmFreezeTurn','SmFreezeLastBlue','UpdateScreen','PnHudPreUpdateScreen','SmFreezeNativeFlashEnemy','CurrentOAMOffset','RgOamRotation','Sprite_Y_Position','Sprite_Attributes','RgOamUsed','DrawMetasprite']:
  if n not in exports:t+='\n.export '+n+'\n'
 for n in ['NmiR0','NmiR1']:
  if not re.search(r'^\.exportzp .*\b'+n+r'\b',t,re.M):t+='\n.exportzp '+n+'\n'
 edit(p,t)
 # Merge only FF's existing granted holes; retain all current S2/Roll/C82
 # and all Quick/Arthur MEMORY/SEGMENTS exactly, including output paths.
 p=J/'private.cfg';t=read(p);mem,segs=t.split('SEGMENTS {',1)
 assert 'FF_FX_PROTOCOL_RUN:'not in mem
 mem=mem.rsplit('}',1)[0]+'FF_FX_PROTOCOL_RUN:start=$be2f,size=$1d1,type=ro,file="",bank=93;\n}\n'
 insert={
 'FF_RAM_PUBLISHER:load=FF_RAM3_MEM,type=ro,start=$a275;':'\nFF_EPOCH_CLASSIFY:load=FF_RAM3_MEM,type=ro,start=$a289;\nFF_EPOCH_HEARTBEAT:load=FF_RAM3_MEM,type=ro,start=$a2cc;',
 'FF_HOST_RENDER:load=FF_RAM3_MEM,type=ro,start=$a300;':'\nFF_EPOCH_COLORS:load=FF_RAM3_MEM,type=ro,start=$a6e5;',
 'FINAL_FANTASY_CORE:load=FF_RAM3_MEM,type=ro,start=$aa00;':'\nFF_EPOCH_PACKET:load=FF_RAM3_MEM,type=ro,start=$b68b;',
 'FF_FX_DATA3:load=FF_RAM3_MEM,type=ro,start=$bcef;':'\nFF_EPOCH_MAIN:load=FF_RAM3_MEM,type=ro,start=$becf;\nFF_EPOCH_TABLES:load=FF_RAM3_MEM,type=ro,start=$bff0;',
 'FF_HOST_PALETTE_C:load=FF_ART_MEM,type=ro;':'\nFF_FX_PROTOCOL_A:load=FF_ART_MEM,run=FF_FX_PROTOCOL_RUN,type=ro;\nFF_FX_PREFLUSH_C:load=FF_ART_MEM,type=ro;\nFF_FX_WORLD_MARKER:load=FF_ART_MEM,type=ro;'}
 for a,b in insert.items():segs=once(segs,a,a+b)
 edit(p,mem+'SEGMENTS {'+segs)
 recipes=[];c=json.loads(read(P/'main-build.json'))['command'][:];c=[retarget(x)for x in c];c[1:1]=['-I',str(J/'src'),'-I',str(J)];recipes.append(('main-build',c))
 names=['loader','veneers','ff-palette','stream','ff-palette-lifecycle','ff-palette-preflush','ff-world-marker','ff-epoch-workers']
 for n in names:recipes.append((n+'-build',[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','-I',str(J),'-I',str(R),'-I',str(R/'src'),'--bin-include-dir',str(J),'--bin-include-dir',str(R),'--create-full-dep',str(J/(n+'.dep')),'-o',str(J/(n+'.o')),str(J/(n+'.s'))]))
 link=json.loads(read(P/'final-link.json'))['command'][:]
 replace=set(['main']+names)
 for i,x in enumerate(link):
  if x.endswith('.o')and Path(x).stem in replace:link[i]=str(J/Path(x).name)
 for flag in ['-o','-Ln','-m','--dbgfile','--mapfile','-C']:
  if flag in link:link[link.index(flag)+1]=str(J/Path(link[link.index(flag)+1]).name)
 if '--ld-args'in link:
  k=link.index('--ld-args')+1;v=link[k].split(',')
  for i in range(1,len(v),2):v[i]=str(J/Path(v[i]).name)
  link[k]=','.join(v)
 for n in names:
  if str(J/(n+'.o'))not in link:link.append(str(J/(n+'.o')))
 recipes.append(('layout-link',link))
 vals=[dict(step=n,validation=validate(c,J,cwd=R))for n,c in recipes];write(O/'output-preflight.json',json.dumps(vals,indent=2)+'\n')
 def run(n,c):
  validate(c,J,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True);write(O/(n+'.json'),json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr)
 for n,c in recipes:run(n,c)
 assert (J/'ram3.bin').read_bytes()==(F/'joint/ram3.bin').read_bytes(),'ActualFFnativeimports/payloadchanged'
 for n in ['code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n),n
 from prepare_cv3_dmc_mirror import prepare
 prepare(R,J/'candidate.nes');fixed=(J/'candidate.nes').read_bytes()[16+127*8192:16+128*8192];(J/'final127.bin').write_bytes(fixed)
 # Final actual127 is rebound into all119/120 sample clones by true source.
 old=read(J/'dmc-clones.s');paths=re.findall(r'\.incbin "([^"]+)"',old);assert len(set(paths))==1,paths
 write(J/'dmc-clones.s',old.replace(paths[0],(J/'final127.bin').as_posix()))
 dc=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','-o',str(J/'dmc-clones.o'),str(J/'dmc-clones.s')]
 run('dmc-clones-build',dc)
 for i,x in enumerate(link):
  if x.endswith('dmc-clones.o'):link[i]=str(J/'dmc-clones.o')
 run('final-link',link);prepare(R,J/'candidate.nes');assert(J/'candidate.nes').read_bytes()[16+127*8192:16+128*8192]==fixed
 old,new=[load(p/'candidate.nes')for p in [P/'joint',J]]
 for n in ['HuEntryBase','HuEnd','GmCommonNmiStart','GmCommonNmiEnd','NrMenuCharacter','MenuResolveCharacter','FmPending','FmResolve','S2ServiceVeneers','S2C82Entry','QwLoaderCore','DpAdmissionPortrait','GmPortraitAnchored']:assert address(old,n)==address(new,n),n
 for name in ['river_city_required_ink_v1.inc','river_city_shared_palette_art.inc','chip_dale_render.s']:assert sha(J/'src'/name)==sha(P/'joint/src'/name),name
 assert (J/'gm-nmi.s').read_bytes()==(P/'joint/gm-nmi.s').read_bytes()
 write(O/'source.patch',''.join(patch))
 d=dict(status='SOURCE_LINKED62_TARGETED_COLD_MAIN_CONTROLS_PENDING_S2_COLD_VISIBILITY_HOLD',candidate=sha(J/'candidate.nes'),parent=sha(P/'joint/candidate.nes'),FF_source_handoff=sha(F/'handoff-source-v1.json'),native=False,installed=False,intended_ready=62,profiles=80,Quick_Ar_payloads_exact=True,FF_payload_cookie_exact_frozen334b=True,RCR_Chip_UI_Goku_Gimmick_source_preserved=True,shared_A79_and_S2_NMI_ingress_unchanged=True,cold_chain='FwMuxMenuResolve->FwMuxMenuA(retireFF)->S2MenuResolve->QwMenuResolve->ArGenResolve->FmResolve',known_hold='S2service17metadataonly nativeemptycold preview; awaitownsourcefix; FF source334b observer pattern-view issue underrootreview.',bindings={str(p.resolve()):sha(p)for p in inputs+[Path(__file__),J/'candidate.nes',J/'candidate.dbg',O/'output-preflight.json',O/'source.patch']})
 write(O/'source-stage.json',json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k!='bindings'}))
 for p in inputs:U.bound(json.loads(read(p)))
if __name__=='__main__':main()
