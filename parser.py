import sys
import copy

from tag import Tag
from token import Token
from lexer import Lexer
from no import No

class Parser():

   def __init__(self, lexer):
      self.lexer = lexer
      self.token = lexer.proxToken() # Leitura inicial obrigatoria do primeiro simbolo
      if self.token is None: # erro no Lexer
        sys.exit(0)

   def sinalizaErroSemantico(self, message):
      print("[Erro Semantico] na linha " + str(self.token.getLinha()) + " e coluna " + str(self.token.getColuna()) + ": ")
      print(message, "\n")

   def sinalizaErroSintatico(self, message):
      print("[Erro Sintatico] na linha " + str(self.token.getLinha()) + " e coluna " + str(self.token.getColuna()) + ": ")
      print(message, "\n")

   def advance(self):
      print("[DEBUG] token: ", self.token.toString())
      self.token = self.lexer.proxToken()
      if self.token is None: # erro no Lexer
        sys.exit(0)
   
   def skip(self, message):
      self.sinalizaErroSintatico(message)
      self.advance()

   # verifica token esperado t 
   def eat(self, t):
      if(self.token.getNome() == t):
         self.advance()
         return True
      else:
         return False

   """
   LEMBRETE:
   Todas as decisoes do Parser, sao guiadas pela Tabela Preditiva (TP)
   """

   # Programa -> CMD EOF
   def Programa(self):
      self.Cmd()
      if(self.token.getNome() != Tag.EOF):
         self.sinalizaErroSintatico("Esperado \"EOF\"; encontrado " + "\"" + self.token.getLexema() + "\"")
         sys.exit(0)

   def Cmd(self):

      # armazena token corrente, uma vez que o ID pode ser consumido
      tempToken = copy.copy(self.token)

      # Cmd -> if E then { CMD } CMD'
      if(self.eat(Tag.KW_PROGRAM)):
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")

      if(self.eat(Tag.KW_NUM) or self.eat(Tag.KW_CHAR)):
         if(not self.eat(Tag.ID)):
            self.sinalizaErroSintatico("Esperado \"ID\", encontrado " + "\"" + self.token.getLexema() + "\"")

      if(self.eat(Tag.KW_IF)): 
         noE = self.E()
         if noE.tipo != Tag.BOOL:
            self.sinalizaErroSemantico("Expressao mal formada.")

         if(not self.eat(Tag.SMB_OBC)):
            self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
         self.Cmd()

         if(not self.eat(Tag.SMB_CBC)):
            self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
         self.CmdLinha()
      
      if(self.eat(Tag.SMB_SEM)):
         self.Cmd()

      if(self.eat(Tag.SMB_OBC)):
         self.Cmd()
         # noE = self.E()
         # if noE.tipo != Tag.BOOL:
         #    self.sinalizaErroSemantico("Expressao mal formada.")

         # if(not self.eat(Tag.SMB_OBC)):
         #    self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
         # self.Cmd()
         
         # if(not self.eat(Tag.SMB_CBC)):
         #    self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
         # self.CmdLinha()
      if(self.eat(Tag.OP_DIV)):
         self.Cmd()

      # Cmd -> id = T
      elif(self.eat(Tag.ID)):
         if(not self.eat(Tag.OP_ATRIB)):
            self.sinalizaErroSintatico("Esperado \"=\", encontrado " + "\"" + self.token.getLexema() + "\"")
       
         noT = self.T()

         if noT.tipo == Tag.NUM:
            self.lexer.ts.removeToken(tempToken.getLexema())
            tempToken.setTipo(noT.tipo)
            self.lexer.ts.addToken(tempToken.getLexema(), tempToken)
         elif noT.tipo == Tag.CHAR:
            self.lexer.ts.removeToken(tempToken.getLexema())
            tempToken.setTipo(noT.tipo)
            self.lexer.ts.addToken(tempToken.getLexema(), tempToken)
         else:
            self.sinalizaErroSemantico("Variável não declarada antes de atribuição")

   def CmdLinha(self):
      # CmdLinha -> else { CMD }
      if(self.eat(Tag.KW_ELSE)):
         if(not self.eat(Tag.SMB_OBC)):
            self.sinalizaErroSintatico("Esperado \"{\", encontrado " + "\"" + self.token.getLexema() + "\"")
         self.Cmd()
         if(not self.eat(Tag.SMB_CBC)):
            self.sinalizaErroSintatico("Esperado \"}\", encontrado " + "\"" + self.token.getLexema() + "\"")
      # CmdLinha -> epsilon
      elif(self.token.getNome() == Tag.SMB_CBC or self.token.getNome() == Tag.EOF or self.token.getNome() == Tag.SMB_SEM ):
         return
      else:
         self.skip("Esperado \"else, }\", encontrado " + "\"" + self.token.getLexema() + "\"")
         sys.exit(0)

   # E -> T T'
   def E(self):
      noE = No()
      if(self.token.getNome() == Tag.ID or self.token.getNome() == Tag.NUM_CONST or self.token.getNome() == Tag.CHAR_CONST ):
         noT = self.T()
         noTLinha = self.TLinha()
         if noTLinha.tipo == Tag.VOID:
            noE.tipo = noT.tipo

         elif noTLinha.tipo == noT.tipo and noT.tipo == Tag.NUM:
            noE.tipo = Tag.BOOL
            
         elif noTLinha.tipo == noT.tipo and noT.tipo == Tag.CHAR:
            noE.tipo = Tag.BOOL
          
         else:
            noE.tipo = Tag.ERRO
            return noE
      else:
         self.sinalizaErroSintatico("Esperado \"id, numero\", encontrado " + "\"" + self.token.getLexema() + "\"")
         sys.exit(0)

   '''
   Mudei um pouco essa implementacao para ficar mais simples.
   T' --> ">" T  | "<" T | ">=" T | 
          "<=" T | "==" T | "!=" T| epsilon
   '''
   def TLinha(self):
      noTLinha = No()
      if(self.eat(Tag.OP_GT) or self.eat(Tag.OP_LT) or self.eat(Tag.OP_GE) or 
         self.eat(Tag.OP_LE) or self.eat(Tag.OP_EQ) or self.eat(Tag.OP_NE)):
        noT = self.T()
        noTLinha.tipo = noT.tipo
        return noTLinha
      else:
         self.skip("Esperado \">, <, >=, <=, ==, !=, then\", encontrado " + "\"" + self.token.getLexema() + "\"")
         sys.exit(0)

   # T -> id | num
   def T(self):
      noT = No()

      # armazena token corrente, uma vez que o ID pode ser consumido
      tempToken = copy.copy(self.token) 

      if(self.eat(Tag.ID)):
          noT.tipo = tempToken.getTipo()
      elif(self.eat(Tag.NUM_CONST)):
         noT.tipo = Tag.NUM
      elif(self.eat(Tag.CHAR_CONST)):
         noT.tipo = Tag.CHAR
      else:
        self.skip("Esperado \"numero, id\", encontrado "  + "\"" + self.token.getLexema() + "\"")
        sys.exit(0)

      return noT
