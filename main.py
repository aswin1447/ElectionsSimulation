
import argparse
import numpy as np

from simulation import Simulation
from configuration import Configuration

from constants import DEFAULT_NUM_ITERATIONS, DEFAULT_PRINT_INTERVAL, DEAULE_CONFIGURATION_JSON
import json


def main(args):
    conf = Configuration(args.conf_json)
    d = Simulation(conf)
    
    affected = {key: 0 for key in conf.candidates_support.keys()}
    affected_weighted = {key: 0 for key in conf.candidates_support.keys()}
    
    for i in range(args.num_iterations):
        if not (args.disable_drift):
            d.random_drift()
        d.sample(conf.num_voters)
        mandates = d.mandates()
        for key in conf.candidates_support.keys():
            if key == "NONE":
                continue # Non-voters are not part of the results
            d._sample[conf.key_to_i[key]] += 1
            delta = np.sum(np.abs(mandates - d.mandates()))
            if delta:
                affected[key] += 1
                affected_weighted[key] += delta
            d._sample[conf.key_to_i[key]] -= 1
        if i % args.print_interval == 0:
            print(i)
            _affected = {key:(0 if val==0 else i/val) for key, val in affected.items()}
            print("Affect chance - 1 in:")
            print(_affected)
            print("Expected value of voting in mandates:")
            _affected_weighted = {key:(0 if val==0 else val/i) for key, val in affected_weighted.items()}
            print(_affected_weighted)
            print("\n\n")
    print("\n\n\nFinal - the chance of affecting result:")
    _affected = {key:(0 if val==0 else args.num_iterations/val) for key, val in affected.items()}
    _affected_weighted = {key:(0 if val==0 else val/args.num_iterations) for key, val in affected_weighted.items()}
    print(_affected)
    print("\n\n\nVoting utility in mandates:")
    print(_affected_weighted)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-iterations", type=int, default=DEFAULT_NUM_ITERATIONS,
        help="Number of simulation iterations. Defualt: {0}".format(DEFAULT_NUM_ITERATIONS))
    parser.add_argument("--print-interval", type=int, default=DEFAULT_PRINT_INTERVAL,
        help="Print aggregated information once in this many iterations. Defualt: {0}".format(DEFAULT_PRINT_INTERVAL))
    parser.add_argument("--disable-drift", action="store_true",
        help="Without this parameter, random drift will be applied to voting percets of each party in each iteration")
    parser.add_argument("--conf-json", type=str, default=DEAULE_CONFIGURATION_JSON,
        help="Json file with configuration for simulation. Default: {0}".format(DEAULE_CONFIGURATION_JSON))
    args = parser.parse_args()
    if args.disable_drift:
        print("""\n\nWarning: sampling without drift!
this can lead into unrealistic results.\n\n""")
    exit(main(args))

