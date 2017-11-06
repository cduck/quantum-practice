'''
Simulation of a small number of qubits with plotting of output probabilities

Example:
```
    import matplotlib.pyplot as plt
    from circuit import QuantumCircuit
    from gate import *
    from simFullState import simulate

    circuit = QuantumCircuit(3)
    reg = circuit[:]

    X(reg)
    H(reg[1])
    CX(reg[1], reg[2])

    result = simulate(circuit)
    print(result.registerProbs())
    result.plot()
```
'''

import matplotlib.pyplot as plt

from circuit import Gate, Qubit, QuantumCircuit
import gate
import gateOperators
from fullStateUtil import *
import util


supportedGates = {
    'M',
    # Single bit
    'I1',
    'X',
    'Y',
    'Z',
    'H',
    'S',
    'Sd',
    'T',
    'Td',
    'Rx',
    'Ry',
    'Rz',
    # Two bit
    'I2',
    'CX',
    'SWAP',
    'CRz',
    # TODO: Other two bit gates (Ising, etc.)
    # Three bit
    'I3',
    'CCX',
    'CCRz',
}


class SimulationError(Exception): pass


def plotResults(results, log=False, percent=False):
    if log:
        percent = False

    width = 0.75
    firstVal = next(iter(results.keys()))
    n = len(firstVal)
    xArr = np.array(tuple(sorted(util.toIntBE(k) for k in results)))
    xDiff = xArr[1:] - xArr[:-1]
    minXSpace = 1 if len(xDiff) < 1 else np.min(xDiff)
    width *= minXSpace
    yArr = np.array([results[k] for k in results])
    yArr = (yArr * 100 if percent else yArr) / np.sum(yArr)  # Normalize
    fmtStr = '{{:0{}b}}\n0x{{:0{}x}}'.format(n, (n+3)//4)
    xLabels = [fmtStr.format(v, util.toIntBE(util.toTupleBE(v, n)[::1])) for v in xArr]

    fig, ax = plt.subplots()
    rects = ax.bar(xArr, yArr, width, log=log) #, color='g')
    if log:
        ax.set_yscale('log', basey=2)
        #start, end = np.log2(ax.get_ylim())
        #ax.set_yticks(np.arange(start, end, stepsize))
    ax.set_ylabel('Probability * 100' if percent else 'Probability')
    ax.set_title('Results')
    ax.set_xticks(xArr)
    ax.set_xticklabels(xLabels, rotation='vertical')
    return fig

def findGateOp(name, args):
    try:
        if args:
            return getattr(gateOperators, name+'Gen')(*args)
        else:
            return getattr(gateOperators, name)
    except AttributeError:
        raise SimulationError('Unsupported gate \'{}\''.format(name)) from None
    except TypeError:
        raise SimulationError('Invalid gate arguments {} for \'{}\''.format(repr(args), name)) from None

def simulate(circuit, hisorySlice=None, continueResult=None, ignoreMGates=False):
    n = circuit.n
    history = circuit.history
    if hisorySlice is not None:
        historyRange = range(*hisorySlice.indices(len(history)))
    else:
        historyRange = range(len(history))
    if continueResult is not None:
        result = continueResult
        if n <= result.n:
            n = result.n
        else:
            result.psi = np.append(result.psi,
                            np.zeros(2**n - len(result.psi), dtype=result.psi.dtype))
            result.n = n
    else:
        result = Result(n)

    measureCount = circuit.countM()
    measureOrder = None
    if measureCount <= 0 or ignoreMGates:
        measureCount = 0
    else:
        bad = False
        if len(history) < n:
            bad = True
        else:
            lastNGates = history[-n:]
            measureOrder = []
            for g in lastNGates:
                if g.instanceOf(gate.M):
                    bitI = g.bits[0]
                    if bitI in measureOrder or bitI < 0 or bitI >= n:
                        bad = True
                        break
                    measureOrder.append(bitI)
                else:
                    bad = True
                    break
        if bad:
            raise NotImplementedError('Unsupported arrangement of measurement gates (mixed with other gates or not one per qubit)')
    result.measureOrder = measureOrder

    for h in historyRange:
        gateInst = history[h]
        if gateInst.instanceOf(gate.M):
            if not ignoreMGates:
                pass  # TODO: Measurements before end
        else:
            gateOp = findGateOp(gateInst.name, gateInst.args)
            result._applyGateOpToBits(gateOp, gateInst.bits)

    return result


class Result:
    def __init__(self, n):
        self.n = n
        self.psi = createZeroState(n)
        self.measureOrder = None
        self.measureOutput = []
        self.finalProbability = 1.0
    def _applyGateOpToBits(self, g, bitIList):
        sGate = swapGate(*tuple(i for i in range(self.n) if i not in bitIList), *bitIList)
        eGate = expandGate(g, self.n)
        self.psi = sGate.dot(self.psi)
        self.psi = eGate.dot(self.psi)
        self.psi = sGate.T.dot(self.psi)
    def _applyOperator(self, op):
        self.psi = op.dot(self.psi)
    def _measureBit(self, bitI):
        self.psi, bitVal, prob = measure(self.psi, bitI.__index__())
        measureOutput.append(bitVal)
        self.finalProbability *= prob
    def __repr__(self):
        return 'FullState('+repr(self.psi)+')'

    def continueSim(self, circuit, **kwargs):
        simulate(circuit, continueResult=self, **kwargs)

    def probOfMeasureBit(self, bitI, state=0):
        return probabilityOfMeasure(self.psi, bitI.__index__(), state=state)
    def registerProbs(self):
        if self.measureOrder:
            sGate = swapGate(*self.measureOrder)
            p = sGate.dot(self.psi)
        else:
            p = self.psi
        return exactMeasureResults(p)
    def previousMeasurements(self):
        return tuple(self.measureOutput)
    def probOfPreviousMeasurements(self):
        return self.finalProbability
    def plot(self, **kwargs):
        self.plotFig(**kwargs)
    def plotFig(self, **kwargs):
        return plotResults(self.registerProbs(), **kwargs)

