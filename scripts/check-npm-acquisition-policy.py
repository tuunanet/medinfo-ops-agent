#!/usr/bin/env python3
# story: e08s01
"""Reject npm dependency sources outside the reviewed public registry boundary."""

import argparse
import base64
import binascii
import json
import sys
from pathlib import Path

OFFICIAL_REGISTRY = "https://registry.npmjs.org/"
DEPENDENCY_FIELDS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)
FILE_SUFFIXES = (".tgz", ".tar", ".tar.gz")
GIT_PREFIXES = (
    "git+",
    "git://",
    "github:",
    "gist:",
    "gitlab:",
    "bitbucket:",
    "ssh://",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    root = parser.parse_args().root.resolve()
    errors = validate_project(root)
    if errors:
        print("\n".join(f"error: {error}" for error in errors), file=sys.stderr)
        return 1
    print("npm acquisition policy passed")
    return 0


def validate_project(root: Path) -> list[str]:
    try:
        root_manifest = load_object(root / "package.json")
        lockfile = load_object(root / "package-lock.json")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return [str(error)]

    workspace_packages, workspace_errors = find_workspace_packages(root, root_manifest)
    project_roots = (root, *(root / path for path in workspace_packages))
    shrinkwrap_errors = [
        f"{(project_root / 'npm-shrinkwrap.json').relative_to(root).as_posix()} is not permitted"
        for project_root in project_roots
        if (project_root / "npm-shrinkwrap.json").exists()
    ]
    return [
        *shrinkwrap_errors,
        *workspace_errors,
        *validate_manifest_sources(root, root_manifest, workspace_packages),
        *validate_lockfile_sources(lockfile, workspace_packages),
    ]


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def find_workspace_packages(
    root: Path,
    root_manifest: dict[str, object],
) -> tuple[dict[str, str], list[str]]:
    workspaces = root_manifest.get("workspaces", [])
    patterns = (
        workspaces.get("packages", []) if isinstance(workspaces, dict) else workspaces
    )
    if not isinstance(patterns, list) or not all(
        isinstance(item, str) for item in patterns
    ):
        return {}, ["package.json workspaces must be a list of paths"]

    workspace_packages = {}
    errors = []
    for pattern in patterns:
        for workspace_path in root.glob(pattern):
            if (
                not workspace_path.is_dir()
                or not workspace_path.resolve().is_relative_to(root)
            ):
                continue
            try:
                workspace_manifest = load_object(workspace_path / "package.json")
                name = workspace_manifest.get("name")
                if not isinstance(name, str) or not name:
                    raise ValueError("workspace package name is required")
            except (OSError, ValueError, json.JSONDecodeError) as error:
                errors.append(f"{workspace_path.relative_to(root)}: {error}")
                continue
            workspace_packages[workspace_path.relative_to(root).as_posix()] = name
    return workspace_packages, errors


def validate_manifest_sources(
    root: Path,
    root_manifest: dict[str, object],
    workspace_packages: dict[str, str],
) -> list[str]:
    manifests = [("package.json", root_manifest)]
    for workspace_path in workspace_packages:
        manifests.append(
            (
                f"{workspace_path}/package.json",
                load_object(root / workspace_path / "package.json"),
            ),
        )

    errors = []
    for path, manifest in manifests:
        specifications, shape_errors = manifest_specifications(manifest)
        errors.extend(f"{path}: {error}" for error in shape_errors)
        errors.extend(
            f"{path}: {source_type} {field} source {name} is not permitted"
            for field, name, specification in specifications
            if (source_type := source_type_for(specification)) is not None
        )
    return errors


def manifest_specifications(
    manifest: dict[str, object],
) -> tuple[list[tuple[str, str, str]], list[str]]:
    specifications = []
    errors = []
    for field in DEPENDENCY_FIELDS:
        if field not in manifest:
            continue
        dependencies = manifest[field]
        if not isinstance(dependencies, dict):
            errors.append(f"{field} must be an object")
            continue
        for name, specification in dependencies.items():
            if not isinstance(name, str) or not isinstance(specification, str):
                errors.append(
                    f"{field} dependency {name} must have a string specification"
                )
            else:
                specifications.append((field, name, specification))

    if "overrides" in manifest:
        override_specifications, override_errors = override_values(
            manifest["overrides"]
        )
        specifications.extend(
            ("overrides", "override", value) for value in override_specifications
        )
        errors.extend(override_errors)
    return specifications, errors


def override_values(
    value: object, path: str = "overrides"
) -> tuple[list[str], list[str]]:
    if isinstance(value, str):
        return [value], []
    if not isinstance(value, dict):
        return [], [f"{path} must contain strings or objects"]

    specifications = []
    errors = []
    for name, nested_value in value.items():
        nested_specs, nested_errors = override_values(nested_value, f"{path}.{name}")
        specifications.extend(nested_specs)
        errors.extend(nested_errors)
    return specifications, errors


def source_type_for(specification: str) -> str | None:
    normalized = specification.lower()
    if normalized.startswith("npm:"):
        return None
    if normalized.startswith("file:"):
        return "file" if normalized.endswith(FILE_SUFFIXES) else "directory"
    if normalized.startswith(GIT_PREFIXES) or normalized.startswith("git@"):
        return "git"
    if normalized.startswith(("http:", "https:")):
        return "remote"
    if len(normalized) > 1 and normalized[0].isalpha() and normalized[1] == ":":
        return "directory"
    if normalized in {".", ".."} or normalized.startswith(
        ("./", ".\\", "../", "..\\", "/", "\\", "~/", "~\\", "workspace:"),
    ):
        return "directory"
    _, separator, scp_path = normalized.partition(":")
    if separator and scp_path:
        return "git"
    if normalized.endswith(FILE_SUFFIXES):
        return "file"
    if "/" in normalized:
        return "git"
    return None


def validate_lockfile_sources(
    lockfile: dict[str, object],
    workspace_packages: dict[str, str],
) -> list[str]:
    if lockfile.get("lockfileVersion") != 3:
        return ["package-lock.json requires lockfileVersion 3"]
    packages = lockfile.get("packages")
    if not isinstance(packages, dict):
        return ["package-lock.json packages must be an object"]

    errors = []
    for package_path, package in packages.items():
        if not isinstance(package_path, str) or not isinstance(package, dict):
            errors.append(
                f"package-lock.json {package_path} has an invalid package record"
            )
        elif package_path in workspace_packages:
            errors.extend(workspace_target_errors(package_path, package))
        elif package_path:
            errors.extend(
                lockfile_package_errors(package_path, package, workspace_packages)
            )
    errors.extend(exact_workspace_link_errors(packages, workspace_packages))
    return errors


def workspace_target_errors(
    workspace_path: str, package: dict[str, object]
) -> list[str]:
    if "link" in package:
        return [
            f"package-lock.json {workspace_path} has an invalid exact workspace link target"
        ]
    return []


def exact_workspace_link_errors(
    packages: dict[str, object], workspace_packages: dict[str, str]
) -> list[str]:
    errors = []
    for workspace_path, workspace_name in workspace_packages.items():
        lock_path = f"node_modules/{workspace_name}"
        package = packages.get(lock_path)
        if (
            not isinstance(package, dict)
            or package.get("link") is not True
            or package.get("resolved") != workspace_path
        ):
            errors.append(
                f"package-lock.json must contain an exact workspace link for {workspace_path}"
            )
    return errors


def lockfile_package_errors(
    package_path: str,
    package: dict[str, object],
    workspace_packages: dict[str, str],
) -> list[str]:
    resolved = package.get("resolved")
    if "link" in package:
        if package["link"] is not True:
            return [
                f"package-lock.json {package_path} has an invalid link value and lacks an npm-registry resolution"
            ]
        expected_name = (
            workspace_packages.get(resolved) if isinstance(resolved, str) else None
        )
        if expected_name and package_path == f"node_modules/{expected_name}":
            return []
        return [f"package-lock.json {package_path} has an unreviewed workspace link"]
    if not isinstance(resolved, str):
        return [f"package-lock.json {package_path} lacks an npm-registry resolution"]

    errors = []
    if not resolved.startswith(OFFICIAL_REGISTRY):
        errors.append(f"package-lock.json {package_path} has a non-registry source")
    integrity = package.get("integrity")
    if not has_valid_sha512_integrity(integrity):
        errors.append(f"package-lock.json {package_path} lacks SHA-512 integrity")
    return errors


def has_valid_sha512_integrity(integrity: object) -> bool:
    if not isinstance(integrity, str) or not integrity.startswith("sha512-"):
        return False
    try:
        digest = base64.b64decode(integrity.removeprefix("sha512-"), validate=True)
    except ValueError, binascii.Error:
        return False
    return len(digest) == 64


if __name__ == "__main__":
    raise SystemExit(main())
