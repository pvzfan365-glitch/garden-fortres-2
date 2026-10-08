// pvz_gw2_welcome.nut
// First-spawn HUD line: either "Loaded N GW2 sounds" or the fallback notice.
// Reads sound/cache/manifest.json written by bin/pvz_gw2_first_run.exe.
// Pure VScript (Squirrel). No SourceMod, no script extender.

local manifestPath = "custom/pvz_gw2_kit/sound/cache/manifest.json";
local shown = false;

function OnGameEvent_player_spawn(params)
{
    if (shown) return;
    shown = true;

    local player = GetPlayerFromUserID(params.userid);
    if (player == null) return;

    local msg = ReadManifestOrFallback();
    ClientPrint(player, 3, msg);        // 3 = HUD_PRINTTALK (chat area)
    ClientPrint(player, 4, msg);        // 4 = HUD_PRINTCENTER (center for 5s)
}

function ReadManifestOrFallback()
{
    // VScript's FileToString is sandboxed to scripts/vscripts/. Manifest lives
    // outside that path, so we rely on the extractor writing a stub into
    // scripts/vscripts/pvz_gw2_manifest.nut with a `MANIFEST_COUNT` global.
    try {
        IncludeScript("pvz_gw2_manifest");   // sets ::MANIFEST_COUNT
        if (MANIFEST_COUNT > 0) {
            return "PvZ GW2 x TF2 v0.1 - Loaded " + MANIFEST_COUNT + " GW2 sounds from your install.";
        }
    } catch (_) { }
    return "PvZ GW2 x TF2 v0.1 - GW2 install not found. Running with stock TF2 audio. Run bin/pvz_gw2_first_run.exe to retry.";
}

__CollectGameEventCallbacks(this);
