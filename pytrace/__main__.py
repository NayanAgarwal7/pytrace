"""
Command Line Interface (CLI) entry point for PyTrace.
Allows: python -m pytrace script.py --explain
"""
import sys
from pathlib import Path
from pytrace import Tracer
from pytrace.ast_parser import parse_source
from pytrace.explainer import Explainer


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m pytrace <script_path> [--explain]")
        sys.exit(1)
    
    script_path = sys.argv[1]
    show_explanations = '--explain' in sys.argv
    
    if not Path(script_path).exists():
        print(f"Error: {script_path} not found")
        sys.exit(1)
    
    # Parse AST before execution
    with open(script_path) as f:
        source_code = f.read()
    context_map = parse_source(source_code)
    
    # Run tracer with AST context
    tracer = Tracer()
    tracer.state.set_context_map(context_map)
    state = tracer.run(script_path)
    
    # Generate explanations if requested
    if show_explanations:
        explainer = Explainer()
        events = state.get_events()
        
        for i, event in enumerate(events):
            history = events[:i]
            explanation = explainer.explain(event, history)
            
            if explanation:
                print(explanation)
    else:
        # Show raw trace
        events = state.get_events()
        for event in events:
            print(f"{event['event'].upper():6} line {event['line']:3} depth {event['depth']}")


if __name__ == '__main__':
    main()