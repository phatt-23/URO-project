from __future__ import annotations
from functools import wraps
from typing import Type
from lib.logger import log

######################################################
#### Ignore LSP errors ###############################
######################################################

def _component_default_manager_settings(cls: "Type[Component]") -> "Type[Component]":
    pack = cls.pack
    grid = cls.grid

    @wraps(cls.pack)
    def new_pack(self, *args, **kwargs):
        self.pack_configure(fill="both", expand=True, padx=10, pady=10)
        pack(self, *args, **kwargs)

    @wraps(cls.grid)
    def new_grid(self, *args, **kwargs):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_configure(row=0, column=0, sticky="nsew", padx=10, pady=10)
        grid(self, *args, **kwargs)

    cls.pack = new_pack
    cls.grid = new_grid
    return cls


def _render_after_init(cls: "Type[Component]") -> "Type[Component]":
    init = cls.__init__
    render = cls.render

    @wraps(cls.__init__)
    def new_init(self, *args, **kw):
        init(self, *args, **kw)
        render(self)

    @wraps(cls.render)
    def new_render(self):
        render(self)

    cls.__init__ = new_init
    cls.render = new_render

    return cls



class ComponentMeta(type):
    def __new__(cls, name, bases, namespace):
        """
        Upon creating the Component class and its derivatives, 
        this method will apply modifications in form of decorators.
        """

        def check_bases(bases):
            for base in bases:
                if base.__name__ == "Component":
                    return True
                return check_bases(base.__bases__)
            return False
        
        is_component = True if name == "Component" else check_bases(bases)

        assert is_component, f"This meta class works only for Component and its derivatives. Instead got class with bases: {bases}!"

        log.debug("Creating component:", name)
        
        instance = super().__new__(cls, name, bases, namespace)

        log.debug("Class name:", name)
        log.debug("Created instance:", instance)

        instance = _component_default_manager_settings(instance)
        instance = _render_after_init(instance)

        return instance

    def __init__(cls, name, bases, namespace):
        """
        Overrides __init__ of the Component class and its derived subclasses alike.
        """

        init = cls.__init__

        @wraps(cls.__init__)
        def new_init(self, *args, **kw):
            log.debug(f"INFO: Initializing {type(self)}")
            log.debug(type(self))
            log.debug("INFO: Done Initializing.")
            init(self, *args, **kw)
        
        cls.__init__ = new_init


