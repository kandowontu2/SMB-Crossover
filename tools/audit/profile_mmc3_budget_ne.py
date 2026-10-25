"""Classify current linked storage and identify concrete redesign targets."""
from pathlib import Path
import collections, hashlib, importlib.util, json, re, zlib

R = Path(__file__).resolve().parents[2]
O = R/'build/verification/mmc3-full-roster-feasibility-ne'
base = json.loads((O/'measurements.json').read_text())
full = base['full']
raw = (R/'build/smb-crossover-mmc5-expanded.nes').read_bytes()
segments = full['PRG_segments']
audio = [s for s in segments if any(w in s['name'] for w in ('AUDIO','MUSIC','DPCM'))]
gfx = [s for s in segments if 'GFX' in s['name']]
flare = [s for s in segments if s['name'].startswith('BILL_ORBIT')]
playlists = [s for s in segments if s['name'].startswith('XG_MUSIC_')]
groups = {}
for name, items in [('audio_and_playlist_segments', audio), ('graphics_record_segments', gfx),
                    ('bill_late_orbit_tables', flare), ('existing_LZ_playlists', playlists)]:
    payload = b''.join(raw[16+s['offset']:16+s['offset']+s['bytes']] for s in items)
    groups[name] = dict(bytes=len(payload), host_zlib_bytes=len(zlib.compress(payload, 9)),
                       segments=[s['name'] for s in items])

# Measure a codec that actually has a 6502 implementation in this project.
spec = importlib.util.spec_from_file_location('ne_playlist_codec', R/'tools/reference/build_playlist_audio.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
chr_data = raw[16+1048576:]
unique_pairs = sorted({chr_data[i:i+32] for i in range(0, len(chr_data),32)})
pair_data = b''.join(unique_pairs)
lz = codec.lz(pair_data)  # Includes an independent exact decode check.
(O/'tile-dictionary-existing-lz.bin').write_bytes(lz)

ram = {}
for name in ('smb-crossover-mmc3', 'smb-crossover-mmc5-expanded'):
    text = (R/'build'/(name+'.dbg')).read_text()
    rows = [dict((k,v.strip('"')) for k,v in re.findall(r'(\w+)=("[^"]*"|[^,]*)', s[4:]))
            for s in text.splitlines() if s.startswith('seg\t')]
    ram[name] = {s['name']:int(s['size'],0) for s in rows if s['name'] in ('BSS','SRAM','ZEROPAGE','SHORTRAM')}

report = dict(ROM_sha256=hashlib.sha256(raw).hexdigest(), groups=groups, static_RAM_segments=ram,
    CHR_dictionary_existing_6502_LZ=dict(raw_bytes=len(pair_data), compressed_bytes=len(lz),
        decoder='Existing 2KiB-history/3..34-byte-match LZSS used by ExpandedAudio',
        exact_host_roundtrip=True,
        PRG_total_if_current_code_plus_dictionary=full['PRG_linked_segment_bytes']+len(lz),
        over_512KiB_bytes=full['PRG_linked_segment_bytes']+len(lz)-524288,
        scope='Offline exact compression-size experiment. No CHR RAM loader or safe per-frame transfer schedule implemented.'),
    hardware_dependencies=dict(ExRAM_range='$5C00-$5FFF', ExRAM_bytes=1024,
        source=['src/x5_profiles.s','src/mmc5_expanded.s'],
        expansion_sound_source=['src/mmc5_sfx.s','src/guest_audio.s']),
    caveats=['Classification is by linked segment name and is not a live-code or music-only proof.',
        'Native imported binaries can contain non-audio data, internal padding and duplicated engines. A reachability/relocation proof is needed before removing any of it.',
        'The current playlist streams already use macro compression plus LZSS. Further generic compression is not an established size solution.',
        'CHR RAM moves compressed graphics into PRG; it does not create PRG capacity. The same 2KiB audio history cannot be borrowed concurrently without a new RAM plan.'])
(O/'budget-profile.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
