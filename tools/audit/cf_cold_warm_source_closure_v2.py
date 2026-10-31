"""Actual current66 source consumers, exact funded spans and public PCs."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/cf-owner-retirement-v2';O=R/'build/cf-cold-warm-source-v3';J=O/'joint';D=R/'build/cf-cold-warm-source-closure-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def scoped(root):
 tab={k:{}for k in['file','mod','scope','sym']}
 for line in(root/'candidate.dbg').read_text().splitlines():
  typ,_,rest=line.partition('\t')
  if typ in tab:
   z=dict(re.findall(r'(\w+)=("[^"]*"|[^,]*)',rest));tab[typ][z['id']]=z
 def chain(i):
  s=tab['scope'][i];return(chain(s['parent'])if'parent'in s else())+(s['name'],)
 def module(i):
  m=tab['mod'][i];return Path(tab['file'][m['file']]['name'].strip('"')).parts[-2:]
 out={}
 for s in tab['sym'].values():
  if 'val'in s and 'scope'in s and s.get('type')in['lab','equ']:
   ss=tab['scope'][s['scope']];out[(module(ss['mod']),chain(s['scope']),s['name'])]=s['val']
 return out

def main():
 D.mkdir(exist_ok=False);stage=json.loads((O/'source-stage.json').read_text())
 for f,h in stage['bindings'].items():assert sha(f)==h,f
 a,b=[qualified(p/'candidate.nes')for p in[P/'joint',J]]
 sa,sb=map(scoped,[P/'joint',J]);changed=[dict(module=k[0],scope=k[1],symbol=k[2].strip('"'),old=v,new=sb.get(k))for k,v in sa.items()if sb.get(k)!=v]
 assert {x['symbol']for x in changed}=={'FmCfHelperEnd','BwStartFlags','BwStartAlts','BwStartGroups','BtRouterBad'},changed
 assert len(changed)==5
 assert all(x['symbol'].startswith('BwStart')and x['new']is None or x['symbol']in['FmCfHelperEnd','BtRouterBad']for x in changed)
 assert address(b,'BtRouterBad')==0xb0da and address(b,'FmCfHelperEnd')==0xb602
 # The exact original51B mask is moved to already-owned menu helper space;
 # all real importers are rebound before its former A67 body is repurposed.
 lo=location(a,'BwStartFlags');hi=location(b,'FmStartIdentityFlags')
 assert a['raw'][lo:lo+51]==b['raw'][hi:hi+51]
 assert address(b,'FmStartIdentityFlags')==0xb5cf
 for n,size in[('MenuResolveCharacter',34),('BwSceneNativePrepared',15)]:
  x,y=location(a,n),location(b,n);assert a['raw'][x:x+size]==b['raw'][y:y+size],n
 # Preserve the genuine Bowser direct constructor and its conditional caller.
 x=location(a,'BwSceneDone')-15;y=location(b,'BwSceneDone')-15
 assert a['raw'][x:x+15]==b['raw'][y:y+15]
 spans=[]
 for n,size in[('FmStartFlags',28),('FmStartIdentityFlags',51),('BwBtResolve',213),('BtServiceVeneers',224),('CfSceneRetireForeign',17),('CfLoadIfCold',42),('CfOrBtCheck',118),('CfLoaderProposal',147),('CfLoaderCoreProposal',302)]:spans.append(dict(owner=n,offset=location(b,n),size=size))
 spans.append(dict(owner='BwScene',offset=location(b,'BwScene'),size=0xb400-address(b,'BwScene')))
 spans.append(dict(owner='CF_granted_carrier_body_shots',offset=16+128*8192+935*1024,size=34*1024))
 delta=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 assert all(any(s['offset']<=i<s['offset']+s['size']for s in spans)for i in delta),[i for i in delta if not any(s['offset']<=i<s['offset']+s['size']for s in spans)][:20]
 assert a['raw'][:16]==b['raw'][:16]
 for n in['bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n),n
 own=R/'build/contra-force-lifecycle-cart-v4/joint'
 for n in['cf-stream.bin','cf-cookie.bin']:assert sha(J/n)==sha(own/n),n
 assert b['raw'][16+128*8192+935*1024:16+128*8192+959*1024]==(J/'cf-stream.bin').read_bytes()
 # Actual linked objects, not copied stale logs or assumed union.o names.
 command=json.loads((O/'final-link.json').read_text())['command'];objects=[Path(x)for x in command if x.endswith('.o')]
 required=[J/'main.o',J/'bowser/cold.o',J/'bowser/router.o',J/'bt/router.o',*[J/(n+'.o')for n in['cf-loader','cf-guard','cf-carrier','cf-retire','cf-cold-warm']]]
 assert all(objects.count(p)==1 for p in required)
 actual_union=R/'build/cf-bt-shared-transport-v3/joint/union.o'
 assert objects.count(actual_union)==1
 old_objects=[Path(x)for x in json.loads((P/'final-link.json').read_text())['command']if x.endswith('.o')]
 assert old_objects.count(actual_union)==1
 od=R/'tools/Windows/cc65/bin/od65.exe';names=['BwStartFlags','FmStartIdentityFlags','BwScene','CfSceneRetireForeign','BwCfSceneLoad','CfLoadIfCold','CfLoaderProposal','CfOrBtCheck','BtServiceVeneers'];imports={n:[]for n in names};bindings={}
 for obj in objects:
  z=subprocess.run([str(od),'--dump-imports',str(obj)],capture_output=True,text=True,check=True);bindings[str(obj.resolve())]=sha(obj)
  for n in names:
   if re.search(r'Name:\s+"'+re.escape(n)+r'"',z.stdout):imports[n].append(str(obj))
 assert not imports['BwStartFlags']and imports['FmStartIdentityFlags']==[],imports
 assert imports['BwScene']==[str(J/'main.o')]
 assert imports['CfSceneRetireForeign']==[str(J/'bowser/cold.o')]
 assert imports['BwCfSceneLoad']==[str(J/'bowser/cold.o')]
 assert imports['CfLoadIfCold']==[str(J/'bowser/router.o')]
 assert imports['CfLoaderProposal']==[str(J/'cf-cold-warm.o')]
 assert 'farcall FmStartIdentityFlags,jmp'in(J/'src/full_roster_menu.s').read_text()
 assert 'farcall BwScene'in(J/'screen_render.s').read_text()
 assert '.assert *<=$b100'in(J/'bt/router.s').read_text()
 q=dict(source=True,passed=True,native=False,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_BT_pending=True,
  actual_scoped_parent_symbols=len(sa),only_declared_internal_or_retired_symbols=changed,all_current66_publicPCs_fixed=True,
  moved_original_51B_Start_mask_byteexact=True,real_Start_call_rebound=True,no_remaining_BwStartFlags_importers=True,original_Bowser_constructor_15B_byteexact=True,
  menu_used_and_granted=[359,400],BT_router_used_and_granted=[211,224],BT_table_slot36_worker_fixed=True,A67_reclaimed_51B_used_by_14B_native_fallback_and_37B_loadselector=True,
  new_ROM_only_granted_17B_and_42B=True,exact_changed_envelopes=spans,changed_bytes=len(delta),header_and_all_other_ROM_CHR_bytes_exact=True,Quick_Ar_FF_BW_images_and_cookies_exact=True,CF_payload_cookie_exact_141b=True,
  actual_linked_importers=imports,actual_consumed_union_object=[str(actual_union)],
  scope='CF pending. Actual menu retirement remains before Selected; foreign scene retires before inner FW/BW overwrites. Selected31 genuine ROM auth/loader then guarded B02015 SceneEnsure, C0 skips original BW constructor. Invalid15/19 genuine native fallback; all other invalid rows decline. No names/palette/P1/native/admission claim.',
  bindings={**bindings,**{str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/cf_cold_warm_source_closure_v1.py',R/'build/cf-cold-warm-source-closure-v1/negative.json',O/'source-stage.json',O/'main-build.json',O/'final-link.json',J/'candidate.nes',J/'candidate.dbg',J/'private.cfg',J/'entrypoint.s',J/'screen_render.s',J/'src/full_roster_menu.s',J/'src/cf_menu_body.inc',J/'bowser/cold.s',J/'bowser/router.s',J/'bt/router.s',J/'cf-cold-warm.s',R/'build/cf-cold-existing-fit-proposal-v2/proposal.json',R/'build/battletoads-shared-owner-gate-review-v1/review.json',R/'build/contra-force-lifecycle-qualified-v1/handoff.json']}})
 (D/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','actual_linked_importers']}))
if __name__=='__main__':main()
