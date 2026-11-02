"""Independent relocatable8KB donor component; never patch a host ROM."""
import json,re,subprocess
import recover_bubble_bobble_source_1101_v1 as B
from py65.disassembler import Disassembler

R=B.R;O=B.O;STATE=0xc000
API={
 'BbSourceClock':0xce30,
 'BbSourceInit':0xd18a,'BbSourceSprites':0xd28e,'BbInput':0xd1a0,
 'BbPlayerStep':0xd1e7,'BbBubbleStep':0xd887,'BbTrappedEnemyStep':0x9528,
 'BbPoseStep':0xd580,'BbHurtBub':0xd54e,'BbHurtBob':0xd578,
 'BbJumpStart':0xd365,'BbJumpAscent':0xd386,'BbShotRequest':0xd530,
 'BbBubbleContact':0xdc55,'BbPopChain':0xdd6d,'BbBubbleSupport':0xd331,
}
IMPORTS={0xc0a4:'Score',0xc470:'LivesUI',0xcee3:'Yield',0xe009:'StageEffects',
 0xee70:'SpecialAbility',0xf01e:'StageBubbles',0xf272:'SpecialPop',0xfa81:'Sound',
 0x8153:'BossPlayer',0x8156:'BossDeath',0x97c9:'EnemyDraw',0x9603:'EnemyRelease',
 0xd870:'FoodUpdate',0xd873:'ElementalUpdate'}
BRANCHES={'BEQ':'jeq','BNE':'jne','BMI':'jmi','BPL':'jpl','BCS':'jcs','BCC':'jcc','BVS':'jvs','BVC':'jvc'}


def ram(a):
 if a<256:return STATE+a
 if 0x200<=a<0x300:return STATE+a-0x100
 if 0x400<=a<0x500 or a in [0x3ab,0x3ac,0x3ad]:return STATE+a-0x200
 raise AssertionError(hex(a))


def labels(p):return {n:int(a,16)for a,n in re.findall(r'^al ([0-9a-fA-F]+) \.(\S+)$',p.read_text(),re.M)}


def main():
 manifest=json.loads((O/'source-closure.json').read_text());idx=json.loads((O/'instruction-index.json').read_text());rows={(b,p):c for b,p,c in idx['rows']}
 syms={};allbytes={}
 for s in manifest['source_ranges']:
  for a in range(s['start'],s['end_exclusive']):allbytes[a]=s['bank'];syms[a]=f'BbOriginal_{a:04X}'
 def code(a):
  if a in syms:return syms[a]
  assert a in IMPORTS,hex(a)
  return 'BbImport'+IMPORTS[a]
 def data(a):
  if a<0x800:return f'${ram(a):04x}'
  if a in [0xdf81,0xdf82]:return 'BbBubbleTileTable'+(''if a==0xdf81 else'+1')
  assert a in syms,hex(a)
  return syms[a]
 source=['.setcpu "6502"\n.macpack longbranch\n.segment "BB_VECTORS"\n.export BbServices,BbReject,BbImports,BbCodeEnd\nBbServices:\n.repeat 37\n jmp BbReject\n.endrepeat\nBbReject:clc\n rts\n.segment "BB_IMPORTS"\nBbImports:']
 # An unbound image rejects imports. The host loader must bind/verify vectors
 # before authenticating it; the37 native service rows remain fail-closed.
 importrows=[]
 for a,name in list(IMPORTS.items())+[(0,'Tile23'),(1,'Tile84')]:
  source.append(f'.export BbImport{name}\nBbImport{name}: jmp BbReject')
  importrows.append(dict(name=name,source=a if a>1 else None))
 source.append('.segment "BB_CODE"')
 for name,a in API.items():source.append(f'.export {name}\n{name}={code(a)}')
 substitutions=[];promoted=0
 for s in manifest['source_ranges']:
  source.append(f'; Original bank{s["bank"]} ${s["start"]:04X}..${s["end_exclusive"]-1:04X}')
  m=B.image(s['bank']);d=Disassembler(m);pc=s['start']
  while pc<s['end_exclusive']:
   source.append(f'.export {syms[pc]}\n{syms[pc]}:')
   c=rows.get((s['bank'],pc))
   if c and pc+len(c)<=s['end_exclusive']:
    n,t=d.instruction_at(pc);mn,mode=m.disassemble[c[0]];v=int.from_bytes(bytes(c[1:]),'little');operand=''
    if pc==0xd8fd:
     source.append(' rts ; source tick tail JMP $D882 becomes one bounded update return')
     substitutions.append(dict(pc=pc,kind='bounded tick return',original=c));pc+=n;continue
    if pc in [0xd0be,0xd0c3]:
     operand='#$00'if pc==0xd0be else'#$05';mn='LDA'
     substitutions.append(dict(pc=pc,kind='original tile map base immediate',original=c))
    elif mode in ['inx','iny']:
     assert pc in [0xd100,0xd117]
     mn='JSR';operand='BbImportTile23'if pc==0xd100 else'BbImportTile84'
     substitutions.append(dict(pc=pc,kind='private query-cursor callback',original=c))
    elif mode=='rel':operand=code((pc+2+(v if v<128 else v-256))&65535);mn=BRANCHES[mn]
    elif mode in ['abs','abx','aby','zpg','zpx','zpy']:
     operand=code(v)if mn in['JSR','JMP']else data(v)
     operand+=dict(abs='',abx=',x',aby=',y',zpg='',zpx=',x',zpy=',y')[mode]
     if mode in ['zpg','zpx','zpy']:promoted+=1
    elif mode=='imm':operand=f'#${v:02x}'
    elif mode=='acc':operand='a'
    else:assert mode=='imp',mode
    source.append(f' {mn.lower()} {operand} ; source${pc:04X}: {t}');pc+=n
   else:source.append(f' .byte ${m.memory[pc]:02x}');pc+=1
  if s['name']=='source_clock':source.append('.export BbOriginal_CE4D\nBbOriginal_CE4D: rts ; original post-clock audio seam')
 # Source phase6 reads two bytes beyond the nominal six-pair table into the
 # following JSR opcode/operand. Preserve that real ROM data overlap instead
 # of accidentally returning the relocated instruction bytes.
 table=bytes(B.image(7).memory[0xdf81:0xdf8f])
 source.append('.export BbBubbleTileTable\nBbBubbleTileTable: .byte '+','.join(f'${v:02x}'for v in table))
 source.append('BbCodeEnd:')
 (O/'component.s').write_text('\n'.join(source)+'\n')
 cfg='MEMORY{V:start=$a000,size=$80,file=%O,fill=yes,fillval=$ff;I:start=$a080,size=$80,file=%O,fill=yes,fillval=$ff;K:start=$a100,size=$1f00,file=%O,fill=yes,fillval=$ff;}SEGMENTS{BB_VECTORS:load=V,type=ro;BB_IMPORTS:load=I,type=ro;BB_CODE:load=K,type=ro;}'
 (O/'component.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'component.bin','-Ln',O/'component.lbl']]:
  p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,'\n'.join(p.stderr.splitlines()[:10])
 blob=(O/'component.bin').read_bytes();lab=labels(O/'component.lbl');assert len(blob)==8192 and lab['BbCodeEnd']<=0xbfe0
 exports={k:lab[k]for k in API};ranges=[]
 for s in manifest['source_ranges']:
  ranges.append(dict(name=s['name'],original_bank=s['bank'],original_start=s['start'],relocated_start=lab[syms[s['start']]]))
 q=dict(passed=True,independent=True,host_ROM_written=False,host_resources_granted=False,native_service_rows=37,native_services_all_reject=True,code_CPU_half_open=[0xa000,0xc000],image_bytes=len(blob),used_through=lab['BbCodeEnd'],source_linked_bytes=lab['BbCodeEnd']-0xa100,used_bytes=lab['BbCodeEnd']-0xa000,FF_tail_bytes=0xbfe0-lab['BbCodeEnd'],header_reserved_half_open=[0xbfe0,0xc000],private_state_half_open=[STATE,STATE+1024],state_layout=dict(zero_page=[STATE,STATE+256],original_OAM=[STATE+256,STATE+512],original_globals=[STATE+512,STATE+768],adapter_reserved=[STATE+768,STATE+1024]),state_original_OAM_is_simulation=True,host_zero_page_used=False,promoted_zero_page_instructions=promoted,exports=exports,imports=[dict(z,vector=lab['BbImport'+z['name']])for z in importrows],substitutions=substitutions,original_code_data_overlap=dict(source_half_open=[0xdf81,0xdf8f],bytes=14,relocated_read_table=lab.get('BbBubbleTileTable'),original_instruction_bytes_preserved_as_data=True),ranges=ranges,sha256=B.sha(blob),scope='Independent8KB image only. Public native37rows fail closed. Original actor entries use source X/Y ABI and private operands. Imports must be bound and authenticated by future host adapters/loader; no raw owner or cartridge allocation is implied.')
 (O/'component-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','image_bytes','used_bytes','source_linked_bytes','FF_tail_bytes','promoted_zero_page_instructions','host_ROM_written']}))


if __name__=='__main__':main()
