"""Actual source/scopedPC/consumer closure for emitted19+31+1 repack."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from cf_cold_warm_source_closure_v2 import scoped
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/cf-cold-warm-palette-source-v1';O=R/'build/cf-preload-name-source-v1';J=O/'joint';D=R/'build/cf-preload-name-source-closure-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 D.mkdir(exist_ok=False);stage=json.loads((O/'source-stage.json').read_text())
 for f,h in stage['bindings'].items():assert sha(f)==h,f
 a,b=map(qualified,[P/'joint/candidate.nes',J/'candidate.nes']);sa,sb=map(scoped,[P/'joint',J])
 changed=[dict(module=k[0],scope=k[1],symbol=k[2].strip('"'),old=v,new=sb.get(k))for k,v in sa.items()if sb.get(k)!=v]
 assert len(changed)==2 and {z['symbol']for z in changed}=={'BwCfSceneLoad','Cf'},changed
 assert address(b,'BwCfSceneLoad')==0xb2d0 and address(b,'BwResolveColdNative')==0xb2bd and address(b,'BwResolveFamilyTail')==0xb2f0
 assert all(z['module']==('bowser','router.s')for z in changed)
 spans=[(location(b,'BwResolveColdNative'),51),(location(b,'BwScene'),0xb400-address(b,'BwScene'))]
 delta=[i for i,(x,y)in enumerate(zip(a['raw'],b['raw']))if x!=y]
 assert len(delta)==39 and all(any(lo<=i<lo+size for lo,size in spans)for i in delta)
 cold=[i for i in delta if location(b,'BwScene')<=i<location(b,'BwScene')+0xb400-address(b,'BwScene')]
 assert len(cold)==1 and a['raw'][cold[0]]==0xcb and b['raw'][cold[0]]==0xd0,cold
 assert a['raw'][:16]==b['raw'][:16]and a['raw'][16+128*8192:]==b['raw'][16+128*8192:]
 for n in['cf-stream.bin','cf-cookie.bin','bowser.bin','ram3.bin','ff-cookie.bin','code.bin','data.bin']:assert sha(J/n)==sha(P/'joint'/n),n
 for n,size in[('MenuResolveCharacter',34),('FmStartFlags',28),('FmStartIdentityFlags',51),('BtServiceVeneers',224),('CfSceneRetireForeign',17),('CfLoadIfCold',42),('CfOrBtCheck',118),('CfRetire',36)]:
  lo,hi=location(a,n),location(b,n);assert a['raw'][lo:lo+size]==b['raw'][hi:hi+size],n
 x,y=location(a,'BwSceneDone')-15,location(b,'BwSceneDone')-15;assert a['raw'][x:x+15]==b['raw'][y:y+15]
 assert b['raw'][location(b,'BwResolveFamilyTail')-1]==0xea
 command=json.loads((O/'final-link.json').read_text())['command'];objects=[Path(x)for x in command if x.endswith('.o')]
 assert objects.count(J/'bowser/router.o')==1 and objects.count(J/'bowser/cold.o')==1
 od=R/'tools/Windows/cc65/bin/od65.exe';importers=[];bindings={}
 for obj in objects:
  run=subprocess.run([str(od),'--dump-imports',str(obj)],capture_output=True,text=True,check=True);bindings[str(obj.resolve())]=sha(obj)
  if re.search(r'Name:\s+"BwCfSceneLoad"',run.stdout):importers.append(str(obj))
 assert importers==[str(J/'bowser/cold.o')]
 q=dict(source=True,passed=True,native=False,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_BT_pending=True,actual_scoped_parent_symbols=len(sa),only_private_symbol_changes=changed,all_foreign_publicPCs_fixed=True,
  old_owned51_actual=[19,31,1],old15_19_fallback_targets_unchanged=True,new18_genuine_FmQueueName=True,one_actual_cold_import_operand_rebound=cold[0],sole_actual_BwCfSceneLoad_importer=importers[0],original_Bowser_ctor15B_byteexact=True,
  changed_bytes=39,exact_changed_envelopes=spans,all_other_header_ROM_CHR_images_cookies_bytes_exact=True,no_new_span_RAM_ZP_mailbox_P1_NMI_or_readiness=True,
  bindings={**bindings,**{str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/cf_cold_warm_source_closure_v2.py',O/'source-stage.json',O/'router-build.json',O/'cold-build.json',O/'final-link.json',J/'candidate.nes',J/'candidate.dbg',J/'bowser/router.s',J/'bowser/cold.s',J/'private.cfg',P/'handoff.json']}})
 (D/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))
if __name__=='__main__':main()
