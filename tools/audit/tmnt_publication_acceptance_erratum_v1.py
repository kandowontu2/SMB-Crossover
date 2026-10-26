"""Additive correction: an ISR flag read cannot give foreground Main slack."""
from pathlib import Path
import argparse
import collections
import json
from tmnt_native_storage_driver import ROOT,sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    old=a.archive/'tmnt-equipment-empty-scans-v1/publication-deadline-v1/proof.json'
    q=json.loads(old.read_text());assert q['strict_before_same_flag_read_requires_saved_CPU_at_least']==410
    bus=a.archive/'tmnt-native-storage-current50b5-v1/parser-native-pilot-v1/candidate-easy/native-bus.jsonl'
    kinds=collections.Counter(json.loads(s)['kind']for s in bus.read_text().splitlines())
    assert set(kinds)=={'completed-game-update','DMA-start','DMA-complete','draw-construction'}
    entry=int(q['actual_NMI_audio_span']['startCPU'])-q['exact_compiled_NMI_prelude_cycles']
    acceptance=entry-q['hardware_NMI_entry_cycles'];publication=q['clear_completion_without_intervening_lag_NMI_CPU']
    assert(entry,acceptance,publication)==(21886300,21886293,21886733)
    distance=publication-acceptance;assert distance==440
    a.output.mkdir(parents=True)
    report='''PUBLICATION DEADLINE ERRATUM: PRIOR410 TARGET WITHDRAWN
2026-10-25. Read-only retained trace/source reconstruction; no native run.
The old model compared hypothetical uninterrupted Main publication to a later
NmiDisable read INSIDE NMI. Main cannot execute during that prelude, so this
is not a scheduling cutoff and410must not be used as a recovery target.

AudioStart21886385 -85compiled prelude =firstNMIopcode21886300.
Minus7hardware entry reconstructs NMI acceptance21886293. Uninterrupted
Main publication21886733 is440cycles later. Conservative strict-before
acceptance needs at least441cycles saved for this assumed same alignment.
425is a measured CPU saving but is16short of that conservative source model.

The raw historical bus log has ONLY draw/complete/DMA events, no NMI-entry,
stackedPC or last-Main-PC observations. Thus the acceptance boundary is source
reconstruction, not a recorded instruction/bus boundary. Instruction/DMC/IRQ
alignment can change. Only a fresh unchanged-workload native run can establish
recovered draws. Preserve all old proof files; this is an additive correction.
'''
    (a.output/'report.txt').write_text(report)
    doc=ROOT/'docs/qa/tmnt-publication-deadline-erratum-2026-10-25.txt';doc.write_text(report+'\nExternal proof: '+str(a.output)+'\n')
    result=dict(valid=True,source_only=True,native_run=False,old410_scheduling_target_withdrawn=True,
                reconstructed_first_NMI_opcode_CPU=entry,reconstructed_acceptance_CPU=acceptance,
                source_counterfactual_publication_CPU=publication,cycles_after_acceptance=distance,
                conservative_strict_before_same_acceptance_saved_cycles=distance+1,
                raw_NMI_entry_stackedPC_lastMain_not_recorded=True,old_raw_event_counts=dict(kinds),
                bindings={str(f):sha(f)for f in[old,bus,Path(__file__),doc]},native_recovery_claim=False)
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
