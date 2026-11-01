# 76-character nightly and character-select timing repair

The final ROM adds Thomas alongside Hogan. Thomas is the second Select alternate
in Ryu's slot. Ten of the86 individual menu identities remain coming soon.

The original combined ROM had17 menu transitions whose rendering/scroll work
ran past the safe update window. Accept the actual palette packet shapes, reuse
the static legend, omit unused palette writes based on actual OAM, and coalesce
duplicate portrait colors. Alex's forced outlines are retained.

The final cold-controller sweep covers120 D-pad/Select transitions and2400
physical transition frames: every heading pixel is identical and no PPUMASK
write reaches a visible scanline. Actual source CPU execution verifies688
Start/A cases and86 unchanged preview OAM/displayed-palette results.

On the final ROM, Hogan repeats his663-update jump/punch/Goomba/camera route;
Thomas repeats selection/lives/source melee and the first native moving-platform
pipe crossing. The combined gameplay parent also clears all four1-1 pipes with
Thomas and earns pistol defeats with all four Contra Force characters. Subsequent
changes are confined to the menu bank; all CHR and selected source images are exact.

These are bounded opening-route checks. Full stages, every upgrade, original
audio and the remaining roster/campaign work are still incomplete.

`source.zip` stores the exact source grafts and recipes, not a standalone prepared
builder. Reuse existing frozen component inputs; recover only exact missing
source paths from the indexed recovery archive. Do not recursively extract old
proof trees. `native-results.zip` stores compact controllers, receipts and at most
four PNGs per run. No videos or frame-image sequences were created.
