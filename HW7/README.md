# CS581-HW7

## Requirements

- Python 3.x

Required Python modules:
- argparse
- sys
- time
- requests (for fetching safe primes)

Install the requests module via pip if you haven't already:

    pip install requests

## Usage

Run the script from the command line with different options:

### Encryption/Decryption Mode

Provide the two prime numbers and the message to encode/decode. Note that the script enforces that:
- Both p and q must be greater than 1.
- p must equal 2q + 1 (i.e., p should be a safe prime based on q).

Example:

    python RSA.py <p> <q> "Your message here"

For example:

    python RSA.py 23 11 "Hello, RSA!"

### Generate Safe Primes

Use the --gen_primes flag to fetch safe primes (p and q) from the online API:

    python RSA.py --gen_primes

The output will display safe prime values for p and q.

### Testing Mode

Run the built-in test suite using the --test flag. This mode fetches safe primes and runs a number of RSA encryption/decryption cycles to ensure the algorithm works as expected:

    python RSA.py --test
