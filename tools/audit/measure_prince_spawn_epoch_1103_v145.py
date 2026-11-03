"""Zero-growth source constructor resync at the first real native engine8 epoch."""
from pathlib import Path
import inspect,json,sys
from types import SimpleNamespace
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_deferred_strike_1102_v116 as V
import prepare_prince_strike_manifest_1103_v130 as CURRENT
O=V.O


def main():
 source=Path(V.__file__);text=inspect.getsource(V.main).replace('v116','v145')
 start=text.index(' _,manifest=C.image()');end=text.index(' images={}',start)
 setup=''' _,manifest=C.image();old=json.loads((O/'native-labels-v122.json').read_text());refs=dict(old)
 texts={n:(O/f'native-{n}-v122.s').read_text()for n in ['services','battle','proxy','public','policies','audio','small']}
 oldclear='PpNativeInit:\\n lda #0\\n sta PpReady\\n jsr PpHostInit'
 assert texts['services'].count(oldclear)==1
 texts['services']=texts['services'].replace(oldclear,'PpNativeInit:\\n jsr PpHostInit')
 assert texts['services'].count(' beq NewEpoch')==1
 texts['services']=texts['services'].replace(' beq NewEpoch',' beq PpFirstStageEpoch')
 texts['services']=texts['services'].replace('PpNativeRetire:','PpFirstStageEpoch:\\n jsr PpNativeInit\\n bne NewEpoch ; Init returns A=$a7/Z0; exactly the prior5B constructor span.\\nPpNativeRetire:')
'''
 text=text[:start]+setup+text[end:]
 text=text.replace("if name=='audio':text=","if name=='audio'and not text.startswith('PpNativeProxyOut='):text=")
 text=text.replace('native-runtime-v78.bin','native-runtime-v122.bin').replace('native-metadata-v78.bin','native-metadata-v122.bin')
 needle="assert len(meta)==6095 and 0xc800+len(meta)==0xdfcf and labels['public']['PpNativeRoute']==old['PpNativeRoute']and labels['services']['PpNativeRetire']==old['PpNativeRetire']"
 assert needle in text;text=text.replace(needle,needle+",(len(meta),labels['public']['PpNativeRoute'],old['PpNativeRoute'],labels['services']['PpNativeRetire'],old['PpNativeRetire'])")
 adapter=SimpleNamespace(**dict(V.C.__dict__,image=CURRENT.image));env=dict(V.__dict__,C=adapter,__file__=str(Path(__file__)));exec(compile(text,str(source),'exec'),env);env['main']()
 path=O/'deferred-strike-measurement-v145.json';q=json.loads(path.read_text());lab=json.loads((O/'native-labels-v145.json').read_text());old=json.loads((O/'native-labels-v122.json').read_text())
 assert all(lab[n]==old[n]for n in ['PpNativeInit','PpNativeRetire','PpNativeTick','PpNativeRoute','PpNativeCall'])
 assert (O/'native-runtime-v145.bin').read_bytes()==(O/'native-runtime-v122.bin').read_bytes()and(O/'native-state-v145.bin').read_bytes()==(O/'native-state-v122.bin').read_bytes()
 before=(O/'native-metadata-v122.bin').read_bytes();after=(O/'native-metadata-v145.bin').read_bytes();changes=[0xc800+i for i,(a,z)in enumerate(zip(before,after))if a!=z]
 assert all(old['PpNativeInit']<=at<old['PpNativeRetire']or old['PpNativeTick']<=at<old['PpNativePitDeath']for at in changes)
 q.update(source_runtime_version=145,spawn_resync_proposal=True,source_backing_growth=0,new_shared_spans=0,new_state_cells=0,actual_changed_metadata_bytes=len(changes),changed_metadata_PC=changes,entry_addresses_unchanged=True,constructor_policy='Existing native engine7 entrance remains untouched. Only already-authenticated/live engine8 Tick with original EpochValid0 resynchronizes the original source constructor from actual native XY/high page once, before source phase0/export. No position constant, new queue or fabricated terrain/outcome. Later epochs use unchanged source movement.',funding='Existing NativeInit5B Ready clear was redundant on every prior constructor ingress: cold continuation zeroesC000..AF then JMPs ResetTail; both publicFresh paths zeroC000..AF then JMP NativeInit. Exact5B becomes JSR NativeInit/BNE NewEpoch helper atD98A..D98F; every downstream address unchanged. New first8 sync is foreground-exclusive before any original live update; Init returns A=A7/Z0.',required='Full finite direct/indirect constructor caller closure including actual CoCold/reset, firstnative engine8 stale-origin reproduction/current coordinates, engine7 parity, warm/retire lifetime, IRQ/genuineFF/nested checks before changed backing/cookie/ROM. Colors/backdrop/status fixes separate; not native-ready.')
 q['bindings'].update({p.relative_to(R).as_posix():CURRENT.M.sha(p.read_bytes())for p in [Path(__file__),source,O/'deferred-strike-measurement-v122.json',O/'native-services-v122.s',O/'native-public-v122.s',O/'native-runtime-v122.bin',O/'native-spawn-diagnostic-v144/capture/spawn-first-write.csv',R/'src/player.s']});path.write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:q[k]for k in ['spawn_resync_proposal','actual_changed_metadata_bytes','entry_addresses_unchanged','metadata_bytes','metadata_end','constructor_policy','required']}))


if __name__=='__main__':main()
