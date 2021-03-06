import sys

from ts import TS
from tag import Tag
from token import Token

class Lexer():
   '''
   Classe que representa o Lexer:
   '''
   def __init__(self, input_file):
      try:
         self.input_file = open(input_file, 'rb')
         self.lookahead = 0
         self.n_line = 1
         self.n_column = 1
         self.ts = TS()
      except IOError:
         print('Erro de abertura do arquivo. Encerrando.')
         sys.exit(0)

   def closeFile(self):
      try:
         self.input_file.close()
      except IOError:
         print('Erro dao fechar arquivo. Encerrando.')
         sys.exit(0)

   def sinalizaErroLexico(self, message):
      print("[Erro Lexico]: ", message, "\n")

   def retornaPonteiro(self):
      if(self.lookahead.decode('ascii') != ''):
         self.input_file.seek(self.input_file.tell()-1)

   def printTS(self):
      self.ts.printTS()

   def proxToken(self):
      estado = 1
      lexema = ""
      c = '\u0000'

      while(True):
         self.lookahead = self.input_file.read(1)
         c = self.lookahead.decode('ascii')

         if(estado == 1):
            if(c == ''):
               return Token(Tag.EOF, "EOF", self.n_line, self.n_column)

            elif (c == ' ' or c == '\r'):
               self.n_column = self.n_column + 1
               estado = 1

            elif (c == '\t'):
               self.n_column = self.n_column + 3
               estado = 1

            elif (c == '\n'):
               self.n_column = 0
               self.n_line = self.n_line + 1
               estado = 1

            elif(c == '='):
               estado = 2

            elif(c == '!'):
               estado = 4

            elif(c == '<'):
               estado = 6

            elif(c == '>'):
               estado = 9

            elif(c.isdigit()):
               lexema += c
               estado = 12

            elif(c.isalpha()):
               lexema += c
               estado = 14

            elif(c == '/'):
               estado = 16
            
            elif(c == '.'):
               estado = 12

            elif(c == '*'):
               estado = 21
            
            elif(c == '-'):
               estado = 22

            elif(c == '+'):
               estado = 23

            elif(c == '{'):
               return Token(Tag.SMB_OBC, "{", self.n_line, self.n_column)

            elif(c == '}'):
               return Token(Tag.SMB_CBC, "}", self.n_line, self.n_column)
            
            elif(c == '('):
               estado = 27

            elif(c == ')'):
               estado = 28

            elif(c == ','):
               estado = 29

            elif(c == ';'):
               estado = 30

            elif(c == '"'):
               estado = 31

            else:
               self.sinalizaErroLexico("Caractere invalido [" + c + "] na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None

         elif(estado == 2):
            if(c == '='):
               return Token(Tag.OP_EQ, "==", self.n_line, self.n_column)
            else:
               self.retornaPonteiro()
               return Token(Tag.OP_ATRIB, "=", self.n_line, self.n_column)

         elif(estado == 4):
            if(c == '='):
               return Token(Tag.OP_NE, "!=", self.n_line, self.n_column)
            else:
               self.sinalizaErroLexico("Caractere invalido [" + c + "] na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None

         elif(estado == 6):
            if(c == '='):
               return Token(Tag.OP_LE, "<=", self.n_line, self.n_column)
            else:
               self.retornaPonteiro()
               return Token(Tag.OP_LT, "<", self.n_line, self.n_column)

         elif(estado == 9):
            if(c == '='):
               return Token(Tag.OP_GE, ">=", self.n_line, self.n_column)
            else:
               self.retornaPonteiro()
               return Token(Tag.OP_GT, ">", self.n_line, self.n_column)

         elif(estado == 12):
            if(c.isdigit()):
               lexema += c

            elif(c == '.'):
               lexema += c
               estado = 18
            else:
               self.retornaPonteiro()
               return Token(Tag.NUM_CONST, lexema, self.n_line, self.n_column)

         elif(estado == 14):
            if(c.isalnum()):
               lexema += c
            else:
               self.retornaPonteiro()
               token = self.ts.getToken(lexema)
               if(token is None):
                  token = Token(Tag.ID, lexema, self.n_line, self.n_column)
                  self.ts.addToken(lexema, token)
               return token

         elif(estado == 35):
            if(c == '/'):
               estado = 1
            else:
               estado = 34
         
         elif(estado == 34):
            if(c == '*'):
               estado = 35
            if(c == ''):
               self.sinalizaErroLexico("?? necessario fechar o comentario! linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None

         elif(estado == 17):
            if(c == '\n'):
               estado = 1

         elif(estado == 16):
            if(c == '/'):
               estado = 17
            elif(c == '\n'):
               estado = 1
            elif(c == '*'):
               estado = 34
            else:
               return Token(Tag.OP_DIV, "/", self.n_line, self.n_column)

         elif(estado == 18):
            if(c.isdigit()):
               lexema += c
               estado = 19
            else:
               self.sinalizaErroLexico("Padrao invalido para numero na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None

         elif(estado == 19):
            if(c.isdigit()):
               lexema += c
            else:
               self.retornaPonteiro()
               return Token(Tag.NUM_CONST, lexema, self.n_line, self.n_column)

         elif(estado == 21):
            self.retornaPonteiro()
            return Token(Tag.OP_MUL, "*", self.n_line, self.n_column)

         elif(estado == 22):
            self.retornaPonteiro()
            return Token(Tag.OP_MIN, "-", self.n_line, self.n_column)
            
         elif(estado == 23):
            self.retornaPonteiro()
            return Token(Tag.OP_AD, "+", self.n_line, self.n_column)
         
         elif(estado == 27):
            self.retornaPonteiro()
            return Token(Tag.SMB_OPA, "(", self.n_line, self.n_column)
         
         elif(estado == 28):
            self.retornaPonteiro()
            return Token(Tag.SMB_CPA, ")", self.n_line, self.n_column)
         
         elif(estado == 29):
            self.retornaPonteiro()
            return Token(Tag.SMB_COM, ",", self.n_line, self.n_column)
         
         elif(estado == 30):
            self.retornaPonteiro()
            return Token(Tag.SMB_SEM, ";", self.n_line, self.n_column)
         
         elif(estado == 32):
            if(c=='\n'):
               self.sinalizaErroLexico("Verifique as aspas! Na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None
            elif (c == '"'):
               return Token(Tag.CHAR_CONST, lexema, self.n_line, self.n_column)
            elif(c.isascii()):
               lexema += c
            else:
               self.sinalizaErroLexico("Caractere invalido [" + c + "] na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None

         elif(estado == 31):
            if(c=='\n'):
               self.sinalizaErroLexico("Voce possui aspas sem fechamento! Na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None
            elif(c.isascii()):
               estado = 32
               lexema += c
            else:
               self.sinalizaErroLexico("Caractere invalido [" + c + "] na linha " +
               str(self.n_line) + " e coluna " + str(self.n_column))
               return None

         else:
            self.sinalizaErroLexico("Caractere desconhecido na linha " +
            str(self.n_line) + " e coluna " + str(self.n_column))
            return None
         # fim if's de estados
      # fim while
