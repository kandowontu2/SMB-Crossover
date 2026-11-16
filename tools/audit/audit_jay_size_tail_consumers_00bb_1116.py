"""Detached current CopyAlternate capacity/temporal-alias reader census."""
from pathlib import Path
import json,re
import audit_jay_private_label_consumers_00bb_1116 as Current

R,H,PIN=Current.Plan.R,Current.H,Current.Plan.PIN
DECODER_SHA='0168fa038f575833dabde4fa70b3ef84d80ed9709c6a8857d6480b2e25002745'
PRODUCER='tools/audit/check_jay_silius_shotgun_transport_1111.py'
PRODUCER_SHA='a115b62d583ce8eb64944e54fe1266bcdd4f1e1aa8a99b985ae7144ad6b0d8f1'
COPY_SOURCE='tools/reference/jay_silius_shotgun_transport_1111.s'
COPY_SOURCE_SHA='55c52e409edeaacba0a5e852316d4228226d91cf8093cb3c00128a1c59c95783'
PLAN='tools/audit/plan_jay_status_size_publication_00bb_1116.py'
PLAN_SHA='6ece60af99ca5d56cd31768c895067a88719fef2ad5d098c35154a86d0aa407d'


def run(raw):
    assert isinstance(raw,bytes)and H(raw)==PIN
    for path,pin in((Path(Current.__file__),DECODER_SHA),(R/PRODUCER,PRODUCER_SHA),(R/COPY_SOURCE,COPY_SOURCE_SHA)):
        assert H(path.read_bytes())==pin
    assert H((R/PLAN).read_bytes())==PLAN_SHA
    producer=(R/PRODUCER).read_text();source=(R/COPY_SOURCE).read_text()
    for line in("copy_pages = 11 if extra_segments else 8 if movement else 3","transfer_defs += 'CopyTailBytes=224\\n'",
                 "{'TRANSFER': (TRANSFER, 64)}","carrier = bytearray(b'\\xea' * 1024)",
                 "carrier[TRANSFER - 0xa400:TRANSFER - 0xa400 + len(copy)] = copy"):
        assert line in producer,line
    assert source.endswith('CopyFailed:\n clc\n rts\n')
    page=lambda p:raw[1048592+p*1024:1048592+(p+1)*1024]
    copy=page(222)[0x3c0:]
    expected=bytes.fromhex('a90085038505a9a48504a9b48506a000a20bb1039105d105d01ac8d0f5e604e606cad0eeb1039105d105d008c8c0e0d0f34c00d01860')
    assert len(expected)==54 and copy==expected+b'\xea'*10
    assert copy[0x31:0x36]==bytes.fromhex('4c00d01860') # success JMP and unchanged CopyFailed
    primary=Current.primary(raw);head,blocks,codec=Current.packet(raw)
    assert primary[0x7f6:0x7f8]==bytes.fromhex('c0d6')
    domains=[('warm primary',3,0xa000,primary),('services',3,0xafc0,page(218)),('support',3,0xb400,page(222)),
        ('motion',3,0xb800,page(232)),('extra',3,0xbc00,page(234)),('cold copier alias',3,0xa7c0,copy)]
    domains += [('scatter'+str(i),bank,pc-0x2000,data)for i,(bank,pc,data)in enumerate(blocks)]
    domains += [('Steve boot',3,0xa000,head[:64]),('Steve cold',1,0xb850,head[80:])]
    ranges=((0xb7f6,0xb800),(0xd7f6,0xd800),(0xa7f6,0xa800),(0xc7f6,0xc800))
    contains=lambda target:any(lo<=target<hi for lo,hi in ranges)
    words=[];controls=[];branches=[];fartriples=[];indexed=[]
    for name,bank,origin,data in domains:
        for i in range(len(data)-1):
            target=int.from_bytes(data[i:i+2],'little')
            if contains(target)or contains(target+1):words.append(dict(domain=name,bank=bank,PC=origin+i,target=target,around=data[max(0,i-3):i+5].hex()))
        for i in range(len(data)-2):
            if data[i]in(0x20,0x4c,0x6c):
                target=int.from_bytes(data[i+1:i+3],'little')
                if contains(target):controls.append(dict(domain=name,bank=bank,PC=origin+i,target=target,opcode=data[i]))
            if data[i]in(0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0):
                target=origin+i+2+int.from_bytes(data[i+1:i+2],'little',signed=True)
                if contains(target):branches.append(dict(domain=name,bank=bank,PC=origin+i,target=target,opcode=data[i],around=data[max(0,i-2):i+4].hex()))
            if bank==3 and data[i]in(0x19,0x1d,0x39,0x3d,0x59,0x5d,0x79,0x7d,0xb9,0xbc,0xbd,0xbe,0xd9,0xdd,0xf9,0xfd):
                operand=int.from_bytes(data[i+1:i+3],'little')
                if any(operand<hi and operand+255>=lo for lo,hi in ranges):
                    indexed.append(dict(domain=name,bank=bank,PC=origin+i,opcode=data[i],base=operand,around=data[max(0,i-2):i+5].hex()))
    for bank in range(128):
        data=raw[16+8192*bank:16+8192*(bank+1)]
        for i in range(len(data)-2):
            target=int.from_bytes(data[i:i+2],'little')
            if data[i+2]==3 and contains(target):fartriples.append(dict(PRG=bank,offset=i,target=target,around=data[max(0,i-3):i+6].hex()))
    direct=head[743:783]
    assert direct.hex()=='00c4030a0000000400c8030b0000000400cc030c0000000400d4020e0000000400d0030f4000bf03'
    assert head[783:815]==bytes((115,119,123,80,82,167,48,50,51,227,222,232,234,75,76,218,1,1,1,1,1,0,1,1,1,2,0,0,0,1,1,0))
    stream_path=R/'tools/reference/jay_silius_stream_decode_1110.s'
    assert H(stream_path.read_bytes())=='b269f8a94faa2a88b4a0dae756fece6603eb75c850820e500403ed3d6a68cf43'
    stream=stream_path.read_text()
    for token in(' lda #$a0\n sta Dst+1',' sta (Dst),y\n cmp (Dst),y','Complete:\n','Failed:\n clc\n'):
        assert token in stream,token
    assert head[925:941]==Current.Plan.COOKIE
    cold_path=R/'tools/reference/steve_armor_packet_1113.s'
    assert H(cold_path.read_bytes())=='d60167e124452c8cb5b54bdc2b775b77bc342efe09852d08c1331b835dc247b5'
    cold=cold_path.read_text()
    assert cold.index('    lda #$c0\n    sta $016c\n    lda #$a7\n')<cold.index('DecodePass:')<cold.index('ColdGood:')<cold.index('CommitRaw1:')
    cfg=R/'build/contra-force-world-roles-1031-v2/joint/candidate.cfg'
    assert H(cfg.read_bytes())=='06b92a8954d94957aa80bc830a2bfac5b84e1a25b642ce9958010f1df966888c'
    # Bind raw-LoHi03 coincidences to complete current immutable assets or
    # exact named data records, rather than trusting only a memory name.
    audio=[]
    for bank,path,pin in((46,'audio/expanded/playlist-07.bin','9143d2b47cd8a65b3d05e9afa25a6db00c6321581f214bd43bad2f44b12605b7'),
                          (107,'audio/full-roster/full-07.bin','f293790a3052708305cb4b54b48ff06cb092c7af3865a1a431e37c31e8609a87')):
        data=(R/path).read_bytes();assert len(data)==8192 and H(data)==pin and raw[16+8192*bank:16+8192*(bank+1)]==data
        audio.append(dict(bank=bank,asset=path,SHA256=pin,whole_current_bank_exact=True))
    roll=R/'src/roll_art.inc';assert H(roll.read_bytes())=='a41674dbe7da6f84dc9588a7275643b8839e1fe594deacc8571072a4ab06c37f'
    poses=[]
    for name,lo,n,word in(('RlP9O1D1',1702,57,1734),('RlP10O1D2',1967,53,2007)):
        lines=roll.read_text().split(name+':',1)[1].splitlines();data=[]
        for line in lines:
            if line and not line[0].isspace()and '.byte'in line and ':'in line:break
            if '.byte'in line:data.extend(int(v)for v in line.split('.byte',1)[1].split(','))
        data=bytes(data);assert len(data)==n and data[0]+1==n
        at=16+121*8192+lo;assert raw[at:at+n]==data
        poses.append(dict(name=name,bank=121,offset=lo,bytes=n,SHA256=H(data),word_offset=word,
            typed_role='quad sprite record: preceding dx byte plus next tile/attribute bytes, not a pointer'))
    clones=R/'build/thomas-natural-host-1031-v6/source/dmc-clones.s'
    assert H(clones.read_bytes())=='7837a7c2ee96a54996cf08e9ed984ebc355e9a7438bb1314f9f740a6b13a2556'
    donor=Path('C:/NES/Super Mario Bros. 2 (USA).nes').read_bytes()
    assert H(donor)=='41300bc4942a8a4f9b53148b404dd5cae3dd708ebdd9b617888d290a51a83e43'
    sample=donor[117840:117840+1153];at=16+120*8192+6528
    assert raw[at:at+1153]==sample and 6528<=7401<6528+1153
    # Freeze every overinclusive lead, including adjacent RTS-minus-one words.
    assert [(r['domain'],r['bank'],r['PC'],r['target'],r['opcode'])for r in controls]==[
        ('support',3,0xb67b,0xa7f6,0x4c)]
    assert branches==[]
    assert [(r['domain'],r['bank'],r['PC'],r['target'])for r in words]==[
        ('services',3,0xb292,0xb7fd),('support',3,0xb67c,0xa7f6),('extra',3,0xbea5,0xb7fd),
        ('scatter8',2,0xa602,0xc7f5),('scatter8',2,0xa614,0xc7f5),
        *[('scatter13',2,pc,target)for pc,target in((0xb27c,0xd7f5),(0xb281,0xd7f8),(0xb284,0xd7f9),
          (0xb287,0xd7fc),(0xb28c,0xd7fd),(0xb3df,0xd7f6),(0xb3e5,0xd7fa),(0xb3f1,0xd7f7),(0xb3f8,0xd7fb))]]
    assert [(r['PRG'],r['offset'],r['target'])for r in fartriples]==[
        (46,3887,0xa7fe),(107,7403,0xc7f9),(120,7401,0xa7ff),(121,1734,0xb7fd),(121,2007,0xa7ff)]
    assert [(r['domain'],r['PC'],r['opcode'],r['base'])for r in indexed]==[
        ('warm primary',0xa6bd,0x79,0xa77d),('extra',0xbca5,0xbc,0xd7ad),('extra',0xbd94,0xf9,0xd74c)]
    host=R/'tools/reference/jay_silius_host_tile_1110.s'
    assert H(host.read_bytes())=='1a927d85c8958f1765518bf68b6d9133b99ff739028b4bc8f219899aaa1da244'
    tile=host.read_text()
    assert ' lda ParserPhase\n cmp #8\n bcc CheckCursor\n'in tile
    assert 'CheckCursor:\n tay\n'in tile
    assert 'PhaseAdvance:\n .byte 0,1,1,1,0,1,1,1\n'in tile
    # Authenticate the actual compiled dominating branch, not only its source.
    phase_guard=bytes.fromhex('ad2207c90890084c86baa9014c54a7a8a205')
    assert primary.count(phase_guard)==1
    assert primary[0x6bd:0x6c0].hex()=='797da7'and primary[0x77d:0x785]==bytes((0,1,1,1,0,1,1,1))
    assert page(234)[0xa3:0xac].hex()=='4ca6bcadd7c0c922d0'
    assert page(234)[0x192:0x19c].hex()=='ca10f94cd7bd860db90b'
    assert page(218)[0x2cf:0x2d6].hex()=='b02c38fdb7bfb0'
    assert page(234)[0x2a2:0x2a9].hex()=='b02c38fdb7bfb0'
    indexed_roles=[dict(PC=0xa6bd,role='actual ADC PhaseAdvance,Y',
        dominating_guard_PC=0xa000+primary.index(phase_guard),guard_hex=phase_guard.hex(),Y_range=[0,7],
        read_interval=[0xa77d,0xa785],source_SHA256=H(host.read_bytes()),tail_not_read=True),
        dict(PC=0xbca5,role='high byte of JMP BCA6 at BCA3; not LDY abs,X',hex='4ca6bcadd7c0'),
        dict(PC=0xbd94,role='relative operand of BPL BD8E at BD93; not SBC abs,Y',hex='ca10f94cd7bd')]
    # No decoded scatter row overlaps the new warm B7F6 helper (D7F6 alias).
    assert all(not(bank==3 and pc<0xd800 and pc+len(data)>0xd7f6)for bank,pc,data in blocks)
    out=dict(passed=True,detached=True,parent_SHA256=PIN,frozen_fullsync_plan_SHA256=PLAN_SHA,no_CPU_or_proposed_overlay=True,outputs=0,
        source_capacity=dict(page=222,offset=0x3c0,runtime='raw3:B7C0..B7FF',cold_alias='raw3:A7C0..A7FF',declared=64,code=54,tail=10,
            complete64_SHA256=H(copy),preserved_CopyFailed='B7F4 CLC / B7F5 RTS',source_producer_SHA256=PRODUCER_SHA,source_SHA256=COPY_SOURCE_SHA),
        unchanged_primary_SHA256=H(primary),warm_A7F6_first16=primary[0x7f6:0x806].hex(),codec=codec,
        domains=[dict(name=n,bank=b,PC=p,bytes=len(d),SHA256=H(d))for n,b,p,d in domains],
        control_operands=controls,relative_branches=branches,words_including_RTS_minus1=words,PRG_Raw3_triplet_leads=fartriples,indexed_read_leads=indexed,
        classified_indexed_reads=indexed_roles,
        classified_words=dict(warm_primary='B67B JMP A7F6 uses unchanged decoded primary ProgressMux. It is not B7F6.',
            service_and_extra='SEC; SBC BFB7,X: B7FD is an instruction-crossing coincidence, not an operand.',
            scatter8='Raw2 SBC C7F5,Y reads companion state in raw2; does not name a raw3 cold alias.',
            scatter13='Raw2 D7F5..D7FD are explicit companion data stores; actual bank2 row descriptors preserve that type.'),
        triplet_source_roles=dict(cfg_SHA256=H(cfg.read_bytes()),complete_audio_assets=audio,Roll_pose_records=poses,
            DMC=dict(bank=120,request=16,offset=6528,bytes=1153,sample_SHA256=H(sample),donor_SHA256=H(donor),
                source=clones.relative_to(R).as_posix(),source_SHA256=H(clones.read_bytes()),exact_current_sample=True)),
        cold_readers=dict(actual_DirectRows_hex=direct.hex(),source_tables_SHA256=H(head[783:815]),
            full_primary_decoder_source_SHA256=H(stream_path.read_bytes()),Steve_cold_source_SHA256=H(cold_path.read_bytes()),
            unchanged_primary_stage257_SHA256=H((page(331)+page(332))[:257]),
            copy_extent='A400..AFDF -> B400..BFDF: 11 full pages plus224; byte-for-byte compare',
            phase='Tail coldalias is copied asdata. Success JMP D000 decodes verified unchanged primary A000..A8BF before cookiecommit. Failure returnsCLC atA7F4/5; invalidheaders prevent liveadmission.',
            expected_Steve_cookie_file=1429421,steve_header_source=head[925:941].hex()),
        new_entry_contract='Only the separately proposed Main B82C JSR may enter warm raw3 B7F6. No existing external/interior entry is being rebound.',
        prelease_remaining='New source grant, strict composition, actual cold/header commit, AXYP/live-stack, size/status store-order IRQ, lifecycle/head consumer and natural Flower qualification remain required.',
        source_SHA256=H(Path(__file__).read_bytes()))
    out['receipt_SHA256']=H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':print('RESULT '+json.dumps(run(Current.Plan.ROM.read_bytes()),separators=(',',':')),flush=True)
