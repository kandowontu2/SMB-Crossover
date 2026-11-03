"""Private same-Main strike delivery at existing row34; no new resources."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
O=C.O


def main():
 _,manifest=C.image();old=json.loads((O/'native-labels-v78.json').read_text());refs=dict(old)
 texts={n:(O/f'native-{n}-v78.s').read_text()for n in ['services','battle','proxy','public','policies','audio','small']}
 assert texts['services'].count(' jsr PpNativeProxyOut\n')==1;texts['services']=texts['services'].replace(' jsr PpNativeProxyOut\n','')
 assert texts['audio'].count('PpNativeDeferredKill:\n')==1;texts['audio']=texts['audio'].replace('PpNativeDeferredKill:\n','PpNativeDeferredKill:\n jsr PpNativeProxyOut\n')
 p=texts['proxy'];start=p.index('PpNativeProxyOut:');end=p.index('PpProxyBestSlot:',start);out=p[start:end]
 out=re.sub(r'(?m)^( b(?:ne|pl|cs)) Return$',r'\1 DefeatNo',out)
 assert out.count(' rts')==1
 out=out.replace(' rts',' clc\n rts\nDefeatNo:clc\n rts')
 texts['proxy']=p[:start]+out+p[end:]
 images={};labels={};ends={};previous=None
 for iteration in range(8):
  refs.update({k:v for row in labels.values()for k,v in row.items()})
  if 'services'in labels:
   refs['PpNativeSfx']=refs['PpNativeRawSfx']=labels['services']['PpNativeQuietSfx']
  if 'battle'in labels:refs['PpOriginalDefenderContact']=labels['battle']['PpBattle_4_ACEC']
  at=old['PpNativeInit']
  for name,segment in [('services','SERVICES'),('battle','BATTLE'),('proxy','PROXY'),('public','PUBLIC'),('policies','COLORS'),('audio','AUDIO'),('small','SMALL')]:
   text=re.sub(r'(?m)^(\w+)=\$[0-9a-fA-F]+$',lambda m:f'{m[1]}=${refs[m[1]]:04x}'if m[1]in refs else m[0],texts[name])
   if name=='audio':text=f'PpNativeProxyOut=${refs["PpNativeProxyOut"]:04x}\n'+text
   supplemental='';segments=''
   if name=='public':supplemental=f'F:start=$b3ef,size=$11,file="{(O/"native-fresh-v116.bin").as_posix()}";';segments='FRESH_PREFIX:load=F,type=ro;'
   if name=='policies':supplemental=f'C:start=$bd22,size=$1c,file="{(O/"native-contact-v116.bin").as_posix()}";';segments='CONTACT:load=C,type=ro;'
   start=0xc766 if name=='audio'else 0xbd3e if name=='small'else at
   cfg=f'MEMORY{{M:start=${start:04x},size=$800,file=%O;{supplemental}}}SEGMENTS{{{segment}:load=M,type=ro;{segments}}}'
   images[name],labels[name]=C.M.A.assemble('native-'+name+'-v116',text,cfg);refs.update(labels[name]);ends[name]=[start,start+len(images[name])]
   if name not in ['audio','small']:at+=len(images[name])
  signature=json.dumps(labels,sort_keys=True)
  if signature==previous:break
  previous=signature
 else:raise AssertionError('Deferred strike relink did not converge')
 meta=(O/'native-metadata-v78.bin').read_bytes()[:old['PpNativeInit']-0xc800]+b''.join(images[n]for n in ['services','battle','proxy','public','policies'])
 assert len(meta)==6095 and 0xc800+len(meta)==0xdfcf and labels['public']['PpNativeRoute']==old['PpNativeRoute']and labels['services']['PpNativeRetire']==old['PpNativeRetire']
 runtime=bytearray((O/'native-runtime-v78.bin').read_bytes());fix=[]
 graph=json.loads((O/'contact-recovery.json').read_text())['instructions'];core=dict(C.M.A.L.P.T.labels(O/'contact-core.lbl'),**old)
 for key,ins in graph.items():
  if ins['mn']not in ['JSR','JMP']:continue
  bank,pc=key.split(':');off=core[f'PpN_{bank}_{pc}']-0xa000;target=int.from_bytes(runtime[off+1:off+3],'little')
  mapping={old[n]:labels['services'][n]for n in ['PpNativeQuietSfx','PpNativeQuietMusic','PpNativeUnpublishedMaterial']}
  if target in mapping:runtime[off+1:off+3]=mapping[target].to_bytes(2,'little');fix.append([0xa000+off,target,mapping[target]])
 for name,delta in [('PpN_7_F044',2),('PpN_7_F08D',3)]:
  off=core[name]-0xa000+delta;assert int.from_bytes(runtime[off+1:off+3],'little')==old['PpCombatControls'];runtime[off+1:off+3]=labels['battle']['PpCombatControls'].to_bytes(2,'little')
 runtime[0xb3ef-0xa000:0xb3fc-0xa000]=(O/'native-fresh-v116.bin').read_bytes();runtime[0xbd22-0xa000:0xbd3e-0xa000]=(O/'native-contact-v116.bin').read_bytes();runtime[0xbd3e-0xa000:0xbd4b-0xa000]=images['small']
 assert len(runtime)==8159 and len(images['audio'])<=154
 state=(O/'native-state_code-v18.bin').read_bytes()+images['audio']+bytes(154-len(images['audio']))
 combined=dict(old,**{n:v for row in labels.values()for n,v in row.items()if n.startswith('Pp')or n in ['NativeLo','NativeHi','NativeBank']})
 for n,data in [('runtime',runtime),('metadata',meta),('state',state)]:(O/f'native-{n}-v116.bin').write_bytes(data)
 (O/'native-labels-v116.json').write_text(json.dumps(combined,indent=2)+'\n')
 q=dict(measured=True,qualified=False,ROM_written=False,new_shared_spans=0,new_state_cells=0,source_parent_memory_SHA256=manifest['expected_memory_only_SHA256'],components=ends,metadata_bytes=len(meta),metadata_end=0xdfcf,audio_bytes=len(images['audio']),audio_spare=154-len(images['audio']),source_state_stream_bytes=len(state),runtime_bytes=len(runtime),public_route_unchanged=combined['PpNativeRoute'],retire_unchanged=combined['PpNativeRetire'],source_event_fields=['C6D0 guardHP0','C6DE original dead85','C61C active native UID128|slot'],same_Main_order='Original sourceTick earns terminal guard; movement export completes; GameCore ProcFireball_Bubble invokes existing authenticated row34 before any EnemiesAndLoopsCore/playerdraw. Same ProxyOut delivers native defeat before original pending nativeKill query. Source actor fields are the request, no fabricated hit/timer/engine/life outcome or new queue cells.',carry='Every ProxyOut return is C0. Existing postreturn C1 nativeKill hook is reserved for actual pending death.',runtime_call_relocations=fix,required='Current actualGameLoop old/new source/native boundary and finalstate parity; exactly-once/multi-actor/stale actor/scene reset; full FF-lag and nestedIRQ. New physical compressed backing/cookie/auth/cold image still pending; this is source-only measurement.',bindings={p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),O/'post-return-manifest-v97.json',O/'current-earned-defeat-negative-v114.json',*[O/f'native-{n}-v78.s'for n in texts],R/'src/game.s',R/'src/object.s',R/'src/new_roster_dispatch.s']})
 (O/'deferred-strike-measurement-v116.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','runtime_call_relocations']}))


if __name__=='__main__':main()
