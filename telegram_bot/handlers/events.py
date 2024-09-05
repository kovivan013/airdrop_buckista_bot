from config import dp
from . import debug_handlers
from . import main_handlers
from . import admin_handlers

def register_events():
    admin_handlers.register(dp)
    main_handlers.register(dp)
