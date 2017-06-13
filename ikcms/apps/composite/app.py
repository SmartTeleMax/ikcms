import ikcms.apps.base


class App(ikcms.apps.base.App):

    components = []

    def __init__(self, cfg):
        self.cfg = cfg
        self.cfg.config_uid()
        self.cfg.config_logging()
        self.env_class = self.get_env_class()
        self.components = [
            component.create(self) for component in self.components]
        for component in self.components:
            component.env_class(self.env_class)
        self.handler = self.get_handler()
        self.root = self.get_root()

    def get_env_class(self):
        from .env import Environment
        return Environment

    def get_handler(self):
        raise NotImplementedError
