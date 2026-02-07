"""
Safe state tracking for traced execution.
Never compares or inspects runtime object values.
"""


class TraceState:
    def __init__(self):
        self.events = []
        self.call_stack = []
        self.locals_stack = [set()]
        self.context_map = {}  # AST context map (injected from outside)
        self.iteration_counter = {}  # (frame_id, line) → count
        
    def set_context_map(self, context_map):
        """Inject AST context map before execution."""
        self.context_map = context_map
    
    def on_call(self, funcname, lineno):
        """Function/method called."""
        self.call_stack.append(funcname)
        self.locals_stack.append(set())
        
        context = self.context_map.get(lineno, [])
        
        self.events.append({
            'event': 'call',
            'function': funcname,
            'line': lineno,
            'depth': len(self.call_stack),
            'context': context
        })
    
    def on_line(self, lineno, created_vars, frame_id=None):
        """Line executed. created_vars = set of new variable names."""
        depth = len(self.call_stack)
        context = self.context_map.get(lineno, [])
        
        # Track iteration count
        if frame_id is not None:
            key = (frame_id, lineno)
            self.iteration_counter[key] = self.iteration_counter.get(key, 0) + 1
            iteration = self.iteration_counter[key]
        else:
            iteration = None
        
        self.events.append({
            'event': 'line',
            'line': lineno,
            'created': sorted(created_vars),
            'depth': depth,
            'context': context,
            'iteration': iteration
        })
    
    def on_return(self, funcname, lineno):
        """Function returned."""
        depth = len(self.call_stack)
        context = self.context_map.get(lineno, [])
        
        self.events.append({
            'event': 'return',
            'function': funcname,
            'line': lineno,
            'depth': depth,
            'context': context
        })
        
        if self.call_stack:
            self.call_stack.pop()
        if self.locals_stack:
            self.locals_stack.pop()
    
    def get_current_locals(self):
        """Return current frame's known local variables."""
        if self.locals_stack:
            return self.locals_stack[-1]
        return set()
    
    def get_events(self):
        """Return all recorded events."""
        return self.events