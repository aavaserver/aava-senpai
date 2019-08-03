import os


def memory_usage_psutil():
    # return the memory usage in MB
    import psutil
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss
    return mem


def current_processes_psutil():
    import psutil
    process = psutil.Process(os.getpid())
    threads = process.threads()
    return threads