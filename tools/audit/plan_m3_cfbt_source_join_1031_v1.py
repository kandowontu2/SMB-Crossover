"""Read-only cumulative M3 factor graft and separately staged RODATA split plan."""
from pathlib import Path
import argparse,collections,difflib,hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
E=R/'build/smb3plus-low-table-factor-host-1031-v4/joint'
A=R/'build/bowser-playable-jump-v1/joint'
O=R/'build/m3-cfbt-source-join-plan-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def check(p):
 q=json.loads(p.read_text())
 for n,v in q.get('bindings',{}).items():assert sha(n)==v,(p,n)
 return q
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def normalized(p,j):return p.read_text(encoding='utf-8').replace(str(j),'JOINT').replace(j.as_posix(),'JOINT')
def od(p,flag):return subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),flag,str(p)],capture_output=True,text=True,check=True).stdout

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--handoff',type=Path,required=True);arg=ap.parse_args()
 H=arg.handoff.resolve();C=H.parent/'joint';h=check(H)
 assert not O.exists()and sha(C/'candidate.nes')=='9b1089d254dfb18ceb5bb2bc14951f2b782aa40cf82fcde63b9cb07d82f456c6'
 factors=R/'docs/qa/checkpoints/2026-10-31/smb3plus-low-table-factor-v1/handoff.json';check(factors)
 grant=R/'docs/qa/checkpoints/2026-10-31/contra-force-p1-experimental-resources/native-restore-factor-grant-v1.json';check(grant)
 assert sha(E/'candidate.nes')=='e54b91fa15b335bb17fd24fa7a0b667ef50bf31c8fad900d6c1a1ec38526116a'
 # The correct current recipes are not the inherited copies inside joint.
 main=R/'build/bt-current-cf-component-v2/main-build.json'
 union=R/'build/cf-bt-shared-transport-v3/union-build.json'
 link=C.parent/'final-link.json'
 recipes={n:dict(path=str(p),sha256=sha(p),command=json.loads(p.read_text())['command'])for n,p in[('main',main),('union',union),('link',link),('M3_CHR',E.parent/'chr-build.json')]}
 def output(cmd):return Path(cmd[cmd.index('-o')+1])
 assert sha(C/'main.o')==sha(output(recipes['main']['command']))
 assert sha(C/'union.o')==sha(output(recipes['union']['command']))
 objects=[Path(x)for x in recipes['link']['command']if x.endswith('.o')];assert len(objects)==len(set(objects))==85
 census=[]
 for p in objects:
  segtext=od(p,'--dump-segments');imp=od(p,'--dump-imports');exp=od(p,'--dump-exports')
  segs={m[1]:int(m[2])for m in re.finditer(r'Name:\s+"([^"]+)"(?:(?!Name:)[\s\S])*?Size:\s+(\d+)',segtext)}
  declared=int(re.search(r'Count:\s+(\d+)',segtext)[1]);assert len(segs)==declared
  imports=re.findall(r'Name:\s+"([^"]+)"',imp)
  assert segs.get('RODATA',0)==0,(p,'Live RODATA')
  assert not any(n.startswith('__RODATA_')for n in imports),(p,'RODATA consumer')
  census.append(dict(path=str(p),sha256=sha(p),declared_segments=declared,segments=segs,imports=imports,
      exports=re.findall(r'Name:\s+"([^"]+)"',exp)))
 currentmain=next(r for r in census if r['path']==str(C/'main.o'))
 assert currentmain['declared_segments']==256 and currentmain['segments']['RODATA']==0
 metadata=[dict(path=r['path'],imports=[n for n in r['imports']if n.startswith('__M3_GFX_')])for r in census if any(n.startswith('__M3_GFX_')for n in r['imports'])]
 assert len(metadata)==1 and Path(metadata[0]['path']).name=='audio2.o'and metadata[0]['imports']==['__M3_GFX_SIZE__']
 assert '.assert __M3_GFX_SIZE__<=$1400,lderror' in (R/'src/rogue_dawn_audio_upper_raw_v4.s').read_text()
 a,e,c=[scoped_load(p/'candidate.nes')for p in[A,E,C]]
 de={i for i,(x,y)in enumerate(zip(a['raw'],e['raw']))if x!=y};dc={i for i,(x,y)in enumerate(zip(a['raw'],c['raw']))if x!=y}
 assert not de&dc,('Genuine cumulative source delta overlaps final shared source',len(de&dc))
 assert a['raw'][:16]==e['raw'][:16]==c['raw'][:16]
 ch=16+128*8192;assert all(969<=(i-ch)//1024<1019 for i in de if i>=ch)
 modules=['src/smb3_mario_motion.s','src/smb3_mario_render.s','src/smb3_native_controller.inc','src/smb3_mario_art.inc','src/smb3_mario_dispatch.s']
 for n in modules:assert normalized(A/n,A)==normalized(C/n,C),('Base M3 producer changed',n)
 # All append spans must be clear of every actual linked segment, not only M3.
 append=[(90,0xecc,0xefa),(91,0x139d,0x13fd),(81,0x105b,0x10ce)]
 for bank,lo,hi in append:
  begin=16+bank*8192+lo;end=16+bank*8192+hi
  assert c['raw'][begin:end]==a['raw'][begin:end]
  for g in c['segs'].values():
   if'ooffs'not in g:continue
   s=int(g['ooffs'],0);t=s+int(g['size'],0)
   assert max(begin,s)>=min(end,t),(bank,lo,hi,g['name'])
 cfg=(C/'private.cfg').read_text();assert 'CF_CHR_POST:start=$f2400,size=$dc00' in cfg
 assert 'SMB3PLUS_BODY_CHR:'not in cfg
 names=(C/'src/new_roster_dispatch.s').read_text();assert '  lda #28\n  clc\n  adc M3Variant\n  jmp NameIndex\n' in names
 menu=(C/'src/character_select.s').read_text();assert '  lda M3Variant\n  eor #1\n  sta M3Variant\n' in menu
 # No source is mutated. These are review-only layout diffs against qualified E54.
 art=(E/'src/smb3_mario_art.inc').read_text();art=once(art,'.segment "M3_GFX"','.segment "M3_GFX_PREFIX"')
 art=once(art,'MbChrOffsets:.byte 0,4,4,244,0,248,252\n .res 74,$ea',
     'MbChrOffsets:.byte 0,4,4,244,0,248,252\n ; Explicit CF67 reservation; RODATA is the audited former empty category.\n.segment "RODATA"\n .res 7,$ea')
 split_sources={'src/smb3_mario_art.inc':art}
 for n in['src/smb3_mario_world_art.inc','smb3plus_float_data.s']:
  split_sources[n]=once((E/n).read_text(),'.segment "M3_GFX"','.segment "RODATA"')
 directives=[]
 for p in E.rglob('*'):
  if p.suffix not in['.s','.inc']:continue
  for line,text in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
   if re.search(r'\.segment\s+"M3_GFX"',text):directives.append(dict(path=str(p),line=line,text=text))
 assert len(directives)==3
 for n,text in split_sources.items():assert not re.search(r'\.segment\s+"M3_GFX"',text),n
 ecfg=(E/'private.cfg').read_text()
 newcfg=once(ecfg,'    X5_NEW_5B: start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$5b;',
  '    X5_NEW_5B: start=$c000,size=$e97,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5b;\n    CF_P1_RESTORE_ROM_MEM:start=$ae97,size=$43,type=ro,file=%O,fill=yes,fillval=$ea,bank=$5b;\n    X5_NEW_5B_AFTER_CF:start=$ceda,size=$1126,type=ro,file=%O,fill=yes,fillval=$ff,bank=$5b;')
 newcfg=once(newcfg,'    M3_GFX:load=X5_NEW_5B,type=ro,define=yes;','    M3_GFX_PREFIX:load=X5_NEW_5B,type=ro,define=yes;')
 newcfg=once(newcfg,'    RODATA:   load = PRGLow,            type = ro,  define   = yes;','    RODATA:load=X5_NEW_5B_AFTER_CF,type=ro,define=yes; # Explicit selected M3 suffix owner; baseline all85 objects empty.')
 newcfg=once(newcfg,'ROGUE_AUDIO_UPPER_RAW_0:load=X5_NEW_5B,type=ro,start=$d400,optional=yes;','ROGUE_AUDIO_UPPER_RAW_0:load=X5_NEW_5B_AFTER_CF,type=ro,start=$d400,optional=yes;')
 newcfg=once(newcfg,'SYMBOLS {','SYMBOLS {\n    __M3_GFX_LOAD__:type=export,value=__M3_GFX_PREFIX_LOAD__;\n    __M3_GFX_RUN__:type=export,value=__M3_GFX_PREFIX_RUN__;\n    __M3_GFX_SIZE__:type=export,value=__M3_GFX_PREFIX_SIZE__+$43+__RODATA_SIZE__;')
 O.mkdir();patch=[]
 for n,text in split_sources.items():patch+=list(difflib.unified_diff((E/n).read_text().splitlines(True),text.splitlines(True),fromfile='qualified-e54/'+n,tofile='later-source-layout/'+n))
 patch+=list(difflib.unified_diff(ecfg.splitlines(True),newcfg.splitlines(True),fromfile='qualified-e54/private.cfg',tofile='later-source-layout/private.cfg'))
 (O/'later-layout.proposal.diff').write_text(''.join(patch),encoding='utf-8');put(O/'actual-object-census.json',census);put(O/'actual-recipes.json',recipes)
 plan=dict(plan_only=True,built=False,native=False,source_base=sha(C/'candidate.nes'),source_base_handoff=sha(H),cumulative_M3=sha(E/'candidate.nes'),ancestor=sha(A/'candidate.nes'),
  stages=['Stage1 NEW source clone of frozen final9b; graft cumulative genuine e54 M3 modules/helpers/menu hunks/CHR only. Retain final compressed46groupunion and all CF/BT source objects/cookies. Original whole M3_GFX remains. No CF67 worker. Rebuild actual main/currentunion/newCHR using guarded final parent producers; final127/125 mirror follows genuine current recipe.',
   'Stage1 require exact disjoint source-delta oracle (verification only), every current object export/public M3 PC, header/fixed/foreign CHR/currentCFBT images exact. Rebind originalM3 controller/9072graphics/sourcepixels/current68 foreignMain/menu/ISR plus finalshared finite BT/CF endpoint/vector receipts.',
   'Stage2 NEW child only after Stage1 source qualification: explicit existing RODATA reuse and M3_GFX_PREFIX rename shown in diff. All3 actual M3_GFX emitters retargeted. No CF worker; reserved67 memory fillEA. Require byte-identical Stage1 ROM, all publicPCs and legacyM3metadata C000/C000/13FD,256 mainsegments, prefixE97+67+suffix523=13FD, and original audio2<=1400 assertion still genuine.',
   'Stage3 separate future CF-owned producer: real67B relocatable worker in own object/runA91/loadphysicalC91. No worker or FF factoring adopted by this plan. Root/CFowner must qualify it independently against exact joined source.'],
  candidate_delta_bytes=len(de),PRG_by_bank=dict(collections.Counter((i-16)//8192 for i in de if 16<=i<ch)),physical_overlap_bytes=0,
  CHR=dict(owned=[969,1019],actual_current_parent_MEMORY='CF_CHR_POST:$F2400+$DC00',new_SEGMENT='SMB3PLUS_BODY_CHR:load=CF_CHR_POST,type=ro,start=$f2400;',all_other_CHR_exact=True),
  M3_modules=modules,helpers=['smb3plus_body_host.s','smb3plus_kick_host.s','smb3plus_float_state.inc','smb3plus_float_data.s','smb3plus_menu_name.s'],
  segment_count=dict(main_actual=256,all_final_objects=85,RODATA_baseline_emitted_bytes=0,RODATA_import_consumers=0,proposed_main=256,new_distinct_main_suffix_category=False,prior_257_failure=str(R/'build/smb3plus-menu-host-1031-v3/main-build.json')),
  metadata=dict(real_consumers=metadata,original_guard='src/rogue_dawn_audio_upper_raw_v4.s: assert __M3_GFX_SIZE__<=$1400',legacy_LOAD_RUN_SIZE_preserved=[0xc000,0xc000,0x13fd],legacy_SIZE_expression='__M3_GFX_PREFIX_SIZE__+$43+__RODATA_SIZE__',expected_suffix_size=0x523,intended_unconsumed_RODATA_metadata_change='LOAD/RUN9FFF→CEDA;SIZE0→523; explicit source category reassignment, not a silent relabel'),
  actual_M3_segment_directives=directives,CF67=[0xae97,0xaeda],remaining_M3_ability_bytes=331,ability_space_modified=False,
  constraints=['No complete old main/cfg/union adoption','No binary-overlay construction','No compile before new private outputs and all CFG MEMORY sideoutputs validated','No new lease/globalbyte/native/readiness/install decision','Final shared cookie/nativeworld32 and all new CF/BT resources must survive exactly'],bindings={})
 files=[Path(__file__),H,factors,grant,C/'candidate.nes',C/'candidate.dbg',C/'candidate.lbl',C/'entrypoint.s',C/'private.cfg',C/'union.s',C/'src/new_roster_dispatch.s',C/'src/character_select.s',E/'candidate.nes',E/'candidate.dbg',E/'private.cfg',A/'candidate.nes',R/'src/rogue_dawn_audio_upper_raw_v4.s',R/'build/smb3plus-menu-host-1031-v3/main-build.json',O/'later-layout.proposal.diff',O/'actual-object-census.json',O/'actual-recipes.json']
 files +=[E/n for n in modules+plan['helpers']+['src/smb3_mario_world_art.inc','smb3plus-chr.s','toad-smb3plus-body.chr','peach-smb3plus-body.chr']]+[C/n for n in modules]+[Path(v['path'])for v in recipes.values()]+objects
 plan['bindings']={str(p.resolve()):sha(p)for p in files};put(O/'plan.json',plan);check(O/'plan.json');print(json.dumps(dict(plan=str(O/'plan.json'),sha256=sha(O/'plan.json'),bindings=len(plan['bindings']),objects=85,overlap=0)))
if __name__=='__main__':main()
