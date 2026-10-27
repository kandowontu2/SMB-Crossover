"""Tiny source metadata only; no emulator launch or source/runtime/ROM copies."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from observe_chip_committed_write import lua
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.rom=a.rom.resolve();a.output=a.output.resolve();assert sha(a.rom)==a.expected_sha256
 b=scoped_load(a.rom);a.output.mkdir(exist_ok=False,parents=True)
 def h(n,d=0,size=3):
  pc=address(b,n)+d;off=location(b,n)+d;bank=(off-16)//8192;bs=b['raw'][off:off+size];banks=[bank]
  if bank==127:
   rel=off-16-127*8192;assert b['raw'][16+125*8192+rel:16+125*8192+rel+size]==bs;banks=[125,127]
  return dict(pc=pc,banks=banks,bytes=list(bs))
 def ret(n,d,op):
  assert b['raw'][location(b,n)+d]==op;return h(n,d,1)
 scopes=[dict(name='NMI',entry=h('NonMaskableInterrupt'),returns=[ret('NonMaskableInterrupt',int(b['syms']['NonMaskableInterrupt']['size'],0)-1,0x40)],terminal_cycles=6,hardware_entry_cycles=7),
 dict(name='AudioUpdate',entry=h('AudioUpdate'),returns=[ret('AudioUpdate',address(b,'AudioUpdate::CrossoverVanillaAudio')-address(b,'AudioUpdate')-1,0x60),ret('AudioUpdate',int(b['syms']['AudioUpdate']['size'],0)-1,0x60)],terminal_cycles=6,hardware_entry_cycles=0),
 dict(name='ExpandedAudioTick',entry=h('ExpandedAudioTick'),returns=[ret('ExpandedAudioTick::Done',0,0x60)],terminal_cycles=6,hardware_entry_cycles=0),
 dict(name='BassSourceAudioTick',entry=h('BassSourceAudioTick'),returns=[ret('BassSourceAudioTick::Done',0,0x60)],terminal_cycles=6,hardware_entry_cycles=0)]
 ram={n:address(b,n)for n in['SelectedCharacter','RlVariant','OperMode','OperMode_Task','GameEngineSubroutine','PlayerStatus','Player_State','WorldNumber','LevelNumber','BassSourceId','XgLzRemaining','XgAudioDelay','BassDmcActive']}
 cfg=dict(ROM_sha256=sha(a.rom),ram=ram,scopes=scopes)
 (a.output/'config.json').write_text(json.dumps(cfg,indent=2)+'\n',newline='\n')
 module=ROOT/'tools/audit/bass_passive_audio_timing_v1.lua'
 (a.output/'append.lua').write_text('BASS_PASSIVE_AUDIO_TIMING='+lua(cfg)+'\nlocal oldClose=ROSTER_CONFIG.bass_close\nlocal audioClose=dofile([=['+module.as_posix()+']=])\nROSTER_CONFIG.bass_close=function()local q=oldClose and oldClose()or{};q.audio_timing=audioClose();return q end\n',newline='\n')
 bindings=[dict(path=str(q),sha256=sha(q),bytes=q.stat().st_size)for q in[a.rom,a.rom.with_suffix('.dbg'),module,Path(__file__).resolve(),a.output/'config.json',a.output/'append.lua']]
 (a.output/'prepared.json').write_text(json.dumps(dict(status='PREPARED_NOT_RUN',read_only=True,bindings=bindings,static_exec_hooks=9,CSV_files=1,no_input_or_state_writes=True,limits='Return opcode observed before execution. Nominal full durations explicitly add6RTS/RTI and7hardware NMI; DMC tail stalls remain a qualified limit. No restoration/campaign claim beyond existing harness.'),indent=2)+'\n',newline='\n')
 print(json.dumps(dict(output=str(a.output),sha256=sha(a.output/'prepared.json'))))
if __name__=='__main__':main()
