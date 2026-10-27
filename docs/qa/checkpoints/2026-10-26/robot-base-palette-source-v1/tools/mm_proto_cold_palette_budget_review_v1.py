"""Bind the literal378 budget failure to its newly captured native owners."""
from pathlib import Path
import argparse
import hashlib
import json

D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'robot-cold-palette-budget-ready-v1'
OLD=D/'robot-cold-palette-candidate-v2/ready-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')
rows=lambda p:[json.loads(x)for x in Path(p).read_text().splitlines()]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    for f,h in json.loads((B/'bindings.json').read_text()).items():assert sha(f)==h,f
    n=B/'native';old=OLD/'native'
    outcome=json.loads((B/'launch-outcome-v1.json').read_text())
    assert outcome['returncode']==1 and not outcome['strict_profile_pass']and outcome['native_worker_released']
    epochs=rows(n/'ability-dma-epochs.jsonl');prior=rows(old/'ability-dma-epochs.jsonl')
    assert epochs==prior
    assert json.loads((n/'first-failure.json').read_text())==json.loads((old/'first-failure.json').read_text())
    assert rows(n/'events.jsonl')==rows(old/'events.jsonl')
    assert (n/'actual-ppu.argb').read_bytes()==(old/'actual-ppu.argb').read_bytes()
    assert (n/'actual-ppu-index.csv').read_bytes()==(old/'actual-ppu-index.csv').read_bytes()
    diag=rows(n/'bass-diagnostic.jsonl');old_diag=rows(old/'bass-diagnostic.jsonl')
    assert [x for x in diag if x['stamp']['frame']<=377]==old_diag
    nmi=next(x for x in diag if x['kind']=='NMI-entry'and x['stamp']['frame']==378)
    assert nmi['state']['CrossoverBehaviorVersion']==nmi['state']['ProtoVariant']==nmi['state']['SelectedCharacter']==1
    packet=nmi['queues']['buffer1'];assert nmi['queues']['buffer1_offset']==53
    assert packet[:28]==[32,35,11,11,30,28,29,14,27,36,36,36,36,36,32,55,2,36,36,32,87,2,36,36,32,74,71,36]
    assert packet[28:54]==[63,29,3,15,55,23,63,25,3,22,48,39,63,16,4,34,15,22,16,63,17,3,15,22,16,0]
    parser=[x for x in diag if x['kind']=='actual-parser-head'and x['stamp']['frame']==378]
    assert len(parser)==9 and parser[-1]['data']['terminator']
    assert [x['data']['PPU_address']for x in parser[:-1]]==[0x2023,0x2037,0x2057,0x204a,0x3f1d,0x3f19,0x3f10,0x3f11]
    costs=[parser[i+1]['stamp']['cpu']-parser[i]['stamp']['cpu']for i in range(8)]
    assert costs==[256,136,136,171,152,152,168,152]
    ret={x['data']['name']:x for x in diag if x['kind']=='actual-owner-return'and x['stamp']['frame']==378}
    assert ret['SamusFreezeUpdateScreen']['data']['inclusive_cycles']==1401
    assert ret['BankSwitchCHR']['data']['inclusive_cycles']==435
    offset_writes=[x for x in diag if x['kind']=='actual-buffer-or-lease-write'and x['data']['address']==1198 and x['stamp']['frame']==377]
    assert [x['data']['value']for x in offset_writes]==[0,28,34,40,47,53]
    assert [(x['stamp']['bankPC'],x['stamp']['pc'])for x in offset_writes[1:]]==[(59,0xbffe),(3,0xb189),(3,0xb1d6),(78,0xab63),(59,0xa0da)]
    special=next(x for x in diag if x['kind']=='actual-owner-entry'and x['data']['name']=='SpecialPalette'and x['stamp']['frame']==377)
    assert special['state']['SsLastPalette']==0 and special['queues']['buffer1_offset']==28
    reset=next(x for x in rows(n/'events.jsonl')if x['kind']=='declared-component-reset')
    cfg=json.loads((n/'config.json').read_text());ss=cfg['diagnostic']['ram']['SsLastPalette']
    assert cfg['ram']['SpecialRamStart']<=ss<cfg['ram']['SpecialRamStart']+cfg['special_ram_bytes']
    fail=next(x for x in epochs if x['kind']=='actual-PPUMASK-write'and x['scoped']and x['enabling']and not x['safe'])
    disable=[x for x in epochs if x['kind']=='actual-PPUMASK-write'and not x['enabling']][-1]
    dma=[x for x in epochs if x['kind']=='completed-DMA-before-render-enable'][-1]
    assert dma['start']['cpu']-disable['stamp']['cpu']==1911
    assert dma['complete']['cpu']-dma['start']['cpu']==517
    assert fail['stamp']['cpu']-dma['complete']['cpu']==4
    selected=[nmi,*parser,*offset_writes,special,reset,*[x for x in diag if x['kind']=='actual-owner-return'and x['stamp']['frame']==378],fail]
    put(a.output/'actual-378-evidence.json',selected)
    sources=D/'robot-cold-palette-candidate-v2/source'
    relevant=['src/inventory.s','src/special_weapons.s','src/megaman_palette.s','src/protoman_cold.s','src/x5_palette.s','src/robot_cold_palette_cache.s','src/reset.s','src/mmc5_expanded.s']
    manifest={str(x):sha(x)for x in [*n.iterdir(),*B.glob('*.json'),B/'launch-host-v1.log',*[(sources/x)for x in relevant],Path(__file__)]if x.is_file()}
    put(a.output/'external-manifest.json',manifest)
    put(a.output/'proof.json',dict(diagnostic_completed=True,native_profile_pass=False,native_launches=1,retries=0,
        actual_original_failure_semantically_exact=True,all353_full_DMA_epochs_semantically_exact=True,
        all377_completed_PPU_and_index_byte_exact=True,events_semantically_exact=True,
        original374_to377_diagnostic_rows_semantically_exact=True,
        actual_mode=1,actual_variant=1,actual_378_NMI_entry=nmi['stamp'],actual_378_state=nmi['state'],actual_378_queues=nmi['queues'],
        actual_parser_command_cycles=costs,actual_HUD28_parser_cycles=sum(costs[:4]),actual_palette25_parser_cycles=sum(costs[4:]),
        actual_palette_gateway_inclusive_cycles=1401,actual_CHR_inclusive_cycles=435,
        other_disable_to_DMA_cycles=75,actual_disable_to_DMA_cycles=1911,actual_DMA_cycles=517,actual_enable_after_DMA_cycles=4,
        first_bad_enable=fail,source_updates=2,completed_component_cases=0,
        exact_ownership='InventoryHud377 appends28B; declared setup clears124B SpecialRam includingSsLastPalette; actualSpecialPalette sees0/default and appends19B viaGetColors; actualMegaManPaletteState59:A0DA appends6B; ProtoFix converts already queued player colors. NMI378 parses28HUD+25palette, publishes435cycleCHR, completesDMAtoo late.',
        duplicate_whole_palette_group=False,redundant_3F11_colors_match_preceding_3F10_tail=True,
        actual_MmLastPalette_RAM_snapshot_available=False,
        additional_source_lead='An exact complete defaultGetColors body palette may permit publishing its existingMmLastPalettecache1/2, onlyif source conditions/state/queuecapacity prove laterMegaPaletteState has the same colors.152 is actual redundant3F11 parser cost, not qualified fix/native recovery.',
        native_worker_released=True,no_production_change=True,
        evidence_sha256=sha(a.output/'actual-378-evidence.json'),manifest_sha256=sha(a.output/'external-manifest.json'),tool_sha256=sha(__file__),
        limits='One diagnostic originalstrictFALSE; no new gameplay qualification. Original observer body/control/ROM unchanged except loggingfocus. InternalMmcacheclear follows executedsource, not an invented nativeRAMsnapshot. Currentfixture explicitly stagesactor/tier/resources and clearsSpecialRam; realweapon-default ownership mustbe separatelytested foranyproductfix. No nativebudgetrecovery claim.'))
    print(json.dumps(dict(proof=str(a.output/'proof.json'),sha256=sha(a.output/'proof.json'),parser=1401,CHR=435,native_pass=False),indent=2))


if __name__=='__main__':main()
