#!/usr/bin/python3
"""
    This module implements factoring functions, as part of
    the pedagogical arithmetic tool set.
"""
import sys

class Factors:
    """
    These functions factor integers and compute factor-related functions
    """
    def eratosthanes(self, n: int) -> list[int]:
        """Returns a list of all prime numbers up to n."""
        if n < 2:
            return []

        # Initialize a boolean list tracking primality
        # True means prime, False means composite
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False  # 0 and 1 are not prime numbers

        # Iterate up to the square root of n
        for i in range(2, int(n**0.5) + 1):
            if is_prime[i]:
                # Mark multiples of i starting from i*i as False
                for multiple in range(i * i, n + 1, i):
                    is_prime[multiple] = False

        # Extract all indices where is_prime is still True
        return [num for num, prime in enumerate(is_prime) if prime]


    def factors(self, n: int) -> list[int]:
        """
        return a list of ALL of the factors of an integer
               (a single factor may be included multiple times)
        """
        # prime numbers are trivial
        primes = self.eratosthanes(n+1)
        if n in primes:
            return [n]

        fact_list = []
        for p in primes:
            while n % p == 0:
                fact_list.append(p)
                n /= p
                if n == 1:
                    return fact_list
        # this should be impossible
        return [-1]

    def greatest_common_factor(self, n1: int, n2: int) -> int:
        """
        return the greatest common factor of two integers
        """
        gcf = 1
        f1 = self.factors(n1)
        f2 = self.factors(n2)

        # divide each by every factor they have in common
        for f in f1:
            if f in f2:
                while n1%f == 0 and n2%f == 0:
                    gcf *= f
                    n1 /= f
                    n2 /= f
        return int(gcf)

    def least_common_multiple(self, n1: int, n2: int) -> int:
        """
        return the least common multiple of two integers
        """
        # x * y = (x/gcf * gcf)*(y/gcf * gcf)
        #       = (x/gcf)*(y/gcf) * gcf^2
        #   but we don't need to square gcf to get a CM
        #       we can factor out 1/gcf
        # LCM(x,y) = (x*y)/gcf
        gcf = self.greatest_common_factor(n1, n2)

        # that need not be s
        return int(n1 * n2 / gcf)


if __name__ == '__main__':
    limit = 100
    fact = Factors()

    print(f"Primes up to {limit}:")
    print(fact.eratosthanes(limit))

    print()
    for n in [2, 5, 6, 12, 30, 75, 81, 83]:
        print(f"factors of {n}: {fact.factors(n)}")
