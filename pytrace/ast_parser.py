"""
Static AST analysis for structural context extraction.
Parses Python source ONCE to build line-number → context mapping.
Does NOT execute code. Does NOT interpret semantics.
"""
import ast


class ASTParser(ast.NodeVisitor):
    """
    Builds a map from line numbers to structural context stacks.
    Context stack = list of (type, name) tuples describing nesting.
    """
    
    def __init__(self, source_code: str):
        self.tree = ast.parse(source_code)
        self.context_map = {}  # line_number → context_stack
        self.stack = []        # current context stack
        self.visit(self.tree)
    
    def generic_visit(self, node):
        """Record context for every node with a line number."""
        if hasattr(node, "lineno"):
            # Copy stack - no shared references
            self.context_map[node.lineno] = list(self.stack)
        super().generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Function definition."""
        self.stack.append(("function", node.name))
        self.generic_visit(node)
        self.stack.pop()
    
    def visit_AsyncFunctionDef(self, node):
        """Async function definition."""
        self.stack.append(("function", node.name))
        self.generic_visit(node)
        self.stack.pop()
    
    def visit_For(self, node):
        """For loop."""
        self.stack.append(("loop", "for"))
        self.generic_visit(node)
        self.stack.pop()
    
    def visit_AsyncFor(self, node):
        """Async for loop."""
        self.stack.append(("loop", "for"))
        self.generic_visit(node)
        self.stack.pop()
    
    def visit_While(self, node):
        """While loop."""
        self.stack.append(("loop", "while"))
        self.generic_visit(node)
        self.stack.pop()
    
    def visit_If(self, node):
        """If statement."""
        self.stack.append(("conditional", "if"))
        self.generic_visit(node)
        self.stack.pop()
    
    def get_context(self, lineno):
        """Get context stack for a line number."""
        return self.context_map.get(lineno, [])


def parse_source(source_code: str):
    """Parse source code and return context map."""
    parser = ASTParser(source_code)
    return parser.context_map