"""Exercise local installers in isolated directories; uses only the stdlib.

Run with: python -m unittest discover -s tests -p test_installers.py -v
PowerShell and Bash tests are skipped when that shell is unavailable.
"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "code-driven-design"


def available_shells():
    result = []
    for name in ("pwsh", "powershell"):
        executable = shutil.which(name)
        if executable:
            result.append((name, executable))
    # Windows' bash.exe is often only a WSL launcher with no installed distro.
    # Git Bash accepts forward-slash Windows paths and can run the POSIX suite.
    if os.name == "nt":
        git_bash = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Git" / "bin" / "bash.exe"
        if git_bash.is_file():
            result.append(("bash", str(git_bash)))
    else:
        executable = shutil.which("bash")
        if executable:
            result.append(("bash", executable))
    return result


SHELLS = available_shells()


@unittest.skipUnless(SHELLS, "No supported shell is installed")
class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="design-skill-installers-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "Release with spaces 中文"
        self.package.mkdir()
        for filename in ("install.ps1", "install.cmd", "install.sh"):
            shutil.copyfile(REPOSITORY_ROOT / filename, self.package / filename)
        skill = self.package / "skills" / SKILL_NAME
        (skill / "agents").mkdir(parents=True)
        (skill / "references").mkdir()
        (skill / "SKILL.md").write_text(
            "---\nname: code-driven-design\ndescription: Test fixture\n---\n# Fixture\n",
            encoding="utf-8",
        )
        (skill / "agents" / "openai.yaml").write_text(
            'interface:\n  display_name: "Code Driven Design"\n', encoding="utf-8"
        )
        (skill / "references" / "中文 reference.txt").write_text("reference", encoding="utf-8")
        (skill / ".included-hidden-file").write_text("preserved", encoding="utf-8")
        (self.package / "do-not-install.txt").write_text("outside skill", encoding="utf-8")
        self.source = skill

    def run_installer(self, shell, destination, force=False):
        name, executable = shell
        if name == "bash":
            command = [executable, (self.package / "install.sh").as_posix(), "--dest", destination.as_posix()]
            if force:
                command.append("--force")
        else:
            command = [
                executable,
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(self.package / "install.ps1"),
                "-Destination",
                str(destination),
            ]
            if force:
                command.append("-Force")
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)

    def destination_for(self, shell):
        return self.root / f"Custom skills 中文 {shell[0]}"

    def assert_no_stage(self, destination):
        if destination.exists():
            self.assertEqual(list(destination.glob(f".{SKILL_NAME}.stage*")), [])

    def test_fresh_install_and_copy_scope(self):
        for shell in SHELLS:
            with self.subTest(shell=shell[0]):
                destination = self.destination_for(shell)
                result = self.run_installer(shell, destination)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                target = destination / SKILL_NAME
                self.assertTrue((target / "SKILL.md").is_file())
                self.assertTrue((target / "agents" / "openai.yaml").is_file())
                self.assertEqual((target / "references" / "中文 reference.txt").read_text(encoding="utf-8"), "reference")
                self.assertEqual((target / ".included-hidden-file").read_text(encoding="utf-8"), "preserved")
                self.assertFalse((target / "do-not-install.txt").exists())
                self.assertFalse((target / "install.ps1").exists())
                self.assertEqual(list(destination.glob(f"{SKILL_NAME}.backup-*")), [])
                self.assertIn("next Codex turn", result.stdout)
                self.assert_no_stage(destination)

    def test_existing_install_is_refused_without_changes(self):
        for shell in SHELLS:
            with self.subTest(shell=shell[0]):
                destination = self.destination_for(shell)
                target = destination / SKILL_NAME
                target.mkdir(parents=True)
                sentinel = target / "local-modification.txt"
                sentinel.write_text("do not overwrite", encoding="utf-8")
                result = self.run_installer(shell, destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Already installed", result.stderr)
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not overwrite")
                self.assertFalse((target / "SKILL.md").exists())
                self.assertEqual(list(destination.glob(f"{SKILL_NAME}.backup-*")), [])
                self.assert_no_stage(destination)

    def test_force_update_preserves_unique_backups(self):
        for shell in SHELLS:
            with self.subTest(shell=shell[0]):
                destination = self.destination_for(shell)
                target = destination / SKILL_NAME
                target.mkdir(parents=True)
                (target / "old-only.txt").write_text("original", encoding="utf-8")
                result = self.run_installer(shell, destination, force=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertFalse((target / "old-only.txt").exists())
                first_backups = list(destination.glob(f"{SKILL_NAME}.backup-*"))
                self.assertEqual(len(first_backups), 1)
                self.assertEqual((first_backups[0] / "old-only.txt").read_text(encoding="utf-8"), "original")
                (target / "second-version.txt").write_text("second", encoding="utf-8")
                result = self.run_installer(shell, destination, force=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                all_backups = list(destination.glob(f"{SKILL_NAME}.backup-*"))
                self.assertEqual(len(all_backups), 2)
                self.assertTrue((first_backups[0] / "old-only.txt").is_file())
                second_backup = next(path for path in all_backups if path != first_backups[0])
                self.assertEqual((second_backup / "second-version.txt").read_text(encoding="utf-8"), "second")
                self.assert_no_stage(destination)

    def test_invalid_package_does_not_replace_existing_install(self):
        (self.source / "agents" / "openai.yaml").unlink()
        for shell in SHELLS:
            with self.subTest(shell=shell[0]):
                destination = self.destination_for(shell)
                target = destination / SKILL_NAME
                target.mkdir(parents=True)
                (target / "sentinel.txt").write_text("safe", encoding="utf-8")
                result = self.run_installer(shell, destination, force=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("agents/openai.yaml", result.stderr)
                self.assertEqual((target / "sentinel.txt").read_text(encoding="utf-8"), "safe")
                self.assertEqual(list(destination.glob(f"{SKILL_NAME}.backup-*")), [])
                self.assert_no_stage(destination)

    def test_destination_cannot_be_inside_source(self):
        for shell in SHELLS:
            with self.subTest(shell=shell[0]):
                destination = self.source / f"nested-{shell[0]}"
                result = self.run_installer(shell, destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("inside the source", result.stderr)
                self.assertFalse((destination / SKILL_NAME).exists())
                self.assert_no_stage(destination)

    def test_existing_file_is_refused_even_with_force(self):
        for shell in SHELLS:
            with self.subTest(shell=shell[0]):
                destination = self.destination_for(shell)
                destination.mkdir()
                target = destination / SKILL_NAME
                target.write_text("existing file", encoding="utf-8")
                result = self.run_installer(shell, destination, force=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("regular directory", result.stderr)
                self.assertEqual(target.read_text(encoding="utf-8"), "existing file")
                self.assert_no_stage(destination)

    @unittest.skipUnless(os.name == "nt", "Windows batch wrapper")
    def test_windows_double_click_wrapper_accepts_arguments(self):
        destination = self.root / "Wrapper custom skills 中文"
        # Supply arguments to avoid the pause reserved for interactive double-clicks.
        result = subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", "call", str(self.package / "install.cmd"), "-Destination", str(destination)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((destination / SKILL_NAME / "SKILL.md").is_file())
        self.assert_no_stage(destination)


if __name__ == "__main__":
    unittest.main()
