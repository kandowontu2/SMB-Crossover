"""Source-owned exact hook envelopes and current66/loader consumer closure."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/cf-bt-shared-transport-v3';O=R/'build/cf-owner-retirement-v2';J=O/'joint'
D=R/'build/cf-owner-retirement-source-closure-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 D.mkdir(exist_ok=False);stage=json.loads((O/'source-stage.json').read_text())
 for f,h in stage['bindings'].items():assert sha(f)==h,f
 a,b,c=[qualified(p)for p in[P/'joint/candidate.nes',J/'candidate.nes',R/'build/bowser-playable-jump-v1/joint/candidate.nes']]
 current_moved={n:[s['val'],b['syms'].get(n,{}).get('val')]for n,s in c['syms'].items()if b['syms'].get(n,{}).get('val')!=s['val']};assert not current_moved,current_moved
 changed=[]
 for n,s in a['syms'].items():
  z=b['syms'].get(n,{}).get('val')
  if z!=s['val']:changed.append(dict(symbol=n,old=s['val'],new=z))
 allowed_internal={'CfWrite11','CfDirect11','CfLegacy11','CfRestorePublication','CfPublishCookie','CfLoadVerified','CfLoadFailed','CfVerify256','CfCopy256','CfMapSourcePage','CfLoadNextPage','CfLoadNextBank'}
 assert {r['symbol']for r in changed}==allowed_internal
 old_loader=qualified(R/'build/contra-force-checkpoint-loader-cart-v1/joint/candidate.nes')
 for row in changed:assert address(b,row['symbol'])==address(old_loader,row['symbol'])
 spans=[(location(b,'MenuResolveCharacter'),34),(location(b,'BwScene'),18),(location(b,'BwSceneNativePrepared'),15),(location(b,'CfRetire'),36),(location(b,'CfLoaderCoreProposal'),302)]
 delta=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 assert len(delta)==358 and all(any(lo<=i<lo+n for lo,n in spans)for i in delta)
 assert a['raw'][:16]==b['raw'][:16]and a['raw'][1048592:]==b['raw'][1048592:]
 for name in['bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin','cf-stream.bin','cf-cookie.bin']:assert sha(J/name)==sha(P/'joint'/name),name
 # Check the actual linked object set, not stale copied recipe names.
 command=json.loads((O/'final-link.json').read_text())['command'];objects=[Path(x)for x in command if x.endswith('.o')]
 assert J/'main.o'in objects and J/'bowser/cold.o'in objects and J/'cf-loader.o'in objects and J/'cf-retire.o'in objects
 assert not any(p.name=='cold.o'and p!=J/'bowser/cold.o'for p in objects)
 od=R/'tools/Windows/cc65/bin/od65.exe';importers={n:[]for n in['CfRetire','BwScene','FwLoad','BwLoad','BtLoad']};object_bindings={}
 for obj in objects:
  run=subprocess.run([str(od),'--dump-imports',str(obj)],capture_output=True,text=True,check=True)
  object_bindings[str(obj.resolve())]=sha(obj)
  for n in importers:
   if re.search(r'Name:\s+"'+re.escape(n)+r'"',run.stdout):importers[n].append(str(obj))
 assert importers['CfRetire']==[str(J/'main.o'),str(J/'bowser/cold.o')],importers
 assert importers['BwScene']==[str(J/'main.o')],importers
 # Internal same-object FwLoad/BwLoad calls are covered by actual executing
 # source entry witnesses in the coverage receipt, not od65 imports alone.
 screen=J/'screen_render.s';assert 'farcall BwScene'in screen.read_text()
 cold=(J/'bowser/cold.s').read_text();assert cold.count('BwFar BwLoad,jsr')==1
 ff=(J/'loader.s').read_text();assert ff.count(' jsr FwLoad\n')==1
 q=dict(source=True,passed=True,native=False,candidate=stage['candidate'],all_current66_symbol_PCs_exact=len(c['syms']),only_12_internal_CF_loader_diagnostic_labels_rebound_to_frozen60a5=changed,
  original_menu_34B=True,scene_first18B_repacked=True,existing_A88_tail15B=True,BW_ROM_AUX_total=204,BW_ROM_AUX_grant=204,
  all_other_ROM_bytes_header_CHR_images_cookies_exact=True,changed_bytes=len(delta),exact_changed_envelopes=spans,actual_linked_importers=importers,
  installed_foreign_A3_writers={'FwLoad':'sole source call FwSceneInit, reached after early BwScene CfRetire','BwLoad':'sole source call BwScene, after early CfRetire','BtLoad':'no installed caller in this still-pending leaf; direct API requires explicit retirement'},
  selected_publication='Actual MenuResolve34 retires before BwMenuResolve→FwMux/S2/Qw/Ar/Fm/Cm publication; global CrossoverInit already runs QwBoot validity clear first.',
  source_A_reuse_contract='InitScreen is sole genuine production SFC ingress to BwScene. Its original A is already SafecallA; pure CfRetire has no nestedSFC and preserves fullAXYP/SMC. New15B helper reuses native JSR return with actual FarCallCommon. Menu first genuine CfRetire SFC saves originalA before the subsequent15B tail.',
  limits='CF/BT remain pending. No naturalCF warm/player policy, soundtest Selected store coverage, or direct-API automatic protection claimed. Future BT/CF cold integration must preserve the early owner boundary.',
  bindings={**object_bindings,**{str(p.resolve()):sha(p)for p in[Path(__file__),O/'source-stage.json',O/'main-build.json',O/'cold-build.json',O/'final-link.json',J/'candidate.nes',J/'candidate.dbg',J/'private.cfg',screen,J/'src/character_select.s',J/'bowser/cold.s',J/'loader.s',J/'cf-loader.s',J/'cf-retire.s',R/'build/contra-force-checkpoint-loader-qualified-v1/handoff.json']}})
 (D/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','only_12_internal_CF_loader_diagnostic_labels_rebound_to_frozen60a5']}))
if __name__=='__main__':main()
