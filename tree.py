
class Tree:

	def __init__( self, value, children = None ):

		self.value = value

		self.children = [] if children == None else children

	def hang( self, child ):

		self.children.append( child )

	def preorder( self, callback ):

		stack = [ self ]

		while stack:

			root = stack.pop()

			callback( root.value )

			for c in root.children:

				stack.append( c )

	def postorder( self, callback ):

		stack = [ ( self, False ) ]

		while stack:

			root, ready = stack.pop()

			if ready:
				callback( root.value )
				continue
			
			for c in root.children:
				stack.append( c )

			stack.append( ( root, True ) )

	def map( self, f ):

		prime = Tree( f( self.value ) )

		stack = [ (c,prime) for c in self.children ]

		while stack:

			node, parent = stack.pop()

			mapped = f( node.value )

			if isinstance( mapped, Tree ):
				node_tree = Tree( mapped.value, mapped.children )
			else:
				node_tree = Tree( mapped )

			parent.hang( node_tree )

			for child in root.children:
				stack.append( (child,node_tree) )

	def supplement( self, f ):

		stack = [ self ]

		while stack:

			root = stack.pop()

			for c in root.children:

				stack.append( c )

	def str_indent( self, indent = 0 ):

		indents = '\t'*indent

		ret = f'{indents}{self.value}'

		for c in self.children:
			ret += '\n'
			ret += c.str_indent( indent + 1 )

		return ret

	def __str__( self ):

		return self.str_indent( )
