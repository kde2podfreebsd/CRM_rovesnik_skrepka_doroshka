def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class ContextManager:
    def __init__(self):
        self.context = {}

    def update_bar_id(self, chat_id: int, bar_id: int):
        self.context[chat_id] = bar_id
    
    def update_event_id(self, chat_id: int, event_id: int):
        self.context[chat_id] = event_id

context_manager = ContextManager()