from database.playertable import PlayerTable

# Bits of player.playerrights
ADMIN = 1

NO_RIGHTS = " Nincs jogosultságod ehhez a parancshoz"


def has_rights(did, bits=ADMIN):
    """True if the Discord user has all the given bits in player.playerrights (same rule as !admin)."""
    rights = PlayerTable().rights(did)
    return rights > 0 and rights & bits == bits
