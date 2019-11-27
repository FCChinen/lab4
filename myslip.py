class CamadaEnlace:
    def __init__(self, linhas_seriais):
        """
        Inicia uma camada de enlace com um ou mais enlaces, cada um conectado
        a uma linha serial distinta. O argumento linhas_seriais é um dicionário
        no formato {ip_outra_ponta: linha_serial}. O ip_outra_ponta é o IP do
        host ou roteador que se encontra na outra ponta do enlace, escrito como
        uma string no formato 'x.y.z.w'. A linha_serial é um objeto da classe
        PTY (vide camadafisica.py) ou de outra classe que implemente os métodos
        registrar_recebedor e enviar.
        """
        self.enlaces = {}
        # Constrói um Enlace para cada linha serial
        for ip_outra_ponta, linha_serial in linhas_seriais.items():
            enlace = Enlace(linha_serial)
            self.enlaces[ip_outra_ponta] = enlace
            enlace.registrar_recebedor(self.callback)

    def registrar_recebedor(self, callback):
        """
        Registra uma função para ser chamada quando dados vierem da camada de enlace
        """
        self.callback = callback

    def enviar(self, datagrama, next_hop):
        """
        Envia datagrama para next_hop, onde next_hop é um endereço IPv4
        fornecido como string (no formato x.y.z.w). A camada de enlace se
        responsabilizará por encontrar em qual enlace se encontra o next_hop.
        """
        # Encontra o Enlace capaz de alcançar next_hop e envia por ele
        self.enlaces[next_hop].enviar(datagrama)

    def callback(self, datagrama):
        if self.callback:
            self.callback(datagrama)


class Enlace:
    #Atributo novo
    dgram = b''
    veiodb = False

    def __init__(self, linha_serial):
        self.linha_serial = linha_serial
        self.linha_serial.registrar_recebedor(self.__raw_recv)
        self.dgram = b''

    def registrar_recebedor(self, callback):
        self.callback = callback

    def enviar(self, datagrama):
        # TODO: Preencha aqui com o código para enviar o datagrama pela linha
        # serial, fazendo corretamente a delimitação de quadros e o escape de
        # sequências especiais, de acordo com o protocolo SLIP (RFC 1055).
        #teste2
        new_datagram = b''
        #utilizar o for sozinho para iterar sobre o datagrama, que é um objeto
        #do tipo byte não é possível!
        #Essa estrutura cria uma lista de bytes do datagrama
        lbytes =[datagrama[i:i+1] for i in range(len(datagrama))] 
        for byte in lbytes:
            if not(isinstance(byte, (bytes))):
                byte = bytes(byte)
            if byte == b'\xc0':
                new_datagram = new_datagram + b'\xdb' + b'\xdc'
            elif byte == b'\xdb':
                new_datagram = new_datagram + b'\xdb' + b'\xdd'
            else:
                new_datagram = new_datagram + byte 
        #teste2
        #teste1
        new_datagram = b'\xc0'+new_datagram+b'\xc0'
        self.linha_serial.enviar(new_datagram);
        #teste1


    def __raw_recv(self, dados):
        # TODO: Preencha aqui com o código para receber dados da linha serial.
        # Trate corretamente as sequências de escape. Quando ler um quadro
        # completo, repasse o datagrama contido nesse quadro para a camada
        # superior chamando self.callback. Cuidado pois o argumento dados pode
        # vir quebrado de várias formas diferentes - por exemplo, podem vir
        # apenas pedaços de um quadro, ou um pedaço de quadro seguido de um
        # pedaço de outro, ou vários quadros de uma vez só.
        lbytes = [dados[i:i+1] for i in range(len(dados))]
        datagramlbytes = [self.dgram[i:i+1] for i in range(len(self.dgram))]
        datagrama = b''
        for i in range(len(lbytes)):
            if lbytes[i] == b'\xc0' and self.dgram != b'':
                self.callback(self.dgram)
                self.dgram = b''
            elif self.veiodb == True:
                if lbytes[i] == b'\xdc':
                    self.dgram = self.dgram + b'\xc0'
                    self.veiodb = False
                elif lbytes[i] == b'\xdd':
                    self.dgram = self.dgram + b'\xdb'
                    self.veiodb = False
            elif lbytes[i] == b'\xdb':
                self.veiodb = True
            elif lbytes[i] != b'\xc0':
                self.dgram += lbytes[i]
