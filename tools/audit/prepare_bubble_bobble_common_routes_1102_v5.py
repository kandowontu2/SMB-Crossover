"""Measure source-owned actual service/scene routes; never mutate the ROM."""
import json
import prepare_bubble_bobble_common_cold_1102_v4 as P
from check_tmnt_render_oa import address,location
R=P.R;O=P.O


def main():
 b=P.scoped_load(P.ROM);assert P.sha(b['raw'])==P.PIN
 owner=P.P.labels(O/'common-owner.lbl');ex=R/'build/excitebike-pose-1101-v3'
 prefix=(ex/'dispatch.s').read_text().split('.include "owner-loader.inc"')[0]
 prefix+=''.join(f'{n}=${address(b,n):04x}\n'for n in['R3','R4','R5','R6','R7'])
 prefix+=f'ExCheckCode=${owner["CoCheckCode"]:04x}\nExSavedSmcOffsets=${owner["CoSmc"]:04x}\nExLoad=${owner["CoCold"]:04x}\nCoRetire=${owner["CoRetire"]:04x}\nExPriorScene=$ac1d\nExCacheServices=$a500\nBbCacheServices=$a000\n'
 for alias,name in[('ExOriginalColors','NrColors'),('ExOriginalStatus','RlNameDispatch')]:prefix+=f'{alias}=${address(b,name):04x}\n{alias}Bank=${((location(b,name)-16)//8192)|128:02x}\n'
 source=(R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc').read_text()
 assert source.count(' cmp #37\n beq ExDispatchOwn')==1
 source=source.replace(' cmp #37\n beq ExDispatchOwn',' and #$fd\n cmp #37\n beq ExDispatchOwn')
 assert source.count(' lda #>ExCacheServices')==1
 source=source.replace(' lda #>ExCacheServices',' lda #>BbCacheServices\n ldx SelectedCharacter\n cpx #39\n beq :+\n lda #>ExCacheServices\n:')
 gate='''
.segment "CO_SCENE_GATE"
.export CoSceneGate,CoSceneGateEnd
CoSceneGate:
 php
 pha
 lda SelectedCharacter
 and #$fd
 cmp #37
 beq CoSceneOwn
 pla
 plp
 jmp ExPriorScene
CoSceneOwn:
 jmp ExSceneOwn
CoSceneGateEnd:
.segment "CO_RETIRE_STUB"
 jmp CoRetire
'''
 scene=(R/'tools/reference/excitebike_scene_1101_v1.inc').read_text().split('.segment "EX_SCENE_OWN"')[1]
 source+=gate+'\n.export ExSceneOwn\n.segment "EX_SCENE_OWN"'+scene
 source+='\nExReset=$b100\n'
 cfg='MEMORY{D:start=$a740,size=$ba,file=%O;V:start=$b08c,size=$6f,file="'+(O/'common-route-veneers.bin').as_posix()+'";F:start=$b031,size=49,file="'+(O/'common-route-foreign.bin').as_posix()+'";FB:start=$b105,size=2,file="'+(O/'common-route-foreign-bank.bin').as_posix()+'";G:start=$b013,size=19,file="'+(O/'common-route-scene-gate.bin').as_posix()+'";S:start=$b062,size=21,file="'+(O/'common-route-scene-own.bin').as_posix()+'";T:start=$b026,size=3,file="'+(O/'common-route-retire-stub.bin').as_posix()+'";}SEGMENTS{EX_DISPATCH:load=D,type=ro;EX_VENEERS:load=V,type=ro;EX_FOREIGN_UI:load=F,type=ro;EX_FOREIGN_BANK:load=FB,type=ro;CO_SCENE_GATE:load=G,type=ro;EX_SCENE_OWN:load=S,type=ro;CO_RETIRE_STUB:load=T,type=ro;}'
 lab=P.assemble('common-routes',prefix+source,cfg)
 def current(pc,count):return b['raw'][16+65*8192+pc-0xa000:16+65*8192+pc-0xa000+count]
 foreign=(O/'common-route-foreign.bin').read_bytes();foreignbank=(O/'common-route-foreign-bank.bin').read_bytes()
 oldforeign=bytearray(current(0xb031,len(foreign)));growth=len((O/'common-routes.bin').read_bytes())-167
 relocations=[]
 for offset,opcode,role in[(10,0xbd,'indexed ExForeignLo reader'),(45,0x4c,'foreign rejection JMP ExDispatchNo')]:
  assert oldforeign[offset-1]==opcode
  old=int.from_bytes(oldforeign[offset:offset+2],'little');assert 0xa740<=old<0xa7e7
  oldforeign[offset:offset+2]=(old+growth).to_bytes(2,'little');relocations.append(dict(role=role,PC=0xb031+offset-1,old_target=old,new_target=old+growth))
 assert foreign==oldforeign and foreignbank==current(0xb105,len(foreignbank))
 q=dict(passed=True,proposal_only=True,ROM_written=False,shared_routing_granted=False,ROM_SHA256=P.PIN,dispatch_bytes=len((O/'common-routes.bin').read_bytes()),dispatch_half_open=[0xa740,0xa740+len((O/'common-routes.bin').read_bytes())],scene_gate_half_open=[lab['CoSceneGate'],lab['CoSceneGateEnd']],scene_own_half_open=[0xb062,0xb077],retirement_stub_half_open=[0xb026,0xb029],foreign_UI_exact=True,existing_Ex_veneers_unchanged=True,existing_row19_reset_target=0xb100,labels=lab,planned_rebindings=['ExDispatch auth call and both savedSMC table operands','Actual InitScreen farcall target→CoSceneGate B013','ExSceneOwn loader→CoCold AE00','Existing ExReset B100→CoRetire AE0B','Foreign Sh menu/scene calls remainB026, now a JMP CoRetire'],remaining=['Actual full public Hu/scene/foreign parity and ISR proof.','Confirm all raw39 policies are source-safe and graphics/colors/status/contact/AI/birth ingresses before any admission.','Actual shot-bank and bbox wrappers still distinguish only36/37 and require measured39 ingress.'])
 q.update(foreign_UI_exact_except_source_bound_relocations=True,foreign_UI_exact=False,foreign_relocations=relocations)
 (O/'common-routes-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,dispatch_bytes=q['dispatch_bytes'],dispatch_growth=q['dispatch_bytes']-167,scene_gate_bytes=19,foreign_UI_relocations=len(relocations),ROM_written=False)))


if __name__=='__main__':main()
