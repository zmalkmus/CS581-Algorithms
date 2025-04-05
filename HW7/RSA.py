import sys
import argparse

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

def rsa(p, q, message_str):

    if p <= 1 or q <= 1:
        print("Both p and q must be greater than 1.")
        sys.exit(1)
    if p != 2 * q + 1:
        print("p must be equal to 2q + 1.")
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
# This prime generate works but is too slow for testing
# import random
# from sympy import isprime

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
# p_safe = generate_safe_prime(512)
# print("Safe prime p =", p_safe)
# print("q = (p-1)//2 =", (p_safe - 1)//2)

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

    for i in range(1, k+1):
        primes = fetch_safe_primes()
        if not primes or 'p' not in primes or 'q' not in primes:
            continue

        p = int(primes['p'])
        q = int(primes['q'])
        message_str = "Hello, RSA!"

        try:
            e, d, n, cipher_int, decrypted_str = rsa(p, q, message_str)
        except Exception as ex:
            raise Exception(f"RSA computation failed during iteration {i}: {ex}")

        if decrypted_str != message_str:
            raise AssertionError(
                f"RSA test failed during iteration {i}: decrypted '{decrypted_str}' does not match original '{message_str}'"
            )

        time.sleep(wait_time)

    print("All RSA tests passed successfully!")


# ================================================================
# Main function
# ================================================================
def main():
    parser = argparse.ArgumentParser(description="RSA encryption/decryption")
    parser.add_argument("--gen_primes", action="store_true", help="Generate safe primes")
    parser.add_argument("--test", action="store_true", help="Run tests instead of normal execution")
    parser.add_argument("p", type=int, nargs="?", help="Prime number p")
    parser.add_argument("q", type=int, nargs="?", help="Prime number q")
    parser.add_argument("message", type=str, nargs="?", help="Message to encode/decode")

    args = parser.parse_args()

    if args.gen_primes:
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

    print(e)
    print(d)
    print(message_str)
    print(cipher_int)
    print(decrypted_str)

if __name__ == "__main__":
    main()
