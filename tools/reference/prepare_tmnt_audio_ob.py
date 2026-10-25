"""Relocate the original TMNT music engine without changing instruction widths."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')


def main():
    p=argparse.ArgumentParser();p.add_argument('--label',required=True);a=p.parse_args()
    assert a.label and all(c.isalnum()or c in '-_'for c in a.label)
    out=OUT/a.label;out.mkdir(parents=True,exist_ok=False)
    coverage=OUT/'probe-v2/coverage.json';info=json.loads(coverage.read_text());raw=Path(info['source']).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==info['source_sha256']
    m=[0]*65536;m[0x8000:0x8000+len(raw)-128]=raw[128:];c=MPU(memory=m);d=Disassembler(c)
    seen=set(info['seen_instructions']);pending=list(seen)
    def valid(pc):return 0x8612<=pc<0xc000 or 0xc000<=pc<0xc018
    while pending:
        pc=pending.pop();width,_=d.instruction_at(pc);op,mode=c.disassemble[m[pc]]
        assert op!='???',(hex(pc),m[pc])
        targets=[]
        if mode=='rel':
            v=m[pc+1];targets=[pc+width,pc+width+(v-256 if v>=128 else v)]
        elif op in ('JMP','JSR'):
            if mode=='abs':targets.append(m[pc+1]+256*m[pc+2])
            if op=='JSR':targets.append(pc+width)
        elif op not in ('RTS','RTI','BRK'):targets=[pc+width]
        for target in targets:
            assert valid(target),('Code closure escaped retained sound code',hex(pc),hex(target))
            if target not in seen:seen.add(target);pending.append(target)
    def move(at):
        if 0x8612<=at<0xc000:return at+0x2000
        if 0xc000<=at<0xc02c:return at-0x2000
        raise AssertionError(('Unowned source ROM pointer',hex(at)))
    words=set(info['pointer_words']);apu=[];operands=[]
    # The command dispatcher adds3*command to this pointer before use.
    # Arithmetic obscures the simple load/store provenance in the observer.
    assert m[0x9014]+256*m[0x9015]==0x918b
    assert bytes(m[0x90b6:0x90b9])==bytes.fromhex('ad1490')
    assert bytes(m[0x90bb:0x90be])==bytes.fromhex('ad1590')
    words.add(0x9014)
    lines=['; Original pinned TMNT NSF engine/data. Original instruction widths retained.',
           '; CPU page1 channel state moves to owned history; E0..ED remain borrowed ZP.',
           '.pushseg','.segment "TMNT_NATIVE_AUDIO_A"','TnNativeImageStart:']
    def region(start,end):
        pc=start
        while pc<end:
            if pc in seen:
                width,txt=d.instruction_at(pc);op,mode=c.disassemble[m[pc]]
                if mode in ('abs','abx','aby','ind'):
                    at=m[pc+1]+256*m[pc+2];suffix=',x'if mode=='abx'else',y'if mode=='aby'else''
                    operand=f'${move(at):04x}'if at>=0x8000 else f'::TnAudioRam+${at-0x100:02x}'if 0x100<=at<=0x1ad else f'${at:04x}'
                    txt=op+' '+('('+operand+')'if mode=='ind'else operand+suffix)
                    if op in ('STA','STX','STY')and 0x4000<=at<=0x4017:
                        helper='TnSource'+op+f'{at-0x4000:02X}'+('X'if mode=='abx'else'Y'if mode=='aby'else'')
                        apu.append(dict(pc=pc,operation=op,mode=mode,address=at,helper=helper))
                        txt='.if ::TN_RAW_APU\n  '+txt+'\n.else\n  jsr ::'+helper+'\n.endif'
                    if 0x100<=at<=0x1ad or at>=0x8000:operands.append(dict(pc=pc,address=at))
                elif mode=='rel':
                    # Keep the original short displacement. Both endpoints
                    # must share the same translation; no expansion is allowed.
                    v=m[pc+1];target=pc+width+(v-256 if v>=128 else v)
                    assert move(target)-move(pc)==target-pc
                    txt=f'.byte ${m[pc]:02x},${v:02x} ; {op} source ${target:04x}'
                lines.append(f'  .assert *=${move(pc):04x},lderror,"Original instruction offset {pc:04x}"')
                lines.append('  '+txt);pc+=width
            elif pc in words:
                target=m[pc]+256*m[pc+1];lines.append(f'  .word ${move(target):04x}');pc+=2
            else:
                # Raw untouched note data; bounded runs stop at instructions
                # and proven pointer words, preserving every source byte.
                values=[m[pc]];pc+=1
                while pc<end and pc not in seen and pc not in words and len(values)<24:
                    values.append(m[pc]);pc+=1
                lines.append('  .byte '+','.join(f'${v:02x}'for v in values))
    region(0xc000,0xc02c)
    lines+=['  .assert *=$a02c,lderror,"NSF bootstrap and DMC table footprint"',
            '  .res $5e6,$ff','TnNativeSourceBegin:']
    region(0x8612,0xa000)
    lines+=['  .assert *=$c000,lderror,"First native bank footprint"','.segment "TMNT_NATIVE_AUDIO_B"']
    region(0xa000,0xc000)
    lines+=['  .assert *=$e000,lderror,"Second native bank footprint"',
            'TnNativeInit=$a000','TnNativePlay=$a644','TnNativeCommand=$b057',
            '.export TnNativeInit,TnNativePlay,TnNativeCommand','.popseg']
    driver=out/'tmnt-native.inc';driver.write_text('\n'.join(lines)+'\n')
    (out/'raw-test.s').write_text('TN_RAW_APU=1\nTnAudioRam=$7000\n.include "tmnt-native.inc"\n')
    (out/'raw-test.cfg').write_text('MEMORY { A:start=$a000,size=$2000,file=%O,fill=yes,fillval=$ff; B:start=$c000,size=$2000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { TMNT_NATIVE_AUDIO_A:load=A,type=ro; TMNT_NATIVE_AUDIO_B:load=B,type=ro; }\n')
    commands=[[str(ROOT/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502','-o',str(out/'raw-test.o'),str(out/'raw-test.s')],
              [str(ROOT/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(out/'raw-test.cfg'),'-Ln',str(out/'raw-test.lbl'),'-o',str(out/'raw-test.bin'),str(out/'raw-test.o')]]
    log=''
    for cmd in commands:
        z=subprocess.run(cmd,cwd=out,capture_output=True,text=True);log+=z.stdout+z.stderr
        (out/'build.log').write_text(log);assert z.returncode==0,(z.stdout+z.stderr)[-1600:]
    q=dict(passed=True,source=info['source'],source_sha256=info['source_sha256'],coverage_sha256=hashlib.sha256(coverage.read_bytes()).hexdigest(),
           original_payload_bytes=len(raw)-128,retained_source_regions=[[0x8612,0xc000],[0xc000,0xc02c]],
           original_unused_prefix_bytes=0x612,source_DPCM_separately_reserved=True,retained_ZP=list(range(0xe0,0xee)),
           state_range=[0x100,0x1ad],closed_instructions=len(seen),observed_instructions=len(info['seen_instructions']),
           pointer_words=len(words),explicit_arithmetic_pointer_roots=[dict(word=0x9014,target=0x918b,low_load=0x90b6,high_load=0x90bb)],APU_stores=apu,changed_operands=operands,
           raw_binary_sha256=hashlib.sha256((out/'raw-test.bin').read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(driver.read_bytes()).hexdigest(),
           scope='Standalone original-driver relocation. Game integration, original waveform/DMC playback and golden output comparison pending.')
    (out/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','closed_instructions','observed_instructions','pointer_words','raw_binary_sha256']}))


if __name__=='__main__':main()
