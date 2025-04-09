import sys
import argparse
import random

# ================================================================
# RSA Encryption/Decryption
# =================================================================
def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y

def miller_rabin(n, k=10):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def rsa(p, q, message_str):
    if p <= 1 or q <= 1:
        print("Both p and q must be greater than 1.")
        sys.exit(1)
    if p != 2 * q + 1:
        print("p must be equal to 2q + 1.")
        sys.exit(1)
    if not (miller_rabin(p)):
        print("p is not prime.")
        sys.exit(1)
    if not (miller_rabin(q)):
        print("q is not prime.")
        sys.exit(1)

    m = int.from_bytes(message_str.encode('utf-8'), byteorder='big')

    n = p * q
    if m >= n:
        print("Message is too large. 'message_str' as an integer must be less than n = p * q.")
        sys.exit(1)

    phi = (p - 1) * (q - 1)

    e = 3
    while gcd(e, phi) != 1:
        e += 2

    _, d, _ = extended_gcd(e, phi)
    d %= phi

    c = pow(m, e, n)

    m_decrypted_int = pow(c, d, n)
    decrypted_bytes = m_decrypted_int.to_bytes((m_decrypted_int.bit_length() + 7) // 8, byteorder='big')

    try:
        m_decrypted_str = decrypted_bytes.decode('utf-8')
    except UnicodeDecodeError:
        m_decrypted_str = "<Decoding Error>"

    return e, d, n, c, m_decrypted_str

# ===============================================================   
# Prime Generation
# ===============================================================
# This prime generate works but is too slow for testing a lot of primes

# def generate_safe_prime(bit_length):
#     while True:
#         # Generate a random candidate for q of (bit_length-1) bits
#         # so that p = 2q + 1 is about 'bit_length' bits.
#         q_candidate = random.getrandbits(bit_length - 1)
#         q_candidate |= 1
        
#         # Check if q_candidate is prime
#         if isprime(q_candidate):
#             p = 2 * q_candidate + 1
#             if p.bit_length() == bit_length and isprime(p):
#                 return p


def fetch_safe_primes(bit_length=2048):
    import requests
    url = f"https://2ton.com.au/getprimes/random/2048"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        base10_values = {}
        for key in ['p', 'q']:
            if key in data and 'base10' in data[key]:
                base10_values[key] = data[key]['base10']
            else:
                print(f"Base10 value for {key} not found.")
        return base10_values
    else:
        print(f"Failed to fetch prime. Status code: {response.status_code}")


# ================================================================
# Testing
# ================================================================
def test_rsa(k=10, wait_time=1):
    import time
    import csv

    results = []  # List to hold timing data for each iteration

    for i in range(1, k + 1):
        primes = fetch_safe_primes()
        if not primes or 'p' not in primes or 'q' not in primes:
            print(f"Skipping iteration {i}: safe primes not available")
            continue

        p = int(primes['p'])
        q = int(primes['q'])
        message_str = "Hello, RSA!"

        # Measure the time taken by the rsa function
        start = time.perf_counter()
        try:
            e, d, n, cipher_int, decrypted_str = rsa(p, q, message_str)
        except Exception as ex:
            raise Exception(f"RSA computation failed during iteration {i}: {ex}")
        end = time.perf_counter()

        duration = end - start  # Time taken for the RSA function call

        if decrypted_str != message_str:
            raise AssertionError(
                f"RSA test failed during iteration {i}: decrypted '{decrypted_str}' does not match original '{message_str}'"
            )

        # Append iteration number, duration and optionally the prime numbers to the results
        results.append({
            "Iteration": i,
            "Duration": duration,
            "p": p,
            "q": q
        })

        # Pause between iterations
        time.sleep(wait_time)

    # Save results to a CSV file
    output_filename = "rsa_timings.csv"
    if results:  # Check that we have at least one result
        keys = results[0].keys()
        with open(output_filename, "w", newline="") as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"All RSA tests passed successfully! Results saved to {output_filename}")
    else:
        print("No valid results to save.")


# ================================================================
# Main function
# ================================================================
def main():
    parser = argparse.ArgumentParser(description="RSA encryption/decryption")
    parser.add_argument("--generate", action="store_true", help="Generate safe primes")
    parser.add_argument("--test", action="store_true", help="Run tests instead of normal execution")
    parser.add_argument("p", type=int, nargs="?", help="Prime number p")
    parser.add_argument("q", type=int, nargs="?", help="Prime number q")
    parser.add_argument("message", type=str, nargs="?", help="Message to encode/decode")

    args = parser.parse_args()

    if args.generate:
        primes = fetch_safe_primes(2048)
        print("p:", primes['p'])
        print("q:", primes['q'])
        return
    
    if args.test:
        print("Running tests...")
        test_rsa()
        return

    if args.p is None or args.q is None or args.message is None:
        parser.error("the following arguments are required: p, q, message")

    p = args.p
    q = args.q
    message_str = args.message

    e, d, n, cipher_int, decrypted_str = rsa(p, q, message_str)

    print(">> ", e)
    print(">> ", d)
    print(">> ", message_str)
    print(">> ", cipher_int)
    print(">> ", decrypted_str)

if __name__ == "__main__":
    main()
