# -*- coding: utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # #
#	TRADUCTORES E INTERPRETADORES CI3725      #
#	Cuarta entrega del proyecto.              #
#   Interpretador para el lenguaje Setlan     #
#	Autores: Carlos Martínez 	- 11-10584    #
#			 Christian Teixeira - 11-11016    #
# # # # # # # # # # # # # # # # # # # # # # # #

from sys import stdout, stdin
printf = stdout.write
read = stdin.readline

error_intr = []
SymTab = None
num_scopes = 0
indent_level = 0

def interpreter_traverser(AST):
	global error_intr
	global num_scopes
	global indent_level

	if AST.type == "block":
		num_scopes += 1
		indent_level += 1

	elif AST.type == "block_end":
		indent_level -= 1

	elif AST.type == "print":
		elements = AST.children[0].children
		string = ""
		for elem in elements:
			if elem.type == "str_stmt":
				act = elem.children[0].val[1:-1]

				# Identificar Regex
				act = act.split("\\n")
				for i in range(len(act)-1):
					string = string + act[i] + "\n"
				if act[-1] != "''":
					string = string + act[-1]
			if elem.type == "var_stmt":
				varname = elem.children[0].val
				string += str(SymTab.valof(varname, num_scopes))

		printf(string)

	elif AST.type == "scan":
		variable = AST.children[0].children[0]
		varType = SymTab.typeof(variable.val, num_scopes)
		
		value = read()
		value = value.split("\n")[0]
		valueType = ""

		try:
			value = int(value)
		except ValueError:
			pass
		else:
			valueType = "int"

		if value == "true" or value == "false":
			valueType = "bool"
		elif valueType != "int":
			valueType = "error"
		
		if valueType != varType:
			# Agrega el error a la lista
			if valueType == "bool" or valueType == "int":
				error_intr.append(("inv_type_scan", variable.val, variable.lineno, variable.colno, varType, valueType))
				return False
			else:
				error_intr.append(("inv_norec_scan", variable.val, variable.lineno, variable.colno))
				return False
		else:
			SymTab.update(variable.val, num_scopes, varType, value, SymTab.lin_decof(variable.val, num_scopes))


	elif AST.type == "assign":
		assign_var = AST.children[0].children[0].val
		assign_var_type = SymTab.typeof(assign_var, num_scopes)
		expr = AST.children[1].children[0]
		expr_val = evaluate(expr)
		if assign_var_type == "int":
			SymTab.update(assign_var, num_scopes, assign_var_type, expr_val, SymTab.lin_decof(assign_var, num_scopes))
		elif assign_var_type == "bool":
			if expr_val:
				SymTab.update(assign_var, num_scopes, assign_var_type, "true", SymTab.lin_decof(assign_var, num_scopes))
			else:
				SymTab.update(assign_var, num_scopes, assign_var_type, "false", SymTab.lin_decof(assign_var, num_scopes))

	# Recorre los hijos del nodo actual
	if AST.children:
		for child in AST.children:
			ch = interpreter_traverser(child)
			if ch == False:
				return False


def execute(AST, ST):
	global SymTab
	SymTab = ST
	inter = interpreter_traverser(AST)

	if inter == None:
		return True
	else:
		return False


def evaluate(expr):
	# Casos base
	if expr.type == "int_stmt" or expr.type == "set_stmt":
		if expr.type == "set_stmt":
			actual_set = []
			for child in expr.children:
				actual_set.append(evaluate(child))
			return actual_set
		else:
			return expr.children[0].val
	if expr.type == "const_stmt":
		return expr.children[0].val == "true"
	if expr.type == "var_stmt":
		return SymTab.valof(expr.children[0].val, num_scopes)

	# Operadores de enteros
	if expr.type == "expr_binopr":
		opr_a = int(evaluate(expr.children[0]))
		opr_b = int(evaluate(expr.children[1]))
		if expr.val.split()[1] == "+": return opr_a + opr_b
		if expr.val.split()[1] == "-": return opr_a - opr_b
		if expr.val.split()[1] == "*": return opr_a * opr_b
		if expr.val.split()[1] == "/":
			if opr_b == 0:
				error_intr.append(("div_by_zero", 0, expr.lineno, expr.colno))
			else:
				return opr_a / opr_b

	if expr.type == "expr_cmpopr":
		opr_a = int(evaluate(expr.children[0]))
		opr_b = int(evaluate(expr.children[1]))
		if expr.val.split()[1] == ">": return opr_a > opr_b
		if expr.val.split()[1] == "<": return opr_a < opr_b
		if expr.val.split()[1] == ">=": return opr_a >= opr_b
		if expr.val.split()[1] == "<=": return opr_a <= opr_b

	if expr.type == "negate_stmt":
		opr_a = int(evaluate(expr.children[0]))
		return -opr_a

	# Operadores de booleanos

	if expr.type == "bool_binopr":
		opr_a = evaluate(expr.children[0])
		opr_b = evaluate(expr.children[1])
		if expr.val.split()[1] == "or": return opr_a or opr_b
		if expr.val.split()[1] == "and": return opr_a and opr_b

	if expr.type == "not_stmt":
		opr_a = evaluate(expr.children[0])
		return not opr_a

	# Operadores de conjuntos

	if expr.type == "expr_setcont":
		opr_a = evaluate(expr.children[0])
		opr_b = evaluate(expr.children[1])
		pass

	if expr.type == "set_binopr":
		opr_a = evaluate(expr.children[0])
		opr_b = evaluate(expr.children[1])
		pass

	if expr.type == "set_mapopr":
		opr_a = evaluate(expr.children[0])
		opr_b = evaluate(expr.children[1])
		pass

	if expr.type == "set_unropr":
		opr_a = evaluate(expr.children[0])
		pass


def get_errors():
	global error_intr
	return error_intr