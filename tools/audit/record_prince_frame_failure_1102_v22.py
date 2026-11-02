"""Preserve the rejected initial frame measurement before corrected reruns."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2];O=R/'build/prince-actor-1101-v1'


def main():
 target=O/'frame-negative-v22.json'
 assert not target.exists(),'Preserve this negative receipt unchanged.'
 q=dict(passed=False,ROM_written=False,shared_sources_written=False,grant=False,cause='Initial v21/v22 private frame factoring used hand-bound ShSavedSmcOffsets AA73, which is source carrier-table data. Actual source-derived SMC table is AA61.',exposed_by=dict(case='Sh raw36 movement row0, RAM2 headerbyte0 XOR1',actual_live_SMC_PC=0x16c,original_value=0x88,incorrect_factored_value=0),earlier_receipt_insufficient=True,omission='Earlier v21 compare omitted page1 live SMC bytes while comparing native state from0200 onward. Corrected checks explicitly compare015A..017B.',superseded_v21_receipt=json.loads((O/'dispatch-factor-CPU-v21.json').read_text()),incorrect_factor_blob_SHA256='405c445d8cb0898a77f38872488f47788f2fa2505ba6d998ac27f3c70e8a7bcb',corrective_requirement='Source-derived exact private symbol, byte-verified table, explicit full SMC parity for rows/foreign/header rejection/IRQ. No grant from the insufficient earlier pass.')
 target.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='superseded_v21_receipt'}))


if __name__=='__main__':main()
