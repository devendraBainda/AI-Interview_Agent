# New utility for safe threading
import threading
import time
import atexit
from typing import List, Callable

class SafeThreadManager:
    """Thread manager with proper cleanup"""
    
    def __init__(self):
        self.active_threads: List[threading.Thread] = []
        self.shutdown_event = threading.Event()
        atexit.register(self.cleanup_all_threads)
    
    def create_thread(self, target: Callable, args=(), kwargs=None, daemon=True):
        """Create a managed thread"""
        if kwargs is None:
            kwargs = {}
        
        thread = threading.Thread(target=target, args=args, kwargs=kwargs)
        thread.daemon = daemon
        self.active_threads.append(thread)
        return thread
    
    def start_thread(self, target: Callable, args=(), kwargs=None, daemon=True):
        """Create and start a managed thread"""
        thread = self.create_thread(target, args, kwargs, daemon)
        thread.start()
        return thread
    
    def cleanup_all_threads(self, timeout=2.0):
        """Clean up all active threads"""
        if not self.active_threads:
            return
        
        print(f"🧹 Cleaning up {len(self.active_threads)} threads...")
        self.shutdown_event.set()
        
        # Wait for threads to finish
        for thread in self.active_threads:
            if thread.is_alive():
                try:
                    thread.join(timeout=timeout)
                except:
                    pass
        
        # Remove finished threads
        self.active_threads = [t for t in self.active_threads if t.is_alive()]
        
        if self.active_threads:
            print(f"⚠️ {len(self.active_threads)} threads still running")
        else:
            print("✅ All threads cleaned up")
    
    def is_shutdown_requested(self):
        """Check if shutdown was requested"""
        return self.shutdown_event.is_set()

# Global thread manager
thread_manager = SafeThreadManager()
