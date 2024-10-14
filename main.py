# Date: 01/10/2024

# Incializa a memória com 256 posições
memoria = [0] * 256

# case 1
memoria[16] = -1
memoria[17] = 10
memoria[18] = 1

# case 2
# memoria[10] = -1
# memoria[11] = 10
# memoria[12] = 1

registradores = [0] * 32
registradores[0] = 0
pc = 0

initialIfId = {
        "instrucao": "noop",
        "pc": 0,
        "nextPc": 1,
        "valid": True
}

initialIdEx = {
        "pc": 0,
        "valA": 0,
        "valB": 0,
        "offset": 0,
        "dest": None,
        "op": "noop",
        "valid": True
}

initialExMem = {
        "target": 0,
        "eq": False,
        "result": 0,
        "valB": 0,
        "dest": None,
        "op": "noop",
        "valid": True
}

initialMemWb = {
        "result": 0,
        "mdata": None,
        "dest": None,
        "op": "noop",
        "valid": True
}

def file_read(nomeArquivo):
    global memoria
    with open(nomeArquivo, 'r') as arquivo:
        for index, linha in enumerate(arquivo):
            memoria[index] = linha.strip()


def busca():
        global pc
        global initialIfId
        global memoria

        if initialIfId["valid"]:
               # intrucao fetch 
                initialIfId["instrucao"] = memoria[initialIfId["pc"]]
                initialIfId["pc"] = initialIfId["nextPc"]

                if initialExMem["op"] == "beq" and initialExMem["eq"]:
                        # a instrução é um branch e a condição é verdadeira
                        initialIfId["nextPc"] = initialExMem["target"]
                else:
                        initialIfId["nextPc"] = initialIfId["nextPc"] + 1
        else:
               initialIfId["instrucao"] = "noop"
               initialIfId["valid"] = True # Resetar a flag para a próxima instrução



def decodifica(decodificaPc: int, instrucao: str):
        global initialIdEx
        if not isinstance(instrucao, str) or instrucao == "noop":
               # nenhuma instrucao para decodificar
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": "noop",
                        "valid": False
                }
                return
        
        instrucaoSplited = instrucao.strip().split(" ")
        instrucaoLen = len(instrucaoSplited)
        op = instrucaoSplited[0]
        valAIndex = int(instrucaoSplited[1]) if instrucaoLen > 1 else None
        valBIndex = int(instrucaoSplited[2]) if instrucaoLen > 2 else None
        offset = int(instrucaoSplited[3]) if instrucaoLen > 3 else 0

        initialIdEx = {
                "pc": decodificaPc,
                "valA": registradores[valAIndex] if valAIndex is not None else 0,
                "valB": registradores[valBIndex] if valBIndex is not None else 0,
                "offset": offset,
                "dest": None,
                "op": op,
                "valid": True
        }

        if op == "lw":
                initialIdEx["dest"] = valBIndex
        elif op == "add":
               initialIdEx["dest"] = offset # NO caso de add o offset é o destino já que é o terceiro parametro


def executa(executaPc: int, valA: int, valB: int, offset: int, dest: int, op: str):
        global initialExMem
        if not initialIdEx["valid"]:
                initialExMem = {
                        "target": 0,
                        "eq": False,
                        "result": 0,
                        "valB": 0,
                        "dest": None,
                        "op": "noop",
                        "valid": False
                }
                return
        
        # executa a instrução baseado no op
        if op == "lw":
                result = valA + offset
        elif op == "add":
                result = valA + valB
        elif op == "sub": 
                result = valA - valB
        elif op == "beq":
               result = 0 
        elif op == "halt":
                result = 0
        else:
                result = 0

        eq = (valA == valB)
        target = executaPc + offset

        initialExMem = {
                "target": target,
                "eq": eq,
                "result": result,
                "valB": valB,
                "dest": dest,
                "op": op,
                "valid": True
        }

        # cuidar da instrução de branch
        if op == "beq":
               if eq:
                      # uma misprediction ocorreu
                      initialIfId["valid"] = False
                      initialIdEx["valid"] = False
                      # atualiza o pc para o target
                      initialIfId["nextPc"] = target

def executaMemoria(result: int, dest: int, op: str):
        global initialMemWb
        if not initialExMem["valid"]:
                initialMemWb = {
                        "result": 0,
                        "mdata": None,
                        "dest": None,
                        "op": "noop",
                        "valid": False
                }
                return

        mdata = None

        if op == "lw":
                mdata = memoria[result]
        elif op == "sw":
                memoria[result] = registradores[dest]

        initialMemWb = {
                "result": result,
                "mdata": mdata,
                "dest": dest,
                "op": op,
                "valid": True
        }


def escreve(result: int, mdata: int, dest: int, op: str):
        if not initialMemWb["valid"]:
                return
        
        if op == "lw":
                registradores[dest] = int(mdata)
        elif op == "add" or op == "sub":
                registradores[dest] = result
        
        # para o resto das instruções não é necessário escrever no registrador

count = 1

def clock():
        global pc
        global initialExMem
        escreve(initialMemWb["result"], initialMemWb["mdata"], initialMemWb["dest"], initialMemWb["op"])
        executaMemoria(initialExMem["result"], initialExMem["dest"], initialExMem["op"])
        executa(initialIdEx["pc"], initialIdEx["valA"], initialIdEx["valB"], initialIdEx["offset"], initialIdEx["dest"], initialIdEx["op"])
        decodifica(initialIfId["pc"], initialIfId["instrucao"])
        busca()

        print("\n\n\n")
        print("### CICLO ", count, " ###")
        print(initialIfId)
        print(initialIdEx)
        print(initialExMem)
        print(initialMemWb)
        print(registradores)


file_read("case1.txt")

#Inicializa a pipeline
print(initialIfId)
print(initialIdEx)
print(initialExMem)
print(initialMemWb)
print(registradores)

while initialMemWb["op"] != "halt":
        clock()
        count += 1


