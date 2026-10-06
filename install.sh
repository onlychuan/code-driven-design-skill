#!/usr/bin/env bash
# Install the skill from this repository or an extracted release ZIP.
set -euo pipefail

skill_name='code-driven-design'
installer_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source_root="$installer_root/skills/$skill_name"
destination_root=''
stage_root=''
backup_root=''
force=0

fail() { printf 'Installation failed: %s\n' "$*" >&2; exit 1; }
usage() {
    printf '%s\n' 'Usage: bash install.sh [--dest SKILLS_DIRECTORY] [--force]' \
        '' 'Installs into ~/.agents/skills by default.' \
        '--dest names the parent skills directory, not the skill directory itself.' \
        'For a legacy Codex path, explicitly use --dest "$CODEX_HOME/skills" or --dest "$HOME/.codex/skills".' \
        '--force preserves the previous version in a uniquely named backup directory.'
}
while (($#)); do
    case "$1" in
        --dest|-d) (($# >= 2)) || fail '--dest needs a directory'; destination_root="$2"; shift 2 ;;
        --force|-f) force=1; shift ;;
        --help|-h) usage; exit 0 ;;
        *) fail "Unknown argument: $1 (use --help)" ;;
    esac
done

validate_package() {
    local package_root="$1" resource
    for resource in SKILL.md agents/openai.yaml; do
        [[ -f "$package_root/$resource" && -s "$package_root/$resource" ]] || fail "Incomplete skill package: missing or empty $resource"
    done
    grep -Eq '^name:[[:space:]]*code-driven-design[[:space:]]*$' "$package_root/SKILL.md" || fail 'SKILL.md must declare name: code-driven-design in its YAML frontmatter'
    [[ -z "$(find "$package_root" -type l -print -quit)" ]] || fail 'Skill packages containing symbolic links are not supported'
}

cleanup() {
    if [[ -n "$stage_root" && -d "$stage_root" ]]; then
        local stage_parent stage_leaf
        stage_parent="$(cd -- "$(dirname -- "$stage_root")" && pwd -P)"
        stage_leaf="$(basename -- "$stage_root")"
        [[ "$stage_parent" == "$destination_root" && "$stage_leaf" == ".$skill_name.stage."* && ! -L "$stage_root" ]] || {
            printf 'Refusing unsafe staging cleanup: %s\n' "$stage_root" >&2
            return 1
        }
        rm -rf -- "$stage_root"
    fi
}
trap cleanup EXIT

[[ -d "$source_root" && ! -L "$source_root" ]] || fail "Skill folder not found: $source_root. Extract the full release ZIP before installing."
validate_package "$source_root"
if [[ -z "$destination_root" ]]; then
    [[ -n "${HOME:-}" ]] || fail 'Cannot locate the user profile. Specify --dest.'
    destination_root="$HOME/.agents/skills"
fi
mkdir -p -- "$destination_root"
destination_root="$(cd -- "$destination_root" && pwd -P)"
source_root="$(cd -- "$source_root" && pwd -P)"
case "$destination_root" in
    "$source_root"|"$source_root"/*) fail 'The installation directory cannot be inside the source skill folder' ;;
esac
target_root="$destination_root/$skill_name"
if [[ -e "$target_root" || -L "$target_root" ]]; then
    ((force)) || fail "Already installed: $target_root. Use --force to update and preserve a backup."
    [[ -d "$target_root" && ! -L "$target_root" ]] || fail 'Existing installation must be a regular directory, not a file or symbolic link'
fi

stage_root="$(mktemp -d "$destination_root/.$skill_name.stage.XXXXXX")"
cp -R -- "$source_root/." "$stage_root/"
validate_package "$stage_root"
if [[ -e "$target_root" ]]; then
    while :; do
        backup_root="$destination_root/$skill_name.backup-$(date -u +%Y%m%dT%H%M%SZ)-$$-$RANDOM"
        [[ ! -e "$backup_root" && ! -L "$backup_root" ]] && break
    done
    mv -- "$target_root" "$backup_root"
fi
if ! mv -- "$stage_root" "$target_root"; then
    if [[ -n "$backup_root" && ! -e "$target_root" && ! -L "$target_root" ]]; then
        mv -- "$backup_root" "$target_root" || fail "Update failed; restore the preserved backup: $backup_root"
        backup_root=''
    fi
    fail 'Could not commit the staged installation'
fi
stage_root=''
printf 'Installed: %s\n' "$target_root"
[[ -z "$backup_root" ]] || printf 'Previous version preserved: %s\n' "$backup_root"
printf '%s\n' 'The skill is available on your next Codex turn. No runtime dependencies were installed.'
