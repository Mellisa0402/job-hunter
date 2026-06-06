"""
User config loading and validation.
Loads from config/user.yaml with fallback to config/user.example.yaml.
CLI arguments can override config values.
"""

import os
from pathlib import Path

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    import json
    _HAS_YAML = False


# ---- Paths ----
PROJECT_ROOT = Path(os.environ.get('JOB_HUNTER_ROOT', Path(__file__).resolve().parent.parent))
USER_CONFIG_PATH = PROJECT_ROOT / 'config' / 'user.yaml'
EXAMPLE_CONFIG_PATH = PROJECT_ROOT / 'config' / 'user.example.yaml'


# ---- Config loading ----
def _load_yaml(path: Path) -> dict:
    """Load a YAML file. Falls back to JSON parsing if pyyaml is not available."""
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    if _HAS_YAML:
        return _yaml.safe_load(raw) or {}
    return _parse_simple_yaml(raw)


def _parse_simple_yaml(text: str) -> dict:
    """Simple YAML subset parser — handles nested dicts and lists.
    Used as fallback when pyyaml is not installed."""
    result = {}
    stack = [(result, -1)]
    for line in text.split('\n'):
        s = line.rstrip()
        if not s or s.lstrip().startswith('#'):
            continue
        indent = len(line) - len(line.lstrip())
        # Pop stack to correct indentation level
        while stack and indent <= stack[-1][1]:
            stack.pop()
        current, _ = stack[-1]
        stripped = s.lstrip()
        if ':' in stripped:
            key, _, val = stripped.partition(': ')
            key = key.strip().lstrip('- ').strip()
            val = val.strip()
            if not val:
                # Nested dict
                current[key] = {}
                stack.append((current[key], indent))
            elif val.startswith('[') and val.endswith(']'):
                current[key] = [
                    x.strip().strip("'\"")
                    for x in val[1:-1].split(',') if x.strip()
                ]
            else:
                v = val.strip("'\"")
                try:
                    current[key] = int(v)
                except ValueError:
                    try:
                        current[key] = float(v)
                    except ValueError:
                        current[key] = v
        elif stripped.startswith('- '):
            if not isinstance(current, list):
                current = current  # skip non-list items
            else:
                current.append(stripped[2:].strip().strip("'\""))
    return result


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base dict."""
    result = dict(base)
    for key, val in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load_user_config(cli_overrides: dict | None = None) -> dict:
    """Load user config from config/user.yaml, falling back to example.
    CLI overrides are applied on top (non-destructive to nested keys)."""
    if USER_CONFIG_PATH.exists():
        config = _load_yaml(USER_CONFIG_PATH)
    elif EXAMPLE_CONFIG_PATH.exists():
        config = _load_yaml(EXAMPLE_CONFIG_PATH)
    else:
        config = {}

    # Apply CLI overrides
    if cli_overrides:
        for key, val in cli_overrides.items():
            if val is not None:
                config[key] = val

    # Resolve paths relative to project root
    config = _resolve_paths(config)

    return config


def _resolve_paths(config: dict) -> dict:
    """Resolve relative paths in config to absolute."""
    profile = config.get('profile', {})
    resume = profile.get('resume', '')
    if resume and not os.path.isabs(resume):
        config.setdefault('profile', {})['resume'] = str(PROJECT_ROOT / resume)

    output = config.get('output', {})
    out_dir = output.get('dir', './output')
    if not os.path.isabs(out_dir):
        output['dir'] = str(PROJECT_ROOT / out_dir)

    return config


def load_site_config(site_yaml_path: Path) -> dict:
    """Load a single site YAML config file."""
    if not site_yaml_path.exists():
        raise FileNotFoundError(f"Site config not found: {site_yaml_path}")
    return _load_yaml(site_yaml_path)


def load_all_site_configs(sites_dir: Path | None = None) -> list[dict]:
    """Load all site YAML configs from config/sites/ directory."""
    if sites_dir is None:
        sites_dir = PROJECT_ROOT / 'config' / 'sites'
    configs = []
    if sites_dir.is_dir():
        for f in sorted(sites_dir.glob('*.yaml')):
            if f.name.startswith('_') or f.name == 'generic.yaml':
                continue
            try:
                cfg = _load_yaml(f)
                cfg['_source_file'] = str(f)
                configs.append(cfg)
            except Exception as e:
                print(f"[Config] Skipping {f}: {e}")
    return configs


def get_resolve_path(relative_path: str) -> Path:
    """Resolve a path relative to the project root."""
    p = Path(relative_path)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p
