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
        "nextPc": 1
}

initialIdEx = {
        "pc": 0,
        "valA": 0,
        "valB": 0,
        "offset": 0,
        "dest": None,
        "op": "noop"
}

initialExMem = {
        "target": 0,
        "eq": False,
        "result": 0,
        "valB": 0,
        "dest": None,
        "op": "noop"
}

initialMemWb = {
        "result": 0,
        "mdata": None,
        "dest": None,
        "op": "noop",
}

def file_read(nomeArquivo):
        global memoria
        arquivo = open(nomeArquivo, 'r')

        for index, linha in enumerate(arquivo):
                memoria[index] = linha.removesuffix("\n")

def busca():
        global pc
        global initialIfId
        global memoria


        initialIfId["instrucao"] = memoria[initialIfId["pc"]]
        initialIfId["pc"] = initialIfId["nextPc"]

        if (initialExMem["op"] == "beq" and initialExMem["eq"]):
                initialIfId["nextPc"] = initialExMem["target"]
        else:
                initialIfId["nextPc"] = initialIfId["nextPc"] + 1



def decodifica(decodificaPc: int, instrucao: str):
        global initialIdEx
        if(not isinstance(instrucao, str)):
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": "noop"
                }
                return
        instrucaoSplited: list[str] = instrucao.split(" ")
        instrucaoLen = len(instrucaoSplited)
        op: str = instrucaoSplited[0]
        valAIndex: int = None if(instrucaoLen < 2) else int(instrucaoSplited[1])
        valBIndex: int = None if(instrucaoLen < 3) else int(instrucaoSplited[2])
        offset: int = None if(instrucaoLen < 4) else int(instrucaoSplited[3])


        if(op == "lw"):
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": registradores[valAIndex],
                        "valB": registradores[valBIndex],
                        "offset": offset,
                        "dest": None if(instrucaoLen < 3) else int(instrucaoSplited[2]),
                        "op": op
                }
                return


        if(op == "add"):
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": registradores[valAIndex],
                        "valB": registradores[valBIndex],
                        "offset": offset,
                        "dest": None if(instrucaoLen < 4) else int(instrucaoSplited[3]),
                        "op": op
                }
                return

        if (op == "noop" or op == "halt"):
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": op
                }
                return

        if (op == "beq"):
                initialIdEx = {
                        "pc": decodificaPc,
                        "valA": registradores[valAIndex],
                        "valB": registradores[valBIndex],
                        "offset": offset,
                        "dest": None,
                        "op": op
                }
                return

def executa(executaPc: int, valA: int, valB: int, offset: int, dest: int, op: str):
        global initialExMem
        global pc
        switch = {
                "lw": valA + offset,
                "noop": 0,
                "add": valA + valB,
                "sub": valA - valB,
                "beq": valA + valB,
                "halt": 0
        }

        initialExMem = {
                "target": offset + executaPc,
                "eq": valA == valB,
                "result": switch[op],
                "valB": valB,
                "dest": dest,
                "op": op
        }

def executaMemoria(result: int, dest: int, op: str):
        global initialMemWb
        mdata = None

        if(op == "lw"):
                mdata = memoria[result]

        initialMemWb = {
                "result": result,
                "mdata": mdata,
                "dest": dest,
                "op": op,
        }


def escreve(result: int, mdata: int, dest: int, op: str):
        if(op == "lw"):
                registradores[dest] = mdata
                return

        if (op == "add"):
                registradores[dest] = result

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

print(initialIfId)
print(initialIdEx)
print(initialExMem)
print(initialMemWb)

while initialMemWb["op"] != "halt":
        clock()
        count += 1


