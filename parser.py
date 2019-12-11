
from tree import Tree


class Nonterminal:

    __instances = {}

    def __new__( cls, sym, r = None ):

        i_hash = ( id(sym), id(r) )

        if i_hash not in Nonterminal.__instances:
            
            instance = object.__new__(cls)
            
            instance.hash = i_hash
            instance.sym  = sym
            instance.r    = r
            instance.nulled = False,
            instance.nulled_by = None
            instance._nulling_tree = None

            Nonterminal.__instances[ i_hash ] = instance

        return Nonterminal.__instances[ i_hash ]

    def nulling_tree( self ):

        if not self.nulled:
            return None
        
        if self._nulling_tree != None:
            return self._nulling_tree

        children = [ sym.nulling_tree() for sym in self.nulled_by.rhs ]

        self._nulling_tree = Tree( self.nulled_by, children )

        return self._nulling_tree

    def nabla( self, r ):
        return Nonterminal( self, r )

    def __hash__( self ):
        return hash( self.hash )

    def respect_string( self ):
        if isinstance( self.sym, Nonterminal):
            return self.sym.respect_string() + self.r
        if self.r:
            return self.r
        return ''

    def root_symbol( self ):
        if isinstance( self.sym, Nonterminal ):
            return self.sym.root_symbol()
        return self.sym

    def __str__( self ):
        if self.r:
            return f'D({self.root_symbol()},{self.respect_string()})'
            return f'D({self.sym},{self.r})'
        return str(self.sym)

    __repr__ = __str__


class Production:

    GIVEN, SCAN, CALL = 0, 1, 2

    def __init__( self, left, rhs, backptr, method, skips = 0 ):

        self.left = left
        self.rhs = tuple( rhs )
        self.backptr = backptr
        self.method  = method
        self.skips = skips

        self.is_scan  = method == Production.SCAN
        self.is_given = method == Production.GIVEN

        self._dep_tree = None

    def dependency_tree( self ):

        if self._dep_tree != None:
            return self._dep_tree

        self._dep_tree = Tree( self )

        if self.backptr != None:
            bp_tree = self.backptr.dependency_tree()
            self._dep_tree.hang( bp_tree )

        for skip in range( self.skips ):
            skip_nulls = self.rhs[skip].nulling_tree()
            skip_deps  = skip_nulls.map( Production.dependency_tree )
            self._dep_tree.hang( skip_deps )

        return self._dep_tree





    def __hash__( self ):

        return hash( ( self.left, self.rhs ) )

    def __str__( self ):

        return f'{self.left} -> {self.rhs}'


class Grammar:

    def __init__( self, nonterminals, productions, start ):

        self.nonterminals = { Nonterminal(sym) for sym in nonterminals }
        self.start        = start

        self.productions = {}
        for l, rs in productions.items():
            if not isinstance( l, Nonterminal ):
                l = Nonterminal( l )
            for r in rs:
                prod = Production( l, r, None, Production.GIVEN )
                self.add_production( prod )

        self.derivatives = {}


    def differentiate( self, n, s ):

        if len(s) > 1:
            nabla = n
            for c in s:
                nabla = self.differentiate( nabla, c )
            return nabla

        if not isinstance( n, Nonterminal ):
            n = Nonterminal( n )

        if s == '':
            return n

        nabla = n.nabla( s )

        if nabla in self.nonterminals:
            return nabla

        self.nonterminals.add( nabla )

        for prod in self.productions.get( n, [] ):

            for skips in range( len(prod.rhs) ):

                head, *tail = prod.rhs[skips:]

                if head == s: # Scan Rule
                    new_rhs = tail
                    new_prod = Production( nabla, new_rhs, prod, Production.SCAN, skips )
                elif isinstance( head, Nonterminal ): # Call Rule
                    if head != n:
                        da = self.differentiate( head, s )
                        new_rhs = ( da, *tail )
                    else:
                        new_rhs = ( nabla, *tail )
                    new_prod = Production( nabla, new_rhs, prod, Production.CALL, skips )
                else:
                    continue

                self.add_production( new_prod, True )

                if not isinstance(head,Nonterminal) or not head.nulled:
                    break

        return nabla


    def add_production( self, prod, allow_prune = False ):

        left = prod.left
        rhs  = prod.rhs

        # Check if nullable
        if all(isinstance(s,Nonterminal) and s.nulled for s in rhs):
            left.nulled_by = prod
            left.nulled    = True

        # Check for optimizations
        prune = False

        if allow_prune:
            # - gamma pruning
            if any(isinstance(s,Nonterminal) and s != left and (s not in self.productions) for s in rhs):
                prune = True
            # - tautology pruning
            if len(rhs) == 1 and left==rhs[0]:
                prune = True

        # Add production
        if not prune:
            if left not in self.productions:
                self.productions[left] = set()
            self.productions[left].add( prod )


    def recognize( self, s ):

        return self.differentiate( self.start, s ).nulled
    

    def parse( self, s ):

        root = self.differentiate( self.start, s )

        if not root.nulled:
            return None

        dependency_tree = root.nulled_by.dependency_tree()

        def collapse( n ):

            pass

        dependency_tree.preorder( collapse )

        print( dependency_tree )


    def disp( self ):
       
        nonterminals = sorted( [ (str(n),n) for n in self.nonterminals ], key=lambda x:len(x[0]) )

        print( 'Nonterminals:\n\t' + '\n\t'.join([ n[0] for n in nonterminals ]) )

        filtered = [ n[0] for n in nonterminals if n[1].nulled ]

        print( '\nNulled Symbols:\n\t' + '\n\t'.join(filtered) )

        print( '\nProductions:')

        for _, n in nonterminals:
            rs = self.productions.get(n,[ ['~~~EMPTY~~~'] ])
            rhs = '\n\t  ->  '.join( [ ' '.join(map(str,r.rhs)) for r in rs] )
            print( f'\n\t{n}\n\t  ->  {rhs}' )

    def size( self ):
        ret = 0
        for prods in self.productions.values():
            ret += len( prods.rhs )
        return ret





















if __name__ == '__main__':

    EXP = Nonterminal( 'EXP' )
    INT = Nonterminal( 'INT' )
    g = Grammar(
        nonterminals = { 'S', 'EXP' },
        productions  = {
            'S' : [
                [ 'I', '=', EXP ]
            ],
            EXP : [
                [ EXP, '+', EXP ],
                #[ EXP, '-', EXP ],
                #[ '(', EXP, ')' ],
                [ '1' ]
            ],
        },
        start = Nonterminal('S')
    )

    g.parse( 'I=1+1' )

    #g.disp()












