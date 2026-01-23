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
        """
        Create a placeholder object that ignores any constructor arguments.
        
        Accepts arbitrary positional and keyword arguments and performs no initialization.
        """
        pass


class _DummySettings:
    """Provide minimal settings attributes used by OptionsMenu."""
    def __init__(self):
        """
        Initialize default dummy settings used to emulate an application's audio/visual and accessibility options.
        
        Attributes:
            music_on: `True` if background music is enabled by default.
            sound_on: `True` if sound effects are enabled by default.
            music_volume: Default music volume (0.0 to 1.0), set to 0.5.
            sound_volume: Default effects volume (0.0 to 1.0), set to 0.5.
            fullscreen: `False` by default (windowed mode).
            language: Default language code, set to "en".
            show_tts_in_options: `False` by default; whether text-to-speech options are shown.
            tts_voice: Default TTS voice identifier, empty string by default.
        """
        self.music_on = True
        self.sound_on = True
        self.music_volume = 0.5
        self.sound_volume = 0.5
        self.fullscreen = False
        self.language = "en"
        self.show_tts_in_options = False
        self.tts_voice = ""

    def save(self):
        """
        No-op save method for dummy settings used to satisfy callers; performs no action.
        """


class _DummySounds:
    """Minimal sounds object used by OptionsMenu methods."""
    def toggle_music(self, on):
        """
        No-op placeholder that accepts a music-enabled flag.
        
        Parameters:
            on (bool): Indicates whether music should be enabled; the value is ignored.
        """
        _ = on  # Mark parameter as used

    def toggle_sound(self, on):
        """
        No-op handler for enabling or disabling sound effects.
        
        Parameters:
            on (bool): True to enable sound effects, False to disable them. This implementation intentionally performs no action.
        """
        _ = on  # Mark parameter as used

    def set_music_volume(self, vol):
        """
        No-op placeholder that accepts a music volume value and performs no action.
        
        Parameters:
            vol (float|int): Intended music volume value; this implementation ignores the value.
        """
        _ = vol  # Mark parameter as used

    def set_effects_volume(self, vol):
        """
        No-op placeholder that accepts an effects volume value and ignores it.
        
        Parameters:
            vol (float | int): Desired effects volume; the value is accepted but not used.
        """
        _ = vol  # Mark parameter as used


class _DummyAchievementSystem:
    def __init__(self):
        """
        Initialize the dummy achievement system.
        
        Creates an `achievements` attribute as an empty list for storing achievement identifiers or objects used by dummy consumers.
        """
        self.achievements = []


def _build_dummy_for_parameter(name):
    """
    Provide a heuristic dummy value appropriate for a constructor parameter name.
    
    Parameters:
        name (str): The parameter name to analyze.
    
    Returns:
        A dummy value chosen based on the parameter name:
          - 0 for count/number/size-like names
          - "" for name/title/path-like names
          - False for flag/enable/is_-style names
          - _DummySettings() for settings/config-like names
          - _DummySounds() for sound/sounds-like names
          - _DummyAchievementSystem() for achievement-like names
          - _Dummy() otherwise
    """
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
    """
    Create an instance of `cls`, supplying heuristic dummy values for required constructor parameters.
    
    Returns:
        instance: An instantiated object of type `cls`.
    
    Raises:
        Exception: Propagates any exception raised while calling `cls(...)` if instantiation fails.
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
    """
    Discover Menu and UI-like classes defined under the modul package.
    
    Searches importable modules under modul, imports modul.menu to locate the base Menu class, and returns a mapping of discovered class names to their class objects. The result includes:
    - direct subclasses of Menu (excluding the Menu base itself), and
    - classes that expose a callable `draw` method together with either `update` or `activate`, or whose class name ends with "Menu", "Screen", "Dashboard", "Viewer", or "Display".
    
    If modul.menu cannot be imported or does not define a Menu base class, an empty dict is returned.
    
    Returns:
        dict: Mapping from class name (str) to the class object for each discovered menu/UI-like class.
    """
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
    """
    Extract class names used in top-level assignment instantiations in main.py.
    
    Scans the main.py file located next to ROOT for lines that resemble top-level assignments of the form
    `name = ClassName(...)` and collects the `ClassName` tokens that start with an uppercase letter.
    Uses a simple heuristic and ignores read errors.
    
    Returns:
        set: A set of class name strings found in such assignments; empty if none or if main.py is missing/unreadable.
    """
    main_py = os.path.join(os.path.dirname(ROOT), "main.py")
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
    """
    Instantiate provided menu-like classes, detect parent/child relationships among them, render each instance to a PNG, and write a manifest describing the hierarchy.
    
    For each class in `classes`, attempts to construct an instance using heuristics, inspects public attributes and menu item actions to discover child relations, renders the menu to a surface (invoking `activate()` and `draw(surface)` when available), and saves "<ClassName>.png" plus a "menus_manifest.md" file in OUT_DIR.
    
    Parameters:
        classes (dict): Mapping of class name (str) to class object for menu-like classes to process.
    
    Side effects:
        - Writes PNG files named "<ClassName>.png" and a "menus_manifest.md" file into OUT_DIR.
        - Logs instantiation, rendering, and I/O errors and warnings.
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
    """
    Initialize the SDL environment, discover menu classes in the modul package, and produce screenshots and a manifest for each discovered menu.
    
    This function initializes pygame, collects menu-like classes, logs and exits if none are found, and invokes the rendering and manifest generation process for the discovered classes.
    """
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