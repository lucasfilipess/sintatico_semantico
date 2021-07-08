import sys
from tag import Tag

class Parser:
    def __init__(self, analisador):
        self.lexer = analisador
        self.token = analisador.proxToken()

        if self.token is None:
            sys.exit(0)

    def sinalizaErroSintatico(self, message):
        print("[Erro Sintatico] na linha " + str(self.token.getLinha()) + " e coluna " + str(
            self.token.getColuna()) + ": ")
        print(message, "\n")
        sys.exit(0)

    def advance(self):
        print("[DEBUG] Token: ", self.token.toString(), "Linha: " + str(self.token.getLinha()) + " Coluna: " + str(self.token.getColuna()))
        self.token = self.lexer.proxToken()
        if self.token is None:  # erro no Lexer
            sys.exit(0)

    def skip(self, message):
        self.sinalizaErroSintatico(message)
        self.advance()

    # verifica token esperado t
    def eat(self, t):
        if (self.token.getNome() == t):
            self.advance()
            return True
        else:
            return False

    def Programa(self):
        if (not self.eat(Tag.KW_PROGRAM)):
            self.sinalizaErroSintatico("Esperado \"program\", encontrado " + "\"" + self.token.getLexema() + "\"")

        if (not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")

        self.body()

    def body(self):
        self.declList()

        if (not self.eat(Tag.SMB_OBC)):
            self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")

        self.stmtList()

        if (not self.eat(Tag.SMB_CBC)):
            self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def declList(self):
        if (self.token.getNome() != Tag.SMB_OBC):
            self.decl()

            if (not self.eat(Tag.SMB_SEM)):
                self.sinalizaErroSintatico("Esperado \";\", encontrado " + "\"" + self.token.getLexema() + "\"")

            self.declList()

            return True
        else:
            return False

    def decl(self):
        self.type()
        self.idList()

    def type(self):
        if(self.token.getLexema() == 'num'):
            self.eat(Tag.KW_NUM)
        elif (self.token.getLexema() == 'char'):
            self.eat(Tag.KW_CHAR)
        else:
            self.sinalizaErroSintatico("Esperado \"num, char\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def idList(self):
        if (not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")

        self.idListLinha()

    def idListLinha(self):
        if (self.token.getNome() != Tag.SMB_SEM):
            if (not self.eat(Tag.SMB_COM)):
                self.sinalizaErroSintatico("Esperado \", | ;\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.idList()
            return True
        else:
            return False

    def stmtList(self):
        if (self.token.getNome() != Tag.SMB_CBC):
            self.stmt()
            if (not self.eat(Tag.SMB_SEM)):
                self.sinalizaErroSintatico("Esperado \";\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.stmtList()
            return True
        else:
            return False

    def stmt(self):
        if (self.token.getNome() == Tag.ID):
            self.assignStmt()
        elif (self.token.getNome() == Tag.KW_IF):
            self.ifStmt()
        elif (self.token.getNome() == Tag.KW_WHILE):
            self.whileStmt()
        elif (self.token.getNome() == Tag.KW_READ):
            self.readStmt()
        elif (self.token.getNome() == Tag.KW_WRITE):
            self.writeStmt()
        else:
            self.sinalizaErroSintatico("Esperado \"ID, IF, WHILE, READ, WRITE\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def assignStmt(self):
        if (not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")
        if (not self.eat(Tag.OP_ATRIB)):
            self.sinalizaErroSintatico("Esperado \"=\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.simpleExpr()

    def ifStmt(self):
        if (not self.eat(Tag.KW_IF)):
            self.sinalizaErroSintatico("Esperado \"IF\", encontrado " + "\"" + self.token.getLexema() + "\"")
        if (not self.eat(Tag.SMB_OPA)):
            self.sinalizaErroSintatico("Esperado \"(\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.expression()
        if (not self.eat(Tag.SMB_CPA)):
            self.sinalizaErroSintatico("Esperado \")\", encontrado " + "\"" + self.token.getLexema() + "\"")
        if (not self.eat(Tag.SMB_OBC)):
            self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.stmtList()
        if (not self.eat(Tag.SMB_CBC)):
            self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.ifStmtLinha()

    def ifStmtLinha(self):
        if (self.token.getNome() != Tag.SMB_SEM):
            if (not self.eat(Tag.KW_ELSE)):
                self.sinalizaErroSintatico("Esperado \"else\", encontrado " + "\"" + self.token.getLexema() + "\"")
            if (not self.eat(Tag.SMB_OBC)):
                self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.stmtList()
            if (not self.eat(Tag.SMB_CBC)):
                self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
            return True
        else:
            return False

    def whileStmt(self):
        self.stmtPrefix()
        if (not self.eat(Tag.SMB_OBC)):
            self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.stmtList()
        if (not self.eat(Tag.SMB_CBC)):
            self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def stmtPrefix(self):
        if (not self.eat(Tag.KW_WHILE)):
            self.sinalizaErroSintatico("Esperado \"while\", encontrado " + "\"" + self.token.getLexema() + "\"")
        if (not self.eat(Tag.SMB_OPA)):
            self.sinalizaErroSintatico("Esperado \"(\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.expression()
        if (not self.eat(Tag.SMB_CPA)):
            self.sinalizaErroSintatico("Esperado \")\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def readStmt(self):
        if (not self.eat(Tag.KW_READ)):
            self.sinalizaErroSintatico("Esperado \"read\", encontrado " + "\"" + self.token.getLexema() + "\"")
        if (not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def writeStmt(self):
        if (not self.eat(Tag.KW_WRITE)):
            self.sinalizaErroSintatico("Esperado \"write\", encontrado " + "\"" + self.token.getLexema() + "\"")
        self.simpleExpr()

    def expression(self):
        self.simpleExpr()
        self.expressionLinha()

    def expressionLinha(self):
        if (self.token.getNome() != Tag.SMB_CPA):
            self.logop()
            self.simpleExpr()
            self.expressionLinha()
            return True
        else:
            return False

    def simpleExpr(self):
        self.term()
        self.simpleExprLinha()

    def simpleExprLinha(self):
        if (self.token.getNome() != Tag.KW_OR and
            self.token.getNome() != Tag.KW_AND and
            self.token.getNome() != Tag.SMB_CPA and
            self.token.getNome() != Tag.SMB_SEM ):

            self.relop()
            self.term()
            self.simpleExprLinha()
            return True
        else:
            return False

    def term(self):
        self.factorB()
        self.termLinha()

    def termLinha(self):
        if (self.token.getNome() != Tag.OP_EQ and
            self.token.getNome() != Tag.OP_GT and
            self.token.getNome() != Tag.OP_GE and
            self.token.getNome() != Tag.OP_LT and
            self.token.getNome() != Tag.OP_LE and
            self.token.getNome() != Tag.OP_NE and
            self.token.getNome() != Tag.KW_OR and
            self.token.getNome() != Tag.KW_AND and
            self.token.getNome() != Tag.SMB_CPA and
            self.token.getNome() != Tag.SMB_SEM):

            self.addop()
            self.factorB()
            self.termLinha()
            return True
        else:
            return False

    def factorB(self):
        self.factorA()
        self.factorBLinha()

    def factorBLinha(self):
        if (self.token.getNome() != Tag.OP_AD and
            self.token.getNome() != Tag.OP_MIN and
            self.token.getNome() != Tag.OP_EQ and
            self.token.getNome() != Tag.OP_GT and
            self.token.getNome() != Tag.OP_GE and
            self.token.getNome() != Tag.OP_LT and
            self.token.getNome() != Tag.OP_LE and
            self.token.getNome() != Tag.OP_NE and
            self.token.getNome() != Tag.KW_OR and
            self.token.getNome() != Tag.KW_AND and
            self.token.getNome() != Tag.SMB_CPA and
            self.token.getNome() != Tag.SMB_SEM):

            self.mulop()
            self.factorA()
            self.factorBLinha()
            return True
        else:
            return False

    def factorA(self):
        if (self.token.getNome() == Tag.ID or
            self.token.getNome() == Tag.CHAR_CONST or
            self.token.getNome() == Tag.NUM_CONST or
            self.token.getNome() == Tag.SMB_OPA):

            self.factor()
        else:
            if (not self.eat(Tag.KW_NOT)):
                self.sinalizaErroSintatico("Esperado \"not\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.factor()

    def factor(self):
        if(self.token.getNome() == Tag.ID):
            if (not self.eat(Tag.ID)):
                self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.CHAR_CONST or self.token.getNome() == Tag.NUM_CONST):
            self.constant()
        else:
            if (not self.eat(Tag.SMB_OPA)):
                self.sinalizaErroSintatico("Esperado \"(\", encontrado " + "\"" + self.token.getLexema() + "\"")
            self.expression()
            if (not self.eat(Tag.SMB_CPA)):
                self.sinalizaErroSintatico("Esperado \")\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def logop(self):
        if (self.token.getNome() == Tag.KW_OR):
            if (not self.eat(Tag.KW_OR)):
                self.sinalizaErroSintatico("Esperado \"or\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.KW_AND):
            if (not self.eat(Tag.KW_AND)):
                self.sinalizaErroSintatico("Esperado \"and\", encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"or, and\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def relop(self):
        if (self.token.getNome() == Tag.OP_EQ):
            if (not self.eat(Tag.OP_EQ)):
                self.sinalizaErroSintatico("Esperado \"==\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_GT):
            if (not self.eat(Tag.OP_GT)):
                self.sinalizaErroSintatico("Esperado \">\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_GE):
            if (not self.eat(Tag.OP_GE)):
                self.sinalizaErroSintatico("Esperado \">=\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_LT):
            if (not self.eat(Tag.OP_LT)):
                self.sinalizaErroSintatico("Esperado \"<\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_LE):
            if (not self.eat(Tag.OP_LE)):
                self.sinalizaErroSintatico("Esperado \"<=\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_NE):
            if (not self.eat(Tag.OP_NE)):
                self.sinalizaErroSintatico("Esperado \"!=\", encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"==, >, >=, <, <=, !=\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def addop(self):
        if (self.token.getNome() == Tag.OP_AD):
            if (not self.eat(Tag.OP_AD)):
                self.sinalizaErroSintatico("Esperado \"+\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_MIN):
            if (not self.eat(Tag.OP_MIN)):
                self.sinalizaErroSintatico("Esperado \"-\", encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"+ ou -\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def mulop(self):
        if (self.token.getNome() == Tag.OP_MUL):
            if (not self.eat(Tag.OP_MUL)):
                self.sinalizaErroSintatico("Esperado \"*\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.OP_MIN):
            if (not self.eat(Tag.OP_DIV)):
                self.sinalizaErroSintatico("Esperado \"/\", encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"* ou /\", encontrado " + "\"" + self.token.getLexema() + "\"")

    def constant(self):
        if (self.token.getNome() == Tag.NUM_CONST):
            if (not self.eat(Tag.NUM_CONST)):
                self.sinalizaErroSintatico("Esperado \"num\", encontrado " + "\"" + self.token.getLexema() + "\"")
        elif (self.token.getNome() == Tag.CHAR_CONST):
            if (not self.eat(Tag.CHAR_CONST)):
                self.sinalizaErroSintatico("Esperado \"char\", encontrado " + "\"" + self.token.getLexema() + "\"")
        else:
            self.sinalizaErroSintatico("Esperado \"num ou char\", encontrado " + "\"" + self.token.getLexema() + "\"")