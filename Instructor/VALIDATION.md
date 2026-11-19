# Standalone edition: week11-standalone-v1

Validated in **5.7.4-51494982+++UE5+Release-5.7** on Windows against baseline commit `6f92f32`.

- All **22 maps** load and generate PCG output. All **70 actor output signatures** (mesh identities and transforms) match the baseline exactly.
- All **277 native packages** load. The asset-registry dependency audit finds zero missing assets, previous-week paths, redirectors, or packages unrelated to the Week 11 maps.
- The four forest-floor/snow textures now live under `/Game/Trail/Textures/Surfaces`. Both ground materials were updated through Unreal asset tools; the old Week09 packages are gone.
- Museum startup, station selection, Forest/Snow navigation, and the Scrub exercise pass. Scrub changes 412 → 268 → 412, with tree/rock outputs unchanged and an exact restored signature.
- `npm run check` checks every native package against the manifest and rejects previous-week content folders, unlisted packages, and incorrect overview release links.
- `Overview.html`, `README.md`, and `START-HERE.html` reference the same versioned package. Both slide decks are included.

Evidence: [standalone-validation.json](standalone-validation.json), [standalone-migration.json](standalone-migration.json). Reusable engine audit: [check_standalone.py](ValidationScripts/check_standalone.py).

Scope: editor validation on this Windows machine with Unreal preinstalled. This does not claim packaged-game testing, gameplay/navigation correctness, or a second-machine test.

## Earlier validation history

# Prior validation update

The kit contains **275 native packages and 21 maps**. The added Spline_Examples map was loaded in the reduced student project in UE 5.7.4, without the private authoring helper. It produced 10 posts, 38 shrubs and 61 boundary-guide segments; all shrub roots passed containment. The source comparisons produced 20 posts at 125 cm and 90 shrubs at 160 cm; restoring the original controls restored the complete baseline signature. The original 20 maps retain the earlier fresh-clone validation below. No second physical machine is claimed.

The local PowerPoint was opened and all 49 slides exported through Microsoft PowerPoint. Native assets and relevant material dependencies are bundled. The graph-count chart is not a CPU/GPU timing measurement.

## Earlier fresh-clone baseline

# Validation of the supplied baseline

The clean GitHub checkout was opened in **UE 5.7.4 on Windows** with the project's default DX12/SM6 settings. All 273 native packages load, all 20 maps produce PCG output, Forest/Snow menu navigation passes, and there are no dirty packages before navigation. The private authoring plugin is absent. The material-usage repair warning is gone. No Fab migration, C++ build, external Python or Houdini setup was performed.

67 native mesh/transform signatures match the earlier baseline. The redesigned slope station intentionally changes its marker transforms, retaining six baseline markers. Its measured 0/12/25-degree surfaces produce six accepted points at 0.975, three at 0.995 and six after restoration. Scrub's guided exercise passes 412 â†’ 268 â†’ 412; Trees/Rocks are identical and the restored signature matches exactly.

This is same-machine validation with Unreal preinstalled. A second physical machine and an unaided novice rehearsal have not been observed. The optional HDA cook is still license-blocked; the main project does not use Houdini.

The offline reader has 47 slides, 44 visible by default, all with notes. Its local links, JavaScript syntax and changing frames in all three GIFs pass. Local-file browser preview was blocked by browser URL policy; browser playback and animation behavior after PPTX export are not asserted. The included reader retains the GIF media independently of presentation-viewer behavior.

`validation-summary.json` records the results. Native content was tested at commit acaf118; subsequent lecture-only changes preserve its package hashes. Future project changes should be tested again rather than inheriting this result automatically.

## Optional maintainer checks

Opening the project does not require running a check. Maintainers with Node installed may use `npm run check` from the repository root to verify the native package hashes and setup configuration.

The portable scripts in ValidationScripts run through Unreal's bundled editor Python, not a separate Python installation. Set WEEK11_VALIDATION_DIR to a new output directory, then launch UnrealEditor.exe with the supplied .uproject and `-ExecCmds="py <absolute path to check_fresh_week11.py>"`. Leave the private authoring plugin disabled. For an unattended capture/test process, `-RenderOffscreen -unattended -NoSourceControl` may be added; do not override the renderer, since the project default is part of the check.

Run the lesson-action script against a clean baseline to test the controlled Scrub comparison and delayed museum navigation. These scripts make temporary test edits and close Unreal without saving the changed exercise values. Use a disposable checkout for validation, and preserve your own student work separately.
