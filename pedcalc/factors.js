/**
 * list of primes
 *
 * @param {int} n - maximum desired number
 * @return {int Array} all primes up to n
 */
function eratosthanes(n) {
	// allocate an array of the appropriate size
	is_prime = new Array(n).fill(true);
	is_prime[0] = false;
	is_prime[1] = false;

	// all multiples of primes are non-prime
	max = n ** 0.5;
	for (let i = 0; i <= max; i++) {
		if (is_prime[i])
			for (let j = 2; i * j < n; j++)
				is_prime[i*j] = false;
	}

	// make a list of those primes
	num_primes = 0;
	for (let i = 0; i < n; i++)
		if (is_prime[i])
			num_primes++;
	primes = new Array(num_primes);
	next_spot = 0;
	for (let i = 0; i < n; i++) {
		if (is_prime[i])
			primes[next_spot++] = i;
	}
	return primes;
}

/**
 * return a string of products
 *
 * @param {int Array} list - array of factors
 * @param {int} count - number of elements to print
 * @param {boolean} parenthesize - enclose in parentheses
 * @return {string}
 */
function product_list(list, count, parenthesize) {
	var output = parenthesize ? "(" : "";
	for( let i = 0; i < count; i++ ) {
		if (i > 0)
			output += " * ";
		output += String(list[i]);
	}
	if (parenthesize)
		output += ")";
	return output;
}

/**
 * all the factors of an integer
 *
 * @param {int} n - number to be factored
 * @return {int Array} - array of factors
 *		   one factor may appear multiple times
 */
function factors(n) {
	primes = eratosthanes(n+1);
	num_primes = primes.length;

	// prime numbers are trivial
	for (let i = 0; i < num_primes; i++)
		if (primes[i] == n)
			return new Array(1).fill(n);

	// divide by primes until we come down to one
	max_factors = n;
	factor_list = new Array(max_factors);
	next_spot = 0;
	for (let i = 0; n > 1 && i < num_primes; i++)
		while (n % primes[i] == 0) {
			factor_list[next_spot++] = primes[i];
			n /= primes[i];
		}

	// reduce the size of the array
	short_list = new Array(next_spot);
	for (let i = 0; i < next_spot; i++)
		short_list[i] = factor_list[i];
	return short_list;
}

/**
 * Factor one integer
 * @param {string} num1
 * @return {string} representing its factors
 */
function factor(num1) {
	var n1 = Number(num1);
	var f1 = factors(n1);
	var output = n1 + " = ";
	output += product_list(f1, f1.length, false);
	return output;
}

/**
 * Least Common Multiple of two integers
 * @param {string} num1
 * @param {string} num2
 * @return {string} representing the LCM
 */
function least_common_multiple(num1, num2) {
	var n1 = Number(num1);
	var f1 = factors(n1);
	var output = product_list(f1, f1.length, true);
	output += " * ";
	var n2 = Number(num2);
	var f2 = factors(n2);
	output += product_list(f2, f2.length, true);

	/*
	 * x * y = (x/gcf * gcf)*(y/gcf * gcf)
	 *       = (x/gcf)*(y/gcf) * gcf^2
	 *   but we don't need to square gcf to get a CM
	 *       we can factor out 1/gcf
	 * LCM(x,y) = (x*y)/gcf
	 */
	temp = greatest_common_factor(num1, num2, false);
	// separate the common factors and their product
	var x = temp.indexOf("=");
	var f = temp.substring(0, x-1).trim();
	output += " / " + f;

	// compute the LCM
	var gcf = Number(temp.substring(x+1, temp.length).trim());
	var lcm = (n1 * n2) / gcf;
	output += " = " + String(lcm);

	return output;
}

/**
 * Greatest common factor of two integers
 * @param {string} num1
 * @param {string} num2
 * @param {boolean} intermediate - show intermediate results
 * @return {string} representing the GCF
 */
function greatest_common_factor(num1, num2, intermediate) {
	var output = "";

	// print factors of first operand
	var n1 = Number(num1);
	var f1 = factors(n1);
	if (intermediate) {
		output = n1 + " = ";
		output += product_list(f1, f1.length, true);
		output += "\n";
	}

	// print factors of second operand
	var n2 = Number(num2);
	var f2 = factors(n2);
	if (intermediate) {
		output += n2 + " = ";
		output += product_list(f2, f2.length, true);
		output += "\n";
	}

	// list to receive the common factors
	var max = f1.length > f2.length ? f1.length : f2.length;
	factor_list = new Array(max);
	factor_count = 0;

	// GCF is the product of all shared factors
	best = 1;
	for( let i = 0; i < f1.length; i++ ) {
		let f = f1[i];
		// see if it is a factor of n2
		for( let j = 0; j < f2.length; j++ ) {
			if (f2[j] == f) {
				// divde by that as many times as possible
				while(n1%f == 0 && n2%f == 0) {
					factor_list[factor_count++] = f;
					best *= f;
					n1 /= f;
					n2 /= f;
				}
				continue;
			}
		}
	}
	output += product_list(factor_list, factor_count, true);
	output += " = " + String(best);
	return output;
}
