"""Current pose-data operand census; unresolved roots remain explicit."""
from hashlib import sha256
from pathlib import Path
import json,re
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
from py65.assembler import Assembler
from types import SimpleNamespace
import current_prince_body_research_571_1114 as Current
import prince_cold_packet_1111 as Packet
import audit_prince_sprite_window_options_1114 as Census
import prince_sword_box_1112 as Boxes


def run(raw):
    reference=Current.normalize(raw,kind='score-571').referenceF11
    chunks=Packet.extract(reference)[1];origins=(0xa000,0xc800,0xc0b0)
    mem=bytearray(65536)
    for origin,data in zip(origins,chunks):mem[origin:origin+len(data)]=data
    cpu=MPU(memory=mem);d=Disassembler(cpu);root=Packet.R/'build/prince-actor-1101-v1'
    source_labels=root/'contact-core.lbl';native_labels=root/'native-labels-v153.json'
    known={int(pc,16):name for pc,name in re.findall(r'^al ([0-9A-Fa-f]+) \.?(PpN_\S+)$',source_labels.read_text(),re.M)}
    known.update({pc:name for name,pc in json.loads(native_labels.read_text()).items()if name.startswith('PpBattle_')})
    # Reconstruct the one remaining local sweep procedure from its retained
    # assembly, rather than inferring an entry from nearby opcode-like data.
    source=Packet.R/'tools/audit/check_prince_wall_sweep_1110_v6.py'
    space=dict(re=re,Assembler=Assembler,N=Census.Old.N,I=SimpleNamespace(address=Census.Old.W.address),
        R=Packet.R,ORIGIN=0xd56a)
    assemble=Census.Old.pure_function(source,'assemble',space);space['assemble']=assemble
    build=Census.Old.pure_function(source,'code',space)
    blocks,positions,_,_=build(dict(Census.Old.W.Symbols.bundle(),raw=reference))
    wall_rebuilt=[]
    for name in('BOUNDS','ENTRY','CORE'):
        lo=positions[name];blob=blocks[name]
        assert bytes(mem[lo:lo+len(blob)])==blob,(name,'Current sweep source changed')
        wall_rebuilt.append([lo,lo+len(blob),sha256(blob).hexdigest()])
    audio_source=root/'native-audio-v157.s';audio_text=audio_source.read_text()
    audio_symbols={name:int(value,16)for name,value in re.findall(r'(?m)^([A-Za-z_][A-Za-z_0-9]*)=\$([0-9a-fA-F]+)$',audio_text)}
    audio_part=audio_text.split('PpNativeColdPrefix:',1)[1].split('; Native X=0',1)[0]
    audio_part=re.sub(r'(?m)^([A-Za-z_][A-Za-z_0-9]*):(?=\S)',r'\1:\n',audio_part)
    audio_blob,_=assemble('PpNativeColdPrefix:'+audio_part,0xc766,audio_symbols)
    staged_audio=chunks[2][0xc65f-0xc100:0xc65f-0xc100+len(audio_blob)]
    assert staged_audio==audio_blob,'Current relocated cold/audio prefix changed'
    audio_mem=bytearray(mem);audio_mem[0xc766:0xc766+len(audio_blob)]=audio_blob
    ad=Disassembler(MPU(memory=audio_mem));audio_starts={};at=0xc766
    while at<0xc766+len(audio_blob):
        size,instruction=ad.instruction_at(at);audio_starts[at]=instruction;at+=size
    starts=dict(known)
    regions=((0xbbc1,0xbcf9),(0xbde2,0xbfa3),(0xbfa3,0xbfdf),
        (0xc0b0,0xc0f8),(0xc100,0xc200),(0xc235,0xc352),(0xc362,0xc3ff),(0xc40b,0xc491),(0xc4ff,0xc606),
        (0xd46e,0xd4a6),(0xd4a7,0xd527),(0xd552,0xd621),(0xd74e,0xd7b0),(0xd800,0xd8b2),(0xd8f1,0xd95f))
    for lo,hi in regions:
        at=lo
        while at<hi:
            size,_=d.instruction_at(at);starts.setdefault(at,'Declared bounded code extent');at+=size
    procedures=('PpNativeCall','PpNativeInit','PpNativeRetire','PpNativeTick','PpNativeMotionExport',
        'PpNativeQuietMusic','PpNativeQuietSfx','PpCombatControls','PpOriginalIncoming','PpOriginalStrike',
        'PpNativeProxyIn','PpNativeProxyOut','PpNativeFresh','PpNativeResetTail','PpNativeRoute',
        'PpNativeColors','PpNativeContact','PpNativeHealthStatus','PpNativeColdPrefix',
        'PpNativeDeathUpdate','PpNativeDeferredKill','PpNativeFullBox','PpNativePickup',
        'PpNativeVerticalExport','PpLiveDispatch','PpStageLive','PpInstallLive','PpStageInstaller')
    named=json.loads(native_labels.read_text())
    farcall_roots=[]
    for stream,(origin,data)in enumerate(zip(origins,chunks)):
        for i in range(len(data)-15):
            if data[i]!=0xa9 or data[i+2:i+6]!=bytes.fromhex('8d6c01a9')or data[i+7:i+11]!=bytes.fromhex('8d6d01a9')or data[i+12:i+15]!=bytes.fromhex('205a01'):continue
            target=data[i+1]+256*data[i+6];bank=data[i+11]
            if bank in(2,3):farcall_roots.append(dict(stream=stream,PC=origin+i,bank=bank,target=target,hex=data[i:i+15].hex()))
    renderer_procedures=('PpHostDraw','PpHostProject','PpReadProjection','PpGridLookup','PpGridProjection','PpGridY','PpGridX')
    pending=list(known)+[named[name]for name in procedures+renderer_procedures]+[0xb310,0xb37c,0xbfa3,audio_symbols['PpColdContinue'],positions['ENTRY']]+[row['target']for row in farcall_roots]
    visited=set()
    def code(at):
        return(0xa000<=at<0xb400 or 0xbbc1<=at<0xbfdf or 0xc0b0<=at<0xc606 or 0xd46e<=at<0xdfe0)
    while pending:
        at=pending.pop()
        if at in visited or not code(at):continue
        visited.add(at);size,instruction=d.instruction_at(at)
        opcode=mem[at];mnemonic,mode=cpu.disassemble[opcode]
        if mnemonic=='???'or mnemonic=='BRK':continue
        starts.setdefault(at,'Reachable from retained original/public procedure root')
        if mnemonic in('RTS','RTI'):continue
        if mnemonic in('JSR','JMP')and mode=='abs':
            target=int.from_bytes(mem[at+1:at+3],'little');pending.append(target)
            if mnemonic=='JMP':continue
        elif mnemonic=='JMP':continue
        if opcode&31==16:
            delta=mem[at+1];pending.append(at+2+delta-(256 if delta&128 else 0))
        pending.append(at+size)
    staged=bytearray(mem);staged[0xc100:0xc100+len(chunks[2])]=chunks[2]
    sd=Disassembler(MPU(memory=staged));staged_starts={};pending=[0xc65f]
    while pending:
        at=pending.pop()
        if at in staged_starts or not 0xc65f<=at<0xc100+len(chunks[2]):continue
        size,instruction=sd.instruction_at(at);staged_starts[at]=instruction
        mnemonic,mode=cpu.disassemble[staged[at]]
        if mnemonic in('BRK','RTS','RTI','???'):continue
        if mnemonic in('JSR','JMP'):
            if mode=='abs':pending.append(int.from_bytes(staged[at+1:at+3],'little'))
            if mnemonic=='JMP':continue
        if staged[at]&31==16:
            delta=staged[at+1];pending.append(at+2+delta-(256 if delta&128 else 0))
        pending.append(at+size)
    rows=[];direct=[];unresolved=[]
    for stream,(origin,data)in enumerate(zip(origins,chunks)):
        for i in range(1,len(data)-1):
            pc=origin+i-1;target=int.from_bytes(data[i:i+2],'little')
            if not 0xc800<=target<0xd466:continue
            if stream==1 and i<3174:continue
            mnemonic,mode=cpu.disassemble[data[i-1]]
            if mode not in('abs','abx','aby','ind'):continue
            row=dict(stream=stream,PC=pc,target=target,hex=data[i-1:i+2].hex(),mnemonic=mnemonic,mode=mode)
            if stream==0 and 0xb400<=pc<0xbbc1:
                row['classification']='Immutable original script/action table bytes; finite existing data readers'
            elif stream==2 and pc>=0xc606:
                stage_pc=pc+80
                covers=[dict(PC=a,instruction=sd.instruction_at(a)[1])for a in range(stage_pc-2,stage_pc)if a in staged_starts and stage_pc<a+sd.instruction_at(a)[0]]
                if covers:
                    row.update(classification='Live original actor data; staged cold word crosses a real instruction',staged_PC=stage_pc,staged_covering=covers)
                else:
                    live_audio=stage_pc-0xc65f+0xc766
                    covers=[dict(PC=a,instruction=ad.instruction_at(a)[1])for a in range(live_audio-2,live_audio)if a in audio_starts and live_audio<a+ad.instruction_at(a)[0]]
                    assert covers,('Unclosed staged/audio operand',row,hex(stage_pc),hex(live_audio))
                    row.update(classification='Inactive actor-data view; relocated audio operand alias',staged_PC=stage_pc,live_audio_PC=live_audio,audio_covering=covers)
            elif pc in starts:
                row['classification']='Instruction boundary candidate';row['source_label']=starts[pc];direct.append(row)
            else:
                covers=[]
                for before in range(pc-2,pc):
                    if before in starts:
                        size,instruction=d.instruction_at(before)
                        if before<pc<before+size:covers.append(dict(PC=before,instruction=instruction,source_label=starts[before],in_current_CFG=before in visited))
                if covers:row.update(classification='Cross-instruction operand alias',covering=covers)
                else:
                    row['classification']='Unresolved opcode-like word'
                    row['context_hex']=bytes(mem[pc-10:pc+14]).hex()
                    row['nearby_starts']=[[a,d.instruction_at(a)[1],starts[a]]for a in range(pc-12,pc+12)if a in starts]
                    unresolved.append(row)
            rows.append(row)
    graphs={};graph_files=[root/name for name in('contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json')]
    for path in graph_files:graphs.update(json.loads(path.read_text())['instructions'])
    index_crossings=[];indirect=[]
    for pc,row in graphs.items():
        mode,value=row['mode'],row['value']
        if row['mn']in('JSR','JMP')and mode!='ind':continue
        if mode in('abs','zpg','abx','aby','zpx','zpy')and 0<=value<2048:
            end=value+(256 if mode in('abx','aby','zpx','zpy')else 1)
            if end>2048:index_crossings.append(dict(original_PC=pc,**row,exclusive_end=end))
        if mode in('iny','inx','ind'):indirect.append(dict(original_PC=pc,**row))
    assert all((row['mn'],row['mode'],row['value'])in(('LDA','iny',0x21),('JMP','ind',0x23))for row in indirect)
    sequence=bytes.fromhex('08ad21c038e9ae8df1b2ad22c0e9961869b48df2b228b9ffff60')
    assert bytes(mem[0xb2da:0xb2da+len(sequence)])==sequence
    actions=[int.from_bytes(mem[a:a+2],'little')for a in range(0xbae5,0xbba1,2)]
    commands=[int.from_bytes(mem[a:a+2],'little')for a in range(0xbba1,0xbbc1,2)]
    assert len(actions)==94 and actions[0]==0 and all(0x96ae<=a<0x96ae+1765 for a in actions[1:])
    assert len(commands)==16 and commands[0]==0 and all(a in known and not 0xc800<=a<0xd466 for a in commands[1:])
    ledger_file=root/'collision-lifetime-proposal-v62.json'
    ledger=json.loads(ledger_file.read_text())
    unreachable=ledger['original_reader_closure']['source_unreachable_ledger']
    assert ledger['passed']and set(row['original_PC']for row in index_crossings)==set(unreachable)=={'4:B8DB','7:E991','7:E996'}
    proxy_start,proxy_end=named['PpNativeProxyIn'],named['PpNativeProxyOut']
    retained_metadata=root/'native-metadata-v149.bin';oldmeta=retained_metadata.read_bytes()
    current_proxy=bytes(mem[proxy_start:proxy_end]);original_proxy=oldmeta[proxy_start-0xc800:proxy_end-0xc800]
    guard_diffs=[(proxy_start+i,a,b)for i,(a,b)in enumerate(zip(current_proxy,original_proxy))if a!=b]
    assert [pc for pc,a,b in guard_diffs]==list(range(0xddeb,0xddee))
    assert bytes(mem[Boxes.HELPER:Boxes.POSE_END])==Boxes.HEAD
    assert bytes(mem[Boxes.TAIL:0xd756])==Boxes.END
    site=0xddeb-proxy_start;normalized_proxy=current_proxy[:site]+bytes.fromhex('bd4606')+current_proxy[site+3:]
    assert normalized_proxy==original_proxy
    assert mem[0xddeb:0xddee]==bytes.fromhex('2066d4')
    assert bytes(mem[proxy_start:proxy_end]).count(bytes.fromhex('a9018dd0c6'))==1
    assert not unresolved and {(r['PC'],r['target'])for r in direct}=={(0xd906,0xc800),(0xd90c,0xc801)}
    assert all(any(c['in_current_CFG']for c in row['covering'])for row in rows if'covering'in row)
    cache_readers=[]
    for pc in visited:
        mnemonic,mode=cpu.disassemble[mem[pc]]
        if mode in('abs','abx','aby','ind')and int.from_bytes(mem[pc+1:pc+3],'little')==0xd7b1:
            cache_readers.append([pc,mnemonic,mode])
    assert sorted(cache_readers)==[[0xd77b,'STA','abs'],[0xd7a1,'LDA','abs']]
    q=dict(current_SHA256=sha256(raw).hexdigest(),reference_F11_SHA256=sha256(reference).hexdigest(),
        known_source_instruction_labels=len(known),declared_regions=[list(r)for r in regions],
        current_direct_CFG_instruction_starts=len(visited),published_procedure_roots=list(procedures),
        published_renderer_roots={name:named[name]for name in renderer_procedures},
        current_private_farcall_publications=farcall_roots,
        independently_reassembled_current_sweep_extents=wall_rebuilt,
        staged_cold_instruction_starts=[[a,v]for a,v in sorted(staged_starts.items())],
        independently_reassembled_relocated_cold_audio_prefix=dict(live=0xc766,staged=0xc65f,bytes=len(audio_blob),SHA256=sha256(audio_blob).hexdigest()),
        original_instruction_graph_entries=len(graphs),original_indexed_domains_crossing_C800=index_crossings,
        original_indirect_operations=indirect,exact_current_sequence_reader_SHA256=sha256(sequence).hexdigest(),
        original_script_native_half_open=[0xb400,0xbae5],all94_action_script_pointers_in1765byte_source=True,
        all15_command_targets_in_known_current_code=commands[1:],
        inherited_unreachable_guard_ledger=unreachable,
        exact_current_guard_importer_SHA256=sha256(bytes(mem[proxy_start:proxy_end])).hexdigest(),
        only_guard_importer_change=dict(PC=0xddeb,old='bd4606',new='2066d4',
            helper_preserved_half_open=[Boxes.HELPER,Boxes.POSE_END],helper_role='Existing box3/9 admission only; X/Y and HP1 import unchanged'),
        inherited_lemma='Native imported GuardHP1 dies before ledger; player Y0 bypasses it. Current importer and all original script/command readers are preserved.',
        possible_opcode_words=rows,direct_instruction_candidates=direct,unresolved=unresolved,
        static_consumer_closure_complete=True,renderer_TileOut_only_current_code_consumers=cache_readers,
        limits='Decoded Prince data/reader closure with exact retained original indexed/indirect invariants. Cold ROM transport, native shared-caller mapping and complete lifecycle qualification are separate.',
        source_files={p.name:sha256(p.read_bytes()).hexdigest()for p in(source_labels,native_labels,audio_source,ledger_file,retained_metadata,*graph_files)},
        ROM_changes=0,outputs=0,Mesen=False)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return q


if __name__=='__main__':
    q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
