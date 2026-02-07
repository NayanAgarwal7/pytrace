"""
Minimal production-safe tracer using sys.settrace.
Avoids all common pitfalls: object comparison, repr() calls, importlib crashes.
"""
import sys
import os
from .state import TraceState


class Tracer:
    def __init__(self):
        self.state = TraceState()
        self.target_file = None
        self.target_file_normalized = None
        self.module_started = False
        self.first_line_skipped = False
        
    def should_trace_file(self, filename):
        """Only trace the target file, not stdlib/importlib/runpy."""
        if not filename or not self.target_file_normalized:
            return False
        
        try:
            norm_filename = os.path.normpath(os.path.abspath(filename))
        except (OSError, ValueError):
            return False
            
        return norm_filename == self.target_file_normalized
    
    def trace_dispatch(self, frame, event, arg):
        """Main trace function - called for every traced event."""
        filename = frame.f_code.co_filename
        
        if not self.should_trace_file(filename):
            return None
        
        funcname = frame.f_code.co_name
        lineno = frame.f_lineno
        frame_id = id(frame)
        
        INTERNAL_VARS = {
            '__builtins__', '__cached__', '__doc__', '__file__',
            '__loader__', '__name__', '__package__', '__spec__',
            '__annotations__'
        }
        
        if event == 'call':
            if funcname == '<module>':
                if not self.module_started:
                    self.state.on_call(funcname, 1)
                    self.module_started = True
                    self.first_line_skipped = False
                return self.trace_dispatch
            else:
                self.state.on_call(funcname, lineno)
                self.first_line_skipped = False
            
        elif event == 'line':
            if not self.module_started:
                return self.trace_dispatch
            
            if not self.first_line_skipped:
                self.first_line_skipped = True
                current_vars = set(frame.f_locals.keys()) - INTERNAL_VARS
                if self.state.locals_stack:
                    self.state.locals_stack[-1].update(current_vars)
                return self.trace_dispatch
            
            old_vars = self.state.get_current_locals()
            new_vars = set(frame.f_locals.keys()) - INTERNAL_VARS
            created = new_vars - old_vars
            
            if self.state.locals_stack:
                self.state.locals_stack[-1].update(created)
            
            self.state.on_line(lineno - 1, created, frame_id)
            
        elif event == 'return':
            old_vars = self.state.get_current_locals()
            new_vars = set(frame.f_locals.keys()) - INTERNAL_VARS
            created = new_vars - old_vars
            
            if created:
                self.state.on_line(lineno, created, frame_id)
            
            if funcname != '<module>':
                self.state.on_return(funcname, lineno)
        
        return self.trace_dispatch
    
    def run(self, script_path):
        """Execute script with tracing enabled."""
        import runpy
        
        self.target_file = script_path
        self.target_file_normalized = os.path.normpath(os.path.abspath(script_path))
        
        sys.settrace(self.trace_dispatch)
        
        try:
            runpy.run_path(script_path, run_name='__main__')
        finally:
            sys.settrace(None)
            
        return self.state