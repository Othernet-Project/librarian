import argparse
import json
import multiprocessing
import os
import subprocess
import time


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PHANTOM_EXEC = 'phantomjs'
JS_FILE = 'load.js'


class PhantomLoad(multiprocessing.Process):

    def __init__(self, queue, target, silent):
        multiprocessing.Process.__init__(self)
        self.queue = queue
        self.target = target
        self.silent = silent

    def run(self):
        cmd = [PHANTOM_EXEC, JS_FILE, str(self.pid), self.target]
        if self.silent:
            cmd += ['silent']

        p = subprocess.Popen(cmd,
                             cwd=MODULE_DIR,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            if line.startswith('---->'):
                print(line[:-1])
            else:
                try:
                    response_data = json.loads(line)
                except ValueError:
                    pass
                else:
                    self.queue.put(response_data)


def report(responses, elapsed_time):
    ms2sec = lambda ms: '{0} secs'.format(ms * 0.001)

    transactions = len(responses)
    transaction_rate = transactions / elapsed_time
    successful = [r['time'] for r in responses if r['success']]
    failed_count = transactions - len(successful)
    if responses:
        average_response_time = sum(successful) / float(transactions)
        availability = len(successful) * 100.0 / transactions
        slowest = max(successful)
        fastest = min(successful)
    else:
        average_response_time = 0
        availability = 0
        slowest = 0
        fastest = 0

    print("=" * 80)
    print("Transactions:            {0}".format(transactions))
    print("Successful transactions: {0}".format(len(successful)))
    print("Failed transactions:     {0}".format(failed_count))
    print("Availability:            {0} %".format(availability))
    print("Elapsed time:            {0} secs".format(elapsed_time))
    print("Average response time:   {0}".format(ms2sec(average_response_time)))
    print("Slowest response time:   {0}".format(ms2sec(slowest)))
    print("Fastest response time:   {0}".format(ms2sec(fastest)))
    print("Transaction rate:        {0} trans/sec".format(transaction_rate))


def perform(target, worker_count, cycle_count, silent):
    print("=" * 80)
    print("Load testing {0} with {1} workers"
          " for {2} cycles.".format(target, worker_count, cycle_count))
    queue = multiprocessing.Queue()
    responses = []
    start_time = time.time()
    for cycle in range(cycle_count):
        print("=" * 80)
        print("Running cycle {0} of {1}".format(cycle + 1, cycle_count))
        if not silent:
            print("=" * 80)

        workers = [PhantomLoad(queue, target, silent)
                   for _ in range(worker_count)]
        [w.start() for w in workers]
        [w.join() for w in workers]

    elapsed_time = time.time() - start_time

    while not queue.empty():
        responses.append(queue.get())

    report(responses, elapsed_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target', type=str, help='Target URL')
    parser.add_argument('-w',
                        '--workers',
                        type=int,
                        default=1,
                        help='Number of workers to run in parallel')
    parser.add_argument('-c',
                        '--cycles',
                        type=int,
                        default=1,
                        help='Number of cycles to repeat test')
    parser.add_argument('--silent',
                        action='store_true',
                        help='Disable verbose output')
    args = parser.parse_args()
    perform(args.target, args.workers, args.cycles, args.silent)
