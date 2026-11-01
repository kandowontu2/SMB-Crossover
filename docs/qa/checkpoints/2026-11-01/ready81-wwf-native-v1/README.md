# 81-character WWF nightly

The WWF slot now cycles Hogan, Ted DiBiase, Bam Bam Bigelow, Honky Tonk Man,
Randy Savage and Andre the Giant with Select. Each uses original poses,
palettes, actor routines and theme data from WWF WrestleMania. Native SMB
terrain, jump input and enemy proxies connect them to this platform game.

The exact ROM passes six cold controller routes: selection, lives, idle,
jump/landing, source punch defeating a Goomba and camera advancement across
a page. All six have displayed sprite/OAM/CHR observations, native vector
register/SMC checks and APU/shared-SFX activity. CPU tests cover688 Start/A
cases,688 linked pose/fallback cases, all16 cookie-byte rejection cases per
wrestler and600 original-versus-buffered audio ticks for each theme.

The complete menu sweep covers120 D-pad/Select transitions and2400 physical
transition frames, with no changed heading pixels or visible PPUMASK writes.

The integration fixes a17-part pose buffer overflow, per-variant cookie loop,
zero-valued palette bytes, software bank ownership after audio, and source
music initialization/channel enabling. No global/ZP allocation or ROM-size
increase was needed. Thomas's selected kernel and native import addresses
are unchanged; unused ROM tails and WWF-owned CHR pages fund the addition.

These checks do not clear full1-1, shortcuts, all upgrades, advanced wrestling,
the complete roster/campaign goal, audio listening quality or steady60Hz.
`source.zip` contains reviewed source grafts and link recipes. Existing frozen
inputs are reused; this does not replace the prepared37-identity builder.
`native-results.zip` contains bounded controllers, compact receipts and at
most four PNGs per run. No video or frame-image sequence was created.

On Windows, run the publishing recipe with `python -X utf8`. Its original
invocation installed and verified the ROM and receipts, then encountered the
locale codec while reading the README. That documentation edit was completed
separately; the tested ROM and frozen source inputs were retained unchanged.
