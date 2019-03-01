
import numpy as np

# Percents, based on random internet polls. updated at 2019-03-01
# https://www.israelhayom.co.il/article/637177
CANDIDATES = {
    "KAHOL_LAVAN": 18.6,
    "LIKUD": 13.7,
    "HABAIT_HAYEHUDI": 4.9,
    "HAYAMIN_HAHADASH": 4.2,
    "MERETZ": 3.5,
    "HAAVODA": 3.5,
    "YAHADUT_HATORA": 3.5,
    "TAAL_HADASH": 3.5,
    "SHAS": 2.8,
    "ZEHUT": 2.1,
    "KULANU": 2.1,
    "GESHER": 1.4,
    "YISRAEL_BEITENU": 1.4,
    "RAAM_BALAD": 0.7,
    "PETEK_LAVAN": 2.1, # Based upon percent in 2013 & 2015
    None: 30, # non-voting. Based upon voting percent in 2013 & 2015
}

# Speculation
SURPLUS_AGREEMENT = [
    ("KAHOL_LAVAN", "HAAVODA"),
    ("LIKUD", "HABAIT_HAYEHUDI"),
    ("HAYAMIN_HAHADASH", "ZEHUT"),
    ("MERETZ", "TAAL_HADASH"),
    ("YAHADUT_HATORA", "SHAS"),
    ("KULANU", "GESHER"),
    ("YISRAEL_BEITENU",),
    ("RAAM_BALAD",),
]

I_TO_KEY = dict()
KEY_TO_I = dict()
for i, key in enumerate(CANDIDATES.keys()):
    I_TO_KEY[i] = key
    KEY_TO_I[key] = i

SURPLUS_AGREEMENT_I = list()
for item in SURPLUS_AGREEMENT:
    SURPLUS_AGREEMENT_I.append(tuple(map(lambda x: KEY_TO_I[x], item)))

SURPLUS_MATRIX = np.zeros((len(CANDIDATES)-2, len(SURPLUS_AGREEMENT)), dtype=np.int16)
for i in range(len(SURPLUS_AGREEMENT_I)):
    for j in SURPLUS_AGREEMENT_I[i]:
        SURPLUS_MATRIX[j,i] = 1


# Number based upon linear trend from 2013&2015 elections
NUM_LEGAL_VOTERS = 5500000
AHUZ_HAHASIMA = 4
NUM_MANDATES = 120

class Simulation:
    def __init__(self):
        self.base_dist = {i: float(j) for i, j in CANDIDATES.items()}
        self.distribution = None
        self._sample = None

    def random_drift(self, constant_variance, relative_variance):
        constant_drift = np.random.normal(0.0, constant_variance, (len(self.base_dist),))
        relative_drift = np.random.normal(0.0, relative_variance, (len(self.base_dist),))
        self.distribution = dict()
        for i, key in enumerate(self.base_dist.keys()):
            self.distribution[key] = max(self.base_dist[key]*np.exp(relative_drift[i]) + constant_drift[i], 0)
        return self.distribution

    def sample(self, num_voters):
        if self.distribution is None:
            print("""Warning: sampling without drift!
                     this can lead into weired behaviours as voters distribution is alligned
                     to polling resolution of a single knesset member""")
            self.distribution = self.base_dist
        pvals = []
        for i, key in enumerate(self.distribution.keys()):
            pvals.append(self.distribution[key])
        pvals = np.array(pvals)
        pvals /= np.sum(pvals)
        result = np.random.multinomial(NUM_LEGAL_VOTERS, pvals, 1)[0]
        result = result[:KEY_TO_I[None]]
        self._sample = result
        return result

    def mandates(self):
        if self.sample is None:
            raise Exception("Cannot distribute mandes without sampling voters!")
        mandates = self._sample/np.sum(self._sample)*NUM_MANDATES
        mandates = mandates.astype(np.int16)
        mandates = mandates * (mandates >= AHUZ_HAHASIMA)
        mandates = mandates[:KEY_TO_I["PETEK_LAVAN"]]
        surplus_matrix = SURPLUS_MATRIX
        surplus_matrix = (surplus_matrix.T * (mandates > 0)).T

        # Bader-offer
        spare_mandates = NUM_MANDATES - np.sum(mandates)
        jointvoters = self._sample[:KEY_TO_I["PETEK_LAVAN"]].dot(surplus_matrix)
        for mandate in range(spare_mandates):
            jointmandates = mandates.dot(surplus_matrix)
            jointcost = jointvoters/(jointmandates+1)
            idx = np.nonzero(surplus_matrix[:,np.argmax(jointcost)])[0]
            individual_cost = self._sample[idx]/(mandates[idx] + 1)
            mandates[idx[np.argmax(individual_cost)]] += 1

        return mandates

NUM_RUNS = 1000000

def main():
    d = Simulation()
    affected = {key: 0 for key in CANDIDATES.keys()}
    affected_weighted = {key: 0 for key in CANDIDATES.keys()}
    for i in range(NUM_RUNS):
        d.random_drift(1, 0.2)
        d.sample(NUM_LEGAL_VOTERS)
        mandates = d.mandates()
        for key in CANDIDATES.keys():
            if key == None:
                continue # Non-voters are not part of the results
            d._sample[KEY_TO_I[key]] += 1
            delta = np.sum(np.abs(mandates - d.mandates()))
            if delta:
                affected[key] += 1
                affected_weighted[key] += delta
            d._sample[KEY_TO_I[key]] -= 1
        if i % 10000 == 0:
            print(i)
            _affected = {key:(0 if val==0 else i/val) for key, val in affected.items()}
            print("Affect chance - 1 in:")
            print(_affected)
            print("Expected value of voting in mandates:")
            _affected_weighted = {key:(0 if val==0 else val/i) for key, val in affected_weighted.items()}
            print(_affected_weighted)
            print("\n\n")
    print("\n\n\nFinal - the chance of affecting result:")
    _affected = {key:(0 if val==0 else NUM_RUNS/val) for key, val in affected.items()}
    _affected_weighted = {key:(0 if val==0 else val/NUM_RUNS) for key, val in affected_weighted.items()}
    print(_affected)
    print("\n\n\nVoting utility in mandates:")
    print(_affected_weighted)
    return 0

if __name__ == "__main__":
    exit(main())
Voting utility in mandates:

# Output:
# {'KAHOL_LAVAN': 0.00011, 'LIKUD': 0.000102, 'HABAIT_HAYEHUDI': 0.000158,
#  'HAYAMIN_HAHADASH': 0.000112, 'MERETZ': 0.000178, 'HAAVODA': 0.000152,
#  'YAHADUT_HATORA': 0.000126, 'TAAL_HADASH': 0.000144, 'SHAS': 0.000126,
#  'ZEHUT': 0.00014, 'KULANU': 0.00013, 'GESHER': 0.000104,
#  'YISRAEL_BEITENU': 7.8e-05, 'RAAM_BALAD': 5.8e-05,
#  'PETEK_LAVAN': 3.2e-05, None: 0}
