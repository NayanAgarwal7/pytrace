"""
Rule-based explanation engine for traced execution events.
Produces deterministic, technical descriptions of state transitions.
NO speculation. NO guessing. NO narrative.
"""


class Explainer:
    """
    Generates technical explanations for execution events.
    All logic is explicit and rule-based.
    """
    
    def explain(self, event, history):
        """
        Generate explanation for a single event.
        
        Args:
            event: Current event dict
            history: List of prior events (read-only)
        
        Returns:
            str or None (None = no explanation needed)
        """
        event_type = event.get('event')
        
        if event_type == 'call':
            return self._explain_call(event, history)
        elif event_type == 'line':
            return self._explain_line(event, history)
        elif event_type == 'return':
            return self._explain_return(event, history)
        
        return None
    
    def _explain_call(self, event, history):
        """Explain function call."""
        funcname = event.get('function')
        
        if funcname == '<module>':
            return None  # Module entry is implicit
        
        return f"Function {funcname} is called."
    
    def _explain_line(self, event, history):
        """Explain line execution with variable creation."""
        line = event.get('line')
        created = event.get('created', [])
        context = event.get('context', [])
        iteration = event.get('iteration')
        
        if not created:
            return None  # No state change
        
        # Build context prefix
        prefix_parts = []
        
        # Extract function context
        func_context = self._get_function_context(context)
        if func_context:
            prefix_parts.append(f"in function {func_context}")
        
        # Extract loop context
        loop_depth = self._get_loop_depth(context)
        if loop_depth > 0 and iteration is not None:
            if loop_depth == 1:
                prefix_parts.append(f"iteration {iteration}")
            else:
                prefix_parts.append(f"nested loop iteration {iteration}")
        
        # Format variable list
        if len(created) == 1:
            var_phrase = f"variable {created[0]}"
        else:
            var_phrase = f"variables {', '.join(created)}"
        
        # Assemble explanation
        if prefix_parts:
            prefix = ', '.join(prefix_parts)
            return f"Line {line}: {prefix.capitalize()}, {var_phrase} created."
        else:
            return f"Line {line}: {var_phrase.capitalize()} created."
    
    def _explain_return(self, event, history):
        """Explain function return."""
        funcname = event.get('function')
        line = event.get('line')
        
        return f"Function {funcname} returns at line {line}."
    
    def _get_function_context(self, context):
        """Extract function name from context stack."""
        for ctx_type, ctx_name in context:
            if ctx_type == 'function':
                return ctx_name
        return None
    
    def _get_loop_depth(self, context):
        """Count number of nested loops in context."""
        return sum(1 for ctx_type, _ in context if ctx_type == 'loop')
    
    def _has_conditional(self, context):
        """Check if context includes conditional."""
        return any(ctx_type == 'conditional' for ctx_type, _ in context)