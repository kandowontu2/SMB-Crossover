"""Measure ungranted private policy tail; original hues/reaction, native ABI.

No ROM, shared mutation, menu admission, or additional allocation is made.
The link address is a proposed exact tail whose consumer grant is separate.
"""
from collections import Counter
from pathlib import Path
import hashlib,itertools,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_cold_worker_1102_v19 as A
import check_prince_host_services_1102_v18 as H
import measure_prince_lzdict_1102_v9 as D
from check_tmnt_render_oa import address
O=A.O;P=H.P;N=H.N


def call(h,name,args=(83,71,109,0x21)):
 h.map();c=N.NesMPU(memory=h.m,pc=h.lab[name]);c.a,c.x,c.y,c.p=args;c.sp=224;c.stPushWord(0x5aff);low=c.sp
 for _ in range(50000):
  if c.pc==0x5b00:break
  low=min(low,c.sp);assert h.m[c.pc]!=0,('Policy BRK',name,hex(c.pc));c.step()
 else:raise AssertionError(('Policy instruction bound',name,hex(c.pc)))
 assert c.sp==224
 return c,low


def main():
 proof=json.loads((O/'player-reaction-CPU-v31.json').read_text());assert proof['passed']
 for name,digest in proof['bindings'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
 b=H.W.scoped_load(H.E.C.BASE)
 # Native palette0 is the ordinary player slot. Original Prince cells all
 # use sourcepalette1; remap the selector only and copy its actual hues.
 art=json.loads((O/'source-art.json').read_text());attrs=Counter(p['attribute']&3 for pose in art['poses']for p in pose['parts_8x16']);assert attrs=={1:2578}
 palette=json.loads((O/'palette-health-authority-v29.json').read_text())['source_sprite_palette_PPU_3F10_3F20'];assert palette[5:8]==[0x27,0x16,0x20]
 lab=P.T.labels(O/'host-services-v18.lbl');life=P.T.labels(O/'host-life-v12.lbl')
 # This is a measured tail outside the current DD32 grant, not a granted
 # placement. The complete original source component remains v31-frozen.
 source=(O/'player-reaction-v31.s').read_text().replace('PpOriginalAlignmentBoundary=$5100',f'PpOriginalAlignmentBoundary=${life["PpWorldLandingAlign"]:04x}')
 source=source.replace('.segment "REACTION"','.segment "POLICIES"')
 defs={n:address(b,n)for n in ['VRAM_Buffer1','VRAM_Buffer1_Offset']}
 defs.update(PpNativeOriginalPitDeath=lab['PpNativePitDeath'],PpNativeKill=lab['Kill'])
 source=''.join(f'{n}=${v:04x}\n'for n,v in defs.items())+source+'''
.export PpNativeContact,PpNativeHealthStatus,PpNativeColors,PpNativeDeathCheck
.export PpNativePoliciesEnd
; The native collision owner has already established real enemy overlap.
; Repeat admission uses the actual original defender-action exclusions at
;4:ACEC..ACF5. No host timer or invented number of grace frames is written.
PpNativeContact:
 php
 pha
 txa
 pha
 tya
 pha
 lda $c6cf
 beq ContactDone
 lda $c616
 cmp #$4a
 beq ContactDone
 cmp #$45
 beq ContactDone
 jsr PpPlayerCombatHurt
ContactDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
; Always route even the last source HP through the owned reaction. The
; native ForceInjury caller tests Z, not a Mario small/big power status.
PpNativeHealthStatus:
 lda #1
 sec
 rts
; Preserve universal backdrop; publish only the three source player hues.
; Six bytes plus terminator must fit the existing84B native queue.
PpNativeColors:
 php
 pha
 txa
 pha
 tya
 pha
 ldx VRAM_Buffer1_Offset
 cpx #$4e
 bcs ColorsDone
 ldy #0
ColorsCopy:
 lda ColorsPacket,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #6
 bne ColorsCopy
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
ColorsDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
ColorsPacket:.byte $3f,$11,3,$27,$16,$20
; The source death85 program reaches final pose185 and then loops there.
; Allow the original animation before the genuine native death service.
; Original source action/pose determine completion, never a host timer.
PpNativeDeathCheck:
 lda $c6cf
 bne CheckPit
 lda $c0ac
 bne DeathDone
 lda $c616
 cmp #85
 bne CheckPit
 lda $c617
 cmp #185
 bne CheckPit
 jmp PpNativeKill
CheckPit:
 jmp PpNativeOriginalPitDeath
DeathDone:
 clc
 rts
PpNativePoliciesEnd:
'''
 blob,labels=A.assemble('player-policies-v32',source,'MEMORY{M:start=$dd32,size=$29e,file=%O;}SEGMENTS{POLICIES:load=M,type=ro;}')
 def host():
  h=H.host(b);h.lab.update(labels);h.s[0x1d32:0x1d32+len(blob)]=blob;h.s[0x7f]=208;h.s[0x80]=0
  return h
 checks=Counter();cpu=[];minimum=224
 for hp,action,flags in itertools.product(range(6),[0,4,69,74,85],[0x20,0x61,0xa1]):
  h=host();h.s[0x6cf]=hp;h.s[0x616]=action;before=bytes(h.s);c,low=call(h,'PpNativeContact',(83,71,109,flags));minimum=min(minimum,low);cpu.append(c.processorCycles)
  assert(c.a,c.x,c.y,c.p&0xef,c.sp)==(83,71,109,(flags|1)&0xef,224)
  blocked=hp==0 or action in [69,74]
  assert h.s[0x6cf]==(hp if blocked else hp-1)
  assert h.s[0x616]==(action if blocked else (85 if hp==1 else 74))
  if blocked:assert bytes(h.s)==before
  else:
   assert h.s[0x6dc]==10 and h.s[0x6d2]==1
   assert h.s[0xad:0xaf]==bytes([255,12])
  checks['native_contact_blocked'if blocked else'native_contact_applied']+=1
 # Every queue offset, including corrupt ones, proves exact bounded writes.
 for off,flags in itertools.product(range(256),[0x20,0xa1]):
  h=host();N.put(h.m,VRAM_Buffer1_Offset=off);at=address(b,'VRAM_Buffer1');before=bytes(h.m[at:at+340]);c,low=call(h,'PpNativeColors',(83,71,109,flags));minimum=min(minimum,low)
  assert(c.a,c.x,c.y,c.p&0xef,c.sp)==(83,71,109,(flags|1)&0xef,224)
  if off<78:
   assert bytes(h.m[at+off:at+off+7])==bytes([63,17,3,39,22,32,0])
   assert N.get(h.m,'VRAM_Buffer1_Offset')==off+6
   assert bytes(h.m[at:at+off])==before[:off]and bytes(h.m[at+off+7:at+340])==before[off+7:]
  else:assert bytes(h.m[at:at+340])==before and N.get(h.m,'VRAM_Buffer1_Offset')==off
  checks['palette_offsets']+=1
 # Source-live original memory never observes the proposed metadata tail:
 # ordinary/coordinate state operands are <0800; script reads and15command
 # jumps are translated into exact authenticated sections, not arbitrary RAM.
 graph={}
 for filename in ['contact-recovery.json','world-coordinate-recovery-v7.json']:graph.update(json.loads((O/filename).read_text())['instructions'])
 direct=0;indirect=[]
 for key,v in graph.items():
  if v['mn']in ['JSR','JMP']and v['mode']!='ind':continue
  if v['mode']in ['abs','abx','aby','zpg','zpx','zpy']and v['value']<2048:
   assert 0xc000+v['value']+(256 if v['mode']in ['abx','aby','zpx','zpy']else 1)<=0xc900;direct+=1
  if v['mode']in ['iny','inx','ind']:
   assert(v['mn'],v['mode'],v['value'])in [('LDA','iny',0x21),('JMP','ind',0x23)];indirect.append(key)
 runtime=bytearray((O/'public-runtime-v24.bin').read_bytes());drawsrc=(O/'host-render-compact-v11.s').read_text();assert 'lda #1\n ldx PpState+$615' in drawsrc and 'lda #$41\n:' in drawsrc
 draw=P.T.labels(O/'host-render-v11.lbl');start=draw['PpHostDraw']-0xa000
 needle=bytes([0xa9,1,0xae,0x15,0xc6,0xf0,2,0xa9,0x41]);positions=[i for i in range(start,len(runtime))if runtime[i:i+len(needle)]==needle];assert len(positions)==1,positions
 at=positions[0];runtime[at+1]=0;runtime[at+8]=0x40
 services=P.T.labels(O/'host-services-v18.lbl');needle=bytes([0x20,services['PpNativePitDeath']&255,services['PpNativePitDeath']>>8]);metadata=bytearray((O/'public-metadata-v24.bin').read_bytes());positions=[i for i in range(len(metadata))if metadata[i:i+3]==needle];assert len(positions)==1,positions
 metadata[positions[0]+1:positions[0]+3]=labels['PpNativeDeathCheck'].to_bytes(2,'little')
 assert len(metadata)==0x1524;metadata.extend(bytes(14));metadata.extend(blob)
 images=[bytes(runtime),bytes(metadata),(O/'native-state_code-v18.bin').read_bytes()];packed=[D.encode(data)for data in images]
 total=31072+254+442+sum(map(len,packed));end=0xdd32+len(blob)
 # Data blobs are small source proposals only, not a candidate ROM/pool.
 (O/'policy-runtime-v32.bin').write_bytes(runtime);(O/'policy-metadata-v32.bin').write_bytes(metadata)
 q=dict(passed=True,source_CPU_only=True,native_emulator=False,ROM_written=False,private_proposal_only=True,additional_placement_granted=False,component_bytes=len(blob),proposed_RAM2_tail_half_open=[0xdd32,end],additional_RAM2_bytes=len(blob),shared_clock_untouched=[0xdfd0,0xdfd3],remaining_before_shared_clock=0xdfd0-end,original_player_reaction_bytes=proof['component_bytes'],native_CPU_cases=dict(checks),contact_CPU=[min(cpu),max(cpu)],minimum_SP=minimum,source_palette_selector_remap=dict(original_index=1,native_player_index=0,foreground_hues=palette[5:8],original_pairs_with_only_palette1=2578,native_backdrop_unchanged=True,only_native_player_palette_3F11_3F13_written=True),native_repeat_contact_predicate='Original4:ACEC..ACF5 excludes defender actions69/74; HP0 also excluded. Genuine native overlap remains the caller. No InjuryTimer writes or invented grace.',death_completion='Source action85 reaches original pose185 before native KillPlayer; actual wholeMain/respawn not yet qualified.',source_graph_instruction_boundaries=len(graph),source_state_operand_domains=direct,source_indirect_sites=indirect,source_tail_reader_closure='All source direct/indexed state remains belowC900 even at256indices. Only translated script/command indirect sites; bounded408pose packets endDB9A. Source original cannot read proposedDD32 tail. Actual native ISR/current lifetime/cold decode/grant remain required.',physical_measurement=dict(current_capacity=44032,proposed_total=total,additional_physical_bytes_required=max(0,total-44032),one_additional_1KB_carrier_suffices=total<=45056,proposed_packed_bytes=list(map(len,packed)),typed_worker_assumed_same442B_pending_recompile=True),scope='Measured authentic reaction/native contact ABI and bounded source-hue palette leaf. New RAM2tail/physical carrier are requests only. New native box policy/outgoing sword/current cold and all-row routing/ISR/lifetime remain unqualified; no menu/native gameplay claim.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'player-reaction-CPU-v31.json',O/'player-reaction-v31.s',O/'player-policies-v32.bin',O/'policy-runtime-v32.bin',O/'policy-metadata-v32.bin',O/'source-art.json',O/'palette-health-authority-v29.json',R/'docs/qa/allocations/prince-shared-successor-1102-v30.json']})
 (O/'player-policies-measurement-v32.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','source_indirect_sites']}))


if __name__=='__main__':main()
