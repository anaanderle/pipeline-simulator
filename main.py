# Date: 01/10/2024

instrucoesInvalidas = 0
instrucoesTotais = 0

# Incializa a memória com 256 posições
memoria = [0] * 256

# case 1
# memoria[16] = -1
# memoria[17] = 10
# memoria[18] = 1

# case 2
memoria[10] = -1
memoria[11] = 10
memoria[12] = 1

registradores = [0] * 32
registradores[0] = 0
pc = 0

initialIfId = {
        "instrucao": "noop",
        "pc": 0,
        "nextPc": 1,
}

initialIdEx = {
        "pc": 0,
        "valA": 0,
        "valB": 0,
        "offset": 0,
        "dest": None,
        "op": "noop",
}

initialExMem = {
        "target": 0,
        "eq": False,
        "result": 0,
        "valB": 0,
        "dest": None,
        "op": "noop",
}

initialMemWb = {
        "result": 0,
        "mdata": None,
        "dest": None,
        "op": "noop",
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
        global instrucoesTotais

        # instrucao fetch
        initialIfId["instrucao"] = memoria[initialIfId["pc"]]
        initialIfId["pc"] = initialIfId["nextPc"]
        instrucoesTotais += 1

def decodifica(decodificaPc: int, instrucao: str):
        global initialIdEx
        if not isinstance(instrucao, str):
               # nenhuma instrucao para decodificar
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": None,
                }
                return
        
        instrucaoSplited = instrucao.strip().split(" ")
        instrucaoLen = len(instrucaoSplited)
        op = instrucaoSplited[0]
        valAIndex = int(instrucaoSplited[1]) if instrucaoLen > 1 else None
        valBIndex = int(instrucaoSplited[2]) if instrucaoLen > 2 else None
        offset = int(instrucaoSplited[3]) if instrucaoLen > 3 else 0

        if op == "noop" or op == "halt":
               # nenhuma instrucao para decodificar
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": op,
                }
                return

        initialIdEx = {
                "pc": decodificaPc,
                "valA": registradores[valAIndex] if valAIndex is not None else 0,
                "valB": registradores[valBIndex] if valBIndex is not None else 0,
                "offset": offset,
                "dest": None,
                "op": op,
        }

        if op == "lw":
                initialIdEx["dest"] = valBIndex
        elif op == "add":
               initialIdEx["dest"] = offset # NO caso de add o offset é o destino já que é o terceiro parametro


def executa(executaPc: int, valA: int, valB: int, offset: int, dest: int, op: str):
        global initialExMem
        global initialIfId
        global initialIdEx

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
        }

def executaMemoria(result: int, dest: int, op: str):
        global initialMemWb
        mdata = None

        if op == "lw":
                mdata = memoria[result]

        initialMemWb = {
                "result": result,
                "mdata": mdata,
                "dest": dest,
                "op": op,
        }


def escreve(result: int, mdata: int, dest: int, op: str):
        if (op == "lw"):
                registradores[dest] = mdata
                return

        if (op == "add"):
                registradores[dest] = result

count = 1

def clock():
        global pc
        global initialExMem
        global initialIdEx
        global initialIfId
        global initialMemWb
        global instrucoesInvalidas

        escreve(initialMemWb["result"], initialMemWb["mdata"], initialMemWb["dest"], initialMemWb["op"])
        executaMemoria(initialExMem["result"], initialExMem["dest"], initialExMem["op"])
        executa(initialIdEx["pc"], initialIdEx["valA"], initialIdEx["valB"], initialIdEx["offset"], initialIdEx["dest"], initialIdEx["op"])
        decodifica(initialIfId["pc"], initialIfId["instrucao"])
        busca()

        if initialExMem["op"] == "beq" and initialExMem["eq"]:
                # uma misprediction ocorreu
                initialIfId["instrucao"] = "noop"
                initialIfId["nextPc"] = initialExMem["target"]
                initialIdEx["valA"] = 0
                initialIdEx["valB"] = 0
                initialIdEx["dest"] = None
                initialIdEx["op"] = "noop"
                instrucoesInvalidas += 2
        else:
                initialIfId["nextPc"] = initialIfId["nextPc"] + 1

        print("\n\n\n")
        print("### CICLO ", count, " ###")
        print(initialIfId)
        print(initialIdEx)
        print(initialExMem)
        print(initialMemWb)
        print(registradores)


file_read("case2.txt")

#Valores iniciais
print(initialIfId)
print(initialIdEx)
print(initialExMem)
print(initialMemWb)
print(registradores)

while initialMemWb["op"] != "halt":
        clock()
        count += 1


print("Instruções totais: ", instrucoesTotais)
print("Instruções inválidas: ", instrucoesInvalidas)