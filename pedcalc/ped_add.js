/**
 * pedagogical addition, showing carries
 *
 * @param {string} num1 - first addend
 * @param {string} num2 - second addend
 * @reutrn {string} decimal alligned results:
 *			 carries
 *			  addend
 *		    + addend
 *			 -------
 *			     sum
 */
function add(num1, num2) {
	// get same number of decimal places, and calculate lengths
	const [ num_1, num_2 ] = decimal_align(num1, num2);
	var len1 = num_1.length;
	var len2 = num_2.length;
	var width = (len1 > len2 ? len1 : len2) + 1;
	var pad1 = num_1.padStart(width);
	var pad2 = num_2.padStart(width);
	var line = "-".repeat(width+1);

	var carry_line = "";					// character carries
	var result = "";						// character sum
	var carries = new Array(width).fill(0);	// numeric carries
	// do the addition one digit at a time
	var current_carry = 0;					// carry into this digit
	for( let i = width - 1; i >= 0; i-- ) {
		if (pad1[i] == '.') {		// skip over (aligned) decimal point
			result = '.' + result;
			carries[i] = 0;
			continue;
		}

		// do the (character) digit addition
		carries[i] = current_carry;
		let digit1 = (pad1[i] == ' ') ? 0 : Number(pad1[i]);
		let digit2 = (pad2[i] == ' ') ? 0 : Number(pad2[i]);
		let total = digit1 + digit2 + current_carry;

		carry_line = String(current_carry) + carry_line;
		result = String(total % 10) + result;
		current_carry = Math.trunc(total/10);
	}

	// validate our results with (binary) addition
	var sum = Number(result);
	var val1 = Number(num1);
	var val2 = Number(num2);
	var correct = val1 + val2;
	var ok = (sum == correct) ? "\n" : " (should be " + String(correct) + ")\n";

	// create the output
	var output = "";
	output += " " + carry_line + "    (carries)\n";
	output += " " + pad1 + "\n";
	output += "+" + pad2 + "\n";
	output += line + "\n";
	output += " " + no_leading_zeroes(result) + ok;
	return output
}
