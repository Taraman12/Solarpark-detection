from logging.config import fileConfig

import os
from os.path import abspath, dirname, join
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

from app.db.base import Base  # noqa

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_src_path():
    current_path = abspath(__file__)
    src_path = None
    while current_path != "/":
        current_path = dirname(current_path)
        if os.path.exists(join(current_path, "src")):
            src_path = join(current_path, "src")
            return src_path


def get_url():
    """Builds the url for the database connection from .env or docker environment variables"""
    if os.environ.get("DOCKERIZED") == "true":
        USER = os.getenv("POSTGRES_USER", "postgres")
        PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        SERVER = os.getenv("POSTGRES_SERVER", "db")
        DB = os.getenv("POSTGRES_DB", "app")
    else:
        src_path = get_src_path()
        dotenv_path = join(src_path, ".env")
        load_dotenv(dotenv_path)
        USER = os.getenv("POSTGRES_USER", "postgres")
        PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
        SERVER = "localhost"
        DB = os.getenv("POSTGRES_DB", "app")
    return f"postgresql://{USER}:{PASSWORD}@{SERVER}/{DB}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # changed from default
    url = get_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # changed from default
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    # changed to cionfiguration
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
