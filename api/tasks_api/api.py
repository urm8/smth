from ninja import NinjaAPI

import tasks.api

from .settings import VERSION

# assume auth is not required in current case
api = NinjaAPI(title="Tasks API", version=VERSION)
api.add_router("tasks", tasks.api.router)
