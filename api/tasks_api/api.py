from ninja import NinjaAPI

import tasks.api

api = NinjaAPI()
api.add_router("tasks", tasks.api.router)
