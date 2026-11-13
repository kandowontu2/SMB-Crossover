#requires -Version 7.0
param([switch]$Apply, [switch]$IncludeBuildBinaries)

# Scoped storage cleanup: standard NTFS compression preserves every reader's
# filename and logical bytes. Do not use compact /EXE (WOF reparse points).
$ErrorActionPreference = 'Stop'
$taskRepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).ProviderPath
$taskBuildRoot = (Resolve-Path -LiteralPath (Join-Path $taskRepoRoot 'build')).ProviderPath
$taskAllowedExtensions = @('.dbg')
if ($IncludeBuildBinaries) { $taskAllowedExtensions += @('.o', '.map', '.nes') }
$taskDebugFiles = @(Get-ChildItem -LiteralPath $taskBuildRoot -File -Recurse |
    Where-Object { $taskAllowedExtensions -contains $_.Extension.ToLowerInvariant() })
$taskBeforeFree = (Get-PSDrive C).Free
$taskDebugHashes = @{}
foreach ($taskDebug in $taskDebugFiles) {
    $taskResolvedDebug = (Resolve-Path -LiteralPath $taskDebug.FullName).ProviderPath
    if (-not $taskResolvedDebug.StartsWith($taskBuildRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Debug target escaped build root'
    }
    if (($taskDebug.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'Debug target is a reparse point'
    }
    $taskDebugHashes[$taskResolvedDebug] = (Get-FileHash -LiteralPath $taskResolvedDebug -Algorithm SHA256).Hash
}
if ($Apply) {
    $taskCompactCommand = Join-Path $env:SystemRoot 'System32/compact.exe'
    foreach ($taskDebugPath in $taskDebugHashes.Keys) {
        $taskCompactOutput = & $taskCompactCommand /C /F /I /Q $taskDebugPath 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw ('Filesystem compression failed: ' + $taskDebugPath + ' ' + ($taskCompactOutput -join ' '))
        }
        if ((Get-FileHash -LiteralPath $taskDebugPath -Algorithm SHA256).Hash -ne $taskDebugHashes[$taskDebugPath]) {
            throw 'Debug content changed'
        }
        if (((Get-Item -LiteralPath $taskDebugPath).Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'Unexpected reparse point after compression'
        }
    }
}
[pscustomobject]@{
    Applied = [bool]$Apply
    Extensions = $taskAllowedExtensions
    VerifiedFiles = $taskDebugHashes.Count
    BeforeFreeBytes = $taskBeforeFree
    AfterFreeBytes = (Get-PSDrive C).Free
    LogicalContentsUnchanged = $true
    PathsUnchanged = $true
    NewFiles = 0
} | ConvertTo-Json -Compress
