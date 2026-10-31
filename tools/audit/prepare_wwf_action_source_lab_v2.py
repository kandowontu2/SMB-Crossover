"""Assemble genuine WWF interpreter/handlers; no host allocations or ROM edits."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_action_vm_recovery_1031_v1 as W
from private_build_outputs_v1 import validate
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
O=R/'build/wwf-action-source-lab-v2'
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n')
BLOCKS=[('WF_ADOPT',0xaed4,0xaf4d),('WF_SELECT',0xaf4d,0xb14d),('WF_INIT',0xd1a5,0xd284),('WF_ENTRY',0xe2e8,0xe40e),('WF_HANDLERS',0xe79e,0xefd0)]
CALLBACKS={0xb6bb:'WfCbAI',0xc6b7:'WfCbRingClamp',0xcd02:'WfCbActorDepthProbe',0xd0c0:'WfCbRingBounds',0xcd25:'WfCbActorContact',0xce17:'WfCbRandom',0xa22e:'WfCbAudio09',0xa23c:'WfCbAudio0F',0xa243:'WfCbAudio12'}
EXPORTS={'WfAdoptRequests':0xaed4,'WfSelectAction':0xaf4d,'WfInitDescriptors':0xd1a5,'WfVmTick':0xe2e8,'WfVmDispatch':0xe385,'WfReadOperand':0xefc8}

def main():
 assert not O.exists();O.mkdir();logs=[]
 try:
  raw=W.W.raw();assert W.W.sha(W.W.ROM)==W.W.SHA;mem=bytearray(65536);mem[0x8000:]=raw[:32768];mpu=MPU(memory=mem);d=Disassembler(mpu);chars=W.W.tables(raw)
  instructions={};static_ram=set()
  for seg,lo,hi in BLOCKS:
   pc=lo
   while pc<hi:
    n,text=d.instruction_at(pc);mn,mode=mpu.disassemble[mem[pc]];assert mn!='???',(hex(pc),text);instructions[pc]=(n,mn,mode,text);pc+=n
   assert pc==hi,(seg,hex(pc),hex(hi))
  aliases={pc:[]for pc in instructions}
  for name,pc in EXPORTS.items():aliases[pc].append(name)
  handlers=[mem[0xe6ea+i*2]+256*mem[0xe6eb+i*2]for i in range(90)]
  assert all(t in instructions for t in handlers)
  for op,pc in enumerate(handlers,8):aliases[pc].append(f'WfOpcode{op:02X}')
  def ref(a,control=False):
   if a in instructions:return f'WfN_{a:04X}'
   if a in[0xbb28,0xbb29]:return 'WfDescriptorPointers'+(''if a==0xbb28 else'+1')
   if a in[0xe6ea,0xe6eb]:return 'WfOpcodeTable'+(''if a==0xe6ea else'+1')
   if control:
    assert a in CALLBACKS,('unclassified native callback',hex(a));return CALLBACKS[a]
   return f'${a:04x}'
  lines=['; Genuine USA WWF source instructions, mechanically decoded and labelled.\n; Native callback imports are explicit environment boundaries, not host grants.\n.setcpu "6502"\n']
  lines += ['.import '+','.join(CALLBACKS.values())+'\n','.import WfDescriptorPointers\n','.export '+','.join(EXPORTS)+'\n','.export WfOpcodeTable\n']
  for seg,lo,hi in BLOCKS:
   lines.append(f'\n.segment "{seg}"\n')
   for pc in sorted(a for a in instructions if lo<=a<hi):
    n,mn,mode,text=instructions[pc];data=bytes(mem[pc:pc+n]);v=data[1]if n>=2 else None;a=int.from_bytes(data[1:],'little')if n==3 else v
    for name in aliases[pc]:lines.append(f'{name}:\n')
    lines.append(f'WfN_{pc:04X}: ; native {pc:04X} {data.hex()}\n')
    if mode=='rel':operand=ref((pc+2+(v if v<128 else v-256))&65535,True)
    elif mode=='imm':operand=f'#${v:02x}'
    elif mode=='acc':operand='a'
    elif mode=='imp':operand=''
    elif mode in['zpg','zpx','zpy']:
     static_ram.add(v);operand=f'${v:02x}'+dict(zpg='',zpx=',x',zpy=',y')[mode]
    elif mode in['inx','iny']:static_ram.add(v);operand=f'(${v:02x},x)'if mode=='inx'else f'(${v:02x}),y'
    elif mode=='ind':static_ram.add(a);operand=f'(${a:04x})'
    elif mode in['abs','abx','aby']:
     if a<0x2000:static_ram.add(a)
     operand=ref(a,mn in['JSR','JMP'])+dict(abs='',abx=',x',aby=',y')[mode]
     if a<=255:operand='a:'+operand
    else:raise AssertionError(('unknown mode',mode,hex(pc)))
    lines.append(' '+mn.lower()+(' '+operand if operand else'')+'\n')
  lines.append('\n.segment "WF_TABLE"\nWfOpcodeTable:\n')
  lines += [f' .word WfOpcode{op:02X} ; native opcode${op:02x}\n'for op in range(8,0x62)]
  (O/'vm.s').write_text(''.join(lines))
  # Data is source-backed and remains at native addresses in this first lab.
  # Only executable code relocates; a host data/state layout is not implied.
  desc=bytes(mem[c['descriptor']+j]for c in chars for j in range(81));assert len(desc)==486
  assert all(mem[c['descriptor']:c['descriptor']+80]==desc[i*81:i*81+80]for i,c in enumerate(chars))
  assert sorted(c['descriptor']for c in chars)==list(range(0xbb34,0xbcc9+1,81))
  (O/'descriptors.bin').write_bytes(desc);scripts=mem[0xf01e:0xfe50];(O/'scripts.bin').write_bytes(scripts)
  s='.export WfDescriptorPointers\n.segment "WF_DESC_PTR"\nWfDescriptorPointers:\n'+''.join(f' .word WfDescriptor{i}\n'for i in range(6))+'\n'
  s+=''.join(f'.segment "WF_DESC{i}"\nWfDescriptor{i}:\n .incbin "{(O/"descriptors.bin").as_posix()}",{i*81},81\n'for i in range(6))
  s+=f'\n.segment "WF_SCRIPTS"\n.incbin "{(O/"scripts.bin").as_posix()}"\n';(O/'data.s').write_text(s)
  def run(n,cmd):
   guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);q=dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr);logs.append(q);save(O/(n+'.json'),q);assert z.returncode==0,(n,z.stderr)
  ca=str(R/'tools/Windows/cc65/bin/ca65.exe');ld=str(R/'tools/Windows/cc65/bin/ld65.exe')
  for n in['vm','data']:run(n+'-build',[ca,'-g','-l',str(O/(n+'.lst')),'--create-full-dep',str(O/(n+'.dep')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))])
  variants={}
  for variant in['native','relocated']:
   callback_values={name:(pc if variant=='native'else 0x7000+i*4)for i,(pc,name)in enumerate(CALLBACKS.items())}
   (O/(variant+'-callbacks.s')).write_text(''.join(f'.export {n} := ${pc:04x}\n'for n,pc in callback_values.items()))
   run(variant+'-callbacks-build',[ca,'-g','--create-full-dep',str(O/(variant+'-callbacks.dep')),'-o',str(O/(variant+'-callbacks.o')),str(O/(variant+'-callbacks.s'))])
   starts={seg:lo for seg,lo,hi in BLOCKS};starts.update(WF_TABLE=0xe6ea,WF_DESC_PTR=0xbb28,WF_SCRIPTS=0xf01e);starts.update({f'WF_DESC{i}':c['descriptor']for i,c in enumerate(chars)})
   if variant=='relocated':
    cursor=0x9000
    for seg,lo,hi in BLOCKS:starts[seg]=cursor;cursor+=hi-lo
    starts['WF_TABLE']=cursor
   cfg='MEMORY { LAB: start=$8000,size=$8000,type=ro,file="'+(O/(variant+'.bin')).as_posix()+'",fill=yes,fillval=$ff; }\nSEGMENTS {\n'
   cfg+=''.join(f' {seg}: load=LAB,type=ro,start=${pc:04x};\n'for seg,pc in sorted(starts.items(),key=lambda q:q[1]))+'}\n';(O/(variant+'.cfg')).write_text(cfg)
   run(variant+'-link',[ld,'-C',str(O/(variant+'.cfg')),'-o',str(O/(variant+'.link.bin')),'-Ln',str(O/(variant+'.lbl')),'-m',str(O/(variant+'.map')),'--dbgfile',str(O/(variant+'.dbg')),str(O/'vm.o'),str(O/'data.o'),str(O/(variant+'-callbacks.o'))])
   b=(O/(variant+'.bin')).read_bytes();assert len(b)==32768
   syms={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(O/(variant+'.lbl')).read_text())}
   spans=[dict(segment=seg,start=starts[seg],original_start=lo,size=hi-lo)for seg,lo,hi in BLOCKS]
   spans += [dict(segment='WF_TABLE',start=starts['WF_TABLE'],original_start=0xe6ea,size=180),dict(segment='WF_DESC_PTR',start=0xbb28,original_start=0xbb28,size=12),dict(segment='WF_SCRIPTS',start=0xf01e,original_start=0xf01e,size=3634)]
   spans += [dict(segment=f'WF_DESC{i}',start=c['descriptor'],original_start=c['descriptor'],size=81)for i,c in enumerate(chars)]
   if variant=='native':
    for q in spans:assert b[q['start']-0x8000:q['start']-0x8000+q['size']]==mem[q['original_start']:q['original_start']+q['size']],q
   variants[variant]=dict(binary=str(O/(variant+'.bin')),labels=syms,spans=spans,callbacks=callback_values)
  manifest=dict(source=True,source_lab=True,no_host_allocation=True,native_host=False,installed=False,original_ROM=W.W.SHA,code_bytes=sum(hi-lo for _,lo,hi in BLOCKS),dispatch_table_bytes=180,descriptor_bytes=486,descriptor_pointer_bytes=12,script_bundle_bytes=3634,actual_source_total_bytes=sum(hi-lo for _,lo,hi in BLOCKS)+180+486+12+3634,opcode_handlers=90,static_RAM_base_operands=sorted(static_ram),actor_identity='actor0 uses2B,actor1 uses2A',cadence='71&1 selects actor;8D is video-frame counter; one tick per actor every2 frames',variants=variants,
   callback_original_entries={name:pc for pc,name in CALLBACKS.items()},limits=['Native data origins retained in isolated lab; no dense host data/state relocation or allocation claim','Relocated-code callbacks require explicit oracle adapter, not the original overlaid code view','No host terrain/audio/raster/menu/native launch or admission'],bindings={str(p.resolve()):SHA(p)for p in[R/'tools/audit/prepare_wwf_action_source_lab_v1.py',R/'build/wwf-action-source-lab-v1/negative.json',Path(__file__),Path(W.__file__),Path(W.W.__file__),W.W.ROM,*[p for p in O.iterdir()if p.is_file()]]})
  save(O/'build-proof.json',manifest);print(json.dumps({k:v for k,v in manifest.items()if k not in['variants','bindings','static_RAM_base_operands']}))
 except Exception as e:save(O/'negative.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
