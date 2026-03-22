class LoggerSingleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            # Initialize any variables here
            cls._instance.log_count = 0
        return cls._instance

    def log(self, message):
        self.log_count += 1
        print(f"[API LOG #{self.log_count}]: {message}")