invalidInstructions = 0
totalInstructions = 0

predictionCounter = {}
predictionType = None

# Initializes memory
memory = [0] * 256

registers = [0] * 32
registers[0] = 0
pc = 0

resultIfId = {
        "instruction": "noop",
        "pc": 0,
        "nextPc": 1,
}

resultIdEx = {
        "pc": 0,
        "valA": 0,
        "valB": 0,
        "offset": 0,
        "dest": None,
        "op": "noop",
}

resultExMem = {
        "target": 0,
        "eq": False,
        "result": 0,
        "valB": 0,
        "dest": None,
        "op": "noop",
        "pc": 0,
}

resultMemWb = {
        "result": 0,
        "mdata": None,
        "dest": None,
        "op": "noop",
}

def fileRead(fileName):
    global memory
    with open(fileName, 'r') as file:
        for index, line in enumerate(file):
            memory[index] = line.strip()

def fetch():
        global pc
        global resultIfId
        global memory
        global totalInstructions

        # Fetch instruction
        resultIfId["instruction"] = memory[resultIfId["pc"]]
        resultIfId["pc"] = resultIfId["nextPc"]
        totalInstructions += 1

def decode(internalPc: int, instruction: str):
        global resultIdEx
        global registers

        if not isinstance(instruction, str):
                resultIdEx = {
                        "pc": internalPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": None,
                }
                return
        
        splitedInstruction = instruction.strip().split(" ")
        instructionLen = len(splitedInstruction)
        op = splitedInstruction[0]
        valAIndex = int(splitedInstruction[1]) if instructionLen > 1 else None
        valBIndex = int(splitedInstruction[2]) if instructionLen > 2 else None
        offset = int(splitedInstruction[3]) if instructionLen > 3 else 0

        if op == "noop" or op == "halt":
                resultIdEx = {
                        "pc": internalPc,
                        "valA": 0,
                        "valB": 0,
                        "offset": 0,
                        "dest": None,
                        "op": op,
                }
                return

        resultIdEx = {
                "pc": internalPc,
                "valA": registers[valAIndex] if valAIndex is not None else 0,
                "valB": registers[valBIndex] if valBIndex is not None else 0,
                "offset": offset,
                "dest": None,
                "op": op,
        }

        if op == "lw":
                resultIdEx["dest"] = valBIndex
        elif op == "add":
               resultIdEx["dest"] = offset

def exec(internalPc: int, valA: int, valB: int, offset: int, dest: int, op: str):
        global resultExMem
        global resultIfId
        global resultIdEx

        # Execute instruction by op
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
        target = internalPc + offset

        resultExMem = {
                "target": target,
                "eq": eq,
                "result": result,
                "valB": valB,
                "dest": dest,
                "op": op,
                "pc": internalPc - 1,
        }

def execMem(result: int, dest: int, op: str):
        global resultMemWb
        mdata = None

        if op == "lw":
                mdata = memory[result]

        resultMemWb = {
                "result": result,
                "mdata": mdata,
                "dest": dest,
                "op": op,
        }

def write(result: int, mdata: int, dest: int, op: str):
        global registers

        if op == "lw":
                registers[dest] = mdata
                return

        if op == "add":
                registers[dest] = result

instructionCounter = 0

def handlePredictionCounter():
        global predictionCounter
        global resultExMem

        predictionCounter[resultExMem["pc"]] = 1 if resultExMem["eq"] else 0

def handleStaticPrediction():
        global resultExMem
        global resultIfId
        global resultIdEx
        global invalidInstructions

        if resultExMem["op"] == "beq" and resultExMem["eq"]:
                resultIfId["instruction"] = "noop"
                resultIfId["nextPc"] = resultExMem["target"]
                resultIdEx["valA"] = 0
                resultIdEx["valB"] = 0
                resultIdEx["dest"] = None
                resultIdEx["op"] = "noop"
                invalidInstructions += 2
        else:
                resultIfId["nextPc"] = resultIfId["nextPc"] + 1

def handleDynamicTakeAction():
        global resultIdEx
        global predictionCounter
        global resultIfId

        if resultIdEx["op"] == "beq":
                oldTakenAction = predictionCounter.get(resultIdEx["pc"] - 1)

                if oldTakenAction == 1:
                        resultIfId["instruction"] = "noop"
                        resultIfId["nextPc"] = resultIdEx["offset"] + resultIdEx["pc"]
                else:
                        resultIfId["nextPc"] = resultIfId["nextPc"] + 1
        else:
                resultIfId["nextPc"] = resultIfId["nextPc"] + 1

def handleDynamicPredictionValidation():
        global predictionCounter
        global resultExMem
        global resultIfId
        global resultIdEx
        global invalidInstructions

        oldTakenAction = predictionCounter.get(resultExMem["pc"]) if predictionCounter.get(
                resultExMem["pc"]) != None else 0

        if oldTakenAction == 0 and resultExMem["eq"]:
                resultIfId["instruction"] = "noop"
                resultIfId["nextPc"] = resultExMem["target"]
                resultIdEx["valA"] = 0
                resultIdEx["valB"] = 0
                resultIdEx["dest"] = None
                resultIdEx["op"] = "noop"
                invalidInstructions += 2
        elif oldTakenAction == 1 and not resultExMem["eq"]:
                resultIfId["instruction"] = "noop"
                resultIfId["nextPc"] = resultExMem["pc"] + 1
                resultIdEx["valA"] = 0
                resultIdEx["valB"] = 0
                resultIdEx["dest"] = None
                resultIdEx["op"] = "noop"
                invalidInstructions += 2
        else:
                handleDynamicTakeAction()

def clock():
        global pc
        global resultExMem
        global resultIdEx
        global resultIfId
        global resultMemWb
        global invalidInstructions
        global predictionCounter
        global predictionType

        write(resultMemWb["result"], resultMemWb["mdata"], resultMemWb["dest"], resultMemWb["op"])
        execMem(resultExMem["result"], resultExMem["dest"], resultExMem["op"])
        exec(resultIdEx["pc"], resultIdEx["valA"], resultIdEx["valB"], resultIdEx["offset"], resultIdEx["dest"], resultIdEx["op"])
        decode(resultIfId["pc"], resultIfId["instruction"])
        fetch()

        if predictionType == "static":
                handleStaticPrediction()
        elif predictionType == "dynamic":
                if resultExMem["op"] == "beq":
                        handleDynamicPredictionValidation()
                        handlePredictionCounter()
                else:
                        handleDynamicTakeAction()
        else:
                resultIfId["nextPc"] = resultIfId["nextPc"] + 1

predictionType = input("Selecione um tipo de predição (static, dynamic ou no prediction): ")
fileToRead = input("Digite o nome do arquivo para ser lido: ")

while True:
        memoryInput = input("Digite a posição da memória para preencher (para sair, digite um valor inválido de memória): ")

        if int(memoryInput) < 0 or int(memoryInput) > 255:
                break

        memoryValue = input("Digite o valor para preencher na posição acima: ")

        memory[int(memoryInput)] = int(memoryValue)

fileRead(fileToRead)

print(resultIfId)
print(resultIdEx)
print(resultExMem)
print(resultMemWb)
print(registers)

def printDynamicPrediction():
        if predictionType == "dynamic":
                print("Tabela de predição de 1 bit: ")
                print("PC  |  Última predição: ")
                for key, value in predictionCounter.items():
                        print(key, "  |  ", value)

while resultMemWb["op"] != "halt":
        clock()

        print("\n\n\n")
        print("### INSTRUÇÃO ", instructionCounter, " ###")
        print("IF/ID: instruction: ", resultIfId["instruction"], " pc: ", resultIfId["pc"])
        print("ID/EX: pc: ", resultIdEx["pc"], " valA: ", resultIdEx["valA"], " valB: ", resultIdEx["valB"], " offset: ", resultIdEx["offset"], " dest: ", resultIdEx["dest"], " op: ", resultIdEx["op"])
        print("EX/MEM: target: ", resultExMem["target"], " eq: ", resultExMem["eq"], " result: ", resultExMem["result"], " valB: ", resultExMem["valB"], " dest: ", resultExMem["dest"], " op: ", resultExMem["op"], " pc: ")
        print("MEM/WB: result: ", resultMemWb["result"], " mdata: ", resultMemWb["mdata"], " dest: ", resultMemWb["dest"], " op: ", resultMemWb["op"])
        print("Registradores: ", registers)
        printDynamicPrediction()

        instructionCounter += 1

print("\n\n\n")
print("RESULTADOS FINAIS")
print("Instruções totais: ", totalInstructions)
print("Instruções inválidas: ", invalidInstructions)
printDynamicPrediction()