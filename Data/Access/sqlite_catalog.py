# sqlite_catalog.py: Compatibility re-export for the SQLite league/fixture catalog.
# Part of LeoBook Data — Access Layer
#
# Canonical implementation and RULEBOOK contract: use ``Data.Access.league_db`` for new code.
# This module exists so tooling/docs can refer to a SQLite-specific catalog name without
# duplicating logic.

from Data.Access.league_db import *  # noqa: F403
