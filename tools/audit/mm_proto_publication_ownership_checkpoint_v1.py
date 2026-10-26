"""Small additive public checkpoint of the unchanged731 ownership observation."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B=D/'mm-proto-publication-ownership-v1'
O=R/'docs/qa/checkpoints/2026-10-26/mm-proto-publication-ownership'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not O.exists();O.mkdir(parents=True)
    originals={B/'freeze-v1/receipt.json':'12e6fb4bbfb099e02f59319509cf3651c3e8bd0991d6439ae5024e7d37803619',B/'native-freeze-v1/receipt.json':'3e0b7c9455e326a0416446d5343076bf28dab951f53f22df4ff3b124db91380b'}
    for p,h in originals.items():assert sha(p)==h
    pairs=[(B/'freeze-v1/receipt.json','source-freeze.json'),(B/'native-freeze-v1/receipt.json','native-freeze.json'),(B/'native-review-v3/proof.json','native-review.json'),
           (B/'native-review-v3/selected-actual-lag-publication-epochs.json','selected-actual-epochs.json'),(B/'native-review-v3/original-observations-exact.json','original-observations-exact.json'),
           (B/'stack-contract-v1/proof.json','source-stack-proof.json'),(B/'mock-v2/proof.json','observer-mock-proof.json'),
           (B/'native-freeze-v1/all-actual-bindings.json','external-actual-bindings.json'),
           (R/'docs/qa/mm-proto-publication-ownership-2026-10-26.txt','source-report-original.txt'),(R/'docs/qa/mm-proto-publication-ownership-native-2026-10-26.txt','native-report-original.txt')]
    for p,rel in pairs:shutil.copyfile(p,O/rel)
    tools=['mm_proto_publication_ownership_observer_v1.lua','mm_proto_publication_ownership_prepare_v2.py','mm_proto_publication_ownership_mock_v2.py','mm_proto_publication_stack_contract_v1.py','mm_proto_publication_ownership_review_v1.py','mm_proto_publication_ownership_review_v2.py','mm_proto_publication_ownership_review_v3.py','mm_proto_publication_ownership_freeze_v1.py','mm_proto_publication_native_freeze_v1.py']
    (O/'tools').mkdir()
    for name in tools:shutil.copyfile(R/'tools/audit'/name,O/'tools'/name)
    (O/'ERRATUM.txt').write_text('''Additive correction; the original frozen reports and observations are unchanged.

VFLIP: The native observer captured SprObject_SprAttrib, not the actual
ObjectVerticalFlip/PlayerVerticalFlip eligibility field. The reported49
eligible alternating counterfactual turns assume normal V-flip. They are
not49 directly observed eligibility decisions or a captured V-flip trace.
Actual ownership counts, all275 pixel frames and all402 hardware pages
remain byte exact. No alternator code was active in this diagnostic.

RAM/SMC: A raw convertAddress quotient0 for stackedPC below8000 is not
PRGbank0; it is classified RAM/SMC without changing the raw record.

COLD RESET: X5ColdInit alone clears only variants. The later implementation
source audit proves the complete actual CrossoverInit chain reaches
X5InventoryInit/X5ProfilesNewGame and clears5C00..5FFF. The old report's
statement that an extra cold clear is required did not inspect that whole
chain. That subsequent assembled proof belongs to the separate private
publication candidate, not to this unchanged-ROM diagnostic.

OLD DESIGN: bit0/XOR81 was an unimplemented proposal. The later private
candidate uses bit6/XORC0. No source/native proof here is retagged for it.
''')
    (O/'README.txt').write_text('''Unchanged731 ownership diagnostic -- no game patch/adoption

One450-frame read-only run, same controller and unchanged731 ROM. All five
original input/PPU/timing/result files and all275 captured frames exactly
match the existing731 reference.402 full256-byte source/destination DMA
pairs pass.432 Main releases,51 completed Rosters,26 no-draw carry images,
343 stale source-epoch transfers and40 protected lag NMIs were observed.
50 distinct Rosters transferred;51 remained pending at the endpoint.

Read ERRATUM.txt first. The49 counterfactual alternations assume normal
V-flip; actual V-flip was not captured. Source fairness is not pixel/shot
fairness. There was no new state byte or scheduling code in this run.

selected-actual-epochs.json retains actual372/445/450 ownership/stack
links, not invented Main instructions. Full raw captures, ROMs, settings,
audio and source ZIPs stay external. external-actual-bindings.json pins
their965 exact paths/hashes for independent review. Original source/native
reports and finite stack/mock tools are included unchanged. Reviewers v1
and v2 had assertion/oracle mistakes; v3 corrected their source bookkeeping
without rerunning native or weakening any original physical256-byte guard.

Versioned prerequisites: the included tools import audit helpers pinned
in external-actual-bindings.json. Those existing helpers are already in
tools/audit; no large repeated tool/source bundles are copied here.
No native grant/retry, implementation, production/default/settings or Git
operation is performed by this checkpoint builder.
''')
    mapping={str(p.relative_to(R)).replace('\\','/'):'Stage this additive checkpoint only; existing source/native reports and live working tools are not implicitly included.'for p in sorted(O.rglob('*'))if p.is_file()}
    mapping[str(Path(__file__).relative_to(R)).replace('\\','/')]='Checkpoint builder; no source/game/native mutation.'
    (O/'review-files.json').write_text(json.dumps(mapping,indent=2)+'\n')
    catalog={p.relative_to(O).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(O.rglob('*'))if p.is_file()}
    (O/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    for rel,z in catalog.items():assert sha(O/rel)==z['sha256']
    proof=dict(passed=True,checkpoint_only=True,game_patch=False,native_launch=False,ROM_sha256='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c',native_worker_released=True,actual402full256DMAand275pixel_frames_exact=True,Vflip_counterfactual_scope_corrected=True,original_reports_unchanged=True,original_bindings=965,catalog_files=len(catalog),bytes=sum(z['bytes']for z in catalog.values()),catalog_sha256=sha(O/'catalog.json'),builder_sha256=sha(__file__),review_map_sha256=sha(O/'review-files.json'),source_native_scope_distinct=True)
    (O/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(O/'proof.json'),**proof),indent=2))
if __name__=='__main__':main()
