"""Exact table-only native backdrop binding and finite owned kind values."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_installer_manifest_1103_v155 as M
O=M.O


def images():
 lab=json.loads((O/'native-labels-v153.json').read_text())
 runtime=(O/'native-runtime-v153.bin').read_bytes();meta=bytearray((O/'native-metadata-v149.bin').read_bytes());state=bytearray((O/'native-state-v153.bin').read_bytes())
 bank=lab['NativeBank']-0xc800;lo=1375+lab['NativeLo']-0xc766;hi=1375+lab['NativeHi']-0xc766
 assert(meta[bank],state[lo],state[hi])==(0xcf,0xe7,0xba)
 meta[bank]=0xce;state[lo]=0x96;state[hi]=0xa2
 return runtime,bytes(meta),bytes(state)


def main():
 base,q=M.image();runtime,meta,state=images();lab=json.loads((O/'native-labels-v153.json').read_text())
 assert M.C.M.A.L.P.T.labels(O/'post-owner-v155.lbl')['PrTypedWorker']==0xab72
 from check_tmnt_render_oa import address,location
 assert address(base,'X5QueueAreaBackdrop')==0xa296 and ((location(base,'X5QueueAreaBackdrop')-16)//8192)|128==0xce
 at=location(base,'X5QueueAreaBackdrop');native=base['raw'][at:at+50]
 assert native[:5]==bytes.fromhex('aeae04e070')and bytes.fromhex('a93f9daf04a9109db004a9019db104')in native
 # Keep explicit assembled-source declarations for these data-only edits.
 services=(O/'native-services-v149.s').read_text();audio=(O/'native-audio-v149.s').read_text()
 assert services.count('NativeBank:.byte $cf,')==1
 services=services.replace('NativeBank:.byte $cf,','NativeBank:.byte $ce,')
 for op in ['<','>']:
  assert audio.count(op+'$bae7,')==1;audio=audio.replace(op+'$bae7,',op+'$a296,')
 (O/'native-services-v157.s').write_text(services);(O/'native-audio-v157.s').write_text(audio)
 sources={n:(O/f'native-{n}-v149.s').read_text()for n in ['services','battle','proxy','public','policies','audio','small']};sources.update(services=services,audio=audio)
 calls=[];writers=[]
 for name,text in sources.items():
  lines=text.splitlines()
  for index,line in enumerate(lines):
   if re.fullmatch(r'\s*(jsr|jmp) PpNativeCall',line):calls.append(dict(component=name,line=index+1,predecessor=lines[index-2:index+1]))
   if 'PpNativeCallKind+1'in line:writers.append([name,index+1,line.strip()])
 assert len(calls)==3 and {x['component']for x in calls}=={'proxy','policies','audio'},calls
 assert writers==[['services',services.splitlines().index(' sty PpNativeCallKind+1')+1,'sty PpNativeCallKind+1']],writers
 assert ' stx InvDropEnemy\n ldy #1\n jsr PpNativeCall'in sources['proxy']
 assert ' ldy #0\n jsr PpNativeCall'in sources['policies']
 assert 'PpNativeDeathUpdate:\n ldy #3\n bne NativeGo\nNativePickup:\n ldy #2\nNativeGo:\n jmp PpNativeCall'in audio
 # The original source graph's only indirect data/control operations are
 # the immutable script reader and the finite original command dispatcher.
 graph={k:v for n in ['contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json']for k,v in json.loads((O/n).read_text())['instructions'].items()};assert len(graph)==2485
 indirect={k:[v['mn'],v['mode'],v['value']]for k,v in graph.items()if v['mode']in ['iny','inx','ind']}
 assert all(tuple(v)in [('LDA','iny',0x21),('JMP','ind',0x23)]for v in indirect.values())
 prior=json.loads((O/'collision-lifetime-proposal-v62.json').read_text());assert prior['passed']
 audio_aliases={k:v for k,v in graph.items()if v['mn']not in ['JSR','JMP']and v['mode']in ['abs','zpg','abx','aby','zpx','zpy']and v['value']<0x800 and v['value']+(256 if v['mode']in ['abx','aby','zpx','zpy']else 1)>0x766}
 assert audio_aliases==prior['original_reader_closure']['conservative_audio_index_sites']
 # A3 BFA3 is source-declared cold finalizer, not a guessed zero hole.
 life=M.C.M.A.L.P.T.labels(O/'host-life-v12.lbl');assert life['PpHostColdFinalize']==0xbfa3
 public=sources['public'];assert ' jmp PpNativeInit'in public and ' ldx #$65\nFreshLastPage:\n sta $c700,x'in public
 assert state[:1375]==(O/'native-state_code-v18.bin').read_bytes()and state[0xc200-0xc0b0:0xc235-0xc0b0]==bytes(53)
 q=dict(passed=True,source_only=True,ROM_written=False,root_lifetime_shared_grant_required=True,source_instruction_boundaries=len(graph),NativeCallKind_writer=writers,all_native_gateway_callers=calls,finite_NativeCallKind_values={'0':'Only owned Colors calls genuine X5QueueAreaBackdrop CE:A296','1':'Validated source-earned guard defeat uses unchanged native9AF8','2':'Actual native star/1up collector','3':'Actual native death updater'},obsolete_kind0_KillPlayer_unreachable='Current source fatal request is privatePpDead2 and existing post-resident PRG124 hook; no remaining kind0 caller before owned Colors. The sole STY kind operand writer executes before every LDY operand read; no alternate public/indirect entry is admitted.',original_indirect_sites=indirect,original_indirect_closure=prior['original_reader_closure']['script_reader'],finite_original_audio_aliases=audio_aliases,cold_live_reader_closure='Original2485instruction graph and frozen constructor/script/pose finite domains cannot target host finalizerBFA3 or original OAMpacketC200; only typedcold decoder reachesBFA3 as its explicit return. Original coldprefixC766..C780 JMPs BFA7 before newBFC4 stages installer over it. Only resident after-return helper invokes new C766 installer; warmResetTail/Fresh targets DEE7/D963 and never finalizer/installer. Original pose renderer packet is synchronous and writes every consumed byte before read; native gateway overwrites13byte packet before read. All53cold bytes are zero before live header publication, demonstrated actual156; no header/cache/auth weakening.',native_backdrop_exact_target={'physical_PRG':78,'CPU':0xa296,'bank':0xce,'first50_hex':native.hex(),'role':'Unchanged X5QueueAreaBackdrop queues3F10 and uses BackgroundColorCtrl or AreaType, including its existing buffer capacity guard'},metadata_data_byte_PC=lab['NativeBank'],audio_data_byte_PC=[lab['NativeLo'],lab['NativeHi']],component_SHA256={n:M.sha(data)for n,data in zip(['runtime','metadata','state'],[runtime,meta,state])},cleanup={'exact_removed_unbound_linker_sidecars':20,'preserved_all_source_binary_combinedlabels_manifest_negative':True},remaining='Actual corrected backing/fullcold, genuine GetPlayerColors/WriteGameText status callers, cold failclosed/IRQ/FF/nested and root exact resource amendment; no native-ready claim.',bindings={p.relative_to(R).as_posix():M.sha(p.read_bytes())for p in [Path(__file__),O/'native-services-v157.s',O/'native-audio-v157.s',O/'native-runtime-v153.bin',O/'native-metadata-v149.bin',O/'native-state-v153.bin',O/'native-labels-v153.json',O/'live-cold-CPU-v156.json',O/'collision-lifetime-proposal-v62.json',*[O/n for n in ['contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json']]]})
 (O/'backdrop-binding-v157.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','original_indirect_sites','finite_original_audio_aliases']}))


if __name__=='__main__':main()
