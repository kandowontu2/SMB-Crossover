"""Strictly rebase frame-token audio onto the delivered Mini body/platform build."""

import argparse
import json
from pathlib import Path
import re
import shutil

import check_native_audio_frame_token_1110_v1 as T
from compose_mini_frame_budget_1108 import check_full_cpu, digest, load
from prepare_mini_lane_audio_native_1110 import (
    BUILD, KERNEL, bound_rom, verify_interrupts, verify_parent, verify_payload,
)
from prepare_selected_native_packet_v1 import prepare, sha

R,F,M,N = T.R,T.F,T.M,T.N
CURRENT = BUILD/'mini-body-platform-native-1110/candidate.nes'
PIN = '14a4e10058c683605344564d118202970da6ccae4482bf1dfca76b9ad743aacc'
EXPECTED = '705906f45d3e09d5ebed30f2a9ac15295283a0ca41eb00879ce08fb2f020c7fe'
CONTROLLER = CURRENT.parent/'route/controller.lua'
READY = CONTROLLER.with_name('ready.json')
FORMAT,RUNTIME,VECTORS,LIFECYCLE = [T.OUT/name for name in
    ('format-proof.json','runtime-proof.json','vectors.json','lifecycle.json')]
PROOFS = (FORMAT,RUNTIME,VECTORS,LIFECYCLE)
OBSERVER = R/'tools/reference/observe_native_audio_frame_token_1110_v1.lua'


def validate_bound(path):
    proof = load(path)
    assert proof['passed'] is True and proof['parent_SHA256']==F.PIN,path
    for file,pin in proof['bindings'].items():
        assert sha(R/file)==pin,(path,file)
    return proof


def build_image():
    declared = bound_rom(F.BASE,F.PIN)
    raw = bound_rom(CURRENT,PIN)
    fmt,rt,_,life = [validate_bound(path) for path in PROOFS]
    _,proof,spans = verify_parent(declared,RUNTIME)
    verify_interrupts(RUNTIME,VECTORS,proof)
    assert fmt['bindings'] and rt['bindings'][FORMAT.relative_to(R).as_posix()]==sha(FORMAT)
    assert life['round_trips']==41 and life['expected_memory_only_SHA256']==proof['expected_memory_only_SHA256']
    assert all(life['bindings'][p.relative_to(R).as_posix()]==sha(p) for p in (RUNTIME,VECTORS))
    assert len(spans)==7 and [q['physical_PRG'] for q in proof['patches']]==[38]*6+[57]
    for row in proof['patches']:
        start,end = row['CPU_half_open']
        assert row['file_offset']==F.offset(row['physical_PRG'],start)
        assert start<end and end-start==len(bytes.fromhex(row['old_hex']))
    candidate = bytearray(raw)
    for start,end,old,new in spans:
        assert candidate[start:end]==old,(start,end,'delivered ROM preimage')
        candidate[start:end] = new
    assert digest(candidate)==EXPECTED
    assert candidate[:16]==raw[:16] and candidate[1048592:]==raw[1048592:]
    verify_payload(raw,KERNEL)
    verify_payload(candidate,KERNEL)
    return raw,bytes(candidate),proof


def audio_config(candidate,proof):
    start = F.offset(57,0xb74c)
    payload = candidate[start:start+1104]
    right_offsets,left,right = payload[735:884],payload[884:972],payload[972:]
    assert len(right_offsets)==149 and len(left)==88 and len(right)==132
    b = M.bundle(candidate)
    entry = proof['labels']['GroundLoopFrame']
    at = F.offset(38,entry)
    assert candidate[at:at+6]==bytes.fromhex('2003cbc9ffd0')
    records = []
    for i,offset in enumerate(right_offsets):
        group = next(j for j in range(0,len(left),4) if i<left[j])
        assert offset%3==0 and offset+3<=len(right)
        values = left[group+1:group+4]+right[offset:offset+3]
        fields = [k for reg,value in zip((0,2,3,4,6,7),values,strict=True)
                  if value!=255 for k in (reg,value)]
        records.append('{'+','.join(map(str,fields))+'}')
    config = dict(token_pc=entry+3,physical=at-16+3,
                  image=M.address(b,'XgMusicApu'),family=M.address(b,'XgAudioCharacter'))
    scalars = ','.join(f'{k}={v}' for k,v in config.items())
    return 'local audioConfig={'+scalars+',tokens={'+','.join(records)+'}}\n'


def controller_for(raw,candidate,proof):
    ready = load(READY)
    assert ready['prepared'] and not ready['emulated_writes'] and ready['ROM_sha256']==digest(raw)==PIN
    assert Path(ready['ROM']).resolve()==CURRENT.resolve()
    bindings = {Path(p).resolve():h for p,h in ready['bindings'].items()}
    for p in (CONTROLLER,CURRENT,CURRENT.with_suffix('.json'),CURRENT.with_suffix('.dbg'),
              CURRENT.with_suffix('.lbl'),KERNEL,KERNEL.with_suffix('.lbl')):
        assert bindings[p.resolve()]==sha(p),p
    text = CONTROLLER.read_text(encoding='utf-8')
    assert text.count(PIN)==text.count(sha(KERNEL))==1
    hooks = re.findall(r'\["physical"\]=(\d+),\["memory"\]="nesPrgRom",'
                       r'\["bytes"\]=\{([\d,]+)\}',text)
    assert hooks
    for address,data in hooks:
        at,expected = 16+int(address),bytes(map(int,data.split(',')))
        assert raw[at:at+len(expected)]==candidate[at:at+len(expected)]==expected,address
    assert text.count('local profileFinish\n')==1
    assert text.count("shot('mini-active-1-2');result(true)")==1
    text = text.replace(PIN,EXPECTED).replace('local profileFinish\n','local profileFinish\nlocal audioAssertFinished\n')
    text = text.replace("shot('mini-active-1-2');result(true)","shot('mini-active-1-2');audioAssertFinished();result(true)")
    result = text+'\n'+audio_config(candidate,proof)+OBSERVER.read_text(encoding='utf-8')
    assert all(token not in result for token in ('emu.write(','emu.reset(','emu.loadSavestate('))
    return result


def verify_cpu(before,after):
    pair = [N.fresh(M.bundle(data)) for data in (before,after)]
    cold = []
    for m in pair:
        N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
              Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
        cold.append(N.invoke(m,'MiniScene'))
        assert bytes(m.ram[3][:5120])==KERNEL.read_bytes() and m.ram[2][0x300]==1
    assert cold[0]==cold[1],cold
    M.compare_state(*pair)
    whole = check_full_cpu(before,after,{})
    assert all(q['min_saved']==q['max_saved']==0 for q in whole),whole
    return dict(actual_MiniScene=cold[0],whole_GameCore=whole)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--check-only',action='store_true',help='Verify in memory without producing any file')
    args = cli.parse_args()
    output = args.output.resolve()
    assert output.is_relative_to(BUILD) and output!=BUILD
    before,after,proof = build_image()
    controller = controller_for(before,after,proof)
    cpu = verify_cpu(before,after)
    summary = dict(parent_SHA256=PIN,candidate_SHA256=EXPECTED,**cpu)
    if not args.check_only:
        assert not output.exists()
        output.mkdir()
        rom = output/'candidate.nes'
        rom.write_bytes(after)
        for suffix in ('.dbg','.lbl'):
            shutil.copyfile(CURRENT.with_suffix(suffix),rom.with_suffix(suffix))
        metadata = rom.with_suffix('.json')
        base = load(CURRENT.with_suffix('.json'))
        assert base['candidate_SHA256']==PIN
        refs = {CURRENT,CONTROLLER,READY,metadata,KERNEL,KERNEL.with_suffix('.lbl'),
                OBSERVER,Path(__file__),*PROOFS}
        base.update(summary,declared_audio_proof_parent_SHA256=F.PIN,
                    audio_frame_token_proofs={str(p):sha(p) for p in PROOFS},
                    private_pending_current_interrupt_proof=True,verification='Private replay pending')
        metadata.write_text(json.dumps(base,indent=2)+'\n',encoding='utf-8')
        prepare(output/'route',rom,controller,refs,expected=EXPECTED,timeout=180,allow_interactive=True,
                scope='Exact delivered Mini full 1-1 controller and offscreen lift checks, plus passive source music and ordered APU/MMC5 register capture.')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
