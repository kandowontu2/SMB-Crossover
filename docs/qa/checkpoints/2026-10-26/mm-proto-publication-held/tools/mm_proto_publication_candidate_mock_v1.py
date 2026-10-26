"""Exercise the actual read-only ownership Lua callbacks, without an emulator."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

from observe_chip_committed_write import lua

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepared',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True)
    cfg=json.loads((a.prepared/'ownership-config.json').read_text())
    cfg['out']=a.output.resolve().as_posix()+'/'
    module=R/'tools/audit/mm_proto_publication_candidate_observer_v1.lua'
    sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa import LuaRuntime
    rt=LuaRuntime(unpack_returned_tuples=True)
    rt.execute('PUBLICATION_OWNERSHIP='+lua(cfg))
    rt.execute('''
host={callbacks={},events={},mem={},rom={},hardware={},banks={126,4,88,127}}
cpu={['cpu.pc']=0,['cpu.sp']=253,['cpu.a']=0,['cpu.x']=0,['cpu.y']=0,
 ['ppu.frameCount']=0,['ppu.scanline']=0,['ppu.cycle']=0,['cpu.cycleCount']=0}
emu={callbackType={exec=1,write=2},eventType={endFrame=1},memType={nesDebug=0,nesSpriteRam=1}}
function emu.read(at,kind)
 if kind==1 then return host.hardware[at]or 0 end
 if at>=0x8000 then return host.rom[at]or 0 end
 return host.mem[at]or 0
end
function emu.getState()return cpu end
function emu.convertAddress(pc)
 if pc<0x8000 then return nil end
 return{address=host.banks[pc//8192-3]*8192+pc%8192}
end
function emu.addMemoryCallback(fn,kind,first,last)
 host.callbacks[#host.callbacks+1]={fn=fn,kind=kind,first=first,last=last or first}
end
function emu.addEventCallback(fn,kind)host.events[#host.events+1]={fn=fn,kind=kind}end
function tick()cpu['cpu.cycleCount']=cpu['cpu.cycleCount']+3;cpu['ppu.cycle']=cpu['ppu.cycle']+9 end
function write(at,v)
 host.mem[at]=v
 for _,c in ipairs(host.callbacks)do if c.kind==2 and at>=c.first and at<=c.last then c.fn(at,v)end end
 tick()
end
function hook(n)
 local h=PUBLICATION_OWNERSHIP.hooks[n];cpu['cpu.pc']=h.pc;host.banks[h.pc//8192-3]=h.bank
 for i,v in ipairs(h.bytes)do host.rom[h.pc+i-1]=v end
 for _,c in ipairs(host.callbacks)do if c.kind==1 and h.pc>=c.first and h.pc<=c.last then c.fn(h.pc)end end
 tick()
end
function mainBegin()hook('GameLoopEntry');cpu['cpu.pc']=PUBLICATION_OWNERSHIP.hooks.GameLoopEntry.pc+5;write(PUBLICATION_OWNERSHIP.ram.NmiDisable,255)end
function source(seed)
 cpu['cpu.pc']=0xa060;host.banks[2]=4
 for i=0,15 do write(0x200+i,(seed+i*7)%256)end
end
function draw(seed)hook('DrawAll');source(seed);write(PUBLICATION_OWNERSHIP.ram.MmPublicationState,128);hook('RosterReady')end
function release()
 cpu['cpu.pc']=PUBLICATION_OWNERSHIP.hooks.GameLoopDone.pc;host.banks[1]=126
 write(PUBLICATION_OWNERSHIP.ram.NmiDisable,0);hook('GameLoopDone')
end
function nmiStart()
 cpu['cpu.sp']=250;host.mem[0x1fb]=0x24;host.mem[0x1fc]=0x55;host.mem[0x1fd]=0x83
 hook('NmiEntry')
end
function dma()
 nmiStart();cpu['cpu.pc']=0xe005;host.banks[4]=127;write(0x4014,2)
 for i=0,255 do host.hardware[i]=host.mem[0x200+i]or 0 end
 hook('DmaComplete');write(PUBLICATION_OWNERSHIP.ram.MmPublicationState,64);hook('NmiReturn')
end
''')
    rt.execute(module.read_text())
    installed=rt.eval('#host.callbacks')
    # No emulator executes these functions. They deliberately invoke the
    # registered real observer callbacks with finite mock state transitions.
    rt.execute('''
mainBegin();draw(11);release()
mainBegin();release();dma() -- no-draw catchup preserves preceding construction
dma() -- stale transfer must retain identical source provenance
mainBegin();draw(31);release()
mainBegin();draw(51);release();dma() -- newer construction overwrites older one
mainBegin();draw(71)
nmiStart();hook('NmiReturn') -- protected lag NMI: no DMA
cpu['cpu.pc']=0xa062;host.banks[2]=4;write(0x20f,222);release();dma()
mainBegin();hook('MoveAll')
cpu['cpu.pc']=0xa100;host.banks[2]=4
for i=0,63 do write(0x200+i*4,248)end
release();dma()
cpu['ppu.frameCount']=450
for _,e in ipairs(host.events)do if e.kind==1 then e.fn()end end
''')
    assert rt.eval('#host.callbacks')==installed
    rows=[json.loads(s) for s in (a.output/'ownership.jsonl').read_text().splitlines()]
    releases=[q['main'] for q in rows if q['kind']=='Main-release']
    starts=[q['DMA'] for q in rows if q['kind']=='DMA-source-owner']
    ends=[q for q in rows if q['kind']=='DMA-completed-owner']
    def raw(x):return bytes(x[str(i)] for i in range(1,257))
    assert len(releases)==6 and len(starts)==len(ends)==5
    assert starts[0]['last_release']['id']==2 and starts[0]['last_roster']['id']==1
    assert starts[0]['last_release']['draws']==0
    assert raw(starts[0]['source'])==raw(starts[0]['last_roster']['source'])
    assert starts[0]['source_write']==starts[1]['source_write']
    assert raw(starts[0]['source'])==raw(starts[1]['source'])
    assert starts[2]['last_roster']['id']==3 and starts[2]['last_release']['id']==4
    assert starts[3]['last_roster']['id']==4 and starts[3]['last_release']['id']==5
    assert raw(starts[3]['source'])!=raw(starts[3]['last_roster']['source'])
    assert starts[4]['last_roster']['id']==4 and starts[4]['last_release']['id']==6
    assert raw(starts[4]['source'])!=raw(starts[4]['last_roster']['source'])
    assert all(q['mirror_exact'] and q['writer_pc']==0x8355 and q['writer_bank']==126 for q in releases)
    assert all(raw(s['source'])==raw(e['hardware']) for s,e in zip(starts,ends))
    accepted=[q for q in rows if q['kind']=='NMI-acceptance']
    assert len(accepted)==6
    assert all(q['interrupted']['stacked_pc']==0x8355 and q['interrupted']['stacked_bank']==126 and q['interrupted']['stacked_p']==0x24 for q in accepted)
    assert any(q['main']==5 and q['construction']==-1 and q['state']['NmiDisable']==255 for q in accepted)
    statewrites=[q for q in rows if q['kind']=='publication-state-write']
    assert len(statewrites)==9 and set(q['value']for q in statewrites)=={64,128}
    returned=[q for q in rows if q['kind']=='NMI-return']
    assert all('MmPublicationState'in q['state'] and 'ObjectVerticalFlip'in q['state']for q in returned)
    assert installed==15
    result=json.loads((a.output/'ownership-result.json').read_text())
    assert result['observed_DMA_starts']==5 and not result['pending_DMA']
    deps={Path(__file__),module,a.prepared/'ownership-config.json',a.prepared/'base-preparer.json'}
    binding={str(p.resolve()):sha(p) for p in sorted(deps)}
    proof=dict(passed=True,source_only=True,native_run=False,mock_only=True,
               actual_module_callbacks_exercised=True,new_publication_state_write_callback_exercised=True,NMI_return_state_includes_actual_Vflip_and_tag=True,static_callback_count=installed,
               Main_releases=6,complete_mock_DMA_pairs=5,source_writes=result['source_writes'],
               no_draw_catchup_provenance=True,stale_transfer_provenance=True,
               repeated_construction_replacement=True,partial_postdraw_write_retained=True,
               direct_lifecycle_replacement_retained=True,hardware_stacked_PC_bank_P_mock=True,
               protected_lag_NMI_without_DMA=True,all_full_mock_hardware_source_pages_exact=True,
               all_actual_main_release_pc_bank_checks_exercised=True,
               runtime_callback_registration_count_change=0,bindings=binding,tool_sha256=sha(__file__),
               limits='Finite Lua callback mock only. No native physical/frame/cost/IRQ timing or game implementation qualification. Original unchanged450 mechanical guards are not retested or relabeled by this mock.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),**proof),indent=2))


if __name__=='__main__':main()
