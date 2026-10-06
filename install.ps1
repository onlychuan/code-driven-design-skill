<#
.SYNOPSIS
Installs the locally packaged code-driven-design skill into Codex.
.EXAMPLE
.\install.ps1
.EXAMPLE
.\install.ps1 -Destination 'D:\Codex Skills' -Force
#>
[CmdletBinding()]
param(
    [string]$Destination = '',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$skillName = 'code-driven-design'
$stageRoot = $null
$destinationRoot = $null
$backupRoot = $null
$backupParent = $null
$installationParent = $null
$targetRoot = $null

function Assert-SkillPackage {
    param([Parameter(Mandatory = $true)][string]$PackageRoot)
    $requiredPaths = @('SKILL.md', 'agents/openai.yaml')
    foreach ($relativePath in $requiredPaths) {
        $resourcePath = Join-Path -Path $PackageRoot -ChildPath $relativePath
        if (-not (Test-Path -LiteralPath $resourcePath -PathType Leaf)) {
            throw "Incomplete skill package: missing $relativePath"
        }
        if ((Get-Item -LiteralPath $resourcePath).Length -eq 0) {
            throw "Incomplete skill package: empty $relativePath"
        }
    }
    $packageItem = Get-Item -LiteralPath $PackageRoot -Force
    if (($packageItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'The skill folder cannot be a symbolic link or junction.'
    }
    $skillText = Get-Content -LiteralPath (Join-Path $PackageRoot 'SKILL.md') -Raw -Encoding UTF8
    if ($skillText -notmatch '(?m)^name:\s*code-driven-design\s*$') {
        throw 'SKILL.md must declare name: code-driven-design in its YAML frontmatter.'
    }
    $links = Get-ChildItem -LiteralPath $PackageRoot -Recurse -Force |
        Where-Object { ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 }
    if ($links) {
        throw 'Skill packages containing symbolic links or junctions are not supported.'
    }
}

function Assert-DirectChild {
    param([string]$Candidate, [string]$Parent, [string]$ExpectedName)
    $candidateFull = [IO.Path]::GetFullPath($Candidate)
    $parentFull = [IO.Path]::GetFullPath($Parent)
    if ($parentFull.Length -gt [IO.Path]::GetPathRoot($parentFull).Length) {
        $parentFull = $parentFull.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    }
    $expectedFull = [IO.Path]::GetFullPath((Join-Path -Path $parentFull -ChildPath $ExpectedName))
    if (-not [string]::Equals($candidateFull, $expectedFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Unsafe path refused: $candidateFull"
    }
    $candidateParent = [IO.Path]::GetDirectoryName($candidateFull)
    if (-not [string]::Equals($candidateParent, $parentFull, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the installation directory: $candidateFull"
    }
}

function Remove-InstallerStage {
    if ($script:stageRoot -and (Test-Path -LiteralPath $script:stageRoot)) {
        $stageName = [IO.Path]::GetFileName($script:stageRoot)
        if (-not $stageName.StartsWith(".$skillName.stage-", [StringComparison]::Ordinal)) {
            throw 'Refusing cleanup of a directory not created by this installer.'
        }
        Assert-DirectChild -Candidate $script:stageRoot -Parent $script:destinationRoot -ExpectedName $stageName
        $stageItem = Get-Item -LiteralPath $script:stageRoot -Force
        if (($stageItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw 'Refusing recursive cleanup of a symbolic link or junction.'
        }
        Remove-Item -LiteralPath $script:stageRoot -Recurse -Force
    }
}

function Assert-BackupParent {
    Assert-DirectChild -Candidate $script:backupParent -Parent $script:installationParent -ExpectedName ".$skillName-backups"
    if (-not (Test-Path -LiteralPath $script:backupParent -PathType Container)) {
        throw 'Backup location must be a regular directory outside the skills directory.'
    }
    $backupParentItem = Get-Item -LiteralPath $script:backupParent -Force
    if (($backupParentItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'Backup directory cannot be a symbolic link or junction.'
    }
}

try {
    $sourceRoot = [IO.Path]::GetFullPath((Join-Path -Path $PSScriptRoot -ChildPath "skills\$skillName"))
    if (-not (Test-Path -LiteralPath $sourceRoot -PathType Container)) {
        throw "Skill folder not found: $sourceRoot. Extract the full release ZIP before installing."
    }
    Assert-SkillPackage -PackageRoot $sourceRoot

    if ([string]::IsNullOrWhiteSpace($Destination)) {
        $userProfilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
        if ([string]::IsNullOrWhiteSpace($userProfilePath)) {
            throw 'Cannot locate the user profile. Specify -Destination with a skills directory.'
        }
        $Destination = Join-Path -Path $userProfilePath -ChildPath '.agents\skills'
    }
    $destinationRoot = [IO.Path]::GetFullPath($Destination)
    New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
    $destinationRoot = (Resolve-Path -LiteralPath $destinationRoot).ProviderPath
    $sourcePrefix = $sourceRoot.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
    if ([string]::Equals($destinationRoot, $sourceRoot, [StringComparison]::OrdinalIgnoreCase) -or $destinationRoot.StartsWith($sourcePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'The installation directory cannot be inside the source skill folder.'
    }
    $targetRoot = Join-Path -Path $destinationRoot -ChildPath $skillName
    Assert-DirectChild -Candidate $targetRoot -Parent $destinationRoot -ExpectedName $skillName

    if (Test-Path -LiteralPath $targetRoot) {
        if (-not $Force) {
            throw "Already installed: $targetRoot. Use -Force to update and preserve a backup."
        }
        $targetItem = Get-Item -LiteralPath $targetRoot -Force
        if (-not $targetItem.PSIsContainer -or (($targetItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw 'Existing installation must be a regular directory, not a file, symbolic link, or junction.'
        }
        $installationParent = [IO.Path]::GetDirectoryName($destinationRoot.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar))
        if ([string]::IsNullOrWhiteSpace($installationParent)) {
            throw 'The installation directory needs a parent directory for external backups.'
        }
        $backupParent = [IO.Path]::GetFullPath((Join-Path -Path $installationParent -ChildPath ".$skillName-backups"))
        Assert-DirectChild -Candidate $backupParent -Parent $installationParent -ExpectedName ".$skillName-backups"
        if (Test-Path -LiteralPath $backupParent) {
            Assert-BackupParent
        }
        else {
            New-Item -ItemType Directory -Path $backupParent | Out-Null
            Assert-BackupParent
        }
    }

    $stageName = ".$skillName.stage-$([Guid]::NewGuid().ToString('N'))"
    $stageRoot = Join-Path -Path $destinationRoot -ChildPath $stageName
    Assert-DirectChild -Candidate $stageRoot -Parent $destinationRoot -ExpectedName $stageName
    New-Item -ItemType Directory -Path $stageRoot | Out-Null
    foreach ($sourceItem in (Get-ChildItem -LiteralPath $sourceRoot -Force)) {
        Copy-Item -LiteralPath $sourceItem.FullName -Destination $stageRoot -Recurse -Force
    }
    Assert-SkillPackage -PackageRoot $stageRoot

    if (Test-Path -LiteralPath $targetRoot) {
        $backupName = "$skillName.backup-$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ'))-$([Guid]::NewGuid().ToString('N').Substring(0, 8))"
        $backupRoot = [IO.Path]::GetFullPath((Join-Path -Path $backupParent -ChildPath $backupName))
        Assert-DirectChild -Candidate $targetRoot -Parent $destinationRoot -ExpectedName $skillName
        Assert-BackupParent
        Assert-DirectChild -Candidate $backupRoot -Parent $backupParent -ExpectedName $backupName
        [IO.Directory]::Move($targetRoot, $backupRoot)
    }
    try {
        Assert-DirectChild -Candidate $stageRoot -Parent $destinationRoot -ExpectedName $stageName
        Assert-DirectChild -Candidate $targetRoot -Parent $destinationRoot -ExpectedName $skillName
        [IO.Directory]::Move($stageRoot, $targetRoot)
        $stageRoot = $null
    }
    catch {
        if ($backupRoot -and -not (Test-Path -LiteralPath $targetRoot)) {
            Assert-BackupParent
            Assert-DirectChild -Candidate $backupRoot -Parent $backupParent -ExpectedName ([IO.Path]::GetFileName($backupRoot))
            Assert-DirectChild -Candidate $targetRoot -Parent $destinationRoot -ExpectedName $skillName
            [IO.Directory]::Move($backupRoot, $targetRoot)
            $backupRoot = $null
        }
        throw
    }

    Write-Output "Installed: $targetRoot"
    if ($backupRoot) { Write-Output "Previous version preserved: $backupRoot" }
    Write-Output 'The skill is available on your next Codex turn. No runtime dependencies were installed.'
    exit 0
}
catch {
    [Console]::Error.WriteLine("Installation failed: $($_.Exception.Message)")
    if ($backupRoot -and (Test-Path -LiteralPath $backupRoot)) {
        [Console]::Error.WriteLine("Previous version preserved: $backupRoot")
    }
    exit 1
}
finally {
    Remove-InstallerStage
}
