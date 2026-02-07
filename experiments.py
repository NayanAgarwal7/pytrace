"""
Runner for tracer experiments.
Usage: python experiments.py <script_path>
"""
import sys
from pathlib import Path
from pytrace import Tracer
from pytrace.ast_parser import parse_source
from pytrace.explainer import Explainer


def format_event(evt):
    """Format a trace event for display."""
    indent = "  " * (evt['depth'] - 1)
    
    if evt['event'] == 'call':
        return f"{indent}CALL {evt['function']} (line {evt['line']})"
    
    elif evt['event'] == 'line':
        created = evt.get('created', [])
        if created:
            vars_str = ', '.join(created)
            return f"{indent}LINE {evt['line']:3d} → created: {vars_str}"
        else:
            return f"{indent}LINE {evt['line']:3d}"
    
    elif evt['event'] == 'return':
        return f"{indent}RETURN {evt['function']} (line {evt['line']})"
    
    return f"{indent}{evt['event'].upper()}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python experiments.py <script_path> [--explain]")
        sys.exit(1)
    
    script_path = sys.argv[1]
    show_explanations = '--explain' in sys.argv
    
    if not Path(script_path).exists():
        print(f"Error: {script_path} not found")
        sys.exit(1)
    
    print(f"=== Tracing: {script_path} ===\n")
    
    # Parse AST BEFORE execution
    with open(script_path) as f:
        source_code = f.read()
    context_map = parse_source(source_code)
    
    # Run tracer with AST context
    tracer = Tracer()
    tracer.state.set_context_map(context_map)
    state = tracer.run(script_path)
    
    # Display events
    events = state.get_events()
    for event in events:
        print(format_event(event))
    
    print(f"\n=== Total events: {len(events)} ===")
    
    # Generate explanations if requested
    if show_explanations:
        print("\n=== Explanations ===\n")
        explainer = Explainer()
        
        for i, event in enumerate(events):
            history = events[:i]  # Prior events only
            explanation = explainer.explain(event, history)
            
            if explanation:
                print(explanation)


if __name__ == '__main__':
    main()