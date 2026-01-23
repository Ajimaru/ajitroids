#!/usr/bin/env python3
"""Generate screenshots for all detected menu classes.

This development helper will scan `modul.menu` for classes that subclass
`Menu`, try to instantiate them, render them on a dummy SDL surface and
write a PNG into the repository `.logs/` directory. It skips classes whose
constructors require parameters and logs useful diagnostics.

Usage:
    python .development/generate_menu_screenshots.py

Output:
    .logs/<MenuClassName>.png
"""
import os
import inspect
import logging
import pkgutil
import importlib
import pygame
import modul

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

try:
    from modul.constants import SCREEN_WIDTH, SCREEN_HEIGHT
except ImportError:
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(ROOT, ".logs")
OUT_DIR = os.path.join(LOG_DIR, "menu_screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_menu_screenshots")


class _Dummy:
    """Lightweight dummy object used to satisfy constructor parameters."""
    def __init__(self, *a, **k):
        pass


class _DummySettings:
    """Provide minimal settings attributes used by OptionsMenu."""
    def __init__(self):
        self.music_on = True
        self.sound_on = True
        self.music_volume = 0.5
        self.sound_volume = 0.5
        self.fullscreen = False
        self.language = "en"
        self.show_tts_in_options = False
        self.tts_voice = ""

    def save(self):
        """Dummy save method."""


class _DummySounds:
    """Minimal sounds object used by OptionsMenu methods."""
    def toggle_music(self, on):
        """Dummy toggle_music method."""
        _ = on  # Mark parameter as used

    def toggle_sound(self, on):
        """Dummy toggle_sound method."""
        _ = on  # Mark parameter as used

    def set_music_volume(self, vol):
        """Dummy set_music_volume method."""
        _ = vol  # Mark parameter as used

    def set_effects_volume(self, vol):
        """Dummy set_effects_volume method."""
        _ = vol  # Mark parameter as used


class _DummyAchievementSystem:
    def __init__(self):
        self.achievements = []


def _build_dummy_for_parameter(name):
    """Return a heuristic dummy value for a constructor parameter name."""
    lname = name.lower()
    if "count" in lname or "num" in lname or "size" in lname:
        return 0
    if "name" in lname or "title" in lname or "path" in lname:
        return ""
    if "flag" in lname or "enable" in lname or lname.startswith("is_"):
        return False
    if "settings" in lname or "config" in lname:
        return _DummySettings()
    if "sound" in lname or "sounds" in lname:
        return _DummySounds()
    if "achievement" in lname:
        return _DummyAchievementSystem()
    return _Dummy()


def instantiate_with_dummies(cls):
    """Try to instantiate `cls` by providing simple dummy args when required.

    Returns the instance or raises the original exception if instantiation
    fails irrecoverably.
    """
    sig = None
    try:
        sig = inspect.signature(cls)
    except (TypeError, ValueError):
        return cls()

    params = list(sig.parameters.values())
    # drop 'self' for bound methods / constructors
    args = []
    for p in params:
        if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        if p.name == "self":
            continue
        if p.default is not inspect.Parameter.empty:
            # has default
            continue
        args.append(_build_dummy_for_parameter(p.name))

    return cls(*args)


def find_modul_modules():
    """Yield all importable modules under the `modul` package."""
    try:
        pkg_path = getattr(modul, "__path__", None)
    except ImportError:
        return
    if not pkg_path:
        return
    for _, name, _ in pkgutil.walk_packages(pkg_path, modul.__name__ + "."):
        try:
            yield importlib.import_module(name)
        except ImportError:
            logger.debug("Failed to import %s", name)


def collect_menu_classes():
    """Return dict mapping class name -> class object for all Menu subclasses found."""
    classes = {}
    # first import modul.menu to get base Menu class
    try:
        menu_mod = importlib.import_module("modul.menu")
    except ImportError:
        logger.error("Could not import modul.menu")
        return classes

    menu_base = getattr(menu_mod, "Menu", None)
    if menu_base is None:
        logger.error("No Menu base class in modul.menu")
        return classes

    # iterate all modules under modul
    for module in find_modul_modules():
        for _, cls in inspect.getmembers(module, inspect.isclass):
            try:
                # include direct Menu subclasses
                if issubclass(cls, menu_base) and cls is not menu_base:
                    classes[cls.__name__] = cls
                    continue
            except TypeError:
                pass
            # also include UI-like classes that aren't Menu subclasses but
            # implement a draw/update or draw/activate API, or have UI-related names
            try:
                has_draw = callable(getattr(cls, "draw", None))
                has_update = callable(getattr(cls, "update", None))
                has_activate = callable(getattr(cls, "activate", None))
                name = cls.__name__
                if (
                    (has_draw and (has_update or has_activate))
                    or name.endswith(
                        ("Menu", "Screen", "Dashboard", "Viewer", "Display")
                    )
                ):
                    classes[name] = cls
            except (AttributeError, TypeError):
                continue
    return classes


def _parse_main_instantiations():
    """Parse `main.py` for top-level instantiations like `x = ClassName(...)`.

    Returns a set of class names referenced in assignments.
    """
    main_py = os.path.join(ROOT, "main.py")
    if not os.path.exists(main_py):
        return set()
    names = set()
    try:
        with open(main_py, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                # simple heuristic: look for `name = ClassName(`
                if "=" in line and "(" in line and line.endswith(")") or "(" in line:
                    parts = line.split("=")
                    if len(parts) >= 2:
                        rhs = parts[1].strip()
                        # take token before first '('
                        token = rhs.split("(", 1)[0].strip()
                        if token and token[0].isupper():
                            # likely a class name
                            names.add(token.split()[0])
    except (OSError, UnicodeDecodeError):
        pass
    return names


def build_hierarchy_and_render(classes):
    """Instantiate menu classes, detect child relations and render screenshots.

    Creates a directory structure in `.logs/` following parent/child relationships.
    """
    instances = {}
    children = {name: set() for name in classes}
    parents = {}

    # instantiate with dummies where needed
    for name, cls in classes.items():
        try:
            inst = instantiate_with_dummies(cls)
            instances[name] = inst
        except (TypeError, ValueError, AttributeError) as e:
            logger.warning("Could not instantiate %s: %s", name, e)

    # detect relations from attributes and MenuItem.action
    for name, inst in instances.items():
        # attributes referencing Menu subclasses or instances
        for attr in dir(inst):
            if attr.startswith("_"):
                continue
            try:
                val = getattr(inst, attr)
            except (AttributeError, TypeError):
                continue
            if val is None:
                continue
            # class reference
            if inspect.isclass(val) and val.__name__ in classes:
                children[name].add(val.__name__)
                parents[val.__name__] = name
            # instance reference
            if type(val).__name__ in classes and isinstance(val, tuple(classes.values())):
                child_name = type(val).__name__
                children[name].add(child_name)
                parents[child_name] = name

        # check menu items
        for it in getattr(inst, "items", []) or []:
            action = getattr(it, "action", None)
            if inspect.isclass(action) and action.__name__ in classes:
                children[name].add(action.__name__)
                parents[action.__name__] = name

    # render and save following hierarchy: create dirs for root menus
    rendered = set()

    # Render all classes into a flat output directory and record hierarchy
    for name in sorted(classes):
        inst = instances.get(name)
        out = os.path.join(OUT_DIR, f"{name}.png")
        try:
            surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.fill((0, 0, 0))
            if inst is not None:
                if hasattr(inst, "activate") and callable(getattr(inst, "activate")):
                    try:
                        inst.activate()
                    except (AttributeError, TypeError) as e:
                        logger.warning("Activate failed for %s: %s", name, e)
                if hasattr(inst, "draw") and callable(getattr(inst, "draw")):
                    try:
                        inst.draw(surface)
                    except (AttributeError, TypeError) as e:
                        logger.warning("Draw failed for %s: %s", name, e)
            pygame.image.save(surface, out)
            logger.info("Wrote %s", out)
            rendered.add(name)
        except (pygame.error, OSError) as e:
            logger.exception("Failed rendering %s: %s", name, e)

    # write manifest into OUT_DIR
    manifest_path = os.path.join(OUT_DIR, "menus_manifest.md")
    try:
        with open(manifest_path, "w", encoding="utf-8") as mf:
            mf.write("# Menu Screenshots Manifest\n\n")
            mf.write("Generated by .development/generate_menu_screenshots.py\n\n")
            for name in sorted(classes):
                file_rel = f"{name}.png"
                parent = parents.get(name, None)
                children_list = sorted(children.get(name, []))
                mf.write(f"- {name}: {file_rel}\n")
                mf.write(f"  - parent: {parent}\n")
                mf.write(f"  - children: {children_list}\n")
    except OSError as e:
        logger.warning("Could not write manifest: %s", e)


def main():
    """Initialize pygame and generate menu screenshots."""
    try:
        pygame.init()
    except pygame.error as e:
        logger.warning("pygame.init() failed: %s", e)

    classes = collect_menu_classes()
    if not classes:
        logger.error("No menu classes found.")
        return
    build_hierarchy_and_render(classes)


if __name__ == "__main__":
    main()
