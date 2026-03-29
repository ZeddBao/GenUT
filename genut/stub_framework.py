"""Stub framework abstractions for UT stub generation."""

from abc import ABC, abstractmethod


class StubFrameworkBase(ABC):
    """Abstract base class for stub frameworks."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Framework identifier name."""
        ...

    @abstractmethod
    def install_stub(self, obj_func: str, stub_func: str) -> str:
        """Return the source line that installs a stub before a test call."""
        ...

    @abstractmethod
    def uninstall_stub(self, obj_func: str) -> str:
        """Return the source line that uninstalls a stub after a test call."""
        ...

    @abstractmethod
    def install_func_ptr_stub(self, var_name: str, stub_func: str, func_type: str) -> str:
        """Return the source line that installs a function pointer stub."""
        ...

    @abstractmethod
    def uninstall_func_ptr_stub(self, var_name: str) -> str:
        """Return the source line that uninstalls a function pointer stub."""
        ...


class MacroStubFramework(StubFrameworkBase):
    """Stub framework using INSTALL_STUB / UNINSTALL_STUB macros."""

    @property
    def name(self) -> str:
        return "macro"

    def install_stub(self, obj_func: str, stub_func: str) -> str:
        return f"    INSTALL_STUB({obj_func}, {stub_func});"

    def uninstall_stub(self, obj_func: str) -> str:
        return f"    UNINSTALL_STUB({obj_func});"

    def install_func_ptr_stub(self, var_name: str, stub_func: str, func_type: str) -> str:
        return f"    INSTALL_FUNC_PTR_STUB({var_name}, {stub_func});"

    def uninstall_func_ptr_stub(self, var_name: str) -> str:
        return f"    UNINSTALL_FUNC_PTR_STUB({var_name});"


_REGISTRY = {
    "macro": MacroStubFramework,
}


def get_stub_framework(name: str) -> StubFrameworkBase:
    """Instantiate a stub framework by name."""
    cls = _REGISTRY.get(name)
    if not cls:
        available = ", ".join(_REGISTRY.keys())
        raise ValueError(f"Unknown stub framework: '{name}'. Available: {available}")
    return cls()
