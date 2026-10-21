"""Root rehash of four retained native movies and their complete frame scans."""
from pathlib import Path
import collections,hashlib,json,wave
R=Path(__file__).resolve().parents[2];V=R/'build/verification';J=V/'root49-h-base-captures-di'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()
read=lambda p:json.loads(Path(p).read_text())
def main():
 out=V/'root49-h-media-root-review-dz.json';assert not out.exists()
 source=J/'review.json';assert sha(source)=='2081f917bf086b790ed75b6cfcfc3f83dc7bfc907c6619690cd4f13bd49b0ce4';j=read(source);assert j['status']=='PASS_FOUR_H_BASE_ROUTE_CAPTURES'
 assert sha(V/'root49-h-route-root-review-dl.json')=='5b64c4e044d51ea5f97e27ebb10082f3bd991c804c8203058e64c359774d9b4d'
 catalog={};reports=[]
 for q in j['results']:
  d=(R/q['manifest']).parent;m=read(d/'manifest.json');p=read(d/'playthrough-lossless.verification/report.json');delivery=read(d/'playthrough.delivery.json');scan=read(d/'review.json')
  assert sha(d/'manifest.json')==q['manifest_sha256']and m['recording_verified']and m['verified_through_2_2']and m['full_frame_audit']and m['controller_only']and not m['memory_or_register_writes']
  assert m['rom_sha256']==sha(d/'smb-crossover-mmc3.nes')=='df226ab7be27a0f0b9231c1a66ac16200ba487ee041be10308dd6757343a8d6f'
  assert p['result']=='passed-exact-rgb-and-pcm'and p['video_rgb_identity']and p['continuous_pcm_identity']and p['timestamps_passed']and not p['frame_or_sample_interpolation']and not p['video_reencoded']
  assert sha(d/'playthrough-lossless.mkv')==p['output']['sha256']==scan['video_sha256']==delivery['master_sha256']
  assert m['lossless_verification_sha256']==sha(d/'playthrough-lossless.verification/report.json')==q['lossless']
  frames=m['result']['frames']-1;assert p['total_frames']==frames==scan['decoded_video_frames']and scan['every_recorded_frame_decoded']and scan['video_kind']=='verified lossless native RGB and PCM master'
  assert sum(a['frames']for a in p['inputs'])==frames
  for a in p['inputs']:assert sha(R/a['path'])==a['sha256']
  wavepath=R/p['wave']['path'];assert sha(wavepath)==p['wave']['sha256']
  h=hashlib.sha256();size=0
  with wave.open(str(wavepath),'rb')as w:
   assert(w.getnchannels(),w.getsampwidth(),w.getframerate())==(2,2,48000)
   while b:=w.readframes(262144):h.update(b);size+=len(b)
  assert size==p['source_pcm']['bytes']==p['master_pcm']['bytes']and h.hexdigest()==p['source_pcm']['sha256']==p['master_pcm']['sha256']
  assert delivery['passed']and delivery['metadata']['passed']and delivery['metadata']['video_frames']==frames and delivery['metadata']['mp4_sha256']==sha(d/'playthrough.mp4')
  assert sha(d/'playthrough.delivery.json')==m['delivery_report_sha256']==q['delivery']
  for n in['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']:
   assert q['streams'][n]['literal']and sha(d/n)==q['streams'][n]['sha256']
  flags={n:len(scan[n])for n in['split_timing_candidates','lag_chr_change_candidates','motion_candidates','video_vertical_shift_candidates','video_background_flash_candidates','illegal_guest_native_stomps']};assert not any(flags.values())
  pending=scan['audio_events_needing_priority_or_audible_review'];assert all(a['physical_audio_writes']for a in pending)
  reports.append(dict(character=q['character'],manifest=q['manifest'],manifest_sha256=sha(d/'manifest.json'),result=m['result'],lossless=str((d/'playthrough-lossless.mkv').relative_to(R)),delivery=str((d/'playthrough.mp4').relative_to(R)),native_parts=len(p['inputs']),decoded_lossless_frames=frames,exact_native_PCM_bytes=size,audio_seconds=p['audio_seconds'],video_seconds=p['video_seconds'],automated_flags=flags,unconfirmed_audio_ownership_events=len(pending),unconfirmed_audio_groups=dict(collections.Counter(a['event']for a in pending)),selected_contact_sheet_frames=scan['contact_sheet_frames'],scan_sha256=sha(d/'review.json'),visually_inspected_contact_sheets={a.name:sha(a)for a in sorted(d.glob('review-contact-*.png'))},limits='Base route only. Contact sheets are selected visual samples; complete RGB decoding is automated. Sound-request/physical-write evidence does not prove every action has correct audible SFX or source waveform. No all-upgrade/full-final-release certification.'))
  for a in d.rglob('*'):
   if a.is_file():catalog[str(a.relative_to(R))]=dict(bytes=a.stat().st_size,sha256=sha(a))
 frozen=J/'root-media-catalog-dz.json';assert not frozen.exists();frozen.write_text(json.dumps(catalog,indent=2)+'\n')
 report=dict(status='PASS_FOUR_RETAINED_H_BASE_MOVIES_EXACT_RGB_PCM_AND_COMPLETE_AUTOMATED_FRAME_SCANS',script_sha256=sha(__file__),source_capture_review_sha256=sha(source),encoder_sha256=sha(R/'tools/playthroughs/encode_capture_delivery.py'),frame_reviewer_sha256=sha(R/'tools/playthroughs/roster_review.py'),recordings=reports,total_decoded_lossless_frames=sum(a['decoded_lossless_frames']for a in reports),native_lossless_parts_retained=sum(a['native_parts']for a in reports),catalog=dict(path=str(frozen.relative_to(R)),sha256=sha(frozen),files=len(catalog)),audio_followup='Link321/MegaMan2727 queue events have physical writes but lack generic overlay owner evidence. NativeRosterWrapper explicitly remaps some native requests; a specialized native ownership/priority/audible audit is required. These are not established missing sounds or waived failures.',manual_every_frame_or_waveform_review=False,all_arsenal_complete=False,all_final_recordings_complete=False,goal_complete=False)
 out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(sha256=sha(out),frames=report['total_decoded_lossless_frames'],parts=report['native_lossless_parts_retained'],catalog_files=len(catalog))))
if __name__=='__main__':main()
