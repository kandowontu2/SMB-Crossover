"""Measure source-closed Prince no-drop acknowledgement and native defeat."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_deferred_strike_1102_v116 as V
O=V.O


def main():
 policy=json.loads((O/'native-drop-policy-CPU-v119.json').read_text());assert policy['passed']and policy['cases']==672 and not policy['actual_owner_tags']
 for path,digest in policy['bindings'].items():assert V.C.M.sha((R/path).read_bytes())==digest,path
 b,_=V.C.image();native=V.C.I.address(b,'InvDropEnemy');assert native==policy['only_native_effect']['address']and policy['suffix_entry']==0x9af8
 text=inspect.getsource(V.main).replace('v116','v120')
 marker=" texts['proxy']=p[:start]+out+p[end:]";assert marker in text
 replacement=""" assert out.count(' stx PpProxyBestSlot')==1
 out=out.replace(' stx PpProxyBestSlot',' stx InvDropEnemy')
 texts['proxy']=f'InvDropEnemy=${INV:04x}\\n'+p[:start]+out+p[end:]
 assert texts['audio'].count('NativeDefeat=$9af5')==1
 texts['audio']=texts['audio'].replace('NativeDefeat=$9af5','NativeDefeat=$9af8')"""
 text=text.replace(marker,replacement)
 env=dict(V.__dict__,INV=native,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
 path=O/'deferred-strike-measurement-v120.json';q=json.loads(path.read_text());q.update(native_no_drop_acknowledgement=dict(policy='native-drop-policy-CPU-v119.json',native_effect='STX InvDropEnemy, exactly the original hook effect.',original_prefix=[126,0x9af5,0x9af8],exact_original_suffix=0x9af8,private_only=True,source_authenticated_outer_entry_required=True,source_native_actor_domain='Flag1/ID0..6/notdefeated, genuine guardHP0/dead85/activeUID; no native data/outcome is invented.',redundant_BestSlot_store='ProxyIn already publishes BestSlot and activeUID together for every admitted guard. Removing its repeated Out store does not change original or host-visible state; wholeGameLoop differential must prove actual lifetime.'))
 q['bindings'].update({p.relative_to(R).as_posix():V.C.M.sha(p.read_bytes())for p in [Path(__file__),Path(V.__file__),O/'native-drop-policy-CPU-v119.json']});path.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
