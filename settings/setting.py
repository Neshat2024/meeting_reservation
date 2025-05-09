from settings.load_env import load_env_variables

DEFAULT_SETTINGS = {
    "ADMINS": "",
    "MANAGERS": "",
    "TOKEN_RESERVE": "",
    "TOKEN_LOGGING": "",
    "LOG_CHANNEL_ID": "",
    "BACKUP_CHANNEL_ID": "",
    "CLOCKIFY_LOG_DIR": "",
    "POSTGRES_DB": "",
    "POSTGRES_USER": "",
    "POSTGRES_PASSWORD": "",
    "DATABASE_URL_RESERVE": "",
    "PROXY_HOST": "",
    "PROXY_PORT": "",
}


class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, env_name: str):
        """Initialize settings with environment variables."""
        if not self._initialized:
            env_vars = load_env_variables(env_name)
            self._settings = {**DEFAULT_SETTINGS, **env_vars}

            # Convert to instance attributes
            for key, value in self._settings.items():
                setattr(self, key, value)
            self._initialized = True

    def reload(self, env_name: str):
        """Reload settings with new environment file"""
        env_vars = load_env_variables(env_name)
        self._settings = {**DEFAULT_SETTINGS, **env_vars}
        for key, value in self._settings.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        if not getattr(self, "_initialized", False):
            raise RuntimeError("Settings not initialized")
        return self._settings[key]

    def get(self, key, default=None):
        if not getattr(self, "_initialized", False):
            raise RuntimeError("Settings not initialized")
        return self._settings.get(key, default)


# Create uninitialized instance
settings = Settings()
