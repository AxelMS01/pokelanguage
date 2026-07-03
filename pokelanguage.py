import enum

# ==========================================
# 1. TOKENS
# ==========================================
class TokenType(enum.Enum):
    WILD = 'wild'; LEGENDARY = 'legendary'; POKEBALL = 'pokeball'; GREATBALL = 'greatball'
    QUICKBALL = 'quickball'; PREMIERBALL = 'premierball'; STRANGEBALL = 'strangeball'
    CATCH = 'catch'; CLONEBALL = 'cloneball'; MISSINGNO = 'missingno'
    ULTRABALL = 'ultraball'; REPEATBALL = 'repeatball'; CRIT = 'crit'; MISSED = 'missed'

    NUMBER = 'NUMBER'; STRING = 'STRING'; IDENTIFIER = 'IDENTIFIER'
    
    PLUS = '+'; MINUS = '-'; MUL = '*'; DIV = '/'
    EQ = '=='; NEQ = '!='; LT = '<'; GT = '>'; LTE = '<='; GTE = '>='
    ASSIGN = '='; BANG = '!'
    
    LPAREN = '('; RPAREN = ')'; LBRACE = '{'; RBRACE = '}'
    LBRACKET = '['; RBRACKET = ']'
    SEMICOLON = ';'; COMMA = ','
    EOF = 'EOF'

class Token:
    def __init__(self, type, value, line=0): # Added line tracking
        self.type = type
        self.value = value
        self.line = line
    def __repr__(self):
        return f'<{self.value}, {self.type.name}>'

# ==========================================
# 2. LEXER (With Line Tracking)
# ==========================================
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1 # Track lines
        self.current_char = self.text[self.pos] if self.text else None

    def advance(self):
        if self.current_char == '\n': self.line += 1
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace(): self.advance()

    def skip_comments(self):
        if self.current_char == '/' and self.text[self.pos+1] == '/':
            while self.current_char and self.current_char != '\n': self.advance()
        elif self.current_char == '/' and self.text[self.pos+1] == '*':
            self.advance(); self.advance()
            while not (self.current_char == '*' and self.text[self.pos+1] == '/'):
                if not self.current_char: raise Exception(f"Unclosed /*BLUE*/ comment at line {self.line}")
                self.advance()
            self.advance(); self.advance()

    def number(self):
        result = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char; self.advance()
        return float(result) if '.' in result else int(result)

    def string(self):
        self.advance()
        result = ''
        while self.current_char and self.current_char != '"': result += self.current_char; self.advance()
        self.advance()
        return result

    def identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char; self.advance()
        keywords = {
            'wild': TokenType.WILD, 'legendary': TokenType.LEGENDARY, 'pokeball': TokenType.POKEBALL,
            'greatball': TokenType.GREATBALL, 'quickball': TokenType.QUICKBALL, 'premierball': TokenType.PREMIERBALL,
            'strangeball': TokenType.STRANGEBALL, 'catch': TokenType.CATCH, 'cloneball': TokenType.CLONEBALL,
            'missingno': TokenType.MISSINGNO, 'ultraball': TokenType.ULTRABALL, 'repeatball': TokenType.REPEATBALL,
            'crit': TokenType.CRIT, 'missed': TokenType.MISSED
        }
        return Token(keywords.get(result, TokenType.IDENTIFIER), result, self.line)

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace(): self.skip_whitespace(); continue
            if self.current_char == '/': self.skip_comments(); continue
            if self.current_char.isdigit(): return Token(TokenType.NUMBER, self.number(), self.line)
            if self.current_char == '"': return Token(TokenType.STRING, self.string(), self.line)
            if self.current_char.isalpha() or self.current_char == '_': return self.identifier()
            
            if self.current_char == '=' and self.text[self.pos+1] == '=': self.advance(); self.advance(); return Token(TokenType.EQ, '==', self.line)
            if self.current_char == '!' and self.text[self.pos+1] == '=': self.advance(); self.advance(); return Token(TokenType.NEQ, '!=', self.line)
            if self.current_char == '<' and self.text[self.pos+1] == '=': self.advance(); self.advance(); return Token(TokenType.LTE, '<=', self.line)
            if self.current_char == '>' and self.text[self.pos+1] == '=': self.advance(); self.advance(); return Token(TokenType.GTE, '>=', self.line)

            single_chars = {
                '+': TokenType.PLUS, '-': TokenType.MINUS, '*': TokenType.MUL, '/': TokenType.DIV,
                '<': TokenType.LT, '>': TokenType.GT, '=': TokenType.ASSIGN, '!': TokenType.BANG,
                '(': TokenType.LPAREN, ')': TokenType.RPAREN, '{': TokenType.LBRACE, '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET, ']': TokenType.RBRACKET, ';': TokenType.SEMICOLON, ',': TokenType.COMMA
            }
            if self.current_char in single_chars:
                char = self.current_char; self.advance(); return Token(single_chars[char], char, self.line)
            raise Exception(f"Error Léxico: Carácter inválido '{self.current_char}' en línea {self.line}")
        return Token(TokenType.EOF, None, self.line)

# ==========================================
# 3. AST NODES
# ==========================================
class NumberNode: 
    def __init__(self, token): self.token = token
class StringNode: 
    def __init__(self, token): self.token = token
class BoolNode: 
    def __init__(self, value): self.value = value
class NullNode: pass
class VarNode: 
    def __init__(self, token): self.token = token
class ArrayNode: 
    def __init__(self, elements): self.elements = elements
class ArrayAccessNode: 
    def __init__(self, array_name, index): self.array_name = array_name; self.index = index
class BinOpNode: 
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
class UnaryOpNode: 
    def __init__(self, op, node): self.op, self.node = op, node
class AssignNode: 
    def __init__(self, name, value, is_const=False): self.name, self.value, self.is_const = name, value, is_const
class PrintNode: 
    def __init__(self, value): self.value = value
class IfNode: 
    def __init__(self, condition, true_block, false_block): self.condition, self.true_block, self.false_block = condition, true_block, false_block
class WhileNode: 
    def __init__(self, condition, block): self.condition, self.block = condition, block
class ForNode: 
    def __init__(self, init, condition, increment, block): self.init, self.condition, self.increment, self.block = init, condition, increment, block
class BlockNode: 
    def __init__(self, statements): self.statements = statements
class FunctionNode: 
    def __init__(self, name, params, body): self.name, self.params, self.body = name, params, body
class ReturnNode: 
    def __init__(self, value): self.value = value
class CallNode: 
    def __init__(self, name, args): self.name, self.args = name, args

# ==========================================
# 4. PARSER
# ==========================================
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(f"Error Sintáctico en línea {self.current_token.line}: Se esperaba {token_type.name}, se obtuvo '{self.current_token.value}'")

    def parse(self): return self.program()
    def program(self): return BlockNode(self.declaration_list())
    def declaration_list(self):
        nodes = []
        while self.current_token.type != TokenType.EOF: nodes.append(self.declaration())
        return nodes
    def declaration(self):
        if self.current_token.type == TokenType.CATCH: return self.fun_decl()
        if self.current_token.type in (TokenType.WILD, TokenType.LEGENDARY): return self.var_decl()
        return self.statement()
    def fun_decl(self):
        self.eat(TokenType.CATCH); name = self.current_token.value; self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN); params = self.parameters_opt(); self.eat(TokenType.RPAREN)
        return FunctionNode(name, params, self.block())
    def parameters_opt(self):
        return [] if self.current_token.type == TokenType.RPAREN else self.parameters()
    def parameters(self):
        params = [self.current_token.value]; self.eat(TokenType.IDENTIFIER)
        while self.current_token.type == TokenType.COMMA: self.eat(TokenType.COMMA); params.append(self.current_token.value); self.eat(TokenType.IDENTIFIER)
        return params
    def var_decl(self):
        is_const = self.current_token.type == TokenType.LEGENDARY
        self.eat(self.current_token.type); name = self.current_token.value; self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN); value = self.expression(); self.eat(TokenType.SEMICOLON)
        return AssignNode(name, value, is_const)
    def statement(self):
        if self.current_token.type == TokenType.POKEBALL: return self.if_stmt()
        if self.current_token.type == TokenType.QUICKBALL: return self.while_stmt()
        if self.current_token.type == TokenType.CLONEBALL: return self.for_stmt()
        if self.current_token.type == TokenType.ULTRABALL: return self.print_stmt()
        if self.current_token.type == TokenType.REPEATBALL: return self.return_stmt()
        if self.current_token.type == TokenType.LBRACE: return self.block()
        return self.expr_stmt()
    def if_stmt(self):
        self.eat(TokenType.POKEBALL); self.eat(TokenType.LPAREN); condition = self.expression(); self.eat(TokenType.RPAREN)
        true_block = self.statement(); false_block = None
        if self.current_token.type == TokenType.GREATBALL: self.eat(TokenType.GREATBALL); false_block = self.statement()
        return IfNode(condition, true_block, false_block)
    def while_stmt(self):
        self.eat(TokenType.QUICKBALL); self.eat(TokenType.LPAREN); condition = self.expression(); self.eat(TokenType.RPAREN)
        return WhileNode(condition, self.statement())
    def for_stmt(self):
        self.eat(TokenType.CLONEBALL); self.eat(TokenType.LPAREN)
        init = self.var_decl() if self.current_token.type == TokenType.WILD else self.expr_stmt()
        condition = self.expression() if self.current_token.type != TokenType.SEMICOLON else BoolNode(True)
        self.eat(TokenType.SEMICOLON)
        increment = self.expression() if self.current_token.type != TokenType.RPAREN else None
        self.eat(TokenType.RPAREN); return ForNode(init, condition, increment, self.statement())
    def print_stmt(self):
        self.eat(TokenType.ULTRABALL); val = self.expression(); self.eat(TokenType.SEMICOLON); return PrintNode(val)
    def return_stmt(self):
        self.eat(TokenType.REPEATBALL)
        val = self.expression() if self.current_token.type != TokenType.SEMICOLON else NullNode()
        self.eat(TokenType.SEMICOLON); return ReturnNode(val)
    def block(self):
        self.eat(TokenType.LBRACE); nodes = []
        while self.current_token.type != TokenType.RBRACE: nodes.append(self.declaration())
        self.eat(TokenType.RBRACE); return BlockNode(nodes)
    def expr_stmt(self): node = self.expression(); self.eat(TokenType.SEMICOLON); return node
    def expression(self): return self.assignment()
    def assignment(self):
        node = self.logic_or()
        if self.current_token.type == TokenType.ASSIGN:
            op = self.current_token; self.eat(TokenType.ASSIGN)
            node = AssignNode(node.token.value if isinstance(node, VarNode) else node, self.assignment())
        return node
    def logic_or(self):
        node = self.logic_and()
        while self.current_token.type == TokenType.STRANGEBALL: op = self.current_token; self.eat(TokenType.STRANGEBALL); node = BinOpNode(node, op, self.logic_and())
        return node
    def logic_and(self):
        node = self.equality()
        while self.current_token.type == TokenType.PREMIERBALL: op = self.current_token; self.eat(TokenType.PREMIERBALL); node = BinOpNode(node, op, self.equality())
        return node
    def equality(self):
        node = self.comparison()
        while self.current_token.type in (TokenType.EQ, TokenType.NEQ): op = self.current_token; self.eat(op.type); node = BinOpNode(node, op, self.comparison())
        return node
    def comparison(self):
        node = self.term()
        while self.current_token.type in (TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE): op = self.current_token; self.eat(op.type); node = BinOpNode(node, op, self.term())
        return node
    def term(self):
        node = self.factor()
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS): op = self.current_token; self.eat(op.type); node = BinOpNode(node, op, self.factor())
        return node
    def factor(self):
        node = self.unary()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV): op = self.current_token; self.eat(op.type); node = BinOpNode(node, op, self.unary())
        return node
    def unary(self):
        if self.current_token.type in (TokenType.MINUS, TokenType.BANG): op = self.current_token; self.eat(op.type); return UnaryOpNode(op, self.unary())
        return self.call()
    def call(self):
        node = self.primary()
        if self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN); args = []
            if self.current_token.type != TokenType.RPAREN:
                args.append(self.expression())
                while self.current_token.type == TokenType.COMMA: self.eat(TokenType.COMMA); args.append(self.expression())
            self.eat(TokenType.RPAREN); return CallNode(node.token.value, args)
        if self.current_token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET); index = self.expression(); self.eat(TokenType.RBRACKET)
            return ArrayAccessNode(node.token.value, index)
        return node
    def primary(self):
        token = self.current_token
        if token.type == TokenType.NUMBER: self.eat(TokenType.NUMBER); return NumberNode(token)
        if token.type == TokenType.STRING: self.eat(TokenType.STRING); return StringNode(token)
        if token.type == TokenType.CRIT: self.eat(TokenType.CRIT); return BoolNode(True)
        if token.type == TokenType.MISSED: self.eat(TokenType.MISSED); return BoolNode(False)
        if token.type == TokenType.MISSINGNO: self.eat(TokenType.MISSINGNO); return NullNode()
        if token.type == TokenType.IDENTIFIER: self.eat(TokenType.IDENTIFIER); return VarNode(token)
        if token.type == TokenType.LBRACKET:
            self.eat(TokenType.LBRACKET); elements = []
            if self.current_token.type != TokenType.RBRACKET:
                elements.append(self.expression())
                while self.current_token.type == TokenType.COMMA: self.eat(TokenType.COMMA); elements.append(self.expression())
            self.eat(TokenType.RBRACKET); return ArrayNode(elements)
        if token.type == TokenType.LPAREN: self.eat(TokenType.LPAREN); node = self.expression(); self.eat(TokenType.RPAREN); return node
        raise Exception(f"Error Sintáctico en línea {token.line}: Expresión inesperada '{token.value}'")

# ==========================================
# 5. SYMBOL TABLE LOGGER (NEW!)
# ==========================================
class SymbolTableLogger:
    def __init__(self):
        self.symbols = []
        self.irregulars = [] # Errors/Exceptions

    def add_symbol(self, name, poke_type, scope, kind, value):
        # Avoid duplicates in same scope for the log file
        if not any(s['ID'] == name and s['Scope'] == scope for s in self.symbols):
            self.symbols.append({
                'ID': name, 'Type': poke_type, 'Scope': scope, 
                'Kind': kind, 'Value': str(value) if value is not None else "MissingNo"
            })

    def update_symbol(self, name, value):
        for s in self.symbols:
            if s['ID'] == name:
                s['Value'] = str(value) if value is not None else "MissingNo"

    def log_irregular(self, error_type, message):
        self.irregulars.append({'Type': error_type, 'Message': message})

    def generate_txt(self, filename="symbol_table.txt"):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("   POKEMON LANGUAGE - SYMBOL TABLE & LOG\n")
            f.write("="*50 + "\n\n")
            
            f.write("--- TABLA DE SÍMBOLOS ---\n")
            f.write(f"{'ID':<15} | {'Type':<10} | {'Scope':<10} | {'Kind':<10} | {'Value':<15}\n")
            f.write("-"*70 + "\n")
            if not self.symbols:
                f.write("(Vacía - Ocurrió un error antes de declarar variables)\n")
            for s in self.symbols:
                f.write(f"{s['ID']:<15} | {s['Type']:<10} | {s['Scope']:<10} | {s['Kind']:<10} | {s['Value']:<15}\n")
            
            f.write("\n--- EXPRESIONES IRREGULARES / ERRORES ---\n")
            if not self.irregulars:
                f.write("(Ninguna - Código ejecutado perfectamente)\n")
            for err in self.irregulars:
                f.write(f"[{err['Type']}] {err['Message']}\n")
            
            f.write("\n" + "="*50 + "\n")

# ==========================================
# 6. INTERPRETER
# ==========================================
class Environment:
    def __init__(self, parent=None, scope_name="Local"):
        self.variables = {}
        self.constants = set()
        self.parent = parent
        self.scope_name = scope_name

    def get(self, name):
        if name in self.variables: return self.variables[name]
        if self.parent: return self.parent.get(name)
        raise Exception(f"La variable 'wild {name}' no está declarada.")

    def set(self, name, value):
        if name in self.constants: raise Exception(f"No se puede modificar la constante 'legendary {name}'.")
        if name in self.variables: self.variables[name] = value; return
        if self.parent: self.parent.set(name, value); return
        raise Exception(f"La variable 'wild {name}' no está declarada.")

    def declare(self, name, value, is_const):
        if is_const: self.constants.add(name)
        self.variables[name] = value

class ReturnException(Exception):
    def __init__(self, value): self.value = value

class Interpreter:
    def __init__(self, parser, logger):
        self.parser = parser
        self.logger = logger
        self.global_env = Environment(scope_name="Global")
        self.current_env = self.global_env

    def interpret(self):
        tree = self.parser.parse()
        self.execute(tree, self.global_env)

    def get_poke_type(self, val):
        if isinstance(val, int): return "Fire"
        if isinstance(val, float): return "Water"
        if isinstance(val, str): return "Grass"
        if isinstance(val, bool): return "Psychic"
        if val is None: return "MissingNo"
        if isinstance(val, tuple) and val[0] == "function": return "Function"
        return "Unknown"

    def execute(self, node, env):
        self.current_env = env
        method_name = f'exec_{type(node).__name__}'
        executor = getattr(self, method_name, self.generic_exec)
        return executor(node, env)

    def generic_exec(self, node, env):
        raise Exception(f"No existe ejecución para {type(node).__name__}")

    def exec_BlockNode(self, node, env):
        new_env = Environment(env, "Local")
        for stmt in node.statements: self.execute(stmt, new_env)

    def exec_AssignNode(self, node, env):
        value = self.evaluate(node.value, env)
        is_const = hasattr(node, 'is_const') and node.is_const

        if is_const:
            env.declare(node.name, value, True)
            self.logger.add_symbol(node.name, self.get_poke_type(value), env.scope_name, "Legendary", value)
        else:
            current_env = env
            found = False
            while current_env is not None:
                if node.name in current_env.variables:
                    found = True; break
                current_env = current_env.parent
            
            if found:
                env.set(node.name, value)
                self.logger.update_symbol(node.name, value)
            else:
                env.declare(node.name, value, False)
                self.logger.add_symbol(node.name, self.get_poke_type(value), env.scope_name, "Wild", value)

    def exec_IfNode(self, node, env):
        if self.evaluate(node.condition, env): self.execute(node.true_block, env)
        elif node.false_block: self.execute(node.false_block, env)

    def exec_WhileNode(self, node, env):
        while self.evaluate(node.condition, env): self.execute(node.block, env)

    def exec_ForNode(self, node, env):
        new_env = Environment(env, "Cloneball Scope")
        self.execute(node.init, new_env)
        while self.evaluate(node.condition, new_env):
            self.execute(node.block, new_env)
            if node.increment: self.evaluate(node.increment, new_env)

    def exec_PrintNode(self, node, env):
        val = self.evaluate(node.value, env)
        if val is None: print("MissingNo")
        elif val == True: print("Crit")
        elif val == False: print("Missed")
        else: print(val)

    def exec_FunctionNode(self, node, env):
        env.declare(node.name, ("function", node.params, node.body), False)
        self.logger.add_symbol(node.name, "Function", env.scope_name, "Catch", f"Params: {node.params}")

    def exec_ReturnNode(self, node, env):
        val = self.evaluate(node.value, env)
        raise ReturnException(val)

    def exec_ExpressionStatement(self, node, env):
        self.evaluate(node, env)

    # --- Evaluate Expressions ---
    def evaluate(self, node, env):
        method_name = f'eval_{type(node).__name__}'
        evaluator = getattr(self, method_name, self.generic_eval)
        return evaluator(node, env)

    def generic_eval(self, node, env): return self.execute(node, env)
    def eval_NumberNode(self, node, env): return node.token.value
    def eval_StringNode(self, node, env): return node.token.value
    def eval_BoolNode(self, node, env): return node.value
    def eval_NullNode(self, node, env): return None
    def eval_VarNode(self, node, env): return env.get(node.token.value)
    def eval_ArrayNode(self, node, env): return [self.evaluate(e, env) for e in node.elements]
    
    def eval_ArrayAccessNode(self, node, env):
        array = env.get(node.array_name)
        index = self.evaluate(node.index, env)
        try:
            return array[int(index)]
        except IndexError:
            err_msg = f"Índice fuera de rango al acceder a '{node.array_name}[{index}]'. Tamaño máximo: {len(array)-1}"
            self.logger.log_irregular("Irregular Expression (Array)", err_msg)
            raise Exception(err_msg)
        except TypeError:
            err_msg = f"Índice inválido '{index}' para el arreglo '{node.array_name}'. Se esperaba un número (Fire)."
            self.logger.log_irregular("Irregular Expression (Type)", err_msg)
            raise Exception(err_msg)

    def eval_BinOpNode(self, node, env):
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        try:
            if node.op.type == TokenType.PLUS: return left + right
            if node.op.type == TokenType.MINUS: return left - right
            if node.op.type == TokenType.MUL: return left * right
            if node.op.type == TokenType.DIV: return left / right
            if node.op.type == TokenType.EQ: return left == right
            if node.op.type == TokenType.NEQ: return left != right
            if node.op.type == TokenType.LT: return left < right
            if node.op.type == TokenType.GT: return left > right
            if node.op.type == TokenType.LTE: return left <= right
            if node.op.type == TokenType.GTE: return left >= right
            if node.op.type == TokenType.PREMIERBALL: return left and right
            if node.op.type == TokenType.STRANGEBALL: return left or right
        except TypeError:
            err_msg = f"Expresión irregular: No se puede operar '{type(left).__name__}' {node.op.value} '{type(right).__name__}'"
            self.logger.log_irregular("Irregular Expression (Type Mismatch)", err_msg)
            raise Exception(err_msg)

    def eval_UnaryOpNode(self, node, env):
        val = self.evaluate(node.node, env)
        if node.op.type == TokenType.MINUS: return -val
        if node.op.type == TokenType.BANG: return not val

    def eval_CallNode(self, node, env):
        func = env.get(node.name)
        if not isinstance(func, tuple) or func[0] != "function": raise Exception("Error: No es una función 'catch'")
        _, params, body = func
        if len(params) != len(node.args): raise Exception("Error: Argumentos no coinciden")
        
        call_env = Environment(env, f"Func:{node.name}")
        for p, a in zip(params, node.args): call_env.declare(p, self.evaluate(a, env), False)
        
        try: self.execute(body, call_env)
        except ReturnException as ret: return ret.value
        return None

# ==========================================
# 7. RUN IT
# ==========================================
if __name__ == '__main__':
    # This test code includes a DELIBERATE irregular expression at the end to test your logger!
    source_code = """
        // RED Clean code test
        wild pikachu = 2;
        legendary level_cap = 15;
        wild pokemon_name = "Charmander";
        
        pokeball (pikachu < level_cap) {
            ultraball "Pokemon is weak.";
        }
        
        wild moves = ["Tackle", "Ember"];
        cloneball (wild i = 0; i <= 1; i = i + 1) {
            ultraball moves[i];
        }
        
        catch heal(amount) {
            repeatball pikachu + amount;
        }
        
        wild new_hp = heal(5);
        ultraball new_hp;
    """
    logger = SymbolTableLogger()
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    interpreter = Interpreter(parser, logger)
    
    try:
        interpreter.interpret()
        print("\n[ÉXITO] Compilación y ejecución completadas.")
    except Exception as e:
        logger.log_irregular("Ejecución Abortada", str(e))
        print(f"\n[ERROR] {e}")
    finally:
        # ALWAYS generate the TXT file, even if it crashes!
        logger.generate_txt("symbol_table.txt")
        print("Archivo 'symbol_table.txt' generado exitosamente.")